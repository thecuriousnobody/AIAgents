import os
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from serpapi import GoogleSearch
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# # Set up Google search tool
search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="Useful for finding current data and information on various topics."
)

def search_api_search(query):
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": config.SEARCH_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

def run_search(query: str) -> str:
    results = search_api_search(query)
    
    # Process and format the results
    formatted_results = []
    for item in results.get('organic_results', []):
        formatted_results.append(f"Title: {item.get('title')}")
        formatted_results.append(f"Link: {item.get('link')}")
        formatted_results.append(f"Snippet: {item.get('snippet')}")
        formatted_results.append("---")
    
    return "\n".join(formatted_results)

search_api_tool = Tool(
    name="Internet Search",
    func=run_search,
    description="Useful for finding current data and information on various topics using the SearchAPI."
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
    func=lambda query: parse_youtube_results(youtube_search(query)),
    description="Useful for searching YouTube for video content related to the topic. Returns parsed results including title, link, channel info, views, and publish date."
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

def google_search_for_twitter(query, num_pages=20):
    logger.info(f"Starting Google search for Twitter results. Query: {query}")
    all_tweets = []
    
    for page in range(num_pages):
        params = {
            "engine": "google",
            "q": f"{query} site:twitter.com",
            "api_key": SERPAPI_API_KEY,
            "start": page * 10,  # 10 results per page
            "num": 10
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            page_tweets = [
                {
                    "link": result.get("link"),
                    "snippet": result.get("snippet"),
                    "title": result.get("title")
                }
                for result in organic_results if "twitter.com" in result.get("link", "")
            ]
            all_tweets.extend(page_tweets)
            
            if len(page_tweets) < 10:
                break  # Stop if we get fewer results than expected (last page)
            
            if len(all_tweets) >= 200:
                break  # Stop if we've reached or exceeded 200 results
            
        except Exception as e:
            logger.error(f"An error occurred during the Google search: {str(e)}")
            break
    
    logger.info(f"Total tweets collected: {len(all_tweets)}")
    return {"tweets": all_tweets[:200]}  # Ensure we return at most 200 results

google_twitter_tool = Tool(
    name="Google Search for Twitter",
    func=lambda query: google_search_for_twitter(query, num_pages=20),
    description="Searches Google for Twitter results related to the topic. Returns up to 200 parsed results including tweet snippets and links from multiple pages of search results."
)


import os
import requests
from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional


# Define input schemas
class SerperSearchInput(BaseModel):
    """Input schema for the Internet Search tool."""
    query: str = Field(..., description="The search query to execute")

class SerperScholarInput(BaseModel):
    """Input schema for the Scholar Search tool."""
    query: str = Field(..., description="The academic search query to execute")
    num_results: Optional[int] = Field(default=20, description="Number of results to return")

def serper_search(query: str) -> str:
    try:
        url = "https://google.serper.dev/search"
        payload = {
            "q": query
        }
        headers = {
            'X-API-KEY': config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Process and format the results
        formatted_results = []
        
        # Handle organic results
        for item in data.get('organic', []):
            formatted_results.append(f"Title: {item.get('title', 'No title')}")
            formatted_results.append(f"Link: {item.get('link', 'No link')}")
            formatted_results.append(f"Snippet: {item.get('snippet', 'No snippet')}")
            formatted_results.append("---")
        
        if not formatted_results:
            return "No results found or error in search."
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"An error occurred while searching: {str(e)}"

def serper_scholar_search(query: str, num_results: int = 20) -> str:
    try:
        # Modify the query to target scholarly content
        scholarly_query = f"{query} site:scholar.google.com"
        
        url = "https://google.serper.dev/search"
        payload = {
            "q": scholarly_query,
            "num": num_results
        }
        headers = {
            'X-API-KEY': config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Process and format the results
        formatted_results = []
        
        # Handle organic results
        for item in data.get('organic', []):
            title = item.get('title', 'No title')
            link = item.get('link', 'No link')
            snippet = item.get('snippet', 'No snippet')
            
            # Extract year and citations from the title and snippet
            year = "N/A"
            citations = "N/A"
            
            # Look for year in title and snippet
            for text in [title, snippet]:
                if not year or year == "N/A":
                    words = text.split()
                    for word in words:
                        # Clean the word from any punctuation
                        clean_word = ''.join(c for c in word if c.isdigit())
                        if clean_word.isdigit() and 1900 < int(clean_word) < 2025:
                            year = clean_word
                            break
            
            # Look for citations in snippet
            snippet_lower = snippet.lower()
            citation_patterns = ['cited by', 'citations:', 'citations -']
            for pattern in citation_patterns:
                if pattern in snippet_lower:
                    try:
                        pattern_index = snippet_lower.index(pattern)
                        # Look at the next few words for a number
                        following_text = snippet[pattern_index:pattern_index + 30].split()
                        for word in following_text:
                            clean_word = ''.join(c for c in word if c.isdigit())
                            if clean_word.isdigit():
                                citations = clean_word
                                break
                    except:
                        continue
            
            formatted_results.append(f"Title: {title}")
            formatted_results.append(f"Link: {link}")
            formatted_results.append(f"Year: {year}")
            formatted_results.append(f"Citations: {citations}")
            formatted_results.append(f"Snippet: {snippet}")
            formatted_results.append("---")
        
        if not formatted_results:
            return "No scholarly results found or error in search."
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"An error occurred while searching scholar: {str(e)}"

# Create tools with flexible input handling
def search_wrapper(query: str) -> str:
    """Wrapper to handle string input"""
    return serper_search(query)

def scholar_wrapper(**kwargs) -> str:
    """Wrapper to handle both single and multiple parameters"""
    query = kwargs.get('query')
    num_results = kwargs.get('num_results', 20)
    return serper_scholar_search(query, num_results)

serper_search_tool = Tool(
    name="Internet Search",
    func=search_wrapper,
    description="Search the internet for current information using Serper API."
)

serper_scholar_tool = Tool(
    name="Scholar Search",
    func=scholar_wrapper,
    description="Search for academic papers and scholarly content using Serper API."
)