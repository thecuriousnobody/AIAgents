import os
import sys
import anthropic
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import search_api_tool

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

def generate_agents_and_tasks(research_topic):
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    model = "claude-3-5-sonnet-20240620"

    # Generate agents
    agent_generation_prompt = f"""Given the research topic: '{research_topic}', determine the optimal number of expert agents needed and generate a title and description for each agent that will contribute to successfully researching this topic. 
    The agent titles should be formatted as 'Agent [number] Title: [title]' and the descriptions should be 1-2 sentences long, starting with 'This agent will be responsible for...'. 
    Each agent should have a specific role in the research process, addressing different aspects of the topic.
    """

    agent_generation_message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
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
    agent_titles = []
    agent_descriptions = []
    lines = agent_generation_response.split("\n")
    for i in range(len(lines)):
        if "Agent" in lines[i] and "Title:" in lines[i]:
            title = lines[i].split(":")[1].strip()
            agent_titles.append(title)
            
            description = []
            j = i + 1
            while j < len(lines) and lines[j].strip():
                description.append(lines[j].strip())
                j += 1
            agent_descriptions.append(" ".join(description))

    # Generate agents
    agents = []
    for title, description in zip(agent_titles, agent_descriptions):
        backstory_prompt = f"Given the agent title '{title}' and the description '{description}', generate a 2-3 sentence backstory for the agent that aligns with their role in researching the topic: '{research_topic}'."
        
        backstory_message = client.messages.create(
            model=model,
            max_tokens=300,
            temperature=0.0,
            system="Generate a concise backstory for an AI research agent.",
            messages=[
                {
                    "role": "user",
                    "content": backstory_prompt,
                },
            ]
        )
        
        backstory = backstory_message.content[0].text.strip()
        
        agent = Agent(
            role=title,
            goal=description,
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            llm=ChatAnthropic(model=model),
            tools=[search_api_tool]
        )
        agents.append(agent)

    # Generate tasks
    tasks = []
    for i, agent in enumerate(agents):
        task_description = f"Based on your role as {agent.role} and your goal: {agent.goal}, perform your part of the research on the topic: '{research_topic}'. Provide a detailed analysis and findings related to your specific area of focus."
        
        task = Task(
            description=task_description,
            agent=agent,
            expected_output=f"A comprehensive report on the aspects of '{research_topic}' relevant to {agent.role}'s expertise and focus area.",
            context=[tasks[i-1]] if i > 0 else None
        )
        tasks.append(task)

    return agents, tasks

def run_research_crew(research_topic):
    agents, tasks = generate_agents_and_tasks(research_topic)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    return result

if __name__ == '__main__':
    research_topic = input("Enter the research topic: ")
    result = run_research_crew(research_topic)
    
    print("\nResearch Results:")
    print(result)

    # Write the generated content to a file
    directory = "/path/to/your/output/directory"
    file_name = f"research_results_{research_topic.replace(' ', '_')}.txt"
    full_path = os.path.join(directory, file_name)  
    
    try:
        with open(full_path, "w") as file:
            file.write(result)
        print(f"\nResults saved to {file_name}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")