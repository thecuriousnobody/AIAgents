from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
# from langchain.utilities import SerpAPIWrapper
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
import os
from anthropic import Anthropic
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_anthropic import ChatAnthropic
import config
import os

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY


# Set up SerpAPI search
search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="Useful for when you need to answer questions about current events or general knowledge. You should ask targeted questions."
)

ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)

if __name__ == '__main__':
    llm = ChatOpenAI(
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )


    host_info = {
        "name": "Rajeev Kumar",
        "email": "theideasandboxpodcast@gmail.com",
        "website": "tisb.world",
        "whatsapp": "3096797200"
    }

    niche_generator = Agent(
        role="Niche Topic Generator",
        goal=f"Generate specific niche topics related to art, science, technology, social engineering, activism, unique cultures, and traditions that have the potential to make for engaging podcast conversations.",
        backstory=f"You are an AI assistant whose job is to generate specific niche topics for the podcast host to explore. These topics should be related to art, science, technology, social engineering, activism, unique cultures, and traditions. Focus on topics that are not commonly discussed but have the potential to provide interesting insights and perspectives. Consider topics that showcase individuals or groups doing innovative work or addressing important issues in these areas.",
        verbose=False,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    )

    guest_finder = Agent(
        role="Potential Guest Finder",
        goal=f"Find individuals or groups working on the generated niche topics who have a low social media presence but are doing interesting and impactful work in their respective fields.",
        backstory=f"You are an AI assistant whose job is to find potential guests for the podcast based on the generated niche topics. Look for individuals or groups who are actively working on projects, initiatives, or research related to the topics, but may not have a large social media following. Focus on finding people who are passionate about their work and have unique perspectives or experiences to share. Provide their names, affiliations, and a brief description of their work.",
        verbose=False,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    )

    generate_niche_topics = Task(
        description=f"Generate specific niche topics related to art, science, technology, social engineering, activism, unique cultures, and traditions that have the potential to make for engaging podcast conversations.",
        agent=niche_generator,
        expected_output="A list of specific niche topics related to art, science, technology, social engineering, activism, unique cultures, and traditions that are not commonly discussed but have the potential to provide interesting insights and perspectives.",

    )

    find_potential_guests = Task(
        description=f"Find individuals or groups working on the generated niche topics who have a low social media presence but are doing interesting and impactful work in their respective fields. Especially working on pursuits in 3rd world countries",
        agent=guest_finder,
        expected_output="A list of potential guests for the podcast, including their names, affiliations, and a brief description of their work related to the generated niche topics.",
    )

    crew = Crew(
        agents=[niche_generator, guest_finder],
        tasks=[generate_niche_topics, find_potential_guests],
        verbose=1,
        process=Process.sequential
    )

    output = crew.kickoff()
    print(output)

    # Write the generated content to a file
    try:
        with open("/Users/rajeevkumar/Documents/TISB Stuff/nicheTOPICSJuly3rdworld.txt", "w") as file:
            file.write(output)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")