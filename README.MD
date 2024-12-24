# Meeting Notes Generator - GitHub ReadMe

## Overview
The Meeting Notes Generator is a Python script designed to streamline the process of generating detailed meeting notes from audio, video, or text files. This tool employs state-of-the-art transcription and natural language processing models to produce comprehensive notes in Word Document (.docx) format. It is perfect for workplaces where accurate and detailed meeting documentation is crucial.

## Features
- **Automatic File Monitoring**: Uses a folder watcher to detect new files.
- **Transcription and Summarization**: Supports `.mp4`, `.mkv`, `.mp3`, `.txt`, and `.docx` file types.
- **Detailed Notes Generation**: Generates structured, detailed meeting notes tailored for technical or professional use.
- **Folder Management**: Moves processed files to a designated folder to maintain organization.

## Requirements
### System Requirements
- Python 3.9 or higher
- Supported operating systems: Windows, macOS, Linux

### Dependencies
The following libraries and tools are required:
- Python libraries: `whisper`, `torch`, `pypandoc`, `watchdog`, `openai`, `ffmpeg-python`
- External tools: `ffmpeg`, `pandoc`

## Installation
1. **Install Python Packages**:
   ```bash
   pip install whisper torch pypandoc watchdog openai ffmpeg-python
   ```

2. **Install External Tools**:
   - [FFmpeg](https://ffmpeg.org/): For audio extraction from video files.
   - [Pandoc](https://pandoc.org/): For document format conversions.

3. **Set Environment Variable**:
   - Add your OpenAI API key as an environment variable:
     ```bash
     export OPENAI_API_KEY=your_api_key_here
     ```

## Usage
### Configuration
Update the `audio_folder` variable in the script to the path of your designated folder. For example:
```python
audio_folder = "C:\\path\\to\\Drop Here to Generate Meeting Notes"
```

### Running the Script
Run the script directly from the command line:
```bash
python meeting_notes_generator.py
```
The script will:
- Monitor the specified folder for new files.
- Process files and generate `.docx` meeting notes in the root directory.
- Move original files to a "Processed Files" folder.

## Privacy and Data Usage
By default, OpenAI retains and uses data for model training. However, this script is configured with an OpenAI account where data retention is **disabled** through the [OpenAI Privacy Center](https://platform.openai.com/account/data-settings). Your files remain confidential and are not used for model training.

## Troubleshooting
- **File Not Processed**:
  - Ensure the file has one of the supported extensions.
  - Check the folder permissions.

- **Dependencies Not Found**:
  - Verify that FFmpeg and Pandoc are installed and added to your system PATH.

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests on the [GitHub repository](https://github.com/rchsun25/VideoToDocXNotes).

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact
For questions or support, please contact Reagan via the repository issues or directly through your preferred communication channel.

