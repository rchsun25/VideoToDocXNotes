# VideoToDocXNotes

**VideoToDocXNotes** is a Python-based tool that transcribes audio or extracts audio from video files, generates a transcription, and creates a summarized document using OpenAI's language models. It supports output in `.md` (Markdown) and `.docx` formats.

## Features
- **Supported input file types**: Video: `.mp4`, `.mkv`, Audio: `.mp3`, Transcript: `.txt`, `.docx`
- **Audio extraction**: Automatically extracts audio from video files (`.mp4`, `.mkv`) using `ffmpeg`.
- **Transcription**: Uses OpenAI's Whisper model to transcribe audio files.
- **Summarization**: Summarizes transcriptions using OpenAI GPT and formats the summary into a Markdown file.
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
   - Summarize the transcription and generate output files in `.md` and `.docx` formats.

4. All processed files will be moved to the appropriate folders:
   - **WORK** folder for transcriptions and other working files.
   - **NOTES** folder for the summarized documents.

## Output

- **Transcriptions**: Saved as `.txt` files.
- **Summaries**: Available as `.md` and `.docx` files.

## File Structure

- **Processed files** are organized in the following folder structure:

```
|-- WORK/
    |-- audio_file.mp3
    |-- transcription.txt
    |-- summary.md
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
