import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
#load_dotenv()

# Initialize the language model
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=config.GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

def write_articles(agent, task):
    print("Starting article writing process...")
    print("Agent role:", agent.role)
    print("Agent goal:", agent.goal)
    print("Task description:", task.description)

    # Execute the task
    written_articles = agent.execute_task(task)

    print("\nWritten articles:")
    for topic, article in written_articles.items():
        print(f"\nTopic: {topic}")
        print(f"Title: {article['title']}")
        print(f"Word count: {len(article['content'].split())}")
        print("Summary:", article['summary'])

    print("\nArticle writing process complete.")
    return written_articles

def create_article_writer_agent():
    return Agent(
        role="Article Writer",
        goal="Write engaging and informative articles based on the fetched news",
        backstory="""You are an AI with excellent writing skills and the ability to summarize complex information. 
        Your task is to create well-structured, engaging articles that provide valuable insights to readers. 
        You have a keen sense of narrative and can adapt your writing style to suit different topics and audiences.""",
        verbose=True,
        llm=llm
    )

def create_article_writing_task(fetched_news):
    return Task(
        description=f"""Write an article for each topic based on the fetched news. For each article:
        1. Create an engaging headline
        2. Write a 500-700 word article that synthesizes information from the fetched news sources
        3. Include relevant quotes from the original sources
        4. Provide a balanced perspective on the topic
        5. End with a brief conclusion or future outlook

        Ensure that each article is well-structured, informative, and engaging for the reader.""",
        agent=create_article_writer_agent()
    )

if __name__ == "__main__":
    # For testing purposes
    import json
    with open("fetched_news.json", "r") as f:
        fetched_news = json.load(f)
    
    agent = create_article_writer_agent()
    task = create_article_writing_task(fetched_news)
    written_articles = write_articles(agent, task)

    # Save the written articles to a file
    with open("written_articles.json", "w") as f:
        json.dump(written_articles, f, indent=2)
    print("Written articles saved to 'written_articles.json'")