import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from crewai import Agent, Task, Crew

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the language model
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=config.GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

def write_articles(writer_agent, writing_task):
    print("Starting article writing process...")
    print("Agent role:", writer_agent.role)
    print("Agent goal:", writer_agent.goal)
    print("Task description:", writing_task.description)

    # Create a Crew with the writer agent and task
    crew = Crew(
        agents=[writer_agent],
        tasks=[writing_task],
        verbose=True
    )

    # Execute the task
    result = crew.kickoff()
    
    # Process the result
    written_articles = process_result(result)

    print("\nWritten articles:")
    if isinstance(written_articles, dict) and 'error' not in written_articles:
        for topic, article in written_articles.items():
            print(f"\nTopic: {topic}")
            print(f"Title: {article.get('title', 'No title')}")
            print(f"Word count: {len(article.get('content', '').split())}")
            print("Summary:", article.get('summary', 'No summary'))
    else:
        print("Error processing articles:", written_articles)

    print("\nArticle writing process complete.")
    return written_articles

def process_result(result):
    if isinstance(result, dict):
        return result
    elif isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # If it's not valid JSON, treat it as a single article
            return {"single_article": {"content": result, "title": "Untitled", "summary": "No summary"}}
    else:
        return {"error": f"Unexpected result type: {type(result)}"}

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
        expected_output="A list of written articles, each containing a title, content, and metadata.",
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