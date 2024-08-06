import whisper
import subprocess
import os

def extract_audio(video_path, audio_path):
    """Extract audio from video file"""
    command = f"ffmpeg -i \"{video_path}\" -ab 160k -ac 2 -ar 44100 -vn \"{audio_path}\""
    try:
        subprocess.call(command, shell=True)
        print(f"Audio extracted successfully: {audio_path}")
    except Exception as e:
        print(f"Error extracting audio: {e}")

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper"""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

# Example usage
video_path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Conversation with Amber Case on The Idea Sandbox (2024-08-02 14_04 GMT-5).mp4"  # Replace with your video file path
audio_path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/Amber_extracted_audio.wav"

# Extract audio from video
extract_audio(video_path, audio_path)
output_dir = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage"
output_file = "transcription_Amber.txt"
full_output_path = os.path.join(output_dir, output_file)

# Transcribe the extracted audio
if os.path.exists(audio_path):
    transcription = transcribe_audio(audio_path)
    if transcription:
        print("Transcription:")
        print(transcription)

        # Save transcription to a file
        with open(full_output_path, "w") as f:
            f.write(transcription)
        print("Transcription saved to transcription.txt")
    else:
        print("Transcription failed.")
else:
    print(f"Audio file not found: {audio_path}")

# Optionally, remove the extracted audio file
# os.remove(audio_path)