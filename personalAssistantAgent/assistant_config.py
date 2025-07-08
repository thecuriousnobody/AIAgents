"""
Personal Assistant Agent Configuration
=====================================

Configuration settings for Rajeev's personal assistant system.
"""

import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    temperature: float = 0.7
    max_tokens: int = 2000
    verbose: bool = True
    max_reasoning_attempts: int = 3

@dataclass
class SystemConfig:
    """Main system configuration"""
    # Output directories
    sessions_dir: str = "/Users/rajeevkumar/Documents/GIT_Repos/AIAgents/personalAssistantAgent/sessions"
    work_items_dir: str = "/Users/rajeevkumar/Documents/GIT_Repos/AIAgents/personalAssistantAgent/work_items"
    
    # Agent settings - use default_factory to avoid mutable default
    agent_config: AgentConfig = None
    
    # Whisper settings (for future implementation)
    whisper_model: str = "whisper-1"
    whisper_language: str = "en"
    
    # Streaming settings
    enable_streaming: bool = True
    stream_chunk_size: int = 1024
    
    def __post_init__(self):
        """Initialize mutable fields after creation"""
        if self.agent_config is None:
            self.agent_config = AgentConfig()

# Project lane priorities and weights for classification
LANE_CLASSIFICATION_WEIGHTS = {
    "podcasting": {
        "keywords_weight": 0.4,
        "context_weight": 0.3,
        "activity_weight": 0.3
    },
    "distillery_lab": {
        "keywords_weight": 0.3,
        "context_weight": 0.4,
        "activity_weight": 0.3
    },
    "podcast_bots_ai": {
        "keywords_weight": 0.5,
        "context_weight": 0.3,
        "activity_weight": 0.2
    },
    "miscellaneous": {
        "keywords_weight": 0.2,
        "context_weight": 0.3,
        "activity_weight": 0.5
    }
}

# Confidence thresholds for classification
CLASSIFICATION_THRESHOLDS = {
    "high_confidence": 0.8,
    "medium_confidence": 0.6,
    "low_confidence": 0.4
}

# Default system prompts
SYSTEM_PROMPTS = {
    "personal_assistant": """You are Rajeev's trusted personal assistant with deep knowledge of his work patterns and preferences. You're conversational, proactive, and focused on helping him think through ideas clearly.""",
    
    "research_classifier": """You are a meticulous researcher and classifier who takes conversational input and turns it into structured, actionable work items with proper lane classification.""",
    
    "execution_agent": """You are the execution specialist who takes classified work items and translates them into real-world actions like calendar events, checklists, and system updates."""
}

# Tool configurations
TOOL_CONFIGS = {
    "serper_search": {
        "max_results": 10,
        "country": "us",
        "language": "en"
    },
    "calendar": {
        "default_duration": 30,  # minutes
        "default_reminder": 15,  # minutes before
        "time_zone": "America/Los_Angeles"
    },
    "checklist": {
        "default_priority": "medium",
        "auto_due_date": True,
        "default_due_days": 7
    }
}

# Load system configuration
def get_system_config() -> SystemConfig:
    """Get the system configuration with environment overrides"""
    config = SystemConfig()
    
    # Override with environment variables if present
    if os.getenv("PA_SESSIONS_DIR"):
        config.sessions_dir = os.getenv("PA_SESSIONS_DIR")
    
    if os.getenv("PA_WORK_ITEMS_DIR"):
        config.work_items_dir = os.getenv("PA_WORK_ITEMS_DIR")
    
    if os.getenv("PA_ENABLE_STREAMING"):
        config.enable_streaming = os.getenv("PA_ENABLE_STREAMING").lower() == "true"
    
    return config
