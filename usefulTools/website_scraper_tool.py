import requests
from bs4 import BeautifulSoup
import time

def get_article_links(url):
    # Function to extract all article links from the main page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # This part will depend on the specific HTML structure of the website
    links = soup.find_all('a', class_='article-link')  # Replace with actual class or identifier
    return [link['href'] for link in links]

def scrape_article(url):
    # Function to scrape content from an individual article
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # This part will depend on the specific HTML structure of the website
    title = soup.find('h1', class_='article-title').text  # Replace with actual class or identifier
    content = soup.find('div', class_='article-content').text  # Replace with actual class or identifier
    return {'title': title, 'content': content}

def main(base_url):
    article_links = get_article_links(base_url)
    articles = []
    
    for link in article_links:
        full_url = base_url + link if not link.startswith('http') else link
        article = scrape_article(full_url)
        articles.append(article)
        time.sleep(1)  # Be polite, don't overwhelm the server
    
    return articles

if __name__ == "__main__":
    base_url = "https://www.newslaundry.com/2024/09/19/window-of-hope-yet-little-changed-in-media-accountability-in-modi-30"  # Replace with your target website
    scraped_articles = main(base_url)
    print(f"Scraped {len(scraped_articles)} articles.")
    # Here you could save the articles to a file, database, etc.