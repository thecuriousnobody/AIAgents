import json
import os
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import sys

# Ensure this path points to the directory containing your agent_generator.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_research_assistant.agent_generator import generate_agents_and_tasks

def serialize_agent(agent):
    return {
        "role": agent.role,
        "goal": agent.goal,
        "backstory": agent.backstory
    }

def serialize_task(task):
    return {
        "description": task.description,
        "expected_output": task.expected_output
    }

def save_to_file(agents, tasks, filename):
    data = {
        "agents": [serialize_agent(agent) for agent in agents],
        "tasks": [serialize_task(task) for task in tasks]
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_from_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    
    agents = [
        Agent(
            role=a['role'],
            goal=a['goal'],
            backstory=a['backstory'],
            allow_delegation=False,
            llm=llm
        ) for a in data['agents']
    ]
    
    tasks = [
        Task(
            description=t['description'],
            expected_output=t['expected_output']
        ) for t in data['tasks']
    ]
    
    # Assign agents to tasks
    for task, agent in zip(tasks, agents):
        task.agent = agent
    
    # Set up task dependencies
    for i in range(1, len(tasks)):
        tasks[i].context = [tasks[i-1]]
    
    return agents, tasks

def run_research(agents, tasks):
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    return crew.kickoff()

def main():
    research_topic = input("Enter a research topic: ")
    
    print(f"\nGenerating agents and tasks for: '{research_topic}'")
    agents, tasks = generate_agents_and_tasks(research_topic)
    
    print("\nGenerated Agents and Tasks:")
    for i, (agent, task) in enumerate(zip(agents, tasks), 1):
        print(f"\nAgent {i}:")
        print(f"Role: {agent.role}")
        print(f"Goal: {agent.goal}")
        print(f"Backstory: {agent.backstory}")
        print(f"\nTask {i}:")
        print(f"Description: {task.description}")
        print(f"Expected Output: {task.expected_output}")
    
    filename = f"{research_topic.replace(' ', '_')}_research_crew.json"
    save_to_file(agents, tasks, filename)
    print(f"\nAgents and tasks saved to {filename}")
    
    proceed = input("\nDo you want to proceed with the research? (yes/no): ").lower()
    if proceed == 'yes':
        print("\nLoading agents and tasks from file and running research...")
        loaded_agents, loaded_tasks = load_from_file(filename)
        result = run_research(loaded_agents, loaded_tasks)
        print("\nResearch Results:")
        print(result)
        
        # Save results to a file
        results_filename = f"{research_topic.replace(' ', '_')}_results.txt"
        with open(results_filename, 'w') as f:
            f.write(result)
        print(f"\nResults saved to {results_filename}")
    else:
        print("Research process cancelled.")

if __name__ == "__main__":
    main()