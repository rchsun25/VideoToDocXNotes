#Github: https://github.com/rchsun25/VideoToDocXNotes
#Requirements - Need to install Pandoc and ffmpeg

import os
import warnings
import whisper
from openai import OpenAI
import torch
from tkinter import filedialog
from tkinter import messagebox
import pypandoc
import ffmpeg

warnings.filterwarnings("ignore")

#Extract audio from video file

def extract_audio(video_file, audio_folder):
    """Extract the audio track from a video file."""
    print("\nExtracting audio from video file:", video_file)
    mp3_audio_file_name = os.path.splitext(video_file)[0] + ".mp3"
    ffmpeg.input(video_file).output(mp3_audio_file_name, loglevel="quiet").run(overwrite_output=True)

    # move original video to a processed folder
    work_folder = os.path.join(audio_folder, "PROCESSED VIDEOS")
    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
    os.replace(video_file, os.path.join(work_folder, os.path.basename(video_file)))

    return mp3_audio_file_name

# TRANSFORMERS MODEL: whisper-small
def transcribe_audio(audio_file_path):
    """Transcribe an audio file using Whisper."""
    print("\nTranscribing audio file:", audio_file_path)

    #Check if GPU is available
    device = "cpu"
    if torch.cuda.is_available() :
        torch.cuda.init()
        device = "cuda" 
    print("Device:", device)

    #Load the model
    model_size = "small"
    model = whisper.load_model(model_size).to(device)
    language = "en"

    #Transcribe the audio file
    transcription_results = model.transcribe(audio_file_path, language=language)
    transcription_text = transcription_results.get('text', "No transcription results found.")
    
# PRINT TRANSCRIPTION
    print("\nTranscription Results:\n", transcription_text) 
    #write transcription to text file
    #transcription file path

    transcription_path = os.path.splitext(audio_file_path)[0] + "_transcription.txt"

    with open(transcription_path, "w", encoding="utf-8") as text_file:
        text_file.write(transcription_text)
    return transcription_text, transcription_path

#Process transcript to summary with openai
def openai_summary(transcription_text, base_path):

    #Need to set OPENAI_API_KEY as environment variable

    #read api key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key = api_key)

    completion = client.chat.completions.create(
        model = "gpt-4o",
        # messages = [
        #     {"role": "system", 
        #      "content": "You are a professor and instructor who is knowledgeable about the subject matter. You are creating detailed lesson notes based on a video transcript."},
        #     {"role": "user", 
        #     "content": "The following is a transcript of a lesson. Based on this video, create a detailed document that is so detailed that the reader will not need to watch the video anymore. Do not mention that the reader does not need to watch the video. Use markdown to format your notes. This is the transcript: " + transcription_text}
        # ]
    #    messages = [
    #         {"role": "system", 
    #          "content": "You are a mechanical engineering project manager with 20 years of experience who is really good at taking detailed technical notes."},
    #         {"role": "user", 
    #         "content": "You will be provided a transcript from a video. Review it and create detailed meeting notes, highlights, and an action plan. Include all details in the notes, including all numbers and equations discussed. Do not summarize anything for the meeting notes. Write notes that are so detailed that the reader will not have to watch the video at all. Use markdown to format your notes. This is the transcript: " + transcription_text}                                                                                                                                                                                                                                                                                                                                                                                                                 
    #     ]
        messages = [
            {"role": "system", 
            "content": "You are a detailed mechanical engineering notetaker knowledgeable about the subject matter. You are creating detailed meeting notes based on a meeting transcript."},
            {"role": "user",                                                                                      
             "content":
                "Meeting Minutes: Develop comprehensive meeting minutes including: Attendees: List all participants. Discussion Points: Detail the topics discussed, including any debates, alternate viewpoints, problem statements, and current situations. Decisions Made: Record all decisions, including who made them and the rationale. Action Items: Specify tasks assigned, responsible individuals, and deadlines. Data & Insights: Display any data presented or insights shared that influenced the meeting\'s course, including any clarifications. Follow-Up: Note any agreed-upon follow-up meetings or checkpoints. Include all details in the notes, including all numbers and equations discussed. Do not summarize anything for the meeting notes. Write notes that are so detailed that the reader will not have to watch the video at all. Use markdown to format your notes. This is the transcript: " + transcription_text
            }
        ]
    )

    print("\nSummary of the transcript:")
    print(completion.choices[0].message.content)

    #write summary to .md file
    #summary file path

    md_path = base_path + "_notes.md"

    with open(md_path, "w", encoding="utf-8") as text_file:
        text_file.write(completion.choices[0].message.content)

    print("\nMD summary saved to:", md_path)

    #save as .docx file

    docx_path = base_path + "_notes.docx"

    pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    print("DOCX summary saved to:", docx_path)
    
    return md_path, docx_path

