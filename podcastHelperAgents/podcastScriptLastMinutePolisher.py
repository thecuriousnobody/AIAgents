import os
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from PyPDF2 import PdfReader
import requests
from io import BytesIO

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
from usefulTools.llm_repository import ClaudeOpus,ClaudeSonnet
from usefulTools.search_tools import search_tool


# Initialize LLM and search tool
llm = ClaudeSonnet

def read_pdf_from_file(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def create_script_polisher_agent():
    return Agent(
        role="Podcast Script Polisher",
        goal="Refine and enhance the provided podcast script",
        backstory="""You are an expert in crafting engaging podcast content. Your role is to review 
        the provided script, identify areas for improvement, and suggest enhancements that will make 
        the conversation more dynamic and insightful.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_information_gatherer_agent():
    return Agent(
        role="Relevant Information Researcher",
        goal="Find additional pertinent information related to the podcast topic and guest",
        backstory="""You are a skilled researcher with a knack for uncovering valuable information. 
        Your task is to find relevant data, current events, or adjacent topics that could enrich 
        the podcast conversation.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )

def create_keyword_generator_agent():
    return Agent(
        role="Conversation Spark Generator",
        goal="Generate evocative keywords and phrases to inspire spontaneous questions",
        backstory="""You are a master of improvisation and creative thinking. Your role is to distill 
        complex topics into powerful keywords and short phrases that can spark engaging questions 
        and comments during the podcast.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_script_polishing_task(polisher_agent, script_content):
    return Task(
        description=f"""Review and polish the following podcast script. Identify areas for improvement 
        and suggest enhancements to make the conversation more engaging and insightful:
        
        {script_content}
        
        Focus on:
        1. Improving flow and coherence
        2. Enhancing the depth of discussion points
        3. Ensuring a balance of topics
        4. Suggesting potential follow-up questions or areas to explore further""",
        agent=polisher_agent,
        expected_output="""A refined version of the script with:
        1. Specific suggestions for improvements (2-3 per major section)
        2. 2-3 new discussion points or angles to consider
        3. A list of 3-5 potential follow-up questions
        4. Overall assessment of the script's strengths and areas for enhancement"""
    )

def create_information_gathering_task(gatherer_agent, guest_name, topic):
    return Task(
        description=f"""Research and gather additional information related to {guest_name} and the topic of {topic}. 
        Focus on:
        1. Recent developments or news in the field
        2. Related work by other experts or organizations
        3. Interesting statistics or data points
        4. Potential controversies or debates in the field
        5. Upcoming events or future trends related to the topic""",
        agent=gatherer_agent,
        expected_output="""A concise report containing:
        1. 3-5 recent news items or developments relevant to the topic
        2. 2-3 related projects or initiatives by other experts/organizations
        3. 3-5 interesting statistics or data points
        4. 1-2 current debates or controversies in the field
        5. 2-3 future trends or upcoming events related to the topic"""
    )

def create_keyword_generation_task(keyword_agent, script_content, research_output):
    return Task(
        description=f"""Based on the following script and research, generate a list of evocative keywords 
        and short phrases that can spark spontaneous questions and comments during the podcast:
        
        Script: {script_content}
        
        Research: {research_output}
        
        Focus on creating:
        1. Single words that encapsulate key concepts
        2. Short phrases (2-3 words) that highlight interesting angles
        3. Thought-provoking questions (5 words or less)
        4. Emotive terms related to the topic's impact""",
        agent=keyword_agent,
        expected_output="""A list of:
        1. 10-15 single-word keywords
        2. 7-10 short phrases (2-3 words each)
        3. 5-7 thought-provoking question starters (5 words or less)
        4. 5-7 emotive terms related to the topic's impact
        Each item should be accompanied by a brief (10 words or less) explanation of its relevance or potential use."""
    )

def main(guest_name, script_path, topic):
    script_content = read_pdf_from_file(script_path)

    polisher = create_script_polisher_agent()
    gatherer = create_information_gatherer_agent()
    keyword_generator = create_keyword_generator_agent()

    polishing_task = create_script_polishing_task(polisher, script_content)
    gathering_task = create_information_gathering_task(gatherer, guest_name, topic)
    keyword_task = create_keyword_generation_task(keyword_generator, "{{polishing_task.output}}", "{{gathering_task.output}}")

    crew = Crew(
        agents=[polisher, gatherer, keyword_generator],
        tasks=[polishing_task, gathering_task, keyword_task],
        verbose=2,
        process=Process.sequential
    )

    result = crew.kickoff()

    print(f"\nPodcast Enhancement Results for Guest: {guest_name}")
    print("\nScript Polishing Suggestions, Additional Information, and Conversation Sparks:")
    print(result)

if __name__ == "__main__":
    # guest_name = input("Enter the name of the podcast guest: ")
    # script_path = input("Enter the local path to your PDF script: ")
    # topic = input("Enter the main topic of the podcast: ")
    guest_name = "Marina Debris"
    script_path = "/Users/rajeevkumar/Downloads/Marina DeBris Final Script.pdf"
    topic = "Ocean waste, artivism"
    main(guest_name, script_path, topic)