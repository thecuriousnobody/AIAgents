from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
import os
import config
import re
import os
import sys
import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain.tools import Tool


# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

# Initialize language model and search tool
from usefulTools.search_tools import search_tool, youtube_tool, search_api_tool


# Contact Information Researcher Agent
contact_researcher = Agent(
    role='Contact Information Researcher',
    goal='Find reliable contact information for potential podcast guests',
    backstory="""You are an expert at finding contact information for professionals and public figures. 
    Your task is to search for and compile email addresses or other reliable contact methods for potential podcast guests. 
    You use various online sources and strategies to find this information, always prioritizing official and professional channels.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

# Verification Agent
verification_agent = Agent(
    role='Contact Information Verifier',
    goal='Verify and cross-reference the contact information found by the researcher',
    backstory="""You are meticulous in verifying information. Your role is to cross-check and confirm 
    the contact details gathered by the Contact Information Researcher. You use multiple sources 
    to ensure the accuracy and currency of the information. You're also skilled at identifying 
    and flagging potentially outdated or incorrect information.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

# Ethical Considerations Agent
ethics_agent = Agent(
    role='Ethical Considerations Advisor',
    goal='Ensure that contact information is obtained and used ethically',
    backstory="""You are an expert in privacy laws and ethical considerations regarding personal information. 
    Your role is to review the gathered contact information and the methods used to obtain it, ensuring everything 
    is done ethically and in compliance with privacy regulations. You provide guidance on how to approach 
    using this information responsibly.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

# Alternative Contact Method Suggester
alternative_contact_agent = Agent(
    role='Alternative Contact Method Suggester',
    goal='Suggest alternative ways to reach out if direct contact information is not found',
    backstory="""You are creative in finding ways to connect with people. When direct email addresses 
    or phone numbers aren't available, you suggest alternative methods to reach out to potential guests. 
    This might include social media platforms, professional networks, or official channels. You're adept 
    at identifying the most appropriate and effective alternative contact methods for each individual.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[search_tool]
)

# Define tasks
research_contact_info = Task(
    description="""Research and compile contact information for the given potential podcast guest. 
    Focus on finding email addresses and phone numbers from official and professional sources. 
    If direct contact information is not available, note this clearly.""",
    agent=contact_researcher,
    expected_output="""A structured report containing:
    1. Guest Name: [Name]
    2. Email Address: [Email if found, or "Not found"]
    3. Phone Number: [Phone if found, or "Not found"]
    4. Official Website: [URL if available]
    5. Professional Social Media Profiles: [List of relevant profiles]
    6. Organization Contact: [If personal contact not found, provide organization's contact info]
    7. Sources: [List of sources used to find this information]
    8. Notes: [Any additional relevant information or challenges encountered]

    Ensure all information is presented clearly and concisely. If certain information is not found, explicitly state so."""
)

verify_contact_info = Task(
    description="""Verify the contact information found by the researcher. Cross-reference with multiple sources 
    to confirm accuracy. Flag any inconsistencies or potential inaccuracies. Provide a confidence level for each 
    piece of information verified.""",
    agent=verification_agent,
    expected_output="""A verification report including:
    1. Verification Status: [Verified / Partially Verified / Unable to Verify]
    2. For each piece of contact information:
       a. Item: [e.g., Email, Phone, Website]
       b. Verification Result: [Confirmed / Unconfirmed / Conflicting Information]
       c. Confidence Level: [High / Medium / Low]
       d. Sources Used for Verification: [List]
       e. Notes: [Any discrepancies or important observations]
    3. Overall Assessment: [Brief summary of the verification process and results]
    4. Recommendations: [Suggestions for further verification if needed]

    Provide clear explanations for any information that could not be verified or where conflicting data was found."""
)

assess_ethical_considerations = Task(
    description="""Review the methods used to obtain the contact information and the information itself. 
    Provide guidance on the ethical use of this information, including any privacy concerns or legal considerations. 
    Suggest best practices for reaching out to the individual.""",
    agent=ethics_agent,
    expected_output="""An ethical assessment report containing:
    1. Ethical Compliance: [Compliant / Partially Compliant / Non-Compliant]
    2. Privacy Concerns:
       a. [List any potential privacy issues]
       b. [Recommendations to address each concern]
    3. Legal Considerations:
       a. [Relevant laws or regulations to be aware of]
       b. [Compliance status with these laws]
    4. Best Practices for Contact:
       a. [List of recommended practices for reaching out]
       b. [Any specific considerations for this individual]
    5. Data Handling Recommendations:
       a. [How to store and use the contact information ethically]
       b. [Data retention and deletion guidelines]
    6. Overall Ethical Assessment:
       [Summary of the ethical implications and final recommendations]

    Provide clear, actionable guidance to ensure ethical use of the contact information."""
)

suggest_alternative_contact = Task(
    description="""If direct contact information (email or phone) is not found or has low confidence, 
    suggest alternative methods to reach out to the potential guest. This could include social media profiles, 
    professional networking sites, or official channels (e.g., through their organization). Provide a rationale 
    for each suggested method.""",
    agent=alternative_contact_agent,
    expected_output="""A report of alternative contact methods including:
    1. Primary Recommendation:
       a. Method: [e.g., LinkedIn Message, Twitter DM, Organization Contact Form]
       b. Rationale: [Why this method is recommended]
       c. Specific Contact Point: [e.g., LinkedIn profile URL, Twitter handle]
       d. Suggested Approach: [Brief on how to use this method effectively]
    2. Secondary Recommendations:
       [List 2-3 additional methods, each with the same structure as above]
    3. Potential Intermediaries:
       a. [Name and role of potential intermediary, if applicable]
       b. [Reason for suggesting this intermediary]
       c. [How to potentially reach the intermediary]
    4. General Advice:
       [Overall strategy for combining these methods if needed]
    5. Cautions:
       [Any warnings or things to avoid when using these alternative methods]

    Ensure each suggestion is practical, respectful, and aligned with professional outreach standards."""
)


# Function to process a single guest
def process_guest(guest_info):
    crew = Crew(
        agents=[contact_researcher, verification_agent, ethics_agent, alternative_contact_agent],
        tasks=[research_contact_info, verify_contact_info, assess_ethical_considerations, suggest_alternative_contact],
        verbose=2,
        process=Process.sequential
    )

    return crew.kickoff(inputs={"guest_info": guest_info})


# Main function to process all guests
def find_guest_contacts(guests_list):
    results = []
    for guest in guests_list:
        result = process_guest(guest)
        results.append(result)
    return results


# Example usage:
guests = [
    """
    Guest 1: Arvind Gupta
    - Current Position: Head of the Digital India Foundation
    - Area of Expertise: Digital transformation, e-governance, and technology-driven social change
    - Relevance to Topic: As a key figure in India's digital transformation, Arvind Gupta can provide insights into the government's initiatives and the impact of digital technologies in rural areas.
    - Recent Work: Involvement in driving social change through technology and scaling digital initiatives in India
    - Potential Contribution: Can offer a comprehensive view of India's digital evolution, including the implementation of Digital Public Infrastructure and its impact on rural communities
    """
]

results = find_guest_contacts(guests)
print(results)