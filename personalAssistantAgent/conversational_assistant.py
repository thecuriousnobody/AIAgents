#!/usr/bin/env python3
"""
Streaming Personal Assistant with Conversational Memory
======================================================

This implements the conversational back-and-forth with Agent 1,
similar to how Claude works with real-time interaction and memory.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
from pydantic import BaseModel
import sys
import os

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from personal_assistant_system import PersonalAssistantAgents, PROJECT_LANES

@dataclass
class ConversationTurn:
    """Represents one turn in the conversation"""
    turn_id: str
    timestamp: str
    speaker: str  # "user" or "assistant"
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    suggested_lane: Optional[str] = None

@dataclass
class ConversationSession:
    """Represents an entire conversation session"""
    session_id: str
    user_id: str
    started_at: str
    last_updated: str
    turns: List[ConversationTurn]
    current_topic: Optional[str] = None
    identified_lane: Optional[str] = None
    confidence_score: Optional[float] = None
    ready_for_processing: bool = False

class ConversationMemory:
    """Manages conversational memory and context"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.agents = PersonalAssistantAgents()
        
    def start_session(self, user_id: str = "rajeev") -> str:
        """Start a new conversation session"""
        session_id = str(uuid.uuid4())[:8]
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            started_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            turns=[]
        )
        self.sessions[session_id] = session
        return session_id
        
    def add_turn(self, session_id: str, speaker: str, message: str, **kwargs) -> ConversationTurn:
        """Add a turn to the conversation"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            speaker=speaker,
            message=message,
            **kwargs
        )
        
        self.sessions[session_id].turns.append(turn)
        self.sessions[session_id].last_updated = datetime.now().isoformat()
        
        return turn
        
    def get_conversation_context(self, session_id: str) -> str:
        """Get formatted conversation context for the agent"""
        if session_id not in self.sessions:
            return ""
            
        session = self.sessions[session_id]
        context = f"Conversation Session {session_id} Context:\n"
        context += f"Started: {session.started_at}\n"
        context += f"Current topic: {session.current_topic or 'Not yet identified'}\n"
        context += f"Suggested lane: {session.identified_lane or 'Not yet determined'}\n\n"
        context += "Conversation history:\n"
        
        for turn in session.turns[-10:]:  # Last 10 turns for context
            context += f"{turn.speaker}: {turn.message}\n"
            
        return context
        
    def update_session_insights(self, session_id: str, topic: str = None, lane: str = None, confidence: float = None):
        """Update session-level insights"""
        if session_id not in self.sessions:
            return
            
        session = self.sessions[session_id]
        if topic:
            session.current_topic = topic
        if lane:
            session.identified_lane = lane
        if confidence:
            session.confidence_score = confidence
            
        session.last_updated = datetime.now().isoformat()

class StreamingPersonalAssistant:
    """Streaming personal assistant with real-time conversation"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.agent = self.memory.agents.create_personal_assistant_agent()
        
    async def start_conversation(self, initial_input: str, user_id: str = "rajeev") -> str:
        """Start a new conversation session"""
        session_id = self.memory.start_session(user_id)
        
        # Add the initial user input
        self.memory.add_turn(session_id, "user", initial_input)
        
        return session_id
        
    async def continue_conversation(self, session_id: str, user_input: str) -> AsyncGenerator[str, None]:
        """Continue conversation with streaming response"""
        
        # Add user turn
        self.memory.add_turn(session_id, "user", user_input)
        
        # Get conversation context
        context = self.memory.get_conversation_context(session_id)
        
        # Create streaming task for the agent
        async for response_chunk in self._stream_agent_response(session_id, user_input, context):
            yield response_chunk
            
    async def _stream_agent_response(self, session_id: str, user_input: str, context: str) -> AsyncGenerator[str, None]:
        """Stream the agent's response in real-time"""
        
        # This is a simulation of streaming - in real implementation,
        # this would connect to Claude's streaming API
        
        prompt = f"""
        {context}
        
        Latest user input: "{user_input}"
        
        As Rajeev's personal assistant, respond conversationally to help refine this input.
        Consider which of his four project lanes this might relate to:
        
        1. Podcasting: {PROJECT_LANES['podcasting'].description}
        2. Distillery Lab: {PROJECT_LANES['distillery_lab'].description}
        3. Podcast Bots AI: {PROJECT_LANES['podcast_bots_ai'].description}
        4. Miscellaneous: {PROJECT_LANES['miscellaneous'].description}
        
        Ask clarifying questions, suggest improvements, and help him think through the idea.
        Be conversational and engaging.
        """
        
        # Simulate streaming response (replace with actual Claude streaming)
        response_parts = [
            "I understand you're talking about ",
            "something related to your work. ",
            "Let me help you refine this idea. ",
            "\n\nBased on what you've said, ",
            "this sounds like it might be related to ",
            "your Podcasting work. ",
            "\n\nA few clarifying questions:\n",
            "1. Is this for an upcoming episode?\n",
            "2. Do you need help with scheduling?\n",
            "3. Are there specific guests involved?\n",
            "\nWhat would you like to focus on first?"
        ]
        
        full_response = ""
        for part in response_parts:
            await asyncio.sleep(0.1)  # Simulate streaming delay
            full_response += part
            yield f"data: {json.dumps({'type': 'token', 'content': part})}\n\n"
            
        # Add assistant turn to memory
        self.memory.add_turn(session_id, "assistant", full_response)
        
        # Analyze and update session insights
        await self._analyze_conversation(session_id)
        
        yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
        
    async def _analyze_conversation(self, session_id: str):
        """Analyze conversation to identify topic and suggested lane"""
        
        # This would use the research agent to analyze the conversation
        # For now, we'll do simple keyword matching
        
        session = self.memory.sessions[session_id]
        
        # Combine all user messages
        user_messages = [turn.message for turn in session.turns if turn.speaker == "user"]
        combined_text = " ".join(user_messages).lower()
        
        # Simple lane detection
        lane_scores = {}
        for lane_key, lane_info in PROJECT_LANES.items():
            score = sum(1 for keyword in lane_info.keywords if keyword in combined_text)
            if score > 0:
                lane_scores[lane_key] = score
                
        if lane_scores:
            suggested_lane = max(lane_scores.keys(), key=lambda k: lane_scores[k])
            confidence = lane_scores[suggested_lane] / len(PROJECT_LANES[suggested_lane].keywords)
            
            self.memory.update_session_insights(
                session_id,
                topic=f"Discussion about {suggested_lane.replace('_', ' ')}",
                lane=suggested_lane,
                confidence=confidence
            )
            
    def is_ready_for_processing(self, session_id: str) -> bool:
        """Check if conversation is ready for the next agents"""
        if session_id not in self.memory.sessions:
            return False
            
        session = self.memory.sessions[session_id]
        
        # Simple heuristics for readiness
        return (
            len(session.turns) >= 4 and  # At least 2 exchanges
            session.confidence_score and session.confidence_score > 0.7 and
            session.identified_lane is not None
        )
        
    def get_refined_input_for_next_agents(self, session_id: str) -> Dict[str, Any]:
        """Get refined input ready for research and execution agents"""
        if session_id not in self.memory.sessions:
            return {}
            
        session = self.memory.sessions[session_id]
        
        # Combine user inputs and assistant refinements
        user_inputs = [turn.message for turn in session.turns if turn.speaker == "user"]
        assistant_responses = [turn.message for turn in session.turns if turn.speaker == "assistant"]
        
        return {
            "session_id": session_id,
            "original_input": user_inputs[0] if user_inputs else "",
            "all_user_inputs": user_inputs,
            "assistant_refinements": assistant_responses,
            "identified_topic": session.current_topic,
            "suggested_lane": session.identified_lane,
            "confidence_score": session.confidence_score,
            "ready_for_processing": self.is_ready_for_processing(session_id)
        }

