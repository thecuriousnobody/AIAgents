import json
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
from anthropic import Anthropic
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
from serpapi import GoogleSearch

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


# Set up environment variables and API keys
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

# Set up search tools
search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="Useful for general internet searches."
)

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

youtube_tool = Tool(
    name="YouTube Search",
    func=lambda q: parse_youtube_results(youtube_search(q)),
    description="Useful for searching YouTube for video editors and their work. Returns parsed results."
)

# Set up language models
llm_GROQ = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ["GROQ_API_KEY"],
    model_name="gemma2-9b-it"
)

ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)

# Define agents
candidate_searcher = Agent(
    role='Indian Video Editor and Social Media Manager Searcher',
    goal='Find potential young, affordable Indian video editors and social media managers',
    backstory="""You are an expert at finding emerging talent in video editing and social media management, specifically from India. 
    You focus on discovering affordable, up-and-coming professionals who align with The Idea Sandbox podcast's mission. 
    You're skilled at using various online platforms to identify promising candidates, with a particular emphasis on Indian talent.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool, youtube_tool]
)

work_analyzer = Agent(
    role='Portfolio and Online Presence Analyzer',
    goal='Evaluate the work samples and online presence of potential Indian candidates',
    backstory="""You are an expert at analyzing the quality, style, and potential of Indian video editors and social media managers. 
    You can assess their work samples, online portfolios, and social media presence to determine if they align with 
    The Idea Sandbox podcast's mission and quality standards. You have a keen eye for identifying talent that offers high quality at affordable rates.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool, youtube_tool]
)

outreach_composer = Agent(
    role='Personalized Outreach Message Composer',
    goal='Craft compelling, personalized outreach messages for potential Indian video editors and social media managers',
    backstory="""You are skilled at composing engaging and personalized outreach messages tailored to Indian professionals. 
    You understand The Idea Sandbox podcast's mission and can convey it effectively to potential collaborators. 
    Your messages are warm, authentic, and emphasize the opportunity for growth, long-term collaboration, and the chance to work on an international project.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

# Define tasks
search_task = Task(
    description="""Search for potential young, affordable Indian video editors and social media managers. 
    Focus on emerging talent from India that shows promise but isn't yet established. Use YouTube, social media platforms, 
    and online portfolios to identify candidates. Compile a list of at least 5 promising Indian candidates with their contact information.
    Use search queries that specifically target Indian talent, such as "Indian YouTube video editors" or "emerging Indian social media managers".""",
    agent=candidate_searcher,
    expected_output="""A list of at least 5 promising Indian candidates, including for each:
    1. Full name
    2. Age (if available)
    3. Location in India
    4. Contact information (email, social media profiles)
    5. Brief description of their work and style
    6. Links to their portfolio or best work samples
    7. Any information on their rates or pricing (if available)
    8. Rationale for why they might be a good fit for The Idea Sandbox podcast
    9. Any relevant experience with international clients or projects"""
)

analyze_task = Task(
    description="""Analyze the work samples, portfolios, and online presence of the Indian candidates identified by the searcher. 
    Evaluate their style, quality, and potential alignment with The Idea Sandbox podcast's mission. Provide a detailed 
    assessment of each candidate's strengths and potential areas for growth. Consider their ability to deliver high-quality work at affordable rates.""",
    agent=work_analyzer,
    expected_output="""For each Indian candidate:
    1. Detailed analysis of their work quality and style
    2. Assessment of their technical skills
    3. Evaluation of their creativity and originality
    4. Analysis of their social media presence and engagement
    5. Potential alignment with The Idea Sandbox podcast's mission
    6. Strengths and areas for improvement
    7. Overall recommendation (Highly Recommended, Recommended, or Not Recommended)
    8. Ranking of candidates based on their potential fit for the podcast
    9. Assessment of their affordability and value for money
    10. Any evidence of their ability to work with international clients""",
    context=[search_task]
)

outreach_task = Task(
    description="""Craft personalized outreach messages for the top 3 Indian candidates identified by the analyzer. 
    Emphasize The Idea Sandbox podcast's mission (as found at tisb.world), the opportunity for growth, and the potential 
    for a long-term collaboration. Highlight that you're looking for authentic, idea-driven content rather than clickbait. 
    Mention the possibility of expanded collaboration as trust builds. Keep the tone warm, sincere, and enthusiastic.
    Emphasize the opportunity to work on an international project and potentially gain exposure to a global audience.""",
    agent=outreach_composer,
    expected_output="""For each of the top 3 Indian candidates:
    1. Subject line for the outreach email
    2. Personalized email body (250-350 words) that includes:
       - Warm greeting addressing the candidate by name
       - Brief introduction of The Idea Sandbox podcast and its mission
       - Specific mention of the candidate's work that impressed you
       - Clear explanation of the opportunity and potential for growth
       - Emphasis on authentic, idea-driven content creation
       - Highlight the international nature of the project
       - Invitation to discuss collaboration further
       - Your contact information and preferred method of communication
       - Enthusiastic closing
    3. Suggested follow-up strategy if no response is received within a week""",
    context=[search_task, analyze_task]
)

# Set up the crew
crew = Crew(
    agents=[candidate_searcher, work_analyzer, outreach_composer],
    tasks=[search_task, analyze_task, outreach_task],
    verbose=1,
    process=Process.sequential
)

# Run the crew
result = crew.kickoff()

print(result)