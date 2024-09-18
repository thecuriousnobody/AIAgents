from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import search_api_tool, youtube_tool
from usefulTools.llm_repository import ClaudeSonnet
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

IDEA_SANDBOX_MISSION = """
    A Sandbox Approach To Harvesting/Distilling Great Ideas
    Welcome to the Idea Sandbox podcast, where we dive into the power of ideas and the belief that they are the foundation of all societal progress and personal fulfillment. In a world increasingly focused on legislative solutions, we explore a different path—one where the spread of enlightened ideas can shape our value system and inspire change far beyond what laws alone can achieve.

    Our mission is rooted in the conviction that while legislative efforts are necessary, they are insufficient to usher in a brighter future. We believe that true transformation comes from embracing and promoting enlightenment ideas that encourage us to think deeper, live fully, and engage with the world and each other more meaningfully.

    At the Idea Sandbox, we're not just talking about theoretical concepts but engaging with thinkers, creators, and doers who exemplify this philosophy in their lives and work. We delve into discussions that challenge the status quo, inspire personal growth, and highlight the incredible potential for human flourishing when we prioritize ideas over injunctions.

    Join us as we explore the limitless possibilities that come from thinking critically, living intentionally, and fostering a culture that values ideas as the catalysts for authentic, sustainable progress. Together, let's create a future that is not only imagined but actively built on the foundation of ideas that enlighten, empower, and connect us all.
"""

def create_agents_and_tasks(full_transcript):
    transcript_analyzer = Agent(
        role="Transcript Analyzer",
        goal="Extract the most compelling and emotionally charged segments from the podcast transcript, including accurate timestamps.",
        backstory="You are an expert in content analysis, capable of identifying key discussions and emotionally resonant moments within a conversation, while accurately tracking their timestamps.",
        verbose=True,
        allow_delegation=False,
        max_iter=100,
        llm=ClaudeSonnet
    )

    intro_script_creator = Agent(
        role="Intro Script Creator",
        goal="Arrange selected compelling segments into a 30-second to 1.5-minute intro that hooks the audience and captures the essence of the podcast, using only original conversation snippets.",
        backstory="You are a skilled editor with a talent for selecting and arranging conversation snippets to create engaging and representative intros, without adding any narration or external content.",
        verbose=True,
        allow_delegation=False,
        max_iter=100,
        llm=ClaudeSonnet
    )

    analyze_transcript_task = Task(
        description=f"""Analyze the following podcast transcript and identify the most compelling and emotionally charged segments that would make for an engaging intro:

        Transcript:
        {full_transcript}

        Idea Sandbox Mission:
        {IDEA_SANDBOX_MISSION}

        Important:
        1. Focus on segments that are emotionally resonant, thought-provoking, or capture the essence of the podcast's mission.
        2. Look for moments that would hook the audience and make them want to listen to the full podcast.
        3. Extract 5-7 short segments (about 5-15 seconds each when spoken) that could be combined into an intro.
        4. Maintain the original timestamp and speaker format for each extracted segment.
        5. If a segment is within a larger timestamped block, estimate its specific timestamp based on its position and the length of the surrounding text.

        For each selected segment, provide:
        1. The extracted transcript portion, including estimated timestamps and speaker names
        2. A brief explanation of why this segment is compelling and how it relates to the podcast's mission""",
        agent=transcript_analyzer,
        expected_output="A list of 5-7 short, compelling transcript segments with explanations for their selection and accurate timestamps."
    )

    create_intro_script_task = Task(
        description="""Using the compelling segments identified from the transcript analysis, create an engaging intro script for the podcast. Your intro script should:

        1. Be 30 seconds to 1.5 minutes long when spoken.
        2. Hook the audience's attention and capture their imagination.
        3. Highlight the most emotionally charged or thought-provoking aspects of the conversation.
        4. Provide a taste of the discussion without giving everything away.
        5. Align with the Idea Sandbox podcast mission.
        6. Consist ONLY of the selected segments from the original conversation, without any additional narration or commentary.
        7. Arrange the segments in a logical and engaging order that creates a natural flow.
        8. Maintain the original timestamps for each segment used.

        Provide the intro script in a format ready for editing, including speaker attributions and timestamps for each segment.""",
        agent=intro_script_creator,
        expected_output="A compelling 30-second to 1.5-minute intro script that hooks the audience and captures the essence of the podcast, using only original conversation snippets with accurate timestamps for each segment.",
        context=[analyze_transcript_task]
    )

    finalize_intro_script_task = Task(
        description="""Review and finalize the intro script. Your final intro script should:

        1. Consist only of segments from the original conversation, with no added narration.
        2. Maintain the hook and emotional resonance of the selected snippets.
        3. Align with the Idea Sandbox podcast mission.
        4. Be ready for editing, with clear speaker attributions and timestamps for each segment.
        5. Include a separate list of all timestamps used, to help the editor locate the original clips.

        Provide the final intro script in a format ready for editing, with an estimated total duration and a separate list of all timestamps used.""",
        agent=intro_script_creator,
        expected_output="A final intro script ready for editing, consisting only of original conversation snippets, with an estimated total duration and a list of all timestamps used.",
        context=[create_intro_script_task]
    )

    return [transcript_analyzer, intro_script_creator], [analyze_transcript_task, create_intro_script_task, finalize_intro_script_task]

def run_podcast_intro_creator(full_transcript, max_retries=3):
    agents, tasks = create_agents_and_tasks(full_transcript)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
        process=Process.sequential
    )

    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1} to run the crew")
            output = crew.kickoff()

            # Check if all tasks are completed
            incomplete_tasks = [task for task in tasks if task.output is None]
            
            if not incomplete_tasks:
                logging.info("All tasks completed successfully")
                return output
            else:
                logging.warning(f"The following tasks were not completed: {[task.description for task in incomplete_tasks]}")
                
                # Reset incomplete tasks
                for task in incomplete_tasks:
                    task.output = None
                
                if attempt < max_retries - 1:
                    logging.info("Retrying incomplete tasks...")
                    time.sleep(5)  # Wait for 5 seconds before retrying
                else:
                    logging.error("Max retries reached. Some tasks are still incomplete.")
                    return "Error: Not all tasks could be completed after maximum retries."

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            if attempt < max_retries - 1:
                logging.info("Retrying due to error...")
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                logging.error("Max retries reached. Unable to complete the process.")
                raise

    return "Error: Unable to complete all tasks after maximum retries."

if __name__ == '__main__':
    transcript_file = input("Enter the path to the full podcast transcript file: ")
    with open(transcript_file, 'r') as file:
        full_transcript = file.read()

    try:
        result = run_podcast_intro_creator(full_transcript)
        
        if result.startswith("Error:"):
            print(result)
        else:
            print("\nPodcast Intro Script:")
            print(result)

            # Write the generated content to a file
            input_filename = os.path.basename(transcript_file)
            output_filename = f"highlights_{input_filename}"
            output_path = os.path.join(os.path.dirname(transcript_file), output_filename)

            try:
                with open(output_path, "w") as file:
                    file.write(result)
                print(f"\nIntro script saved to {output_filename}")
            except IOError as e:
                print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")