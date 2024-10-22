
# Video to Audio Transcription & Summarization Tool

This Python tool extracts audio from video files, transcribes it using a speech recognition model, and generates a summary using OpenAI's GPT model. The transcriptions and summaries are saved in both `.txt` and `.docx` formats, and the files are organized into folders for easy access.

## Features
- **Audio Extraction**: Converts video files (`.mp4`) to audio files (`.mp3`).
- **Automatic Transcription**: Transcribes audio files using the `whisper-small` model from Hugging Face's `transformers` library.
- **AI-Powered Summarization**: Summarizes transcriptions using OpenAI's GPT model.
- **File Organization**: Automatically organizes audio, transcription, and summary files into designated folders.

## Requirements
The following libraries are required to run the code:

```
pip install transformers
pip install torch
pip install moviepy
pip install openai
pip install python-docx
pip install pypandoc
```

## How It Works
1. **Audio Extraction**: If a video file is selected, the audio is extracted and saved as an `.mp3` file.
2. **Transcription**: The audio file is transcribed using the `whisper-small` model from Hugging Face.
3. **Summarization**: The transcription text is summarized using OpenAI's GPT model. The summary is saved in Markdown (`.md`) and Word document (`.docx`) formats.
4. **File Management**: Transcription results and summaries are moved to appropriate folders (`WORK` and `NOTES`).

## File Structure
The program creates the following folders in the directory where the audio or video file is located:
- **WORK**: Stores the `.mp3` audio files and transcription files (`.txt` and `.md`).
- **NOTES**: Stores the summarized document (`.docx`).

## Usage
1. Run the script.
2. Select the audio/video file(s) using the file dialog.
3. The script will process each file, and results will be saved automatically.

### Example Workflow:
- Select an `.mp4` or `.mp3` file.
- If a video file is selected, the audio is extracted.
- The extracted audio is transcribed.
- A summary is generated from the transcription.
- All files are moved to their respective folders (`WORK` and `NOTES`).

## Additional Notes
- The program supports `.mp4`, `.mp3`, and `.txt` files.
- If a `.txt` file is selected, the program skips the transcription step and directly generates a summary from the text.
