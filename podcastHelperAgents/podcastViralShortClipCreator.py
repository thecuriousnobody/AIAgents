from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import os
from typing import List, Dict, Tuple
import logging
import time
import json
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('podcast_clipper.log'),
        logging.StreamHandler()
    ]
)

class ContentType(Enum):
    INTELLECTUAL = "intellectual"
    EMOTIONAL = "emotional"
    CONTROVERSIAL = "controversial"
    PRACTICAL = "practical"
    THEORETICAL = "theoretical"

@dataclass
class ThematicElement:
    """Tracks thematic elements and their relevance"""
    theme: str
    keywords: List[str]
    importance: float  # 0-1 scale
    related_themes: List[str]

class ContentAnalytics:
    """Enhanced analytics incorporating both viral potential and thematic relevance"""
    
    def __init__(self, subject_matter: Dict[str, ThematicElement]):
        self.subject_matter = subject_matter
        self.emotional_keywords = [
            "incredible", "amazing", "shocking", "never", "breakthrough",
            "revolutionary", "unexpected", "surprising", "dramatic"
        ]
    
    def calculate_combined_score(self, segment: dict) -> Dict[str, float]:
        """Calculate combined score based on viral potential and thematic relevance"""
        
        # Calculate base viral score
        viral_score = self._calculate_viral_score(segment)
        
        # Calculate thematic relevance
        thematic_score = self._calculate_thematic_score(segment)
        
        # Calculate intellectual depth
        intellectual_score = self._calculate_intellectual_depth(segment)
        
        # Weighted combination
        combined_score = (
            viral_score * 0.4 +
            thematic_score * 0.4 +
            intellectual_score * 0.2
        )
        
        return {
            'combined_score': combined_score,
            'viral_score': viral_score,
            'thematic_score': thematic_score,
            'intellectual_score': intellectual_score,
            'content_type': self._determine_content_type(segment)
        }
    
    def _calculate_viral_score(self, segment: dict) -> float:
        score = 0
        text = segment['text'].lower()
        
        # Emotional impact
        score += sum(2 for word in self.emotional_keywords if word in text)
        
        # Length optimization
        duration = segment.get('duration', 0)
        if 15 <= duration <= 30:
            score += 5
        elif 10 <= duration <= 45:
            score += 3
        
        # Engagement factors
        if "?" in text: score += 2  # Questions
        if "!" in text: score += 1  # Emphasis
        
        return min(score / 10, 1.0)  # Normalize to 0-1
    
    def _calculate_thematic_score(self, segment: dict) -> float:
        score = 0
        text = segment['text'].lower()
        
        for theme in self.subject_matter.values():
            # Direct keyword matches
            keyword_matches = sum(1 for keyword in theme.keywords if keyword in text)
            score += keyword_matches * theme.importance
            
            # Related theme consideration
            for related in theme.related_themes:
                if related.lower() in text:
                    score += 0.5 * theme.importance
        
        return min(score, 1.0)  # Normalize to 0-1
    
    def _calculate_intellectual_depth(self, segment: dict) -> float:
        text = segment['text'].lower()
        score = 0
        
        # Intellectual indicators
        depth_markers = [
            "because", "therefore", "however", "although",
            "fundamental", "principle", "theory", "concept",
            "analysis", "research", "study", "evidence"
        ]
        
        score += sum(0.2 for marker in depth_markers if marker in text)
        
        # Complex sentence structure
        if len(text.split()) > 20: score += 0.2
        if ";" in text: score += 0.1
        
        return min(score, 1.0)  # Normalize to 0-1
    
    def _determine_content_type(self, segment: dict) -> ContentType:
        scores = {
            ContentType.INTELLECTUAL: self._calculate_intellectual_depth(segment),
            ContentType.EMOTIONAL: self._calculate_viral_score(segment),
            ContentType.THEORETICAL: self._calculate_thematic_score(segment)
        }
        return max(scores.items(), key=lambda x: x[1])[0]

