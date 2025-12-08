#!/usr/bin/env python3
"""
Agent Orchestrator - Central Coordinator for Chennai Tech Intelligence
=====================================================================

Manages and coordinates multiple AI agents for comprehensive Chennai tech ecosystem monitoring.

Features:
- Agent lifecycle management
- Intelligent task distribution
- Data aggregation and correlation  
- Performance monitoring
- Fault tolerance and recovery
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Import all our specialized agents
from agents.job_market_scout import JobMarketScout
from agents.salary_intelligence import SalaryIntelligenceAgent
from agents.tech_stack_monitor import TechStackMonitor  
from agents.startup_tracker import StartupEcosystemTracker
from agents.community_pulse import CommunityPulseAgent

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Performance metrics for each agent"""
    name: str
    status: str = "initializing"
    last_update: Optional[datetime] = None
    total_updates: int = 0
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    data_points_collected: int = 0
    errors_count: int = 0
    last_error: Optional[str] = None

class AgentOrchestrator:
    """
    Central orchestrator managing all Chennai tech intelligence agents
    
    Responsibilities:
    - Initialize and manage agent lifecycle
    - Coordinate data gathering operations
    - Aggregate intelligence from multiple sources
    - Monitor agent performance and health
    - Handle failures and implement recovery strategies
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agents"""
        
        # Agent fleet
        self.agents: Dict[str, Any] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        
        # Orchestrator state
        self.is_running = False
        self.last_intelligence_update = None
        self.intelligence_cache = {}
        
        logger.info("🎯 Agent Orchestrator initialized")
    
    async def initialize_agents(self):
        """Initialize all AI agents with their specific configurations"""
        
        try:
            logger.info("🚀 Initializing Chennai Tech Intelligence Agent Fleet")
            
            # Initialize Job Market Scout Agent
            self.agents["job_market_scout"] = JobMarketScout(
                name="Job Market Scout",
                focus_area="Chennai IT Jobs",
                update_frequency=300  # 5 minutes
            )
            self.agent_metrics["job_market_scout"] = AgentMetrics(
                name="Job Market Scout"
            )
            
            # Initialize Salary Intelligence Agent
            self.agents["salary_intelligence"] = SalaryIntelligenceAgent(
                name="Salary Intelligence",
                focus_area="Chennai Tech Compensation", 
                update_frequency=600  # 10 minutes
            )
            self.agent_metrics["salary_intelligence"] = AgentMetrics(
                name="Salary Intelligence"
            )
            
            # Initialize Tech Stack Monitor Agent
            self.agents["tech_stack_monitor"] = TechStackMonitor(
                name="Tech Stack Monitor",
                focus_area="Chennai Technology Trends",
                update_frequency=900  # 15 minutes
            )
            self.agent_metrics["tech_stack_monitor"] = AgentMetrics(
                name="Tech Stack Monitor"
            )
            
            # Initialize Startup Ecosystem Tracker
            self.agents["startup_tracker"] = StartupEcosystemTracker(
                name="Startup Tracker", 
                focus_area="Chennai Startup Ecosystem",
                update_frequency=1800  # 30 minutes
            )
            self.agent_metrics["startup_tracker"] = AgentMetrics(
                name="Startup Tracker"
            )
            
            # Initialize Community Pulse Agent
            self.agents["community_pulse"] = CommunityPulseAgent(
                name="Community Pulse",
                focus_area="Chennai Tech Community", 
                update_frequency=3600  # 60 minutes
            )
            self.agent_metrics["community_pulse"] = AgentMetrics(
                name="Community Pulse"
            )
            
            # Initialize all agents
            for agent_name, agent in self.agents.items():
                try:
                    await agent.initialize()
                    self.agent_metrics[agent_name].status = "ready"
                    logger.info(f"✅ {agent_name} initialized successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {agent_name}: {e}")
                    self.agent_metrics[agent_name].status = "error"
                    self.agent_metrics[agent_name].last_error = str(e)
            
            self.is_running = True
            logger.info("🎉 All agents initialized and ready for intelligence gathering")
            
        except Exception as e:
            logger.error(f"❌ Critical error initializing agents: {e}")
            raise
    
    async def gather_intelligence(self) -> Dict[str, Any]:
        """
        Coordinate intelligence gathering from all agents
        
        Returns consolidated intelligence report
        """
        
        if not self.is_running:
            logger.warning("⚠️ Orchestrator not running, cannot gather intelligence")
            return {}
        
        logger.info("🔍 Starting coordinated intelligence gathering")
        
        intelligence_report = {
            "timestamp": datetime.now().isoformat(),
            "job_market": {},
            "salary_trends": {},
            "tech_stack": {}, 
            "startup_activity": {},
            "community_events": {},
            "system_health": {}
        }
        
        # Gather data from each agent concurrently
        gathering_tasks = []
        
        for agent_name, agent in self.agents.items():
            if self.agent_metrics[agent_name].status == "ready":
                task = asyncio.create_task(
                    self._gather_from_agent(agent_name, agent),
                    name=f"gather_{agent_name}"
                )
                gathering_tasks.append((agent_name, task))
        
        # Wait for all agents to complete (with timeout)
        completed_data = {}
        
        for agent_name, task in gathering_tasks:
            try:
                # 60-second timeout per agent
                agent_data = await asyncio.wait_for(task, timeout=60.0)
                completed_data[agent_name] = agent_data
                
                # Update metrics
                self.agent_metrics[agent_name].last_update = datetime.now()
                self.agent_metrics[agent_name].total_updates += 1
                self.agent_metrics[agent_name].status = "ready"
                
                logger.info(f"✅ {agent_name} completed intelligence gathering")
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ {agent_name} timed out during intelligence gathering")
                self.agent_metrics[agent_name].errors_count += 1
                self.agent_metrics[agent_name].last_error = "Timeout"
                
            except Exception as e:
                logger.error(f"❌ {agent_name} failed during intelligence gathering: {e}")
                self.agent_metrics[agent_name].errors_count += 1
                self.agent_metrics[agent_name].last_error = str(e)
        
        # Aggregate intelligence data
        intelligence_report.update(self._aggregate_intelligence(completed_data))
        
        # Cache the latest intelligence
        self.intelligence_cache = intelligence_report
        self.last_intelligence_update = datetime.now()
        
        logger.info(f"🎯 Intelligence gathering completed: {len(completed_data)} agents contributed")
        
        return intelligence_report
    
    async def _gather_from_agent(self, agent_name: str, agent) -> Dict[str, Any]:
        """Gather intelligence from a specific agent"""
        
        start_time = datetime.now()
        
        try:
            # Each agent has a gather_intelligence method
            data = await agent.gather_intelligence()
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            self.agent_metrics[agent_name].avg_response_time = response_time
            
            # Count data points
            if isinstance(data, dict):
                self.agent_metrics[agent_name].data_points_collected = len(data)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Agent {agent_name} gathering failed: {e}")
            raise
    
    def _aggregate_intelligence(self, agent_data: Dict[str, Dict]) -> Dict[str, Any]:
        """Aggregate and correlate intelligence from multiple agents"""
        
        aggregated = {
            "job_market": agent_data.get("job_market_scout", {}),
            "salary_trends": agent_data.get("salary_intelligence", {}), 
            "tech_stack": agent_data.get("tech_stack_monitor", {}),
            "startup_activity": agent_data.get("startup_tracker", {}),
            "community_events": agent_data.get("community_pulse", {}),
        }
        
        # Add cross-correlation insights
        aggregated["insights"] = self._generate_cross_insights(agent_data)
        
        # Add system health
        aggregated["system_health"] = self._generate_system_health()
        
        return aggregated
    
    def _generate_cross_insights(self, agent_data: Dict) -> Dict[str, Any]:
        """Generate insights by correlating data across agents"""
        
        insights = {
            "market_temperature": "moderate",  # Based on job + startup activity
            "skill_demand_alignment": {},      # Jobs vs tech trends
            "compensation_fairness": {},       # Salary vs market activity
            "community_engagement": "active",  # Events vs job market
            "growth_indicators": []            # Combined metrics
        }
        
        # This is where sophisticated AI analysis would happen
        # For demo purposes, we'll return structured placeholder data
        
        return insights
    
    def _generate_system_health(self) -> Dict[str, Any]:
        """Generate overall system health metrics"""
        
        total_agents = len(self.agents)
        ready_agents = sum(1 for m in self.agent_metrics.values() if m.status == "ready")
        
        return {
            "agents_operational": f"{ready_agents}/{total_agents}",
            "overall_health": "healthy" if ready_agents == total_agents else "degraded",
            "last_update": self.last_intelligence_update.isoformat() if self.last_intelligence_update else None,
            "data_quality": "high" if ready_agents >= total_agents * 0.8 else "moderate"
        }
    
    async def get_agent_count(self) -> int:
        """Get number of active agents"""
        return len(self.agents)
    
    async def get_agent_statuses(self) -> List[Dict]:
        """Get basic status of all agents"""
        return [
            {
                "name": metrics.name,
                "status": metrics.status,
                "last_update": metrics.last_update.isoformat() if metrics.last_update else None
            }
            for metrics in self.agent_metrics.values()
        ]
    
    async def get_detailed_agent_statuses(self) -> List[Dict]:
        """Get detailed metrics for all agents"""
        return [
            {
                "agent_name": metrics.name,
                "status": metrics.status,
                "last_update": metrics.last_update.isoformat() if metrics.last_update else None,
                "data_points_collected": metrics.data_points_collected,
                "success_rate": metrics.success_rate,
                "total_updates": metrics.total_updates,
                "errors_count": metrics.errors_count,
                "avg_response_time": metrics.avg_response_time
            }
            for metrics in self.agent_metrics.values()
        ]
    
    async def get_latest_intelligence(self) -> Dict[str, Any]:
        """Get the most recent intelligence data"""
        
        if not self.intelligence_cache:
            # If no cache, return empty structure
            return {
                "timestamp": datetime.now().isoformat(),
                "job_market": {"status": "no_data", "message": "Gathering initial data..."},
                "salary_trends": {"status": "no_data", "message": "Gathering initial data..."},
                "tech_stack": {"status": "no_data", "message": "Gathering initial data..."},
                "startup_activity": {"status": "no_data", "message": "Gathering initial data..."},
                "community_events": {"status": "no_data", "message": "Gathering initial data..."}
            }
        
        return self.intelligence_cache
    
    async def get_agent_data(self, agent_name: str) -> Dict[str, Any]:
        """Get specific data from a particular agent"""
        
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}
        
        try:
            return await self.agents[agent_name].get_latest_data()
        except Exception as e:
            return {"error": f"Failed to get data from {agent_name}: {str(e)}"}
    
    async def trigger_agent_update(self, agent_name: str):
        """Manually trigger an update from a specific agent"""
        
        if agent_name not in self.agents:
            logger.error(f"❌ Agent {agent_name} not found")
            return
        
        try:
            logger.info(f"🔄 Triggering update for {agent_name}")
            await self.agents[agent_name].force_update()
            logger.info(f"✅ {agent_name} update completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to trigger update for {agent_name}: {e}")
    
    async def shutdown_agents(self):
        """Gracefully shutdown all agents"""
        
        logger.info("📴 Shutting down all agents")
        
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.info(f"✅ {agent_name} shut down successfully")
                
            except Exception as e:
                logger.error(f"❌ Error shutting down {agent_name}: {e}")
        
        self.is_running = False
        logger.info("🔚 All agents shut down")