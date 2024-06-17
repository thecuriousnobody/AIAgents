from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import config
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY


llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192"
    # model_name="mixtral-8x7b-32768"
    # model_name = "gemma-7b-it"
)

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain.utilities import WikipediaAPIWrapper


# Define the guest info schema
class GuestInfo:
    def __init__(self, name, work, expertise, perspective, specific_work):
        self.name = name
        self.work = work
        self.expertise = expertise
        self.perspective = perspective
        self.specific_work = specific_work


# Define the guest info retrieval agent
class GuestInfoRetrievalAgent(Agent):
    def run(self, guest_name):
        """
        Retrieve guest information from Wikipedia based on the guest's name.

        Args:
            guest_name (str): The name of the guest.

        Returns:
            GuestInfo: The retrieved guest information.
        """
        wikipedia = WikipediaAPIWrapper()

        # Search for the guest's Wikipedia page
        search_results = wikipedia.search(guest_name)
        if search_results:
            page_title = search_results[0]
            page_content = wikipedia.page(page_title).content

            # Extract relevant information from the page content
            work = self.extract_work(page_content)
            expertise = self.extract_expertise(page_content)
            perspective = self.extract_perspective(page_content)
            specific_work = self.extract_specific_work(page_content)

            guest_info = GuestInfo(
                name=guest_name,
                work=work,
                expertise=expertise,
                perspective=perspective,
                specific_work=specific_work
            )

            return guest_info
        else:
            raise ValueError(f"No Wikipedia page found for guest: {guest_name}")

    def extract_work(self, content):
        # Implement logic to extract work information from the page content
        # You can use NLP techniques or pattern matching to identify relevant information
        # For simplicity, let's assume the work information is always present in the first paragraph
        first_paragraph = content.split("\n")[0]
        return first_paragraph

    def extract_expertise(self, content):
        # Implement logic to extract expertise information from the page content
        # You can use NLP techniques or pattern matching to identify relevant information
        # For simplicity, let's assume the expertise information is always present in the second paragraph
        second_paragraph = content.split("\n")[1]
        return second_paragraph

    def extract_perspective(self, content):
        # Implement logic to extract perspective information from the page content
        # You can use NLP techniques or pattern matching to identify relevant information
        # For simplicity, let's assume the perspective information is always present in the third paragraph
        third_paragraph = content.split("\n")[2]
        return third_paragraph

    def extract_specific_work(self, content):
        # Implement logic to extract specific work information from the page content
        # You can use NLP techniques or pattern matching to identify relevant information
        # For simplicity, let's assume the specific work information is always present in the fourth paragraph
        fourth_paragraph = content.split("\n")[3]
        return fourth_paragraph


# Define the emailer agent
class EmailerAgent(Agent):
    def run(self, guest_info):
        """
        Craft a personalized email based on the guest's information.

        Args:
            guest_info (GuestInfo): The guest information object.

        Returns:
            str: The drafted email.
        """
        opening_line = f"Dear {guest_info.name},\n\nI hope this email finds you well. I came across your fascinating work on {guest_info.work} and was truly impressed by your insights."

        introduction = "I am reaching out to you today to invite you to be a guest on the Idea Sandbox Podcast. Our podcast focuses on tackling complex challenges and exploring innovative solutions across various fields."

        examples = f"Your expertise in {guest_info.expertise} and your unique perspective on {guest_info.perspective} would be invaluable to our listeners. We believe that your work on {guest_info.specific_work} aligns perfectly with the mission of our podcast."

        call_to_action = "We would be honored to have you join us for an episode of the Idea Sandbox Podcast. The interview would be conducted remotely at a time that is most convenient for you. We are flexible with the format and can tailor the discussion to your preferences."

        podcast_info = "Our podcast has a dedicated audience of professionals and enthusiasts who are passionate about innovation and problem-solving. We provide episode transcripts and promote each interview across our social media channels and website. You can find some of our previous interviews with notable guests at [link to podcast episodes]."

        closing = "Thank you for considering this invitation. We genuinely believe that your participation would greatly enrich the conversation and provide our listeners with valuable insights.\n\nPlease let me know if you have any questions or if there is any additional information I can provide. I look forward to the possibility of collaborating with you.\n\nBest regards,\n[Your Name]\nHost of the Idea Sandbox Podcast"

        email_draft = f"{opening_line}\n\n{introduction}\n\n{examples}\n\n{call_to_action}\n\n{podcast_info}\n\n{closing}"

        return email_draft


# Define the adapter agent
class AdapterAgent(Agent):
    def run(self, email_draft, podcast_ethos):
        """
        Review the email draft, offer critiques, and suggest improvements based on the podcast's ethos.

        Args:
            email_draft (str): The drafted email from the emailer agent.
            podcast_ethos (str): The ethos and mission of the Idea Sandbox Podcast.

        Returns:
            str: The revised email draft with suggestions for improvement.
        """
        review = f"Here are some suggestions to improve the email draft:\n\n1. Personalization: Make sure to highlight specific aspects of the guest's work that align with the podcast's theme. This will show that you have done thorough research and are genuinely interested in their expertise.\n\n2. Compelling content: Emphasize how the guest's insights can benefit the podcast's audience. Provide concrete examples of how their work relates to the challenges and solutions discussed on the podcast.\n\n3. Podcast ethos: Inject more of the Idea Sandbox Podcast's ethos into the email. Mention how the podcast aims to foster meaningful conversations and collaborate with experts like the guest to drive innovation and solve complex problems."

        revised_email_draft = f"{email_draft}\n\n{review}"

        return revised_email_draft


# Define the email drafting process
class EmailDraftingProcess(Process):
    guest_info_retrieval_agent: GuestInfoRetrievalAgent
    emailer_agent: EmailerAgent
    adapter_agent: AdapterAgent

    def run(self, guest_name, podcast_ethos):
        guest_info = self.guest_info_retrieval_agent.run(guest_name)
        email_draft = self.emailer_agent.run(guest_info)
        final_email = self.adapter_agent.run(email_draft, podcast_ethos)
        return final_email


# Example usage
guest_name = "Elon Musk"
podcast_ethos = "The Idea Sandbox Podcast is dedicated to exploring innovative ideas and solutions to complex challenges. We bring together experts from diverse fields to foster meaningful conversations and collaborate on driving positive change."

email_drafting_process = EmailDraftingProcess(
    guest_info_retrieval_agent=GuestInfoRetrievalAgent(llm=ChatOpenAI()),
    emailer_agent=EmailerAgent(llm=ChatOpenAI()),
    adapter_agent=AdapterAgent(llm=ChatOpenAI())
)

final_email = email_drafting_process.run(guest_name, podcast_ethos)
print(final_email)

crew = Crew(processes=[email_drafting_process])
crew.run()