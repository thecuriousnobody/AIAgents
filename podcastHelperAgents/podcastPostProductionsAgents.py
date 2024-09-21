import os
import sys
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain.agents import Tool
import config
from anthropic import APIStatusError
import time
from usefulTools.search_tools import search_tool, youtube_tool, search_api_tool
from usefulTools.llm_repository import ClaudeSonnet

# Set up environment variables and API keys
os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

# Initialize tools and models
llm = ClaudeSonnet


def retry_on_overload(func, max_retries=5, initial_wait=1):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except APIStatusError as e:
                if 'overloaded_error' in str(e):
                    wait_time = initial_wait * (2 ** retries)
                    print(f"API overloaded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise
        raise Exception("Max retries reached. API still overloaded.")

    return wrapper


@retry_on_overload
def kickoff_crew(crew):
    return crew.kickoff()


# Define agents
def create_idea_distiller_agent():
    return Agent(
        role="Idea Distiller",
        goal="Distill and clarify the central theme and key points from the provided context",
        backstory="You are an expert in understanding and clarifying complex ideas, capable of extracting the essence of an argument or theme.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_data_researcher_agent():
    return Agent(
        role="Data Researcher",
        goal="Find relevant and up-to-date information and statistics related to the central theme",
        backstory="You are a skilled researcher with a talent for finding accurate and pertinent information from various online sources.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )


def create_script_creator_agent():
    return Agent(
        role="Script Creator",
        goal="Create a comprehensive script that incorporates the central theme, research data, and personal views",
        backstory="You are an experienced content creator who can weave together various elements into a cohesive and engaging script.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


# Define tasks
def distill_ideas_task(agent, context, personal_view):
    return Task(
        description=f"Analyze the following context and personal view, then distill the central theme and key points:\n\nContext: {context}\n\nPersonal View: {personal_view}\n\nProvide a clear and concise summary of the main idea and any supporting points.",
        agent=agent,
        expected_output="A distilled version of the central theme and key points, clearly articulated and organized."
    )


def research_data_task(agent, distilled_ideas):
    return Task(
        description=f"Research and gather relevant, up-to-date information and statistics related to the following theme and points:\n\n{distilled_ideas}\n\nProvide a comprehensive summary of your findings, including sources where appropriate.",
        agent=agent,
        expected_output="A detailed summary of relevant data and statistics, with sources, that either support or challenge the central theme.",
        tools=[search_api_tool],
        context=["distill_ideas_task"]
    )


def create_script_task(agent, distilled_ideas, research_data, personal_view):
    return Task(
        description=f"Create a comprehensive script using the following elements:\n\nDistilled Ideas: {distilled_ideas}\n\nResearch Data: {research_data}\n\nPersonal View: {personal_view}\n\nDevelop a script that incorporates the central theme, relevant data, and personal insights. The script should flow logically, be engaging, and suitable for narration with accompanying visuals.",
        agent=agent,
        expected_output="A complete script that weaves together the central theme, research data, and personal views into a cohesive and engaging narrative.",
        context=["distill_ideas_task", "research_data_task"]
    )


def main(context, personal_view, output_file):
    # Create agents
    idea_distiller = create_idea_distiller_agent()
    data_researcher = create_data_researcher_agent()
    script_creator = create_script_creator_agent()

    # Create tasks
    distill_task = distill_ideas_task(idea_distiller, context, personal_view)
    research_task = research_data_task(data_researcher, "{{distill_task.output}}")
    script_task = create_script_task(script_creator, "{{distill_task.output}}", "{{research_task.output}}",
                                     personal_view)

    # Create and run the crew
    content_enhancement_crew = Crew(
        agents=[idea_distiller, data_researcher, script_creator],
        tasks=[distill_task, research_task, script_task],
        verbose=2,
        process=Process.sequential
    )

    result = kickoff_crew(content_enhancement_crew)

    # Write the final script to a file
    with open(output_file, 'w') as f:
        f.write(result)

    print(f"Enhanced content script has been written to {output_file}")


if __name__ == "__main__":
    context = input("Enter the central theme or focus point of your content: ")
    personal_view = input("Enter your personal view or reason for asking about this topic: ")
    output_file = input("Enter the path for the output script file: ")

    main(context, personal_view, output_file)