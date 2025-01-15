from typing import List, Optional, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from enum import Enum
import re
import os

class TranscriptFormat(Enum):
    """Format options for the transcript."""
    RAW = "raw"  # Returns transcript as is
    CHUNKS = "chunks"  # Returns transcript in time-based chunks

class YouTubeFreeLoaderWithSpeakers:
    """A class to load YouTube transcripts without requiring a paid API, with speaker diarization."""
    
    def __init__(
        self,
        url: str,
        add_video_info: bool = False,
        language: List[str] = ["en"],
        translation: Optional[str] = None,
        transcript_format: TranscriptFormat = TranscriptFormat.RAW,
        chunk_size_seconds: int = 120
    ):
        """Initialize the YouTube transcript loader.
        
        Args:
            url: YouTube video URL
            add_video_info: Whether to include video metadata
            language: List of language preferences in descending priority
            translation: Target language for translation
            transcript_format: Format of the transcript (RAW or CHUNKS)
            chunk_size_seconds: Size of chunks in seconds if using CHUNKS format
        """
        # Extract video ID and create full URL
        self.video_id = self._extract_video_id(url)
        self.url = f"https://www.youtube.com/watch?v={self.video_id}"
        
        self.add_video_info = add_video_info
        self.language = language
        self.translation = translation
        self.transcript_format = transcript_format
        self.chunk_size_seconds = chunk_size_seconds
        
    def _extract_video_id(self, url: str) -> str:
        """Extract the video ID from a YouTube URL."""
        patterns = [
            r'(?:v=|\/videos\/|embed\/|youtu.be\/|\/v\/|\/e\/|watch\?v%3D|watch\?feature=player_embedded&v=|%2Fvideos%2F|embed%\u200C\u200B2F|youtu.be%2F|%2Fv%2F)([^#\&\?\n]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        raise ValueError(
            f"Could not extract video ID from URL: {url}"
        )

    def _get_video_info(self) -> dict:
        """Get video metadata using pytube's innertube client."""
        from pytube.innertube import InnerTube

        info = {"url": self.url}
        
        try:
            # Create an innertube client
            innertube = InnerTube(client='WEB')
            
            # Get video metadata directly
            response = innertube.player(self.video_id)
            video_details = response.get('videoDetails', {})
            
            # Extract information
            info["title"] = video_details.get('title', 'Title unavailable')
            info["author"] = video_details.get('author', 'Author unavailable')
            info["length_seconds"] = int(video_details.get('lengthSeconds', 0))
            info["description"] = video_details.get('shortDescription', 'Description unavailable')
            info["view_count"] = int(video_details.get('viewCount', 0))
            
        except Exception as e:
            print(f"\nDebug - Error getting video info: {str(e)}")
            info["title"] = "Title unavailable"
            info["author"] = "Author unavailable"
            info["length_seconds"] = 0
            info["description"] = "Description unavailable"
            info["view_count"] = 0
            info["error"] = str(e)
            
        return info

    def _merge_speaker_segments(self, transcript: List[dict]) -> List[dict]:
        """Merge consecutive segments from the same speaker into chunks."""
        MIN_SPEAKER_SWITCH_GAP = 1.5  # Minimum time gap to consider a speaker switch
        MAX_MERGE_GAP = 2.0  # Maximum gap between segments to still merge them
        
        merged = []
        current_chunk = None
        current_speaker = 0
        
        for entry in transcript:
            # Calculate time gap if we have a previous chunk
            time_gap = 0
            if current_chunk:
                chunk_end = current_chunk["start"] + current_chunk["duration"]
                time_gap = entry["start"] - chunk_end
            
            # Decide if we should start a new chunk
            start_new_chunk = (
                current_chunk is None or  # First chunk
                time_gap > MIN_SPEAKER_SWITCH_GAP or  # Significant pause
                time_gap > MAX_MERGE_GAP  # Too big gap to merge
            )
            
            if start_new_chunk:
                # If we have a previous chunk, save it
                if current_chunk:
                    current_chunk["speaker"] = f"speaker_{current_speaker:02d}"
                    merged.append(current_chunk)
                
                # Start new chunk
                current_chunk = {
                    "text": entry["text"],
                    "start": entry["start"],
                    "duration": entry["duration"]
                }
                
                # Switch speaker if there was a significant gap
                if time_gap > MIN_SPEAKER_SWITCH_GAP:
                    current_speaker = 1 - current_speaker
            else:
                # Merge with current chunk
                current_chunk["text"] += " " + entry["text"]
                current_chunk["duration"] = (entry["start"] + entry["duration"]) - current_chunk["start"]
        
        # Add the last chunk
        if current_chunk:
            current_chunk["speaker"] = f"speaker_{current_speaker:02d}"
            merged.append(current_chunk)
        
        return merged

    def _format_transcript(self, transcript: List[dict]) -> List[dict]:
        """Format the transcript based on specified format and chunk size."""
        # Merge consecutive segments from the same speaker
        merged_transcript = self._merge_speaker_segments(transcript)
        
        if self.transcript_format == TranscriptFormat.RAW:
            return merged_transcript
            
        # For CHUNKS format, we'll respect the chunk_size_seconds parameter
        if len(merged_transcript) == 0:
            return []
            
        chunks = []
        current_chunk_start = 0
        current_chunk = []
        
        for entry in merged_transcript:
            if entry["start"] - current_chunk_start >= self.chunk_size_seconds and current_chunk:
                # Combine current chunk entries
                combined = {
                    "text": " ".join(e["text"] for e in current_chunk),
                    "start": current_chunk[0]["start"],
                    "duration": current_chunk[-1]["start"] + current_chunk[-1]["duration"] - current_chunk[0]["start"],
                    "speaker": current_chunk[0]["speaker"],
                    "url": f"{self.url}&t={int(current_chunk[0]['start'])}s"
                }
                chunks.append(combined)
                current_chunk = [entry]
                current_chunk_start = entry["start"]
            else:
                current_chunk.append(entry)
        
        # Add the last chunk
        if current_chunk:
            combined = {
                "text": " ".join(e["text"] for e in current_chunk),
                "start": current_chunk[0]["start"],
                "duration": current_chunk[-1]["start"] + current_chunk[-1]["duration"] - current_chunk[0]["start"],
                "speaker": current_chunk[0]["speaker"],
                "url": f"{self.url}&t={int(current_chunk[0]['start'])}s"
            }
            chunks.append(combined)
        
        return chunks if self.transcript_format == TranscriptFormat.CHUNKS else merged_transcript

    def load(self) -> List[dict]:
        """Load and return the transcript with optional video information."""
        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
            
            # Try to get transcript in preferred language
            transcript = None
            for lang in self.language:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
                    
            if transcript is None:
                # If no preferred language found, try to get any available transcript
                transcript = transcript_list.find_transcript([])
            
            # Get the actual transcript data
            if self.translation:
                # Translate if requested
                transcript = transcript.translate(self.translation)
            transcript_data = transcript.fetch()
            
            # Format transcript
            formatted_transcript = self._format_transcript(transcript_data)
            
            # Add video info if requested
            if self.add_video_info:
                video_info = self._get_video_info()
                for entry in formatted_transcript:
                    entry["video_info"] = video_info
                    
            return formatted_transcript
            
        except Exception as e:
            raise Exception(f"Error loading transcript: {str(e)}")


