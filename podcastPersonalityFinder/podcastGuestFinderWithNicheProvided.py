from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")

def create_agents_and_tasks(niche_topic):
    topic_analyzer = Agent(
        role="Topic Analyzer",
        goal=f"Analyze the provided niche topic and identify key aspects, related fields, and potential perspectives for discussion.",
        backstory=f"You are an expert at breaking down complex topics and identifying various angles for in-depth discussion. Your analysis helps guide the search for suitable podcast guests.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    expert_finder = Agent(
        role="Expert Finder",
        goal=f"Identify a diverse range of potential guests related to the analyzed topic, including both high-profile individuals and those doing important work with lower public visibility.",
        backstory=f"You have a vast knowledge of people working across various disciplines, from renowned experts to lesser-known but impactful individuals. Your job is to find a mix of guests who can provide unique and valuable insights on the topic, regardless of their public profile.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    contact_researcher = Agent(
        role="Contact Information Researcher",
        goal=f"Find contact information or points of contact for the identified potential guests, regardless of their public profile.",
        backstory=f"You are skilled at finding contact information for individuals across various sectors. Your role is to provide the podcast host with ways to reach out to potential guests, whether they are high-profile experts or lesser-known individuals doing important work.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )


    analyze_topic_task = Task(
        description=f"Analyze the following niche topic in depth: '{niche_topic}'. Identify key aspects, related fields, historical context, current relevance, and potential perspectives for discussion. Consider various angles that could provide a comprehensive understanding of the topic.",
        agent=topic_analyzer,
        expected_output="A detailed analysis of the niche topic, including key aspects, related fields, historical context, current relevance, and potential perspectives for discussion."
    )

    find_experts_task = Task(
        description=f"""Based on the analysis of the niche topic '{niche_topic}', identify a diverse range of potential guests who could provide valuable insights as podcast guests. Include:

        1. High-profile experts (e.g., renowned academics, established professionals, public figures)
        2. Mid-level professionals and academics doing important work in the field
        3. Up-and-coming researchers or practitioners
        4. Individuals from NGOs, grassroots organizations, or community initiatives
        5. People with direct, personal experience related to the topic
        6. Voices that might offer unconventional or underrepresented perspectives

        Aim for a balance between different types of guests. Don't limit the number of potential guests; provide as many relevant individuals as you can find. For each potential guest, briefly explain their relevance to the topic and what unique perspective they might offer.""",
        agent=expert_finder,
        expected_output="""A comprehensive list of potential podcast guests, including:
        1. Their names and roles/affiliations
        2. A brief description of their work or experience related to the topic
        3. Why they would be a valuable guest (their unique perspective or contribution)
        4. Their approximate level of public profile (high, medium, low)
        
        The list should include a mix of high-profile experts and lesser-known individuals doing important work in the field."""
    )

    research_contacts_task = Task(
        description=f"""For the identified potential guests, research and provide their contact information or suggest ways to reach them. This may include:

        1. Professional email addresses
        2. Social media profiles (LinkedIn, Twitter, etc.)
        3. Contact information for their affiliated organizations
        4. Personal or professional websites
        5. Agents or representatives (for high-profile individuals)
        6. Suggestions for intermediaries who might facilitate an introduction

        If direct contact information is not publicly available, provide alternative suggestions for how the host might reach out or connect with the individual.""",
        agent=contact_researcher,
        expected_output="""For each potential guest:
        1. Any available contact information
        2. Suggestions for reaching out if direct contact info is not available
        3. Notes on the best approach for contacting each individual (e.g., through their organization, via social media, etc.)
        4. Any relevant etiquette or cultural considerations for reaching out to these individuals"""
    )

    return [topic_analyzer, expert_finder, contact_researcher], [analyze_topic_task, find_experts_task, research_contacts_task]

def run_guest_finder(niche_topic):
    agents, tasks = create_agents_and_tasks(niche_topic)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
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
    file_name = f"potential_guests_{niche_topic.replace(' ', '_')}.txt"
    try:
        with open(file_name, "w") as file:
            file.write(result)
        print(f"\nResults saved to {file_name}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")