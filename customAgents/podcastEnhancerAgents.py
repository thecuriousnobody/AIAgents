from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ContentInsight:
    timestamp: str
    topic: str
    theme: str
    description: str
    connections: List[str]
    potential_references: List[Dict]
    b_roll_suggestions: List[Dict]
    quotes: List[Dict]

@dataclass
class EditingRecommendation:
    segment_start: str
    segment_end: str
    enhancement_type: str
    source_link: str
    context: str
    rationale: str

def create_enhanced_agents():
    """Create specialized agents for podcast content analysis and enhancement"""
    
    pattern_detector = Agent(
        role="Pattern Detective",
        goal="""Identify recurring themes, systemic patterns, and intellectual frameworks.
            Connect ideas across domains and find surprising parallels.""",
        backstory="""Expert at recognizing deep structures and patterns in conversations.
            Trained to think laterally and draw unexpected connections.""",
        verbose=True
    )
    
    cultural_anthropologist = Agent(
        role="Cultural Anthropologist",
        goal="""Find relevant cross-cultural comparisons and contrasts.
            Identify how different societies approach similar challenges.""",
        backstory="""Scholar of comparative cultural studies.
            Expert at contextualizing ideas within different cultural frameworks.""",
        verbose=True
    )
    
    content_curator = Agent(
        role="Content Curator", 
        goal="""Discover compelling supplementary content that enriches the discussion:
            - Academic papers and expert opinions
            - Historical parallels and precedents
            - Contemporary examples and case studies
            - Contrarian viewpoints and creative tensions""",
        backstory="""Research specialist with deep knowledge of academic and media sources.
            Expert at finding content that adds depth while maintaining accessibility.""",
        verbose=True
    )
    
    visual_storyteller = Agent(
        role="Visual Storyteller",
        goal="""Identify opportunities for visual enhancement:
            - B-roll footage suggestions
            - Illustrative examples
            - Data visualizations
            - Scene-setting imagery""",
        backstory="""Expert in visual communication and storytelling.
            Skilled at finding ways to make abstract concepts tangible.""",
        verbose=True
    )

    return [pattern_detector, cultural_anthropologist, content_curator, visual_storyteller]

def analyze_segment(transcript_segment: str, agents: List[Agent]) -> ContentInsight:
    """Analyze a transcript segment using multiple agents"""
    
    [pattern_detector, cultural_anthropologist, content_curator, visual_storyteller] = agents
    
    # Pattern detection
    patterns = pattern_detector.analyze(transcript_segment)
    
    # Cultural analysis
    cultural_context = cultural_anthropologist.analyze(transcript_segment)
    
    # Content curation
    supplementary_content = content_curator.find_content(
        context=transcript_segment,
        patterns=patterns,
        cultural_context=cultural_context
    )
    
    # Visual enhancement
    visual_suggestions = visual_storyteller.suggest_visuals(
        context=transcript_segment,
        content=supplementary_content
    )
    
    return ContentInsight(
        timestamp=extract_timestamp(transcript_segment),
        topic=patterns['main_topic'],
        theme=patterns['theme'],
        description=patterns['summary'],
        connections=patterns['connections'],
        potential_references=supplementary_content['references'],
        b_roll_suggestions=visual_suggestions['b_roll'],
        quotes=supplementary_content['quotes']
    )

