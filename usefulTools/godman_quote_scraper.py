#!/usr/bin/env python3
"""
Godman Quote Scraper Tool
=========================

A specialized web scraper for extracting quotes from official godman websites:
- Sadhguru: https://isha.sadhguru.org/en/wisdom/type/quotes
- Sri Sri: https://www.artofliving.org/in-en/wisdom/quotes/inspirational-quotes-on-life
- Heartfulness: https://heartfulness.org/us/one-beautiful-thought-archive/

This tool creates a CrewAI-compatible tool for the Godman Quote Generator.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
from crewai_tools import tool
import json
from typing import List, Dict
import re
from datetime import datetime

class GodmanQuoteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Website configurations with multiple fallback selectors
        self.site_configs = {
            "sadhguru": {
                "base_url": "https://isha.sadhguru.org",
                "quotes_url": "https://isha.sadhguru.org/en/wisdom/type/quotes",
                "name": "Sadhguru",
                "selectors": {
                    "quote_containers": [
                        ".wisdom-card", ".quote-card", ".card", "article", ".post", 
                        ".content-item", ".wisdom-item", ".entry", ".item"
                    ],
                    "quote_text": [
                        ".quote-text", ".wisdom-excerpt", ".content", ".excerpt", 
                        "p", ".text", ".description", ".summary", ".quote"
                    ],
                    "quote_link": ["a", ".read-more", ".wisdom-link", ".permalink"]
                }
            },
            "sri_sri": {
                "base_url": "https://www.artofliving.org",
                "quotes_url": "https://www.artofliving.org/in-en/wisdom/quotes/inspirational-quotes-on-life",
                "name": "Sri Sri Ravi Shankar", 
                "selectors": {
                    "quote_containers": [
                        ".quote-item", ".wisdom-card", ".card", "article", ".post",
                        ".content-item", ".quote-box", ".wisdom-item", ".entry", ".item"
                    ],
                    "quote_text": [
                        ".quote-text", ".content", ".excerpt", ".description", 
                        "p", ".text", ".quote", ".wisdom-text", ".quote-content"
                    ],
                    "quote_link": ["a", ".read-more", ".permalink"]
                }
            },
            "heartfulness": {
                "base_url": "https://heartfulness.org",
                "quotes_url": "https://heartfulness.org/us/one-beautiful-thought-archive/",
                "name": "Daaji",
                "selectors": {
                    "quote_containers": [
                        ".thought-card", ".quote-card", ".card", "article", ".post",
                        ".content-item", ".thought-item", ".entry", ".item", ".thought"
                    ],
                    "quote_text": [
                        ".thought-text", ".quote-text", ".content", ".excerpt", 
                        "p", ".text", ".description", ".quote", ".thought-content"
                    ],
                    "quote_link": ["a", ".read-more", ".permalink"]
                }
            }
        }

    def _make_request(self, url: str, max_retries: int = 3) -> requests.Response:
        """Make a web request with retries and error handling."""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(random.uniform(1, 3))
                
    def _extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Try multiple selectors to extract text content."""
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Get the first non-empty text
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 20:  # Minimum length for a quote
                        return text
        
        # Fallback: try to find any paragraph with substantial text
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30 and len(text) < 500:  # Reasonable quote length
                return text
                
        return ""

    def _clean_quote_text(self, text: str) -> str:
        """Clean and format quote text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^(Quote:|Wisdom:|Thought:)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*(- Sadhguru|- Sri Sri|- Daaji)$', '', text, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{2,}', '...', text)
        
        return text.strip()

    def scrape_sadhguru_quotes(self, max_quotes: int = 20) -> List[Dict]:
        """Scrape quotes from Sadhguru's website."""
        quotes = []
        config = self.site_configs["sadhguru"]
        
        try:
            # Get the main quotes page
            response = self._make_request(config["quotes_url"])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find quote containers with multiple fallback strategies
            quote_containers = []
            for selector in config["selectors"]["quote_containers"]:
                containers = soup.select(selector)
                if containers:
                    quote_containers = containers[:max_quotes * 2]  # Get more to filter
                    print(f"   Found {len(containers)} containers using selector: {selector}")
                    break
            
            # If no containers found, try to extract from all paragraphs
            if not quote_containers:
                print("   No containers found, trying paragraph extraction...")
                paragraphs = soup.find_all('p')
                for p in paragraphs[:max_quotes]:
                    text = p.get_text(strip=True)
                    if len(text) > 50 and len(text) < 400:  # Reasonable quote length
                        quote_text = self._clean_quote_text(text)
                        if quote_text:
                            quotes.append({
                                "text": quote_text,
                                "author": config["name"],
                                "source": "isha.sadhguru.org",
                                "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                                "category": "wisdom"
                            })
                            if len(quotes) >= max_quotes:
                                break
            else:
                # Process containers
                for container in quote_containers:
                    quote_text = self._extract_text_by_selectors(container, config["selectors"]["quote_text"])
                    
                    if quote_text:
                        quote_text = self._clean_quote_text(quote_text)
                        
                        if len(quote_text) > 30:  # Filter very short texts
                            quotes.append({
                                "text": quote_text,
                                "author": config["name"],
                                "source": "isha.sadhguru.org",
                                "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                                "category": "wisdom"
                            })
                    
                    # Be polite to the server
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    if len(quotes) >= max_quotes:
                        break
                    
        except Exception as e:
            print(f"Error scraping Sadhguru quotes: {e}")
            
        return quotes

    def scrape_sri_sri_quotes(self, max_quotes: int = 20) -> List[Dict]:
        """Scrape quotes from Sri Sri Ravi Shankar's website."""
        quotes = []
        config = self.site_configs["sri_sri"]
        
        try:
            response = self._make_request(config["quotes_url"])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find quote containers with multiple fallback strategies
            quote_containers = []
            for selector in config["selectors"]["quote_containers"]:
                containers = soup.select(selector)
                if containers:
                    quote_containers = containers[:max_quotes * 2]  # Get more to filter
                    print(f"   Found {len(containers)} containers using selector: {selector}")
                    break
            
            # If no containers found, try to extract from all paragraphs
            if not quote_containers:
                print("   No containers found, trying paragraph extraction...")
                paragraphs = soup.find_all('p')
                for p in paragraphs[:max_quotes]:
                    text = p.get_text(strip=True)
                    if len(text) > 50 and len(text) < 400:  # Reasonable quote length
                        quote_text = self._clean_quote_text(text)
                        if quote_text:
                            quotes.append({
                                "text": quote_text,
                                "author": config["name"],
                                "source": "artofliving.org",
                                "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                                "category": "wisdom"
                            })
                            if len(quotes) >= max_quotes:
                                break
            else:
                # Process containers
                for container in quote_containers:
                    quote_text = self._extract_text_by_selectors(container, config["selectors"]["quote_text"])
                    
                    if quote_text:
                        quote_text = self._clean_quote_text(quote_text)
                        
                        if len(quote_text) > 30:
                            quotes.append({
                                "text": quote_text,
                                "author": config["name"],
                                "source": "artofliving.org",
                                "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                                "category": "wisdom"
                            })
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    if len(quotes) >= max_quotes:
                        break
                    
        except Exception as e:
            print(f"Error scraping Sri Sri quotes: {e}")
            
        return quotes

    def scrape_heartfulness_quotes(self, max_quotes: int = 20) -> List[Dict]:
        """Scrape quotes from Heartfulness/Daaji's website."""
        quotes = []
        config = self.site_configs["heartfulness"]
        
        try:
            response = self._make_request(config["quotes_url"])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find quote containers with multiple fallback strategies
            quote_containers = []
            for selector in config["selectors"]["quote_containers"]:
                containers = soup.select(selector)
                if containers:
                    quote_containers = containers[:max_quotes * 2]  # Get more to filter
                    print(f"   Found {len(containers)} containers using selector: {selector}")
                    break
            
            # If no containers found, try to extract from all paragraphs
            if not quote_containers:
                print("   No containers found, trying paragraph extraction...")
                paragraphs = soup.find_all('p')
                for p in paragraphs[:max_quotes]:
                    text = p.get_text(strip=True)
                    if len(text) > 50 and len(text) < 400:  # Reasonable quote length
                        quote_text = self._clean_quote_text(text)
                        if quote_text:
                            quotes.append({
                                "text": quote_text,
                                "author": config["name"],
                                "source": "heartfulness.org",
                                "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                                "category": "wisdom"
                            })
                            if len(quotes) >= max_quotes:
                                break
            else:
                # Process containers
                for container in quote_containers:
                    quote_text = self._extract_text_by_selectors(container, config["selectors"]["quote_text"])
                    
                    if quote_text:
                        quote_text = self._clean_quote_text(quote_text)
                        
                        if len(quote_text) > 30:
                            quotes.append({
                                "text": quote_text,
                                "author": config["name"],
                                "source": "heartfulness.org",
                                "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                                "category": "wisdom"
                            })
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    if len(quotes) >= max_quotes:
                        break
                    
        except Exception as e:
            print(f"Error scraping Heartfulness quotes: {e}")
            
        return quotes

    def scrape_all_quotes(self, max_quotes_per_source: int = 20) -> List[Dict]:
        """Scrape quotes from all configured websites."""
        all_quotes = []
        
        print("🔍 Scraping Sadhguru quotes...")
        sadhguru_quotes = self.scrape_sadhguru_quotes(max_quotes_per_source)
        all_quotes.extend(sadhguru_quotes)
        print(f"   Found {len(sadhguru_quotes)} Sadhguru quotes")
        
        print("🔍 Scraping Sri Sri quotes...")
        sri_sri_quotes = self.scrape_sri_sri_quotes(max_quotes_per_source)
        all_quotes.extend(sri_sri_quotes)
        print(f"   Found {len(sri_sri_quotes)} Sri Sri quotes")
        
        print("🔍 Scraping Heartfulness quotes...")
        heartfulness_quotes = self.scrape_heartfulness_quotes(max_quotes_per_source)
        all_quotes.extend(heartfulness_quotes)
        print(f"   Found {len(heartfulness_quotes)} Heartfulness quotes")
        
        print(f"✅ Total quotes scraped: {len(all_quotes)}")
        return all_quotes

