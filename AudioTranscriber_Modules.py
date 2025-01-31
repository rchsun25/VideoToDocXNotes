#Github: https://github.com/rchsun25/VideoToDocXNotes
#Requirements - Need to install Pandoc and ffmpeg

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
from datetime import datetime

warnings.filterwarnings("ignore")

# Logging setup
LOG_FILE = "Modules_processing_log.txt"
os.makedirs("logs", exist_ok=True)
LOG_PATH = os.path.join("logs", LOG_FILE)

def log_event(message):
    """Logs events with timestamp to both console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)  # Print to console
    with open(LOG_PATH, "a") as log_file:
        log_file.write(log_message + "\n")  # Write to log file

def watchdog_heartbeat():
    """Prints a heartbeat message every 30 minutes to confirm watchdog is running."""
    while True:
        log_event("Watchdog is still running...")
        time.sleep(1800)  # 30 minutes

# UI class for displaying messages to the user
class UI:
    @staticmethod
    def show_error(message):
        """Displays an error message to the user."""
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", message)
        root.destroy()

# FileManager class for handling file operations
class FileManager:
    def __init__(self, input_folder, processed_folder):
        """Initializes file manager with input and processed folders."""
        self.input_folder = input_folder
        self.root_folder = os.path.dirname(input_folder)
        self.processed_folder = processed_folder
        
        # Ensure input folder exists
        os.makedirs(self.input_folder, exist_ok=True)
        log_event(f"Initialized FileManager with input folder: {input_folder}")

    @staticmethod
    def uniquify(path):
        """Ensures unique filenames by appending a counter if the file exists."""
        filename, extension = os.path.splitext(path)
        counter = 1
        while os.path.exists(path):
            path = f"{filename} ({counter}){extension}"
            counter += 1
        return path

    @staticmethod
    def is_file_ready(file_path):
        """Checks if a file is ready for processing by attempting to open it."""
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
        """Moves files to the processed folder with unique naming."""
        os.makedirs(self.processed_folder, exist_ok=True)
        log_event(f"Created processed folder: {self.processed_folder}")

        if os.path.exists(src_path):
            dest_path = os.path.join(
                self.processed_folder,
                os.path.basename(src_path)
            )
            dest_path = self.uniquify(dest_path)
            os.replace(src_path, dest_path)
            log_event(f"Moved {src_path} to processed folder: {dest_path}")

    def move_to_root(self, src_path):
        """Moves final DOCX to the root folder with unique naming."""
        if os.path.exists(src_path):
            dest_path = os.path.join(
                self.root_folder,
                os.path.basename(src_path)
            )
            dest_path = self.uniquify(dest_path)
            os.replace(src_path, dest_path)
            log_event(f"Moved {src_path} to root folder: {dest_path}")

# AudioProcessor class for extracting audio from video files
class AudioProcessor:
    def __init__(self, file_manager):
        """Initializes the audio processor with a file manager."""
        self.file_manager = file_manager

    def extract_audio(self, video_path):
        """Extracts audio from a video file and saves it as an MP3."""
        mp3_path = os.path.splitext(video_path)[0] + ".mp3"
        log_event(f"Extracting audio from video file: {video_path}")
        ffmpeg.input(video_path).output(mp3_path, loglevel="quiet").run(overwrite_output=True)
        self.file_manager.move_to_processed(video_path)
        log_event(f"Audio extracted and saved as: {mp3_path}")
        return mp3_path

# Transcriber class for transcribing audio and text files
class Transcriber:
    def __init__(self, model_size="small"):
        """Initializes the transcriber with a Whisper model."""
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.model_size).to(self.device)
        log_event(f"Initialized Transcriber with model size: {model_size} on device: {self.device}")

    def transcribe(self, audio_path):
        """Transcribes an audio file using the Whisper model."""
        log_event(f"Transcribing audio file: {audio_path}")
        result = self.model.transcribe(audio_path, language="en")
        return result["text"]

    @staticmethod
    def read_text_file(file_path):
        """Reads text from a text file."""
        log_event(f"Reading text file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def read_docx_file(file_path):
        """Reads text from a DOCX file."""
        log_event(f"Reading DOCX file: {file_path}")
        return pypandoc.convert_file(file_path, 'plain', format='docx')

# SummaryGenerator class for generating notes using OpenAI
class SummaryGenerator:
    def __init__(self, api_key):
        """Initializes the summary generator with an OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        log_event("Initialized SummaryGenerator with OpenAI API")

    def generate_notes(self, transcription, base_path):
        """Generates notes from a transcription using OpenAI."""
        log_event(f"Generating notes for transcription from: {base_path}")
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
        log_event(f"Generated notes saved as: {docx_path}")
        return docx_path

