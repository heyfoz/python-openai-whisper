# Python Whisper transcription

Turn an audio recording into a transcript or a subtitle file. By default the script runs Whisper on your CPU. Your audio stays on your computer. You can also explicitly select OpenAI for hosted transcription.

## Transcribe a file locally

Choose your setup for [Windows](#windows), [Linux](#linux), or [macOS](#macos). Each uses Python 3.12 and runs Whisper on your CPU. At the audio file prompt, paste the full path to your recording. Press Enter at the format prompt for plain text, or enter `vtt` or `srt` for captions.

### Windows

Open **Command Prompt** on an x64 PC. If you need Git or Python 3.12, install the missing tools with WinGet, then open a new Command Prompt.

```bat
winget install --id Git.Git --exact
winget install --id Python.Python.3.12 --exact
```

```bat
git clone https://github.com/heyfoz/python-openai-whisper.git
cd python-openai-whisper
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements-local.txt
python whisper_local.py
```

For **PowerShell**, use the same clone, `cd`, and `py` commands. Then run the environment's Python directly. Use this same executable for the examples below.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
.\.venv\Scripts\python.exe whisper_local.py
```

If Windows reports a missing Visual C++ runtime DLL when loading the model, install the x64 redistributable. [Microsoft Visual C++ downloads](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

### Linux

Start with Git and Python 3.12 with `venv` support. On Ubuntu 24.04, you can install them with

```sh
sudo apt update
sudo apt install git python3.12 python3.12-venv
```

In Bash or another POSIX shell, run

```sh
git clone https://github.com/heyfoz/python-openai-whisper.git
cd python-openai-whisper
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-local.txt
python whisper_local.py
```

### macOS

Open **Terminal**. If you use Homebrew and need Git or Python 3.12, run `brew install git python@3.12`. [Python 3.12 on Homebrew](https://formulae.brew.sh/formula/python@3.12)

```sh
git clone https://github.com/heyfoz/python-openai-whisper.git
cd python-openai-whisper
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-local.txt
python whisper_local.py
```

### Run again or choose a model

In a new terminal, return to the project folder and repeat the activation command for your platform, or use the PowerShell executable above. You can pass a recording directly to skip the prompts. Quote paths containing spaces, for example `python whisper_local.py "meeting notes.m4a" -o meeting.srt`.

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
python whisper_local.py interview.mp3 -o interview.vtt
```

## Use OpenAI

Install the optional client with `python -m pip install openai`. The following command uploads the recording to OpenAI and uses your API account. The script reads `OPENAI_API_KEY` or prompts privately in an interactive terminal.

```sh
python whisper_local.py recording.m4a --backend openai
```

Hosted text uses `gpt-transcribe`. Hosted VTT and SRT use `whisper-1` for compatibility until its scheduled shutdown on February 26, 2027. For ongoing subtitle work or files over the API's 25 MB limit, choose the local backend. [OpenAI file transcription guide](https://developers.openai.com/api/docs/guides/speech-to-text)

## License

[MIT](LICENSE)
