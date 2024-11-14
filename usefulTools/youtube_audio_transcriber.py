import os
import whisper
from pytube import YouTube
from pydub import AudioSegment
import sys

def validate_youtube_url(url):
    """
    Validate YouTube URL and check if video is accessible
    """
    try:
        # Try creating a YouTube object to validate the URL
        yt = YouTube(url)
        # Try accessing video information to verify it's available
        yt.check_availability()
        return True, yt
    except Exception as e:
        if "Video unavailable" in str(e):
            return False, "This video is unavailable. It might be private or deleted."
        elif "Video is age restricted" in str(e):
            return False, "This video is age restricted and cannot be accessed."
        elif "regex_search" in str(e):
            return False, "Invalid YouTube URL. Please provide a valid YouTube video URL."
        else:
            return False, f"Error accessing video: {str(e)}"

def download_youtube_audio(url, output_path):
    """
    Download audio from YouTube video and convert to WAV format
    """
    try:
        # First validate the URL and get video info
        is_valid, result = validate_youtube_url(url)
        if not is_valid:
            print(f"\nError: {result}")
            return None, None
            
        yt = result
        print(f"\nVideo found: {yt.title}")
        print(f"Duration: {yt.length} seconds")
        
        # Get audio stream
        print("\nExtracting audio stream...")
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            print("Error: No audio stream available for this video.")
            return None, None
        
        # Download audio
        print("Downloading audio...")
        temp_path = audio_stream.download(output_path=output_path)
        
        # Convert to WAV format
        base_path = os.path.splitext(temp_path)[0]
        wav_path = f"{base_path}.wav"
        
        print("Converting to WAV format...")
        try:
            if temp_path.endswith('.mp4'):
                audio = AudioSegment.from_file(temp_path, format="mp4")
            else:
                audio = AudioSegment.from_file(temp_path)
            
            audio.export(wav_path, format="wav")
            print("Audio conversion successful.")
        except Exception as e:
            print(f"Error during audio conversion: {str(e)}")
            print("\nPlease ensure ffmpeg is installed:")
            print("- On macOS: brew install ffmpeg")
            print("- On Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("- On Windows: Download from https://www.ffmpeg.org/download.html")
            return None, None
        
        # Remove temporary file
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Warning: Could not remove temporary file {temp_path}: {str(e)}")
        
        print(f"Audio successfully saved as: {wav_path}")
        return wav_path, yt.title
        
    except Exception as e:
        print(f"Error during audio download: {str(e)}")
        return None, None

def transcribe_audio(audio_path, language="ta"):
    """
    Transcribe audio using OpenAI Whisper model
    """
    try:
        print("\nLoading Whisper model...")
        # Load the Whisper model (using medium model for better accuracy)
        model = whisper.load_model("medium")
        
        print("\nTranscribing audio... This may take a while depending on the video length.")
        # Transcribe the audio with specified language
        result = model.transcribe(
            audio_path,
            language=language,
            task="transcribe"
        )
        
        return result["text"]
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def main():
    print("\nYouTube Audio Transcriber")
    print("This tool will download a YouTube video's audio and transcribe it using OpenAI's Whisper model.")
    print("Note: Transcription quality may vary depending on audio quality and background noise.")
    print("\nRequirements:")
    print("- ffmpeg must be installed for audio processing")
    print("- Internet connection for downloading YouTube videos")
    print("- Sufficient disk space for temporary audio files")
    
    # Get YouTube URL
    url = input("\nPlease enter the YouTube video URL: ")
    
    # Create output directory if it doesn't exist
    output_dir = "/Users/rajeevkumar/Documents/TISB Stuff/guestPrep/YouTube Transcripts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Download audio
    audio_path, video_title = download_youtube_audio(url, output_dir)
    
    if audio_path and video_title:
        # Get language choice
        print("\nAvailable languages for transcription:")
        print("1. Tamil (ta)")
        print("2. English (en)")
        choice = input("Choose language (1 or 2): ")
        
        language = "ta" if choice == "1" else "en"
        
        # Transcribe audio
        transcription = transcribe_audio(audio_path, language)
        
        if transcription:
            # Save transcription
            transcript_filename = f"{video_title.replace(' ', '_')}_whisper_transcript_{language}.txt"
            transcript_path = os.path.join(output_dir, transcript_filename)
            
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcription)
            
            print(f"\nTranscription completed and saved to: {transcript_path}")
            
            # Clean up audio file
            try:
                os.remove(audio_path)
                print("Temporary audio file cleaned up.")
            except Exception as e:
                print(f"Note: Could not remove temporary audio file: {str(e)}")
        else:
            print("\nTranscription failed. Please try another video or check your installation.")
            print("Make sure you have sufficient system resources (CPU/RAM) for transcription.")
    else:
        print("\nFailed to process audio. Please check the URL and try again.")
        print("Make sure the video is publicly accessible and not age-restricted.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)
