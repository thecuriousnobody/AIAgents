import whisper
from pyannote.audio import Pipeline
import torch
import os
import sys
import time
import gc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def transcribe_and_diarize(audio_path, auth_token):
    print("Starting transcription and diarization process...")
    
    # Load Whisper model
    print("Loading Whisper model...")
    whisper_model = whisper.load_model("base")
    
    # Transcribe audio
    print("Transcribing audio...")
    start_time = time.time()
    result = whisper_model.transcribe(audio_path)
    segments = result["segments"]
    print(f"Transcription completed in {time.time() - start_time:.2f} seconds")
    
    # Clear memory
    del whisper_model
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    # Initialize pyannote pipeline
    print("Initializing pyannote pipeline...")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=auth_token)
    
    # Force CPU usage for pyannote
    pipeline.to(torch.device('cpu'))

    # Perform diarization
    print("Performing speaker diarization...")
    start_time = time.time()
    diarization = pipeline(audio_path)
    print(f"Diarization completed in {time.time() - start_time:.2f} seconds")

    # Clear memory
    del pipeline
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    # Combine transcription with diarization
    print("Aligning transcription with speaker segments...")
    speaker_segments = list(diarization.itertracks(yield_label=True))

    # Align transcription with speaker segments
    final_output = []
    for i, trans_segment in enumerate(segments):
        trans_start = trans_segment['start']
        trans_end = trans_segment['end']
        trans_text = trans_segment['text']

        # Find overlapping speaker segment
        for segment, _, speaker in speaker_segments:
            if (segment.start <= trans_start < segment.end or
                segment.start < trans_end <= segment.end):
                final_output.append({
                    "start": trans_start,
                    "end": trans_end,
                    "speaker": speaker,
                    "text": trans_text
                })
                break
        
        if i % 100 == 0:
            print(f"Processed {i}/{len(segments)} segments")

    print("Alignment completed")
    return final_output

# Usage
audio_path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Kiran_extracted_audio.wav"
auth_token = config.HUGGING_FACE_API_KEY  # Replace with your actual token

print(f"Processing audio file: {audio_path}")
result = transcribe_and_diarize(audio_path, auth_token)

# Save and display results
print("Saving results...")
with open("transcription_with_speakers.txt", "w") as f:
    for segment in result:
        line = f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['speaker']}: {segment['text']}\n"
        f.write(line)
        print(line, end='')

print("Transcription with speaker diarization saved to transcription_with_speakers.txt")
print("Process completed successfully")