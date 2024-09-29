from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
import PyPDF2
from langdetect import detect
from googletrans import Translator
# Assume these are properly imported and set up
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import search_tool, search_api_tool

llm = ClaudeSonnet

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def detect_language(text):
    return detect(text)

def translate_to_english(text, source_lang):
    translator = Translator()
    return translator.translate(text, src=source_lang, dest='en').text

def process_bill_document(file_path):
    # Read the PDF
    bill_text = read_pdf(file_path)
    
    # Detect language
    detected_lang = detect_language(bill_text)
    
    # Translate if not in English
    if detected_lang != 'en':
        bill_text = translate_to_english(bill_text, detected_lang)
    
    return bill_text, detected_lang

def create_legislative_bill_analysis_crew(bill_text, original_lang):
    # Define the agents (same as before)
    bill_analyzer = Agent(
        role="Legislative Bill Analyzer",
        goal="Thoroughly analyze the content and implications of the given legislative bill",
        backstory="You are an expert in Indian legislative processes with a deep understanding of legal language and policy implications.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

    impact_assessor = Agent(
        role="Socioeconomic Impact Assessor",
        goal="Evaluate the potential impacts of the bill on various segments of Indian society",
        backstory="You are a socioeconomic researcher with expertise in analyzing policy impacts across different demographic and economic groups in India.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

    data_researcher = Agent(
        role="Data and Statistics Researcher",
        goal="Gather relevant data and statistics to support impact assessments",
        backstory="You are a data scientist specializing in Indian demographics, economics, and social statistics.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

    policy_recommender = Agent(
        role="Policy Recommendation Specialist",
        goal="Suggest policy improvements or complementary measures to address potential issues",
        backstory="You are a policy expert with experience in crafting balanced and effective legislation in the Indian context.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    fact_checker = Agent(
        role="Fact-Checking and Quality Control Specialist",
        goal="Verify all information and ensure the accuracy of analyses and recommendations",
        backstory="You are a meticulous fact-checker with expertise in Indian law, policy, and socioeconomic data.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_api_tool]
    )

    language_specialist = Agent(
        role="Language and Translation Specialist",
        goal="Ensure accurate interpretation of the bill's language, especially if translated",
        backstory="You are a multilingual expert in legal terminology and translation, specializing in Indian languages and legislative documents.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Define the tasks
    language_review_task = Task(
        description=f"Review the bill's text, considering it was originally in {original_lang} and translated to English. Ensure no meaning was lost in translation and clarify any language-specific nuances.",
        agent=language_specialist,
        expected_output="A report on the accuracy of the translation and any important language-specific considerations."
    )

    bill_analysis_task = Task(
        description="Analyze the given legislative bill, identifying key provisions, objectives, and potential areas of impact.",
        agent=bill_analyzer,
        expected_output="A comprehensive breakdown of the bill's content, objectives, and potential areas of societal impact.",
        context=[language_review_task]
    )

    bill_analysis_task = Task(
        description="Analyze the given legislative bill, identifying key provisions, objectives, and potential areas of impact.",
        agent=bill_analyzer,
        expected_output="A comprehensive breakdown of the bill's content, objectives, and potential areas of societal impact."
    )

    data_research_task = Task(
        description="Research and compile relevant data and statistics related to the bill's focus areas and potential impacts.",
        agent=data_researcher,
        expected_output="A collection of relevant data and statistics to support impact assessments.",
        context=[bill_analysis_task]
    )

    impact_assessment_task = Task(
        description="Evaluate the potential impacts of the bill on various segments of Indian society, including different economic classes, public/private sector employees, and demographic groups.",
        agent=impact_assessor,
        expected_output="A detailed assessment of the bill's potential impacts on different societal groups, supported by data.",
        context=[bill_analysis_task, data_research_task]
    )

    policy_recommendation_task = Task(
        description="Based on the impact assessment, suggest policy improvements or complementary measures to address potential issues or enhance positive outcomes.",
        agent=policy_recommender,
        expected_output="A set of policy recommendations to address potential issues or enhance the bill's effectiveness.",
        context=[impact_assessment_task]
    )

    fact_checking_task = Task(
        description="Review all analyses, data, and recommendations for accuracy and consistency.",
        agent=fact_checker,
        expected_output="A verification report highlighting any discrepancies or areas needing correction, along with final verified information.",
        context=[bill_analysis_task, data_research_task, impact_assessment_task, policy_recommendation_task]
    )

    final_report_task = Task(
        description="Compile a comprehensive final report on the bill's analysis, impacts, and recommendations, suitable for distribution to citizens. Include any relevant language considerations.",
        agent=fact_checker,
        expected_output="A clear, concise, and accurate report summarizing the bill's content, impacts, and recommendations, tailored for public understanding, including notes on original language if relevant.",
        context=[language_review_task, bill_analysis_task, data_research_task, impact_assessment_task, policy_recommendation_task, fact_checking_task]
    )

    # Create and return the crew
    return Crew(
    agents=[bill_analyzer, impact_assessor, data_researcher, policy_recommender, fact_checker, language_specialist],
    tasks=[language_review_task, bill_analysis_task, data_research_task, impact_assessment_task, policy_recommendation_task, fact_checking_task, final_report_task],
    verbose=True,  # Changed from 2 to True
    process=Process.sequential
    )
# Usage
file_path = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Kalpana Sharma/bill1640_39.pdf"
bill_text, original_lang = process_bill_document(file_path)
crew = create_legislative_bill_analysis_crew(bill_text, original_lang)
result = crew.kickoff()

print(result)