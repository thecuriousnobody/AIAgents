import os
import sys
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crewai import Agent, Task, Crew, Process
from usefulTools.search_tools import serper_search_tool, serper_scholar_tool
import config
from usefulTools.llm_repository import ClaudeSonnet
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
# Initialize LLM instances


def split_transcript_into_chunks(transcript, chunk_size=4):
    """Split transcript into chunks of roughly chunk_size paragraphs each."""
    lines = transcript.split('\n')
    chunks = []
    current_chunk = []
    paragraph_count = 0
    
    for line in lines:
        current_chunk.append(line)
        
        # Count empty lines as paragraph separators
        if not line.strip():
            paragraph_count += 1
            
            # When we reach chunk_size paragraphs, save the chunk
            if paragraph_count >= chunk_size:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                paragraph_count = 0
    
    # Add any remaining lines as the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def create_agents_and_tasks(transcript_chunk, chunk_number, total_chunks):
    """Create podcast editing agents and tasks for a specific chunk."""
    
    context_analyzer = Agent(
        role="Context Analyzer",
        goal="""Analyze podcast transcript chunks to understand the conversation context
                and identify key discussion points that could benefit from visual enhancement""",
        backstory="""Expert content analyst specializing in understanding conversation flow
                    and context. Skilled at identifying key themes, important references,
                    and moments that could benefit from visual support.""",
        tools=[serper_search_tool],
        llm=ClaudeSonnet
    )

    visual_enhancement_specialist = Agent(
        role="Visual Enhancement Specialist",
        goal="""Based on conversation context, suggest specific visual enhancements
                including B-roll, screenshots, diagrams, and relevant imagery""",
        backstory="""Expert video editor specializing in visual storytelling and content enhancement.
                    Skilled at identifying moments where visual elements can strengthen the narrative
                    and improve viewer engagement.""",
        tools=[serper_search_tool],
        llm=ClaudeSonnet
    )

    content_researcher = Agent(
        role="Content Researcher",
        goal="""Research and find specific supplementary content that matches the
                conversation context and enhances viewer understanding""",
        backstory="""Skilled researcher with expertise in finding high-quality supplementary
                    content from various sources. Experienced in identifying credible visual
                    and academic resources that can enhance video content.""",
        tools=[serper_search_tool, serper_scholar_tool],
        llm=ClaudeSonnet
    )

    context_analysis = Task(
        description=f"""Analyze this chunk ({chunk_number}/{total_chunks}) of the podcast transcript:

            1. Conversation Context
                - Main topics being discussed
                - Key points or arguments made
                - Important references or examples mentioned
            2. Visual Enhancement Opportunities
                - Moments that need visual clarification
                - References that could benefit from visual aids
                - Complex concepts that need illustration
            
            Transcript chunk to analyze:
            {transcript_chunk}""",
        agent=context_analyzer,
        expected_output="""Context analysis report with:
            1. MAIN DISCUSSION POINTS
               - [Timestamp] Topic summary
               - Key arguments/points
               - Important references
            
            2. VISUAL OPPORTUNITIES
               - [Timestamp] Moments needing visuals
               - Concepts requiring illustration
               - Reference visualization needs"""
    )

    visual_enhancement = Task(
        description=f"""Based on the conversation context in this chunk ({chunk_number}/{total_chunks}),
            suggest specific visual enhancements:
            1. B-roll Opportunities
                - Identify moments where B-roll footage could enhance the narrative
                - Suggest specific types of B-roll footage
                - Provide timestamps for each suggestion
            2. Visual Aid Recommendations
                - Points where diagrams/charts could clarify concepts
                - Opportunities for showing screenshots or images
                - Moments where on-screen text could reinforce key points
            
            Transcript chunk to analyze:
            {transcript_chunk}""",
        agent=visual_enhancement_specialist,
        expected_output="""Visual enhancement suggestions with:
            1. B-ROLL NEEDS
               - [Timestamp] Description of needed B-roll
               - Specific visual elements to include
               - Suggested duration and style
            
            2. VISUAL AIDS
               - [Timestamp] Type of visual aid needed
               - Description of content to show
               - Purpose and impact"""
    )

    content_research = Task(
        description=f"""Research and identify specific supplementary content for this chunk ({chunk_number}/{total_chunks}):
            1. Find relevant visual content
                - Images that illustrate key points
                - Video clips that demonstrate concepts
                - Websites or resources to showcase
            2. Provide specific URLs and sources
                - Direct links to suggested content
                - Usage rights/licensing information
                - Alternative options if primary suggestions unavailable
            
            Transcript chunk to analyze:
            {transcript_chunk}""",
        agent=content_researcher,
        expected_output="""Content resource list with:
            1. VISUAL RESOURCES
               - [Timestamp] URLs to specific images/videos
               - Source and licensing information
               - Alternative options
            
            2. ADDITIONAL RESOURCES
               - [Timestamp] Supplementary websites
               - Background information sources
               - Further reading suggestions"""
    )

    return [context_analyzer, visual_enhancement_specialist, content_researcher], [
        context_analysis,
        visual_enhancement,
        content_research
    ]

def analyze_podcast_chunk(transcript_chunk, chunk_number, total_chunks):
    """Analyze a single chunk of the podcast transcript."""
    try:
        agents, tasks = create_agents_and_tasks(transcript_chunk, chunk_number, total_chunks)
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process=Process.sequential,
            memory=False,
            max_rpm=30
        )
        
        result = crew.kickoff()
        return result
    except Exception as e:
        print(f"Error analyzing chunk {chunk_number}: {str(e)}")
        return None

def analyze_podcast(transcript):
    """Run the podcast analysis process on chunks of the transcript."""
    chunks = split_transcript_into_chunks(transcript)
    total_chunks = len(chunks)
    
    print(f"\nSplit transcript into {total_chunks} chunks for analysis")
    all_results = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\nAnalyzing chunk {i}/{total_chunks}...")
        result = analyze_podcast_chunk(chunk, i, total_chunks)
        if result:
            all_results.append(f"\n\nCHUNK {i}/{total_chunks} ANALYSIS:\n{result}")
    
    return "\n".join(all_results) if all_results else None

def read_transcript(file_path):
    """Read transcript from the provided file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading transcript file: {str(e)}")
        return None

def main():
    # Get path and clean it by removing any quotes
    transcript_path = input("\nEnter the path to your transcript file: ").strip().strip("'\"")
    print(f"\nReading transcript from: {transcript_path}")
    
    transcript = read_transcript(transcript_path)
    if not transcript:
        return
    
    print("\nStarting podcast analysis...")
    result = analyze_podcast(transcript)
    
    if result:
        print("\nAnalysis Results:")
        print(result)
        
        # Save results to a file next to the transcript
        output_path = os.path.join(
            os.path.dirname(transcript_path),
            f"visual_enhancement_suggestions_{os.path.basename(transcript_path)}"
        )
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(result))
            print(f"\nResults saved to: {output_path}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")
    else:
        print("\nAnalysis failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
