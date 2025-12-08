#!/usr/bin/env python3
"""
Chennai Tech Intelligence Hub - Main API Server
==============================================

FastAPI backend coordinating multiple AI agents for real-time Chennai tech ecosystem monitoring.

Features:
- Multi-agent orchestration
- Real-time WebSocket updates  
- Async data processing
- RESTful API endpoints
- Professional error handling
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents.job_market_scout import JobMarketScout
from agents.salary_intelligence import SalaryIntelligenceAgent  
from agents.tech_stack_monitor import TechStackMonitor
from agents.startup_tracker import StartupEcosystemTracker
from agents.community_pulse import CommunityPulseAgent
from core.agent_orchestrator import AgentOrchestrator
from core.data_pipeline import DataPipeline
from core.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Chennai Tech Intelligence Hub",
    description="AI-powered real-time monitoring of Chennai's IT ecosystem",
    version="1.0.0",
    docs_url="/api/docs"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global State & Managers
# ============================================================================

# Initialize agent orchestrator and WebSocket manager
orchestrator = AgentOrchestrator()
websocket_manager = WebSocketManager()
data_pipeline = DataPipeline()

# ============================================================================
# Data Models
# ============================================================================

class AgentStatus(BaseModel):
    agent_name: str
    status: str
    last_update: datetime
    data_points_collected: int
    success_rate: float

class TechIntelligenceResponse(BaseModel):
    timestamp: datetime
    job_market: Dict
    salary_trends: Dict  
    tech_stack: Dict
    startup_activity: Dict
    community_events: Dict
    system_health: Dict

class AlertMessage(BaseModel):
    type: str
    priority: str
    message: str
    timestamp: datetime
    agent_source: str

# ============================================================================
# Startup & Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize all agents and start background monitoring"""
    logger.info("🚀 Starting Chennai Tech Intelligence Hub")
    
    # Initialize AI agents
    await orchestrator.initialize_agents()
    
    # Start background data collection
    asyncio.create_task(background_intelligence_gathering())
    
    logger.info("✅ All agents initialized and monitoring started")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup resources"""
    logger.info("📴 Shutting down Chennai Tech Intelligence Hub")
    await orchestrator.shutdown_agents()

# ============================================================================
# Background Tasks  
# ============================================================================

async def background_intelligence_gathering():
    """Continuously gather intelligence from all agents"""
    
    while True:
        try:
            logger.info("🔄 Starting intelligence gathering cycle")
            
            # Coordinate all agents to gather data
            intelligence = await orchestrator.gather_intelligence()
            
            # Process and store data
            await data_pipeline.process_intelligence(intelligence)
            
            # Broadcast updates to WebSocket clients
            await websocket_manager.broadcast_update(intelligence)
            
            logger.info(f"✅ Intelligence cycle completed: {len(intelligence)} data points")
            
            # Wait before next cycle (30 seconds for demo, would be longer in production)
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"❌ Error in intelligence gathering: {e}")
            await asyncio.sleep(60)  # Wait longer on error

# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/", response_class=JSONResponse)
async def root():
    """API health check and info"""
    return {
        "service": "Chennai Tech Intelligence Hub",
        "status": "operational", 
        "version": "1.0.0",
        "active_agents": await orchestrator.get_agent_count(),
        "uptime": datetime.now().isoformat(),
        "docs": "/api/docs"
    }

@app.get("/api/health", response_model=Dict)
async def health_check():
    """Detailed system health check"""
    
    agent_statuses = await orchestrator.get_agent_statuses()
    
    return {
        "system_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": agent_statuses,
        "data_pipeline": await data_pipeline.get_status(),
        "websocket_connections": websocket_manager.connection_count()
    }

@app.get("/api/intelligence", response_model=TechIntelligenceResponse) 
async def get_current_intelligence():
    """Get latest intelligence from all agents"""
    
    try:
        intelligence = await orchestrator.get_latest_intelligence()
        
        return TechIntelligenceResponse(
            timestamp=datetime.now(),
            job_market=intelligence.get("job_market", {}),
            salary_trends=intelligence.get("salary_trends", {}),
            tech_stack=intelligence.get("tech_stack", {}), 
            startup_activity=intelligence.get("startup_activity", {}),
            community_events=intelligence.get("community_events", {}),
            system_health=intelligence.get("system_health", {})
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting intelligence: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve intelligence data"}
        )

@app.get("/api/agents", response_model=List[AgentStatus])
async def get_agent_statuses():
    """Get status of all AI agents"""
    return await orchestrator.get_detailed_agent_statuses()

@app.get("/api/job-market")
async def get_job_market_intelligence():
    """Get detailed job market analysis"""
    return await orchestrator.get_agent_data("job_market_scout")

@app.get("/api/salaries")
async def get_salary_intelligence():
    """Get salary and compensation analysis"""
    return await orchestrator.get_agent_data("salary_intelligence")

@app.get("/api/tech-trends")
async def get_tech_stack_intelligence():
    """Get technology trend analysis"""
    return await orchestrator.get_agent_data("tech_stack_monitor")

@app.get("/api/startups")
async def get_startup_intelligence():
    """Get startup ecosystem analysis"""
    return await orchestrator.get_agent_data("startup_tracker")

@app.get("/api/community")
async def get_community_intelligence():
    """Get community and events analysis"""
    return await orchestrator.get_agent_data("community_pulse")

@app.post("/api/agents/{agent_name}/trigger")
async def trigger_agent_update(agent_name: str, background_tasks: BackgroundTasks):
    """Manually trigger an agent to update its data"""
    
    background_tasks.add_task(orchestrator.trigger_agent_update, agent_name)
    
    return {
        "message": f"Agent {agent_name} update triggered",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# WebSocket Endpoint for Real-time Updates
# ============================================================================

@app.websocket("/ws/intelligence")
async def websocket_intelligence_feed(websocket: WebSocket):
    """Real-time intelligence feed via WebSocket"""
    
    await websocket_manager.connect(websocket)
    
    try:
        # Send initial data
        initial_data = await orchestrator.get_latest_intelligence()
        await websocket.send_json({
            "type": "initial_data",
            "data": initial_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"📨 Received WebSocket message: {data}")
                
                # Echo back for connection testing
                await websocket.send_json({
                    "type": "echo",
                    "message": "Connection active",
                    "timestamp": datetime.now().isoformat()
                })
                
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
    finally:
        websocket_manager.disconnect(websocket)

# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    logger.info("🌟 Starting Chennai Tech Intelligence Hub API Server")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )