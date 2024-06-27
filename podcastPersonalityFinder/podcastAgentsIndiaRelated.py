from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
from anthropic import Anthropic
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_anthropic import ChatAnthropic
import config
import os

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

search_tool = DuckDuckGoSearchRun()

ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620"
)

if __name__ == '__main__':
    llm = ChatOpenAI(
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )


    host_info = {
        "name": "Rajeev Kumar",
        "email": "theideasandboxpodcast@gmail.com",
        "website": "tisb.world",
        "whatsapp": "3096797200"
    }

    whatsapp_university_expert_finder = Agent(
        role="WhatsApp University Expert Finder",
        goal="Identify and compile information on individuals who are doing significant work in understanding, researching, or combating the 'WhatsApp University' phenomenon in India.",
        backstory="""You are an AI assistant specialized in identifying experts, researchers, activists, and thought leaders who are working to understand and address the 'WhatsApp University' phenomenon in India. This includes:

        1. Researchers studying the spread of misinformation through WhatsApp in India
        2. Social scientists analyzing the impact of WhatsApp-based propaganda on Indian society
        3. Journalists investigating and reporting on the 'WhatsApp University' phenomenon
        4. Activists working to counter misinformation and promote digital literacy
        5. Technologists developing tools or platforms to combat fake news on WhatsApp
        6. Policy experts proposing regulations or guidelines to address this issue
        7. Educators creating programs to enhance critical thinking and media literacy
        8. Public figures who have spoken out against the misuse of WhatsApp for propaganda

        Your task is to find individuals who are making significant contributions in these areas, with a focus on those who can provide unique insights, innovative solutions, or impactful perspectives on the 'WhatsApp University' phenomenon and its effects on Indian society.""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    
    )
    whatsapp_university_guest_finder = Agent(
        role="WhatsApp University Expert Finder",
        goal="Identify individuals or groups doing impactful work related to the 'WhatsApp University' phenomenon in India, particularly those with lower social media presence but significant contributions.",
        backstory="""You are an AI assistant specialized in discovering potential podcast guests who are making meaningful contributions to understanding or addressing the 'WhatsApp University' phenomenon in India. Your focus is on finding experts who may not have a large public profile but are doing crucial work in this field. This includes:

        1. Academic researchers studying misinformation spread through WhatsApp in India
        2. Social scientists analyzing the societal impact of WhatsApp-based propaganda
        3. Investigative journalists uncovering stories related to 'WhatsApp University'
        4. Grassroots activists combating misinformation and promoting digital literacy
        5. Technologists developing innovative solutions to counter fake news on WhatsApp
        6. Policy experts proposing nuanced approaches to address this issue
        7. Educators creating impactful programs to enhance critical thinking and media literacy
        8. Lesser-known public figures who have taken strong stands against WhatsApp misuse

        Your task is to uncover individuals who are passionately working in these areas but may not be widely recognized. Look for those with unique perspectives, hands-on experience, or innovative approaches to the 'WhatsApp University' phenomenon.""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    )

    find_whatsapp_university_experts = Task(
        description="""Identify and compile information on at least 5 individuals who are doing noteworthy work related to the 'WhatsApp University' phenomenon in India. For each individual, provide:

        1. Name and professional title
        2. Area of expertise (e.g., research, activism, journalism, technology)
        3. Brief summary of their work related to 'WhatsApp University'
        4. Any significant publications, projects, or initiatives they've undertaken
        5. Their potential unique contribution to a podcast discussion on this topic
        6. If available, their contact information or professional affiliations

        Prioritize individuals who offer diverse perspectives and approaches to understanding or addressing this issue.""",
        agent=whatsapp_university_expert_finder,
        expected_output="""A list of at least 10 individuals with detailed information on each, including:
        - Full name and title
        - Area of expertise
        - Summary of relevant work
        - Notable publications or projects
        - Potential podcast contribution
        - Contact information (if available)

        The list should represent a diverse range of approaches and perspectives on the 'WhatsApp University' phenomenon."""
    )
    find_whatsapp_university_guests = Task(
        description="""Identify and compile information on at least 5 individuals or groups who are doing impactful work related to the 'WhatsApp University' phenomenon in India, but may not have a high public profile. For each potential guest, provide:

        1. Name and professional title or role
        2. Affiliation (organization, institution, or independent status)
        3. Area of expertise within the 'WhatsApp University' context
        4. Brief description of their work, highlighting its impact and uniqueness
        5. Any notable projects, publications, or initiatives they've undertaken
        6. Their potential unique contribution to a podcast discussion on this topic
        7. If available, contact information or means to reach them
        8. Explanation of why they would be a valuable guest despite potentially lower public visibility

        Prioritize individuals or groups who offer fresh perspectives, ground-level insights, or innovative approaches to understanding or combating the 'WhatsApp University' phenomenon.""",
        agent=whatsapp_university_guest_finder,
        expected_output="""A list of at least 5 potential guests with detailed information on each, including:
        - Full name and title/role
        - Affiliation
        - Area of expertise
        - Summary of relevant work and its impact
        - Notable projects or publications
        - Potential unique podcast contribution
        - Contact information (if available)
        - Justification for their value as a guest

        The list should represent a diverse range of perspectives and approaches to the 'WhatsApp University' phenomenon, with a focus on impactful work rather than public profile."""
    )
    crew = Crew(
        agents=[whatsapp_university_expert_finder, whatsapp_university_guest_finder],
        tasks=[find_whatsapp_university_experts, find_whatsapp_university_guests],
        verbose=1,
        process=Process.sequential
    )

    output = crew.kickoff()
    print(output)

    # Write the generated content to a file
    try:
        with open("/Users/rajeevkumar/Documents/TISB/pitchEmails/potentialWhatsAppUGuests.txt", "w") as file:
            file.write(output)
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")