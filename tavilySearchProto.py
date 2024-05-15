from tavily import TavilyClient
from podcastShortlisterAgent import topic


def summarize_tavily_info(tavily_response):
    # Parse the Tavily AI response and extract the relevant information
    summary_points = []
    for result in tavily_response['results']:
        summary_points.append(result['title'])
        summary_points.append(result['content'])

    # Create a summarized version of the information
    summary = "\n".join(summary_points)
    return summary


def process_guest(guest):
    guest_name = guest['name']
    print(guest_name)
    guest_description = guest['description']
    print(guest_description)
    tavily = TavilyClient(api_key="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")
    query = f"{guest_name}, {guest_description}"
    query = query[:399] if len(query) > 400 else query
    tavily_response = tavily.search(query=query, search_depth="advanced")

    tavily_summary = summarize_tavily_info(tavily_response)
    return tavily_summary