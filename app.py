import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import *
from tkinter import ttk
import cv2
import uuid
from vosk import Model, KaldiRecognizer
import wave
import json
import srt
import numpy as np
import scipy.io.wavfile as wav
import moviepy.editor as mp
from datetime import timedelta
from funcion import funcion

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Text Transcription")
         
        bg_color = "gray" 
        self.root.configure(bg=bg_color)

        # Custom Toolbar
        self.toolbar_frame = tk.Frame(root)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew")

        # Add buttons to the toolbar
        tk.Button(self.toolbar_frame, text="Add Video Path", command=self.add_video_entry).grid(row=0, column=2, padx=5)
        tk.Button(self.toolbar_frame, text="Add Audio Path", command=self.add_audio_entry).grid(row=0, column=3, padx=5)
       
        # Frames
        video_frame = tk.Frame(root)
        video_frame.grid(row=1, column=0, padx=10, pady=20, sticky="ew")

        audio_frame = tk.Frame(root)
        audio_frame.grid(row=2, column=0, padx=10, pady=20, sticky="ew")

        transcript_frame = tk.Frame(root)
        transcript_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        subtitles_frame = tk.Frame(root)
        subtitles_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        # Variables
        self.video_paths = []
        self.audio_paths = []
        self.current_video_entry = tk.StringVar()
        self.current_audio_entry = tk.StringVar()

        # Labels
        tk.Label(video_frame, text="Video Files:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(audio_frame, text="Audio Files:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(transcript_frame, text="Transcript:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(subtitles_frame, text="Subtitles:").grid(row=0, column=0, padx=10, pady=10)

        # Entry Widgets
        self.video_entry = tk.Entry(video_frame, textvariable=self.current_video_entry, width=60)
        self.video_entry.grid(row=0, column=1, padx=10, pady=10)
        self.audio_entry = tk.Entry(audio_frame, textvariable=self.current_audio_entry, width=60)
        self.audio_entry.grid(row=0, column=1, padx=10, pady=10)
        #download
        self.download_transcript_button = tk.Button(transcript_frame, text="Download Transcript", command=self.download_transcript, state=tk.DISABLED)
        self.download_transcript_button.grid(row=0, column=0, sticky="nw")

        self.subtitles_text = tk.Text(subtitles_frame, height=20, width=100, wrap="word")
        self.subtitles_text.grid(row=1, column=0, padx=10, pady=10, rowspan=4)

        # Text Widgets
        self.transcript_text = tk.Text(transcript_frame, height=17, width=100, wrap="word")
        self.transcript_text.grid(row=1, column=0, padx=10, pady=10, rowspan=2)

        self.subtitles_text = tk.Text(subtitles_frame, height=20, width=100, wrap="word")
        self.subtitles_text.grid(row=1, column=0, padx=10, pady=10, rowspan=4)

        # Adjust weights for column configurations
        transcript_frame.columnconfigure(0, weight=1)
        subtitles_frame.columnconfigure(0, weight=1)

        # Transcripts Button
        tk.Button(root, text="Transcripts", command=self.extract_transcript).grid(row=5, column=0, pady=10)
        tk.Button(transcript_frame, text="Download Transcript", command=self.download_transcript).grid(row=0, column=0, sticky="nw")
        
        tk.Button(subtitles_frame, text="Download Subtitles", command=self.download_subtitles).grid(row=0, column=0, sticky="nw")

        # Make the toolbar span all columns
        self.toolbar_frame.grid(columnspan=2)
       
      

    def browse_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if video_path:
            self.current_video_entry.set(video_path)

    def browse_audio(self):
        audio_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
        if audio_path:
            self.current_audio_entry.set(audio_path)

    def add_video_entry(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
        if video_path:
            self.video_paths.append(video_path)
            self.video_entry.insert(tk.END, video_path + "\n")

    def add_audio_entry(self):
        audio_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
        if audio_path:
            self.audio_paths.append(audio_path)
            self.audio_entry.insert(tk.END, audio_path + "\n")
    
    def download_transcript(self):
        transcript_content = self.transcript_text.get("1.0", tk.END)
        transcript_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

        if transcript_file_path:
            try:
                with open(transcript_file_path, "w") as transcript_file:
                    transcript_file.write(transcript_content)
                self.show_notification("Bản trích xuất đã được tải về thành công.")
            except Exception as e:
                print(f"Lỗi: {e}")
                self.show_notification("Không thể tải về bản trích xuất.")

    def download_subtitles(self):
        subtitles_content = self.subtitles_text.get("1.0", tk.END)
        subtitles_file_path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("Subtitles files", "*.srt")])

        if subtitles_file_path:
            try:
                with open(subtitles_file_path, "w", encoding="utf-8") as subtitles_file:
                    subtitles_file.write(subtitles_content)
                self.show_notification("Phụ đề đã được tải về thành công.")
            except Exception as e:
                print(f"Lỗi: {e}")
                self.show_notification("Không thể tải về phụ đề.")
    
    def show_notification(self, message):
            messagebox.showinfo("Notification", message)

    def extract_transcript(self):
        video_paths = self.video_paths + [self.current_video_entry.get()]
        audio_paths = self.audio_paths + [self.current_audio_entry.get()]

        model = Model(model_path="vosk-model-en-us-0.42-gigaspeech")
        
        
        if all(not path for path in video_paths) and all(not path for path in audio_paths):
            self.show_notification("Hãy đưa ít nhất tệp vào trong phần đường d.")
            return

        for video, audio in zip(video_paths, audio_paths):
            video_id = str(uuid.uuid4())
            os.makedirs(f"{video_id}")

            if not audio:
                audio_path = f"{video_id}/audio.wav"
            else:
                audio_path = audio

            function = funcion(
                video,
                audio_path,
                f"{video_id}/mono_audio.wav",
                f"{video_id}/transcript.txt",
                f"{video_id}/words.json",
                f"{video_id}/captions.srt",
                model,
            )

            function.extract_transcript()

            with open(function.transcript, "r") as trans_file:
                transcript_content = trans_file.read()
                self.transcript_text.delete("1.0", tk.END)
                self.transcript_text.insert(tk.END, transcript_content)

            with open(function.subtitles, "r", encoding="utf8") as sub_file:
                subtitles_content = sub_file.read()
                self.subtitles_text.delete("1.0", tk.END)
                self.subtitles_text.insert(tk.END, subtitles_content)
            
            self.show_notification(f"Transcription  is completed.")

        self.video_entry.delete(0, tk.END)
        self.audio_entry.delete(0, tk.END)
        self.current_video_entry.set("")
        self.current_audio_entry.set("")
           
if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.geometry("840x1800")
    root.mainloop()