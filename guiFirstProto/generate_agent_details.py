import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config 
import anthropic
import re


def generate_agent_details(agent_title):
    model = "claude-3-haiku-20240307"

    # prompt = f"Given the agent title '{agent_title}', generate a 3 to 4 line backstory and a short role description for the agent. Please format your response as follows:\n\nBackstory:\n[Backstory here]\n\nRole: [Role here]"
    # prompt = f"Given the agent title '{agent_title}', generate a 3 to 4 line backstory and a short role description for the agent. Please format your response as follows:\n\n<backstory>\n[Backstory here]\n</backstory>\n\n<role>[Role here]</role>"
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    prompt = f"Given the agent title '{agent_title}', generate a role in one sentence for the agent."

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
        system="You are an artificial intelligence assistant and you need to "
               "generate a role for an AI agent based on the given title.",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    response = message.content
    role =  [block.text for block in response]
    print(role[0])

    return role[0]

