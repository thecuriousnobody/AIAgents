
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import config

# topic = "Shame, scolding and othering in Indian society, examining cultural Norms of Discipline and communication in Indian Society and Beyond"  # Change this variable to the desired topic
topic = "The lives of extras in Bollywood, Karnataka Kollywood, TollyWood Telugu Cinema, Tamil Movie Land. What is their background, and what kind of a living do they make?"
num_guests = 5

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

if __name__ == '__main__':
    llm = ChatOpenAI(
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
        # model_name="mixtral-8x7b-32768"
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
        goal=f"Find potential guests for the Idea Sandbox podcast who are legitimate experts doing verifiable and interesting work related to {topic}.",
        backstory=f"You are an AI assistant whose job is to find potential guests for the Idea Sandbox podcast. Look for people who are recognized experts in {topic}, have published work or have been featured in reputable sources, and would likely be willing to appear on a podcast with a low subscriber base and viewership. Make sure to include the full name, affiliation, and a brief description of their relevant work for each potential guest in your suggestions.",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )
    guest_critic = Agent(
        role="Guest Critic",
        goal=f"Critique the potential guests suggested by the Guest Pooler based on their alignment with the mission of the Idea Sandbox podcast, their verifiable expertise in {topic}, and their legitimacy as recognized experts in the field.",
        backstory=f"You are an AI assistant whose job is to critique the potential guests suggested by the Guest Pooler. [...] When evaluating potential guests, consider the following criteria: 1. Are they recognized experts in {topic} with verifiable credentials, such as academic affiliations, published work, or features in reputable sources? 2. Is their work relevant to the podcast's mission and does it demonstrate expertise in {topic}? 3. Are they legitimate experts in the field, and not just individuals with unverified claims or limited credibility? Include the full name, affiliation, and a brief description of their relevant work for each potential guest in your critique.",
        verbose=False,
        llm=llm
    )

    pool_guests = Task(
        description=f"Find potential guests for the Idea Sandbox podcast who are legitimate experts doing verifiable and interesting work related to {topic}.",
        agent=guest_pooler,
        expected_output="A list of potential guests for the Idea Sandbox podcast, including their full name, affiliation, a brief description of their relevant work, and contact information (email or social media handle).",
    )

    critique_guests = Task(
        description=f"Critique the potential guests suggested by the Guest Pooler based on their alignment with the mission of the Idea Sandbox podcast, their verifiable expertise in {topic}, and their legitimacy as recognized experts in the field.",
        agent=guest_critic,
        expected_output=f"A list of potential guests that align with the mission of the Idea Sandbox podcast, have verifiable expertise in {topic}, and are legitimate experts in the field, including their full name, affiliation, and a brief description of their relevant work and contact information..",
    )


    crew = Crew(
        agents=[guest_pooler, guest_critic],
        tasks=[pool_guests, critique_guests],
        verbose=1,
        process=Process.sequential
    )

    output = crew.kickoff()
    print(output)

    # Extract the potential guest information from the monitor's output
    guest_list = output.split("\n")[:num_guests]
    # __all__ = ['topic','guest_list']
    # Write guest_list and topic to a file
    try:
        with open("/Users/rajeevkumar/Documents/TISB Stuff/guestPrep/guest_list.txt", "w") as file:
            file.write(f"topic={topic}\n")
            file.write("guest_list=[")
            file.write(",".join(f'"{guest}"' for guest in guest_list))
            file.write("]")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

