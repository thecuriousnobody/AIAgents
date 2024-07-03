import os
from crewai import Agent, Task, Crew, Process
import PyPDF2
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_anthropic import ChatAnthropic
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from anthropic import APIStatusError
from langchain.agents import Tool
import time


os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

# Initialize tools and models
search_tool = DuckDuckGoSearchRun()


llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)

search_tool_wrapped = Tool(
    name="Internet Search",
    func=search_tool.run,
    description="Useful for when you need to answer questions about current events. Input should be a search query."
)

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
        role="Document Reader",
        goal="Accurately read and extract information from the input document",
        backstory="You are an expert in document analysis and information extraction. Your task is to read through documents and identify the key points and themes.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_summarizer_agent():
    return Agent(
        role="Content Summarizer",
        goal="Distill complex information into clear, concise salient points",
        backstory="You are a master of synthesis, capable of taking large amounts of information and extracting the most important ideas. Your summaries are clear, concise, and capture the essence of the original content.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_researcher_agent():
    return Agent(
        role="Information Researcher",
        goal="Expand on salient points with additional relevant information",
        backstory="You are a curious and thorough researcher with a vast knowledge base. Your task is to take key points and enrich them with additional context, examples, or supporting details.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool_wrapped]
    )

def create_condenser_agent():
    return Agent(
        role="Final Prompt Creator",
        goal="Create concise, thought-provoking prompts for podcast discussion",
        backstory="You are an expert in creating engaging prompts for discussion. Your task is to take expanded information and distill it into short, powerful phrases that will spark conversation and deep thinking.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def read_document_task(reader_agent, file_path):
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
    else:
        with open(file_path, 'r') as file:
            text = file.read()
    
    return Task(
        description=f"Analyze the following document content and extract key information:\n\n{text}",
        agent=reader_agent,
        expected_output="A comprehensive summary of the key points and main ideas from the document."
    )

def summarize_content_task(summarizer_agent, content):
    return Task(
        description=f"Summarize the following content into salient points:\n\n{content}",
        agent=summarizer_agent,
        expected_output="A list of concise, bullet-point style salient points that capture the essence of the content."
    )

def research_points_task(researcher_agent, points):
    return Task(
        description=f"""Research and expand on the following points with additional relevant information. 
        For each point, use the Internet Search tool to find current and relevant information. 
        Formulate specific search queries for each point to get the most relevant results.
        
        Points to research:
        {points}
        
        For each point:
        1. Formulate a clear search query.
        2. Use the Internet Search tool with this query.
        3. Analyze the search results and extract relevant information.
        4. Expand the original point with this new information.
        """,
        agent=researcher_agent,
        expected_output="An expanded version of each point, enriched with additional context, examples, or supporting details from current sources."
    )

def create_final_prompts_task(condenser_agent, expanded_points):
    return Task(
        description=f"Create concise, thought-provoking prompts from the following expanded information:\n\n{expanded_points}",
        agent=condenser_agent,
        expected_output="A list of short, powerful phrases or questions that can spark discussion and deep thinking during the podcast."
    )

def main(input_file_path, output_file_path):
    reader_agent = create_reader_agent()
    summarizer_agent = create_summarizer_agent()
    researcher_agent = create_researcher_agent()
    condenser_agent = create_condenser_agent()

    # Step 1: Read the document
    read_task = read_document_task(reader_agent, input_file_path)
    read_crew = Crew(
        agents=[reader_agent],
        tasks=[read_task],
        verbose=2,
        process=Process.sequential
    )
    # document_content = read_crew.kickoff()
    document_content = kickoff_crew(read_crew)

    # Step 2: Summarize the content
    summarize_task = summarize_content_task(summarizer_agent, document_content)
    summarize_crew = Crew(
        agents=[summarizer_agent],
        tasks=[summarize_task],
        verbose=2,
        process=Process.sequential
    )
    salient_points = summarize_crew.kickoff()

    # Step 3: Research and expand on the points
    research_task = research_points_task(researcher_agent, salient_points)
    research_crew = Crew(
        agents=[researcher_agent],
        tasks=[research_task],
        verbose=2,
        process=Process.sequential
    )
    expanded_points = research_crew.kickoff()

    # Step 4: Create final prompts
    condense_task = create_final_prompts_task(condenser_agent, expanded_points)
    condense_crew = Crew(
        agents=[condenser_agent],
        tasks=[condense_task],
        verbose=2,
        process=Process.sequential
    )
    final_prompts = condense_crew.kickoff()

    # Write the final prompts to a file
    with open(output_file_path, 'a') as f:  # 'a' mode for appending
        f.write("\n\n--- New Session ---\n\n")  # Add a separator for clarity
        f.write(final_prompts)

    print(f"Final prompts have been written to {output_file_path}")

if __name__ == "__main__":
    # input_file = input("Enter the path to your input document: ")
    # output_file = input("Enter the desired path for the output file: ")
    input_file = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Kiran Garimella/KiranGarimellaMyPersonalRant.pdf"
    output_file = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Kiran Garimella/Kiran Garimella Script 1.txt"
    main(input_file, output_file)