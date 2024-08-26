import whisperx
import gc
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
os.environ["HUGGING_FACE_API_KEY"] = config.HUGGING_FACE_API_KEY
from transformers import pipeline

import whisperx
import gc

# device = "cuda"
batch_size = 4 # reduce if low on GPU mem
# compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

device = "cpu"
compute_type = "int8"  # Use int8 for CPU

audio_file = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Kiran_extracted_audio.wav"

audio = whisperx.load_audio(audio_file)

model = whisperx.load_model("large-v3", device=device, compute_type=compute_type)

result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"]) # before alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
diarize_model = whisperx.DiarizationPipeline(use_auth_token=config.HUGGING_FACE_API_KEY,
                                             device=device)
diarize_segments = diarize_model(audio, min_speakers=2, max_speakers=2)

result = whisperx.assign_word_speakers(diarize_segments, result)
print(diarize_segments)
print(result["segments"]) # segments are now assigned speaker IDs