from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import os
import sys
from PyPDF2 import PdfReader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import search_tool, youtube_tool, search_api_tool
from usefulTools.llm_repository import ClaudeSonnet

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def create_agents_and_tasks(pdf_content):
    pdf_reader = Agent(
        role="PDF Reader",
        goal="Extract and summarize the key information from the entire provided PDF document.",
        backstory="You are an expert at quickly parsing and understanding complex documents, no matter their length.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    bill_analyzer = Agent(
        role="Bill Analyzer",
        goal="Analyze the full bill content and identify all key points, changes, and potential impacts.",
        backstory="You are a legislative expert with deep knowledge of Indian law and policy, capable of understanding complex bills in their entirety.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    historical_researcher = Agent(
        role="Historical Researcher",
        goal="Research and provide comprehensive historical context and related information for the bill.",
        backstory="You have extensive knowledge of Indian legislative history and can quickly find and synthesize relevant information from various sources.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_api_tool]
    )

    citizen_impact_analyst = Agent(
        role="Citizen Impact Analyst",
        goal="Analyze how the bill will impact the average citizen and summarize in simple terms, considering all aspects of the bill.",
        backstory="You are skilled at translating complex policy into everyday implications for citizens, ensuring no important details are overlooked.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    read_pdf_task = Task(
        description=f"Read and summarize the key points from the following complete PDF content:\n\n{pdf_content}",
        agent=pdf_reader,
        expected_output="A comprehensive summary of the bill's main points, objectives, and structure."
    )

    analyze_bill_task = Task(
        description="Analyze the complete bill content, identify all key changes, and potential impacts. Consider every section of the bill.",
        agent=bill_analyzer,
        expected_output="A detailed analysis of the entire bill, including all major changes and potential consequences.",
        context=[read_pdf_task]
    )

    research_history_task = Task(
        description="Research comprehensive historical context and related information for this bill. Consider past legislation, social context, and political factors.",
        agent=historical_researcher,
        expected_output="Extensive historical information and context for the bill, including related past legislation and sociopolitical factors.",
        context=[analyze_bill_task]
    )

    analyze_citizen_impact_task = Task(
        description="Analyze and summarize how this bill will impact the average citizen, considering all aspects of the bill and its potential long-term effects.",
        agent=citizen_impact_analyst,
        expected_output="A clear, comprehensive explanation of how the bill will affect everyday citizens, including both immediate and potential future impacts.",
        context=[analyze_bill_task, research_history_task]
    )

    return [pdf_reader, bill_analyzer, historical_researcher, citizen_impact_analyst], [read_pdf_task, analyze_bill_task, research_history_task, analyze_citizen_impact_task]

def run_bill_analysis(pdf_path):
    pdf_content = read_pdf(pdf_path)
    agents, tasks = create_agents_and_tasks(pdf_content)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    output = crew.kickoff()
    return output

if __name__ == '__main__':
    pdf_path = input("Enter the path to the PDF file of the bill: ")
    result = run_bill_analysis(pdf_path)
    
    print("\nBill Analysis Results:")
    print(result)

    # Convert CrewOutput to string
    result_str = str(result)

    # Write the generated content to a file
    directory = os.path.dirname(pdf_path)
    file_name = f"bill_analysis_{os.path.basename(pdf_path).replace('.pdf', '')}.txt"
    full_path = os.path.join(directory, file_name)  
    
    try:
        with open(full_path, "w", encoding='utf-8') as file:
            file.write(result_str)
        print(f"\nResults saved to {file_name}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")