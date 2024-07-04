import os
from crewai import Agent, Task, Crew, Process
import PyPDF2
from langchain_anthropic import ChatAnthropic
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from anthropic import APIStatusError
import time

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

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
        llm=llm
    )

def create_summarizer_agent():
    return Agent(
        role="Research Summarizer",
        goal="Distill complex research information into clear, concise salient points",
        backstory="You are a master of synthesizing academic research, capable of extracting and presenting the most important aspects of studies in a clear, concise manner.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def read_document_task(reader_agent, file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    return Task(
        description=f"Analyze the following research paper and extract key information including the title, methodology, main findings, and recommendations:\n\n{text}",
        agent=reader_agent,
        expected_output="A comprehensive summary of the key elements of the research paper, including title, methodology, findings, and recommendations."
    )

def summarize_research_task(summarizer_agent, content):
    return Task(
        description=f"Summarize the following research content into salient points, focusing on key findings, methodologies, and recommendations:\n\n{content}",
        agent=summarizer_agent,
        expected_output="A list of concise, bullet-point style salient points that capture the essence of the research, preceded by the study title."
    )

def main(input_file_path, output_file_path):
    reader_agent = create_reader_agent()
    summarizer_agent = create_summarizer_agent()

    # Step 1: Read and analyze the document
    read_task = read_document_task(reader_agent, input_file_path)
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
    research_summary = summarize_crew.kickoff()

    # Write the research summary to a file
    with open(output_file_path, 'a') as f:  # 'a' mode for appending
        f.write("\n\n--- New Research Paper ---\n\n")  # Add a separator for clarity
        f.write(research_summary)

    print(f"Research summary has been written to {output_file_path}")

if __name__ == "__main__":
    input_file = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Kiran Garimella/ShortisTheRoadFeartoHate.pdf"
    output_file = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Kiran Garimella/Kiran Garimella Research Summaries.txt"
    main(input_file, output_file)