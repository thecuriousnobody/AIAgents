#!/usr/bin/env python3
"""
Personal Assistant Agent System
==============================

A sophisticated multi-agent system for managing Rajeev's four project lanes:
1. Podcasting - Content creation, episodes, publishing
2. Distillery Lab - Accelerator/consulting work  
3. Podcast Bots AI - Startup development
4. Miscellaneous - Everything else

Architecture:
- Agent 1: Personal Assistant (Gatekeeper) - Conversational refinement
- Agent 2: Research & Classification - Deep understanding & routing
- Agent 3: Execution Agent - Real actions (calendar, checklists, etc.)

This is a prototyping exercise - we'll discover and build together!
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import Tool
from datetime import datetime, timedelta
import os
import sys
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import serper_search_tool

# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPER_API_KEY"] = config.SERPER_API_KEY

# =============================================================================
# DATA MODELS
# =============================================================================

class ProjectLane(BaseModel):
    """Represents one of the four project lanes"""
    name: str
    description: str
    keywords: List[str]
    typical_activities: List[str]

class WorkItem(BaseModel):
    """Represents a work item with unique ID"""
    work_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    lane: str
    title: str
    description: str
    priority: str = "medium"  # high, medium, low
    status: str = "new"  # new, in_progress, completed
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    actions_needed: List[str] = []
    calendar_events: List[str] = []
    
class ConversationContext(BaseModel):
    """Tracks conversation context for the personal assistant"""
    session_id: str
    user_input: str
    refined_understanding: str
    lane_suggestions: List[str]
    clarifying_questions: List[str]
    confidence_score: float

# =============================================================================
# PROJECT LANE CONFIGURATION
# =============================================================================

PROJECT_LANES = {
    "podcasting": ProjectLane(
        name="Podcasting",
        description="Content creation, episode production, publishing, and podcast growth",
        keywords=["podcast", "episode", "recording", "editing", "publishing", "content", "guests", "interviews"],
        typical_activities=[
            "Recording episodes",
            "Editing content", 
            "Publishing to platforms",
            "Guest outreach",
            "Content planning",
            "Show notes creation"
        ]
    ),
    "distillery_lab": ProjectLane(
        name="Distillery Lab",
        description="Accelerator and consulting work, mentoring, technical direction",
        keywords=["accelerator", "consulting", "mentoring", "technical", "startup", "advice", "review"],
        typical_activities=[
            "Mentor sessions",
            "Technical reviews",
            "Startup advising",
            "Portfolio company work",
            "Investment decisions",
            "Strategic planning"
        ]
    ),
    "podcast_bots_ai": ProjectLane(
        name="Podcast Bots AI",
        description="Startup development, features, user feedback, growth, investor relations",
        keywords=["podcast bots", "startup", "AI", "features", "users", "growth", "investors", "product"],
        typical_activities=[
            "Feature development",
            "User feedback analysis",
            "Growth metrics tracking",
            "Investor updates",
            "Product roadmap",
            "Technical architecture"
        ]
    ),
    "miscellaneous": ProjectLane(
        name="Miscellaneous",
        description="General collaborations, personal projects, and other activities",
        keywords=["collaboration", "personal", "other", "general", "misc", "random"],
        typical_activities=[
            "Personal projects",
            "Collaborations",
            "Learning activities",
            "Research projects",
            "Side experiments",
            "General tasks"
        ]
    )
}

# =============================================================================
# AGENTS
# =============================================================================

class PersonalAssistantAgents:
    def __init__(self):
        self.llm = ClaudeSonnet
        self.conversation_history: List[ConversationContext] = []
        
    def create_personal_assistant_agent(self) -> Agent:
        """Agent 1: Personal Assistant (Gatekeeper)"""
        return Agent(
            role='Personal Assistant & Gatekeeper',
            goal='Act as Rajeev\'s intelligent personal assistant, understanding his work across 4 project lanes and helping refine ideas through conversation',
            backstory=f"""You are Rajeev's trusted personal assistant who intimately knows his work across four major project lanes:

            1. PODCASTING: {PROJECT_LANES['podcasting'].description}
            2. DISTILLERY LAB: {PROJECT_LANES['distillery_lab'].description}  
            3. PODCAST BOTS AI: {PROJECT_LANES['podcast_bots_ai'].description}
            4. MISCELLANEOUS: {PROJECT_LANES['miscellaneous'].description}

            Your personality is:
            - Conversational and engaging
            - Proactive in asking clarifying questions
            - Knowledgeable about his ongoing projects
            - Able to suggest improvements and refinements
            - Focused on helping him think through ideas clearly

            You receive speech-to-text input and engage in real-time conversation to:
            - Understand what he's trying to communicate
            - Suggest which project lane this belongs to
            - Ask clarifying questions to refine the idea
            - Help him think through next steps
            - Prepare clear, actionable information for the specialist agents

            You are NOT responsible for execution - just conversation and refinement.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],
            reasoning=True,
            max_reasoning_attempts=3
        )
    
    def create_research_classifier_agent(self) -> Agent:
        """Agent 2: Research & Classification Specialist"""
        return Agent(
            role='Research & Classification Specialist',
            goal='Take refined input from the Personal Assistant and do deep research, understanding, and classification into the appropriate project lane',
            backstory="""You are a research and classification specialist who takes the refined conversations from the Personal Assistant and does the deep work of:

            1. RESEARCH: Using search tools to understand context, find relevant information, and gather background
            2. CLASSIFICATION: Definitively determining which project lane this belongs to
            3. WORK ID CREATION: Generating unique work IDs for tracking
            4. STRUCTURING: Organizing the information for the Execution Agent

            You have access to search tools and can:
            - Research people, companies, technologies mentioned
            - Find context about ongoing projects
            - Verify information and add relevant details
            - Create comprehensive work items with all necessary information

            Your output should be structured, detailed, and ready for action.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[serper_search_tool],
            reasoning=True,
            max_reasoning_attempts=3
        )
    
    def create_execution_agent(self) -> Agent:
        """Agent 3: Execution Agent"""
        return Agent(
            role='Execution Agent',
            goal='Take classified work items and execute real actions like calendar updates, checklist creation, and system updates',
            backstory="""You are the execution specialist who takes fully researched and classified work items and actually does things:

            1. CALENDAR MANAGEMENT: Creating calendar events, scheduling reminders
            2. CHECKLIST CREATION: Breaking down work into actionable tasks
            3. SYSTEM UPDATES: Updating project tracking systems
            4. COMMUNICATION: Preparing communications and follow-ups

            You work with structured work items that have:
            - Unique work IDs
            - Clear project lane assignments
            - Detailed descriptions and context
            - Specific actions needed

            Your job is to translate these into real-world actions and provide clear feedback on what was accomplished.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[],  # TODO: Add calendar, checklist, notification tools
            reasoning=True,
            max_reasoning_attempts=3
        )

