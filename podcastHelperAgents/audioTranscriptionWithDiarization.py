import torch
import torchaudio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import whisper
import sys
import os
from tqdm import tqdm
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Audio file path
sample = input("Please enter the path to your audio file: ")

def transcribe_audio(filename):
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    
    print("Starting transcription...")
    # Transcribe the entire audio file
    result = model.transcribe(filename, verbose=False)
    
    print(f"Detected language: {result['language']}")
    
    # Extract segments and add progress bar
    segments = []
    for segment in tqdm(result['segments'], desc="Processing segments"):
        segments.append({
            "start": segment['start'],
            "end": segment['end'],
            "text": segment['text']
        })
    
    print("Transcription completed.")
    return {"segments": segments}

# Get audio info
audio_info = torchaudio.info(sample)
duration_seconds = audio_info.num_frames / audio_info.sample_rate
print(f"Processing audio file: {sample}")
print(f"Duration: {duration_seconds:.2f} seconds")
print(f"Sample rate: {audio_info.sample_rate} Hz")

# Transcription
transcription_result = transcribe_audio(sample)

# Diarization
print("\nStarting diarization...")
device = torch.device("cpu")
print(f"Using device: {device}")

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                    use_auth_token=config.HUGGING_FACE_API_KEY)
pipeline = pipeline.to(device)

# Load the entire audio file
waveform, sample_rate = torchaudio.load(sample)

print(f"Processing {waveform.shape[1]/sample_rate:.2f} seconds of audio at {sample_rate} Hz sample rate")

with ProgressHook() as hook:
    diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate}, hook=hook)

print("Diarization completed.")

# Combine transcription and diarization
combined_results = []
for segment in transcription_result["segments"]:
    start = segment["start"]
    end = segment["end"]
    text = segment["text"]
    
    speaker = None
    for turn, _, spk in diarization.itertracks(yield_label=True):
        if turn.start <= (start + end) / 2 <= turn.end:
            speaker = spk
            break
    
    combined_results.append({
        "start": start,
        "end": end,
        "text": text,
        "speaker": speaker if speaker else "Unknown"
    })

# Write combined output to file
output_dir = os.path.dirname(sample)
base_name = os.path.splitext(os.path.basename(sample))[0]
output_file = os.path.join(output_dir, f"transcription_diarization_output_{base_name}.txt")

# with open(output_file, "w") as f:
#     f.write(f"Original audio file: {sample}\n")
#     f.write(f"Processed duration: {duration_seconds:.2f} seconds\n")
#     f.write(f"Sample rate: {sample_rate} Hz\n\n")
#     for chunk in combined_results:
#         f.write(f"[{chunk['start']:.2f}s - {chunk['end']:.2f}s] Speaker {chunk['speaker']}: {chunk['text']}\n")

def format_time(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"

with open(output_file, "w") as f:
    f.write(f"Original audio file: {sample}\n")
    f.write(f"Processed duration: {format_time(duration_seconds)}\n")
    f.write(f"Sample rate: {sample_rate} Hz\n\n")
    for chunk in combined_results:
        start_time = format_time(chunk['start'])
        end_time = format_time(chunk['end'])
        f.write(f"[{start_time} - {end_time}] {chunk['speaker']}: {chunk['text']}\n")

print(f"\nTranscription with diarization completed. Output saved to: {output_file}")



# Input and output file paths
consolidated_output_file = os.path.join(output_dir, f"consolidated_transcription_diarization_output_{base_name}.txt")

import re

def parse_line(line):
    match = re.match(r'\[(\d{2}:\d{2}\.\d{2}) - (\d{2}:\d{2}\.\d{2})\] (SPEAKER_\d+): (.+)', line)
    if match:
        start_time, end_time, speaker, text = match.groups()
        return {
            'start': start_time,
            'end': end_time,
            'speaker': speaker,
            'text': text.strip()
        }
    return None

def consolidate_speaker_segments(segments):
    consolidated = []
    current_segment = None

    for segment in segments:
        if current_segment is None:
            current_segment = segment
        elif segment['speaker'] == current_segment['speaker']:
            current_segment['end'] = segment['end']
            current_segment['text'] += ' ' + segment['text']
        else:
            consolidated.append(current_segment)
            current_segment = segment

    if current_segment:
        consolidated.append(current_segment)

    return consolidated

# Read and parse the input file
segments = []
header_lines = []
with open(output_file, 'r') as f:
    for line in f:
        if line.startswith('['):
            segment = parse_line(line.strip())
            if segment:
                segments.append(segment)
        else:
            header_lines.append(line)

print(f"Number of segments read: {len(segments)}")
print(f"Number of header lines: {len(header_lines)}")

# Consolidate the segments
consolidated_segments = consolidate_speaker_segments(segments)

print(f"Number of consolidated segments: {len(consolidated_segments)}")

# Write the consolidated output
with open(consolidated_output_file, 'w') as f:
    # Write the header information
    f.writelines(header_lines)
    f.write('\n')

    # Write the consolidated segments
    for segment in consolidated_segments:
        f.write(f"[{segment['start']} - {segment['end']}] {segment['speaker']}: {segment['text']}\n\n")

print(f"Consolidated output written to: {consolidated_output_file}")
