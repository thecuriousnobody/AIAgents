import sounddevice as sd
import numpy as np
import threading
import queue
import torch
import whisper
import tkinter as tk
from tkinter import ttk, messagebox
from googletrans import Translator, LANGUAGES
import time
import warnings
import webrtcvad
import wave
import contextlib
from collections import deque
import sys
import requests
warnings.filterwarnings("ignore")

class RealTimeMeetingTranslator:
    def __init__(self):
        try:
            print("Initializing translator...")
            print("Loading Whisper model...")
            self.model = whisper.load_model("base")
            print("Whisper model loaded successfully")
            
            print("Setting up translator...")
            # Try multiple translation services
            self.translation_services = [
                'translate.google.com',
                'translate.google.co.in',
                'translate.google.co.uk'
            ]
            self.current_service_index = 0
            self.translator = self.create_translator()
            
            self.samplerate = 16000
            self.mic_buffer = queue.Queue()
            self.speakers_buffer = queue.Queue()
            self.recording = False
            self.vad = webrtcvad.Vad(3)
            self.audio_window = deque(maxlen=30)
            self.log_queue = queue.Queue()
            
            print("Detecting audio devices...")
            # List available input devices
            print("\nAvailable input devices:")
            devices = sd.query_devices()
            self.system_device_id = None
            
            for i, device in enumerate(devices):
                print(f"{i}: {device['name']} (Max inputs: {device['max_input_channels']}, Max outputs: {device['max_output_channels']})")
                # Find system audio output device
                if (device['max_input_channels'] > 0 and 
                    ('studio' in device['name'].lower() or 
                     'speakers' in device['name'].lower() or 
                     'system' in device['name'].lower())):
                    self.system_device_id = i
                    print(f"Selected system audio device: {device['name']} (ID: {i})")
                    print(f"Device details: {device}")
            
            if self.system_device_id is None:
                # Try to find any output device that can be used as input
                for i, device in enumerate(devices):
                    if device['max_input_channels'] > 0 and device['max_output_channels'] > 0:
                        self.system_device_id = i
                        print(f"Selected alternative system audio device: {device['name']} (ID: {i})")
                        print(f"Device details: {device}")
                        break
                
            if self.system_device_id is None:
                print("Warning: No system audio device found")
                
            print("Initialization complete")
            self.setup_gui()
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise
    
    def create_translator(self):
        """Create a new translator instance with the current service"""
        service_url = self.translation_services[self.current_service_index]
        return Translator(service_urls=[service_url])
    
    def rotate_translation_service(self):
        """Switch to the next translation service"""
        self.current_service_index = (self.current_service_index + 1) % len(self.translation_services)
        self.translator = self.create_translator()
        service_url = self.translation_services[self.current_service_index]
        self.log_debug(f"Switched to translation service: {service_url}")
    
    def setup_gui(self):
        try:
            print("Setting up GUI...")
            self.root = tk.Tk()
            self.root.title("Real-Time Tamil-English Meeting Translator")
            self.root.geometry("1000x800")
            
            # Add debug info display
            self.debug_text = tk.Text(self.root, height=4, wrap=tk.WORD)
            self.debug_text.pack(fill="x", padx=10, pady=5)
            self.debug_text.insert(tk.END, "Debug Information:\n")
            
            # Status label
            self.status_label = ttk.Label(self.root, text="Status: Ready")
            self.status_label.pack(pady=5)
            
            # Translation display
            self.text_frame = ttk.Frame(self.root)
            self.text_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Your Speech (English)
            self.english_label = ttk.Label(self.text_frame, text="Your Speech (English):")
            self.english_label.pack()
            
            self.english_text = tk.Text(self.text_frame, height=5, wrap=tk.WORD)
            self.english_text.pack(fill="both", expand=True, pady=5)
            
            # Tamil Translation of Your Speech
            self.tamil_translation_label = ttk.Label(self.text_frame, text="Tamil Translation:")
            self.tamil_translation_label.pack()
            
            self.tamil_translation_text = tk.Text(self.text_frame, height=5, wrap=tk.WORD)
            self.tamil_translation_text.pack(fill="both", expand=True, pady=5)
            
            # Other Person's Speech (Tamil)
            self.tamil_label = ttk.Label(self.text_frame, text="Other Person's Speech (Tamil):")
            self.tamil_label.pack()
            
            self.tamil_text = tk.Text(self.text_frame, height=5, wrap=tk.WORD)
            self.tamil_text.pack(fill="both", expand=True, pady=5)
            
            # English Translation of Tamil Speech
            self.english_translation_label = ttk.Label(self.text_frame, text="English Translation:")
            self.english_translation_label.pack()
            
            self.english_translation_text = tk.Text(self.text_frame, height=5, wrap=tk.WORD)
            self.english_translation_text.pack(fill="both", expand=True, pady=5)
            
            # Control buttons
            self.button_frame = ttk.Frame(self.root)
            self.button_frame.pack(pady=10)
            
            self.record_button = ttk.Button(
                self.button_frame, 
                text="Start Translation", 
                command=self.toggle_recording
            )
            self.record_button.pack(side="left", padx=5)
            
            self.clear_button = ttk.Button(
                self.button_frame, 
                text="Clear", 
                command=self.clear_text
            )
            self.clear_button.pack(side="left", padx=5)
            
            # Start the GUI update loop
            self.root.after(100, self.process_log_queue)
            
            print("GUI setup complete")
            
        except Exception as e:
            print(f"Error setting up GUI: {e}")
            raise
    
    def process_log_queue(self):
        """Process any pending log messages in the queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                timestamp = time.strftime("%H:%M:%S")
                self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
                self.debug_text.see(tk.END)
                print(f"[{timestamp}] {message}")
        except queue.Empty:
            pass
        finally:
            # Schedule the next queue check
            if not self.root.quit_flag if hasattr(self.root, 'quit_flag') else True:
                self.root.after(100, self.process_log_queue)
    
    def log_debug(self, message):
        """Add debug message to queue for processing"""
        self.log_queue.put(message)
    
    def clear_text(self):
        self.english_text.delete(1.0, tk.END)
        self.tamil_translation_text.delete(1.0, tk.END)
        self.tamil_text.delete(1.0, tk.END)
        self.english_translation_text.delete(1.0, tk.END)
        self.debug_text.delete(1.0, tk.END)
    
    def is_speech(self, audio_chunk):
        try:
            return self.vad.is_speech(audio_chunk, self.samplerate)
        except Exception as e:
            self.log_debug(f"VAD Error: {e}")
            return True
    
    def translate_text(self, text, src_lang, dest_lang):
        """Helper function to handle translation with retries and error handling"""
        max_retries = len(self.translation_services)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                self.log_debug(f"Attempting to translate from {src_lang} to {dest_lang}: {text}")
                self.log_debug(f"Using translation service: {self.translation_services[self.current_service_index]}")
                
                translation = self.translator.translate(text, src=src_lang, dest=dest_lang)
                if translation and translation.text:
                    self.log_debug(f"Translation successful: {translation.text}")
                    return translation.text
                else:
                    raise Exception("Empty translation result")
                    
            except Exception as e:
                last_error = str(e)
                self.log_debug(f"Translation attempt {attempt + 1} failed: {e}")
                self.rotate_translation_service()
                time.sleep(0.5)  # Brief pause before retry
        
        self.log_debug(f"All translation attempts failed. Last error: {last_error}")
        return f"[Translation failed] {text}"
    
    def process_mic_audio(self):
        self.log_debug("Started processing microphone audio")
        while self.recording:
            try:
                audio_data = []
                start_time = time.time()
                while time.time() - start_time < 0.5:
                    if not self.recording:
                        break
                    try:
                        data = self.mic_buffer.get(timeout=0.1)
                        audio_data.append(data)
                    except queue.Empty:
                        continue
                
                if audio_data:
                    self.log_debug("Processing microphone audio chunk")
                    audio_array = np.concatenate(audio_data)
                    result = self.model.transcribe(audio_array, language='en')
                    text = result["text"].strip()
                    
                    if text:
                        self.log_debug(f"Detected English speech: {text}")
                        translation = self.translate_text(text, 'en', 'ta')
                        # Queue the display update
                        self.root.after(0, self.update_english_display, text, translation)
            
            except Exception as e:
                self.log_debug(f"Mic Processing Error: {e}")
    
    def process_speaker_audio(self):
        self.log_debug("Started processing speaker audio")
        while self.recording:
            try:
                audio_data = []
                start_time = time.time()
                while time.time() - start_time < 0.5:
                    if not self.recording:
                        break
                    try:
                        data = self.speakers_buffer.get(timeout=0.1)
                        audio_data.append(data)
                    except queue.Empty:
                        continue
                
                if audio_data:
                    self.log_debug("Processing speaker audio chunk")
                    audio_array = np.concatenate(audio_data)
                    result = self.model.transcribe(audio_array, language='ta')
                    text = result["text"].strip()
                    
                    if text:
                        self.log_debug(f"Detected Tamil speech: {text}")
                        translation = self.translate_text(text, 'ta', 'en')
                        # Queue the display update
                        self.root.after(0, self.update_tamil_display, text, translation)
            
            except Exception as e:
                self.log_debug(f"Speaker Processing Error: {e}")
    
    def update_english_display(self, original, translation):
        timestamp = time.strftime("%H:%M:%S")
        self.english_text.insert(tk.END, f"[{timestamp}] {original}\n")
        self.tamil_translation_text.insert(tk.END, f"[{timestamp}] {translation}\n")
        self.english_text.see(tk.END)
        self.tamil_translation_text.see(tk.END)
    
    def update_tamil_display(self, original, translation):
        timestamp = time.strftime("%H:%M:%S")
        self.tamil_text.insert(tk.END, f"[{timestamp}] {original}\n")
        self.english_translation_text.insert(tk.END, f"[{timestamp}] {translation}\n")
        self.tamil_text.see(tk.END)
        self.english_translation_text.see(tk.END)
    
    def mic_callback(self, indata, frames, time, status):
        if status:
            self.log_debug(f"Mic Input Error: {status}")
        self.mic_buffer.put(indata.copy())
    
    def system_audio_callback(self, indata, frames, time, status):
        if status:
            self.log_debug(f"System Audio Input Error: {status}")
        self.speakers_buffer.put(indata.copy())
    
    def start_recording(self):
        try:
            self.recording = True
            self.log_debug("Starting audio capture...")
            
            # Start microphone input
            self.mic_stream = sd.InputStream(
                callback=self.mic_callback,
                channels=1,
                samplerate=self.samplerate
            )
            self.mic_stream.start()
            self.log_debug("Microphone stream started")
            
            # Start system audio input if available
            if self.system_device_id is not None:
                try:
                    self.log_debug(f"Attempting to start system audio stream with device ID {self.system_device_id}")
                    self.system_stream = sd.InputStream(
                        device=self.system_device_id,
                        callback=self.system_audio_callback,
                        channels=1,
                        samplerate=self.samplerate,
                        blocksize=1024
                    )
                    self.system_stream.start()
                    self.log_debug("System audio stream started successfully")
                except Exception as e:
                    self.log_debug(f"Failed to start system audio stream: {e}")
                    self.system_device_id = None
            
            # Start processing threads
            self.mic_process_thread = threading.Thread(target=self.process_mic_audio)
            self.speaker_process_thread = threading.Thread(target=self.process_speaker_audio)
            
            self.mic_process_thread.start()
            self.speaker_process_thread.start()
            
            self.log_debug("All processing threads started")
            self.status_label.config(text="Status: Translation Active")
            
        except Exception as e:
            self.log_debug(f"Error starting recording: {e}")
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
    
    def stop_recording(self):
        try:
            self.recording = False
            self.log_debug("Stopping recording...")
            
            if hasattr(self, 'mic_stream'):
                self.mic_stream.stop()
                self.mic_stream.close()
            
            if hasattr(self, 'system_stream'):
                self.system_stream.stop()
                self.system_stream.close()
            
            if hasattr(self, 'mic_process_thread'):
                self.mic_process_thread.join()
            if hasattr(self, 'speaker_process_thread'):
                self.speaker_process_thread.join()
            
            self.log_debug("Recording stopped")
            self.status_label.config(text="Status: Ready")
            
        except Exception as e:
            self.log_debug(f"Error stopping recording: {e}")
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
            self.record_button.config(text="Stop Translation")
        else:
            self.stop_recording()
            self.record_button.config(text="Start Translation")
    
    def run(self):
        try:
            self.log_debug("Starting application...")
            self.root.mainloop()
        except Exception as e:
            print(f"Error running application: {e}")
            raise

if __name__ == "__main__":
    try:
        print("Starting Tamil-English Meeting Translator...")
        translator = RealTimeMeetingTranslator()
        translator.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
