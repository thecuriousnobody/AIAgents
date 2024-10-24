import speech_recognition as sr
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
import os
import sys
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.search_tools import search_tool, youtube_tool
from usefulTools.llm_repository import ClaudeSonnet

class AIJamieAssistant:
    def __init__(self):
        # Initialize the recognizer
        self.recognizer = sr.Recognizer()
        # Store microphone instance
        self.microphone = sr.Microphone()
        
        # Adjust microphone settings once at startup
        with self.microphone as source:
            print("Adjusting for ambient noise. Please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            # Set dynamic energy threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 4000  # Adjust if needed
        
        self.confirmation_phrases = [
            "look this up", "search this", "find this", "get this", 
            "go ahead", "yes please", "please", "do it", "that's it",
            "thanks", "thank you", "okay", "yep", "yeah"
        ]
        self.setup_agents()

    def listen_for_speech(self, timeout=None):
        """Helper function to handle one instance of listening."""
        with self.microphone as source:
            try:
                print(".", end="", flush=True)  # Visual feedback
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio).lower()
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                print("\n🔄 Network error, retrying...")
                return None
            except Exception as e:
                print(f"\n⚠️ Error during listening: {e}")
                return None

    def listen_for_command(self):
        """Main listening function with proper error handling."""
        print("\nListening for 'Jamie'...")
        
        while True:
            initial_text = self.listen_for_speech()
            
            if initial_text and "jamie" in initial_text:
                command = initial_text.split("jamie", 1)[1].strip()
                print(f"\n👂 Heard command: '{command}'")
                print("Waiting for confirmation... (say 'look this up' or similar)")
                
                # Listen for confirmation with timeout
                confirmation_attempts = 0
                max_attempts = 3
                
                while confirmation_attempts < max_attempts:
                    confirmation = self.listen_for_speech(timeout=5)
                    if confirmation:
                        if any(phrase in confirmation for phrase in self.confirmation_phrases):
                            print(f"✓ Command confirmed!")
                            return command
                        else:
                            print(f"Heard: '{confirmation}' - Not a confirmation phrase")
                    
                    confirmation_attempts += 1
                
                print("\nNo confirmation received. Please try again.")
                return None
            
            time.sleep(0.1)  # Prevent CPU overload

    def setup_agents(self):
        self.query_analyzer = Agent(
            role="Query Analyzer",
            goal="Analyze and refine voice commands into searchable queries",
            backstory="Expert at understanding context from podcast conversations and transforming casual requests into precise research queries.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )

        self.information_finder = Agent(
            role="Information Finder",
            goal="Find relevant and up-to-date information based on the analyzed query",
            backstory="Skilled researcher who can quickly find accurate and relevant information from various online sources.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[search_tool, youtube_tool]
        )

        self.content_curator = Agent(
            role="Content Curator",
            goal="Format and present the found information in an easily digestible way",
            backstory="Expert at organizing information and presenting it in a clear, concise manner for live podcast discussions.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )

    def process_command(self, command):
        tasks = self.create_tasks(command)
        crew = Crew(
            agents=[self.query_analyzer, self.information_finder, self.content_curator],
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        return crew.kickoff()

    def create_tasks(self, voice_command):
        # Create tasks similar to podcastGuestFinderWithNicheProvided.py
        analyze_task = Task(
            description=f"""Analyze this voice command and transform it into a precise search query:
            Command: {voice_command}
            
            Consider:
            1. Key terms and concepts mentioned
            2. Type of information requested (statistics, facts, examples, etc.)
            3. Any specific time periods or constraints mentioned
            4. The context of a live podcast discussion
            
            Format the output as a clear search query.""",
            agent=self.query_analyzer,
            expected_output="A refined, searchable query based on the voice command."
        )

        research_task = Task(
            description="""Using the refined query, search for relevant information.
            
            Focus on:
            1. Recent and verified information
            2. Reputable sources
            3. Specific data points that can be quickly cited
            4. Content that includes URLs for verification
            
            Include both the information and source URLs.""",
            agent=self.information_finder,
            expected_output="Researched information with source URLs",
            context=[analyze_task]
        )

        curate_task = Task(
            description="""Format the research results for live podcast presentation.
            
            Requirements:
            1. Clear, concise presentation of key points
            2. Numbered list of clickable source URLs
            3. Easy-to-read statistics or facts
            4. Brief summaries of key findings
            
            Format for quick reading and reference during live discussion.""",
            agent=self.content_curator,
            expected_output="Formatted information with clickable links",
            context=[research_task]
        )

        return [analyze_task, research_task, curate_task]
    def run(self):
        """Main run loop with improved error handling."""
        print("\n=== AI Jamie Initialized ===")
        print("🎙️ I'm your podcast research assistant!")
        print("Say 'Jamie' followed by your request")
        print("Then confirm with phrases like 'look this up' or 'yes'")
        
        while True:
            try:
                command = self.listen_for_command()
                
                if command:
                    print(f"\n🔍 Processing: '{command}'")
                    try:
                        results = self.process_command(command)
                        print("\n=== Results ===")
                        print(results)
                        
                        # Extract and display URLs
                        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', results)
                        if urls:
                            print("\n🔗 Relevant Links:")
                            for i, url in enumerate(urls, 1):
                                print(f"{i}. {url}")
                        
                        print("\n👂 Ready for next command!")
                        
                    except Exception as e:
                        print(f"\n⚠️ Error processing request: {e}")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! AI Jamie shutting down.")
                break
            except Exception as e:
                print(f"\n⚠️ Error: {e}")
                print("Restarting listening system...")
                time.sleep(1)
                continue

if __name__ == "__main__":
    try:
        jamie = AIJamieAssistant()
        jamie.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! AI Jamie shutting down.")
    except Exception as e:
        print(f"\nFatal error: {e}")

