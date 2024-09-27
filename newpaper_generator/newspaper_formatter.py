import sys
import os
import json
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

def create_newspaper_formatting_task(newspaper_layout):
    return Task(
        description="Format the newspaper layout into a visually appealing HTML document.",
        expected_output="A formatted HTML document containing the complete newspaper.",
        input_data={
            "newspaper_layout": newspaper_layout
        }
    )

if __name__ == "__main__":
    # For testing purposes
    sample_newspaper_layout = {
        "sections": [
            {
                "name": "Top Stories",
                "articles": [
                    {
                        "title": "Sample Article 1",
                        "content": "This is the content of sample article 1."
                    },
                    {
                        "title": "Sample Article 2",
                        "content": "This is the content of sample article 2."
                    }
                ]
            }
        ]
    }
    
    agent = create_newspaper_formatter_agent()
    task = create_newspaper_formatting_task(sample_newspaper_layout)
    formatted_newspaper = format_newspaper(agent, task)

    # Save the formatted newspaper to a file
    with open("formatted_newspaper.json", "w") as f:
        json.dump(formatted_newspaper, f, indent=2)
    print("Formatted newspaper saved to 'formatted_newspaper.json'")