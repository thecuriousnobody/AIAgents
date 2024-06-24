import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config 
import anthropic
import re


def generate_agent_details(blog_rough_cut,goal, context):
    # model = "claude-3-haiku-20240307"
    model = "claude-3-5-sonnet-20240620"
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # Step 1: Analyze and distill key points from the rough cut blog
    analysis_prompt = f"""Analyze the following rough cut blog and distill its key points, main themes, and areas that need improvement. Focus on content, structure, clarity, and overall impact.

    Rough Cut Blog:
    {blog_rough_cut}

    Provide a concise summary of the key points and areas for improvement."""

    analysis_message = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0.2,
        # system="You are an expert content analyst. Your task is to analyze the given rough cut blog and provide a concise summary of its key points and areas for improvement.",
        system="You are an expert content analyst with extensive experience in blog writing and editing. Your task is to thoroughly analyze the given rough cut blog, providing a comprehensive summary of its key points, strengths, and areas for improvement. Focus on content structure, argument flow, language use, and overall impact. Offer specific, actionable suggestions for enhancing the blog's quality and effectiveness.",
   
        messages=[
            {
                "role": "user",
                "content": analysis_prompt,
            },
        ]
    )

    blog_analysis = analysis_message.content[0].text.strip()

    # Step 2: Generate agents based on the analysis, goal, and context
    agent_generation_prompt = f"""Your primary task is to refine the provided rough cut blog into a compelling, publication-ready piece. 
    Analyze the following:
    
    1. Blog Analysis: {blog_analysis}
    2. Goal: {goal}
    3. Context: {context}

    Based on this information, determine the optimal number of expert agents needed and generate a title and description for each agent that will contribute to successfully refining the blog. 
    The agent titles should be formatted as 'Agent [number] Title: [title]' and the descriptions should be 1-2 sentences long, starting with 'This agent will be responsible for...'. 
    Each agent should have a specific role in improving the content, structure, clarity, and overall impact of the blog post, addressing the key points and areas for improvement identified in the analysis. 
    The agents will collaborate and iterate on the rough cut until it reaches a state suitable for publication."""


    agent_generation_message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
        system="""You are an AI assistant tasked with determining the optimal number of expert agents and generating their titles and descriptions to support the refinement of the provided rough cut blog. The primary goal is to transform the rough cut into a compelling, publication-ready piece.

        Please analyze the blog rough cut, considering the given goal and context, and create agents that will collaborate and iterate on the content to improve its structure, clarity, and overall impact.

        It is important that the agent titles are formatted consistently, and the descriptions provide a clear overview of each agent's specific responsibilities in the blog refinement process. Please make sure the output follows this structured format:

        Agent 1 Title: "[title]"
        This agent will be responsible for [description].

        Agent 2 Title: "[title]" 
        This agent will be responsible for [description].

        [Repeat for each agent]

        The goal is to provide a comprehensive and well-structured plan that maximizes the effectiveness of the blog refinement process, ensuring the rough cut is transformed into a polished, compelling piece suitable for publication.""",
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
        backstory_prompt = f"Given the agent title '{role}' and the description '{description}', generate a 3 to 4 line backstory for the agent that aligns with their role in refining the provided rough cut blog. The backstory should highlight the agent's expertise, skills, or experience that will contribute to improving the content, structure, clarity, and overall impact of the blog post, ultimately transforming it into a compelling, publication-ready piece."
        
        backstory_message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.0,
            system="You are an artificial intelligence assistant and your task is to generate a backstory for an AI agent that aligns with the given title and description. The generated backstory should provide context and emphasize the agent's capabilities in effectively fulfilling their role in the blog refinement process. The backstory should showcase the agent's expertise, skills, or experience that will contribute to improving the rough cut blog and transforming it into a polished, compelling piece suitable for publication.",
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

        print(f"Description: {role}")
        print(f"Backstory: {backstory}")
        print()


    return num_agents, agents, blog_analysis