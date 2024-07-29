import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import anthropic


def generate_agent_details(central_idea, goal, context):
    model = "claude-3-5-sonnet-20240620"
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Step 1: Analyze the central idea, goal, and context
    analysis_prompt = f"""Analyze the following information:

    Central Idea: {central_idea}
    Goal: {goal}
    Context: {context}

    Provide a concise summary of the key points and potential challenges or areas that need attention."""

    analysis_message = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0.2,
        system="You are an expert analyst with extensive experience in various fields. Your task is to thoroughly analyze the given central idea, goal, and context, providing a comprehensive summary of key points, potential challenges, and areas that need attention. Offer specific, actionable insights for addressing the goal effectively.",
        messages=[
            {
                "role": "user",
                "content": analysis_prompt,
            },
        ]
    )

    idea_analysis = analysis_message.content[0].text.strip()

    # Step 2: Generate agents based on the analysis, goal, and context
    agent_generation_prompt = f"""Your primary task is to determine the optimal number of expert agents needed to achieve the given goal based on the central idea and context. 
    Analyze the following:

    1. Idea Analysis: {idea_analysis}
    2. Central Idea: {central_idea}
    3. Goal: {goal}
    4. Context: {context}

    Based on this information, generate a title and description for each agent that will contribute to successfully achieving the goal. 
    The agent titles should be formatted as 'Agent [number] Title: [title]' and the descriptions should be 1-2 sentences long, starting with 'This agent will be responsible for...'. 
    Each agent should have a specific role in addressing the key points and potential challenges identified in the analysis. 
    The agents will collaborate and iterate to achieve the stated goal within the given context."""

    agent_generation_message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
        system="""You are an AI assistant tasked with determining the optimal number of expert agents and generating their titles and descriptions to support achieving the given goal based on the central idea and context. Please analyze the provided information and create agents that will collaborate and iterate to address the key points and potential challenges.

        It is important that the agent titles are formatted consistently, and the descriptions provide a clear overview of each agent's specific responsibilities. Please make sure the output follows this structured format:

        Agent 1 Title: "[title]"
        This agent will be responsible for [description].

        Agent 2 Title: "[title]" 
        This agent will be responsible for [description].

        [Repeat for each agent]

        The goal is to provide a comprehensive and well-structured plan that maximizes the effectiveness of the collaborative process in achieving the stated goal.""",
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
    for role, description in zip(agent_titles, agent_descriptions):
        backstory_prompt = f"Given the agent title '{role}' and the description '{description}', generate a 3 to 4 line backstory for the agent that aligns with their role in achieving the goal based on the central idea and context. The backstory should highlight the agent's expertise, skills, or experience that will contribute to addressing the key points and potential challenges, ultimately helping to achieve the stated goal."

        backstory_message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.0,
            system="You are an artificial intelligence assistant and your task is to generate a backstory for an AI agent that aligns with the given title and description. The generated backstory should provide context and emphasize the agent's capabilities in effectively fulfilling their role in the collaborative process. The backstory should showcase the agent's expertise, skills, or experience that will contribute to achieving the stated goal within the given context.",
            messages=[
                {
                    "role": "user",
                    "content": backstory_prompt,
                },
            ]
        )

        backstory = backstory_message.content[0].text.strip()

        agent = {
            "role": role,
            "backstory": backstory
        }
        agents.append(agent)

        print(f"Role: {role}")
        print(f"Backstory: {backstory}")
        print()

    return num_agents, agents, idea_analysis