def save_transcript_to_file(transcript: List[dict], output_dir: str, video_info: dict) -> str:
    """Save the transcript as a text file.
    
    Args:
        transcript: List of transcript entries
        output_dir: Directory to save the transcript file
        video_info: Dictionary containing video information
        
    Returns:
        Path to the saved transcript file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a safe filename from the video title
    title = video_info.get("title", "untitled")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if not safe_title:
        safe_title = "untitled"
    
    # Create the full file path
    file_path = os.path.join(output_dir, f"{safe_title}.txt")
    
    # Format transcript text
    transcript_text = ""
    for i, entry in enumerate(transcript):
        # Get end time for the current segment
        end_time = entry["start"] + entry["duration"]
        
        # Format times as MM:SS
        start_minutes = int(entry["start"]) // 60
        start_seconds = int(entry["start"]) % 60
        end_minutes = int(end_time) // 60
        end_seconds = int(end_time) % 60
        
        # Format the line with time range and speaker
        time_range = f"[{start_minutes:02d}:{start_seconds:02d} - {end_minutes:02d}:{end_seconds:02d}]"
        speaker = entry.get("speaker", "speaker_00")
        
        # Add formatted line
        transcript_text += f"{time_range} {speaker}: {entry['text']}\n\n"
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        # Add video info header
        f.write(f"Title: {video_info.get('title', 'Unknown')}\n")
        f.write(f"Author: {video_info.get('author', 'Unknown')}\n")
        f.write(f"URL: {video_info.get('url', 'Unknown')}\n")
        f.write(f"Duration: {video_info.get('length_seconds', 0)} seconds\n")
        f.write("\n--- Transcript ---\n\n")
        f.write(transcript_text)
    
    return file_path

def main():
    """Main function to handle YouTube transcript extraction."""
    output_dir = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Youtube_Transcripts"
    
    try:
        # Get YouTube URL from user and clean it
        print("\nEnter YouTube URL: ", end='', flush=True)
        url = input().strip()
        
        # Remove any text before http or https if present
        if 'http' in url:
            url = url[url.find('http'):]
        
        # Initialize loader with video info enabled
        loader = YouTubeFreeLoaderWithSpeakers(url, add_video_info=True)
        
        print("Loading transcript...")
        transcript = loader.load()
        
        # Get video info for the file
        video_info = transcript[0].get("video_info", {}) if transcript else {}
        
        # Save transcript to file
        saved_path = save_transcript_to_file(transcript, output_dir, video_info)
        print(f"\nTranscript saved to: {saved_path}")
        
        # Print video info for verification
        print("\nVideo Information:")
        print(f"Title: {video_info.get('title', 'Unknown')}")
        print(f"Author: {video_info.get('author', 'Unknown')}")
        print(f"Duration: {video_info.get('length_seconds', 0)} seconds")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return

if __name__ == "__main__":
    main()
