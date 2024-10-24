import anthropic
from crewai import Agent, Crew, Task
from langchain_anthropic import ChatAnthropic
from usefulTools.search_tools import search_api_tool
import config
import time
import re

class SupervisorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.agents = []
        self.tasks = []
        self.status = "Initializing"

    def add_agent(self, agent):
        self.agents.append(agent)

    def add_task(self, task):
        self.tasks.append(task)

    def monitor_progress(self):
        # Implement logic to monitor task progress
        pass

    def handle_error(self, error):
        # Implement error handling logic
        self.status = f"Error occurred: {str(error)}"
        # Attempt to recover or retry the task
        pass

    def get_status(self):
        return self.status

    def run_research(self):
        self.status = "Research in progress"
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True
        )

        results = []
        try:
            for step in crew.kickoff():
                result = f"Step: {step}\n"
                results.append(result)
                yield result
                self.status = f"Completed step: {step}"
                time.sleep(1)  # Simulate some processing time

            final_result = "\n".join(results)
            self.status = "Research completed"
            yield f"Final Result: {final_result}\n"
        except Exception as e:
            self.handle_error(e)
            yield f"Error: {str(e)}\n"

def generate_agents(query):
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    model_name = "claude-3-5-sonnet-20240620"
    llm = ChatAnthropic(model=model_name, anthropic_api_key=config.ANTHROPIC_API_KEY)

    supervisor = SupervisorAgent(llm)

    agent_generation_prompt = f"""Given the research query: '{query}', determine the optimal number of expert agents needed (between 3 and 6) and generate a role and description for each agent that will contribute to successfully researching this query. 
    For each agent, provide the information in the following format:
    Agent [number]: [Role]
    Description: [1-2 sentence description]

    Each agent should have a specific role in the research process, addressing different aspects of the query.
    """

    agent_generation_message = client.messages.create(
        model=model_name,
        max_tokens=8192,
        temperature=0.5,
        system="You are an AI assistant tasked with determining the optimal number of expert agents and generating their roles and descriptions to support the research of the given query.",
        messages=[
            {
                "role": "user",
                "content": agent_generation_prompt,
            },
        ]
    )

    agent_generation_response = agent_generation_message.content[0].text
    
    # Parse agent details
    agents = []
    agent_pattern = re.compile(r'Agent \d+: (.+)\nDescription: (.+)')
    matches = agent_pattern.findall(agent_generation_response)
    
    for role, description in matches:
        agent = Agent(
            role=role.strip(),
            goal=description.strip(),
            backstory="An AI agent specialized in " + role.strip(),
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[search_api_tool]
        )
        supervisor.add_agent(agent)
        agents.append({
            "role": agent.role,
            "description": agent.goal,
            "useGoogleSearch": True
        })

    return supervisor, agents

def run_research(supervisor):
    for i, agent in enumerate(supervisor.agents):
        task = Task(
            description=f"Research and provide insights related to your role as {agent.role}. Focus on your specific area of expertise and how it relates to the overall research query.",
            agent=agent,
            expected_output="A comprehensive report on the aspects relevant to the agent's expertise and focus area."
        )
        supervisor.add_task(task)

    return supervisor.run_research()
