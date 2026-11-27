"""Transcribe one audio file on this computer or with the OpenAI API."""

import argparse
import getpass
import os
import sys
from html import escape
from pathlib import Path


FORMATS = ("text", "vtt", "srt")
DEFAULT_MODEL = "small"


def timestamp(milliseconds, decimal):
    seconds, millis = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}{decimal}{millis:03}"


def render_segments(segments, output_format):
    lines = ["WEBVTT", ""] if output_format == "vtt" else []
    decimal = "," if output_format == "srt" else "."
    cue = 0
    for segment in segments:
        text = " ".join(segment.text.split())
        if not text:
            continue
        if output_format == "text":
            lines.append(text)
            continue
        cue += 1
        start = max(0, round(segment.start * 1000))
        end = max(start + 1, round(segment.end * 1000))
        if output_format == "srt":
            lines.append(str(cue))
        lines.extend([
            f"{timestamp(start, decimal)} --> {timestamp(end, decimal)}",
            escape(text, quote=False),
            "",
        ])
    if output_format == "text":
        return " ".join(lines) + "\n"
    return "\n".join(lines) + "\n" if lines else ""


def transcribe_local(audio, model_name, offline, output_format):
    if offline:
        # The tokenizer and the model loader both use the Hugging Face cache.
        os.environ["HF_HUB_OFFLINE"] = "1"
    try:
        from faster_whisper import WhisperModel
    except ModuleNotFoundError as exc:
        if exc.name != "faster_whisper":
            raise
        raise ValueError("Install the local engine with python -m pip install -r requirements-local.txt") from exc

    model = WhisperModel(
        os.path.expanduser(model_name), device="cpu", compute_type="int8", local_files_only=offline
    )
    segments, _ = model.transcribe(str(audio))
    return render_segments(segments, output_format)


def transcribe_hosted(audio, output_format):
    if audio.stat().st_size > 25_000_000:
        raise ValueError("OpenAI accepts uploads up to 25 MB. Use the local backend for this file.")
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        if exc.name != "openai":
            raise
        raise ValueError("Install the API client with: python -m pip install openai") from exc

    key = os.getenv("OPENAI_API_KEY")
    if not key and sys.stdin.isatty():
        key = getpass.getpass("OpenAI API key: ")
    if not key:
        raise ValueError("Set OPENAI_API_KEY to use the OpenAI backend.")
    with OpenAI(api_key=key) as client, audio.open("rb") as source:
        if output_format == "text":
            result = client.audio.transcriptions.create(model="gpt-transcribe", file=source)
            return result.text.rstrip("\n") + "\n"
        result = client.audio.transcriptions.create(
            model="whisper-1", file=source, response_format=output_format
        )
        return result.rstrip("\n") + "\n"


def prompt(message):
    print(message, file=sys.stderr, end="", flush=True)
    return input().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", nargs="?", type=Path, help="recording to transcribe")
    parser.add_argument("--backend", choices=("local", "openai"), default="local",
                        help="local (default), or openai to upload the recording")
    parser.add_argument("--model", help="local Whisper model name or CTranslate2 directory (default: small)")
    parser.add_argument("--offline", action="store_true", help="use only previously downloaded model files")
    parser.add_argument("--format", choices=FORMATS, help="output format (default: infer from -o, else text)")
    parser.add_argument("-o", "--output", type=Path, help="write a new UTF-8 file (default: standard output)")
    args = parser.parse_args()
    if args.backend == "openai" and (args.offline or args.model is not None):
        parser.error("--model and --offline apply only to the local backend")

    audio = args.audio
    output_format = args.format
    if audio is None:
        if not sys.stdin.isatty():
            parser.error("provide an audio file")
        value = prompt(f"Audio file ({args.backend} backend): ")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        audio = Path(value)
        if not output_format and not args.output:
            output_format = prompt("Format [text/vtt/srt, default text]: ").lower() or "text"
            if output_format not in FORMATS:
                parser.error("choose text, vtt, or srt")

    audio = audio.expanduser()
    if not audio.is_file():
        parser.error(f"audio file does not exist: {audio}")
    output = args.output.expanduser() if args.output else None
    if output:
        if output.exists():
            parser.error(f"output already exists: {output}")
        if not output.parent.is_dir():
            parser.error(f"output directory does not exist: {output.parent}")
        if output_format is None and output.suffix.lower() in (".srt", ".vtt"):
            output_format = output.suffix.lower()[1:]
    output_format = output_format or "text"

    if args.backend == "openai":
        transcript = transcribe_hosted(audio, output_format)
    else:
        model = args.model or DEFAULT_MODEL
        print(f"Transcribing locally with {model}…", file=sys.stderr)
        transcript = transcribe_local(audio, model, args.offline, output_format)
    if output:
        with output.open("x", encoding="utf-8", newline="\n") as dest:
            dest.write(transcript)
        print(f"Saved {output}", file=sys.stderr)
    else:
        sys.stdout.write(transcript)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as error:
        sys.exit(f"Error: {error}")
