import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config 
import anthropic
import re


def generate_agent_details(goal, context):
    model = "claude-3-haiku-20240307"
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Generate the number of agents and their titles
    agent_generation_prompt = f"Given the goal '{goal}' and the context '{context}', determine the optimal number of agents and generate a title and description for each agent that will contribute to successfully achieving the goal. The agent titles should be formatted as 'Agent [number] Title: [title]' and the descriptions should be 1-2 sentences long, starting with 'This agent will be responsible for...'."

    agent_generation_message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
        system="""You are an AI assistant tasked with determining the optimal number of agents and generating their titles and descriptions to support the given goal and context. It is important that the agent titles are formatted consistently, and the descriptions provide a clear overview of each agent's responsibilities. Please make sure the output follows this structured format:

        Agent 1 Title: "[title]"
        This agent will be responsible for [description].

        Agent 2 Title: "[title]" 
        This agent will be responsible for [description].

        [Repeat for each agent]

        The goal is to provide a comprehensive and well-structured plan that maximizes the chances of successfully achieving the given goal.""",
            messages=[
                {
                    "role": "user",
                    "content": agent_generation_prompt,
                },
            ]
        )
    agent_generation_response = agent_generation_message.content
    response_text = agent_generation_response[0].text
    agent_titles = []
    agent_descriptions = []

    lines = response_text.split("\n")
    for i in range(len(lines)):
        if "Agent" in lines[i] and "Title:" in lines[i]:
            title = lines[i].split(":")[1].strip()
            agent_titles.append(title)
            
            description = []
            j = i + 1
            while j < len(lines) and lines[j].strip():
                description.append(lines[j].strip())
                j += 1
            agent_descriptions.append("\n".join(description))

    num_agents = len(agent_titles)
    print(f"Number of agents decided for the task: {num_agents}\n")

    print("\nAgent Titles:")
    for title in agent_titles:
        print(title)

    print("\nAgent Descriptions:")
    for description in agent_descriptions:
        print(description)
        print()
    
    

    # Generate the role and backstory for each agent
    agents = []
    for title, role in zip(agent_titles, agent_descriptions):
        backstory_prompt = f"Given the agent title '{title}' and the description '{role}', generate a 3 to 4 line backstory for the agent that aligns with the role and supports the achievement of the goal '{goal}'."
        backstory_message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.0,
            system="You are an artificial intelligence assistant and your task is to generate a backstory for an AI agent that aligns with the given title and description. The generated backstory should provide context and support the agent's ability to effectively fulfill their role and contribute to the successful achievement of the given goal.",
            messages=[
                {
                    "role": "user",
                    "content": backstory_prompt,
                },
            ]
        )
        backstory = backstory_message.content[0].text.strip()

        agent = {
            "title": title,
            "role": role,
            "backstory": backstory
        }
        agents.append(agent)

        print(f"Agent Title: {title}")
        print(f"Description: {role}")
        print(f"Backstory: {backstory}")
        print()


    return num_agents, agents