from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from duckduckgo_search import DDGS
import time
import random
from langchain.tools import Tool


def rate_limited_duckduckgo_search(query: str, max_retries=5, base_delay=1) -> str:
    print(f"Searching for: {query}")  # Debug print
    ddgs = DDGS()
    for attempt in range(max_retries):
        try:
            results = list(ddgs.text(query, max_results=5))
            formatted_results = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['href']}\nSummary: {result['body']}"
                for result in results
            ])
            return formatted_results
        except Exception as e:
            if "429 Too Many Requests" in str(e):
                delay = (2 ** attempt) * base_delay + random.uniform(0, 1)
                print(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                raise
    raise Exception("Max retries reached. Unable to complete search.")


# Create the tool
search_tool = Tool(
    name="DuckDuckGo Search",
    func=rate_limited_duckduckgo_search,
    description="Useful for when you need to answer questions about current events. You should ask targeted questions."
)


def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    individuals = []
    for line in content.split('\n'):
        if line.strip() and not line.startswith(' '):
            individuals.append(line.strip())
    return individuals


def search_contact_info(individuals):
    results = {}
    for individual in individuals:
        name = individual.split(' - ')[0] if ' - ' in individual else individual
        query = f"email address of {individual}"
        results[name] = search_tool.run(query)
        time.sleep(2)  # Adding a delay between searches to avoid rate limiting
    return results


def extract_email(search_result):
    # This is a simple extraction method. You might need a more sophisticated approach.
    lines = search_result.split('\n')
    for line in lines:
        if '@' in line and '.' in line.split('@')[1]:
            return line.strip()
    return "No email found"


def main(file_path):
    individuals = parse_file(file_path)
    search_results = search_contact_info(individuals)

    contact_info = {}
    for name, result in search_results.items():
        email = extract_email(result)
        contact_info[name] = {"email": email, "full_search_result": result}

    with open('contact_info.json', 'w') as f:
        json.dump(contact_info, f, indent=2)

    print("Contact information has been saved to contact_info.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_txt_file>")
    else:
        file_path = sys.argv[1]
        main(file_path)