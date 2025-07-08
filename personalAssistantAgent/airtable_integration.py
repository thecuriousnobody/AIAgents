#!/usr/bin/env python3
"""
Airtable Integration for Personal Assistant
==========================================

Handles CRUD operations for task management in Airtable.
Integrates with the personal assistant workflow to automatically
create and manage tasks across the 4 project lanes.
"""

import requests
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirtableManager:
    """Manages task operations with Airtable API"""
    
    def __init__(self, base_id: str, api_key: str, table_name: str = "Tasks"):
        """
        Initialize Airtable manager
        
        Args:
            base_id: Airtable base ID (starts with 'app')
            api_key: Personal access token
            table_name: Name of the table (default: "Tasks")
        """
        self.base_id = base_id
        self.api_key = api_key
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Project lane mapping
        self.lanes = {
            "podcasting": "Podcasting",
            "podcast_bots_ai": "Podcast Bots AI", 
            "distillery_lab": "Distillery Lab",
            "miscellaneous": "Miscellaneous"
        }
        
        # Task statuses
        self.statuses = {
            "not_started": "Not Started",
            "in_progress": "In Progress", 
            "done": "Done",
            "waiting": "Waiting"
        }
    
    def create_task(self, title: str, description: str, lane: str, status: str = "not_started") -> Dict[str, Any]:
        """
        Create a new task in Airtable
        
        Args:
            title: Task title
            description: Task description
            lane: Project lane (podcasting, podcast_bots_ai, distillery_lab, miscellaneous)
            status: Task status (default: not_started)
            
        Returns:
            Dictionary with creation result
        """
        try:
            # Validate inputs
            if lane not in self.lanes:
                raise ValueError(f"Invalid lane: {lane}. Must be one of {list(self.lanes.keys())}")
            
            if status not in self.statuses:
                raise ValueError(f"Invalid status: {status}. Must be one of {list(self.statuses.keys())}")
            
            # Prepare record data
            record_data = {
                "records": [{
                    "fields": {
                        "Title": title,
                        "Description": description,
                        "Lane": self.lanes[lane],
                        "Start Date": date.today().isoformat()
                        # Skip Status and Created Date for now - let Airtable handle them
                    }
                }]
            }
            
            logger.info(f"Creating task: {title} in {lane} lane")
            
            # Make API request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=record_data
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result["records"][0]["id"]
                logger.info(f"✅ Task created successfully with ID: {task_id}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "title": title,
                    "lane": self.lanes[lane],
                    "status": self.statuses[status]
                }
            else:
                logger.error(f"❌ Failed to create task: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update a task's status
        
        Args:
            task_id: Airtable record ID
            new_status: New status (not_started, in_progress, done, waiting)
            
        Returns:
            Dictionary with update result
        """
        try:
            if new_status not in self.statuses:
                raise ValueError(f"Invalid status: {new_status}")
            
            # Prepare update data
            update_data = {
                "records": [{
                    "id": task_id,
                    "fields": {
                        "Status": self.statuses[new_status]
                    }
                }]
            }
            
            logger.info(f"Updating task {task_id} status to {new_status}")
            
            # Make API request
            response = requests.patch(
                self.base_url,
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Task status updated successfully")
                return {
                    "success": True,
                    "task_id": task_id,
                    "new_status": self.statuses[new_status]
                }
            else:
                logger.error(f"❌ Failed to update task: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error updating task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tasks_by_lane(self, lane: str) -> Dict[str, Any]:
        """
        Get all tasks for a specific lane
        
        Args:
            lane: Project lane
            
        Returns:
            Dictionary with tasks
        """
        try:
            if lane not in self.lanes:
                raise ValueError(f"Invalid lane: {lane}")
            
            # Build filter formula
            filter_formula = f"{{Lane}} = '{self.lanes[lane]}'"
            
            # Make API request
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"filterByFormula": filter_formula}
            )
            
            if response.status_code == 200:
                result = response.json()
                tasks = result.get("records", [])
                
                logger.info(f"✅ Retrieved {len(tasks)} tasks for {lane} lane")
                return {
                    "success": True,
                    "lane": self.lanes[lane],
                    "task_count": len(tasks),
                    "tasks": tasks
                }
            else:
                logger.error(f"❌ Failed to get tasks: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting tasks: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_similar_tasks(self, title: str, lane: str) -> Dict[str, Any]:
        """
        Search for tasks with similar titles in the same lane to avoid duplicates
        
        Args:
            title: Task title to search for
            lane: Project lane
            
        Returns:
            Dictionary with similar tasks
        """
        try:
            if lane not in self.lanes:
                raise ValueError(f"Invalid lane: {lane}")
            
            # Get all tasks for this lane
            lane_tasks = self.get_tasks_by_lane(lane)
            
            if not lane_tasks["success"]:
                return lane_tasks
            
            # Simple similarity check (can be enhanced)
            similar_tasks = []
            title_lower = title.lower()
            
            for task in lane_tasks["tasks"]:
                task_title = task["fields"].get("Title", "").lower()
                # Check if titles have significant overlap
                if any(word in task_title for word in title_lower.split() if len(word) > 3):
                    similar_tasks.append(task)
            
            return {
                "success": True,
                "similar_count": len(similar_tasks),
                "similar_tasks": similar_tasks
            }
            
        except Exception as e:
            logger.error(f"❌ Error searching tasks: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Airtable connection"""
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"maxRecords": 1}
            )
            
            if response.status_code == 200:
                logger.info("✅ Airtable connection successful")
                return {
                    "success": True,
                    "message": "Airtable connection successful"
                }
            else:
                logger.error(f"❌ Airtable connection failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Connection failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Airtable connection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def test_airtable_integration():
    """Test function for Airtable integration"""
    print("🧪 Testing Airtable Integration...")
    print("Note: You need to set AIRTABLE_BASE_ID and AIRTABLE_API_KEY environment variables")
    
    import os
    base_id = os.getenv("AIRTABLE_BASE_ID")
    api_key = os.getenv("AIRTABLE_API_KEY")
    
    if not base_id or not api_key:
        print("❌ Missing environment variables. Please set:")
        print("   export AIRTABLE_BASE_ID='your_base_id'")
        print("   export AIRTABLE_API_KEY='your_api_key'")
        return False
    
    # Initialize manager
    airtable = AirtableManager(base_id, api_key)
    
    # Test connection
    connection_test = airtable.test_connection()
    if not connection_test["success"]:
        print(f"❌ Connection test failed: {connection_test['error']}")
        return False
    
    print("✅ Connection test passed!")
    
    # Test task creation
    task_result = airtable.create_task(
        title="Test task from Personal Assistant",
        description="This is a test task created by the personal assistant system",
        lane="podcasting",
        status="not_started"
    )
    
    if task_result["success"]:
        print(f"✅ Test task created successfully: {task_result['task_id']}")
        return True
    else:
        print(f"❌ Task creation failed: {task_result['error']}")
        return False

if __name__ == "__main__":
    test_airtable_integration()
