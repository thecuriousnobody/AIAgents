from crewai import Agent, Task, Crew, Process
import xml.etree.ElementTree as ET
import os
import sys
import re
import logging
from datetime import timedelta
from typing import List, Dict
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import serper_search_tool

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TranscriptSegment:
    def __init__(self, start_time: str, end_time: str, speaker: str, content: str):
        self.start_time = start_time
        self.end_time = end_time
        self.speaker = speaker
        self.content = content

    def __str__(self):
        return f"[{self.start_time} - {self.end_time}] {self.speaker}: {self.content}"

def parse_timestamp(timestamp: str) -> float:
    """Convert timestamp to seconds"""
    try:
        minutes, seconds = map(float, timestamp.split(':'))
        return minutes * 60 + seconds
    except ValueError as e:
        logger.error(f"Error parsing timestamp {timestamp}: {e}")
        return 0.0

def analyze_transcript(transcript_text: str) -> List[Dict]:
    """Enhanced transcript analysis with debug logging"""
    logger.info("Starting transcript analysis")
    segments = []
    
    # Updated regex pattern to match your transcript format
    pattern = r'\[(\d{2}:\d{2}\.\d{2}) - (\d{2}:\d{2}\.\d{2})\] ([^:]+): (.+)'
    
    # Log the first 500 characters of transcript for verification
    logger.debug(f"Transcript preview: {transcript_text[:500]}")
    
    matches = list(re.finditer(pattern, transcript_text))
    logger.info(f"Found {len(matches)} transcript segments")
    
    # Process matches into TranscriptSegment objects
    raw_segments = []
    for match in matches:
        start_time, end_time, speaker, content = match.groups()
        segment = TranscriptSegment(start_time, end_time, speaker, content)
        raw_segments.append(segment)
        logger.debug(f"Parsed segment: {segment}")
    
    # Analyze segments for topics and importance
    current_topic = None
    current_segments = []
    
    for i, segment in enumerate(raw_segments):
        # Topic detection heuristics
        topic_changes = [
            ("social_media", ["algorithm", "feed", "social media", "clickbait"]),
            ("ai_impact", ["AI", "artificial intelligence", "automation", "future"]),
            ("fitness_culture", ["gym", "workout", "fitness", "body"]),
            ("spirituality_critique", ["guru", "spiritual", "ashram", "religion"]),
            ("gender_roles", ["men", "women", "gender", "relationship"]),
            ("technology", ["technology", "internet", "digital", "online"]),
        ]
        
        content_lower = segment.content.lower()
        
        # Detect topic changes
        for topic, keywords in topic_changes:
            if any(keyword.lower() in content_lower for keyword in keywords):
                if current_topic != topic:
                    if current_segments:
                        # Save current segment group
                        combined_segment = {
                            'start_time': current_segments[0].start_time,
                            'end_time': current_segments[-1].end_time,
                            'title': current_topic,
                            'description': f"Discussion about {current_topic.replace('_', ' ')}",
                            'content': "\n".join(f"{s.speaker}: {s.content}" for s in current_segments),
                            'importance': len(current_segments)  # Basic importance scoring
                        }
                        segments.append(combined_segment)
                        logger.debug(f"Added segment: {combined_segment['title']} ({combined_segment['start_time']} - {combined_segment['end_time']})")
                    
                    current_topic = topic
                    current_segments = [segment]
                else:
                    current_segments.append(segment)
                break
    
    # Add final segment if exists
    if current_segments:
        combined_segment = {
            'start_time': current_segments[0].start_time,
            'end_time': current_segments[-1].end_time,
            'title': current_topic,
            'description': f"Discussion about {current_topic.replace('_', ' ')}",
            'content': "\n".join(f"{s.speaker}: {s.content}" for s in current_segments),
            'importance': len(current_segments)
        }
        segments.append(combined_segment)
    
    logger.info(f"Analysis complete. Found {len(segments)} content segments")
    return segments

def create_agents_and_tasks(transcript_path: str):
    content_analyzer = Agent(
        role="Content Analyzer",
        goal="Analyze podcast conversations for compelling segments, using timestamp information",
        backstory="""Expert content analyst skilled at:
        - Recognizing natural conversation breakpoints
        - Identifying topic transitions
        - Understanding context and flow
        - Processing timestamped transcripts""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    research_agent = Agent(
        role="Web Researcher",
        goal="Research context and background for identified segments",
        backstory="""Expert researcher who:
        - Finds relevant supporting material
        - Verifies factual claims
        - Provides additional context
        - Links to expert opinions""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )
    
    analyze_content_task = Task(
        description=f"""Analyze the transcript at '{transcript_path}'.
        The transcript contains timestamped entries in the format:
        [MM:SS.SS - MM:SS.SS] SPEAKER: Content
        
        Identify segments based on:
        - Natural topic transitions
        - Compelling discussions
        - Coherent conversation chunks
        - Clear context boundaries
        
        Use the timestamps to mark segment boundaries.""",
        agent=content_analyzer,
        expected_output="""Analysis including:
        1. List of segments with exact start/end timestamps
        2. Topic classification and descriptions
        3. Importance scores
        4. Speaker contributions
        5. Context notes"""
    )
    
    research_task = Task(
        description="""For each identified segment, research:
        - Supporting evidence for claims
        - Background information
        - Expert perspectives
        - Related discussions
        
        Focus on enhancing understanding of the conversation.""",
        agent=research_agent,
        expected_output="""For each segment:
        1. Relevant sources
        2. Supporting evidence
        3. Expert insights
        4. Additional context""",
        context=[analyze_content_task]
    )
    
    return [content_analyzer, research_agent], [analyze_content_task, research_task]

