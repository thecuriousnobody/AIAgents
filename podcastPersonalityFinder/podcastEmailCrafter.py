from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
from anthropic import Anthropic
import anthropic
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from duckduckgo_search import DDGS
# from langchain.utilities import SerpAPIWrapper
import config
import os
import re
import time
import random
from googleCustomSearch import google_custom_search
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper


from crewai_tools.tools import SerperDevTool
from langchain.tools import Tool

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="Useful for when you need to answer questions about current events or general knowledge. You should ask targeted questions."
)

llm_GROQ= ChatOpenAI(
    openai_api_base = "https://api.groq.com/openai/v1",
    openai_api_key =  os.getenv("GROQ_API_KEY"),
    model_name = "gemma2-9b-it"
)


ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)

def get_user_input_path():
    while True:
        user_path = input("Enter the full path to your podcast personalities file: ").strip()
        if os.path.isfile(user_path):
            return user_path
        else:
            print(f"The file '{user_path}' does not exist. Please enter a valid file path.")

def parse_podcast_personalities(file_path=None):
    if file_path is None:
        file_path = get_user_input_path()
    
    with open(file_path, 'r') as file:
        content = file.read()

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    model = "claude-3-5-sonnet-20240620"

    system_message = """You are an AI assistant skilled at extracting structured information from text.
    Your task is to parse information about podcast personalities, extracting their name, title, and a brief description of their work."""

    prompt = f"""Parse the following text and extract the name, title, and work description for each person mentioned.
    Format the output as a JSON array of objects, with keys 'name', 'title', and 'work'.
    If any information is missing, leave the corresponding value as an empty string.
    Ensure the output is valid JSON.
    
    Text to parse:
    {content}"""

    message = client.messages.create(
        model=model,
        max_tokens=2000,
        temperature=0,
        system=system_message,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    response = message.content[0].text

    # Extract the JSON array from the response
    json_match = re.search(r'\[.*\]', response, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        try:
            personalities = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            personalities = []
    else:
        print("No JSON array found in the response")
        personalities = []

    return personalities


personalities = parse_podcast_personalities()

for person in personalities:
    guest_name = person['name']
    guest_title = person['title']
    guest_work_summary = person['work']

    host_name = "Rajeev Kumar"
    host_podcast = "The Idea Sandbox"
    host_mission = """The Idea Sandbox podcast is a crucible for transformative thinking, championing the power of ideas as the true architects of 
    societal progress and personal fulfillment. We challenge the notion that legislation alone can craft a better world, 
    instead fostering a space where enlightened concepts can germinate, flourish, and reshape our collective values. 
    By engaging with visionaries who embody this philosophy, we aim to ignite critical thinking, inspire intentional living, 
    and cultivate a culture where ideas are the catalysts for authentic, sustainable change. Our mission transcends mere discussion; 
    we're building a movement that empowers individuals to think deeper, live fuller, and connect more meaningfully, 
    ultimately crafting a future where human potential is unleashed through the power of transformative ideas."""
    host_email = "theideasandboxpodcast@gmail.com"
    host_website = "https://tisb.world"
    host_phone = "+13096797200"


    if __name__ == '__main__':
        llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.getenv("GROQ_API_KEY"),
            model_name="gemma2-9b-it"
        )


        host_info = {
            "name": "Rajeev Kumar",
            "email": "theideasandboxpodcast@gmail.com",
            "website": "tisb.world",
            "whatsapp": "3096797200"
        }

        info_gatherer = Agent(
            role='Podcast Guest Researcher',
            goal=f'Find relevant information and contact details for {guest_name}, specializing in {guest_work_summary}',
            backstory=f"""You are an expert researcher specializing in finding comprehensive 
            information about individuals in various fields. Your current task is to gather 
            data on {guest_name}, an expert in {guest_work_summary}. You excel at crafting precise 
            search queries, filtering information from credible sources, and synthesizing 
            key insights about a person's work, expertise, and recent activities. Your primary 
            objectives are to:
            1. Find accurate contact information, especially email addresses
            2. Gather relevant background information about their work and expertise
            3. Identify recent activities, publications, or statements related to {guest_work_summary}
            4. Discover any public content they've produced that might be relevant to a podcast appearance
            
            You have a keen eye for detail and can critically evaluate the credibility of sources. 
            Your talent for clear and concise summarization helps you distill complex information 
            into easily digestible reports.""",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,  # Placeholder for the actual language model
            max_iter=5,
            memory=True,
            tools=[search_tool],  # Add any additional tools as needed
        )

        email_crafter = Agent(
            role="Personalized Podcast Invitation Composer",
            goal="Craft compelling, personalized email invitations for potential podcast guests that resonate with the podcast's mission and the guest's unique expertise.",
            backstory="""You are an AI assistant specializing in composing engaging and personalized email invitations for 'The Idea Sandbox' podcast. With a deep understanding of the podcast's mission to harvest ideas, foster enlightened beliefs, and promote societal progress through thought, you craft each invitation to reflect the host's passion for intellectual discourse.

            Your expertise lies in synthesizing information about potential guests and creating invitations that highlight the relevance of their work to the podcast's mission. You have a keen ability to convey authenticity and genuine enthusiasm, avoiding clichés and overly formal language.

            Your invitations are designed to be concise yet impactful, typically ranging from 250-350 words. You excel at emphasizing the potential for meaningful, thought-provoking conversations and incorporating elements of the podcast's mission into each invitation.

            You understand the importance of personalization and always strive to create a warm, welcoming tone that reflects the unique aspects of each potential guest's work and its connection to the broader themes of idea exploration and societal progress.""",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[search_tool],
        
        )

        gather_guest_info = Task(
            description="""Research and compile comprehensive information about a potential podcast guest, focusing on their work, expertise, relevance to the podcast's themes, and most importantly, their contact information.

            Special focus on finding the guest's email address:
            1. Check the guest's personal or professional website for a contact page or email address.
            2. Look for the guest's institutional/organizational email if they're affiliated with a university or company.
            3. Search professional networking sites like LinkedIn for contact information.
            4. Check recent publications or conference proceedings where the guest may have provided an email for correspondence.
            5. Look for contact information on their social media profiles.
            6. If direct email isn't found, identify the most promising method to reach out to the guest (e.g., through their agent, institution, or a contact form on their website).

            Ensure all searches and methods used to find contact information are ethical and respect privacy.""",
            agent=info_gatherer,  # Assuming 'info_gatherer' is your previously defined agent
            expected_output="""A detailed profile of the potential guest, including:
            1. Full name and professional title
            2. Current affiliation (university, organization, company)
            3. Contact information:
            a. Email address (primary objective)
            b. Alternative contact methods if email is not found
            4. Brief biography highlighting key achievements and background
            5. Detailed summary of their most significant work or research
            6. Recent publications, projects, or initiatives
            7. Any public statements or opinions related to the podcast's themes
            8. Their potential unique perspective or contribution to the podcast
            9. Relevant social media profiles or personal websites
            10. Any previous podcast or media appearances
            11. Methods used to search for contact information and their results

            The information should be well-organized, accurate, and directly relevant to crafting a personalized invitation and preparing for a potential podcast conversation. If an email address is not found, provide a clear explanation of the best alternative method to contact the guest."""
        )


        craft_invitation_email = Task(
            description=f"""
            Compose a personalized, engaging email invitation for a potential podcast guest, highlighting the relevance of their work to the podcast's mission and emphasizing the potential for a meaningful conversation. Remember, this is a solo effort by the host, not a team project.

            Use the following information to craft the email:

            Host Information:
            - Name: {host_name}
            - Podcast: {host_podcast}
            - Mission: {host_mission}
            - Email: {host_email}
            - Website: {host_website}
            - Phone: {host_phone}

            Guest Information:
            - Name: {guest_name}
            - Title: {guest_title}
            - Work Summary: {guest_work_summary}

            The output should be structured as follows:
            1. Guest's email address (ONLY if found during info gathering)[blank line] (ONLY if email was found)
            2. A blank line
            3. Subject line for the email
            4. Another blank line
            5. The body of the email

            The email body should:
            1. Address the guest by name and title
            2. Introduce the host as an individual and the podcast as his personal project
            3. Highlight the guest's work and its relevance to the podcast's mission
            4. Clearly invite the guest to participate
            5. Include the host's contact information (email, website, and phone number)
            6. Close with enthusiasm for a potential conversation

            Key points to remember:
            - Use "I" instead of "we" throughout the email to emphasize this is a solo effort
            - Convey the personal passion and individual commitment of the host
            - Highlight that this is an independent podcast driven by one person's mission
            - Emphasize the unique, intimate nature of the conversation that comes from a one-on-one dialogue

            Ensure the email is warm, personal, 250-350 words long, and avoids clichés and overly formal language.
            Use the exact host information provided, do not invent or alter any details.
            """,
            agent=email_crafter,
            expected_output="""Output should be structured as follows:

            1. Guest's email address
            [blank line]
            2. Subject line
            [blank line]
            3. Email body:
            - A warm, personal greeting addressing the guest by name and title
            - A brief introduction of the host as an individual and the podcast as his personal project
            - A paragraph highlighting the guest's work and its relevance to the podcast's themes
            - An explanation of why the guest's perspective would be valuable to the podcast audience
            - A clear invitation to participate in the podcast
            - A brief description of the podcast format and what to expect
            - Flexibility in scheduling and any technical requirements
            - The host's contact information and preferred method of communication
            - A polite closing that expresses enthusiasm for a potential conversation
            
            The email body should be:
            - Between 250-350 words
            - Written in a warm, authentic tone that reflects the host's personal passion for ideas
            - Free of clichés and overly formal language
            - Tailored to the specific guest, incorporating details from the info gatherer's research
            - Aligned with the podcast's mission of harvesting ideas, fostering enlightened beliefs, and promoting societal progress through thought
            - Use "I" instead of "we" to emphasize the solo nature of the podcast
            - Include the host's exact name, email, and phone number as provided""",
            context = [gather_guest_info]
        )

        crew = Crew(
            agents=[info_gatherer, email_crafter],
            tasks=[gather_guest_info, craft_invitation_email],
            verbose=1,
            process=Process.sequential
        )

        output = crew.kickoff()
        print(output)

        def write_guest_email_to_file(content, guest_name, directory="/Users/rajeevkumar/Documents/TISB/pitchEmails"):
            """
            Write email content to a file named after the guest in the specified directory.
            Creates the directory if it doesn't exist.
            """
            try:
                # Ensure the directory exists
                os.makedirs(directory, exist_ok=True)
                
                # Clean the guest name to make it suitable for a filename
                clean_name = re.sub(r'[^\w\-_\. ]', '_', guest_name)
                clean_name = clean_name.replace(' ', '_')
                
                # Construct the filename
                filename = f"{clean_name}_email.txt"
                
                # Construct the full file path
                file_path = os.path.join(directory, filename)
                
                # Write the content to the file
                with open(file_path, "w") as file:
                    file.write(content)
                print(f"Successfully wrote email for {guest_name} to {file_path}")
            except IOError as e:
                print(f"An error occurred while writing to the file: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    # Example usage

    write_guest_email_to_file(output, guest_name)


if __name__ == "__main__":
    parse_podcast_personalities()
