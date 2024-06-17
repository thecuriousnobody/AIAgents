from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import config
import os

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

class AgentManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-70b-8192"
        )
        self.agents = []
        self.goal = ""
        self.abort_flag = False
        self.final_output = []
    def set_goal(self, goal):
        self.goal = goal

    def create_agent(self, agent_name, role):
        agent = Agent(
            role=role,
            goal=self.goal,
            backstory=f"You are an AI agent named {agent_name} working on the goal: {self.goal}",
            verbose=False,
            allow_delegation=False,
            llm=self.llm,
            name=agent_name
        )
        self.agents.append(agent)

    def update_agent_role(self, agent_name, new_role):
        for agent in self.agents:
            if agent.name == agent_name:
                agent.role = new_role
                agent.backstory = f"You are an AI agent named {agent_name} working on the goal: {self.goal}"
                break

    def run_agents(self):
        tasks = []
        for agent in self.agents:
            task = Task(
                description=agent.role,
                agent=agent,
                expected_output=f"Output for {agent.role} (Goal: {self.goal})",
                goal=self.goal
            )
            tasks.append(task)

        crew = Crew(
            agents=self.agents,
            tasks=tasks,
            verbose=1,
            process=Process.sequential
        )

        self.final_output = []
        for output in crew.kickoff():
            if self.abort_flag:
                break
            self.final_output.append(output)
            yield output

    def get_final_output(self):
        return "\n".join(self.final_output)