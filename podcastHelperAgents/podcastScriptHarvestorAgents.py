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
def create_agents_and_tasks(full_transcript, chapter_script):
    transcript_analyzer = Agent(
        role="Transcript Analyzer",
        goal="Extract relevant conversation segments from the podcast transcript based on provided topics or overall podcast mission.",
        backstory="You are an expert in content analysis, capable of identifying key discussions within a conversation and aligning them with broader themes.",
        verbose=True,
        allow_delegation=False,
         max_iter = 100,
        llm=ClaudeSonnet
    )

    creative_script_composer = Agent(
        role="Creative Script Composer",
        goal="Craft a compelling narrative structure for the podcast using only content from the transcript, highlighting key ideas that align with the Idea Sandbox mission.",
        backstory="You are a skilled storyteller with a deep understanding of the Idea Sandbox podcast's mission. Your expertise lies in identifying and organizing the most relevant and engaging parts of a conversation into a coherent narrative.",
        verbose=True,
        allow_delegation=False,
        max_iter = 100,
        llm=ClaudeSonnet
    )

    fact_checker = Agent(
        role="Fact-Checker and Data Enhancer",
        goal="Verify claims and find relevant factual information to support or contextualize the conversation.",
        backstory="You are a meticulous researcher focused on finding accurate and relevant data to enhance understanding of complex topics.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        max_iter = 100,
        tools=[search_api_tool]
    )

    script_compiler = Agent(
        role="Script Compiler",
        goal="Compile extracted conversation segments, creative narrative structure, and factual data into a cohesive script.",
        backstory="You are a skilled editor who can organize information clearly and concisely while maintaining narrative flow and engagement.",
        verbose=True,
        allow_delegation=False,
        max_iter = 100,
        llm=ClaudeSonnet
    )

    if chapter_script:
        analyze_transcript_task = Task(
            description=f"""Analyze the following podcast transcript and extract relevant segments based on these chapter topics:

            Transcript:
            {full_transcript}

            Chapter Topics:
            {chapter_script}

            Important: The transcript follows this format for each speaker's dialogue:
            [start_time - end_time] SPEAKER_NAME: dialogue content

            For example:
            [25:04.00 - 26:01.22] RAJEEV: dialogue content

            When extracting relevant portions:
            1. Maintain this timestamp and speaker format.
            2. Identify and extract the most relevant portions of the transcript for each topic.
            3. Include the start and end timestamps for each extracted segment.
            4. Ensure that the extracted segments capture the core of the discussion on each topic.
            5. Process ALL provided topics. Do not finish until every topic has been addressed.

            For each topic, provide:
            1. The topic title
            2. The extracted transcript segments, including timestamps and speaker names
            3. A brief summary of the key points discussed in these segments""",
            agent=transcript_analyzer,
            expected_output="A structured format with topics, timestamped and attributed transcript segments, and brief summaries for each script item, covering ALL provided topics."
        )
    else:
        analyze_transcript_task = Task(
            description=f"""Analyze the following podcast transcript and identify key themes and compelling narrative arcs that align with the Idea Sandbox podcast mission:

        Transcript:
        {full_transcript}

        Idea Sandbox Mission:
        {IDEA_SANDBOX_MISSION}

        Important: The transcript follows this format for each speaker's dialogue:
        [start_time - end_time] SPEAKER_NAME: dialogue content

        When analyzing the transcript:
        1. Identify 5 key themes or ideas that align with the central mission of creating a compelling video script.
        2. For each theme, extract relevant portions of the transcript, maintaining the timestamp, exact speech without summarizing and speaker format.
        3. Provide a brief summary of how each theme relates to the podcast's mission and why it's compelling.
        4. Suggest a narrative structure that weaves these themes together into an engaging story.""",
            agent=transcript_analyzer,
            expected_output="A list of 5 key themes with relevant transcript segments, summaries, and a suggested narrative structure."
        )

    if not chapter_script:
        creative_script_task = Task(
            description=f"""Based on the analysis of the podcast transcript and the Idea Sandbox mission, create a compelling script structure for the podcast episode. Your script should:

            1. Use ONLY content from the provided transcript. Do not invent or add any information not present in the original conversation.
            2. Identify 5 key themes or ideas from the transcript that align with the Idea Sandbox mission.
            3. For each theme, extract relevant portions of the transcript, maintaining the timestamp and speaker format.
            4. Create a narrative arc that engages the audience and showcases the nuances of the topic, using these extracted segments.
            5. Organize the extracted content in a logical flow that tells a compelling story while staying true to the original conversation.
            6. Highlight areas where the conversation aligns particularly well with the Idea Sandbox mission.

            Idea Sandbox Mission:
            {IDEA_SANDBOX_MISSION}

            Provide a detailed outline of the script, including:
            1. The 3-5 key themes you've identified
            2. For each theme, the relevant extracted transcript segments with timestamps
            3. A suggested order for presenting these themes and segments
            4. Brief notes on how each part relates to the Idea Sandbox mission

            Remember, your role is to organize and highlight the most relevant parts of the existing conversation, not to create new content.""",
            agent=creative_script_composer,
            expected_output="A detailed script outline with key themes, extracted transcript segments, and a suggested narrative structure, all derived directly from the original transcript.",
            context=[analyze_transcript_task]
        )

    fact_check_task = Task(
            description="""Review the extracted transcript segments and/or creative script outline. For each segment or key point:
        1. Identify claims or statements that would benefit from factual support or additional context.
        2. Use the search tool to find relevant, factual information related to these claims or the broader themes.
        3. Compile a brief list of factual points, statistics, or contextual information that enhances understanding of the topic.
        4. If any claims in the transcript appear questionable, provide accurate information to clarify or correct.
        5. Consider how this information can be integrated to support the narrative structure while maintaining engagement.

        Use the search tool to find and verify information. Provide this information in a clear, concise format that can be easily integrated into the final script.""",
        agent=fact_checker,
        expected_output="A list of factual points, relevant data, and any necessary clarifications for each key theme or segment, supported by search results.",
        context=[analyze_transcript_task, creative_script_task] if not chapter_script else [analyze_transcript_task]
    )

    compile_script_task = Task(
        description=f"""Compile the analyzed transcript segments, creative script structure (if applicable), and fact-checked information into a final, cohesive script. Your script should:

        1. Follow the provided chapter structure or the creative narrative structure developed earlier.
        2. Integrate the extracted conversation segments, maintaining the original timestamp and speaker format.
        3. Incorporate relevant factual information and context provided by the fact-checker where appropriate.
        4. Ensure the flow of information is natural and enhances the original conversation without overshadowing it.
        5. Align with the Idea Sandbox podcast mission:
        {IDEA_SANDBOX_MISSION}

        6. Highlight the nuances and complexity of the topic, avoiding oversimplification.
        7. Present a compelling narrative that engages the audience while staying true to the content of the original conversation.

        The final script should primarily showcase the original conversation, with factual enhancements and narrative structure serving to support and contextualize the discussion.""",
        agent=script_compiler,
        expected_output="A final script document with a clear narrative structure, extracted transcript segments (including timestamps), integrated factual information, and alignment with the Idea Sandbox mission.",
        context=[analyze_transcript_task, fact_check_task, creative_script_task] if not chapter_script else [analyze_transcript_task, fact_check_task]
    )

    tasks = [analyze_transcript_task, fact_check_task, compile_script_task]
    if not chapter_script:
        tasks.insert(1, creative_script_task)

    return [transcript_analyzer, creative_script_composer, fact_checker, script_compiler], tasks

def run_podcast_optimizer(full_transcript, chapter_script, max_retries=3):
    agents, tasks = create_agents_and_tasks(full_transcript, chapter_script)

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
    # transcript_file = input("Enter the path to the full podcast transcript file: ")
    transcript_file = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/consolidated_transcription_diarization_output_Kiran_extracted_audio.txt"
    with open(transcript_file, 'r') as file:
        full_transcript = file.read()

    chapter_script_file = input("Enter the path to the chapter script file (press Enter if not available): ")
    chapter_script = ""
    if chapter_script_file:
        with open(chapter_script_file, 'r') as file:
            chapter_script = file.read()

    try:
        result = run_podcast_optimizer(full_transcript, chapter_script)
        
        if result.startswith("Error:"):
            print(result)
        else:
            print("\nPodcast Optimization Results:")
            print(result)

            # Write the generated content to a file
            directory = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/"
            file_name = f"optimized_podcast_script_kiranGarimella_Sonnet3.txt"
            full_path = os.path.join(directory, file_name)  

            try:
                with open(full_path, "w") as file:
                    file.write(result)
                print(f"\nResults saved to {file_name}")
            except IOError as e:
                print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")