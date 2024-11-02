# utils/audio_manager.py

import speech_recognition as sr
import pyaudio
import numpy as np
from typing import Optional, List, Dict
import threading
import queue

class AudioManager:
    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self._setup_recognizer()
        
    def _setup_recognizer(self):
        """Configure speech recognizer with settings from config."""
        for key, value in self.config.MIC_SETTINGS.items():
            setattr(self.recognizer, key, value)
    
    def list_microphones(self) -> List[Dict]:
        """List all available microphones with details."""
        p = pyaudio.PyAudio()
        mics = []
        
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Is input device
                mics.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })
        
        p.terminate()
        return mics
    
    def select_preferred_microphone(self) -> Optional[sr.Microphone]:
        """Select microphone based on preferred keywords."""
        mics = self.list_microphones()
        
        # First, try to find a mic matching preferred keywords
        for mic in mics:
            if any(keyword.lower() in mic['name'].lower() 
                  for keyword in self.config.PREFERRED_MIC_KEYWORDS):
                return sr.Microphone(device_index=mic['index'])
        
        # Fallback to default microphone
        return sr.Microphone()
    
    def start_listening(self):
        """Start background listening thread."""
        self.is_listening = True
        threading.Thread(target=self._audio_listener_thread, daemon=True).start()
    
    def stop_listening(self):
        """Stop background listening."""
        self.is_listening = False
    
    def _audio_listener_thread(self):
        """Background thread for continuous audio monitoring."""
        mic = self.select_preferred_microphone()
        
        with mic as source:
            self.recognizer.adjust_for_ambient_noise(
                source, 
                duration=self.config.MIC_SETTINGS['adjust_ambient_duration']
            )
            
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=None,
                        phrase_time_limit=10
                    )
                    self.audio_queue.put(audio)
                except Exception as e:
                    print(f"Error in audio listener: {e}")
                    continue
    
    def get_next_audio(self) -> Optional[sr.AudioData]:
        """Get next audio segment from queue."""
        try:
            return self.audio_queue.get(timeout=1)
        except queue.Empty:
            return None
    
    def is_mic_muted(self, audio_data: sr.AudioData) -> bool:
        """Check if microphone is muted based on audio levels."""
        audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(audio_array)))
        return rms < self.config.VAD_CONFIG['silence_threshold']
    
    def process_audio(self, audio_data: sr.AudioData) -> Optional[str]:
        """Process audio data into text with enhanced debugging."""
        try:
            text = self.recognizer.recognize_google(audio_data).lower()
            print(f"DEBUG - AudioManager processed: '{text}'")  # Add this debug line
            return text
        except sr.UnknownValueError:
            print("_", end="", flush=True)  # Indicate no speech detected
            return None
        except sr.RequestError:
            print("N", end="", flush=True)  # Indicate network error
            return None
        except Exception as e:
            print(f"\nError processing audio: {e}")
            return None