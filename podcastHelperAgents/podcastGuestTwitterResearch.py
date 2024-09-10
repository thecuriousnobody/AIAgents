import os
import sys
from pprint import pprint
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
# Add the parent directory of 'usefulTools' to the Python path
from pprint import pprint
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import os
import sys
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from usefulTools.search_tools import google_twitter_tool
from usefulTools.llm_repository import ClaudeSonnet
# Add the parent directory to sys.path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set up API keys
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

# Define agents
tweet_collector = Agent(
    role='Tweet Collector',
    goal='Collect and compile up to 200 relevant tweets from the target person',
    backstory="You are an expert in finding and collecting the most relevant and interesting tweets from a given person's Twitter profile. You're thorough and aim to gather a comprehensive set of up to 200 tweets for analysis.",
    verbose=True,
    allow_delegation=False,
    tools=[google_twitter_tool],
    llm=ClaudeSonnet
)


tweet_analyzer = Agent(
    role='Tweet Analyzer',
    goal='Analyze collected tweets and distill interesting insights and potential conversation topics',
    backstory="You are a skilled analyst capable of extracting meaningful insights and identifying potential conversation starters from a set of tweets.",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet
)

content_organizer = Agent(
    role='Content Organizer',
    goal='Organize and quality check the analyzed tweets, identifying the most promising conversation starters for the Idea Sandbox podcast',
    backstory="You are an expert in content curation and organization, with a keen eye for identifying compelling topics that would make for engaging podcast discussions.",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet
)

# Define tasks
def collect_tweets_task(person):
    return Task(
        description=f"Search for and collect up to 200 relevant and interesting tweets from or about {person}'s Twitter profile. Focus on tweets that reveal their thoughts, interests, and potential areas of expertise. Aim to gather a diverse and comprehensive collection.",
        agent=tweet_collector,
        expected_output="A comprehensive list of up to 200 relevant tweets, including the tweet content, date, and any notable metrics (likes, retweets, etc.). If fewer than 200 tweets are found, explain why.",
    )

def analyze_tweets_task(collect_task):
    return Task(
        description="Analyze the collected tweets to identify recurring themes, unique perspectives, and potential conversation starters. Look for tweets that could lead to engaging discussions on the Idea Sandbox podcast. Given the larger number of tweets, focus on identifying the most significant patterns and standout content.",
        agent=tweet_analyzer,
        expected_output="A comprehensive analysis of the tweets, including: 1) A list of key recurring themes or topics, 2) At least 10 specific insights derived from the tweets, 3) A selection of 15-20 standout tweets that are particularly interesting or conversation-worthy, with brief explanations of their significance.",
        context=[collect_task]
    )

def organize_content_task(analyze_task):
    return Task(
        description="Review the analyzed tweets and insights. Organize them into clear categories or themes. Identify and prioritize the most promising conversation starters for the Idea Sandbox podcast. Ensure the selected topics are diverse, engaging, and aligned with the podcast's focus on innovative ideas.",
        agent=content_organizer,
        expected_output="A structured document outlining the top conversation starters derived from the person's tweets, organized by theme. Include specific tweets that support each topic and a brief explanation of why each would make for an engaging podcast discussion.",
        context=[analyze_task]
    )

# Function to run the Twitter analysis process
def analyze_twitter_content(person):
    print(f"Starting Twitter analysis for: {person}")
    
    # Create tasks
    collect_task = collect_tweets_task(person)
    analyze_task = analyze_tweets_task(collect_task)
    organize_task = organize_content_task(analyze_task)
    
    # Create crew
    twitter_analysis_crew = Crew(
        agents=[tweet_collector, tweet_analyzer, content_organizer],
        tasks=[collect_task, analyze_task, organize_task],
        verbose=True,
        process=Process.sequential
    )
    
    # Run the crew
    result = twitter_analysis_crew.kickoff(inputs={"person": person})
    return result

# Example usage
if __name__ == "__main__":
    target_person = input("Enter the name of the person to analyze on Twitter: ")
    analysis_result = analyze_twitter_content(target_person)
    print("\nTwitter Analysis Results:")
    print(analysis_result)

    # Save the results to a file
    with open(f"{target_person}_twitter_analysis.txt", "w") as file:
        file.write(analysis_result)
    print(f"\nResults saved to {target_person}_twitter_analysis.txt")