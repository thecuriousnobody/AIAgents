import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import json
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
# Initialize the language model
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=config.GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

def fetch_news(news_agent, news_task):
    print("Starting news fetching process...")
    print("Agent role:", news_agent.role)
    print("Agent goal:", news_agent.goal)
    print("Task description:", news_task.description)

    # Execute the task
    fetched_news = news_agent.execute_task(news_task)

    print("\nFetched news articles:")
    if isinstance(fetched_news, dict):
        for topic, articles in fetched_news.items():
            print(f"\nTopic: {topic}")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article.get('title', 'No title')}")
                print(f"     Source: {article.get('source', 'No source')}")
                print(f"     URL: {article.get('url', 'No URL')}")
    elif isinstance(fetched_news, str):
        print(fetched_news)
    else:
        print("Unexpected data type for fetched news.")

    print("\nNews fetching process complete.")
    return fetched_news

def create_news_fetcher_agent():
    return Agent(
        role="News Fetcher",
        goal="Fetch relevant and reliable news articles for the selected topics",
        backstory="""You are an AI specialized in finding the most relevant and reliable news sources. 
        Your task is to gather high-quality news articles from reputable sources for each of the selected topics. 
        You have access to a wide range of news APIs and databases, and you're skilled at evaluating the credibility 
        and relevance of news sources.""",
        verbose=True,
        llm=llm
    )

def create_news_fetching_task(topics):
    return Task(
        description=f"""Fetch 3-5 relevant news articles for each of the following topics: {', '.join(topics)}. 
        For each article, provide:
        1. Article title
        2. Source name
        3. URL
        4. A brief summary (2-3 sentences)
        5. Justification for its selection (relevance, credibility of source, etc.)

        Ensure a diversity of perspectives and sources for each topic.""",
        expected_output="A list of news articles for each selected topic, including titles, summaries, and source URLs.",
        agent=create_news_fetcher_agent()
    )

def select_topics(agent, task):
    print("Starting topic selection process...")
    print("Agent role:", agent.role)
    print("Agent goal:", agent.goal)
    print("Task description:", task.description)

    # Execute the task
    selected_topics = agent.execute_task(task)

    print("\nSelected topics:")
    for topic in selected_topics.split('\n'):
        if topic.strip():
            print(f"- {topic.strip()}")

    print("\nTopic selection process complete.")
    return selected_topics.split('\n')

def create_topic_selector_agent():
    return Agent(
        role="Topic Selector",
        goal="Select engaging and relevant topics for the AI newspaper",
        backstory="""You are an AI with a broad knowledge of current events and trending topics. 
        Your task is to select a diverse range of engaging and relevant topics for the AI newspaper. 
        You understand what makes a story newsworthy and can identify topics that will interest readers.""",
        verbose=True,
        llm=llm
    )

def create_topic_selection_task():
    return Task(
        description="""Select 5-7 diverse and engaging topics for today's AI newspaper. 
        Consider current events, technology trends, scientific discoveries, cultural phenomena, 
        and human interest stories. Provide each topic on a new line.""",
        expected_output="A list of 5-7 current and engaging news topics, one per line.",
        agent=create_topic_selector_agent()
    )

# Add this line at the end of the file to ensure all functions are exported
__all__ = ['select_topics', 'create_topic_selector_agent', 'create_topic_selection_task']

if __name__ == "__main__":
    # For testing purposes
    test_topics = ["Technology", "Climate Change", "Global Economics"]
    agent = create_news_fetcher_agent()
    task = create_news_fetching_task(test_topics)
    fetched_news = fetch_news(agent, task)

    # Save the fetched news to a file
    with open("fetched_news.json", "w") as f:
        json.dump(fetched_news, f, indent=2)
    print("Fetched news saved to 'fetched_news.json'")