from pyannote.audio import Pipeline

# You'll need to get an access token from Hugging Face
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                    use_auth_token="YOUR_HUGGING_FACE_TOKEN")

# Apply the pipeline to an audio file
diarization = pipeline("path/to/your/audio/file.wav")

# Print the results
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")