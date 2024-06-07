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
    agent_generation_prompt = f"Given the goal '{goal}' and the context '{context}', determine the number of agents needed and generate a title for each agent to optimally achieve the goal."
    agent_generation_message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
        system="You are an artificial intelligence assistant tasked with determining the number of agents and generating titles for each agent based on the given goal and context. It is crucial that the generated titles and the number of agents are optimized to maximize the chances of successfully achieving the goal.",

        messages=[
            {
                "role": "user",
                "content": agent_generation_prompt,
            },
        ]
    )
    agent_generation_response = agent_generation_message.content
    response_text = agent_generation_response[0].text
    agent_titles = [line.strip() for line in response_text.split("\n") if line.startswith("Agent") and "Title" in line]
    num_agents = len(agent_titles)
    print(f"Number of agents decided for the task: {num_agents}\n")

    # Generate the role and backstory for each agent
    agents = []
    for title in agent_titles:
        role_prompt = f"Given the agent title '{title}' and the goal '{goal}', generate a role in one sentence for the agent that maximizes the chances of achieving the goal."
        role_message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.0,
            system="You are an artificial intelligence assistant and your primary objective is to generate a role for an AI agent that is specifically tailored to the given title and goal. The generated role should be designed to maximize the chances of successfully achieving the goal.",
            messages=[
                {
                    "role": "user",
                    "content": role_prompt,
                },
            ]
        )
        role = role_message.content[0].text.strip()

        backstory_prompt = f"Given the agent title '{title}', the role '{role}', and the goal '{goal}', generate a 3 to 4 line backstory for the agent that aligns with the role and supports the achievement of the goal."
        backstory_message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.0,
            system="You are an artificial intelligence assistant and your task is to generate a backstory for an AI agent that aligns with the given title, role, and goal. The generated backstory should provide context and support the agent's ability to effectively fulfill their role and contribute to the successful achievement of the goal.",
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
        print(f"Role: {role}")
        print(f"Backstory: {backstory}")
        print()


    return num_agents, agents