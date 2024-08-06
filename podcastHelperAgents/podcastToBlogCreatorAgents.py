from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import datetime

# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

# Initialize language model
ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
    )

# Define the mission statement
mission_statement = """
A Sandbox Approach To Harvesting/Distilling Great Ideas
Welcome to the Idea Sandbox podcast, where we dive into the power of ideas and the belief that they are the foundation of all societal progress and personal fulfillment. We explore how the spread of enlightened ideas can shape our value system and inspire change far beyond what laws alone can achieve.

Our mission is rooted in the conviction that while legislative efforts are necessary, they are insufficient to usher in a brighter future. We believe that true transformation comes from embracing and promoting enlightenment ideas that encourage us to think deeper, live fully, and engage with the world and each other more meaningfully.

At the Idea Sandbox, we're not just talking about theoretical concepts but engaging with thinkers, creators, and doers who exemplify this philosophy in their lives and work. We delve into discussions that challenge the status quo, inspire personal growth, and highlight the incredible potential for human flourishing when we prioritize ideas over injunctions.

Join us as we explore the limitless possibilities that come from thinking critically, living intentionally, and fostering a culture that values ideas as the catalysts for authentic, sustainable progress. Together, let's create a future that is not only imagined but actively built on the foundation of ideas that enlighten, empower, and connect us all.
"""

# Define agents
document_reader = Agent(
    role="Document Reader",
    goal="Accurately read and process the entire podcast transcript",
    backstory="You are an expert in reading and comprehending complex documents. Your role is to carefully read the entire podcast transcript and prepare it for analysis.",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
)

content_analyzer = Agent(
    role="Content Analyzer",
    goal="Extract key ideas, insights, and important points from the podcast transcript",
    backstory=f"You are an expert in analyzing complex discussions and extracting meaningful insights. You understand the mission of the Idea Sandbox podcast: {mission_statement}",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
)

blog_composer = Agent(
    role="Blog Composer",
    goal="Craft a compelling and insightful blog post based on the podcast analysis",
    backstory=f"You are a skilled writer specializing in transforming complex ideas into engaging blog posts. You understand the mission of the Idea Sandbox podcast: {mission_statement}",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
)

def create_read_transcript_task(transcript):
    return Task(
        description=f"""Read the following podcast transcript carefully. Process and structure the content for easy analysis:

        {transcript}

        Prepare the transcript by:
        1. Clearly delineating between speakers (if applicable)
        2. Properly formatting paragraphs
        3. Marking any notable sections or topics
        4. Including timestamps (if available in the original transcript)""",
        agent=document_reader,
        expected_output="""The full transcript of the podcast, properly formatted and structured. This should include:
        1. Clear delineation between speakers (if applicable)
        2. Properly formatted paragraphs
        3. Any notable sections or topics clearly marked
        4. Timestamps (if available in the original transcript)
        The output should be the entire transcript, not a summary, ready for in-depth analysis."""
    )

def create_analyze_content_task():
    return Task(
        description="Analyze the provided podcast transcript. Extract key ideas, insights, and important points that align with the Idea Sandbox mission. Focus on new perspectives, challenges to existing notions, and noteworthy discussion points.",
        agent=content_analyzer,
        expected_output="""A comprehensive analysis of the podcast content, including:
        1. Main themes and topics discussed
        2. Key arguments or ideas presented by participants
        3. New insights or perspectives introduced
        4. Challenges to existing notions or accepted knowledge
        5. Areas of agreement or disagreement between participants
        6. Noteworthy quotes or moments that encapsulate important ideas
        7. How the discussion aligns with or expands upon the Idea Sandbox mission
        8. Any questions or topics that were left open for further exploration
        This analysis should be detailed and structured, providing a solid foundation for blog post composition."""
    )

def create_compose_blog_task():
    return Task(
        description="Using the provided analysis of the podcast content, compose a comprehensive and engaging blog post that captures the essence of the episode and aligns with the Idea Sandbox mission.",
        agent=blog_composer,
        expected_output="""A well-structured blog post that includes:
        1. An engaging title that captures the main theme or a key insight from the episode
        2. Introduction
           - Brief overview of the podcast topic and its significance
           - How the episode aligns with the Idea Sandbox mission
        3. Main body
           - Detailed exploration of the key ideas, insights, and perspectives discussed
           - Highlight of new or challenging concepts introduced
           - Integration of noteworthy quotes or moments from the podcast
        4. Analysis and reflection
           - How the ideas presented challenge or expand current thinking
           - Potential implications or applications of the discussed concepts
        5. Conclusion
           - Summary of key takeaways
           - Reflection on how these ideas contribute to the Idea Sandbox mission
        6. Call-to-action for readers (e.g., listen to the full podcast, share thoughts on the ideas presented)
        The blog post should be engaging, thought-provoking, and true to the spirit of the Idea Sandbox podcast."""
    )

def save_blog_post_to_file(blog_post, podcast_title):
    filename = f"{podcast_title.replace(' ', '_')}_blog_post.txt"
    filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.')).rstrip()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(blog_post)
    
    print(f"Blog post saved to: {file_path}")

def read_transcript_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        return None

def analyze_podcast_transcript(transcript_file_path, podcast_title):
    transcript = read_transcript_from_file(transcript_file_path)
    
    if transcript is None:
        print("Failed to read the transcript. Exiting.")
        return None
    
    read_transcript_task = create_read_transcript_task(transcript)
    analyze_content_task = create_analyze_content_task()
    compose_blog_task = create_compose_blog_task()
    
    podcast_analysis_crew = Crew(
        agents=[document_reader, content_analyzer, blog_composer],
        tasks=[read_transcript_task, analyze_content_task, compose_blog_task],
        verbose=2,
        process=Process.sequential
    )
    
    results = podcast_analysis_crew.kickoff()
    
    blog_post_content = results[-1]  # Get the result of the last task
    save_blog_post_to_file(blog_post_content, podcast_title)
    
    return blog_post_content

# Example usage
if __name__ == "__main__":
    transcript_file_path = "/Volumes/Samsung/digitalArtifacts/podcastRawFootage/transcription_Kiran.txt"
    podcast_title = "Whatsapp University"
    
    blog_post = analyze_podcast_transcript(transcript_file_path, podcast_title)
    
    if blog_post:
        print("Blog post analysis complete. Check the saved file for the full content.")
    else:
        print("Blog post generation failed.")