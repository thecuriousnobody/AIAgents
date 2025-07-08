#!/usr/bin/env python3
"""
Streaming Personal Assistant Interface
=====================================

Real-time streaming interface for the personal assistant system.
This handles speech-to-text input and streams responses back in real-time.
"""

import asyncio
import json
import queue
import threading
import time
from typing import AsyncGenerator, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from crewai import Agent, Task, Crew, Process
from crewai.agent import Agent as CrewAIAgent

# For future Whisper integration
# import openai
# import whisper

from personal_assistant_system import PersonalAssistantAgents, PROJECT_LANES
from assistant_config import get_system_config, SYSTEM_PROMPTS

@dataclass
class StreamingMessage:
    """Represents a streaming message"""
    type: str  # 'agent_start', 'agent_thinking', 'agent_response', 'task_complete', 'error'
    agent: str
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class StreamingCallback:
    """Callback handler for CrewAI streaming"""
    
    def __init__(self, message_queue: queue.Queue):
        self.message_queue = message_queue
        self.current_agent = None
        
    def on_agent_start(self, agent: CrewAIAgent, task_description: str):
        """Called when an agent starts working"""
        self.current_agent = agent.role if hasattr(agent, 'role') else 'Unknown Agent'
        message = StreamingMessage(
            type='agent_start',
            agent=self.current_agent,
            content=f"🤖 {self.current_agent} is starting to work on your request...",
            timestamp=datetime.now().isoformat(),
            metadata={'task_description': task_description}
        )
        self.message_queue.put(message)
    
    def on_agent_thinking(self, agent: CrewAIAgent, thought: str):
        """Called when an agent is reasoning/thinking"""
        agent_name = agent.role if hasattr(agent, 'role') else 'Agent'
        message = StreamingMessage(
            type='agent_thinking',
            agent=agent_name,
            content=f"💭 {agent_name}: {thought}",
            timestamp=datetime.now().isoformat()
        )
        self.message_queue.put(message)
    
    def on_agent_response(self, agent: CrewAIAgent, response: str):
        """Called when an agent produces a response"""
        agent_name = agent.role if hasattr(agent, 'role') else 'Agent'
        message = StreamingMessage(
            type='agent_response',
            agent=agent_name,
            content=response,
            timestamp=datetime.now().isoformat()
        )
        self.message_queue.put(message)
    
    def on_task_complete(self, task_result: Any):
        """Called when a task is completed"""
        message = StreamingMessage(
            type='task_complete',
            agent='System',
            content="✅ Task completed successfully!",
            timestamp=datetime.now().isoformat(),
            metadata={'result': str(task_result)}
        )
        self.message_queue.put(message)
    
    def on_error(self, error: Exception):
        """Called when an error occurs"""
        message = StreamingMessage(
            type='error',
            agent='System',
            content=f"❌ Error: {str(error)}",
            timestamp=datetime.now().isoformat(),
            metadata={'error_type': type(error).__name__}
        )
        self.message_queue.put(message)

