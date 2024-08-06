import speech_recognition as sr
import pyaudio
import time
import threading
import queue

class VoiceRecognition:
    def __init__(self, microphone_index=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=microphone_index)
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.is_listening = False
        self.silence_threshold = 1000  # Adjust this value to set the silence threshold
        self.silence_duration = 1  # Seconds of silence to trigger transcription

    @staticmethod
    def list_microphones():
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"{index}: {name}")

    def callback(self, recognizer, audio):
        self.audio_queue.put(audio)

    def recognize_worker(self):
        while self.is_listening:
            try:
                audio = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            try:
                text = self.recognizer.recognize_google(audio)
                if text:
                    self.text_queue.put(text)
            except sr.UnknownValueError:
                pass  # Silence, continue listening
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

    def listen_and_transcribe(self, duration=None):
        self.is_listening = True
        recognition_thread = threading.Thread(target=self.recognize_worker)
        recognition_thread.start()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        print("Start speaking. The system will transcribe after 3 seconds of silence.")
        stop_listening = self.recognizer.listen_in_background(self.microphone, self.callback)
        
        start_time = time.time()
        last_speech_time = start_time
        full_text = []

        while (duration is None) or (time.time() - start_time < duration):
            if not self.text_queue.empty():
                text = self.text_queue.get()
                full_text.append(text)
                last_speech_time = time.time()
                print(f"Recognized: {text}")  # Print each recognized segment
                
            if time.time() - last_speech_time > self.silence_duration:
                if full_text:
                    transcription = " ".join(full_text)
                    yield transcription
                    full_text = []
                last_speech_time = time.time()  # Reset the silence timer

            time.sleep(0.1)

        stop_listening(wait_for_stop=False)
        self.is_listening = False
        recognition_thread.join()

    def get_voice_input(self, duration=None):
        return self.listen_and_transcribe(duration)