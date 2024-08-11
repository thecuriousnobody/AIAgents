from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")

# Initialize SerpAPIWrapper with the API key

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")

search_wrapper = SerpAPIWrapper(
    serpapi_api_key=config.SERPAPI_API_KEY,
    params={
        "engine": "google",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "num": 10,
        "tbm": "",
        "safe": "active",
        "device": "desktop",
        "output": "json",
        "no_cache": False
    }
)

# Create a custom tool using the SerpAPIWrapper
search_tool = Tool(
    name="Search",
    func=search_wrapper.run,
    description="Useful for searching the internet to find information on people, topics, or current events."
)

def create_agents_and_tasks(niche_topic):
    topic_analyzer = Agent(
        role="Topic Analyzer",
        goal=f"Analyze the provided niche topic and identify key aspects, related fields, and potential perspectives for discussion.",
        backstory="You are an expert at breaking down complex topics and identifying various angles for in-depth discussion.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    expert_finder = Agent(
        role="Expert Finder",
        goal=f"Identify a diverse range of potential guests related to the analyzed topic.",
        backstory="You have vast knowledge of people working across various disciplines, with a focus on both well-known experts and lesser-known but impactful individuals.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    )

    contact_researcher = Agent(
        role="Contact Information Researcher",
        goal=f"Find contact information for the identified potential guests.",
        backstory="You are skilled at finding contact information for individuals across various sectors.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    )

    analyze_topic_task = Task(
        description=f"Analyze the following niche topic in depth: '{niche_topic}'. Identify key aspects, related fields, historical context, current relevance, and potential perspectives for discussion.",
        agent=topic_analyzer,
        expected_output="A detailed analysis of the niche topic, including key aspects, related fields, historical context, current relevance, and potential perspectives for discussion."
    )

    find_experts_task = Task(
        description=f"Based on the analysis of the niche topic '{niche_topic}', identify a diverse range of potential guests who could provide valuable insights as podcast guests.",
        agent=expert_finder,
        expected_output="A list of potential podcast guests, including their names, roles/affiliations, relevance to the topic, and unique perspectives they could offer.",
        context=[analyze_topic_task]
    )

    research_contacts_task = Task(
        description=f"For the identified potential guests, research and provide their contact information or suggest ways to reach them.",
        agent=contact_researcher,
        expected_output="Contact information or suggested methods of reaching out for each identified potential guest, including professional email addresses, social media profiles, or affiliated organization contacts.",
        context=[find_experts_task]
    )

    return [topic_analyzer, expert_finder, contact_researcher], [analyze_topic_task, find_experts_task, research_contacts_task]

def run_guest_finder(niche_topic):
    agents, tasks = create_agents_and_tasks(niche_topic)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    output = crew.kickoff()
    return output

if __name__ == '__main__':
    niche_topic = input("Enter the niche topic for the podcast: ")
    result = run_guest_finder(niche_topic)
    
    print("\nGuest Finder Results:")
    print(result)

    # Define the folder path
    folder_path = "/Users/rajeevkumar/Documents/TISB/pitchEmails"
    
    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Define the file name with the full path
    file_name = os.path.join(folder_path, f"potential_guests_{niche_topic.replace(' ', '_')}.txt")

    # Write the generated content to the file
    try:
        with open(file_name, "w") as file:
            file.write(result)
        print(f"\nResults saved to {file_name}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")