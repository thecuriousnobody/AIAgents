from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import serper_search_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY


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
        goal=f"Identify a diverse range of potential guests related to the analyzed topic, including those with high, medium, and low public profiles.",
        backstory="You have vast knowledge of people working across various disciplines, with a focus on both well-known experts and lesser-known but impactful individuals.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools = [serper_search_tool]
    )

    contact_researcher = Agent(
        role="Contact Information Researcher",
        goal=f"Find contact information for all identified potential guests, regardless of their public profile.",
        backstory="You are skilled at finding contact information for individuals across various sectors and levels of public visibility.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools = [serper_search_tool]
    )

    analyze_topic_task = Task(
        description=f"Analyze the following niche topic in depth: '{niche_topic}'. Identify key aspects, related fields, historical context, current relevance, and potential perspectives for discussion.",
        agent=topic_analyzer,
        expected_output="A detailed analysis of the niche topic, including key aspects, related fields, historical context, current relevance, and potential perspectives for discussion."
    )

    find_experts_task = Task(
        description=f"Based on the analysis of the niche topic '{niche_topic}', identify a diverse range of potential guests who could provide valuable insights as podcast guests. Include individuals with high, medium, and low public profiles.",
        agent=expert_finder,
        expected_output="""A comprehensive list of at least 15 potential podcast guests, including:
        1. Their names and roles/affiliations
        2. A brief description of their work or experience related to the topic
        3. Why they would be a valuable guest (their unique perspective or contribution)
        4. Their approximate level of public profile (high, medium, low)
        
        Ensure the list includes a balanced mix of high-profile experts, mid-level professionals, and lesser-known individuals doing important work in the field. Aim for at least 5 individuals in each category (high, medium, low profile).""",
        context=[analyze_topic_task]
    )

    research_contacts_task = Task(
        description=f"For all identified potential guests, regardless of their public profile, research and provide their contact information or suggest ways to reach them.",
        agent=contact_researcher,
        expected_output="""For each potential guest:
        1. Any available contact information
        2. Suggestions for reaching out if direct contact info is not available
        3. Notes on the best approach for contacting each individual (e.g., through their organization, via social media, etc.)
        4. Any relevant etiquette or cultural considerations for reaching out to these individuals""",
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

    # Write the generated content to a file
    directory = "/Users/rajeevkumar/Documents/TISB/guestLeads"
    file_name = f"potential_guests_{niche_topic.replace(' ', '_')}.txt"
    full_path = os.path.join(directory, file_name)  
    
    try:
        with open(full_path, "w") as file:
            file.write(str(result))
        print(f"\nResults saved to {file_name}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")