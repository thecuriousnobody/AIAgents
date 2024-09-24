import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
#from dotenv import load_dotenv

# Load environment variables
#load_dotenv()

# Initialize the language model
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=config.GROQ_API_KEY,
    model_name="llama3-70b-8192"
)

def design_layout(agent, task):
    print("Starting layout design process...")
    print("Agent role:", agent.role)
    print("Agent goal:", agent.goal)
    print("Task description:", task.description)

    # Execute the task
    layout = agent.execute_task(task)

    print("\nNewspaper Layout:")
    print(layout['description'])
    print("\nSection breakdown:")
    for section, content in layout['sections'].items():
        print(f"\n{section}:")
        for item in content:
            print(f"  - {item}")

    print("\nLayout design process complete.")
    return layout

def create_layout_designer_agent():
    return Agent(
        role="Layout Designer",
        goal="Design an appealing and user-friendly layout for the AI newspaper",
        backstory="""You are an AI with a keen eye for design and user experience in digital publications. 
        Your task is to create an engaging and easy-to-navigate layout for the AI newspaper. You understand 
        the principles of digital design, readability, and user engagement.""",
        verbose=True,
        llm=llm
    )

def create_layout_design_task(written_articles):
    return Task(
        description=f"""Design a layout for the AI newspaper using the written articles. The layout should:
        1. Have a clear hierarchy of information
        2. Be visually appealing and easy to navigate
        3. Include a mix of text and visual elements (suggest placeholders for images or infographics)
        4. Have a responsive design suitable for both desktop and mobile viewing
        5. Include sections for different topics
        6. Incorporate design elements that enhance readability and engagement

        Provide a detailed description of the layout, including the placement of articles, 
        suggested visual elements, and the overall structure of the newspaper.""",
        agent=create_layout_designer_agent()
    )

if __name__ == "__main__":
    # For testing purposes
    import json
    with open("written_articles.json", "r") as f:
        written_articles = json.load(f)
    
    agent = create_layout_designer_agent()
    task = create_layout_design_task(written_articles)
    newspaper_layout = design_layout(agent, task)

    # Save the layout design to a file
    with open("newspaper_layout.json", "w") as f:
        json.dump(newspaper_layout, f, indent=2)
    print("Newspaper layout saved to 'newspaper_layout.json'")