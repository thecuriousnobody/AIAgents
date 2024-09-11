import os
import sys
from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import SerpAPIWrapper
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import re
import random
import textwrap

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")

search = SerpAPIWrapper()
search_tool = Tool(
    name="Internet Search",
    func=search.run,
    description="Useful for finding current data and information to support blog arguments."
)

def improve_language_authenticity(text):
    ai_word_alternatives = {
        "tapestry": ["mix", "blend", "combination", "array"],
        "plethora": ["abundance", "wealth", "lot", "many"],
        "myriad": ["countless", "numerous", "many", "diverse"],
        "paradigm": ["model", "pattern", "example", "standard"],
        "synergy": ["cooperation", "teamwork", "combined effect"],
        "leverage": ["use", "utilize", "take advantage of"],
        "robust": ["strong", "sturdy", "powerful", "healthy"],
        "holistic": ["comprehensive", "all-encompassing", "complete"],
        "innovative": ["new", "novel", "creative", "original"],
        "cutting-edge": ["advanced", "leading", "modern", "state-of-the-art"],
        "seamless": ["smooth", "effortless", "uninterrupted"],
        "optimize": ["improve", "enhance", "perfect", "refine"],
        "streamline": ["simplify", "make efficient", "reorganize"],
        "ecosystem": ["environment", "community", "network"],
        "empower": ["enable", "allow", "equip", "give power to"],
        "revolutionize": ["transform", "change radically", "overhaul"]
    }
    
    def replace_word(match):
        word = match.group(0)
        alternatives = ai_word_alternatives.get(word.lower(), [word])
        return random.choice(alternatives)
    
    for word in ai_word_alternatives.keys():
        text = re.sub(r'\b' + word + r'\b', replace_word, text, flags=re.IGNORECASE)
    
    return text

def process_content_in_chunks(blog_content, chunk_size=2000):
    chunks = textwrap.wrap(blog_content, chunk_size, break_long_words=False, replace_whitespace=False)
    processed_chunks = []

    for chunk in chunks:
        processed_chunk = process_chunk(chunk)
        processed_chunks.append(processed_chunk)

    return "\n\n".join(processed_chunks)


def process_chunk(chunk):

    return chunk
    
def create_agents_and_tasks(blog_content):

    content_organizer = Agent(
        role="Content Organizer",
        goal="Organize the rough draft into coherent, manageable paragraphs.",
        backstory="You are an expert at structuring content for clarity and flow, focusing on logical progression of ideas.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    data_researcher = Agent(
        role="Data Researcher",
        goal="Find relevant data and information to support the blog's arguments.",
        backstory="You are skilled at finding and integrating factual, impactful data into narratives, focusing on credible sources.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool]
    )

    content_enhancer = Agent(
        role="Content Enhancer",
        goal="Integrate researched data into the organized content without altering the original voice or adding commentary.",
        backstory="You are adept at seamlessly incorporating factual information into existing text while maintaining the original tone and structure.",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

    organize_content_task = Task(
        description=f"""Organize the following blog content into clear, coherent paragraphs:

        {blog_content}

        Focus on logical flow and progression of ideas. Do not add any new content or alter the original voice.""",
        agent=content_organizer,
        expected_output="The original blog content organized into clear, manageable paragraphs."
    )

    research_data_task = Task(
        description=f"""Based on the organized blog content, research and find relevant data, statistics, or examples that support the main arguments. Focus on credible, current information.""",
        agent=data_researcher,
        expected_output="A list of relevant data points, statistics, and examples with their sources.",
        context=[organize_content_task]
    )

    enhance_content_task = Task(
        description="""Integrate the researched data into the organized blog content. 
        Insert the information where it's most relevant, without altering the original voice or adding commentary. 
        The goal is to support the existing arguments with facts, not to change the content's tone or structure.""",
        agent=content_enhancer,
        expected_output="The organized blog content with relevant data seamlessly integrated.",
        context=[organize_content_task, research_data_task]
    )

    return [content_organizer, data_researcher, content_enhancer], [organize_content_task, research_data_task, enhance_content_task]
    


def run_content_enhancer(blog_content):
    # First, process the content in chunks
    processed_content = process_content_in_chunks(blog_content)

    # Then, apply your existing enhancement logic
    agents, tasks = create_agents_and_tasks(processed_content)

    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,
        process=Process.sequential
    )

    return output
    output = crew.kickoff()

if __name__ == "__main__":

    rough_draft_file = input("Enter the filename for your rough draft blog post: ")

    with open(rough_draft_file, "r") as file:
        blog_content = file.read()

    enhanced_content = run_content_enhancer(blog_content)
    
    print("Enhanced Content (Ready for your personal refinement):")
    print(enhanced_content)

    base_name = os.path.splitext(os.path.basename(rough_draft_file))[0]
    file_name = f"enhanced_{base_name}_.txt"
    directory = "/Users/rajeevkumar/Documents/TISB/enhancedBlogs"
    full_path = os.path.join(directory, file_name)  

    with open(full_path, "w") as file:
        file.write(enhanced_content)

    # Verify completeness
    with open(full_path, "r") as file:
        final_content = file.read()
        if final_content.endswith(blog_content[-100:]):
            print("Content processing complete. All text has been included.")
        else:
            print("Warning: Some content may have been truncated. Please check the output.")