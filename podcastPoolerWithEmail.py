import os
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

os.environ["GROQ_API_KEY"] = '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'

llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192"
)

topic = "mental health"  # Change this variable to the desired topic

host_info = {
    "name": "Rajeev Kumar",
    "email": "theideasandboxpodcast@gmail.com",
    "website": "tisb.world",
    "whatsapp": "3096797200"
}

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

email_drafter = Agent(
    role="Email Drafter",
    goal="Draft compelling email pitches for the shortlisted potential guests based on their backgrounds and expertise.",
    backstory=f"You are an AI assistant whose job is to draft compelling email pitches for the shortlisted potential guests. Use the information about their backgrounds and expertise to create personalized and persuasive invitations that will increase the likelihood of them agreeing to be on the Idea Sandbox podcast. Include the host's information in the email: Name: {host_info['name']}, Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}",
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

draft_emails = Task(
    description="Draft compelling email pitches for the shortlisted potential guests based on their backgrounds and expertise.",
    agent=email_drafter,
    expected_output=f"Personalized and persuasive email invitations for each shortlisted potential guest, tailored to their backgrounds and expertise. The emails should include the host's information: Name: {host_info['name']}, Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}",
)

crew = Crew(
    agents=[guest_pooler, guest_critic, monitor, email_drafter],
    tasks=[pool_guests, critique_guests, monitor_agents, draft_emails],
    verbose=1,
    process=Process.sequential
)

output = crew.kickoff()
print(output)