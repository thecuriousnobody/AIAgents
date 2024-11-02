from crewai import Agent, Task, Crew, Process
import os
import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))  
import re
import time
from typing import Optional, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
print("Config file being used:", config.__file__)
from usefulTools.search_tools import search_api_tool, youtube_tool
from usefulTools.llm_repository import ClaudeSonnet
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

# Import our modular components
from experimentalJamie.config.audio_config import AudioConfig
from experimentalJamie.config.command_config import CommandConfig
from experimentalJamie.utils.audio_manager import AudioManager
from experimentalJamie.utils.context_manager import ContextManager
from experimentalJamie.utils.state_manager import StateManager, JamieState

class ExperimentalJamie:
    def __init__(self):
        print("Initializing Experimental Jamie...")
        
        try:
            # Debug print for tracking initialization
            print("1. Setting up configurations...")
            self.audio_config = AudioConfig()
            self.command_config = CommandConfig()
            
            print("2. Initializing audio manager...")
            self.audio_manager = AudioManager(self.audio_config)
            
            print("3. Setting up other managers...")
            self.context_manager = ContextManager(self.command_config)
            self.state_manager = StateManager()
            
            print("4. Setting up agents...")
            self.setup_agents()
            
            # Now try to list microphones
            print("\nAvailable Microphones:")
            mics = self.audio_manager.list_microphones()
            for mic in mics:
                print(f"Index: {mic['index']}, Name: {mic['name']}")
                
            print("Initialization complete!")
            
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def setup_agents(self):
        self.query_analyzer = Agent(
            role="Context-Aware Query Analyzer",
            goal="Transform voice commands into precise search queries while maintaining conversational context",
            backstory="Expert at understanding context and nuance in podcast conversations, capable of transforming casual requests into targeted research queries.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )

        self.information_finder = Agent(
            role="Adaptive Information Finder",
            goal="Find relevant information based on conversation context and search mode",
            backstory="Skilled researcher who adapts search depth and focus based on the conversation context and requested detail level.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet,
            tools=[search_api_tool, youtube_tool]
        )

        self.content_curator = Agent(
            role="Dynamic Content Curator",
            goal="Present information in a format optimized for live podcast discussions",
            backstory="Expert at organizing and presenting information for easy consumption during live discussions, with an understanding of timing and flow.",
            verbose=True,
            allow_delegation=False,
            llm=ClaudeSonnet
        )

    def create_contextual_tasks(self, command: str) -> List[Task]:
        # Get relevant context and search mode
        recent_context = self.context_manager.get_recent_context()
        search_mode = self.context_manager.get_search_mode(command)
        
        analyze_task = Task(
            description=f"""Analyze voice command with context:
            Command: {command}
            Recent Context: {recent_context}
            Search Mode: {search_mode['depth']}
            
            Create a search strategy that:
            1. Considers conversation history
            2. Matches the requested depth ({search_mode['depth']})
            3. Maintains topical relevance
            4. Identifies key search terms""",
            agent=self.query_analyzer,
            expected_output="A contextualized search strategy"
        )

        research_task = Task(
            description=f"""Research based on analysis and search mode:
            Mode: {search_mode['depth']}
            Max Sources: {search_mode['max_sources']}
            Timeout: {search_mode['timeout']}
            
            Requirements:
            1. Match depth requirements
            2. Verify source credibility
            3. Include supporting data
            4. Consider context""",
            agent=self.information_finder,
            expected_output="Research results matching specified mode",
            context=[analyze_task]
        )

        curate_task = Task(
            description="""Format findings for live discussion:
            
            Requirements:
            1. Clear structure for quick reading
            2. Highlighted key points
            3. Easily quotable statistics
            4. Accessible source links
            5. Suggested follow-up points""",
            agent=self.content_curator,
            expected_output="Podcast-ready information",
            context=[research_task]
        )

        return [analyze_task, research_task, curate_task]

    def process_command(self, command: str) -> str:
        try:
            self.state_manager.transition_to(JamieState.PROCESSING)
            
            # Create and execute tasks
            tasks = self.create_contextual_tasks(command)
            crew = Crew(
                agents=[self.query_analyzer, self.information_finder, self.content_curator],
                tasks=tasks,
                verbose=True,
                process=Process.sequential
            )
            
            results = crew.kickoff()
            
            # Store in context
            self.context_manager.add_command(command, results)
            
            return results
            
        except Exception as e:
            self.state_manager.transition_to(JamieState.ERROR, {"error": str(e)})
            raise e

    def run(self):
        print("\n=== Experimental Jamie Initialized ===")
        print("🎙️ Setting up audio system...")
        
        self.audio_manager.start_listening()
        print(f"Wake words: {', '.join([self.command_config.WAKE_WORDS['primary']] + self.command_config.WAKE_WORDS['alternates'])}")
        print("Start your request with 'Jamie' and end with 'thanks'")
        print("\n🎤 Listening continuously...")
        
        # Buffer for collecting complete command
        command_buffer = ""
        command_in_progress = False
        
        while True:
            try:
                audio_data = self.audio_manager.get_next_audio()
                if not audio_data:
                    print(".", end="", flush=True)
                    continue

                if self.audio_manager.is_mic_muted(audio_data):
                    print("M", end="", flush=True)
                    continue

                text = self.audio_manager.process_audio(audio_data)
                if text:
                    text = text.lower().strip()
                    print(f"\nDEBUG - Heard: '{text}'")
                    
                    # Check for wake word if not already collecting a command
                    wake_words = [self.command_config.WAKE_WORDS['primary']] + self.command_config.WAKE_WORDS['alternates']
                    
                    if not command_in_progress:
                        if any(wake_word in text for wake_word in wake_words):
                            print("\n🎧 Started listening to command...")
                            command_in_progress = True
                            # Extract the part after wake word
                            for wake_word in wake_words:
                                if wake_word in text:
                                    command_buffer = text.split(wake_word, 1)[1].strip()
                                    break
                    
                    # If we're collecting a command, keep adding to buffer
                    elif command_in_progress:
                        command_buffer += " " + text
                        print(f"DEBUG - Current buffer: '{command_buffer}'")
                        
                        # Check if the command buffer contains "thanks"
                        if "thanks" in command_buffer:
                            # Extract everything before "thanks"
                            final_command = command_buffer.split("thanks")[0].strip()
                            print(f"\n👂 Processing complete command: '{final_command}'")
                            
                            try:
                                results = self.process_command(final_command)
                                print("\n=== Results ===")
                                print(results)
                                
                                # Extract and display URLs
                                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', results)
                                if urls:
                                    print("\n🔗 Sources:")
                                    for i, url in enumerate(urls, 1):
                                        print(f"{i}. {url}")
                                
                            except Exception as e:
                                print(f"\n⚠️ Error processing request: {e}")
                            
                            # Reset for next command
                            command_buffer = ""
                            command_in_progress = False
                            print("\n🎤 Ready for next command...")

                else:
                    print("_", end="", flush=True)
                    
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                self.audio_manager.stop_listening()
                break
            except Exception as e:
                print(f"\n⚠️ Error: {e}")
                print("Restarting listening system...")
                time.sleep(1)
                continue

if __name__ == "__main__":
    try:
        jamie = ExperimentalJamie()
        jamie.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nFatal error: {e}")