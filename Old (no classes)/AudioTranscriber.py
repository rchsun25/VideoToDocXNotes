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

import watchdog.events
import watchdog.observers
import time

from ctypes import windll

warnings.filterwarnings("ignore")

#initialize global variables
#audio_folder = "C:\\Users\\Reagan\\Desktop\\MeetingNotesGenerator\\Drop Here to Generate Meeting Notes" #working dir
audio_folder = "E:\\MeetingNotesGenerator\\Drop Here to Generate Meeting Notes" #working dir
pipelineFile = ""
transcription_path = ""
transcription_text = ""
md_path = ""
docx_path = ""


#Watchdog class to monitor the folder for new files
class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=["*.mp4", "*.mkv", "*.mp3", "*.txt", "*.docx"], ignore_directories=True, case_sensitive=False)

    def on_modified(self, event):
        print("\nNew file created:", event.src_path)
        #Process the new file
        run()

#Extract audio from video file
def extract_audio(audio_file):
    global pipelineFile
    print("\nExtracting audio from video file:", audio_file)
    mp3_audio_file_name = pipelineFile.split(".")[0] + ".mp3"
    ffmpeg.input(audio_file).output(mp3_audio_file_name, loglevel="quiet").run(overwrite_output=True)
    audio_file = mp3_audio_file_name

    #move video file to Processed Files folder
    work_folder = os.path.join(audio_folder, '..', "Processed Files - DELETE IF YOU'RE DONE")
    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
    os.replace(pipelineFile, os.path.join(work_folder, os.path.basename(pipelineFile)))

    return audio_file

# TRANSFORMERS MODEL: whisper-small
def transcribe_audio(audio_file_path):
    global pipelineFile

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
    global pipelineFile

    #Need to set OPENAI_API_KEY as environment variable

    #read api key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key = api_key)

    completion = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", 
             "content": "You are a detailed mechanical engineering notetaker knowledgable about the subject matter. You are creating detailed meeting notes based on a meeting transcript."},
            {"role": "user",                                                                                      
             "content":
                "Meeting Minutes: Develop comprehensive meeting minutes including: Attendees: List all participants. Brief Summary: Provide a brief summary of the discussion. Action Items: Specify tasks assigned, responsible individuals, and deadlines. Discussion Points: Detail the topics discussed, including any debates, alternate viewpoints, problem statements, and current situations. Make this section as long as possible so no details are left out. Decisions Made: Record all decisions, including who made them and the rationale. Data & Insights: Display any data presented or insights shared that influenced the meeting\'s course, including any clarifications. Follow-Up: Note any agreed-upon follow-up meetings or checkpoints. Include all details in the notes, including all numbers and equations discussed. Do not summarize anything for the meeting notes. If there are empty sections just remove them. Write notes that are so detailed that the reader will not have to watch the video at all. Use markdown to format your notes. This is the transcript: " + transcription_text
            }
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
    uniquify(docx_path)
    pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
    print("DOCX summary saved to:", docx_path)
    
    return md_path, docx_path

#Move .txt and .mp3 files to a WORK folder
#Move .docx file to a NOTES folder
#Create WORK and NOTES folders if they don't exist
def MoveFilestoFolders(audio_folder, audio_file_path, transcription_path, md_path, docx_path):
    work_folder = os.path.join(audio_folder, '..', "Processed Files - DELETE IF YOU'RE DONE")
    # notes_folder = os.path.join(audio_folder, "NOTES")

    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
    # if not os.path.exists(notes_folder):
    #     os.makedirs(notes_folder)

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
        new_docx_path = uniquify(os.path.join(work_folder,'..', os.path.basename(docx_path)))
        os.replace(docx_path, new_docx_path)
    
            
    print("\nFiles moved to Processed Files folder.")

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

def is_file_copy_finished(file_path):
    finished = False

    GENERIC_WRITE         = 1 << 30
    FILE_SHARE_READ       = 0x00000001
    OPEN_EXISTING         = 3
    FILE_ATTRIBUTE_NORMAL = 0x80

    if not isinstance(file_path, str):
        file_path_unicode = file_path.decode('utf-8')
    else:
        file_path_unicode = file_path

    h_file = windll.Kernel32.CreateFileW(file_path_unicode, GENERIC_WRITE, FILE_SHARE_READ, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)

    if h_file != -1:
        windll.Kernel32.CloseHandle(h_file)
        finished = True

    #print('is_file_copy_finished: ' + str(finished))
    return finished


def main():
    #global variables
    global audio_folder
    global pipelineFile
    global transcription_path
    global transcription_text
    global md_path
    global docx_path

    audio_folder = os.path.dirname(pipelineFile)

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

def run():

    global pipelineFile

    #Get files in the folder with full paths
    filesList = os.listdir(audio_folder)

    #Process each file in the folder
    while filesList:
        file = filesList.pop(0)
        #check if file type is supported
        if not file.endswith(('.mp4','.mkv','.mp3','.txt','.docx')):
            #make a text file one folder up to show that file type is not supported
            with open(os.path.join(audio_folder,'..',"FILE TYPE NOT SUPPORTED.txt"), "w") as text_file:
                text_file.write("File type not supported: " + file)
            print("File type not supported.")
            continue

        pipelineFile = audio_folder + "\\" + file #construct full path

        #check if file is done copying
        while not is_file_copy_finished(pipelineFile):
            print("File is still copying. Waiting...")
            time.sleep(1)

        print("\nProcessing file:", pipelineFile)
        #make a text file one folder up to show that  the file is being processed
        with open(os.path.join(audio_folder,'..',"PROCESSING - PLEASE WAIT.txt"), "w") as text_file:
            text_file.write("Processing file: " + pipelineFile)
        main()

    #delete the processing file if exists
    if os.path.exists(os.path.join(audio_folder,'..',"PROCESSING - PLEASE WAIT.txt")):
        os.remove(os.path.join(audio_folder,'..',"PROCESSING - PLEASE WAIT.txt"))
    print("\nProcess completed.")

if __name__ == "__main__":
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    #Watchdog - monitor the folder for new files
    observer = watchdog.observers.Observer()
    observer.schedule(Handler(), path=audio_folder)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    #run() #run the script without watchdog