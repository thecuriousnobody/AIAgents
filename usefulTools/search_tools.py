import os
from crewai_tools import SerperDevTool
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
# from serpapi import GoogleSearch
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set up environment variables for Serper Dev API
os.environ["SERPER_API_KEY"] = config.SERPER_API_KEY
os.environ["SERPAPI_API_KEY"] = getattr(config, 'SERPAPI_API_KEY', '')  # Fallback for existing code

import logging
import requests
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to import CrewAI SerperDevTool for enhanced functionality
try:
    from crewai_tools import SerperDevTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("CrewAI tools not available. Using basic Serper integration.")

# Try to import LangChain GoogleSerperAPIWrapper
try:
    from langchain_community.utilities import GoogleSerperAPIWrapper
    LANGCHAIN_SERPER_AVAILABLE = True
except ImportError:
    LANGCHAIN_SERPER_AVAILABLE = False
    print("LangChain GoogleSerperAPIWrapper not available.")


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

# youtube_tool = Tool(
#     name="YouTube Search",
#     func=lambda query: parse_youtube_results(youtube_search(query)),
#     description="Useful for searching YouTube for video content related to the topic. Returns parsed results including title, link, channel info, views, and publish date."
# )

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")


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

# =============================================================================
# CREWAI SERPERDEVTOOL INTEGRATION
# =============================================================================

def create_serper_dev_tool(
    n_results: int = 10,
    country: str = "us", 
    locale: str = "en",
    location: str = None
) -> SerperDevTool:
    """
    Create a SerperDevTool with custom parameters.
    
    Args:
        n_results: Number of results to return (default: 10)
        country: Country for results (default: "us")
        locale: Locale for results (default: "en")
        location: Specific location for results (optional)
    
    Returns:
        SerperDevTool: Configured search tool
    """
    tool_params = {
        "n_results": n_results,
        "country": country,
        "locale": locale
    }
    
    if location:
        tool_params["location"] = location
    
    return SerperDevTool(**tool_params)

# Create default SerperDevTool instances
serper_dev_tool = create_serper_dev_tool()

# Create specialized versions for Facebook group research
facebook_serper_tool = create_serper_dev_tool(
    n_results=15,
    country="us",
    locale="en"
)

# Create location-specific tools
us_serper_tool = create_serper_dev_tool(
    n_results=10,
    country="us",
    locale="en",
    location="United States"
)

uk_serper_tool = create_serper_dev_tool(
    n_results=10,
    country="gb",
    locale="en",
    location="United Kingdom"
)

canada_serper_tool = create_serper_dev_tool(
    n_results=10,
    country="ca",
    locale="en", 
    location="Canada"
)

australia_serper_tool = create_serper_dev_tool(
    n_results=10,
    country="au",
    locale="en",
    location="Australia"
)

# =============================================================================
# LEGACY TOOLS (kept for backward compatibility)
# =============================================================================

# Method 1: CrewAI SerperDevTool (Enhanced for Facebook Group Research)
if CREWAI_AVAILABLE:
    # General search tool for podcasting and broadcasting groups
    facebook_group_search_tool = SerperDevTool(
        n_results=10,
        country="us",
        locale="en",
        location="United States"
    )
    
    # Specialized search for international communities
    international_search_tool = SerperDevTool(
        n_results=15,
        country="",  # No country restriction for global results
        locale="en"
    )
    
    # Business-focused search tool
    business_search_tool = SerperDevTool(
        n_results=12,
        country="us",
        locale="en",
        location="New York"
    )
else:
    # Fallback to basic serper search if CrewAI tools not available
    facebook_group_search_tool = serper_search_tool
    international_search_tool = serper_search_tool
    business_search_tool = serper_search_tool

