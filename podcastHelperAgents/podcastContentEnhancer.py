from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import search_tool, youtube_tool, search_api_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

def create_agents_and_tasks(transcript):
    content_analyzer = Agent(
        role="Content Analyzer",
        goal="Analyze the transcript to identify moments where supporting content could enhance understanding or engagement",
        backstory="You are an expert at identifying opportunities in conversations where additional context, data, or visuals could make the content more compelling and informative.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    timestamp_extractor = Agent(
        role="Timestamp Extractor",
        goal="Extract and process timestamp information for identified enhancement opportunities",
        backstory="You are skilled at processing transcript timestamps and determining the most relevant timeframes for content enhancement.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    content_suggester = Agent(
        role="Content Suggester",
        goal="Suggest specific, compelling supporting content for identified moments",
        backstory="You are an expert at finding and suggesting relevant scholarly articles, data visualizations, news pieces, and other content that can enhance the conversation's depth and credibility.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

    analyze_content_task = Task(
        description=f"""Analyze the transcript and identify 5-10 key moments where supporting content could enhance the conversation.
        Focus on moments where:
        1. Complex concepts are discussed that could benefit from visualization
        2. Claims or statements that could be supported by data or research
        3. Historical references that could be enriched with context
        4. Technical concepts that could be illustrated
        5. Controversial topics that could benefit from balanced sources
        
        Ignore moments that would only benefit from literal or obvious illustrations.""",
        agent=content_analyzer,
        expected_output="""A list of 5-10 key moments, each including:
        1. Brief description of the discussion point
        2. Why this moment would benefit from enhancement
        3. Type of supporting content that would be most effective
        4. Rough location in the transcript"""
    )

    extract_timestamps_task = Task(
        description="For each identified moment, extract and process the timestamp information to provide precise timing for content insertion.",
        agent=timestamp_extractor,
        expected_output="""For each moment:
        1. Start timestamp
        2. End timestamp
        3. Speaker name/identifier
        4. Exact quote or summary of relevant speech
        5. Notes on timing considerations""",
        context=[analyze_content_task]
    )

    suggest_content_task = Task(
        description="""For each timestamped moment, suggest specific supporting content that would enhance the conversation.
        Focus on compelling and credible sources that add genuine value.""",
        agent=content_suggester,
        expected_output="""For each moment:
        1. Specific content suggestions (URLs, descriptions, or search terms)
        2. Why this content would be effective
        3. How it should be integrated
        4. Alternative suggestions if primary suggestion isn't available
        5. Any technical or copyright considerations""",
        context=[extract_timestamps_task]
    )

    return [content_analyzer, timestamp_extractor, content_suggester], [analyze_content_task, extract_timestamps_task, suggest_content_task]

def run_content_enhancer(transcript):
    agents, tasks = create_agents_and_tasks(transcript)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    output = crew.kickoff()
    return output

def save_enhancement_suggestions(transcript_name, result):
    # Create output filename based on input transcript name
    output_filename = f"{transcript_name}_enhancement_suggestions.txt"
    
    try:
        with open(output_filename, "w") as file:
            file.write(str(result))
        print(f"\nResults saved to {output_filename}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Get transcript file path from user
    transcript_path = input("Enter the path to your transcript file: ")
    
    try:
        # Read the transcript file
        with open(transcript_path, 'r') as file:
            transcript = file.read()
            
        # Get base filename without extension for output file naming
        transcript_name = os.path.splitext(os.path.basename(transcript_path))[0]
        
        # Process the transcript
        result = run_content_enhancer(transcript)
        
        print("\nContent Enhancement Suggestions:")
        print(result)
        
        # Save results
        save_enhancement_suggestions(transcript_name, result)
        
    except FileNotFoundError:
        print(f"Error: Could not find transcript file at {transcript_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
