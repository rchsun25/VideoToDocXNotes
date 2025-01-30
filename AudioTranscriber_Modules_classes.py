import os
import time
import warnings
import torch
import whisper
from openai import OpenAI
import pypandoc
import ffmpeg
import tkinter as tk
from tkinter import messagebox
import watchdog.events
import watchdog.observers
from ctypes import windll

warnings.filterwarnings("ignore")

class UI:
    @staticmethod
    def show_error(message):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", message)
        root.destroy()

class FileManager:
    def __init__(self, input_folder, processed_folder):
        self.input_folder = input_folder
        self.root_folder = os.path.dirname(input_folder)
        self.processed_folder = processed_folder
        
        # Ensure both folders exist
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.processed_folder, exist_ok=True)

    @staticmethod
    def uniquify(path):
        filename, extension = os.path.splitext(path)
        counter = 1
        while os.path.exists(path):
            path = f"{filename} ({counter}){extension}"
            counter += 1
        return path

    @staticmethod
    def is_file_ready(file_path):
        if not isinstance(file_path, str):
            file_path = file_path.decode('utf-8')
        
        GENERIC_WRITE = 1 << 30
        FILE_SHARE_READ = 0x00000001
        OPEN_EXISTING = 3
        FILE_ATTRIBUTE_NORMAL = 0x80
        
        h_file = windll.Kernel32.CreateFileW(
            file_path, GENERIC_WRITE, FILE_SHARE_READ,
            None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None
        )
        if h_file != -1:
            windll.Kernel32.CloseHandle(h_file)
            return True
        return False

    def move_to_processed(self, src_path):
        """Move files to processed folder with unique naming"""
        if os.path.exists(src_path):
            dest_path = os.path.join(
                self.processed_folder,
                os.path.basename(src_path)
            )
            dest_path = self.uniquify(dest_path)
            os.replace(src_path, dest_path)

    def move_to_root(self, src_path):
        """Move final DOCX to root folder with unique naming"""
        if os.path.exists(src_path):
            dest_path = os.path.join(
                self.root_folder,
                os.path.basename(src_path)
            )
            dest_path = self.uniquify(dest_path)
            os.replace(src_path, dest_path)

class AudioProcessor:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def extract_audio(self, video_path):
        mp3_path = os.path.splitext(video_path)[0] + ".mp3"
        ffmpeg.input(video_path).output(mp3_path, loglevel="quiet").run(overwrite_output=True)
        self.file_manager.move_to_processed(video_path)
        return mp3_path

class Transcriber:
    def __init__(self, model_size="small"):
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.model_size).to(self.device)

    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path, language="en")
        return result["text"]

    @staticmethod
    def read_text_file(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def read_docx_file(file_path):
        return pypandoc.convert_file(file_path, 'plain', format='docx')

class SummaryGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_notes(self, transcription, base_path):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a detailed mechanical engineering notetaker knowledgable about the subject matter. You are creating detailed lecture module notes based on a lecture transcript."
            }, {
                "role": "user",
                "content": f"Module Notes: Write comprehensive notes for a lecture module. Include: Module Title: Provide the title of the module. Module Description: Summarize the module's content. Learning Objectives: List the learning objectives. Key Concepts: Detail the key concepts. Detailed Notes: Take detailed notes and include everything. Make this section as long as possible so no details are left out. Examples: Provide examples to illustrate the concepts. Exercises: Include exercises to reinforce learning. References: List any references used.  Use markdown to format your notes. Transcript: {transcription}"
            }]
        )
        
        md_path = f"{base_path}_notes.md"
        docx_path = f"{base_path}_notes.docx"
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)
        
        pypandoc.convert_file(md_path, 'docx', outputfile=docx_path)
        os.remove(md_path)
        
        return docx_path

class ProcessingPipeline:
    def __init__(self, input_folder, processed_folder, api_key):
        self.file_manager = FileManager(input_folder, processed_folder)
        self.root_folder = self.file_manager.root_folder
        self.audio_processor = AudioProcessor(self.file_manager)
        self.transcriber = Transcriber()
        self.summary_generator = SummaryGenerator(api_key)
        self.ui = UI()

    def process_file(self, file_path):
        processing_file = os.path.join(self.root_folder, "PROCESSING - PLEASE WAIT.txt")
        try:
            # Create processing indicator
            with open(processing_file, "w") as f:
                f.write(f"Processing: {os.path.basename(file_path)}")
            
            base_path = os.path.splitext(file_path)[0]
            
            if file_path.endswith(('.mp4', '.mkv')):
                file_path = self.audio_processor.extract_audio(file_path)
            
            if file_path.endswith('.mp3'):
                transcription = self.transcriber.transcribe(file_path)
            elif file_path.endswith('.txt'):
                transcription = self.transcriber.read_text_file(file_path)
            elif file_path.endswith('.docx'):
                transcription = self.transcriber.read_docx_file(file_path)
            else:
                self.ui.show_error("Unsupported file type")
                return
            
            docx_path = self.summary_generator.generate_notes(transcription, base_path)
            
            # Move files to appropriate locations
            self.file_manager.move_to_root(docx_path)
            self.file_manager.move_to_processed(file_path)

        except Exception as e:
            self.ui.show_error(str(e))
        finally:
            # Clean up processing indicator
            if os.path.exists(processing_file):
                os.remove(processing_file)
     
                
class FileMonitor:
    def __init__(self, folder, pipeline):
        self.folder = folder
        self.pipeline = pipeline
        self.observer = watchdog.observers.Observer()
        self.event_handler = self.create_handler()

    def create_handler(self):
        patterns = ["*.mp4", "*.mkv", "*.mp3", "*.txt", "*.docx"]
        handler = watchdog.events.PatternMatchingEventHandler(
            patterns=patterns,
            ignore_directories=True,
            case_sensitive=False
        )
        handler.on_modified = self.handle_event
        return handler

    def handle_event(self, event):
        if not event.is_directory and self.is_valid_file(event.src_path):
            self.process_file(event.src_path)

    def is_valid_file(self, path):
        return os.path.dirname(path) == self.folder and os.path.isfile(path)

    def process_file(self, file_path):
        while not FileManager.is_file_ready(file_path):
            time.sleep(1)
        self.pipeline.process_file(file_path)

    def start(self):
        self.observer.schedule(self.event_handler, self.folder, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    INPUT_FOLDER = "E:\\ModuleNotesGenerator\\Drop Here to Generate Module Notes"
    PROCESSED_FOLDER = os.path.join(INPUT_FOLDER, "..", "Processed Files - DELETE IF YOU'RE DONE")
    API_KEY = os.getenv("OPENAI_API_KEY")

    pipeline = ProcessingPipeline(
        input_folder=INPUT_FOLDER,
        processed_folder=PROCESSED_FOLDER,
        api_key=API_KEY
    )

    monitor = FileMonitor(INPUT_FOLDER, pipeline)
    monitor.start()