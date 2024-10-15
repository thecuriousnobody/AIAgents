import os
import json
from crewai import Agent, Task
from usefulTools.llm_repository import ClaudeSonnet
from langchain_anthropic import ChatAnthropic
from usefulTools.search_tools import search_api_tool
import anthropic
import config

def generate_agents_and_tasks(research_topic):
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    model_name = "claude-3-5-sonnet-20240620"  # or whatever the correct model name is
    llm = ChatAnthropic(model=model_name, anthropic_api_key=config.ANTHROPIC_API_KEY)

    # Generate agents
    agent_generation_prompt = f"""Given the research topic: '{research_topic}', determine the optimal number of expert agents needed (between 3 and 5) and generate a title and description for each agent that will contribute to successfully researching this topic. 
    The agent titles should be formatted as 'Agent [number] Title: [title]' and the descriptions should be 1-2 sentences long, starting with 'This agent will be responsible for...'. 
    Each agent should have a specific role in the research process, addressing different aspects of the topic.
    Also, indicate whether each agent would benefit from having a search tool (yes/no).
    """

    agent_generation_message = client.messages.create(
        model=model_name,
        max_tokens=8192,
        temperature=0.5,
        system="You are an AI assistant tasked with determining the optimal number of expert agents and generating their titles and descriptions to support the research of the given topic.",
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
    lines = agent_generation_response.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("Agent"):
            title = line.split(":")[1].strip()
            i += 1
            if i < len(lines):
                description = lines[i].strip()
                i += 1
                if i < len(lines):
                    needs_search = "yes" in lines[i].lower()
                    agents.append({"title": title, "description": description, "needs_search": needs_search})
        i += 1

    # Generate backstories and create Agent objects
    created_agents = []
    for i, agent_info in enumerate(agents, 1):
        backstory_prompt = f"Generate a 2-3 sentence backstory for Agent {i}, a {agent_info['title']}. The backstory should align with their role in researching the topic: '{research_topic}'. Do not include a specific name, just refer to them as 'Agent {i}'."
        
        backstory_message = client.messages.create(
            model=model_name,
            max_tokens=8192,
            temperature=0.5,
            system="Generate a concise backstory for an AI research agent without using a specific name.",
            messages=[{"role": "user", "content": backstory_prompt}]
        )
        
        backstory = backstory_message.content[0].text.strip()
        
        agent = Agent(
            role=agent_info['title'],
            goal=agent_info['description'],
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[search_api_tool] if agent_info['needs_search'] else []
        )
        created_agents.append(agent)

    # Generate tasks
    tasks = []
    for i, agent in enumerate(created_agents):
        task_description = f"Based on your role as {agent.role} and your goal: {agent.goal}, perform your part of the research on the topic: '{research_topic}'. Provide a detailed analysis and findings related to your specific area of focus."
        
        task = Task(
            description=task_description,
            agent=agent,
            expected_output=f"A comprehensive report on the aspects of '{research_topic}' relevant to {agent.role}'s expertise and focus area.",
            context=[tasks[i-1]] if i > 0 else None
        )
        tasks.append(task)

    # Save generated agents and tasks to a file
    output_data = {
        "research_topic": research_topic,
        "agents": [{"role": agent.role, "goal": agent.goal, "backstory": agent.backstory} for agent in created_agents],
        "tasks": [{"description": task.description, "expected_output": task.expected_output} for task in tasks]
    }
    
    directory = "/Volumes/Samsung/AI/AI_Prototype_Outputs"
    os.makedirs(directory, exist_ok=True)
    output_file = os.path.join(directory, f"{research_topic.replace(' ', '_')}_agents_and_tasks.json")
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Agents and tasks have been saved to: {output_file}")

    return created_agents, tasks