class StreamingPersonalAssistant:
    """Streaming version of the personal assistant"""
    
    def __init__(self):
        self.config = get_system_config()
        self.agents = PersonalAssistantAgents()
        self.message_queue = queue.Queue()
        self.streaming_callback = StreamingCallback(self.message_queue)
        
    async def process_speech_stream(self, user_input: str) -> AsyncGenerator[StreamingMessage, None]:
        """Process user speech and stream responses in real-time"""
        
        try:
            # Start the processing in a separate thread
            processing_thread = threading.Thread(
                target=self._process_in_background,
                args=(user_input,)
            )
            processing_thread.start()
            
            # Stream messages as they become available
            while processing_thread.is_alive() or not self.message_queue.empty():
                try:
                    # Get message with timeout to avoid blocking
                    message = self.message_queue.get(timeout=0.1)
                    yield message
                except queue.Empty:
                    # No message available, continue
                    await asyncio.sleep(0.1)
                    continue
            
            # Wait for thread to complete
            processing_thread.join()
            
            # Get any remaining messages
            while not self.message_queue.empty():
                message = self.message_queue.get()
                yield message
                
        except Exception as e:
            error_message = StreamingMessage(
                type='error',
                agent='System',
                content=f"Failed to process request: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
            yield error_message
    
    def _process_in_background(self, user_input: str):
        """Process the user input in background thread"""
        try:
            # Simulate the 3-agent workflow with streaming
            self._simulate_agent_workflow(user_input)
        except Exception as e:
            self.streaming_callback.on_error(e)
    
    def _simulate_agent_workflow(self, user_input: str):
        """Simulate the 3-agent workflow with streaming callbacks"""
        
        # Agent 1: Personal Assistant
        self.streaming_callback.on_agent_start(
            type('Agent', (), {'role': 'Personal Assistant'})(),
            f"Understanding and refining: '{user_input}'"
        )
        
        time.sleep(1)  # Simulate processing time
        
        self.streaming_callback.on_agent_thinking(
            type('Agent', (), {'role': 'Personal Assistant'})(),
            "Analyzing which project lane this relates to..."
        )
        
        time.sleep(1.5)
        
        # Simulate lane classification
        lane_suggestion = self._classify_lane_quick(user_input)
        
        assistant_response = f"""I understand you're talking about: {user_input}

Based on the keywords and context, this seems to relate to your **{lane_suggestion}** project lane.

Let me ask a few clarifying questions:
1. Is this a new task or an update on existing work?
2. What's the priority level for this?
3. Are there any specific deadlines or timeframes?

I'm preparing this for deeper research and classification..."""

        self.streaming_callback.on_agent_response(
            type('Agent', (), {'role': 'Personal Assistant'})(),
            assistant_response
        )
        
        time.sleep(2)
        
        # Agent 2: Research & Classification
        self.streaming_callback.on_agent_start(
            type('Agent', (), {'role': 'Research & Classification Specialist'})(),
            "Researching context and creating work item..."
        )
        
        time.sleep(1)
        
        self.streaming_callback.on_agent_thinking(
            type('Agent', (), {'role': 'Research & Classification Specialist'})(),
            f"Searching for relevant information about: {user_input}"
        )
        
        time.sleep(2)
        
        research_response = f"""Research completed! Here's what I found:

🆔 **Work ID**: WI-{datetime.now().strftime('%m%d')}-{hash(user_input) % 1000:03d}
📂 **Project Lane**: {lane_suggestion}
⭐ **Priority**: Medium
📅 **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Classification Confidence**: 85%
**Actions Needed**:
- Create calendar reminder
- Add to project checklist
- Update tracking system

Passing to Execution Agent for action..."""

        self.streaming_callback.on_agent_response(
            type('Agent', (), {'role': 'Research & Classification Specialist'})(),
            research_response
        )
        
        time.sleep(1.5)
        
        # Agent 3: Execution
        self.streaming_callback.on_agent_start(
            type('Agent', (), {'role': 'Execution Agent'})(),
            "Executing real-world actions..."
        )
        
        time.sleep(1)
        
        self.streaming_callback.on_agent_thinking(
            type('Agent', (), {'role': 'Execution Agent'})(),
            "Creating calendar events and checklist items..."
        )
        
        time.sleep(1.5)
        
        execution_response = f"""✅ **Execution Complete!**

**Calendar Events Created**:
- Follow-up reminder for {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}
- Project review scheduled for {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}

**Checklist Items Added**:
- [ ] Research and planning phase
- [ ] Implementation tasks
- [ ] Review and testing
- [ ] Final delivery/completion

**System Updates**:
- Added to {lane_suggestion} project tracker
- Updated priority matrix
- Created work item documentation

**Next Steps**:
- You'll receive calendar notifications
- Checklist items are ready for execution
- All work is properly categorized and tracked

Your assistant is ready for the next input! 🚀"""

        self.streaming_callback.on_agent_response(
            type('Agent', (), {'role': 'Execution Agent'})(),
            execution_response
        )
        
        self.streaming_callback.on_task_complete(execution_response)
    
    def _classify_lane_quick(self, user_input: str) -> str:
        """Quick lane classification based on keywords"""
        user_input_lower = user_input.lower()
        
        lane_scores = {}
        for lane_name, lane_info in PROJECT_LANES.items():
            score = 0
            for keyword in lane_info.keywords:
                if keyword.lower() in user_input_lower:
                    score += 1
            lane_scores[lane_name] = score
        
        # Return the lane with highest score, or miscellaneous if tie
        best_lane = max(lane_scores, key=lane_scores.get)
        return PROJECT_LANES[best_lane].name

# =============================================================================
# CONSOLE STREAMING INTERFACE
# =============================================================================

async def run_streaming_console():
    """Run a streaming console interface for testing"""
    print("🎤 Streaming Personal Assistant Console")
    print("=" * 50)
    print("Type your message and see real-time agent responses!")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    assistant = StreamingPersonalAssistant()
    
    while True:
        user_input = input("\n💬 You: ")
        if user_input.lower() == 'quit':
            break
            
        print("\n🤖 Assistant is processing...")
        print("-" * 40)
        
        # Stream the responses
        async for message in assistant.process_speech_stream(user_input):
            if message.type == 'agent_start':
                print(f"\n{message.content}")
            elif message.type == 'agent_thinking':
                print(f"  {message.content}")
            elif message.type == 'agent_response':
                print(f"\n📝 {message.agent}:")
                print(f"{message.content}")
            elif message.type == 'task_complete':
                print(f"\n{message.content}")
            elif message.type == 'error':
                print(f"\n{message.content}")
        
        print("\n" + "=" * 50)

# For FastAPI integration (future)
class FastAPIStreamingResponse:
    """FastAPI-compatible streaming response"""
    
    def __init__(self, assistant: StreamingPersonalAssistant):
        self.assistant = assistant
    
    async def stream_response(self, user_input: str):
        """Generate Server-Sent Events for FastAPI"""
        async for message in self.assistant.process_speech_stream(user_input):
            data = {
                'type': message.type,
                'agent': message.agent,
                'content': message.content,
                'timestamp': message.timestamp,
                'metadata': message.metadata
            }
            yield f"data: {json.dumps(data)}\n\n"

if __name__ == "__main__":
    import asyncio
    from datetime import timedelta
    
    asyncio.run(run_streaming_console())
