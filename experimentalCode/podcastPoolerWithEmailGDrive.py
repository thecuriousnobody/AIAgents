import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

import config


def save_to_google_drive(content, file_name):
    creds = None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('/Users/rajeevkumar/Documents/myPersonalDocuments/client_secret_949298345051-ieb70h2d31ot22jfjv1vs3la4149vmp5.apps.googleusercontent.com.json', ['https://www.googleapis.com/auth/drive'])
        creds = flow.run_local_server(port=0)

    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'mimeType': 'text/plain'}
        media = MediaIoBaseUpload(BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media).execute()
        print(f'File ID: {file.get("id")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        file = None

    return file



# ... (previous code for setting up tasks and crew)
import os
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

topic = "European Sexuality"  # Change this variable to the desired topic

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    # model_name="llama3-70b-8192"
    model_name="mixtral-8x7b-32768"
    # model_name = "gemma-7b-it"
)



host_info = {
    "name": "Rajeev Kumar",
    "email": "theideasandboxpodcast@gmail.com",
    "website": "tisb.world",
    "whatsapp": "3096797200"
}

guest_pooler = Agent(
    role="Guest Pooler",
    goal=f"Find potential guests for the Idea Sandbox podcast who are doing interesting work related to {topic}.",
    backstory=f"You are an AI assistant whose job is to find potential guests for the Idea Sandbox podcast. Look for people doing interesting work in {topic}, and who would likely be willing to appear on a podcast with low subscriber base and viewership.",
    verbose=False,
    allow_delegation=False,
    llm=llm
)

guest_critic = Agent(
    role="Guest Critic",
    goal=f"Critique the potential guests suggested by the Guest Pooler based on their alignment with the mission of the Idea Sandbox podcast and their expertise in {topic}.",
    backstory=f"You are an AI assistant whose job is to critique the potential guests suggested by the Guest Pooler. The Idea Sandbox podcast focuses on the power of ideas as catalysts for personal growth and societal change. We seek guests who: 1. Believe in the transformative potential of enlightened ideas over solely legislative solutions. 2. Exemplify the philosophy of leveraging ideas for positive impact through their life and work. 3. Engage in discussions that challenge the status quo and inspire critical thinking. 4. Actively contribute to fostering a culture that values ideas as the foundation for authentic, sustainable progress. When evaluating potential guests, consider how well they align with our mission of promoting ideas that encourage deeper thinking, intentional living, and meaningful engagement with the world. Ideal guests should demonstrate the ability to inspire personal growth and highlight the potential for human flourishing through prioritizing enlightened ideas. Ensure that the guests have relevant expertise in {topic}.",
    verbose=False,
    llm=llm
)

monitor = Agent(
    role="Monitor",
    goal="Monitor the Guest Pooler and Guest Critic to ensure they stay on mission and keep track of the agreed-upon potential guests.",
    backstory="You are an AI assistant whose job is to monitor the Guest Pooler and Guest Critic agents. Make sure they stay focused on finding guests who align with the Idea Sandbox podcast's mission and have expertise in the specified topic. Keep track of the potential guests that both agents agree upon.",
    verbose=False,
    llm=llm
)

email_drafter = Agent(
    role="Email Drafter",
    goal="Draft compelling email pitches for the shortlisted potential guests based on their backgrounds and expertise.",
    backstory=f"You are an AI assistant whose job is to draft compelling email pitches for the shortlisted potential guests. Use the information about their backgrounds and expertise to create personalized and persuasive invitations that will increase the likelihood of them agreeing to be on the Idea Sandbox podcast. Include the host's information in the email: Name: {host_info['name']}, Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}",
    verbose=False,
    llm=llm
)

pool_guests = Task(
    description=f"Find potential guests for the Idea Sandbox podcast who are doing interesting work related to {topic}.",
    agent=guest_pooler,
    expected_output="A list of potential guests for the Idea Sandbox podcast, along with their contact information (email or social media handle).",
)

critique_guests = Task(
    description=f"Critique the potential guests suggested by the Guest Pooler based on their alignment with the mission of the Idea Sandbox podcast and their expertise in {topic}.",
    agent=guest_critic,
    expected_output=f"A list of potential guests that align with the mission of the Idea Sandbox podcast and have relevant expertise in {topic}.",
)

monitor_agents = Task(
    description="Monitor the Guest Pooler and Guest Critic to ensure they stay on mission and keep track of the agreed-upon potential guests.",
    agent=monitor,
    expected_output=f"A final list of potential guests for the Idea Sandbox podcast who have expertise in {topic}, along with their contact information.",
)

draft_emails = Task(
    description="Draft compelling email pitches for the shortlisted potential guests based on their backgrounds and expertise.",
    agent=email_drafter,
    expected_output=f"Personalized and persuasive email invitations for each shortlisted potential guest, tailored to their backgrounds and expertise. The emails should include the host's information: Name: {host_info['name']}, Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}",
)

crew = Crew(
    agents=[guest_pooler, guest_critic, monitor, email_drafter],
    tasks=[pool_guests, critique_guests, monitor_agents, draft_emails],
    verbose=1,
    process=Process.sequential
)

output = crew.kickoff()
print(output)


# Save the output to Google Drive
file_name = f"{topic}_guests.txt"
save_to_google_drive(output, file_name)

