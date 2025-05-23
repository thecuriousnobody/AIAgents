import os
import sys
from crewai import Agent, Task, Crew, Process, LLM
from search_tools_serper import serper_search_tool, serper_scholar_tool

# Initialize LLM instances
ClaudeSonnet = LLM(
    model="claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=8192,
    temperature=0.6
)

ClaudeHaiku = LLM(
    model="claude-3-5-haiku-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=8192,
    temperature=0.6
)

def create_agents_and_tasks(podcast_transcript):
    """Create podcast editing agents and tasks."""
    
    visual_enhancement_specialist = Agent(
        role="Visual Enhancement Specialist",
        goal="""Identify opportunities for adding supplementary visual content to enhance 
                the video podcast, including B-roll, screenshots, diagrams, and relevant imagery""",
        backstory="""Expert video editor specializing in visual storytelling and content enhancement.
                    Skilled at identifying moments where visual elements can strengthen the narrative
                    and improve viewer engagement. Experienced in sourcing and suggesting appropriate
                    supplementary content.""",
        tools=[serper_search_tool],
        llm=ClaudeSonnet
    )

    content_researcher = Agent(
        role="Content Researcher",
        goal="""Research and suggest relevant supplementary content including images, videos,
                websites, and academic resources that could enhance the viewer's understanding""",
        backstory="""Skilled researcher with expertise in finding high-quality supplementary
                    content from various sources. Experienced in identifying credible visual
                    and academic resources that can enhance video content.""",
        tools=[serper_search_tool, serper_scholar_tool],
        llm=ClaudeHaiku
    )

    engagement_optimizer = Agent(
        role="Engagement Optimizer",
        goal="""Identify key moments for visual enhancement and suggest creative ways to
                maintain viewer engagement through supplementary content""",
        backstory="""Expert in video engagement optimization with deep understanding of
                    audience retention strategies. Skilled at identifying opportunities
                    for visual enhancement and suggesting creative content additions.""",
        tools=[serper_search_tool],
        llm=ClaudeHaiku
    )

    visual_enhancement_analysis = Task(
        description=f"""Analyze the podcast transcript and identify opportunities for visual enhancement:
            1. B-roll Opportunities
                - Identify moments where B-roll footage could enhance the narrative
                - Suggest specific types of B-roll footage
                - Provide timestamps for each suggestion
            2. Visual Aid Recommendations
                - Points where diagrams/charts could clarify concepts
                - Opportunities for showing screenshots or images
                - Moments where on-screen text could reinforce key points
            3. Transition Enhancement
                - Visual transition opportunities
                - Suggestions for smooth visual flow
            
            Transcript to analyze: {podcast_transcript}""",
        agent=visual_enhancement_specialist,
        expected_output="""Detailed visual enhancement report with:
            1. B-ROLL SUGGESTIONS
               - [Timestamp] Description of needed B-roll
               - Specific visual elements to include
               - Suggested duration and style
            
            2. VISUAL AIDS
               - [Timestamp] Type of visual aid needed
               - Description of content to show
               - Purpose and impact
            
            3. TRANSITIONS
               - [Timestamp] Transition opportunities
               - Visual flow suggestions
               - Enhancement recommendations"""
    )

    supplementary_content = Task(
        description=f"""Research and identify specific supplementary content:
            1. Find relevant visual content
                - Images that illustrate key points
                - Video clips that demonstrate concepts
                - Websites or resources to showcase
            2. Source academic or technical content
                - Relevant research papers or studies
                - Technical diagrams or illustrations
                - Expert sources to reference
            3. Provide specific URLs and sources
                - Direct links to suggested content
                - Usage rights/licensing information
                - Alternative options if primary suggestions unavailable
            
            Transcript to analyze: {podcast_transcript}""",
        agent=content_researcher,
        expected_output="""Comprehensive content resource list:
            1. VISUAL RESOURCES
               - [Timestamp] URLs to specific images/videos
               - Source and licensing information
               - Alternative options
            
            2. ACADEMIC CONTENT
               - [Timestamp] Relevant papers/studies
               - Technical resource links
               - Expert source references
            
            3. ADDITIONAL RESOURCES
               - [Timestamp] Supplementary websites
               - Background information sources
               - Further reading suggestions"""
    )

    engagement_optimization = Task(
        description=f"""Analyze for engagement enhancement opportunities:
            1. Key Moments
                - Identify segments needing visual support
                - Suggest engagement-boosting visuals
                - Timestamp critical points
            2. Viewer Retention Strategies
                - Visual hooks and attention grabbers
                - Pattern interrupts and visual variety
                - Engagement maintenance techniques
            3. Creative Enhancement Ideas
                - Unique visual additions
                - Unexpected but relevant content
                - Memorable visual elements
            
            Transcript to analyze: {podcast_transcript}""",
        agent=engagement_optimizer,
        expected_output="""Strategic enhancement plan:
            1. KEY MOMENTS
               - [Timestamp] Critical points for enhancement
               - Specific visual suggestions
               - Expected impact on engagement
            
            2. RETENTION TACTICS
               - [Timestamp] Visual hook opportunities
               - Pattern interrupt suggestions
               - Engagement maintenance ideas
            
            3. CREATIVE ELEMENTS
               - [Timestamp] Unique visual suggestions
               - Unexpected content opportunities
               - Memorable visual moments"""
    )

    return [visual_enhancement_specialist, content_researcher, engagement_optimizer], [
        visual_enhancement_analysis,
        supplementary_content,
        engagement_optimization
    ]

def analyze_podcast(transcript):
    """Run the podcast analysis process."""
    try:
        # Create and run crew
        agents, tasks = create_agents_and_tasks(transcript)
        
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
        print(f"Error during podcast analysis: {str(e)}")
        return None

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
