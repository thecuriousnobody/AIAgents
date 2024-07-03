import os
import sys
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_anthropic import ChatAnthropic
from langchain.agents import Tool
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from anthropic import APIStatusError
import time

os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

# Initialize tools and models
search_tool = DuckDuckGoSearchRun()
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

search_tool_wrapped = Tool(
    name="Internet Search",
    func=search_tool.run,
    description="Useful for finding information about people, their work, and current events. Input should be a search query."
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
    return crew.kickoff()

def create_information_gatherer_agent():
    return Agent(
        role="Information Gatherer",
        goal="Find comprehensive background information about the podcast guest",
        backstory="You are an expert researcher capable of finding accurate and relevant information about individuals from various online sources.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool_wrapped]
    )

def create_social_media_analyzer_agent():
    return Agent(
        role="Social Media Analyzer",
        goal="Analyze the guest's public social media presence for insights into their perspectives and interests",
        backstory="You are a social media expert who can extract meaningful insights from public social media profiles and posts.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool_wrapped]
    )

def create_publication_reviewer_agent():
    return Agent(
        role="Publication Reviewer",
        goal="Find and analyze published works by the guest to understand their expertise and viewpoints",
        backstory="You are a literary analyst and research expert capable of finding and summarizing key points from an individual's publications.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool_wrapped]
    )

def create_sentiment_analyzer_agent():
    return Agent(
        role="Sentiment Analyzer",
        goal="Analyze the overall tone and perspective of the guest's public content",
        backstory="You are an expert in sentiment analysis and can discern underlying tones, biases, and perspectives from written content.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def create_insight_synthesizer_agent():
    return Agent(
        role="Insight Synthesizer",
        goal="Combine all gathered information to create a concise and insightful profile of the guest",
        backstory="You are a master of synthesis, capable of distilling complex information into clear, actionable insights for podcast preparation.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

def gather_information_task(agent, guest_name, guest_designation):
    return Task(
        description=f"Research and gather comprehensive background information about {guest_name}, who is a {guest_designation}. Focus on their career, major achievements, areas of expertise, and any recent notable activities or statements.",
        agent=agent,
        expected_output="A detailed summary of the guest's background, career, and notable achievements."
    )

def analyze_social_media_task(agent, guest_name):
    return Task(
        description=f"Analyze the public social media presence of {guest_name}. Look for patterns in their posts, topics they frequently discuss, and any strong opinions or interests they express. Focus on professional platforms like LinkedIn and Twitter if available.",
        agent=agent,
        expected_output="A summary of key insights from the guest's social media presence, including main topics of interest and any notable perspectives."
    )

def review_publications_task(agent, guest_name):
    return Task(
        description=f"Find and review any significant publications, articles, or papers by {guest_name}. Summarize their key contributions and the main themes in their work.",
        agent=agent,
        expected_output="A list of notable publications by the guest and a summary of their key ideas and contributions to their field."
    )

def analyze_sentiment_task(agent, guest_name, gathered_info):
    return Task(
        description=f"Analyze the overall tone and perspective in the public content of {guest_name} based on the following information:\n\n{gathered_info}\n\nIdentify any consistent themes, potential biases, or unique viewpoints.",
        agent=agent,
        expected_output="An analysis of the guest's overall tone, perspective, and any notable biases or unique viewpoints identified in their public content."
    )

def synthesize_insights_task(agent, all_info):
    return Task(
        description=f"Synthesize all the gathered information into a concise profile that would be useful for podcast preparation. Include key points about the guest's background, expertise, perspectives, and potential areas of interest for discussion. Here's the information to synthesize:\n\n{all_info}",
        agent=agent,
        expected_output="A concise profile of the guest with key insights and potential areas for discussion during the podcast."
    )

def main(guest_name, guest_designation, output_file_path):
    info_gatherer = create_information_gatherer_agent()
    social_analyzer = create_social_media_analyzer_agent()
    publication_reviewer = create_publication_reviewer_agent()
    sentiment_analyzer = create_sentiment_analyzer_agent()
    insight_synthesizer = create_insight_synthesizer_agent()

    # Step 1: Gather Information
    gather_task = gather_information_task(info_gatherer, guest_name, guest_designation)
    gather_crew = Crew(agents=[info_gatherer], tasks=[gather_task], verbose=2, process=Process.sequential)
    gathered_info = kickoff_crew(gather_crew)

    # Step 2: Analyze Social Media
    social_task = analyze_social_media_task(social_analyzer, guest_name)
    social_crew = Crew(agents=[social_analyzer], tasks=[social_task], verbose=2, process=Process.sequential)
    social_insights = kickoff_crew(social_crew)

    # Step 3: Review Publications
    publication_task = review_publications_task(publication_reviewer, guest_name)
    publication_crew = Crew(agents=[publication_reviewer], tasks=[publication_task], verbose=2, process=Process.sequential)
    publication_insights = kickoff_crew(publication_crew)

    # Step 4: Analyze Sentiment
    all_gathered_info = f"{gathered_info}\n\n{social_insights}\n\n{publication_insights}"
    sentiment_task = analyze_sentiment_task(sentiment_analyzer, guest_name, all_gathered_info)
    sentiment_crew = Crew(agents=[sentiment_analyzer], tasks=[sentiment_task], verbose=2, process=Process.sequential)
    sentiment_analysis = kickoff_crew(sentiment_crew)

    # Step 5: Synthesize Insights
    all_info = f"{all_gathered_info}\n\n{sentiment_analysis}"
    synthesize_task = synthesize_insights_task(insight_synthesizer, all_info)
    synthesize_crew = Crew(agents=[insight_synthesizer], tasks=[synthesize_task], verbose=2, process=Process.sequential)
    final_profile = kickoff_crew(synthesize_crew)

    # Write the final profile to a file
    with open(output_file_path, 'a') as f:
        f.write(f"\n\n--- Guest Profile: {guest_name} ({guest_designation}) ---\n\n")
        f.write(final_profile)

    print(f"Guest profile for {guest_name} has been written to {output_file_path}")

if __name__ == "__main__":
    # guest_name = input("Enter the guest's name: ")
    # guest_designation = input("Enter the guest's designation: ")
    guest_name = "Dr. Kiran Garimella"
    guest_designation = "ASSISTANT PROFESSOR OF LIBRARY AND INFORMATION SCIENCE, Rutgers University"
    output_file = input("Enter the path for the output file: ")
    main(guest_name, guest_designation, output_file)