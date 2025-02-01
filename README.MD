# Automated Notes Generator 🚀

Two Python scripts for generating **meeting minutes** and **lecture module notes** from audio/video/text files, powered by Whisper transcription and OpenAI GPT-4.

## 📋 Features

| Meeting Notes Generator              | Module Notes Generator               |
|--------------------------------------|---------------------------------------|
| ✅ Attendees list                    | ✅ Module title & description        |
| ✅ Action items & deadlines          | ✅ Learning objectives                |
| ✅ Detailed discussion points        | ✅ Key concepts & examples           |
| ✅ Decisions with rationale          | ✅ Exercises & references            |
| ✅ Follow-up meetings tracking       | ✅ Comprehensive technical details   |

**Shared Features**  
- 🕵️ File monitoring for automatic processing  
- 📄 Supports MP4, MKV, MP3, TXT, DOCX inputs  
- 📂 Auto-moves processed files to dedicated folders  
- 📝 Logging for audit and debugging  
- 🚨 Error handling with user notifications  

## 🛠️ Setup Guide

### Prerequisites
- Python 3.10+
- [Pandoc](https://pandoc.org/installing.html) (for DOCX conversion)
- [FFmpeg](https://ffmpeg.org/download.html) (for audio extraction)
- OpenAI API key ([Get yours](https://platform.openai.com/api-keys))

### Installation
1. **Clone repository**  
   ```bash
   git clone https://github.com/yourusername/notes-generator.git
   cd notes-generator
   ```

2. **Install Python packages**  
   ```bash
   pip install -r requirements.txt  # Create this file with: openai python-docx watchdog pypandoc whisper torch ffmpeg-python
   ```

3. **Configure environment**  
   Create `.env` file:
   ```plaintext
   OPENAI_API_KEY=sk-your-key-here
   ```

4. **Prepare folders**  
   ```bash
   # For Windows
   mkdir "E:\MeetingNotesGenerator\Drop Here to Generate Meeting Notes"
   mkdir "E:\ModuleNotesGenerator\Drop Here to Generate Module Notes"
   ```

## 🖥️ Usage

### Workflow Overview
1. **Input**: User drops supported files into monitored folder  
2. **Processing**:  
   - Video files → Audio extraction → Transcription → AI summary  
   - Text/DOCX files → Direct processing → AI summary  
3. **Output**: Cleanly formatted DOCX file generated in root folder  
4. **Cleanup**: Original files moved to "Processed Files" subfolder

### For Meetings
1. Drop files into:  
   `E:\MeetingNotesGenerator\Drop Here to Generate Meeting Notes`  
   *Supported formats: .mp4, .mkv, .mp3, .txt, .docx*

2. Run:  
   ```bash
   python NotesGenerator_Meetings.py
   ```

3. Output files will appear in:  
   `E:\MeetingNotesGenerator\[Input Filename]_notes.docx`

### For Lecture Modules
1. Drop files into:  
   `E:\ModuleNotesGenerator\Drop Here to Generate Module Notes`

2. Run:  
   ```bash
   python NotesGenerator_Modules.py
   ```

3. Output files will appear in:  
   `E:\ModuleNotesGenerator\[Input Filename]_notes.docx`

## Folder Structure
```
Root Folder/
├── Drop Here to Generate Meeting Notes/  # Input folder for meetings
├── Drop Here to Generate Module Notes/   # Input folder for modules
├── Processed Files - DELETE IF YOU'RE DONE/  # Auto-created
└── [Generated Notes].docx                # Output files
```

## 🔍 Troubleshooting

**Common Issues**  
- ❗ "File not processed": Ensure files are fully copied before processing starts  
- ❗ "API error": Verify OpenAI key format in `.env` and account quota  
- ❗ "FFmpeg/Pandoc missing": Confirm system PATH includes these utilities  
- ❗ "Permission issues": Run scripts as administrator on Windows

**Logs Location**  
- Meeting logs: `logs/Meetings_processing_log.txt`  
- Module logs: `logs/Modules_processing_log.txt`  

## 🤝 Contributing
1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/improvement`)  
3. Submit a pull request  

## 📜 License
MIT License - See [LICENSE](LICENSE)  

---

**Credits**  
- Audio transcription: [OpenAI Whisper](https://github.com/openai/whisper)  
- AI summaries: [GPT-4](https://openai.com/gpt-4)  
- DOCX conversion: [Pandoc](https://pandoc.org/)  
- Audio extraction: [FFmpeg](https://ffmpeg.org/)
```