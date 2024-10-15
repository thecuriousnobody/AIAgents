from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from langchain.tools import Tool

# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

# Initialize language model and search tool
ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)
search_tool = DuckDuckGoSearchRun()


def custom_search(query: str, config: dict = None) -> str:
    """Custom search function that wraps DuckDuckGoSearchRun and handles the config parameter."""
    return search_tool.run(query)


# Create a custom tool that uses the custom search function
custom_search_tool = Tool(
    name="Internet Search",
    func=custom_search,
    description="""
    Use this tool to search the internet for current information. 
    To use this tool, provide a search query as a simple string. Do not use JSON format or any other complex structure.

    Correct usage example: "latest developments in artificial intelligence"
    Incorrect usage example: {"query": "latest developments in artificial intelligence"}

    Always provide your search query as a simple string.
    """
)

# Define the podcast's mission
podcast_mission = """The Idea Sandbox podcast is a crucible for transformative thinking, championing the power of ideas as the true architects of 
societal progress and personal fulfillment. We challenge the notion that legislation alone can craft a better world, 
instead fostering a space where enlightened concepts can germinate, flourish, and reshape our collective values. 
By engaging with visionaries who embody this philosophy, we aim to ignite critical thinking, inspire intentional living, 
and cultivate a culture where ideas are the catalysts for authentic, sustainable change."""

# Get user input for the general topic
user_topic = input("Enter a general topic or question you'd like to explore (e.g., 'Are wars necessary?'): ")

# Define agents
idea_generator = Agent(
    role='Creative Idea Generator',
    goal=f'Generate innovative and thought-provoking podcast episode ideas related to the topic: "{user_topic}"',
    backstory=f"""You are a wellspring of creativity, constantly generating unique and captivating ideas for podcast episodes. 
    Your ideas focus on the given topic: "{user_topic}", but always tie back to the core mission of The Idea Sandbox podcast. 
    You have a knack for identifying emerging trends, controversial aspects, and unexplored angles within this topic that could lead to fascinating discussions.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

idea_refiner = Agent(
    role='Idea Refiner and Connector',
    goal=f'Refine and connect generated ideas related to "{user_topic}" to the podcast\'s mission and potential guests',
    backstory=f"""You excel at taking raw ideas about "{user_topic}" and polishing them into coherent, compelling episode concepts. 
    Your strength lies in connecting seemingly disparate ideas within this topic and finding the common thread that ties them to the podcast's mission. 
    You also have a talent for identifying potential guests whose expertise aligns with these refined concepts.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

guest_suggester = Agent(
    role='Guest Researcher and Suggester',
    goal=f'Identify and suggest potential guests who are experts on "{user_topic}" and align with the podcast\'s mission',
    backstory=f"""You are an expert at identifying thought leaders, innovators, and unique voices in fields related to "{user_topic}". 
    Your suggestions for potential guests always consider their relevance to the episode topic, their ability to provide 
    fresh perspectives on "{user_topic}", and their alignment with the podcast's mission of fostering transformative ideas.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

# Define tasks
generate_ideas = Task(
    description=f"""Generate 5 innovative and thought-provoking podcast episode ideas that explore the topic: "{user_topic}"
    while aligning with the podcast's mission:
    {podcast_mission}

    Each idea should:
    1. Be original and captivating
    2. Relate to both the given topic and the podcast's themes of transformative thinking and societal progress
    3. Have potential for in-depth discussion and analysis
    4. Appeal to a wide audience while still being intellectually stimulating

    Present each idea with a compelling title and a brief description.""",
    agent=idea_generator,
    expected_output="""A list of 5 podcast episode ideas, each containing:
    1. A compelling title (5-10 words)
    2. A brief description (2-3 sentences) explaining the core concept and its relevance to both the given topic and the podcast's mission
    3. A short explanation of why this idea is innovative and thought-provoking

    Format:
    1. [Title]
       Description: [Brief explanation]
       Innovation: [Why this idea is unique and captivating]

    2. [Title]
       Description: [Brief explanation]
       Innovation: [Why this idea is unique and captivating]

    ... (and so on for all 5 ideas)"""
)

refine_ideas = Task(
    description=f"""Take the generated ideas related to "{user_topic}" and refine them into fully-fledged episode concepts. For each idea:
    1. Expand on the core concept, highlighting its relevance to both the given topic and the podcast's mission
    2. Identify 2-3 key talking points or questions to explore
    3. Suggest a unique angle or approach to make the episode stand out
    4. Explain how this episode could contribute to the broader conversation about "{user_topic}" in the context of societal progress and personal fulfillment""",
    agent=idea_refiner,
    expected_output="""A detailed refinement of each of the 5 episode ideas, including:
    1. Expanded concept (4-5 sentences) that delves deeper into the idea and its significance
    2. 2-3 key talking points or questions to explore during the episode
    3. A unique angle or approach that sets this episode apart
    4. An explanation of how this episode contributes to the broader conversation on the topic

    Format:
    1. [Original Title] - [Refined Title (if changed)]
       Expanded Concept: [Detailed explanation]
       Key Talking Points:
       - [Point 1]
       - [Point 2]
       - [Point 3 (if applicable)]
       Unique Angle: [Description of what makes this episode stand out]
       Broader Impact: [How this episode contributes to the larger conversation]

    2. [Original Title] - [Refined Title (if changed)]
       ... (same structure as above)

    ... (and so on for all 5 ideas)"""
)

suggest_guests = Task(
    description=f"""For each refined episode concept related to "{user_topic}", suggest 2-3 potential guests who would be excellent fits. For each guest:
    1. Provide their name, current position, and area of expertise related to "{user_topic}"
    2. Explain why they would be a good fit for the specific episode topic
    3. Highlight any recent work, publications, or statements that make them particularly relevant to "{user_topic}"
    4. Describe how their perspective could contribute to a transformative discussion on this topic

    Ensure a diverse range of voices and perspectives across your suggestions.""",
    agent=guest_suggester,
    expected_output="""For each of the 5 refined episode concepts, provide 2-3 suggested guests:

    Format:
    1. [Episode Title]
       Guest 1: [Name]
       - Current Position: [Title and Organization]
       - Area of Expertise: [Brief description]
       - Relevance to Topic: [Why they're a good fit for this episode]
       - Recent Work: [Relevant publication, statement, or project]
       - Potential Contribution: [How they could add value to the discussion]

       Guest 2: [Name]
       ... (same structure as Guest 1)

       Guest 3 (if applicable): [Name]
       ... (same structure as Guest 1)

    2. [Episode Title]
       ... (same structure as above for each episode)

    ... (and so on for all 5 episode concepts)

    Conclude with a brief statement on how the suggested guests represent a diverse range of perspectives on the topic."""
)

# Create the crew
idea_incubator_crew = Crew(
    agents=[idea_generator, idea_refiner, guest_suggester],
    tasks=[generate_ideas, refine_ideas, suggest_guests],
    verbose=True,
    process=Process.sequential
)

# Run the crew
results = idea_incubator_crew.kickoff()

# Print or process the results as needed
print(results)