def generate_editing_recommendations(
    insights: List[ContentInsight]
) -> List[EditingRecommendation]:
    """Generate specific editing recommendations based on content insights"""
    
    recommendations = []
    
    for insight in insights:
        # Generate B-roll recommendations
        for suggestion in insight.b_roll_suggestions:
            recommendations.append(
                EditingRecommendation(
                    segment_start=suggestion['start_time'],
                    segment_end=suggestion['end_time'],
                    enhancement_type='b_roll',
                    source_link=suggestion['source'],
                    context=suggestion['context'],
                    rationale=suggestion['rationale']
                )
            )
            
        # Generate quote overlay recommendations
        for quote in insight.quotes:
            if quote['relevance_score'] > 0.8:
                recommendations.append(
                    EditingRecommendation(
                        segment_start=quote['timestamp'],
                        segment_end=str(float(quote['timestamp']) + 5.0),
                        enhancement_type='quote_overlay',
                        source_link=quote['source'],
                        context=quote['context'],
                        rationale=quote['rationale']
                    )
                )
                
        # Generate visualization recommendations
        for connection in insight.connections:
            if connection['visualization_potential'] > 0.7:
                recommendations.append(
                    EditingRecommendation(
                        segment_start=insight.timestamp,
                        segment_end=str(float(insight.timestamp) + 10.0),
                        enhancement_type='visualization',
                        source_link=connection['data_source'],
                        context=connection['context'],
                        rationale=connection['rationale']
                    )
                )
    
    return recommendations

def format_editor_instructions(
    recommendations: List[EditingRecommendation]
) -> str:
    """Format editing recommendations into clear instructions"""
    
    instructions = []
    
    for rec in sorted(recommendations, key=lambda x: x.segment_start):
        instruction = f"""
Segment: {rec.segment_start} - {rec.segment_end}
Enhancement Type: {rec.enhancement_type}
Source: {rec.source_link}

Context: {rec.context}
Rationale: {rec.rationale}

---"""
        instructions.append(instruction)
        
    return "\n".join(instructions)

def split_into_segments(transcript: str) -> List[Dict]:
    """Split transcript into logical segments based on topic shifts and natural breaks"""
    segments = []
    current_segment = {
        'text': [],
        'start_time': None,
        'end_time': None,
        'speaker': None
    }
    
    # Regular expression for timestamp lines like [HH:MM:SS.SS - HH:MM:SS.SS]
    timestamp_pattern = r'\[(\d{2}:\d{2}\.\d{2}) - (\d{2}:\d{2}\.\d{2})\]'
    
    for line in transcript.split('\n'):
        # Check for timestamp markers
        timestamp_match = re.match(timestamp_pattern, line)
        if timestamp_match:
            if current_segment['text']:
                segments.append(current_segment)
                current_segment = {
                    'text': [],
                    'start_time': None,
                    'end_time': None,
                    'speaker': None
                }
            
            current_segment['start_time'] = timestamp_match.group(1)
            current_segment['end_time'] = timestamp_match.group(2)
            
            # Extract speaker if present
            speaker_match = re.search(r'\] (.+?):', line)
            if speaker_match:
                current_segment['speaker'] = speaker_match.group(1)
                
            # Add the actual content
            content = line.split(':', 1)[-1].strip()
            if content:
                current_segment['text'].append(content)
        else:
            # Add non-timestamp lines to current segment
            if line.strip():
                current_segment['text'].append(line.strip())
    
    # Add final segment
    if current_segment['text']:
        segments.append(current_segment)
    
    return segments

def main(transcript_path: str):
    # Initialize agents
    agents = create_enhanced_agents()
    
    # Process transcript
    with open(transcript_path) as f:
        transcript = f.read()
    
    # Analyze content
    segments = split_into_segments(transcript)
    insights = [analyze_segment(seg, agents) for seg in segments]
    
    # Generate recommendations
    recommendations = generate_editing_recommendations(insights)
    
    # Format instructions
    instructions = format_editor_instructions(recommendations)
    
    # Save outputs
    output_dir = os.path.dirname(transcript_path)
    base_name = os.path.splitext(os.path.basename(transcript_path))[0]
    
    with open(os.path.join(output_dir, f"{base_name}_edit_instructions.txt"), 'w') as f:
        f.write(instructions)
    
    return {
        'insights': insights,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    transcript_path = input("Enter transcript path: ")
    results = main(transcript_path)
    print("Analysis complete! Editor instructions generated.")