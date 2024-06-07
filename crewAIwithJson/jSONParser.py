import json
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import config
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY


# Path to the folder containing the JSON files
folder_path = "/Users/rajeevkumar/Documents/SlumBoyzStuff/AIChatAgentsNew/venv/agents"

agents = []

llm = ChatOpenAI(
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    # Check if the file is a JSON file
    if filename.endswith(".json"):
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)

        # Load the JSON data
        with open(file_path, 'r') as f:
            agent_data = json.load(f)
        # print agent_data.
        # Get the agent's name from the JSON data
        agent_name = agent_data.get('name', filename.split('.')[0])

        # Create the agent
        agent = Agent(
            name=agent_name,
            description=agent_data.get('description', ''),
            verbose=True,
            allow_delegation=agent_data.get('allow_delegation', False),
            llm=llm
        )

        # Append the agent to the list
        agents.append(agent)

# Now you can use the agents as needed
for agent in agents:
    print(f"Agent: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Verbose: {agent.verbose}")
    print(f"Allow Delegation: {agent.allow_delegation}")
    print("---")

