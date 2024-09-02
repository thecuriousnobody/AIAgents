import os
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from serpapi import GoogleSearch
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY
import logging

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# Set up Google search tool
search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="Useful for finding current data and information on various topics."
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