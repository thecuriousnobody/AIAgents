import os
import sys
import logging
import time
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from usefulTools.llm_repository import ClaudeSonnet

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

def create_agents_and_tasks(full_transcript, host_sentiment):
    sentiment_analyzer = Agent(
        role="Sentiment Analyzer",
        goal="Analyze the host's post-podcast sentiment and extract key themes and emotions to guide segment selection.",
        backstory="You are an expert in emotional intelligence and content analysis, capable of distilling complex sentiments into actionable insights.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    segment_extractor = Agent(
        role="Segment Extractor",
        goal="Extract compelling segments from the podcast transcript that align with the host's sentiments, including accurate timestamps.",
        backstory="You are an expert in content analysis, capable of identifying key discussions and emotionally resonant moments that reflect the host's intended tone and sentiments.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    analyze_sentiment_task = Task(
        description=f"""Analyze the host's post-podcast sentiment summary and extract key themes, emotions, and intentions:

        Host's Sentiment:
        {host_sentiment}

        Provide:
        1. A list of 3-5 key emotional themes or tones expressed by the host
        2. Any specific moments or topics the host seemed to emphasize
        3. The overall intended tone or message the host wants to convey through the highlights""",
        agent=sentiment_analyzer,
        expected_output="A detailed analysis of the host's sentiment, including key themes, emotions, and intended message."
    )

    extract_segments_task = Task(
        description=f"""Based on the sentiment analysis, extract 5-7 segments from the podcast transcript that best reflect the host's sentiments and the podcast's mission:

        Transcript:
        {full_transcript}

        Idea Sandbox Mission:
        {IDEA_SANDBOX_MISSION}

        For each selected segment:
        1. Provide the exact transcript portion, including precise timestamps and speaker names
        2. Explain how this segment aligns with the host's expressed sentiments and the podcast's mission
        3. Aim for segments that are roughly 15-30 seconds long when spoken

        Format your output as a list of segments, each containing:
        - Timestamp
        - Speaker
        - Transcript excerpt
        - Explanation of relevance to host's sentiment and podcast mission""",
        agent=segment_extractor,
        context=[analyze_sentiment_task],
        expected_output="A list of 5-7 extracted segments from the transcript, each with timestamps, speakers, excerpts, and explanations of relevance."
    )

    return [sentiment_analyzer, segment_extractor], [analyze_sentiment_task, extract_segments_task]


def run_podcast_segment_extractor(full_transcript, host_sentiment, max_retries=3):
    agents, tasks = create_agents_and_tasks(full_transcript, host_sentiment)

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
            if all(task.output is not None for task in tasks):
                logging.info("All tasks completed successfully")
                return output
            else:
                logging.warning("Some tasks were not completed")
                if attempt < max_retries - 1:
                    logging.info("Retrying...")
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

    host_sentiment = input("Please provide your post-podcast sentiment summary: ")

    try:
        result = run_podcast_segment_extractor(full_transcript, host_sentiment)
        
        if result.startswith("Error:"):
            print(result)
        else:
            print("\nExtracted Podcast Segments:")
            print(result)

            # Write the extracted segments to a file
            input_filename = os.path.basename(transcript_file)
            output_filename = f"extracted_segments_{input_filename}"
            output_path = os.path.join(os.path.dirname(transcript_file), output_filename)

            try:
                with open(output_path, "w") as file:
                    file.write(result)
                print(f"\nExtracted segments saved to {output_filename}")
            except IOError as e:
                print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")