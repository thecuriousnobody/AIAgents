import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

# Initialize the language model
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=config.GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

def format_newspaper(formatter_agent, formatting_task):
    print("Starting newspaper formatting process...")
    print("Agent role:", formatter_agent.role)
    print("Agent goal:", formatter_agent.goal)
    print("Task description:", formatting_task.description)

    # Execute the task
    formatted_newspaper = formatter_agent.execute_task(formatting_task)

    print("\nNewspaper formatting complete.")
    print("Formatted newspaper structure:")
    print(formatted_newspaper)

    return formatted_newspaper

def create_newspaper_formatter_agent():
    return Agent(
        role="Newspaper Formatter",
        goal="Format the articles into a cohesive and well-structured digital newspaper",
        backstory="""You are an AI expert in digital publishing and newspaper layout. Your task is to take 
        the written articles and organize them into a visually appealing and easy-to-navigate digital newspaper. 
        You understand the principles of digital design, readability, and user engagement.""",
        verbose=True,
        llm=llm
    )

def create_newspaper_formatting_task(written_articles):
    return Task(
        description=f"""Format the following articles into a cohesive digital newspaper:

        {written_articles}

        Your task includes:
        1. Organizing articles into appropriate sections
        2. Creating a visually appealing layout
        3. Adding headlines, subheadings, and pull quotes
        4. Suggesting placement for images or infographics (if applicable)
        5. Ensuring a consistent style throughout the newspaper
        6. Creating a table of contents or navigation menu

        Provide a detailed description of the formatted newspaper, including the overall structure, 
        section organization, and any design elements you've incorporated.""",
        agent=create_newspaper_formatter_agent()
    )

if __name__ == "__main__":
    # For testing purposes
    import json
    with open("written_articles.json", "r") as f:
        written_articles = json.load(f)
    
    agent = create_newspaper_formatter_agent()
    task = create_newspaper_formatting_task(written_articles)
    formatted_newspaper = format_newspaper(agent, task)

    # Save the formatted newspaper to a file
    with open("formatted_newspaper.json", "w") as f:
        json.dump(formatted_newspaper, f, indent=2)
    print("Formatted newspaper saved to 'formatted_newspaper.json'")