import os
from crewai import Agent, Task, Crew, Process
import PyPDF2
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from anthropic import APIStatusError
import time

os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

# Set up SerpAPI search
search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="""Useful for when you need to answer questions about 
    current events or general knowledge. You should ask targeted questions."""
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
    output = crew.kickoff()
    return output.result if hasattr(output, 'result') else str(output)


def create_reader_agent():
    return Agent(
        role="Research Paper Analyzer",
        goal="Accurately extract key information from research papers",
        backstory="""You are an expert in analyzing academic papers, capable of identifying 
                  crucial elements such as methodologies, findings, and recommendations.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )


def create_summarizer_agent():
    return Agent(
        role="Research Summarizer",
        goal="Distill complex research information into clear, concise salient points",
        backstory="""You are a master of synthesizing academic research, capable of extracting 
        and presenting the most important aspects of studies in a clear, concise manner.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )


def create_insight_extractor():
    return Agent(
        role="Insight Extractor",
        goal="Extract key insights and implications from research findings",
        backstory="""You are an expert at identifying the most important takeaways from research 
                  and understanding their broader implications. You can connect ideas across 
                  different domains and provide valuable context.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )


def read_document_task(reader_agent, file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    return Task(
        description=f"""Analyze the following research paper and extract key information 
        including the title, authors, methodology, main findings, and recommendations. 
        If necessary, use the Internet Search tool to gather additional context or information:

        {text}""",
        agent=reader_agent,
        expected_output="""A comprehensive summary of the key elements of the research paper, 
                        including title, authors, methodology, findings, and recommendations, 
                        along with any relevant additional information from internet searches."""
    )


def summarize_research_task(summarizer_agent, content):
    return Task(
        description=f"""Summarize the following research content into salient points, 
        focusing on key findings, methodologies, and recommendations. 
        Organize the information in a clear, structured format. 
        If necessary, use the Internet Search tool to provide additional context or supporting information:

        {content}""",
        agent=summarizer_agent,
        expected_output="""A structured summary of the research, including main topics, 
                        key findings, methodologies, and recommendations, 
                        presented in a clear and organized format."""
    )


def extract_insights_task(insight_extractor, content):
    return Task(
        description=f"""Based on the following research summary, extract key insights and their broader implications. 
        Consider how these findings might apply to different contexts or industries. 
        Use the Internet Search tool to find additional relevant information or examples 
        that could enhance understanding of the research implications.

        Research summary:
        {content}

        Your task is to:
        1. Identify the most significant insights from the research
        2. Explain the broader implications of these insights
        3. Provide examples of how these insights might be applied in different contexts
        4. Highlight any connections to current trends or developments in related fields
        5. Suggest areas for further research or exploration based on these findings

        Organize your response in a clear, structured format.""",
        agent=insight_extractor,
        expected_output="""A structured list of key insights from the research, 
        their broader implications, potential applications, connections to current trends, 
        and suggestions for further exploration."""
    )


def main(input_file_path, output_file_path):
    reader_agent = create_reader_agent()
    summarizer_agent = create_summarizer_agent()
    insight_extractor = create_insight_extractor()

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
    research_summary = kickoff_crew(summarize_crew)

    # Step 3: Extract insights and implications
    insight_task = extract_insights_task(insight_extractor, research_summary)
    insight_crew = Crew(
        agents=[insight_extractor],
        tasks=[insight_task],
        verbose=2,
        process=Process.sequential
    )
    research_insights = kickoff_crew(insight_crew)

    # Write the research summary and insights to a file
    with open(output_file_path, 'a') as f:
        f.write("\n\n--- New Research Paper Analysis ---\n\n")
        f.write(research_summary)
        f.write("\n\n--- Key Insights and Implications ---\n\n")
        f.write(research_insights)

    print(f"Research summary and insights have been written to {output_file_path}")


if __name__ == "__main__":
    input_file = "/path/to/your/input/file.pdf"
    output_file = "/path/to/your/output/file.txt"
    main(input_file, output_file)