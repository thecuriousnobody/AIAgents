from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from crewai_tools import YoutubeVideoSearchTool
from langchain_community.tools import DuckDuckGoSearchRun
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
# Ensure you have set up your API keys in your environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
# Initialize LLMs
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import search_api_tool

os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

def create_youtube_analyzer_agent(youtube_url):
    youtube_tool = YoutubeVideoSearchTool(youtube_video_url=youtube_url)
    return Agent(
        role="YouTube Content Analyzer",
        goal="Analyze the content of the specified YouTube video",
        backstory="""You are an expert in digital content analysis with a focus on YouTube videos. 
        Your task is to thoroughly analyze the provided video, extracting key information, insights, 
        and themes that could be relevant for a podcast interview.""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

def create_question_generator_agent():
    return Agent(
        role="Podcast Question Generator",
        goal="Generate compelling and insightful questions based on YouTube video analysis",
        backstory="""You are a seasoned podcast host and interviewer. Your expertise lies in crafting 
        thought-provoking questions that lead to engaging conversations. Use the insights from the 
        video analysis to create questions that will resonate with both the guest and the audience.""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

def create_video_analysis_task(analyzer_agent):
    return Task(
        description="""Analyze the content of the YouTube video. Provide:
        1. A summary of the main topics discussed
        2. Key quotes or statements made by the speaker
        3. Any unique perspectives or insights shared
        4. The overall tone and style of the speaker's communication
        5. Any recurring themes or ideas
        6. Potential areas of controversy or debate
        7. Background context that might be relevant for the interview""",
        agent=analyzer_agent,
        expected_output="""A comprehensive analysis of the YouTube video content, including:
        1. A concise summary of main topics (100-150 words)
        2. 3-5 key quotes with brief context
        3. List of 2-3 unique perspectives or insights
        4. Brief description of the speaker's communication style
        5. 2-3 recurring themes or ideas
        6. 1-2 potential areas of controversy or debate, if any
        7. Relevant background context (50-75 words)"""
    )

def create_question_generation_task(question_agent, content_analysis):
    return Task(
        description=f"""Based on the following content analysis, generate a set of 10-15 compelling questions for the podcast interview:
        {content_analysis}
        
        Your questions should:
        1. Cover the main topics identified in the video
        2. Explore unique perspectives shared by the speaker
        3. Encourage the speaker to elaborate on key statements or ideas
        4. Provide opportunities for the speaker to share new insights not covered in the video
        5. Include a mix of straightforward and thought-provoking questions
        6. Address any potential areas of controversy or debate respectfully
        7. Connect the speaker's ideas to broader industry trends or societal issues""",
        agent=question_agent,
        expected_output="""A list of 10-15 well-crafted interview questions, including:
        1. 3-4 questions on main topics from the video
        2. 2-3 questions exploring unique perspectives
        3. 2-3 questions asking for elaboration on key statements
        4. 2-3 questions probing for new insights
        5. 1-2 thought-provoking or challenging questions
        6. 1 question addressing potential controversies (if applicable)
        7. 1-2 questions connecting the speaker's ideas to broader contexts
        Each question should be clear, concise, and open-ended to encourage detailed responses."""
    )

def create_creative_inquiry_task(question_agent, content_analysis):
    return Task(
        description=f"""Based on the following content analysis, generate 10-15 highly original, 
        thought-provoking questions for the podcast interview. Your questions should:
        1. Uncover the guest's core motivations and the deeper purpose behind their work
        2. Explore unconventional or potentially controversial ideas related to their field
        3. Present hypothetical scenarios that challenge the guest to think beyond current constraints
        4. Draw unexpected connections between the guest's work and broader societal or philosophical concepts
        5. Encourage the guest to share their most ambitious, "blue sky" visions for the future

        Aim for questions that will surprise both the guest and the audience, leading to unique insights 
        and a memorable conversation.

        Content Analysis: {content_analysis}""",
        agent=question_agent,
        expected_output="""A list of 10-15 highly original and thought-provoking questions that:
        1. Probe into the guest's core motivations (2-4 questions)
        2. Explore unconventional ideas in the guest's field (2-4 questions)
        3. Present a challenging hypothetical scenario (2 question)
        4. Make an unexpected connection to broader concepts (2-4 questions)
        5. Encourage sharing of ambitious future visions (4 question)
        Each question should be unique, surprising, and capable of eliciting deep, insightful responses."""
    )

def main():
    guest_name = input("Enter the name of the podcast guest: ")
    youtube_url = input("Enter the URL of the YouTube video to analyze: ")
   
    analyzer = create_youtube_analyzer_agent(youtube_url)
    question_generator = create_question_generator_agent()

    analysis_task = create_video_analysis_task(analyzer)
    question_task = create_question_generation_task(question_generator, "{{analysis_task.output}}")
    creative_task = create_creative_inquiry_task(question_generator, "{{analysis_task.output}}")

    crew = Crew(
        agents=[analyzer, question_generator],
        tasks=[analysis_task, question_task, creative_task],
        verbose=2,
        process=Process.sequential
    )

    result = crew.kickoff()

    print(f"\nPodcast Preparation for Guest: {guest_name}")
    print("\nGenerated Questions and Creative Inquiries:")
    print(result)

if __name__ == "__main__":
    main()