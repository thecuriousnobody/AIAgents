#!/usr/bin/env python3
"""
Task Management Agent for Personal Assistant
===========================================

This agent takes the refined conversation output and creates/updates
tasks in Airtable automatically. It understands context and can:
- Create new tasks
- Update existing tasks 
- Change task statuses
- Avoid duplicates
"""

from crewai import Agent, Task, Crew, Process
from datetime import datetime
import re
import logging
from typing import Dict, Any
from airtable_integration import AirtableManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskManagementAgent:
    """Agent responsible for creating and managing tasks in Airtable"""
    
    def __init__(self, airtable_manager: AirtableManager):
        """
        Initialize the task management agent
        
        Args:
            airtable_manager: Instance of AirtableManager for API operations
        """
        self.airtable = airtable_manager
        
    def create_task_management_agent(self) -> Agent:
        """Create the CrewAI agent for task management"""
        return Agent(
            role='Task Management Specialist',
            goal='Convert conversation outcomes into structured tasks in Airtable, managing the complete task lifecycle',
            backstory="""You are a task management specialist who understands how to convert 
            conversational context into actionable, trackable tasks. You work with 4 project lanes:
            
            1. PODCASTING: Content creation, episodes, guest management, publishing
            2. PODCAST BOTS AI: Startup development, features, user feedback, growth
            3. DISTILLERY LAB: Accelerator/consulting work, mentoring, strategic planning
            4. MISCELLANEOUS: Personal projects, collaborations, other activities
            
            Your responsibilities:
            - Analyze conversation context to extract actionable tasks
            - Determine the appropriate project lane
            - Create clear, specific task titles and descriptions
            - Set appropriate initial status (Not Started, In Progress, Done, Waiting)
            - Check for similar existing tasks to avoid duplicates
            - Update existing tasks when conversation refers to ongoing work
            
            You focus on creating tasks that are:
            - Specific and actionable
            - Properly categorized by project lane
            - Trackable with clear outcomes
            - Connected to the original conversation context""",
            verbose=True,
            allow_delegation=False,
            tools=[],
            reasoning=True,
            max_reasoning_attempts=3
        )
    
    def process_conversation_for_tasks(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process conversation data and create/update tasks accordingly
        
        Args:
            conversation_data: Dictionary containing conversation context
            
        Returns:
            Dictionary with task management results
        """
        try:
            # Extract key information
            user_input = conversation_data.get("user_input", "")
            agent_response = conversation_data.get("agent_response", "")
            project_lane = conversation_data.get("project_lane", "miscellaneous")
            session_id = conversation_data.get("session_id", "")
            
            logger.info(f"Processing conversation for task creation - Lane: {project_lane}")
            
            # Create the task management agent
            task_agent = self.create_task_management_agent()
            
            # Create a task to analyze and create tasks
            analysis_task = Task(
                description=f"""Analyze this conversation and determine what tasks need to be created or updated:
                
                USER INPUT: {user_input}
                AGENT RESPONSE: {agent_response}
                IDENTIFIED PROJECT LANE: {project_lane}
                SESSION ID: {session_id}
                
                Based on this conversation, determine:
                1. What specific, actionable tasks should be created?
                2. What should the task titles be? (Keep them concise but descriptive)
                3. What detailed descriptions should each task have?
                4. What lane does each task belong to? (podcasting, podcast_bots_ai, distillery_lab, miscellaneous)
                5. What should the initial status be? (not_started, in_progress, done, waiting)
                
                For each task, provide:
                - Title: Clear, actionable task title
                - Description: Detailed description with context from the conversation
                - Lane: The appropriate project lane
                - Status: Initial status (usually 'not_started' unless mentioned otherwise)
                - Reasoning: Why this task was identified from the conversation
                
                If the conversation seems to be about updating existing work rather than creating new tasks,
                indicate that and suggest what kind of updates might be needed.""",
                agent=task_agent,
                expected_output="""A structured analysis with task recommendations in this format:
                
                TASK ANALYSIS:
                [Your analysis of what tasks should be created]
                
                RECOMMENDED TASKS:
                Task 1:
                - Title: [Task title]
                - Description: [Detailed description]
                - Lane: [project lane]
                - Status: [status]
                - Reasoning: [Why this task was identified]
                
                Task 2:
                [... if multiple tasks needed]
                
                OR if no new tasks needed:
                NO NEW TASKS NEEDED
                Reasoning: [Explanation of why no tasks should be created]
                
                POTENTIAL UPDATES:
                [If existing tasks might need updates, describe what kind]"""
            )
            
            # Execute the analysis
            crew = Crew(
                agents=[task_agent],
                tasks=[analysis_task],
                verbose=True,
                process=Process.sequential
            )
            
            analysis_result = crew.kickoff()
            analysis_text = str(analysis_result)
            
            # Parse the analysis and create tasks
            task_results = self._parse_and_create_tasks(analysis_text, project_lane)
            
            return {
                "success": True,
                "session_id": session_id,
                "analysis": analysis_text,
                "tasks_created": task_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing conversation for tasks: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_and_create_tasks(self, analysis_text: str, default_lane: str) -> list:
        """
        Parse the agent's analysis and create tasks in Airtable
        
        Args:
            analysis_text: The agent's task analysis
            default_lane: Default project lane if not specified
            
        Returns:
            List of task creation results
        """
        task_results = []
        
        try:
            # Check if no tasks needed
            if "NO NEW TASKS NEEDED" in analysis_text.upper():
                logger.info("Agent determined no new tasks needed")
                return []
            
            # Simple parsing for task blocks (can be enhanced)
            task_blocks = re.findall(r'Task \d+:(.*?)(?=Task \d+:|$)', analysis_text, re.DOTALL)
            
            for task_block in task_blocks:
                try:
                    # Extract task information using regex
                    title_match = re.search(r'Title:\s*(.+)', task_block)
                    desc_match = re.search(r'Description:\s*(.+?)(?=\n\s*-|\n\s*Lane:|$)', task_block, re.DOTALL)
                    lane_match = re.search(r'Lane:\s*(\w+)', task_block)
                    status_match = re.search(r'Status:\s*(\w+)', task_block)
                    
                    if title_match:
                        title = title_match.group(1).strip()
                        description = desc_match.group(1).strip() if desc_match else title
                        lane = lane_match.group(1).strip() if lane_match else default_lane
                        status = status_match.group(1).strip() if status_match else "not_started"
                        
                        # Map lane names to our system
                        lane_mapping = {
                            "podcasting": "podcasting",
                            "podcast": "podcasting", 
                            "podcast_bots_ai": "podcast_bots_ai",
                            "bots": "podcast_bots_ai",
                            "distillery_lab": "distillery_lab",
                            "distillery": "distillery_lab",
                            "lab": "distillery_lab",
                            "miscellaneous": "miscellaneous",
                            "misc": "miscellaneous",
                            "other": "miscellaneous"
                        }
                        
                        lane = lane_mapping.get(lane.lower(), default_lane)
                        
                        # Check for similar tasks first
                        similar_check = self.airtable.search_similar_tasks(title, lane)
                        
                        if similar_check["success"] and similar_check["similar_count"] > 0:
                            logger.info(f"Found {similar_check['similar_count']} similar tasks for '{title}'")
                            task_results.append({
                                "action": "skipped_duplicate",
                                "title": title,
                                "reason": f"Similar task already exists",
                                "similar_count": similar_check["similar_count"]
                            })
                        else:
                            # Create the task
                            create_result = self.airtable.create_task(title, description, lane, status)
                            task_results.append(create_result)
                            
                except Exception as e:
                    logger.error(f"❌ Error processing individual task: {e}")
                    task_results.append({
                        "success": False,
                        "error": f"Task parsing error: {e}"
                    })
            
            return task_results
            
        except Exception as e:
            logger.error(f"❌ Error parsing tasks: {e}")
            return [{
                "success": False,
                "error": f"Parsing error: {e}"
            }]

def test_task_management():
    """Test the task management system"""
    print("🧪 Testing Task Management Agent...")
    
    # This would normally use real Airtable credentials
    print("Note: This test requires Airtable credentials to be set")
    
    # Mock conversation data
    conversation_data = {
        "user_input": "I need to work on podcast scheduling features and update the guest outreach process",
        "agent_response": "I understand you want to work on scheduling features for Podcast Bots AI and improve guest outreach for your podcast",
        "project_lane": "podcasting", 
        "session_id": "test_session_123"
    }
    
    print("Test conversation data prepared")
    print("In real usage, this would create tasks in Airtable")

if __name__ == "__main__":
    test_task_management()
