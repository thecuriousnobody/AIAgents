#!/usr/bin/env python3
"""
FastAPI Backend for Personal Assistant
=====================================

Clean API backend for the NPM frontend to communicate with.
Handles audio transcription, agent responses, and workflow orchestration.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Local imports
from whisper_integration import WhisperTranscriber
from personal_assistant_system import PersonalAssistantWorkflow, PersonalAssistantAgents
from airtable_integration import AirtableManager
from task_management_agent import TaskManagementAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Assistant API",
    description="Backend API for the Personal Assistant web interface",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://127.0.0.1:3000"],  # Common frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
whisper_transcriber = WhisperTranscriber("base")
assistant_workflow = PersonalAssistantWorkflow()

# Initialize Airtable integration (optional - will be None if not configured)
airtable_manager = None
task_management_agent = None

try:
    airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
    airtable_api_key = os.getenv("AIRTABLE_API_KEY")
    
    if airtable_base_id and airtable_api_key:
        airtable_manager = AirtableManager(airtable_base_id, airtable_api_key)
        task_management_agent = TaskManagementAgent(airtable_manager)
        logger.info("✅ Airtable integration initialized")
    else:
        logger.info("⚠️ Airtable credentials not found - task management disabled")
except Exception as e:
    logger.error(f"❌ Airtable initialization failed: {e}")

# Session storage
sessions: Dict[str, Dict[str, Any]] = {}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_conversational_response(transcription: str) -> str:
    """Get a conversational response from the personal assistant agent"""
    try:
        # Use the new personal assistant response method
        response = assistant_workflow.get_personal_assistant_response(transcription)
        return response
        
    except Exception as e:
        logger.error(f"Conversational response error: {e}")
        return f"I understand you said: '{transcription}'. Let me help you with that. Which project lane should I focus on - Podcasting, Distillery Lab, Podcast Bots AI, or something else?"

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Personal Assistant API",
        "version": "1.0.0",
        "whisper_status": "loaded" if whisper_transcriber.is_loaded else "not_loaded",
        "endpoints": {
            "transcribe": "POST /transcribe - Upload audio for transcription",
            "chat": "POST /chat - Get conversational response",
            "approve": "POST /approve - Approve and trigger full workflow",
            "sessions": "GET /sessions - View active sessions"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "whisper_loaded": whisper_transcriber.is_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """
    Transcribe uploaded audio file
    
    Args:
        audio: Audio file (WAV, MP3, etc.)
        session_id: Optional session ID for tracking
        
    Returns:
        Transcription results
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Transcribe the audio
        result = whisper_transcriber.transcribe_audio_file(temp_file_path)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Store in session
        if session_id not in sessions:
            sessions[session_id] = {"created_at": datetime.now().isoformat()}
        
        sessions[session_id].update({
            "transcription": result["text"],
            "transcription_confidence": result.get("confidence", 0.8),
            "transcription_timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "transcription": result["text"],
            "confidence": result.get("confidence", 0.8),
            "language": result.get("language", "en"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/chat")
async def chat_with_assistant(request_data: dict):
    """
    Get conversational response from the personal assistant
    
    Args:
        request_data: JSON with 'message' and optional 'session_id'
        
    Returns:
        Conversational response
    """
    try:
        message = request_data.get("message", "")
        session_id = request_data.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get conversational response
        response = get_conversational_response(message)
        
        # Store in session
        if session_id not in sessions:
            sessions[session_id] = {"created_at": datetime.now().isoformat()}
        
        sessions[session_id].update({
            "user_message": message,
            "agent_response": response,
            "chat_timestamp": datetime.now().isoformat(),
            "status": "awaiting_approval"
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/approve")
async def approve_and_execute(request_data: dict):
    """
    Approve the conversation and trigger full workflow
    
    Args:
        request_data: JSON with 'session_id' and optional 'action'
        
    Returns:
        Workflow execution results
    """
    try:
        session_id = request_data.get("session_id")
        action = request_data.get("action", "approve")
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Get the original message/transcription
        original_input = session.get("transcription") or session.get("user_message", "")
        
        if not original_input:
            raise HTTPException(status_code=400, detail="No input to process")
        
        # Trigger full workflow (all 3 agents)
        workflow_result = assistant_workflow.process_speech_input(original_input)
        
        # Create tasks in Airtable if configured
        task_results = None
        if task_management_agent:
            try:
                # Prepare conversation data for task creation
                conversation_data = {
                    "user_input": original_input,
                    "agent_response": session.get("agent_response", ""),
                    "project_lane": "miscellaneous",  # Default - will be determined by agent
                    "session_id": session_id
                }
                
                # Create tasks
                task_results = task_management_agent.process_conversation_for_tasks(conversation_data)
                logger.info(f"Task creation result: {task_results.get('success', False)}")
                
            except Exception as e:
                logger.error(f"Task creation failed: {e}")
                task_results = {"success": False, "error": str(e)}
        else:
            logger.info("Task management not configured - skipping task creation")
        
        # Update session
        session.update({
            "approved_at": datetime.now().isoformat(),
            "workflow_result": workflow_result,
            "task_results": task_results,
            "status": "completed"
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Workflow completed successfully",
            "workflow_session_id": workflow_result.get("session_id"),
            "task_results": task_results,
            "tasks_created": task_results.get("tasks_created", []) if task_results else [],
            "timestamp": workflow_result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Approval error: {e}")
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@app.post("/reject")
async def reject_response(request_data: dict):
    """
    Reject the current response
    
    Args:
        request_data: JSON with 'session_id' and optional 'reason'
        
    Returns:
        Acknowledgment
    """
    try:
        session_id = request_data.get("session_id")
        reason = request_data.get("reason", "")
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session
        sessions[session_id].update({
            "rejected_at": datetime.now().isoformat(),
            "rejection_reason": reason,
            "status": "rejected"
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Response rejected",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Rejection error: {e}")
        raise HTTPException(status_code=500, detail=f"Rejection failed: {str(e)}")

@app.post("/feedback")
async def provide_feedback(request_data: dict):
    """
    Provide feedback for improvement
    
    Args:
        request_data: JSON with 'session_id' and 'feedback'
        
    Returns:
        Acknowledgment
    """
    try:
        session_id = request_data.get("session_id")
        feedback = request_data.get("feedback", "")
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store feedback
        sessions[session_id].update({
            "feedback": feedback,
            "feedback_timestamp": datetime.now().isoformat(),
            "status": "feedback_provided"
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Feedback received",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")

@app.post("/refine")
async def refine_understanding(request_data: dict):
    """
    Refine the agent's understanding with additional context
    
    Args:
        request_data: JSON with 'session_id', 'conversation_context', and 'refinement'
        
    Returns:
        Refined response from the agent
    """
    try:
        session_id = request_data.get("session_id")
        conversation_context = request_data.get("conversation_context", "")
        refinement = request_data.get("refinement", "")
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not refinement:
            raise HTTPException(status_code=400, detail="Refinement text is required")
        
        # Get the current session data
        session = sessions[session_id]
        
        # Build the refined prompt for the agent
        refined_prompt = f"""
        You are refining your understanding based on additional context from the user.
        
        CONVERSATION CONTEXT:
        {conversation_context}
        
        The user has provided additional details to refine your understanding. 
        Please provide an updated, more comprehensive response that incorporates:
        1. Your previous understanding
        2. The new information provided
        3. A refined analysis of which project lane this belongs to
        4. Updated suggestions and next steps
        
        Be conversational and show that you've incorporated the new information thoughtfully.
        """
        
        # Get refined response from the agent
        refined_response = assistant_workflow.refine_understanding(conversation_context, refinement)
        
        # Update session with refined understanding
        session.update({
            "refined_response": refined_response,
            "refinement_history": session.get("refinement_history", []) + [{
                "refinement": refinement,
                "response": refined_response,
                "timestamp": datetime.now().isoformat()
            }],
            "status": "refined",
            "refinement_timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "session_id": session_id,
            "refined_response": refined_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Refinement error: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@app.get("/sessions")
async def get_sessions():
    """Get all active sessions (for debugging)"""
    return {
        "sessions": sessions,
        "total_sessions": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get specific session details"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "session_data": sessions[session_id],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/airtable/test")
async def test_airtable_connection():
    """Test Airtable connection and configuration"""
    if not airtable_manager:
        return {
            "airtable_configured": False,
            "message": "Airtable not configured. Set AIRTABLE_BASE_ID and AIRTABLE_API_KEY environment variables."
        }
    
    try:
        test_result = airtable_manager.test_connection()
        return {
            "airtable_configured": True,
            "connection_test": test_result,
            "message": "Airtable integration ready" if test_result["success"] else "Airtable connection failed"
        }
    except Exception as e:
        return {
            "airtable_configured": True,
            "connection_test": {"success": False, "error": str(e)},
            "message": f"Airtable test failed: {e}"
        }

@app.post("/airtable/create-test-task")
async def create_test_task():
    """Create a test task in Airtable"""
    if not airtable_manager:
        raise HTTPException(status_code=400, detail="Airtable not configured")
    
    try:
        result = airtable_manager.create_task(
            title="Test Task from Personal Assistant API",
            description=f"This is a test task created at {datetime.now().isoformat()}",
            lane="miscellaneous",
            status="not_started"
        )
        return result
    except Exception as e:
        logger.error(f"Test task creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")

# =============================================================================
# STARTUP
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("Starting Personal Assistant API...")
    
    # Load Whisper model
    logger.info("Loading Whisper model...")
    if whisper_transcriber.load_model():
        logger.info("✅ Whisper model loaded successfully")
    else:
        logger.error("❌ Failed to load Whisper model")
    
    logger.info("🚀 Personal Assistant API ready!")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Personal Assistant API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
