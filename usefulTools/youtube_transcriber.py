import requests
import os
import re
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def consolidate_transcript(response_text):
    try:
        data = json.loads(response_text)
        
        # Check for error message
        if 'error' in data:
            error_msg = data['error']
            if "doesn't exist or there are no translations available" in error_msg:
                print("\nThis video does not have any captions/transcripts available.")
                print("Possible reasons:")
                print("1. The video owner hasn't added any captions")
                print("2. Automatic captions are not available for this video")
                print("3. The video might be private or deleted")
            else:
                print(f"\nAPI Error: {error_msg}")
            return None
            
        transcript = data.get('transcripts', [])
        if not transcript:
            print("\nWarning: No transcripts found in the response")
            return None
        consolidated_text = ' '.join(item['text'] for item in transcript)
        return consolidated_text
    except json.JSONDecodeError as e:
        print(f"\nError: Unable to parse the API response. Error: {str(e)}")
        return None

def get_available_languages(video_id):
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_transcripts",
        "video_id": video_id,
        "api_key": config.SEARCH_API_KEY,
        "get_languages": "true"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = json.loads(response.text)
            if 'languages' in data:
                print("\nAvailable languages for this video:")
                for lang in data['languages']:
                    print(f"- {lang['language_code']}: {lang['language_name']}")
                return data['languages']
            elif 'error' in data:
                print(f"\nError getting languages: {data['error']}")
        return None
    except Exception as e:
        print(f"\nError getting available languages: {str(e)}")
        return None

def get_video_id(url):
    patterns = [
        r'watch\?v=([^&]*)',  # Standard YouTube URL
        r'youtu\.be/([^?]*)',  # Shortened YouTube URL
        r'embed/([^?]*)'       # Embedded YouTube URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    print("\nError: Unable to extract the video ID from the provided URL.")
    return None

def get_video_title(url):
    if url.startswith('http://') or url.startswith('https://'):
        video_id = get_video_id(url)
        
        if video_id is not None:
            url = f'https://www.youtube.com/watch?v={video_id}'
            try:
                response = requests.get(f'https://noembed.com/embed?url={url}')
                if response.status_code == 200:
                    data = response.json()
                    return data.get('title')
                else:
                    print(f"\nError fetching video title: Status code {response.status_code}")
            except Exception as e:
                print(f"\nError fetching video title: {str(e)}")
    return None

def get_transcript(video_id, lang=None):
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_transcripts",
        "video_id": video_id,
        "api_key": config.SEARCH_API_KEY
    }
    
    if lang:
        params["lang"] = lang
    
    try:
        print(f"\nRequesting transcript{' in ' + lang if lang else ' (default language)'}")
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return consolidate_transcript(response.text)
        else:
            print(f"\nError: API request failed with status code {response.status_code}")
            print("API Error Response:", response.text)
            return None
    except Exception as e:
        print(f"\nError making API request: {str(e)}")
        return None

def main():
    print("\nYouTube Transcript Extractor")
    print("Note: This tool can only extract transcripts from videos that have captions available.")
    print("If a video doesn't have any captions (manual or automatic), no transcript can be extracted.")
    
    youtube_url = input("\nPlease enter the full URL of the YouTube video: ")
    output_dir = "/Users/rajeevkumar/Documents/TISB Stuff/guestPrep/YouTube Transcripts"

    video_id = get_video_id(youtube_url)
    if video_id is None:
        print("Error: Unable to extract the video ID from the provided URL.")
        exit()

    # First, get available languages
    available_languages = get_available_languages(video_id)
    
    if not available_languages:
        print("\nTrying to get transcript in default language...")
        transcript = get_transcript(video_id)
    else:
        # Check if Tamil is available
        tamil_available = any(lang['language_code'] == 'ta' for lang in available_languages)
        
        if tamil_available:
            print("\nTamil transcript is available. Fetching Tamil transcript...")
            transcript = get_transcript(video_id, 'ta')
        else:
            print("\nTamil transcript is not available.")
            # Ask user if they want to proceed with default language
            proceed = input("Would you like to get the transcript in the default language? (y/n): ")
            if proceed.lower() == 'y':
                transcript = get_transcript(video_id)
            else:
                print("Operation cancelled.")
                exit()

    if transcript:
        video_title = get_video_title(youtube_url)
        if video_title is None:
            video_title = video_id
        
        filename = f"{video_title.replace(' ', '_')}_transcript.txt"
        filepath = os.path.join(output_dir, filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"\nTranscript has been saved to: {filepath}")
    else:
        print("\nFailed to get transcript. Please try another video that has captions available.")
        print("You can check if a video has captions by looking for the 'CC' button in the YouTube player.")

if __name__ == "__main__":
    main()
