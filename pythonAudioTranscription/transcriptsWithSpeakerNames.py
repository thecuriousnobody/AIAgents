# upload audio file
import whisper
import datetime

import subprocess
from pydub import AudioSegment
import torch
import pyannote.audio
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
embedding_model = PretrainedSpeakerEmbedding( 
    "speechbrain/spkrec-ecapa-voxceleb",
    device=torch.device("cpu"))

from pyannote.audio import Audio
from pyannote.core import Segment

import wave
import contextlib
from tqdm import tqdm
from sklearn.cluster import AgglomerativeClustering
import numpy as np

def convert_to_mono(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export("temp_mono.wav", format="wav")
    return "temp_mono.wav"

path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Kiran_extracted_audio.wav"
mono_path = convert_to_mono(path)
audio = Audio()
num_speakers = 2 #@param {type:"integer"}

language = 'English' #@param ['any', 'English']

model_size = 'large' #@param ['tiny', 'base', 'small', 'medium', 'large']


model_name = model_size
if language == 'English' and model_size != 'large':
  model_name += '.en'


if path[-3:] != 'wav':
  subprocess.call(['ffmpeg', '-i', path, 'audio.wav', '-y'])
  path = 'audio.wav'


model = whisper.load_model(model_size)
result = model.transcribe(path, verbose=False)
segments = result["segments"]

with contextlib.closing(wave.open(path,'r')) as f:
  frames = f.getnframes()
  rate = f.getframerate()
  duration = frames / float(rate)

audio = Audio()

def segment_embedding(segment):
    start = segment["start"]
    end = min(duration, segment["end"])
    clip = Segment(start, end)
    waveform, sample_rate = audio.crop(mono_path, clip)
    return embedding_model(waveform[None])

# Calculate embeddings with progress bar
print("Calculating speaker embeddings...")
embeddings = np.zeros(shape=(len(segments), 192))
for i, segment in enumerate(tqdm(segments, desc="Processing segments", unit="segment")):
    embeddings[i] = segment_embedding(segment)

embeddings = np.nan_to_num(embeddings)

print("Clustering speakers...")
clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
labels = clustering.labels_
for i in range(len(segments)):
  segments[i]["speaker"] = 'SPEAKER ' + str(labels[i] + 1)

def time(secs):
    return datetime.timedelta(seconds=round(secs))

# f = open("transcript.txt", "w")

print("Writing transcript...")
with open("transcript.txt", "w") as f:
    for i, segment in enumerate(tqdm(segments, desc="Writing segments", unit="segment")):
        if i == 0 or segments[i - 1]["speaker"] != segment["speaker"]:
            f.write("\n" + segment["speaker"] + ' ' + str(time(segment["start"])) + '\n')
        f.write(segment["text"][1:] + ' ')

print("Transcription complete. Output saved to transcript.txt")

import os
os.remove(mono_path)

