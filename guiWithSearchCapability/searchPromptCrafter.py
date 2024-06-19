import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config 
import anthropic
import re



def generate_cogent_prompt(query, goal, context):
    model = "claude-3-haiku-20240307"
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    system_message = """You are an AI assistant skilled at generating effective search queries.
    Your task is to create a concise search query that combines the given subject matter, goal, and context. 
    The search query should be structured as a few lines of text with relevant keywords and phrases, 
    and should not include any additional explanations or context unless you deem it necessary."""

    prompt = f"""Generate a precise search query that incorporates the given query, goal, and context.
    The query could be a few lines of text suitable for an internet search. if the query has a list of people, you will
    organize the search like a list of people, if it has a list of things, you will organize the search like a list of things.
    It needs to read like a search query that you would type into a search engine, not like a question or a sentence.
    Remember this prompt will be fed into
    another AI agent that can understand human language, so therefore it needs to be clear and could contian slang if you think it
    might improve chances of getting at an accurate result, but also 
    contain adequate information to guide the search. You also need to incorporate the query into the search query
    such that it is relevant to the goal and context, remember adding relevant keywords and phrases is key to a successful search.
    Anything ommited from the query will not be considered in the search.
     Given the Query: {query}, Goal: {goal}, Context: {context}"""

    message = client.messages.create(
        model=model,
        max_tokens=2000,
        temperature=0.7,
        system=system_message,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    response = message.content
    generated_query = [block.text for block in response]
    print(generated_query[0])
    return generated_query[0]