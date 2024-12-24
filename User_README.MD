# Meeting Notes Generator - ReadMe

## Overview
This system automatically monitors a shared folder for new files, transcribes audio or video content, and generates detailed meeting notes in Word Document (.docx) format. The supported file types are:
- Video: `.mp4`, `.mkv`
- Audio: `.mp3`
- Text: `.txt`, `.docx`

## How to Use
1. **Drop Files**:
   - Place any supported file into the "Drop Here to Generate Meeting Notes" folder.
   - No further action is required; the system will automatically detect and process your files.

2. **Processing**:
   - The system will extract audio (if necessary), transcribe the content, and generate detailed meeting notes.
   - Once processed, your original file will be moved to a folder named "Processed Files - DELETE IF YOU'RE DONE," located one level above the shared folder.

3. **Retrieve Notes**:
   - Generated notes will be saved as `.docx` files in the root folder titled "MeetingNotesGenerator."

## How to Record and Transcribe Meetings from Microsoft Teams
If your meeting is conducted on Microsoft Teams, you can easily generate a transcription by following these steps:

1. **Schedule a Meeting**:
   - Recording and transcription options are only available in scheduled meetings, not calls.
   - You can schedule a meeting via Microsoft Outlook by creating a calendar event and inviting participants.

2. **Start Transcription**:
   - During the meeting, click on **More > Record and Transcribe > Start transcription**.
   - It is recommended to use transcription only (without video recording) for this notes generator as it is faster to process.

3. **Download the Transcription or Video**:
   - After the meeting, the transcription or video can be downloaded by the meeting organizer.
   - Go to the **Chat** tab for the meeting and click **View Recap** within the meeting chat to access the files.

## Features
- **Automatic File Monitoring**: Continuously monitors the folder for new files.
- **Audio Transcription**: Converts audio or video to text using state-of-the-art transcription models.
- **Detailed Notes Generation**: Creates comprehensive, detailed meeting notes.
- **Folder Management**: Automatically organizes processed files into designated folders.

## Privacy and Data Usage
By default, OpenAI retains and uses user data for model training. However, OpenAI data retention and training are **disabled** for the account running this system. This configuration was set through the [OpenAI Privacy Center](https://platform.openai.com/account/data-settings). As a result:
- Your data is **not retained** by OpenAI.
- Your data is **not used** for training OpenAI models.

This system complies with company privacy policies, and your files will remain confidential.

## Troubleshooting
- **File Not Supported**:
  - Ensure your file has one of the supported extensions: `.mp4`, `.mkv`, `.mp3`, `.txt`, or `.docx`.
- **Missing File**:
  - If your file does not appear in the "MeetingNotesGenerator" folder, contact the system administrator.

## Contact
For further assistance, contact Reagan or the IT department.

