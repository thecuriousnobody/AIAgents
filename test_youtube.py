import yt_dlp

def test_youtube_download(url):
    try:
        print(f"Attempting to access video at: {url}")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"Successfully accessed video: {info.get('title', 'No title')}")
            print("Video details:")
            print(f"Duration: {info.get('duration', 'Unknown')} seconds")
            print(f"Channel: {info.get('uploader', 'Unknown')}")
            print(f"Views: {info.get('view_count', 'Unknown')}")
        return True
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=MB-NcnpkF-0"
    test_youtube_download(url)
