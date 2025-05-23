from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import serper_search_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

def validate_email(email):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def create_podcast_discovery_agents(country, category=None):
    """Create agents for podcast host discovery."""
    
    podcast_scout = Agent(
        role="Podcast Platform Scout",
        goal=f"Systematically search and catalog podcasts in {country}, focusing on {category if category else 'all categories'}",
        backstory="You are an expert at navigating podcast platforms, identifying promising podcasts across different audience sizes and genres.",
        verbose=True,
        allow_delegation=True,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )

    contact_researcher = Agent(
        role="Podcast Contact Investigator",
        goal="Discover and validate contact information for podcast hosts, prioritizing email addresses",
        backstory="You are skilled at finding publicly available contact information while respecting privacy guidelines.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[serper_search_tool]
    )

    podcast_categorizer = Agent(
        role="Podcast Audience Segmentation Specialist",
        goal="Analyze and categorize podcasts based on audience size and relevance",
        backstory="You excel at evaluating podcast metrics and identifying podcasts with potential for growth and engagement.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    # Tasks for podcast discovery
    scout_task = Task(
        description=f"Search and compile a list of podcasts in {country}, {'focusing on ' + category if category else 'across all categories'}. Include podcast name, host name, brief description, and estimated audience size.",
        agent=podcast_scout,
        expected_output="""A comprehensive list of podcasts including:
        1. Podcast Name
        2. Host Name(s)
        3. Brief Description
        4. Estimated Audience Size Category (Small/Medium/Large)
        5. Platform Links (Spotify, Apple Podcasts)"""
    )

    categorization_task = Task(
        description="Segment and prioritize podcasts based on audience size and potential value.",
        agent=podcast_categorizer,
        expected_output="""Categorized podcast list:
        - Small Podcasts (0-1000 subscribers)
        - Medium Podcasts (1000-10,000 subscribers)
        - Large Podcasts (10,000+ subscribers)
        
        For each category, include:
        1. Podcast Name
        2. Potential for collaboration
        3. Unique value proposition""",
        context=[scout_task]
    )

    contact_research_task = Task(
        description="Research and compile contact information for podcast hosts, with a focus on email addresses.",
        agent=contact_researcher,
        expected_output="""Contact Information Compilation:
        For each podcast host:
        1. Name
        2. Verified Email Address (if available)
        3. Alternative Contact Methods
        4. Notes on Contact Approach""",
        context=[categorization_task]
    )

    return [podcast_scout, contact_researcher, podcast_categorizer], \
           [scout_task, categorization_task, contact_research_task]

def run_podcast_host_discovery(country, category=None):
    """Main function to run podcast host discovery process."""
    agents, tasks = create_podcast_discovery_agents(country, category)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    output = crew.kickoff()
    return output

def save_results(result, country, category=None):
    """Save discovery results to a file."""
    directory = os.path.join(os.path.dirname(__file__), "podcast_host_leads")
    os.makedirs(directory, exist_ok=True)
    
    filename = f"podcast_hosts_{country}{'_' + category if category else ''}.txt"
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, "w") as file:
            file.write(str(result))
        print(f"Results saved to {filepath}")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == '__main__':
    print("🎙️ Podcast Host Discovery Tool 🌍")
    country = input("Enter the country to search podcasts in: ").strip()
    category = input("(Optional) Enter a podcast category (press Enter to skip): ").strip() or None

    result = run_podcast_host_discovery(country, category)
    
    print("\n🔍 Discovery Results:")
    print(result)
    
    save_option = input("\nDo you want to save these results? (yes/no): ").lower()
    if save_option in ['yes', 'y']:
        save_results(result, country, category)