# Move .txt and .mp3 files to a WORK folder
# Move .docx file to a NOTES folder
# Delete the temporary .md file and create WORK and NOTES folders if they do not exist
def MoveFilestoFolders(audio_folder, audio_file_path, transcription_path, md_path, docx_path):
    work_folder = os.path.join(audio_folder, "WORK")
    notes_folder = os.path.join(audio_folder, "NOTES")

    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
    if not os.path.exists(notes_folder):
        os.makedirs(notes_folder)

    #Move files to WORK and NOTES folders
    #if file exists, replace it
    if os.path.exists(audio_file_path):
        os.replace(audio_file_path, os.path.join(work_folder, os.path.basename(audio_file_path)))
    if os.path.exists(transcription_path):
        os.replace(transcription_path, os.path.join(work_folder, os.path.basename(transcription_path)))
    if os.path.exists(md_path):
        # Delete the temporary Markdown file
        os.remove(md_path)
    if os.path.exists(docx_path):
        os.replace(docx_path, os.path.join(notes_folder, os.path.basename(docx_path)))
    
            
    print("\nFiles moved to WORK and NOTES folders.")


########################## PROGRAM STARTS HERE ####################################

#GET THE AUDIO FILE PATH

root = filedialog.Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()

files = filedialog.askopenfilenames(parent=root,
                                    filetypes=[("Video/Audio Files", "*.mp4 *.mkv *.mp3"), ("Transcript", "*.txt *.docx")])
filesList = list(files)
if not filesList:
    messagebox.showerror(title="Error", message="No file selected.")
    print("No file selected.")
    exit()

while filesList:
    pipelineFile = filesList.pop(0)
    print("\nProcessing file:", pipelineFile)

    audio_folder = os.path.dirname(pipelineFile)

    transcription_path = ""
    transcription_text = ""
    md_path = ""
    docx_path = ""

    #Extract audio if file is a video
    if pipelineFile.endswith(('.mp4', '.mkv')):
        pipelineFile = extract_audio(pipelineFile, audio_folder)

    base_path = os.path.splitext(pipelineFile)[0]

    if pipelineFile.endswith('.mp3'):
        #SEARCH FOR THE AUDIO IN THE FILE PATH AND EXECUTE TRANSCRIPTION
        transcription_text,transcription_path = transcribe_audio(pipelineFile)
    if pipelineFile.endswith(('.txt')):
        #READ TRANSCRIPTION FROM THE TEXT FILE
        with open(pipelineFile, "r", encoding="utf-8") as text_file:
            transcription_text = text_file.read()
    if pipelineFile.endswith('.docx'):
        #READ TRANSCRIPTION FROM THE DOCX FILE
        transcription_text = pypandoc.convert_file(pipelineFile, 'plain', format='docx')

    #If no transcription text found, something went wrong, exit
    if not transcription_text:
        messagebox.showerror(title="Error", message="File type not supported.")
        print("\nFile type not supported.")
        exit()
    #Process transcript to summary with openai
    md_path, docx_path = openai_summary(transcription_text, base_path)

    #Move files to WORK and NOTES folders
    MoveFilestoFolders(audio_folder, pipelineFile, transcription_path, md_path, docx_path)

print("\nProcess completed.")