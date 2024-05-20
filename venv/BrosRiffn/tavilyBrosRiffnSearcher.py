from tavily import TavilyClient
import config
import requests
def summarize_tavily_info(tavily_response):
    # Parse the Tavily AI response and extract the relevant information
    summary_points = []
    for result in tavily_response['results']:
        summary_points.append(result['title'])
        summary_points.append(result['content'])

    # Create a summarized version of the information
    summary = "\n".join(summary_points)
    return summary

def process_search_results(query):
    tavily = TavilyClient(api_key=config.TAVILY_API_KEY)
    query = query[:399] if len(query) > 400 else query

    if len(query) < 5:
        print(f"Query is too short. Min query length is 5 characters. Query: {query}")
        return None

    try:
        tavily_response = tavily.search(query=query, search_depth="advanced")
        tavily_summary = summarize_tavily_info(tavily_response)
        return tavily_summary
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response Content: {e.response.content}")
        return None