import os
import sys
from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import datetime
from serpapi import GoogleSearch
from search_tools import search_tool, youtube_tool, search_api_tool


# Add the parent directory to sys.path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set up API keys
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

# Initialize AI models
ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")


# Define agents
query_refiner = Agent(
    role='Query Refiner',
    goal='Distill raw text into focused search queries for both web and video content',
    backstory="You are an expert in understanding user intentions and crafting precise search queries for various types of content.",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet
)

researcher = Agent(
    role='Researcher',
    goal='Conduct comprehensive searches and gather vital information from both web and video sources',
    backstory="You are a skilled researcher with a knack for finding the most relevant and important information on any topic, using both web and video sources. You can effectively use parsed YouTube data to enhance your research.",
    verbose=True,
    allow_delegation=False,
    tools=[search_api_tool,youtube_tool],
    llm=ClaudeSonnet
)

organizer = Agent(
    role='Information Organizer',
    goal='Organize research results into a structured, easy-to-understand format, integrating both web and video content',
    backstory="You are an expert in information management, capable of organizing complex data from various sources into clear, concise, and useful formats. You excel at integrating information from both textual and video sources.",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet
)

# Define tasks
def refine_query_task_routine(topic):
    return Task(
        description=f"Take the user's topic '{topic}' and distill it into focused, effective search queries for both web and YouTube searches.",
        agent=query_refiner,
        expected_output="Two clear, concise search queries: one for web search and one for YouTube search, both capturing the essence of the user's topic.",
    )

def research_task_routine(refine_query_task):
    return Task(
        description="Use the refined queries to conduct comprehensive searches using both web and YouTube sources. Gather the most vital information on the topic, including relevant video content.",
        agent=researcher,
        expected_output="A comprehensive collection of the most relevant information from both web and video sources, including key points, links, and parsed YouTube video data.",
        context = [refine_query_task]
    )

def organize_info_task_routine(research_task):
    return Task(
        description="Take the research results from both web and video sources and organize them into a structured format. Integrate web-based information with relevant video content, ensuring clear attribution and easy navigation between different types of sources.",
        agent=organizer,
        expected_output="A well-organized document with key information from both web and video sources, including parsed YouTube data. The document should have clear sections for textual and video content, with easy-to-follow links and a coherent narrative that integrates both types of information.",
        context = [research_task]
    )

# Function to run the research process
def conduct_research(topic):
    print(f"Starting research on topic: {topic}")
    
    # Create tasks with the specific topic
    refine_query_task = refine_query_task_routine(topic)
    research_task = research_task_routine(refine_query_task)
    organize_info_task = organize_info_task_routine(research_task)
    
    # Create crew with the topic-specific tasks
    research_crew = Crew(
        agents=[query_refiner, researcher, organizer],
        tasks=[refine_query_task, research_task, organize_info_task],
        verbose=True,
        process=Process.sequential
    )
    
    # Run the crew with the topic as input
    result = research_crew.kickoff(inputs={"topic": topic})
    return result

# Example usage
if __name__ == "__main__":
    user_topic = input("Enter a topic to research: ")
    research_result = conduct_research(user_topic)
    print("\nResearch Results:")
    print(research_result)