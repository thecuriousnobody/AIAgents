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
        transcript = data.get('transcripts', [])
        consolidated_text = ' '.join(item['text'] for item in transcript)
        return consolidated_text
    except json.JSONDecodeError:
        print("Error: Unable to parse the API response.")
        return None

def get_video_id(url):
    # Extract video ID from YouTube URL
    pattern = r'watch\?v=([^&]*)'
    match = re.search(pattern, url)
    
    if match is not None:
        return match.group(1)
    else:
        print("Error: Unable to extract the video ID from the provided URL.")
        return None

def get_video_title(url):
    # Extract video title from YouTube URL (this is a very basic approach and might not work for all cases)
    if url.startswith('http://') or url.startswith('https://'):
        video_id = get_video_id(url)
        
        if video_id is not None:
            url = f'https://www.youtube.com/watch?v={video_id}'
            data = requests.get(f'https://noembed.com/embed?url={url}').json()
            return data['title']
    else:
        return None

def main():
    # Ask user for YouTube URL
    youtube_url = input("Please enter the full URL of the YouTube video: ")

    output_dir = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Youtube_Transcripts"

    # Get video ID from YouTube URL
    video_id = get_video_id(youtube_url)
    
    if video_id is None:
        print("Error: Unable to extract the video ID from the provided URL.")
        exit()

    # Get video title (this might not work for all cases, a more robust solution would be needed)
    video_title = get_video_title(youtube_url)

    if video_title is None:
        print("Error: Unable to find the video title in the YouTube URL.")
        exit()
    
    filename = f"{video_title.replace(' ', '_')}_transcript.txt"

    filepath = os.path.join(output_dir, filename)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    url = "https://www.searchapi.io/api/v1/search"
    params = {
      "engine": "youtube_transcripts",
      "video_id": video_id,
      "api_key": config.SEARCH_API_KEY,
      "lang":"en"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        consolidated_transcript = consolidate_transcript(response.text)
        
        if consolidated_transcript is not None:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(consolidated_transcript)
            print(f"Consolidated transcript has been saved to: {filepath}")
        else:
            print("Failed to consolidate the transcript.")
    else:
        print(f"Error: API request failed with status code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
