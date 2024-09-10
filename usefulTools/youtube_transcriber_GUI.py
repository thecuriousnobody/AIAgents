import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import threading

def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'(?:youtube\.com\/embed\/)([^&\n?#]+)',
        r'(?:youtube\.com\/v\/)([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def generate_transcript():
    urls = url_entry.get("1.0", tk.END).strip().split("\n")
    output_dir = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Youtube_Transcripts"
    
    progress['maximum'] = len(urls)
    progress['value'] = 0
    
    def process_urls():
        for i, url in enumerate(urls):
            video_id = extract_video_id(url)
            if not video_id:
                root.after(0, lambda: messagebox.showerror("Error", f"Invalid YouTube URL: {url}"))
                continue
            
            api_url = "https://www.searchapi.io/api/v1/search"
            params = {
                "engine": "youtube_transcripts",
                "video_id": video_id,
                "api_key": config.SEARCH_API_KEY
            }
            
            try:
                response = requests.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                video_title = data.get("video_title", "Unknown_Title")
                safe_title = re.sub(r'[^\w\-_\. ]', '_', video_title)
                
                transcript = "\n".join([item["text"] for item in data.get("transcript", [])])
                
                filename = f"{safe_title[:50]}.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(transcript)
                
                root.after(0, lambda: progress.step())
                
            except requests.RequestException as e:
                root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate transcript for {url}: {str(e)}"))
        
        root.after(0, lambda: messagebox.showinfo("Complete", "All transcripts have been processed."))
        root.after(0, lambda: progress.config(value=0))

    threading.Thread(target=process_urls, daemon=True).start()

# Create main window
root = tk.Tk()
root.title("YouTube Transcript Generator")

# Create and pack widgets
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="YouTube URLs (one per line):").grid(column=0, row=0, sticky=tk.W, pady=5)
url_entry = tk.Text(frame, width=50, height=5)
url_entry.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5)

generate_button = ttk.Button(frame, text="Generate Transcripts", command=generate_transcript)
generate_button.grid(column=0, row=2, sticky=tk.W, pady=10)

progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress.grid(column=0, row=3, sticky=(tk.W, tk.E), pady=10)

# Start the GUI event loop
root.mainloop()