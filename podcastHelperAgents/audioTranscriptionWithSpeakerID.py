import whisper
from pyannote.audio import Pipeline
import torch

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def transcribe_and_diarize(audio_path, auth_token):
    # Load Whisper model
    whisper_model = whisper.load_model("base")
    
    # Transcribe audio
    print("Transcribing audio...")
    result = whisper_model.transcribe(audio_path)
    segments = result["segments"]

    # Initialize pyannote pipeline
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=auth_token)

    # Perform diarization
    print("Performing speaker diarization...")
    diarization = pipeline(audio_path)

    # Combine transcription with diarization
    speaker_segments = []
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        speaker_segments.append({
            "start": segment.start,
            "end": segment.end,
            "speaker": speaker
        })

    # Align transcription with speaker segments
    final_output = []
    for trans_segment in segments:
        trans_start = trans_segment['start']
        trans_end = trans_segment['end']
        trans_text = trans_segment['text']

        # Find overlapping speaker segment
        for speaker_seg in speaker_segments:
            if (speaker_seg['start'] <= trans_start < speaker_seg['end'] or
                speaker_seg['start'] < trans_end <= speaker_seg['end']):
                final_output.append({
                    "start": trans_start,
                    "end": trans_end,
                    "speaker": speaker_seg['speaker'],
                    "text": trans_text
                })
                break

    return final_output

# Usage
audio_path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Kiran_extracted_audio.wav"
auth_token = config.HUGGING_FACE_API_KEY  # Replace with your actual token

result = transcribe_and_diarize(audio_path, auth_token)

# Save and display results
with open("transcription_with_speakers.txt", "w") as f:
    for segment in result:
        line = f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['speaker']}: {segment['text']}\n"
        f.write(line)
        print(line, end='')

print("Transcription with speaker diarization saved to transcription_with_speakers.txt")