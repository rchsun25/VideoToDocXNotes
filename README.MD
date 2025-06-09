# VideoToDocXNotes

**VideoToDocXNotes** is a Python-based tool that transcribes audio or extracts audio from video files, generates a transcription, and creates a summarized document using OpenAI's language models. It temporarily writes the summary to a Markdown file before saving it as a `.docx`; only the `.docx` summary is retained.

## Features
- **Supported input file types**: Video: `.mp4`, `.mkv`, Audio: `.mp3`, Transcript: `.txt`, `.docx`
- **Audio extraction**: Automatically extracts audio from video files (`.mp4`, `.mkv`) using `ffmpeg`.
- **Transcription**: Uses OpenAI's Whisper model to transcribe audio files.
- **Summarization**: Summarizes transcriptions using OpenAI GPT, temporarily storing the summary as a Markdown file before converting it to `.docx`.
- **File organization**: Automatically organizes generated files into `WORK` and `NOTES` folders for easy access.

## Requirements
- Python 3.7+
- Whisper model (`transformers` package)
- OpenAI API access
- FFmpeg
- Pypandoc
- PyTorch
- Tkinter

## Installation

1. Install the required packages using pip:

    ```bash
    pip install torch whisper ffmpeg pypandoc openai tkinter
    ```

2. Install **Pandoc** by following [this guide](https://pandoc.org/installing.html).

3. Install **FFmpeg** by following [this guide](https://ffmpeg.org/download.html).

4. Add your OpenAI API key to your user environmental variables by following [this guide](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).

## Usage

1. Run the `AudioTranscriber.py` script:

    ```bash
    python AudioTranscriber.py
    ```

2. Select the audio or video file you wish to process using the file dialog that appears.

3. The program will:
   - Extract the audio if it's a video file.
   - Transcribe the audio.
   - Summarize the transcription, create a temporary `.md` file, and generate a `.docx` summary.

4. All processed files will be moved to the appropriate folders:
   - **WORK** folder for transcriptions and other working files.
   - **NOTES** folder for the summarized documents.

## Output

- **Transcriptions**: Saved as `.txt` files.
- **Summaries**: The `.docx` file is kept while the intermediate `.md` file is deleted.

## File Structure

- **Processed files** are organized in the following folder structure:

```
|-- WORK/
    |-- audio_file.mp3
    |-- transcription.txt
|-- NOTES/
    |-- summary.docx
```

## Contributing

Feel free to open issues or pull requests for suggestions and improvements.

## Running Tests

Unit tests are written with [pytest](https://pytest.org). After installing the
requirements, run the test suite from the repository root:

```bash
pytest
```

## WPF Version

A minimal Windows desktop interface is provided in the `VideoToDocXNotesWPF`
folder. It allows you to select a file and runs `AudioTranscriber.py` in the
background. To build it you will need the [.NET SDK](https://dotnet.microsoft.com/):

```bash
dotnet build VideoToDocXNotesWPF/VideoToDocXNotesWPF.csproj
```

Run the resulting executable on Windows to launch the GUI.
