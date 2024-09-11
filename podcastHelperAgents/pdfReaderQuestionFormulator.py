import os
from crewai import Agent, Task, Crew, Process
import PyPDF2
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain.utilities import SerpAPIWrapper
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from anthropic import APIStatusError
import time
from usefulTools.search_tools import search_tool, youtube_tool,search_api_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY



def retry_on_overload(func, max_retries=5, initial_wait=1):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except APIStatusError as e:
                if 'overloaded_error' in str(e):
                    wait_time = initial_wait * (2 ** retries)
                    print(f"API overloaded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise
        raise Exception("Max retries reached. API still overloaded.")
    return wrapper

def chunk_pdf(file_path, chunk_size=18):
    chunks = []
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        for i in range(0, total_pages, chunk_size):
            chunk_text = ""
            for j in range(i, min(i + chunk_size, total_pages)):
                chunk_text += pdf_reader.pages[j].extract_text()
            chunks.append(chunk_text)
    return chunks

@retry_on_overload
def kickoff_crew(crew):
    return crew.kickoff()

def create_reader_agent():
    return Agent(
        role="Research Paper Analyzer",
        goal="Accurately extract key information from research papers",
        backstory="You are an expert in analyzing academic papers, capable of identifying crucial elements such as methodologies, findings, and recommendations.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

def create_summarizer_agent():
    return Agent(
        role="Research Summarizer",
        goal="Distill complex research information into clear, concise salient points",
        backstory="You are a master of synthesizing academic research, capable of extracting and presenting the most important aspects of studies in a clear, concise manner.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

def create_podcast_question_generator():
    return Agent(
        role="Podcast Question Generator",
        goal="Generate thought-provoking questions and discussion points for the Idea Sandbox podcast",
        backstory="You are an expert at crafting engaging questions that spark critical thinking and curiosity. Your questions aim to explore ideas that can lead to societal progress and personal fulfillment, with a focus on scalability to vast populations.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

def read_document_task(reader_agent, file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    return Task(
        description=f"""Analyze the following research paper and extract key information including the title, methodology, main findings, and recommendations. If necessary, use the Internet Search tool to gather additional context or information:

        {text}""",
        agent=reader_agent,
        expected_output="A comprehensive summary of the key elements of the research paper, including title, methodology, findings, and recommendations, along with any relevant additional information from internet searches."
    )

def summarize_research_task(summarizer_agent, content):
    return Task(
        description=f"""Summarize the following research content into salient points, focusing on key findings, methodologies, and recommendations. If necessary, use the Internet Search tool to provide additional context or supporting information:

        {content}""",
        agent=summarizer_agent,
        expected_output="A list of concise, bullet-point style salient points that capture the essence of the research, preceded by the study title, and including any relevant additional information from internet searches."
    )

def generate_podcast_questions_task(question_generator, content, podcast_description, guest_name, guest_expertise):
    return Task(
        description=f"""Based on the following research summary and the Idea Sandbox podcast description, generate a list of thought-provoking questions and discussion points for the podcast interview with {guest_name}, an expert in {guest_expertise}. Focus on ideas that can be scaled to vast populations, and approach the topics from critical thinking and curiosity perspectives. Use the Internet Search tool to find additional relevant information, interesting facts, or current events that could enhance the discussion.

        Research summary:
        {content}

        Podcast description:
        {podcast_description}

        Your task is to create questions that:
        1. Explore the transformative power of ideas presented in the research
        2. Challenge the status quo and inspire personal growth
        3. Discuss how these ideas can be scaled to benefit large populations
        4. Encourage critical thinking and curiosity
        5. Align with the podcast's mission of exploring ideas beyond legislative solutions
        6. Incorporate interesting facts or current events found through internet searches
        7. Specifically relate to {guest_name}'s expertise in {guest_expertise}

        Provide a diverse range of questions without any limit on the number. Include brief explanations or context for questions that draw from additional internet research.""",
        agent=question_generator,
        expected_output=f"A list of thought-provoking questions and discussion points for the Idea Sandbox podcast interview with {guest_name}, including additional context from internet searches."
    )

def main(input_file_path, output_file_path, podcast_description, guest_name, guest_expertise):
    reader_agent = create_reader_agent()
    summarizer_agent = create_summarizer_agent()
    question_generator = create_podcast_question_generator()

    # Chunk the PDF
    chunks = chunk_pdf(input_file_path)

    all_summaries = []
    all_questions = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1} of {len(chunks)}")

        # Step 1: Read and analyze the document chunk
        read_task = Task(
            description=f"Analyze the following research paper chunk and extract key information including methodologies, findings, and recommendations. If necessary, use the Internet Search tool to gather additional context or information:\n\n{chunk}",
            agent=reader_agent,
            expected_output="A comprehensive summary of the key elements of this chunk of the research paper, including methodology, findings, and recommendations, along with any relevant additional information from internet searches."
        )
        read_crew = Crew(
            agents=[reader_agent],
            tasks=[read_task],
            verbose=2,
            process=Process.sequential
        )
        document_content = kickoff_crew(read_crew)

        # Step 2: Summarize the research content
        summarize_task = summarize_research_task(summarizer_agent, document_content)
        summarize_crew = Crew(
            agents=[summarizer_agent],
            tasks=[summarize_task],
            verbose=2,
            process=Process.sequential
        )
        research_summary = kickoff_crew(summarize_crew)
        all_summaries.append(research_summary)

        # Step 3: Generate podcast questions and discussion points
        question_task = generate_podcast_questions_task(question_generator, research_summary, podcast_description, guest_name, guest_expertise)
        question_crew = Crew(
            agents=[question_generator],
            tasks=[question_task],
            verbose=2,
            process=Process.sequential
        )
        podcast_questions = kickoff_crew(question_crew)
        all_questions.append(podcast_questions)
        print(podcast_questions)

        # Write the chunk's summary and questions to the file
        with open(output_file_path, 'a') as f:
            f.write(f"\n\n--- Chunk {i+1} Summary ---\n\n")
            f.write(research_summary)
            f.write(f"\n\n--- Chunk {i+1} Questions ---\n\n")
            f.write(podcast_questions)

    print(f"All chunk summaries and questions have been written to {output_file_path}")

if __name__ == "__main__":
    input_file = input("Please enter the full path to the input PDF file: ").strip()
    guest_name = input("Please enter the guest's name: ").strip()
    guest_expertise = input("Please enter the guest's area of expertise: ").strip()

    # output_file = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/pHDThesisBasedQuestions.txt"

    # Generate output file path
    input_dir = os.path.dirname(input_file)
    input_filename = os.path.basename(input_file)
    output_filename = os.path.splitext(input_filename)[0] + "_questions.txt"
    output_file = os.path.join(input_dir, output_filename)

    podcast_description = """
    A Sandbox Approach To Harvesting/Distilling Great Ideas
    Welcome to the Idea Sandbox podcast, where we dive into the power of ideas and the belief that they are the foundation of all societal progress and personal fulfillment. In a world increasingly focused on legislative solutions, we explore a different path—one where the spread of enlightened ideas can shape our value system and inspire change far beyond what laws alone can achieve.
    
    Our mission is rooted in the conviction that while legislative efforts are necessary, they are insufficient to usher in a brighter future. We believe that true transformation comes from embracing and promoting enlightenment ideas that encourage us to think deeper, live fully, and engage with the world and each other more meaningfully.
    
    At the Idea Sandbox, we're not just talking about theoretical concepts but engaging with thinkers, creators, and doers who exemplify this philosophy in their lives and work. We delve into discussions that challenge the status quo, inspire personal growth, and highlight the incredible potential for human flourishing when we prioritize ideas over injunctions.
    
    Join us as we explore the limitless possibilities that come from thinking critically, living intentionally, and fostering a culture that values ideas as the catalysts for authentic, sustainable progress. Together, let's create a future that is not only imagined but actively built on the foundation of ideas that enlighten, empower, and connect us all.
    """
    # guest_name = "Kiran Garimella"  # Replace with actual guest name
    # guest_expertise = "Misinformation, Whatsapp"  # Replace with actual guest expertise
    main(input_file, output_file, podcast_description, guest_name, guest_expertise)