def create_fcpxml(segments: List[Dict]) -> str:
    """Generate FCP XML focused on marker placement"""
    root = ET.Element("fcpxml", version="1.10")
    
    # Resources section with basic format definition
    resources = ET.SubElement(root, "resources")
    ET.SubElement(resources, "format", 
        id="r1", name="FFVideoFormat1080p24", 
        frameDuration="1/24s", width="1920", height="1080")
    
    # Library structure
    library = ET.SubElement(root, "library")
    event = ET.SubElement(library, "event", name="Podcast Edit")
    project = ET.SubElement(event, "project", name="Podcast Edit Markers")
    sequence = ET.SubElement(project, "sequence", format="r1")
    spine = ET.SubElement(sequence, "spine")
    
    # Create a generic clip element to hold markers
    clip = ET.SubElement(spine, "clip", 
        name="Timeline", 
        duration="7200s")  # 2-hour default duration
    
    # Add markers for each segment
    for i, seg in enumerate(segments, 1):
        # IN marker
        in_marker = ET.SubElement(clip, "marker")
        # Convert timestamp to seconds for FCP
        start_seconds = str(parse_timestamp(seg['start_time'])) + "s"
        in_marker.set("start", start_seconds)
        in_marker.set("duration", "0s")
        in_marker.set("value", f"IN_{i}")
        in_note = (f"Segment: {seg['title']}\n"
                  f"Description: {seg['description']}\n"
                  f"Importance: {seg.get('importance', 'N/A')}")
        in_marker.set("note", in_note)
        
        # OUT marker
        out_marker = ET.SubElement(clip, "marker")
        end_seconds = str(parse_timestamp(seg['end_time'])) + "s"
        out_marker.set("start", end_seconds)
        out_marker.set("duration", "0s")
        out_marker.set("value", f"OUT_{i}")
        out_marker.set("note", f"End of segment: {seg['title']}")
    
    return ET.tostring(root, encoding='unicode', method='xml')

def validate_transcript_path(path: str) -> str:
    """Validate and clean transcript file path."""
    # Remove any quotes and extra whitespace
    clean_path = path.strip().strip("'\"")
    
    # Convert to absolute path if needed
    if not os.path.isabs(clean_path):
        clean_path = os.path.abspath(clean_path)
    
    # Check if file exists
    if not os.path.exists(clean_path):
        raise FileNotFoundError(f"Transcript file not found: {clean_path}")
    
    logger.info(f"Using transcript file: {clean_path}")
    return clean_path

def run_content_analyzer(transcript_path: str):
    try:
        # Validate and clean path
        transcript_path = validate_transcript_path(transcript_path)
        
        # Read transcript file
        with open(transcript_path, 'r') as f:
            transcript_text = f.read()
            logger.info(f"Successfully read transcript file: {transcript_path}")
    except Exception as e:
        logger.error(f"Error reading transcript file: {e}")
        return None

    # Initialize agents and tasks
    agents, tasks = create_agents_and_tasks(transcript_path)
    
    # Create crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    
    # Execute analysis
    logger.info("Starting crew analysis")
    result = crew.kickoff()
    
    # Analyze transcript directly
    logger.info("Performing direct transcript analysis")
    segments = analyze_transcript(transcript_text)
    
    # Generate output files
    directory = os.path.dirname(transcript_path)
    base_name = os.path.splitext(os.path.basename(transcript_path))[0]
    
    xml_path = os.path.join(directory, f"{base_name}_markers.fcpxml")
    segments_path = os.path.join(directory, f"{base_name}_segments.txt")
    research_path = os.path.join(directory, f"{base_name}_research.txt")
    
    

    try:
        # Create FCPXML
        xml_content = create_fcpxml(segments)
        with open(xml_path, 'w') as f:
            f.write(xml_content)
            logger.info(f"Created FCPXML file: {xml_path}")
        
        # Create human-readable segments file
        with open(segments_path, 'w') as f:
            f.write("# Podcast Segments\n\n")
            for i, seg in enumerate(segments, 1):
                f.write(f"## Segment {i}: {seg['title']}\n")
                f.write(f"Time: {seg['start_time']} - {seg['end_time']}\n")
                f.write(f"Description: {seg['description']}\n")
                f.write(f"Content:\n{seg['content']}\n\n")
                f.write("---\n\n")
            logger.info(f"Created segments file: {segments_path}")
        
        # Create research file if research results exist
        if 'research' in result:
            with open(research_path, 'w') as f:
                f.write(result['research'])
                logger.info(f"Created research file: {research_path}")
        
        print("\nGenerated files:")
        print(f"FCP Markers: {xml_path}")
        print(f"Segments: {segments_path}")
        if 'research' in result:
            print(f"Research: {research_path}")
            
    except Exception as e:
        logger.error(f"Error generating output files: {e}")
    
    return result

if __name__ == "__main__":
    try:
        transcript_path = input("Enter transcript file path: ").strip()
        # Validate path before processing
        transcript_path = validate_transcript_path(transcript_path)
        result = run_content_analyzer(transcript_path)
        print("\nAnalysis complete!")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
