import os
import sys
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
import config
from anthropic import APIStatusError
import time
from usefulTools.search_tools import search_api_tool
from usefulTools.llm_repository import ClaudeSonnet

# Set up environment variables and API keys
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

# Initialize tools and models
llm = ClaudeSonnet

def retry_on_overload(func, max_retries=5, initial_wait=1):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except APIStatusError as e:
                if 'overloaded_error' in str(e):
                    wait_time = initial_wait * (2 ** retries)
                    print(f"API overloaded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise
        raise Exception("Max retries reached. API still overloaded.")
    return wrapper

@retry_on_overload
def kickoff_crew(crew):
    return crew.kickoff()

# Define agents
def create_transcript_analyzer_agent():
    return Agent(
        role="Transcript Analyzer",
        goal="Analyze the podcast transcript and identify claims or statements that could benefit from supporting research",
        backstory="You are an expert in content analysis, capable of identifying key claims and statements that would be strengthened by additional research or data.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_research_agent():
    return Agent(
        role="Research Specialist",
        goal="Find relevant and up-to-date information to support or contextualize identified claims",
        backstory="You are a skilled researcher with a talent for finding accurate and pertinent information from various online sources to support or provide context for claims made in the podcast.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

def create_content_integrator_agent():
    return Agent(
        role="Content Integrator",
        goal="Compile research findings and create a structured output with timestamps for video integration",
        backstory="You are an experienced content producer who can effectively organize research findings and link them to appropriate points in the podcast transcript for seamless integration into the final video.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

# Define tasks
def analyze_transcript_task(agent, transcript):
    return Task(
        description=f"Analyze the following podcast transcript and identify 5-10 key claims or statements that could benefit from supporting research. For each identified claim, provide the timestamp and a brief explanation of why it needs support:\n\n{transcript}\n\nProvide a list of claims with their timestamps and explanations.",
        agent=agent,
        expected_output="A list of 5-10 claims or statements from the podcast, each with its timestamp and a brief explanation of why it needs supporting research."
    )

def research_claims_task(agent, claims):
    return Task(
        description=f"Research and gather relevant, up-to-date information to support or contextualize the following claims:\n\n{claims}\n\nFor each claim, provide a summary of your findings, including sources where appropriate.",
        agent=agent,
        expected_output="A detailed summary of relevant data, statistics, or contextual information for each claim, with sources.",
        tools=[search_api_tool]
    )

def integrate_content_task(agent, claims, research):
    return Task(
        description=f"Create a structured output that integrates the original claims and the research findings. For each claim:\n1. Provide the original timestamp\n2. Briefly state the claim\n3. Summarize the supporting research or context\n4. Suggest a concise (1-2 sentences) statement to be added to the video\n\nClaims: {claims}\n\nResearch: {research}\n\nFormat the output so it can be easily used to enhance the video content.",
        agent=agent,
        expected_output="A structured document with timestamps, claims, supporting research, and suggested statements for video integration."
    )

def main(transcript_file):
    # Read the transcript
    with open(transcript_file, 'r') as f:
        transcript = f.read()

    # Create agents
    transcript_analyzer = create_transcript_analyzer_agent()
    researcher = create_research_agent()
    content_integrator = create_content_integrator_agent()

    # Create tasks
    analyze_task = analyze_transcript_task(transcript_analyzer, transcript)
    research_task = research_claims_task(researcher, "{{analyze_task.output}}")
    integrate_task = integrate_content_task(content_integrator, "{{analyze_task.output}}", "{{research_task.output}}")

    # Create and run the crew
    podcast_enhancement_crew = Crew(
        agents=[transcript_analyzer, researcher, content_integrator],
        tasks=[analyze_task, research_task, integrate_task],
        verbose=2,
        process=Process.sequential
    )

    result = kickoff_crew(podcast_enhancement_crew)

    # Generate output file name based on input file
    input_filename = os.path.basename(transcript_file)
    output_filename = f"research_suggestions_{os.path.splitext(input_filename)[0]}.txt"
    output_file = os.path.join(os.path.dirname(transcript_file), output_filename)

    # Write the final output to a file
    with open(output_file, 'w') as f:
        f.write(result)

    print(f"Enhanced content suggestions have been written to {output_file}")

if __name__ == "__main__":
    transcript_file = input("Enter the path to the podcast transcript file: ")
    main(transcript_file)