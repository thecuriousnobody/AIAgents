from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
from usefulTools.llm_repository import ClaudeOpus,ClaudeSonnet
from usefulTools.search_tools import search_tool
from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
llm = ClaudeSonnet

def create_podcast_prep_crew(guest_name):
    # Define the agents
    research_agent = Agent(
        role="Internet Research Specialist",
        goal=f"Gather comprehensive information about {guest_name} from various online sources",
        backstory=f"You are an expert in online research with a keen eye for detail. Your specialty is finding and collating information about {guest_name} from diverse sources including social media, news articles, academic publications, and interviews.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )

    distillation_agent = Agent(
        role="Information Synthesizer",
        goal="Distill and organize the gathered information into clear, concise, and relevant points",
        backstory="You are a master of synthesis, capable of taking large amounts of information and extracting the most important and interesting aspects. You have a talent for organizing information in a way that tells a compelling story.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    question_formulation_agent = Agent(
        role="Creative Question Formulator",
        goal="Create thought-provoking and engaging questions based on the distilled information",
        backstory="You are an expert interviewer with a deep understanding of The Idea Sandbox podcast's ethos. You craft questions that not only explore the guest's expertise but also challenge them to think in new ways and relate their work to broader societal issues.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Define the tasks
    research_task = Task(
        description=f"Research {guest_name}. Find information about their career background, publications, interviews, social media presence, and any other relevant online information.",
        agent=research_agent,
        expected_output="A comprehensive summary of the research findings on the guest's background, work, and recent activities."
    )

    distillation_task = Task(
        description=f"Take the research findings and distill them into key points about {guest_name}'s work, expertise, and notable ideas or projects.",
        agent=distillation_agent,
        expected_output="A list of concise, bullet-point style salient points that capture the essence of the guest's work and ideas."
    )

    question_formulation_task = Task(
        description=f"Based on the distilled information, create a set of 10-15 thought-provoking questions for {guest_name} that align with The Idea Sandbox podcast's focus on transformative ideas and their practical applications.",
        agent=question_formulation_agent,
        expected_output="A list of 10-15 well-crafted interview questions, incorporating insights from the research and distillation phases."
    )

    # Create and return the crew
    return Crew(
        agents=[research_agent, distillation_agent, question_formulation_agent],
        tasks=[research_task, distillation_task, question_formulation_task],
        verbose=2,
        process=Process.sequential
    )

# Usage
guest_name = "Marina Debris"
crew = create_podcast_prep_crew(guest_name)
result = crew.kickoff()

print(result)