# Method 2: LangChain Integration for Custom Search
if LANGCHAIN_SERPER_AVAILABLE:
    try:
        from crewai_tools import BaseTool
    except ImportError:
        from langchain.tools import BaseTool
    from pydantic import Field
    
    class FacebookGroupSearchTool(BaseTool):
        name: str = "Facebook Group Search"
        description: str = "Specialized search for Facebook groups related to podcasting and broadcasting"
        search: GoogleSerperAPIWrapper = Field(default_factory=GoogleSerperAPIWrapper)
        
        def _run(self, query: str) -> str:
            try:
                # Enhance query for Facebook group search
                enhanced_query = f"site:facebook.com/groups {query} podcast OR broadcasting OR content creation"
                return self.search.run(enhanced_query)
            except Exception as e:
                return f"Error performing Facebook group search: {str(e)}"
    
    class PodcastCommunitySearchTool(BaseTool):
        name: str = "Podcast Community Search"
        description: str = "Search for podcast and broadcasting communities across platforms"
        search: GoogleSerperAPIWrapper = Field(default_factory=GoogleSerperAPIWrapper)
        
        def _run(self, query: str) -> str:
            try:
                # Search across multiple platforms
                enhanced_query = f"{query} (site:facebook.com OR site:reddit.com OR site:discord.com) podcast community"
                return self.search.run(enhanced_query)
            except Exception as e:
                return f"Error performing community search: {str(e)}"

    # Create instances of custom tools
    facebook_group_finder = FacebookGroupSearchTool()
    podcast_community_finder = PodcastCommunitySearchTool()
else:
    # Fallback implementations
    facebook_group_finder = serper_search_tool
    podcast_community_finder = serper_search_tool

# Enhanced Serper search specifically for Facebook groups
def facebook_group_search(query: str, num_results: int = 15, country: str = "us") -> str:
    """
    Enhanced search function specifically designed for finding Facebook groups
    related to podcasting and broadcasting.
    """
    try:
        url = "https://google.serper.dev/search"
        
        # Enhance the query for Facebook group discovery
        enhanced_query = f"site:facebook.com/groups {query} podcast OR broadcasting OR content OR media"
        
        payload = {
            "q": enhanced_query,
            "num": num_results,
            "gl": country,  # Geographic location
            "hl": "en"      # Language
        }
        headers = {
            'X-API-KEY': config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Process and format the results specifically for Facebook groups
        formatted_results = []
        
        for item in data.get('organic', []):
            title = item.get('title', 'No title')
            link = item.get('link', 'No link')
            snippet = item.get('snippet', 'No snippet')
            
            # Extract potential member count from snippet
            member_count = "Unknown"
            snippet_lower = snippet.lower()
            
            # Look for member indicators
            member_patterns = ['members', 'member', 'people']
            for pattern in member_patterns:
                if pattern in snippet_lower:
                    words = snippet.split()
                    for i, word in enumerate(words):
                        if pattern in word.lower() and i > 0:
                            # Look for number before the pattern
                            prev_word = words[i-1].replace(',', '').replace('.', '')
                            if prev_word.replace('k', '').replace('K', '').isdigit():
                                member_count = prev_word
                                break
            
            # Determine if it's likely an active group
            activity_indicators = ['active', 'daily', 'weekly', 'recent', 'new posts', 'discussion']
            activity_level = "Unknown"
            for indicator in activity_indicators:
                if indicator in snippet_lower:
                    activity_level = "Active"
                    break
            
            formatted_results.append(f"Group Name: {title}")
            formatted_results.append(f"Link: {link}")
            formatted_results.append(f"Members: {member_count}")
            formatted_results.append(f"Activity Level: {activity_level}")
            formatted_results.append(f"Description: {snippet}")
            formatted_results.append("---")
        
        if not formatted_results:
            return "No Facebook groups found for the given query."
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"An error occurred while searching for Facebook groups: {str(e)}"

# Create a wrapper for the Facebook group search
def facebook_group_wrapper(query: str) -> str:
    """Wrapper for Facebook group search"""
    return facebook_group_search(query)

# Export the main search tool (this will be used in facebookGroupFinder.py)
search_tool = facebook_group_search_tool if CREWAI_AVAILABLE else serper_search_tool

# Additional tools for specialized searches
youtube_tool = serper_search_tool  # Placeholder for YouTube search
search_api_tool = serper_search_tool  # Placeholder for search API