# =============================================================================
# COMMAND LINE INTERFACE (Simulating Web Interface)
# =============================================================================

class ConversationCLI:
    """Command line interface simulating the web microphone interface"""
    
    def __init__(self):
        self.assistant = StreamingPersonalAssistant()
        self.current_session_id = None
        
    async def start_interactive_session(self):
        """Start an interactive conversation session"""
        print("🎤 Personal Assistant - Interactive Mode")
        print("=" * 60)
        print("This simulates the microphone button → conversation workflow")
        print("Type 'quit' to exit, 'new' to start new session")
        print("=" * 60)
        
        while True:
            if not self.current_session_id:
                user_input = input("\n🎤 Start speaking (or 'quit'): ").strip()
                if user_input.lower() == 'quit':
                    break
                if user_input.lower() == 'new':
                    continue
                    
                # Start new session
                self.current_session_id = await self.assistant.start_conversation(user_input)
                print(f"\n🆔 Session started: {self.current_session_id}")
                
                # Get first response
                print("🤖 Assistant:", end=" ")
                await self._stream_response(user_input)
                
            else:
                user_input = input(f"\n🎤 Continue conversation (session {self.current_session_id}): ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'new':
                    self.current_session_id = None
                    continue
                elif user_input.lower() == 'process':
                    # Check if ready to process
                    if self.assistant.is_ready_for_processing(self.current_session_id):
                        refined_input = self.assistant.get_refined_input_for_next_agents(self.current_session_id)
                        print("\n✅ Ready for processing! Refined input:")
                        print(json.dumps(refined_input, indent=2))
                        
                        # Here you would call the research and execution agents
                        print("\n🔄 Would now call Research & Execution agents...")
                        self.current_session_id = None
                    else:
                        print("\n⏳ Not ready for processing yet. Continue conversation...")
                    continue
                    
                # Continue conversation
                print("🤖 Assistant:", end=" ")
                await self._stream_response(user_input)
                
        print("\n👋 Conversation ended!")
        
    async def _stream_response(self, user_input: str):
        """Stream the assistant's response"""
        if not self.current_session_id:
            return
            
        async for chunk in self.assistant.continue_conversation(self.current_session_id, user_input):
            if chunk.startswith("data: "):
                data = json.loads(chunk[6:])
                if data['type'] == 'token':
                    print(data['content'], end='', flush=True)
                elif data['type'] == 'complete':
                    print(f"\n\n💡 Ready to process? Type 'process' or continue conversation...")

# =============================================================================
# TESTING
# =============================================================================

async def test_streaming_conversation():
    """Test the streaming conversation interface"""
    cli = ConversationCLI()
    await cli.start_interactive_session()

if __name__ == "__main__":
    import asyncio
    
    print("🗣️  Streaming Personal Assistant with Memory")
    print("This simulates the Claude-like conversational interface")
    
    asyncio.run(test_streaming_conversation())
