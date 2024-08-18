import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def google_custom_search(query, api_key=config.GOOGLE_API_KEY, cx='16a98b7fb85c346d4', num_results=10):
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'num': min(num_results, 10)  # API allows max 10 results per query
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    results = []
    if 'items' in data:
        for item in data['items']:
            results.append({
                'title': item['title'],
                'snippet': item['snippet'],
                'link': item['link']
            })
    
    return results

# Example usage
if __name__ == "__main__":
    API_KEY = config.GOOGLE_API_KEY
    CX = '16a98b7fb85c346d4'
    
    query = "artificial intelligence"
    search_results = google_custom_search(query, API_KEY, CX)
    
    for result in search_results:
        print(f"Title: {result['title']}")
        print(f"Snippet: {result['snippet']}")
        print(f"Link: {result['link']}")
        print("---")