# Create CrewAI tool
@tool
def godman_quote_scraper_tool(max_quotes_per_source: int = 15) -> str:
    """
    Scrape real quotes directly from official godman websites.
    
    This tool scrapes authentic quotes from:
    - Sadhguru (isha.sadhguru.org)
    - Sri Sri Ravi Shankar (artofliving.org)
    - Daaji/Heartfulness (heartfulness.org)
    
    Args:
        max_quotes_per_source: Maximum number of quotes to scrape from each website (default: 15)
    
    Returns:
        A formatted string containing all scraped quotes organized by author
    """
    scraper = GodmanQuoteScraper()
    quotes = scraper.scrape_all_quotes(max_quotes_per_source)
    
    if not quotes:
        return "❌ No quotes were successfully scraped from the websites."
    
    # Organize quotes by author
    organized_quotes = {}
    for quote in quotes:
        author = quote["author"]
        if author not in organized_quotes:
            organized_quotes[author] = []
        organized_quotes[author].append(quote)
    
    # Format output
    output = f"🎯 SCRAPED GODMAN QUOTES - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    output += "=" * 60 + "\n\n"
    
    for author, author_quotes in organized_quotes.items():
        output += f"📿 {author.upper()} QUOTES ({len(author_quotes)} found)\n"
        output += "-" * 40 + "\n"
        
        for i, quote in enumerate(author_quotes, 1):
            output += f"{i}. \"{quote['text']}\"\n"
            output += f"   Source: {quote['source']}\n"
            output += f"   Scraped: {quote['scraped_date']}\n\n"
        
        output += "\n"
    
    return output

# Test function
if __name__ == "__main__":
    print("Testing Godman Quote Scraper...")
    result = godman_quote_scraper_tool(5)
    print(result)
