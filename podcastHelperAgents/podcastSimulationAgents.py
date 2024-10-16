import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from crewai_tools import Tool

# Add the parent directory to sys.path to import config and tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import search_api_tool
from usefulTools.llm_repository import ClaudeSonnet

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Set up API keys
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPAPI_API_KEY"] = config.SERPAPI_API_KEY

# Initialize AI model
llm = ClaudeSonnet

# Load configuration
def load_config():
    config_path = 'podcastHelperAgents/podcast_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    logging.warning(f"Config file not found at {config_path}. Using default values.")
    return {
        "interjection_frequency": 3,
        "summary_length": 10,
        "save_directory": "podcast_simulations"
    }

CONFIG = load_config()

class PodcastSimulationSystem:
    def __init__(self, guest_name, topic):
        self.guest_name = guest_name
        self.topic = topic
        self.conversation_history = []
        self.turn_count = 0

        # Define agents
        self.guest_simulator = Agent(
            role=f"Guest: {guest_name}",
            goal=f"Simulate the speaking style, knowledge, and opinions of {guest_name}, an expert in {topic}",
            backstory=f"You are {guest_name}, an expert in {topic}. You have extensive knowledge and strong opinions based on your experience and research.",
            verbose=True,
            allow_delegation=False,
            tools=[search_api_tool],
            llm=llm
        )

        self.historical_context_agent = Agent(
            role="Historical Context Provider",
            goal=f"Provide relevant historical context related to {topic}",
            backstory=f"You are an expert historian specializing in {topic}. Your role is to provide historical background that enriches the conversation.",
            verbose=True,
            allow_delegation=False,
            tools=[search_api_tool],
            llm=llm
        )

        self.current_affairs_agent = Agent(
            role="Current Affairs Expert",
            goal=f"Bring up recent developments and news related to {topic}",
            backstory=f"You are a journalist specializing in current events related to {topic}. Your role is to keep the conversation up-to-date with the latest developments.",
            verbose=True,
            allow_delegation=False,
            tools=[search_api_tool],
            llm=llm
        )

        self.fact_checker = Agent(
            role="Fact Checker",
            goal="Verify claims and provide additional sources",
            backstory="You are a meticulous fact-checker with a keen eye for accuracy. Your role is to ensure the information discussed is correct and well-sourced.",
            verbose=True,
            allow_delegation=False,
            tools=[search_api_tool],
            llm=llm
        )

        self.conversation_manager = Agent(
            role="Conversation Manager",
            goal="Guide the conversation flow and ensure engagement",
            backstory="You are an experienced podcast host and conversation facilitator. Your role is to keep the discussion on track, interesting, and productive.",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    def create_tasks(self, user_input):
        tasks = [
            Task(
                description=f"Respond to the user's input: '{user_input}' as {self.guest_name}, an expert in {self.topic}. Include relevant web links and citations to support your response.",
                agent=self.guest_simulator,
                expected_output="A well-sourced response from the guest that addresses the user's input, including web links and citations."
            ),
            Task(
                description=f"Fact-check the following statement: '{user_input}'. Provide web links to support your fact-checking.",
                agent=self.fact_checker,
                expected_output="A fact-check report on the user's statement, including verification or corrections, with supporting web links."
            ),
            Task(
                description="Suggest the next direction for the conversation based on the recent exchanges. Include potential topics that could be explored further with relevant sources.",
                agent=self.conversation_manager,
                expected_output="A suggestion for the next topic or question to keep the conversation engaging and on-topic, with potential sources for further exploration."
            )
        ]

        if self.turn_count % CONFIG["interjection_frequency"] == 0:
            tasks.extend([
                Task(
                    description=f"Provide relevant historical context related to the recent conversation about {self.topic}. Include citations from historical papers or reputable sources.",
                    agent=self.historical_context_agent,
                    expected_output="Historical information or context relevant to the current conversation topic, with citations from historical papers or reputable sources."
                ),
                Task(
                    description=f"Bring up recent developments or news related to {self.topic} that are relevant to the conversation. Include links to news articles or research papers.",
                    agent=self.current_affairs_agent,
                    expected_output="Recent news or developments related to the conversation topic, with links to news articles or research papers."
                )
            ])

        return tasks

    def run_conversation(self):
        logging.info(f"Starting podcast simulation with {self.guest_name} about {self.topic}")
        print(f"Welcome to the podcast simulation with {self.guest_name} about {self.topic}.")
        print("Commands: 'exit' to end, 'switch' to change guest/topic, 'summary' for a summary, 'export' to save as script, 'save' to save progress.")

        try:
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    logging.info("User requested to exit the simulation")
                    break
                elif user_input.lower() == 'switch':
                    self.guest_name = input("Enter new guest name: ")
                    self.topic = input("Enter new topic: ")
                    self.guest_simulator.role = f"Guest: {self.guest_name}"
                    self.guest_simulator.goal = f"Simulate the speaking style, knowledge, and opinions of {self.guest_name}, an expert in {self.topic}"
                    self.guest_simulator.backstory = f"You are {self.guest_name}, an expert in {self.topic}. You have extensive knowledge and strong opinions based on your experience and research."
                    logging.info(f"Switched to conversation with {self.guest_name} about {self.topic}")
                    print(f"Switched to conversation with {self.guest_name} about {self.topic}")
                    continue
                elif user_input.lower() == 'summary':
                    summary = self.generate_summary()
                    print(f"\nConversation Summary:\n{summary}\n")
                    continue
                elif user_input.lower() == 'export':
                    self.export_as_script()
                    continue
                elif user_input.lower() == 'save':
                    self.save_conversation()
                    continue

                self.conversation_history.append(f"User: {user_input}")

                tasks = self.create_tasks(user_input)
                crew = Crew(
                    agents=[self.guest_simulator, self.fact_checker, self.conversation_manager, 
                            self.historical_context_agent, self.current_affairs_agent],
                    tasks=tasks,
                    verbose=True,
                    process=Process.sequential
                )

                try:
                    result = crew.kickoff()
                    print(result)
                    self.conversation_history.append(str(result))  # Convert CrewOutput to string
                    self.turn_count += 1
                except Exception as e:
                    logging.error(f"Error during crew execution: {str(e)}")
                    print("An error occurred while processing your input. Please try again.")

        except KeyboardInterrupt:
            logging.info("User interrupted the simulation")
            print("\nSimulation interrupted by user.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            print(f"An unexpected error occurred: {str(e)}")
        finally:
            self.save_conversation()
            summary = self.generate_summary()
            print(f"\nFinal Conversation Summary:\n{summary}")
            self.export_as_script()
            logging.info("Podcast simulation ended")
            print("Thank you for participating in the podcast simulation.")

    def generate_summary(self):
        logging.info("Generating conversation summary")
        summary_task = Task(
            description=f"Summarize the following podcast conversation with {self.guest_name} about {self.topic}. Include key points discussed and any significant sources or citations mentioned:\n\n" + 
                        "\n".join(self.conversation_history[-CONFIG["summary_length"]:]),
            agent=self.conversation_manager,
            expected_output="A concise summary of the recent conversation highlights, key points discussed, and significant sources or citations mentioned."
        )
        summary_crew = Crew(
            agents=[self.conversation_manager],
            tasks=[summary_task],
            verbose=True,
            process=Process.sequential
        )
        return str(summary_crew.kickoff())  # Convert CrewOutput to string

    def export_as_script(self):
        logging.info("Exporting conversation as podcast script")
        export_task = Task(
            description=f"Convert the following podcast conversation with {self.guest_name} about {self.topic} into a properly formatted podcast script. Include all sources, citations, and web links mentioned in the conversation:\n\n" + 
                        "\n".join(self.conversation_history),
            agent=self.conversation_manager,
            expected_output="A formatted podcast script based on the conversation history, including all sources, citations, and web links mentioned."
        )
        export_crew = Crew(
            agents=[self.conversation_manager],
            tasks=[export_task],
            verbose=True,
            process=Process.sequential
        )
        script = str(export_crew.kickoff())  # Convert CrewOutput to string
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{CONFIG['save_directory']}/podcast_script_{self.guest_name}_{self.topic}_{timestamp}.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(script)
        logging.info(f"Podcast script exported to {filename}")
        print(f"Podcast script exported to {filename}")

    def save_conversation(self):
        logging.info("Saving conversation history")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{CONFIG['save_directory']}/podcast_simulation_{self.guest_name}_{self.topic}_{timestamp}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        logging.info(f"Conversation saved to {filename}")
        print(f"Conversation saved to {filename}")

# Example usage
if __name__ == "__main__":
    try:
        guest_name = input("Enter the guest's name: ")
        topic = input("Enter the podcast topic: ")
        simulation = PodcastSimulationSystem(guest_name, topic)
        simulation.run_conversation()
    except Exception as e:
        logging.error(f"An error occurred while running the simulation: {str(e)}")
        print(f"An error occurred while running the simulation: {str(e)}")
