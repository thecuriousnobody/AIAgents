import requests
import json
from pydub import AudioSegment
import os
import requests
import json
from tqdm import tqdm
# Replace with your actual Hugging Face API key
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import torch
import whisper
import time
API_KEY = config.HUGGING_FACE_API_KEY
import whisperx
import gc
import io
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Load your API key
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"


def transcribe_chunk(audio_chunk, chunk_start_time, max_retries=10):
    for attempt in range(max_retries):
        try:
            # Convert AudioSegment to WAV format in memory
            buffer = io.BytesIO()
            audio_chunk.export(buffer, format="wav")
            audio_data = buffer.getvalue()
            
            files = {
                'audio': ('audio.wav', audio_data, 'audio/wav')
            }
            data = {
                'model': 'openai/whisper-large-v3',
                'task': 'transcribe',
                'return_timestamps': 'true'
            }
            
            print(f"Sending request to {API_URL}")
            print(f"Headers: {headers}")
            print(f"Data: {data}")
            print(f"Files: {files.keys()}")
            
            response = requests.post(API_URL, headers=headers, files=files, data=data)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            # Adjust timestamps
            if 'chunks' in result:
                for chunk in result['chunks']:
                    chunk['timestamp'] = (
                        chunk['timestamp'][0] + chunk_start_time,
                        chunk['timestamp'][1] + chunk_start_time
                    )
            return result
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response content: {response.text}")
            wait_time = min(2 ** attempt * 30, 600)  # Exponential backoff, max 10 minutes
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
    raise Exception(f"Failed to transcribe chunk after {max_retries} attempts")


def process_audio_file(file_path, chunk_duration_ms=30000, resume_from=0, max_chunks=None):
    audio = AudioSegment.from_wav(file_path)
    duration_ms = len(audio)
    chunks = [audio[i:i+chunk_duration_ms] for i in range(0, duration_ms, chunk_duration_ms)]
    
    if max_chunks is not None:
        chunks = chunks[:max_chunks]
    
    full_transcription = []
    for i, chunk in enumerate(chunks[resume_from:], start=resume_from):
        print(f"Processing chunk {i+1} of {len(chunks)}...")
        chunk_start_time = i * (chunk_duration_ms / 1000)  # Convert to seconds
        try:
            result = transcribe_chunk(chunk, chunk_start_time)
            full_transcription.append(result)
            
            # Save progress after each chunk
            save_progress(file_path, full_transcription, i+1)
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            print(f"Saving progress and stopping...")
            break
    
    return full_transcription

def save_progress(file_path, transcription, last_chunk):
    progress_file = f"{os.path.splitext(file_path)[0]}_progress.json"
    with open(progress_file, 'w') as f:
        json.dump({"last_chunk": last_chunk, "transcription": transcription}, f)
    print(f"Progress saved to {progress_file}")

def load_progress(file_path):
    progress_file = f"{os.path.splitext(file_path)[0]}_progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        return progress["last_chunk"], progress["transcription"]
    return 0, []

def transcribe_audio(audio_file_path, max_chunks=None):
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found at {audio_file_path}")
    
    file_size = os.path.getsize(audio_file_path)
    print(f"Processing audio file: {audio_file_path}")
    print(f"File size: {file_size} bytes")
    
    resume_from, partial_transcription = load_progress(audio_file_path)
    if resume_from > 0:
        print(f"Resuming from chunk {resume_from}")
    
    transcription_results = process_audio_file(audio_file_path, resume_from=resume_from, max_chunks=max_chunks)
    transcription_results = partial_transcription + transcription_results
    
    output_file = f"{os.path.splitext(audio_file_path)[0]}_transcription.txt"
    with open(output_file, 'w') as f:
        for i, result in enumerate(transcription_results):
            f.write(f"Chunk {i+1}:\n")
            if 'text' in result:
                f.write(f"Full text: {result['text']}\n\n")
            if 'chunks' in result:
                f.write("Detailed segments with timestamps:\n")
                for chunk in result['chunks']:
                    start_time, end_time = chunk['timestamp']
                    f.write(f"[{start_time:.2f} - {end_time:.2f}] {chunk['text']}\n")
            f.write("\n" + "="*50 + "\n\n")
    
    print(f"\nTranscription with timestamps saved to {output_file}")
    return output_file

if __name__ == "__main__":
    audio_file_path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Kiran_extracted_audio.wav"
    try:
        # For testing with 5 chunks:
        output_file = transcribe_audio(audio_file_path, max_chunks=2)
        # For full processing, comment out the above line and uncomment the below line:
        # output_file = transcribe_audio(audio_file_path)
        print(f"Transcription completed successfully. Output saved to: {output_file}")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")