from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import sys
import os
from usefulTools.search_tools import search_tool,youtube_tool
from usefulTools.llm_repository import ClaudeSonnet 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
# Assuming you have a config.py file with your API keys
import config

os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY


def create_research_agent(guest_name, profession):
    return Agent(
        role="Expert Research Agent",
        goal=f"Conduct comprehensive research on {guest_name}, a {profession}, to understand their expertise, work, and recent activities.",
        backstory=f"""You are an elite researcher with a PhD in Information Science and years of experience 
        in digital forensics and data mining. Your expertise lies in uncovering comprehensive information 
        about individuals across various fields, with a particular focus on those making significant 
        contributions to their areas of expertise.

        Your current mission is to gather in-depth data on {guest_name}, a distinguished professional 
        in the field of {profession}. You possess an unparalleled ability to craft precise search queries, 
        navigate through vast amounts of online information, and extract valuable insights from both 
        academic and popular sources.

        Your key strengths include:
        1. Advanced search techniques using boolean operators and specialized databases
        2. Critical evaluation of source credibility and bias
        3. Cross-referencing information from multiple sources to ensure accuracy
        4. Identifying patterns and connections in seemingly unrelated data
        5. Synthesizing complex information into clear, concise summaries

        For this task, your primary objectives are to:
        1. Uncover the full scope of {guest_name}'s professional background and expertise
        2. Identify their most significant contributions to the field of {profession}
        3. Find recent publications, talks, or projects they've been involved with
        4. Discover any controversial or cutting-edge ideas they've proposed
        5. Locate any public content (articles, interviews, lectures) that showcases their thoughts and personality

        You have a keen eye for detail and a talent for reading between the lines to uncover hidden gems 
        of information. Your goal is to provide a comprehensive dossier that will serve as the foundation 
        for an engaging and insightful podcast interview.""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet,
        tools=[search_tool, youtube_tool]
    )

def create_question_formulation_agent():
    return Agent(
        role="Master Interview Strategist",
        goal="Craft a set of compelling, insightful questions that will lead to a thought-provoking and engaging podcast interview.",
        backstory="""You are a renowned journalist and master interviewer with decades of experience 
        conducting in-depth conversations with thought leaders, innovators, and experts across various fields. 
        Your interviews have won numerous awards and are known for their ability to uncover new insights, 
        challenge conventional thinking, and inspire audiences.

        Your expertise includes:
        1. Analyzing complex research and distilling it into engaging conversation topics
        2. Crafting questions that encourage deep reflection and novel responses
        3. Balancing between open-ended inquiries and specific, targeted questions
        4. Identifying potential areas of controversy or innovation to explore
        5. Structuring a conversation to build rapport and gradually delve into more challenging topics

        For this task, your objectives are to:
        1. Thoroughly analyze the research provided on the guest
        2. Develop a mix of questions that cover the guest's background, expertise, and recent work
        3. Create open-ended questions that encourage storytelling and detailed explanations
        4. Formulate specific questions aimed at uncovering practical insights and actionable information
        5. Design questions that challenge the guest to consider new perspectives or future implications of their work
        6. Incorporate questions that relate the guest's work to broader societal issues or trends

        Your questions should be tailored to align with the "Idea Sandbox" podcast's ethos of exploring 
        transformative ideas and their practical applications. Aim to create a question set that will not only 
        educate the audience but also inspire them to think critically and engage more deeply with the subject matter.

        Remember, your goal is not just to extract information, but to facilitate a conversation that brings 
        out the guest's passion, challenges their assumptions, and potentially leads to new realizations or 
        ideas during the interview itself.""",
        verbose=True,
        allow_delegation=False,
        llm=ClaudeSonnet
    )

def create_research_task(research_agent, guest_name, profession):
    return Task(
        description=f"""Conduct an extensive and meticulous research on {guest_name}, a {profession}. 
        Your research should cover:
        1. Their professional background and key career milestones
        2. Main areas of expertise and significant contributions to their field
        3. Recent projects, publications, or public statements
        4. Any controversial or innovative ideas they've proposed
        5. Their impact on the field of {profession} and potential future directions of their work
        
        Provide a comprehensive summary of your findings, organized in a clear and logical manner. 
        Include any interesting anecdotes or lesser-known facts that could add depth to the interview.""",
        agent=research_agent
    )

def create_question_formulation_task(question_agent, research_output):
    return Task(
        description=f"""Based on the following research, formulate a set of 10-15 engaging questions for 
        the podcast interview. Your questions should:
        1. Cover the guest's background, major works, and recent activities
        2. Include both open-ended questions to encourage discussion and specific questions to uncover new, practical information
        3. Challenge the guest to consider new perspectives or implications of their work
        4. Relate the guest's expertise to broader societal issues or trends
        5. Aim to uncover information that goes beyond what's readily available in public sources
        
        Structure your questions to create a natural flow of conversation, starting with broader topics 
        and gradually diving into more specific or challenging areas. 
        
        Research to base your questions on: {research_output}""",
        agent=question_agent
    )

# The main function and the rest of the code remain the same as in the previous version
def main(guest_name, profession):
    research_agent = create_research_agent(guest_name, profession)
    question_agent = create_question_formulation_agent()

    initial_research_task = Task(
        description=f"Conduct initial research on {guest_name}, a {profession}.",
        agent=research_agent,
        expected_output="A comprehensive summary of the initial research findings on the guest's background, work, and recent activities."
    )

    initial_question_task = Task(
        description="Formulate initial questions based on the research.",
        agent=question_agent,
        expected_output="A list of 20-30 initial interview questions based on the research findings."
    )

    research_refinement_task = Task(
        description="Refine and expand the research based on the initial questions.",
        agent=research_agent,
        expected_output="An expanded and refined research summary, addressing any gaps identified by the initial questions."
    )

    final_question_task = Task(
        description="Finalize the interview questions based on the refined research.",
        agent=question_agent,
        expected_output="A final list of 20-30 well-crafted interview questions, incorporating insights from the refined research."
    )

    crew = Crew(
        agents=[research_agent, question_agent],
        tasks=[initial_research_task, initial_question_task, research_refinement_task, final_question_task],
        verbose=2,  # Increased verbosity to see more of the process
        process=Process.sequential
    )

    result = crew.kickoff()

    # Write the generated content to a file
    try:
        with open("/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/podcastPrepOron.txt", "w") as file:
            file.write(result)
        print("Output successfully written to podcastPrep.txt")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    guest_name = input("Enter the guest's name: ")
    profession = input("Enter the guest's profession: ")
    main(guest_name, profession)