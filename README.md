# Python Whisper transcription

Turn an audio recording into a transcript or a subtitle file. By default the script runs Whisper on your CPU. Your audio stays on your computer. You can also explicitly select OpenAI for hosted transcription.

## Transcribe a file locally

Use Python 3.12 and a virtual environment. From a terminal on macOS or Linux, run

```sh
git clone https://github.com/heyfoz/python-openai-whisper.git
cd python-openai-whisper
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-local.txt
python whisper_local.py recording.m4a
```

On Windows, create the environment with `py -3.12 -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1` in PowerShell. Run `python whisper_local.py` on its own for prompts.

The first local run downloads the multilingual `small` model. Only the selected model is downloaded. Choose `tiny` for a quick draft, or try `large-v3` when you can spend more time and memory on accuracy. Inference uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and needs no API key.

```sh
python whisper_local.py recording.m4a --model tiny
python whisper_local.py recording.m4a -o subtitles.vtt
python whisper_local.py recording.m4a --model small --offline -o subtitles.srt
python whisper_local.py recording.m4a --model /path/to/faster-whisper-model --offline
```

For offline use, download the chosen model once or supply a complete CTranslate2 Whisper directory including its tokenizer. The script detects the spoken language. A local run always processes audio on this computer, including when a model download fails.

## Save or pipe the result

Use `-o` to create a new UTF-8 file. A `.vtt` or `.srt` filename selects that subtitle format. Other filenames default to text. Use `--format` to choose explicitly, including when piping captions to another program. Existing output files are preserved.

```sh
python whisper_local.py interview.mp3 -o interview.txt
python whisper_local.py interview.mp3 --format vtt > interview.vtt
```

## Use OpenAI

Install the optional client with `python -m pip install openai`. The following command uploads the recording to OpenAI and uses your API account. The script reads `OPENAI_API_KEY` or prompts privately in an interactive terminal.

```sh
python whisper_local.py recording.m4a --backend openai
```

Hosted text uses `gpt-transcribe`. Hosted VTT and SRT use `whisper-1` for compatibility until its scheduled shutdown on February 26, 2027. For ongoing subtitle work or files over the API's 25 MB limit, choose the local backend. [OpenAI file transcription guide](https://developers.openai.com/api/docs/guides/speech-to-text)

## License

[MIT](LICENSE)
