import subprocess
import os
import sys
from pathlib import Path

def check_ffmpeg():
    ffmpeg_path = "/opt/homebrew/bin/ffmpeg"  # The path we know FFmpeg is installed at
    try:
        subprocess.run([ffmpeg_path, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ffmpeg_path
    except FileNotFoundError:
        print("FFmpeg is not installed or not in the expected location. Please install FFmpeg to continue.")
        return None

def extract_audio(video_path, audio_path, ffmpeg_path):
    """Extract audio from video file"""
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False
    
    command = f'"{ffmpeg_path}" -i "{video_path}" -ab 160k -ac 2 -ar 44100 -vn "{audio_path}"'
    try:
        subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE)
        print(f"Audio extracted successfully: {audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        print(f"FFmpeg error output: {e.stderr.decode()}")
        return False

def main():
    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        sys.exit(1)

    # Get input video path from user and clean it
    input_path = input("Enter the path to your video file: ").strip()
    
    # Remove any surrounding quotes
    input_path = input_path.strip("'\"")
    
    # Handle the path correctly - if it's absolute, use it directly
    if input_path.startswith('/'):
        video_path = input_path
    else:
        # Only resolve relative paths
        video_path = str(Path(input_path).resolve())
        
    print(f"Using video path: {video_path}")  # Debug print to verify path
    
    # Generate output audio path
    audio_dir = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage"
    audio_filename = os.path.splitext(os.path.basename(video_path))[0] + "_extracted_audio.wav"
    audio_path = os.path.join(audio_dir, audio_filename)

    if extract_audio(video_path, audio_path, ffmpeg_path):
        if os.path.exists(audio_path):
            print(f"Audio file created successfully at: {audio_path}")
            print("Audio extraction completed. Ready for transcription.")
        else:
            print(f"Error: Audio file not found at {audio_path} after extraction.")
    else:
        print("Audio extraction failed.")

if __name__ == "__main__":
    main()
