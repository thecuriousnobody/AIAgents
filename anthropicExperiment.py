import os
from langchain.llms import Anthropic
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from datetime import datetime
from random import randint
from langchain.tools import tool
from crewai_tools import SerperDevTool

import config

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

llm = Anthropic(model="claude-v1")

ClaudeHaiku = ChatAnthropic(
    model = "claude-3-haiku-20240307"
)

topic = "Indian Godmen Culture"  # Change this variable to the desired topic

guest_pooler = Agent(
    role="Guest Pooler",
    goal=f"Find potential guests for the Idea Sandbox podcast who are doing interesting work related to {topic}.",
    backstory=f"You are an AI assistant whose job is to find potential guests for the Idea Sandbox podcast. Look for people doing interesting work in {topic}, and who would likely be willing to appear on a podcast with low subscribership and viewership.",
    verbose=False,
    allow_delegation=False,
    llm=llm
)

guest_critic = Agent(
    role="Guest Critic",
    goal=f"Critique the potential guests suggested by the Guest Pooler based on their alignment with the mission of the Idea Sandbox podcast and their expertise in {topic}.",
    backstory=f"You are an AI assistant whose job is to critique the potential guests suggested by the Guest Pooler. Ensure that the guests align with the mission of the Idea Sandbox podcast and have relevant expertise in {topic}.",
    verbose=False,
    llm=llm
)

monitor = Agent(
    role="Monitor",
    goal="Monitor the Guest Pooler and Guest Critic to ensure they stay on mission and keep track of the agreed-upon potential guests.",
    backstory="You are an AI assistant whose job is to monitor the Guest Pooler and Guest Critic agents. Make sure they stay focused on finding guests who align with the Idea Sandbox podcast's mission and have expertise in the specified topic. Keep track of the potential guests that both agents agree upon.",
    verbose=False,
    llm=llm
)

pool_guests = Task(
    description=f"Find potential guests for the Idea Sandbox podcast who are doing interesting work related to {topic}.",
    agent=guest_pooler,
    expected_output="A list of potential guests for the Idea Sandbox podcast, along with their contact information (email or social media handle).",
)

critique_guests = Task(
    description=f"Critique the potential guests suggested by the Guest Pooler based on their alignment with the mission of the Idea Sandbox podcast and their expertise in {topic}.",
    agent=guest_critic,
    expected_output=f"A list of potential guests that align with the mission of the Idea Sandbox podcast and have relevant expertise in {topic}.",
)

monitor_agents = Task(
    description="Monitor the Guest Pooler and Guest Critic to ensure they stay on mission and keep track of the agreed-upon potential guests.",
    agent=monitor,
    expected_output=f"A final list of potential guests for the Idea Sandbox podcast who have expertise in {topic}, along with their contact information.",
)

crew = Crew(
    agents=[guest_pooler, guest_critic, monitor],
    tasks=[pool_guests, critique_guests, monitor_agents],
    verbose=1,
    process=Process.sequential
)

output = crew.kickoff()
print(output)