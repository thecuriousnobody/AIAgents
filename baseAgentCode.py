import os
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

import config

os.environ["GROQ_API_KEY"] =config.GROQ_API_KEY

llm = ChatOpenAI(
    openai_api_base = "https://api.groq.com/openai/v1",
    openai_api_key =  os.getenv("GROQ_API_KEY"),
    model_name = "llama3-70b-8192"
)

# model = "llama3-8b-8192"
# model="llama3-70b-8192"
email = "What is the final data? Can you send me the data soon?"

# search_tool = SerperDevTool()

classifier = Agent(
    role = "email classifier",
    goal = "accurately classify emails based on their importance. give every email one of these"
           "ratings: important, casual or spam",
    backstory = "You are an AI assistant whose only job is 3to classify emails accurately and honestly. dont be afraid to give"
                "emails a bad rating if they are not important. Your job is to help the user manage ther inbox",
    verbose = False,
    allow_delegation = False,
    llm = llm
)

responder = Agent(
    role = "email responder",
    goal = "based on the importance of the email, write a concise and simple response. If the email is rated 'important'"
           "write a formal response, if the email is 'casual' write a casual response, and if the email is rated 'spam'"
           "ignore the email. no matter what, be very concise",
    backstory = "You are AI assistant whose only job is to write short responses to emails based on their importance."
                "The importance will be provided to you by the 'classifier' agent.",
    verbose = False,
    llm = llm
)

classify_email = Task(
    description=f"Classify the following email:'{email}",
    agent = classifier,
    expected_output = "One of these three options:'important', 'casual', or 'spam'",
)

respond_to_email = Task(
    description=f"Respond to the email:'{email} based on the importance provided by the 'classifer' agent.",
    agent = responder,
    expected_output = "a very concise response to the email based on the importance provided by the 'classifier' agent",
)

crew = Crew(
    agents = [classifier,responder],
    tasks = [classify_email,respond_to_email],
    verbose = 1,
    process = Process.sequential
)


output = crew.kickoff()
print (output)