# =============================================================================
# WORKFLOW ORCHESTRATION
# =============================================================================

class PersonalAssistantWorkflow:
    def __init__(self):
        self.agents = PersonalAssistantAgents()
        self.session_id = str(uuid.uuid4())[:8]
        
    def process_speech_input(self, user_speech: str) -> Dict[str, Any]:
        """Main workflow: Speech input -> Conversation -> Classification -> Execution"""
        
        # Create agents
        personal_assistant = self.agents.create_personal_assistant_agent()
        research_classifier = self.agents.create_research_classifier_agent()
        execution_agent = self.agents.create_execution_agent()
        
        # Task 1: Personal Assistant Conversation
        conversation_task = Task(
            description=f"""The user said: "{user_speech}"
            
            As Rajeev's personal assistant, engage with this input:
            1. Understand what he's trying to communicate
            2. Identify which project lane(s) this might relate to:
               - Podcasting: {PROJECT_LANES['podcasting'].description}
               - Distillery Lab: {PROJECT_LANES['distillery_lab'].description}
               - Podcast Bots AI: {PROJECT_LANES['podcast_bots_ai'].description}
               - Miscellaneous: {PROJECT_LANES['miscellaneous'].description}
            
            3. Ask clarifying questions if needed
            4. Suggest improvements or refinements
            5. Prepare a refined understanding for the specialist agents
            
            Be conversational and engaging - you're having a real-time chat with him.""",
            agent=personal_assistant,
            expected_output="""A conversational response that includes:
            1. Your understanding of what he said
            2. Which project lane(s) you think this relates to and why
            3. Any clarifying questions you have
            4. Suggestions for refinement or improvement
            5. A refined, clear version of the task/idea ready for research and classification
            
            Format this as a natural conversation - like you're talking to him in person."""
        )
        
        # Task 2: Research & Classification
        research_task = Task(
            description=f"""Based on the Personal Assistant's conversation and refined understanding, do deep research and classification:
            
            1. RESEARCH: Use search tools to find relevant context, background information, and details
            2. CLASSIFY: Definitively determine which project lane this belongs to
            3. CREATE WORK ID: Generate a unique work ID for tracking
            4. STRUCTURE: Organize all information into a comprehensive work item
            
            Consider the user's four project lanes:
            - Podcasting: Content creation, episodes, publishing
            - Distillery Lab: Accelerator/consulting work
            - Podcast Bots AI: Startup development
            - Miscellaneous: Everything else
            
            Research any people, companies, technologies, or concepts mentioned.""",
            agent=research_classifier,
            expected_output="""A structured work item containing:
            1. Unique work ID
            2. Assigned project lane with confidence score
            3. Clear title and description
            4. Research findings and context
            5. Priority level (high/medium/low)
            6. Specific actions needed
            7. Any calendar events or reminders to create
            8. Background information gathered from research""",
            context=[conversation_task]
        )
        
        # Task 3: Execution
        execution_task = Task(
            description=f"""Take the classified work item and execute real actions:
            
            1. CALENDAR: Create any necessary calendar events or reminders
            2. CHECKLISTS: Break down the work into actionable tasks
            3. UPDATES: Update relevant tracking systems
            4. COMMUNICATIONS: Prepare any necessary communications or follow-ups
            
            For this prototype, simulate the actions but provide detailed descriptions of what would be done.""",
            agent=execution_agent,
            expected_output="""A comprehensive execution report containing:
            1. Calendar events created (with dates, times, descriptions)
            2. Checklist items created (with priorities and due dates)
            3. System updates made (which systems, what changes)
            4. Communications prepared (who to contact, what to say)
            5. Summary of all actions taken
            6. Next steps and follow-up items""",
            context=[research_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[personal_assistant, research_classifier, execution_agent],
            tasks=[conversation_task, research_task, execution_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the workflow
        result = crew.kickoff()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_session_results(user_speech, result, timestamp)
        
        return {
            "session_id": self.session_id,
            "user_input": user_speech,
            "result": result,
            "timestamp": timestamp
        }
    
    def save_session_results(self, user_input: str, result: Any, timestamp: str):
        """Save session results to file"""
        output_dir = "/Users/rajeevkumar/Documents/GIT_Repos/AIAgents/personalAssistantAgent/sessions"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"session_{self.session_id}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PERSONAL ASSISTANT SESSION RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"User Input: {user_input}\n")
            f.write("=" * 80 + "\n\n")
            f.write(str(result))
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("END OF SESSION\n")
            f.write("=" * 80 + "\n")
        
        print(f"Session saved to: {filepath}")
    
    def get_personal_assistant_response(self, user_speech: str) -> str:
        """Get just the personal assistant's conversational response"""
        try:
            # Create personal assistant agent
            personal_assistant = self.agents.create_personal_assistant_agent()
            
            # Create a simple conversation task
            conversation_task = Task(
                description=f"""The user just said: "{user_speech}"
                
                As Rajeev's intelligent personal assistant, respond conversationally and helpfully:
                
                1. UNDERSTAND: What is he trying to communicate or accomplish?
                2. IDENTIFY: Which project lane does this relate to?
                   - Podcasting: Content creation, episodes, publishing, interviews
                   - Distillery Lab: Accelerator/consulting work, startups, mentoring
                   - Podcast Bots AI: His startup development, features, growth
                   - Miscellaneous: Personal projects, collaborations, other activities
                
                3. RESPOND: Give a helpful, intelligent response that shows you understand and can help
                4. SUGGEST: What specific actions or next steps would be helpful?
                
                Be conversational, proactive, and demonstrate understanding of his work context.
                Don't just repeat what he said - add value and insight.""",
                agent=personal_assistant,
                expected_output="""A conversational response that shows understanding and provides value:
                1. Acknowledge what he said with understanding
                2. Identify the relevant project lane and why
                3. Suggest specific next steps or actions
                4. Ask clarifying questions if needed
                5. Demonstrate knowledge of his ongoing work
                
                Be natural and conversational - like a smart assistant who knows his work well."""
            )
            
            # Execute just this single task
            crew = Crew(
                agents=[personal_assistant],
                tasks=[conversation_task],
                verbose=True,
                process=Process.sequential
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Personal assistant response error: {e}")
            return f"I understand you said: '{user_speech}'. Let me help you with that. Which project lane should I focus on - Podcasting, Distillery Lab, Podcast Bots AI, or something else?"

    def refine_understanding(self, conversation_context: str, refinement: str) -> str:
        """Refine the agent's understanding with additional context"""
        try:
            # Create personal assistant agent
            personal_assistant = self.agents.create_personal_assistant_agent()
            
            # Create a refinement task
            refinement_task = Task(
                description=f"""You are refining your understanding based on additional context from the user.
                
                CONVERSATION CONTEXT:
                {conversation_context}
                
                The user has provided this additional refinement: "{refinement}"
                
                Please provide an updated, more comprehensive response that incorporates:
                1. Your previous understanding
                2. The new information provided by the user
                3. A refined analysis of which project lane this belongs to
                4. Updated suggestions and next steps based on the complete picture
                
                Be conversational and show that you've thoughtfully incorporated the new information.
                Focus on building upon your previous response rather than starting over.""",
                agent=personal_assistant,
                expected_output="""A refined conversational response that shows:
                1. Acknowledgment of the additional information
                2. Updated understanding incorporating both previous and new context
                3. Refined project lane identification if needed
                4. Updated suggestions and next steps
                5. Any new clarifying questions based on the complete picture
                
                Be natural and conversational - show that you're building on the conversation."""
            )
            
            # Execute the refinement task
            crew = Crew(
                agents=[personal_assistant],
                tasks=[refinement_task],
                verbose=True,
                process=Process.sequential
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Refinement error: {e}")
            return f"I understand you want to add: '{refinement}'. Let me incorporate this into my understanding and provide a more complete response."

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function for testing the personal assistant system"""
    print("🤖 Personal Assistant Agent System")
    print("=" * 60)
    print("This is your multi-agent personal assistant for managing:")
    print("1. Podcasting")
    print("2. Distillery Lab (Accelerator)")
    print("3. Podcast Bots AI (Startup)")
    print("4. Miscellaneous")
    print("=" * 60)
    
    # Initialize the workflow
    workflow = PersonalAssistantWorkflow()
    
    # Get user input (in real implementation, this would come from Whisper)
    user_speech = input("\n🎤 What would you like to tell your assistant? ")
    
    print(f"\n🔄 Processing your input: '{user_speech}'")
    print("Running through the 3-agent workflow...")
    
    # Process the speech input
    result = workflow.process_speech_input(user_speech)
    
    print(f"\n✅ Processing complete!")
    print(f"Session ID: {result['session_id']}")
    print(f"Timestamp: {result['timestamp']}")
    print("\nResults saved to sessions folder.")

if __name__ == "__main__":
    main()