def create_agents_and_tasks(transcript: str, podcast_metadata: dict, subject_matter: Dict[str, ThematicElement]) -> Tuple[List[Agent], List[Task]]:
    """Creates specialized agents and tasks for viral clip generation with thematic awareness"""
    
    content_analyzer = Agent(
        role="Content Intelligence Analyst",
        goal="Identify segments that balance viral potential with thematic relevance and intellectual depth",
        backstory="""You are an expert in content analysis with deep knowledge of both viral 
        mechanics and intellectual discourse. You understand how to identify moments that 
        are both engaging and substantively valuable.""",
        verbose=True,
        allow_delegation=False,
        llm=ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            max_tokens=4096
        )
    )
    
    narrative_architect = Agent(
        role="Narrative Flow Designer",
        goal="Craft compelling story arcs that maintain intellectual integrity while maximizing engagement",
        backstory="""You are a master storyteller who understands how to balance 
        intellectual depth with engaging narrative structure. You know how to create 
        compelling arcs that educate and entertain.""",
        verbose=True,
        allow_delegation=False,
        llm=ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            max_tokens=4096
        )
    )
    
    subject_expert = Agent(
        role="Subject Matter Expert",
        goal=f"Ensure clip maintains thematic coherence and intellectual value in {podcast_metadata['key_themes']}",
        backstory="""You are an expert in the podcast's subject matter, capable of 
        identifying key insights and ensuring the narrative maintains intellectual 
        integrity while remaining accessible.""",
        verbose=True,
        allow_delegation=False,
        llm=ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            max_tokens=4096
        )
    )

    # Task 1: Initial Content Analysis with Thematic Awareness
    analyze_content_task = Task(
        description=f"""Analyze the transcript for segments that balance viral potential with thematic relevance:

        Transcript:
        {transcript}

        Subject Matter Focus:
        {json.dumps({k: v.__dict__ for k, v in subject_matter.items()}, indent=2)}

        Requirements:
        1. Identify segments that:
           - Advance key themes and insights
           - Maintain intellectual depth
           - Have viral potential
           - Create emotional or intellectual resonance
        2. Score segments using ContentAnalytics system
        3. Ensure balanced representation of different content types
        4. Consider audience sophistication level
        5. Maintain precise timestamp tracking

        Metadata:
        {json.dumps(podcast_metadata, indent=2)}
        """,
        agent=content_analyzer,
        expected_output="JSON array of selected segments with comprehensive scoring"
    )

    # Additional tasks follow similar pattern...
    # [Tasks 2-4 would be updated similarly to incorporate thematic elements]

    return [content_analyzer, narrative_architect, subject_expert], [analyze_content_task]

def initialize_subject_matter(podcast_metadata: dict) -> Dict[str, ThematicElement]:
    """Initialize subject matter analysis framework based on podcast metadata"""
    
    subject_matter = {}
    
    for theme in podcast_metadata['key_themes']:
        # This would ideally come from a more sophisticated theme database
        if theme == "innovation":
            subject_matter[theme] = ThematicElement(
                theme=theme,
                keywords=["innovative", "breakthrough", "novel", "disruptive"],
                importance=0.9,
                related_themes=["creativity", "technology", "progress"]
            )
        elif theme == "creativity":
            subject_matter[theme] = ThematicElement(
                theme=theme,
                keywords=["creative", "artistic", "imaginative", "original"],
                importance=0.8,
                related_themes=["innovation", "expression", "design"]
            )
        # Add more theme definitions as needed
    
    return subject_matter

def run_viral_clip_generator(transcript: str, podcast_metadata: dict, max_retries: int = 3) -> dict:
    """Main function to generate viral-optimized podcast clips with thematic awareness"""
    
    # Initialize subject matter analysis
    subject_matter = initialize_subject_matter(podcast_metadata)
    
    # Create analytics engine
    analytics = ContentAnalytics(subject_matter)
    
    agents, tasks = create_agents_and_tasks(transcript, podcast_metadata, subject_matter)
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
        process=Process.sequential
    )

    # Rest of the function remains similar...

if __name__ == '__main__':
    try:
        # Get transcript file path
        transcript_file = input("Enter path to transcript file: ")
        with open(transcript_file, 'r') as f:
            transcript = f.read()
        
        # Enhanced metadata with more subject matter details
        podcast_metadata = {
            "title": "The Idea Sandbox",
            "episode": "EP123",
            "target_audience": ["entrepreneurs", "creators", "innovators"],
            "key_themes": ["innovation", "creativity", "business"],
            "tone": "intellectual but accessible",
            "target_platforms": ["YouTube", "Instagram", "LinkedIn"],
            "subject_depth": "intermediate to advanced",
            "discussion_focus": "intersection of creativity and business innovation"
        }
        
        # Generate the clip
        result = run_viral_clip_generator(transcript, podcast_metadata)
        
        # Save the result
        output_file = f"viral_clip_{podcast_metadata['episode']}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"\nThematic viral clip script generated and saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise