from tavily import TavilyClient
from searchPromptCrafter import generate_cogent_prompt
import config


def summarize_tavily_info(tavily_response):
    # Parse the Tavily AI response and extract the relevant information
    summary_points = []
    for result in tavily_response['results']:
        summary_points.append(result['title'])
        summary_points.append(result['content'])

    # Create a summarized version of the information
    summary = "\n".join(summary_points)
    return summary



def process_search_results(query, goal, context):
    # Refine the user's query
    refined_query = generate_cogent_prompt(query, goal, context)

    # Perform the search using the refined query
    tavily = TavilyClient(config.TAVILY_API_KEY)
    tavily_response = tavily.search(query=refined_query, search_depth="advanced")

    # Parse and process the search results
    search_results = summarize_tavily_info(tavily_response)

    return search_results 