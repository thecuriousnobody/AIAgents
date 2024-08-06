from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")

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

    topic_generator = Agent(
        role="Indian Bureaucracy Topic Generator",
        goal="Generate specific topics related to Indian bureaucracy, governance challenges, and reform initiatives that would make for engaging and insightful podcast conversations.",
        backstory="You are an expert on Indian governance with a deep understanding of the bureaucratic system, its history, and current challenges. Your job is to identify compelling topics that shed light on the inner workings, issues, and potential reforms of Indian bureaucracy.",
        verbose=False,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    guest_finder = Agent(
        role="Indian Bureaucracy Expert Finder",
        goal="Identify potential guests who can provide informed, candid insights into Indian bureaucracy without fear of reprisal.",
        backstory="You are a well-connected researcher with extensive knowledge of experts in Indian governance. Your task is to find individuals who can speak freely and authoritatively about the challenges and potential reforms in Indian bureaucracy. This includes academics, researchers, authors, former officials, and activists who are not constrained by current government positions.",
        verbose=False,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    generate_topics = Task(
        description="Generate a list of specific, compelling topics related to Indian bureaucracy, focusing on current challenges, historical context, and potential reforms. Consider issues like corruption, efficiency, technology adoption, and the impact on citizens.",
        agent=topic_generator,
        expected_output="A list of 10-15 specific topics related to Indian bureaucracy that would make for engaging and insightful podcast discussions.",
    )

    find_potential_guests = Task(
        description="For each topic generated, identify 2-3 potential guests who can provide informed, candid insights. Focus on academics, researchers, authors, former officials, and activists who are not constrained by current government positions and can speak freely about the challenges and potential reforms in Indian bureaucracy.",
        agent=guest_finder,
        expected_output="A list of potential guests for each topic, including their names, affiliations, relevant expertise or publications, and a brief explanation of why they would be valuable contributors to the discussion.",
    )

    crew = Crew(
        agents=[topic_generator, guest_finder],
        tasks=[generate_topics, find_potential_guests],
        verbose=1,
        process=Process.sequential
    )

    output = crew.kickoff()
    print(output)

    # Write the generated content to a file
    try:
        with open("/Users/rajeevkumar/Documents/BrosRiffn/indianBureaucracyExperts.txt", "w") as file:
            file.write(output)
        print("Output successfully written to indianBureaucracyExperts.txt")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")