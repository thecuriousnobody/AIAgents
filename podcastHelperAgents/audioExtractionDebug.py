import subprocess
import os
import sys

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        print("FFmpeg is not installed or not in PATH. Please install FFmpeg to continue.")
        return False

def extract_audio(video_path, audio_path):
    """Extract audio from video file"""
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False
    
    command = f"ffmpeg -i \"{video_path}\" -ab 160k -ac 2 -ar 44100 -vn \"{audio_path}\""
    try:
        subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE)
        print(f"Audio extracted successfully: {audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        print(f"FFmpeg error output: {e.stderr.decode()}")
        return False

def main():
    if not check_ffmpeg():
        sys.exit(1)

    # Get input video path from user
    video_path = input("Enter the path to your video file: ").strip()
    
    # Generate output audio path
    audio_dir = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage"
    audio_filename = os.path.splitext(os.path.basename(video_path))[0] + "_extracted_audio.wav"
    audio_path = os.path.join(audio_dir, audio_filename)

    if extract_audio(video_path, audio_path):
        if os.path.exists(audio_path):
            print(f"Audio file created successfully at: {audio_path}")
            # Here you would add the code to transcribe the audio
            # For now, we'll just print a message
            print("Audio extraction completed. Ready for transcription.")
        else:
            print(f"Error: Audio file not found at {audio_path} after extraction.")
    else:
        print("Audio extraction failed.")

if __name__ == "__main__":
    main()