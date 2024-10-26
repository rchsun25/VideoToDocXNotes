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
def extract_audio(audio_file):
    print("\nExtracting audio from video file:", audio_file)
    mp3_audio_file_name = pipelineFile.split(".")[0] + ".mp3"
    ffmpeg.input(audio_file).output(mp3_audio_file_name, loglevel="quiet").run(overwrite_output=True)
    audio_file = mp3_audio_file_name

    #move video file to PROCESSED VIDEOS folder
    work_folder = os.path.join(audio_folder, "PROCESSED VIDEOS")
    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
    os.replace(pipelineFile, os.path.join(work_folder, os.path.basename(pipelineFile)))

    return audio_file

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
    transcription_path = pipelineFile.split(".")[0] + "_transcription.txt"
    with open(transcription_path, "w", encoding="utf-8") as text_file:
        text_file.write(transcription_text)
    return transcription_text, transcription_path

#Process transcript to summary with openai
def openai_summary(transcription_text):

    #Need to set OPENAI_API_KEY as environment variable

    #read api key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key = api_key)

    completion = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", 
             "content": "You are a professor and instructor who is knowledgable about the subject matter. You are creating detailed lesson notes based on a video transcript."},
            {"role": "user", 
            "content": "The following is a transcript of a lesson. Based on this video, create a detailed document that is so detailed that the reader will not need to watch the video anymore. Do not mention that the reader does not need to watch the video. Use markdown to format your notes. This is the transcript: " + transcription_text}
        ]
    )

    print("\nSummary of the transcript:")
    print(completion.choices[0].message.content)

    #write summary to .md file
    #summary file path
    md_path = pipelineFile.split(".")[0] + "_notes.md"
    with open(md_path, "w", encoding="utf-8") as text_file:
        text_file.write(completion.choices[0].message.content)

    print("\nMD summary saved to:", md_path)

    #save as .docx file
    docx_path = pipelineFile.split(".")[0] + "_notes.docx"
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
        #os.replace(md_path, os.path.join(work_folder, os.path.basename(md_path)))
        #delete the .md file
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
    if pipelineFile.endswith(('.mp4','.mkv')):
        pipelineFile = extract_audio(pipelineFile)

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
    md_path, docx_path = openai_summary(transcription_text)

    #Move files to WORK and NOTES folders
    MoveFilestoFolders(audio_folder, pipelineFile, transcription_path, md_path, docx_path)

print("\nProcess completed.")