# ProcessingPipeline class for handling the main processing workflow
class ProcessingPipeline:
    def __init__(self, input_folder, processed_folder, api_key):
        """Initializes the processing pipeline with folders and API key."""
        self.file_manager = FileManager(input_folder, processed_folder)
        self.root_folder = self.file_manager.root_folder
        self.audio_processor = AudioProcessor(self.file_manager)
        self.transcriber = Transcriber()
        self.summary_generator = SummaryGenerator(api_key)
        self.ui = UI()
        log_event("Initialized ProcessingPipeline")

    def process_file(self, file_path):
        """Processes a file through the entire pipeline."""
        processing_file = os.path.join(self.root_folder, "PROCESSING - PLEASE WAIT.txt")
        try:
            # Create processing indicator
            with open(processing_file, "w+") as f:
                f.write(f"Processing: {os.path.basename(file_path)}")
            log_event(f"Started processing file: {file_path}")

            base_path = os.path.splitext(file_path)[0]
            
            if file_path.endswith(('.mp4', '.mkv')):
                log_event(f"Extracting audio from video file: {file_path}")
                file_path = self.audio_processor.extract_audio(file_path)
            
            if file_path.endswith('.mp3'):
                log_event(f"Transcribing audio file: {file_path}")
                transcription = self.transcriber.transcribe(file_path)
            elif file_path.endswith('.txt'):
                log_event(f"Reading text file: {file_path}")
                transcription = self.transcriber.read_text_file(file_path)
            elif file_path.endswith('.docx'):
                log_event(f"Reading DOCX file: {file_path}")
                transcription = self.transcriber.read_docx_file(file_path)
            else:
                error_msg = f"Unsupported file type: {file_path}"
                log_event(error_msg)
                self.ui.show_error(error_msg)
                return
            
            log_event(f"Generating notes for file: {file_path}")
            docx_path = self.summary_generator.generate_notes(transcription, base_path)
            
            # Move files to appropriate locations
            log_event(f"Moving files to final locations for: {file_path}")
            self.file_manager.move_to_root(docx_path)
            self.file_manager.move_to_processed(file_path)
            log_event(f"Successfully processed file: {file_path}")

        except Exception as e:
            error_msg = f"Error processing file {file_path}: {str(e)}"
            log_event(error_msg)
            self.ui.show_error(error_msg)
        finally:
            # Clean up processing indicator
            if os.path.exists(processing_file):
                os.remove(processing_file)
                log_event(f"Removed processing indicator for: {file_path}")

# FileMonitor class for monitoring the input folder for new files
class FileMonitor:
    def __init__(self, folder, pipeline):
        """Initializes file monitoring with folder and processing pipeline."""
        self.folder = folder
        self.pipeline = pipeline
        self.observer = watchdog.observers.Observer()
        self.event_handler = self.create_handler()
        log_event(f"Initialized FileMonitor for folder: {folder}")

    def create_handler(self):
        """Creates a watchdog event handler for supported file patterns."""
        patterns = ["*.mp4", "*.mkv", "*.mp3", "*.txt", "*.docx"]
        handler = watchdog.events.PatternMatchingEventHandler(
            patterns=patterns,
            ignore_directories=True,
            case_sensitive=False
        )
        handler.on_modified = self.handle_event
        return handler

    def handle_event(self, event):
        """Handles file modification events."""
        if not event.is_directory and self.is_valid_file(event.src_path):
            log_event(f"Detected new file: {event.src_path}")
            self.process_file(event.src_path)

    def is_valid_file(self, path):
        """Checks if a file is in the monitored folder and is a valid file."""
        return os.path.dirname(path) == self.folder and os.path.isfile(path)

    def process_file(self, file_path):
        """Processes a file after ensuring it's ready."""
        while not FileManager.is_file_ready(file_path):
            log_event(f"Waiting for file to be ready: {file_path}")
            time.sleep(1)
        self.pipeline.process_file(file_path)

    def start(self):
        """Starts the file monitoring process."""
        self.observer.schedule(self.event_handler, self.folder, recursive=False)
        self.observer.start()
        log_event("Started file monitoring")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            log_event("Stopped file monitoring")
        self.observer.join()

# Main execution
if __name__ == "__main__":
    INPUT_FOLDER = "E:\\ModuleNotesGenerator\\Drop Here to Generate Module Notes"
    PROCESSED_FOLDER = os.path.join(INPUT_FOLDER, "..", "Processed Files - DELETE IF YOU'RE DONE")
    API_KEY = os.getenv("OPENAI_API_KEY")

    # Start watchdog heartbeat in a separate thread
    import threading
    heartbeat_thread = threading.Thread(target=watchdog_heartbeat, daemon=True)
    heartbeat_thread.start()

    # Initialize and start the pipeline
    pipeline = ProcessingPipeline(
        input_folder=INPUT_FOLDER,
        processed_folder=PROCESSED_FOLDER,
        api_key=API_KEY
    )

    monitor = FileMonitor(INPUT_FOLDER, pipeline)
    monitor.start()