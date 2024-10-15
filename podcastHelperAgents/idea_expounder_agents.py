from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import search_api_tool

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

def create_agents_and_tasks(initial_idea):
    divergent_thinker = Agent(
        role="Divergent Thinker",
        goal="Generate wildly imaginative and unconventional thoughts based on the initial idea.",
        backstory="You are a creative genius known for your ability to think outside the box and come up with ideas that challenge conventional wisdom.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    abstract_connector = Agent(
        role="Abstract Connector",
        goal="Create philosophical and abstract connections between the initial idea and complex concepts.",
        backstory="You are a philosopher with a deep understanding of abstract concepts and the ability to draw unexpected connections between ideas.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    futuristic_visionary = Agent(
        role="Futuristic Visionary",
        goal="Explore how the initial idea might evolve or be applied in future scenarios and advanced technological contexts.",
        backstory="You are a futurist with a keen ability to anticipate technological trends and societal changes, always thinking decades or centuries ahead.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

    cross_disciplinary_linker = Agent(
        role="Cross-Disciplinary Linker",
        goal="Connect the initial idea to various academic and professional disciplines, finding unique applications and interpretations.",
        backstory="You are a polymath with expertise across multiple fields, known for your ability to apply concepts from one discipline to solve problems in another.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

    divergent_thinking_task = Task(
        description=f"Generate 10-20 wildly imaginative and unconventional thoughts or scenarios based on the initial idea: '{initial_idea}'. Push the boundaries of creativity and challenge conventional thinking. Aim for diversity and originality in your ideas.",
        agent=divergent_thinker,
        expected_output="A list of 10-20 highly creative and unconventional ideas or scenarios that expand on the initial concept in unexpected ways."
    )

    abstract_connection_task = Task(
        description=f"Create 10-20 philosophical or abstract connections between the initial idea '{initial_idea}' and complex concepts such as consciousness, reality, time, existence, or any other abstract notions. Strive for depth and diversity in your connections.",
        agent=abstract_connector,
        expected_output="A list of 10-20 profound and thought-provoking connections between the initial idea and various abstract philosophical concepts.",
        context=[divergent_thinking_task]
    )

    futuristic_vision_task = Task(
        description=f"""Envision 10-20 ways the initial idea '{initial_idea}' might evolve or be applied in future scenarios, considering advanced technologies and potential societal changes. Use the search tool to gather information on current trends and predictions in relevant fields. Aim for a wide range of possibilities across different time frames and technological domains.

        For each scenario:
        1. Describe the futuristic application or evolution of the idea.
        2. Provide at least one specific example or prediction.
        3. Include a direct quote or paraphrase from a relevant source, along with its URL.
        4. Briefly discuss the potential impact or implications of this scenario.""",
        agent=futuristic_visionary,
        expected_output="A list of 10-20 diverse futuristic scenarios or applications of the initial idea, taking into account potential technological advancements and societal shifts, supported by current trends and predictions, including specific examples and source citations.",
        context=[abstract_connection_task]
    )

    cross_disciplinary_task = Task(
        description=f"""Identify 10-20 unique ways the initial idea '{initial_idea}' could be interpreted or applied across different academic or professional disciplines. Use the search tool to find recent developments or research in various fields that could relate to the idea. Strive for a broad range of disciplines and novel connections.

For each interpretation or application:
1. Clearly state the discipline or field.
2. Explain how the initial idea intersects with or applies to this discipline.
3. Provide at least one specific example or recent development.
4. Include a direct quote or paraphrase from a relevant source, along with its URL.
5. Briefly discuss the potential impact or implications of this application.""",
        agent=cross_disciplinary_linker,
        expected_output="A list of 10-20 cross-disciplinary applications or interpretations of the initial idea, demonstrating its potential relevance in diverse fields, supported by recent developments or research, including specific examples and source citations.",
        context=[futuristic_vision_task]
    )

    return [divergent_thinker, abstract_connector, futuristic_visionary, cross_disciplinary_linker], [divergent_thinking_task, abstract_connection_task, futuristic_vision_task, cross_disciplinary_task]

def run_idea_expounder(initial_idea):
    agents, tasks = create_agents_and_tasks(initial_idea)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    output = crew.kickoff()
    return output

if __name__ == '__main__':
    initial_idea = input("Enter an initial idea to expound upon: ")
    result = run_idea_expounder(initial_idea)
    
    print("\nIdea Expounder Results:")
    print(result)

    # Write the generated content to files
    directory = "/Volumes/Samsung/AI/ideaExpounderOutputs"
    os.makedirs(directory, exist_ok=True)
    base_filename = f"expanded_idea_{initial_idea.replace(' ', '_')}"
    json_path = os.path.join(directory, f"{base_filename}.json")
    text_path = os.path.join(directory, f"{base_filename}.txt")
    
    try:
        # Save as JSON
        structured_result = {
            "initial_idea": initial_idea,
            "results": str(result)
        }
        with open(json_path, "w") as json_file:
            json.dump(structured_result, json_file, indent=2)
        print(f"\nJSON results saved to {json_path}")

        # Save as text
        with open(text_path, "w") as text_file:
            text_file.write(f"Initial Idea: {initial_idea}\n\n")
            text_file.write("Expanded Ideas:\n\n")
            text_file.write(str(result))
        print(f"Text results saved to {text_path}")

    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
