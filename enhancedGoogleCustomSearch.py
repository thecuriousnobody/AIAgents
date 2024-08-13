import requests
import os
import sys
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import config

nltk.download('punkt')
nltk.download('stopwords')

def google_custom_search(query, api_key=config.GOOGLE_API_KEY, cx='16a98b7fb85c346d4', num_results=10, aggregate=False):
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'num': min(num_results, 10)  # API allows max 10 results per query
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if not aggregate:
        results = []
        if 'items' in data:
            for item in data['items']:
                results.append({
                    'title': item['title'],
                    'snippet': item['snippet'],
                    'link': item['link']
                })
        return results
    else:
        return aggregate_results(data)

def aggregate_results(data):
    all_text = ""
    for item in data.get('items', []):
        all_text += item['snippet'] + " "
        
        # Fetch and parse the webpage content
        try:
            page = requests.get(item['link'], timeout=5)
            soup = BeautifulSoup(page.content, 'html.parser')
            all_text += soup.get_text() + " "
        except:
            pass  # Skip if unable to fetch the page
    
    # Tokenize the text into sentences
    sentences = sent_tokenize(all_text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_sentences = [' '.join([word for word in sentence.split() if word.lower() not in stop_words]) for sentence in sentences]
    
    # Calculate word frequency
    words = ' '.join(filtered_sentences).split()
    freq_dist = FreqDist(words)
    
    # Select top sentences based on word frequency
    sentence_scores = {}
    for i, sentence in enumerate(filtered_sentences):
        for word in sentence.split():
            if word in freq_dist:
                if i not in sentence_scores:
                    sentence_scores[i] = 0
                sentence_scores[i] += freq_dist[word]
    
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:5]
    
    # Construct the summary
    summary = ' '.join([sentences[i] for i in sorted(top_sentences)])
    
    return summary

# Example usage
if __name__ == "__main__":
    API_KEY = config.GOOGLE_API_KEY
    CX = '16a98b7fb85c346d4'
    
    query = "OLA Electric Scooter"
    search_results = google_custom_search(query, API_KEY, CX, aggregate=True)
    
    print("Aggregated Summary:")
    print(search_results)