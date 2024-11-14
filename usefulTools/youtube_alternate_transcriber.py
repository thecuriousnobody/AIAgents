import yt_dlp
import speech_recognition as sr
import os
from pydub import AudioSegment
import time
from deep_translator import GoogleTranslator
from urllib.parse import parse_qs, urlparse

def get_video_title(url):
    """Get the title of the YouTube video"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title', 'Untitled')
    except Exception as e:
        print(f"Error getting video title: {str(e)}")
        return 'Untitled'

def sanitize_filename(title):
    """Convert title to safe filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '_')
    return title[:100].strip('. ')

def split_audio(audio_path, chunk_length_ms=30000):
    """Split audio file into chunks"""
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunks.append(audio[i:i + chunk_length_ms])
    return chunks

def split_text_into_chunks(text, chunk_size=1000):
    """Split text into smaller chunks for translation"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        if current_length + word_length + 1 <= chunk_size:
            current_chunk.append(word)
            current_length += word_length + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def translate_text(text, source_lang='auto', target_lang='en'):
    """Translate text to specified language using deep_translator"""
    try:
        # Split text into smaller chunks
        chunks = split_text_into_chunks(text)
        translated_chunks = []
        
        print(f"Translating text in {len(chunks)} chunks...")
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        
        for i, chunk in enumerate(chunks, 1):
            try:
                print(f"Translating chunk {i} of {len(chunks)}...")
                translated = translator.translate(chunk)
                translated_chunks.append(translated)
                time.sleep(1)  # Add delay between translations
            except Exception as e:
                print(f"Error translating chunk {i}: {str(e)}")
                translated_chunks.append(chunk)
        
        return ' '.join(translated_chunks)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def download_and_transcribe(video_url, language='en-US', output_dir='/Users/rajeevkumar/Documents/TISB Stuff/guestPrep/YouTube Transcripts'):
    """Download a YouTube video, convert it to audio, transcribe it, and translate if needed."""
    try:
        # Get video title and create safe filename
        video_title = get_video_title(video_url)
        safe_title = sanitize_filename(video_title)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Download YouTube video audio
        print("Downloading video...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': 'temp_audio.%(ext)s'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        wav_file = "temp_audio.wav"
        
        # Split audio into chunks
        print("Splitting audio into chunks...")
        chunks = split_audio(wav_file)
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Process each chunk
        full_text = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1} of {len(chunks)}...")
            
            # Export chunk to temporary file
            chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            
            # Transcribe chunk
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language=language)
                    full_text.append(text)
                except sr.RequestError as e:
                    print(f"Could not request results for chunk {i+1}; {e}")
                except sr.UnknownValueError:
                    print(f"Could not understand audio in chunk {i+1}")
                
            # Clean up chunk file
            os.remove(chunk_path)
            
            # Add a small delay between API calls
            time.sleep(0.5)
        
        # Clean up main audio file
        os.remove(wav_file)
        
        # Join all transcribed text
        transcribed_text = " ".join(full_text)
        
        # Save original transcript
        original_transcript_path = os.path.join(output_dir, f"{safe_title}_original.txt")
        with open(original_transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcribed_text)
        print(f"Original transcript saved to {original_transcript_path}")
        
        # Translate and save English transcript if original language is not English
        if language != 'en-US':
            print("Translating to English...")
            # Map language codes to ISO format used by deep_translator
            lang_map = {
                'ta': 'ta',  # Tamil
                'en-US': 'en',  # English
                'fr': 'fr',  # French
            }
            source_lang = lang_map.get(language, 'auto')
            translated_text = translate_text(transcribed_text, source_lang=source_lang, target_lang='en')
            translated_transcript_path = os.path.join(output_dir, f"{safe_title}_english.txt")
            with open(translated_transcript_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
            print(f"English translation saved to {translated_transcript_path}")
            return original_transcript_path, translated_transcript_path
        
        return original_transcript_path, None
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None

# Example usage
if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    language = input("Enter language code (e.g., en-US, ta, fr) or press Enter for English: ") or 'en-US'
    
    original_path, translated_path = download_and_transcribe(video_url, language)
    
    if original_path:
        print("\nTranscription completed successfully!")
        if translated_path:
            print("Both original and English translations have been saved.")
