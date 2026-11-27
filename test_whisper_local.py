import io
import os
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import whisper_local as cli


class TranscriptionTests(unittest.TestCase):
    def test_subtitles_use_integer_milliseconds_and_escape_text(self):
        segments = [
            SimpleNamespace(start=0, end=1, text=" "),
            SimpleNamespace(start=59.9999, end=61.125, text=" A & B < C "),
        ]
        self.assertEqual(cli.render_segments(segments, "text"), "A & B < C\n")
        self.assertEqual(cli.render_segments(segments, "vtt"),
                         "WEBVTT\n\n00:01:00.000 --> 00:01:01.125\nA &amp; B &lt; C\n\n")
        self.assertEqual(cli.render_segments(segments, "srt"),
                         "1\n00:01:00,000 --> 00:01:01,125\nA &amp; B &lt; C\n\n")

    def test_failed_default_run_does_not_upload_or_leave_output(self):
        with TemporaryDirectory() as directory:
            audio = Path(directory, "sample.wav")
            audio.touch()
            output = audio.with_suffix(".srt")
            with (
                patch.object(sys, "argv", ["whisper_local.py", str(audio), "-o", str(output)]),
                patch.object(cli, "transcribe_local", side_effect=ValueError("model missing")) as local,
                patch.object(cli, "transcribe_hosted") as hosted,
                redirect_stderr(io.StringIO()),
                self.assertRaisesRegex(ValueError, "model missing"),
            ):
                cli.main()
            local.assert_called_once_with(audio, "small", False, "srt")
            hosted.assert_not_called()
            self.assertFalse(output.exists())

    def test_hosted_text_and_captions_use_their_supported_responses(self):
        sdk = MagicMock()
        create = sdk.OpenAI.return_value.__enter__.return_value.audio.transcriptions.create
        with (
            TemporaryDirectory() as directory,
            patch.dict(sys.modules, {"openai": sdk}),
            patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}),
        ):
            audio = Path(directory, "sample.wav")
            audio.touch()
            create.return_value = SimpleNamespace(text="hello")
            self.assertEqual(cli.transcribe_hosted(audio, "text"), "hello\n")
            self.assertEqual(create.call_args.kwargs["model"], "gpt-transcribe")
            self.assertNotIn("response_format", create.call_args.kwargs)
            for fmt in ("vtt", "srt"):
                with self.subTest(fmt=fmt):
                    create.return_value = "caption\n"
                    self.assertEqual(cli.transcribe_hosted(audio, fmt), "caption\n")
                    self.assertEqual(create.call_args.kwargs["model"], "whisper-1")
                    self.assertEqual(create.call_args.kwargs["response_format"], fmt)


if __name__ == "__main__":
    unittest.main()
