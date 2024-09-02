import os
import sys
from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
from serpapi import GoogleSearch
import datetime

# Add the parent directory to sys.path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set up API keys
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

# Initialize AI models
ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")

# Set up search tools
def web_search(query):
    search = SerpAPIWrapper()
    return search.run(query)

def youtube_search(query):
    params = {
        "engine": "youtube",
        "search_query": query,
        "api_key": os.environ["SERPAPI_API_KEY"]
    }
    search = GoogleSearch(params)
    return search.get_dict()

def parse_youtube_results(json_data):
    parsed_results = []
    video_results = json_data.get("video_results", [])
    
    for video in video_results:
        channel = video.get("channel", {})
        parsed_video = {
            "title": video.get("title"),
            "link": video.get("link"),
            "channel_name": channel.get("name"),
            "channel_link": channel.get("link"),
            "views": video.get("views"),
            "published_date": video.get("published_date")
        }
        parsed_results.append(parsed_video)
    
    return parsed_results

web_search_tool = Tool(
    name="Web Search",
    func=web_search,
    description="Useful for finding general information on various topics from the web."
)

youtube_tool = Tool(
    name="YouTube Search",
    func=lambda q: parse_youtube_results(youtube_search(q)),
    description="Useful for searching YouTube for video content related to the topic. Returns parsed results including title, link, channel info, views, and publish date."
)

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
    tools=[web_search_tool, youtube_tool],
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
refine_query_task = Task(
    description="Take the user's raw text and distill it into focused, effective search queries for both web and YouTube searches.",
    agent=query_refiner,
    expected_output="Two clear, concise search queries: one for web search and one for YouTube search, both capturing the essence of the user's request.",
    context=None
)

research_task = Task(
    description="Use the refined queries to conduct comprehensive searches using both web and YouTube sources. Gather the most vital information on the topic, including relevant video content.",
    agent=researcher,
    expected_output="A comprehensive collection of the most relevant information from both web and video sources, including key points, links, and parsed YouTube video data.",
    context=["refine_query_task"]
)

organize_info_task = Task(
    description="Take the research results from both web and video sources and organize them into a structured format. Integrate web-based information with relevant video content, ensuring clear attribution and easy navigation between different types of sources.",
    agent=organizer,
    expected_output="A well-organized document with key information from both web and video sources, including parsed YouTube data. The document should have clear sections for textual and video content, with easy-to-follow links and a coherent narrative that integrates both types of information.",
    context=["research_task"]
)

# Create crew
research_crew = Crew(
    agents=[query_refiner, researcher, organizer],
    tasks=[refine_query_task, research_task, organize_info_task],
    verbose=2,
    process=Process.sequential
)

# Function to run the research process
def conduct_research(topic):
    print(f"Starting research on topic: {topic}")
    result = research_crew.kickoff(inputs={"topic": topic})
    return result

# Example usage
if __name__ == "__main__":
    user_topic = input("Enter a topic to research: ")
    research_result = conduct_research(user_topic)
    print("\nResearch Results:")
    print(research_result)