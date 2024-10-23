#Github: https://github.com/rchsun25/VideoToDocXNotes

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

#Requirements
#Need to install Pandoc

#Extract audio from video file
def extract_audio(audio_file_path):
    print("\nExtracting audio from video file:", audio_file_path)
    mp3_audio_file_name = audio_file_name.split(".")[0] + ".mp3"
    ffmpeg.input(audio_file_path).output(mp3_audio_file_name, loglevel="quiet").run(overwrite_output=True)
    audio_file_path = mp3_audio_file_name

    #move video file to PROCESSED VIDEOS folder
    work_folder = os.path.join(audio_folder, "PROCESSED VIDEOS")
    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
    os.replace(audio_file_name, os.path.join(work_folder, os.path.basename(audio_file_name)))

    return audio_file_path

# TRANSFORMERS MODEL: whisper-small
def transcribe_audio(audio_file_path):
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
    transcription_path = audio_file_name.split(".")[0] + "_transcription.txt"
    with open(transcription_path, "w", encoding="utf-8") as text_file:
        text_file.write(transcription_text)
    return transcription_text, transcription_path

#Process transcript to summary with openai
def openai_summary(transcription_text):

    #read api key from txt file
    with open("C:/Users/reaga/Downloads/audioTest/chatgpt_key.txt", "r") as file:
        api_key = file.read().strip()

    client = OpenAI(api_key = api_key)

    completion = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role": "system", "content": "You are a detailed and thorough notetaker. You will be provided a transcript from a video. Take notes based on this transcript. Give an overall summary at the top, followed by detailed notes on what is happening in the video. The headings should be Summary and Notes. Use markdown to format your notes."},
            {"role": "user", 
            "content": transcription_text}
        ]
    )

    print("\nSummary of the transcript:")
    print(completion.choices[0].message.content)

    #write summary to .md file
    #summary file path
    md_path = audio_file_name.split(".")[0] + "_notes.md"
    with open(md_path, "w", encoding="utf-8") as text_file:
        text_file.write(completion.choices[0].message.content)

    print("\nMD summary saved to:", md_path)

    #save as .docx file
    docx_path = audio_file_name.split(".")[0] + "_notes.docx"
    pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    print("DOCX summary saved to:", docx_path)
    
    return md_path, docx_path

#Move .txt and .mp3 files to a WORK folder
#Move .docx file to a NOTES folder
#Create WORK and NOTES folders if they don't exist
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
        os.replace(transcription_path, os.path.join(work_folder, os .path.basename(transcription_path)))
    if os.path.exists(md_path):
        os.replace(md_path, os.path.join(work_folder, os.path.basename(md_path)))
    if os.path.exists(docx_path):
        os.replace(docx_path, os.path.join(notes_folder, os.path.basename(docx_path)))
    
            
    print("\nFiles moved to WORK and NOTES folders.")


########################## PROGRAM STARTS HERE ####################################

#GET THE AUDIO FILE PATH

root = filedialog.Tk()
root.wm_attributes('-topmost', 1)
root.withdraw()

files = filedialog.askopenfilenames(parent=root,
                                    filetypes=[("Video/Audio Files", "*.mp4 *.mkv *.mp3"), ("Transcript", "*.txt")])
filesList = list(files)
if not filesList:
    messagebox.showerror(title="Error", message="No file selected.")
    print("No file selected.")
    exit()

while filesList:
    audio_file_name = filesList.pop(0)
    print("\nProcessing file:", audio_file_name)

    audio_folder = os.path.dirname(audio_file_name)
    audio_file_path = os.path.join(audio_folder, audio_file_name)

    transcription_path = ""
    transcription_text = ""
    md_path = ""
    docx_path = ""

    #Extract audio if file is a video
    if audio_file_name.endswith(".mp4") or audio_file_name.endswith(".mkv"):
        audio_file_path = extract_audio(audio_file_path)

    if not audio_file_name.endswith(".txt"):
        #SEARCH FOR THE AUDIO IN THE FILE PATH AND EXECUTE TRANSCRIPTION
        transcription_text,transcription_path = transcribe_audio(audio_file_path)
    else:
        #READ TRANSCRIPTION FROM THE TEXT FILE
        with open(audio_file_path, "r", encoding="utf-8") as text_file:
            transcription_text = text_file.read()

    #Process transcript to summary with openai
    md_path, docx_path = openai_summary(transcription_text)

    #Move files to WORK and NOTES folders
    MoveFilestoFolders(audio_folder, audio_file_path, transcription_path, md_path, docx_path)

print("\nProcess completed.")