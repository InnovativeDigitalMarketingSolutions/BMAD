"""
Agent Service - Main FastAPI Application

This module provides the main FastAPI application for the Agent Service,
including health checks, agent management endpoints, and service discovery.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="BMAD Agent Service",
    description="Agent lifecycle management, execution, and coordination service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Service metadata
SERVICE_NAME = "agent-service"
SERVICE_VERSION = "1.0.0"
STARTUP_TIME = datetime.now(timezone.utc)

# Mock data for development (replace with database)
AGENTS_DB = {
    "architect": {
        "id": "architect",
        "name": "Architect",
        "type": "system_design",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "last_execution": None
    },
    "backend": {
        "id": "backend",
        "name": "Backend Developer",
        "type": "development",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "last_execution": None
    },
    "frontend": {
        "id": "frontend",
        "name": "Frontend Developer",
        "type": "development",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "last_execution": None
    }
}

# Health check models
from pydantic import BaseModel

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str

class ServiceHealth(BaseModel):
    status: str
    uptime: str
    checks: Dict[str, str]

# Event models
class AgentEvent:
    def __init__(self, event_type: str, agent_id: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.agent_id = agent_id
        self.data = data
        self.timestamp = datetime.now(timezone.utc).isoformat()

# Health check endpoints
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint"""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )

@app.get("/health/ready", response_model=ServiceHealth)
async def readiness_check():
    """Readiness probe for Kubernetes"""
    uptime = str(datetime.now(timezone.utc) - STARTUP_TIME)
    checks = {
        "database": "healthy",
        "redis": "healthy",
        "service_discovery": "healthy"
    }
    
    return ServiceHealth(
        status="ready",
        uptime=uptime,
        checks=checks
    )

@app.get("/health/live", response_model=HealthStatus)
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return HealthStatus(
        status="alive",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )

# Agent management endpoints
@app.get("/agents", response_model=List[Dict[str, Any]])
async def list_agents():
    """List all registered agents"""
    logger.info("Listing all agents")
    return list(AGENTS_DB.values())

# Agent discovery endpoints (must come before /agents/{agent_id} routes)
@app.get("/agents/discover")
async def discover_agents():
    """Discover available agents"""
    logger.info("Discovering available agents")
    
    # Mock discovery - in real implementation, this would query service discovery
    discovered_agents = []
    for agent_id, agent in AGENTS_DB.items():
        if agent["status"] == "active":
            discovered_agents.append({
                "id": agent_id,
                "name": agent["name"],
                "type": agent["type"],
                "version": agent["version"]
            })
    
    return {
        "discovered_agents": discovered_agents,
        "total_count": len(discovered_agents),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/agents/types")
async def list_agent_types():
    """List available agent types"""
    logger.info("Listing agent types")
    
    types = set(agent["type"] for agent in AGENTS_DB.values())
    
    return {
        "agent_types": list(types),
        "total_types": len(types),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: str):
    """Get agent details by ID"""
    logger.info(f"Getting agent details for {agent_id}")
    
    if agent_id not in AGENTS_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AGENTS_DB[agent_id]

@app.post("/agents", response_model=Dict[str, Any])
async def register_agent(agent_data: Dict[str, Any]):
    """Register a new agent"""
    logger.info(f"Registering new agent: {agent_data.get('name', 'Unknown')}")
    
    agent_id = agent_data.get("id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent ID is required")
    
    if agent_id in AGENTS_DB:
        raise HTTPException(status_code=409, detail="Agent already exists")
    
    # Add metadata
    agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
    agent_data["status"] = "active"
    agent_data["last_execution"] = None
    
    AGENTS_DB[agent_id] = agent_data
    
    # Publish event (mock)
    event = AgentEvent("agent.registered", agent_id, agent_data)
    logger.info(f"Published event: {event.event_type}")
    
    return agent_data

@app.put("/agents/{agent_id}", response_model=Dict[str, Any])
async def update_agent(agent_id: str, agent_data: Dict[str, Any]):
    """Update agent details"""
    logger.info(f"Updating agent: {agent_id}")
    
    if agent_id not in AGENTS_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields
    AGENTS_DB[agent_id].update(agent_data)
    
    # Publish event (mock)
    event = AgentEvent("agent.updated", agent_id, agent_data)
    logger.info(f"Published event: {event.event_type}")
    
    return AGENTS_DB[agent_id]

@app.delete("/agents/{agent_id}")
async def deregister_agent(agent_id: str):
    """Deregister an agent"""
    logger.info(f"Deregistering agent: {agent_id}")
    
    if agent_id not in AGENTS_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_data = AGENTS_DB.pop(agent_id)
    
    # Publish event (mock)
    event = AgentEvent("agent.deregistered", agent_id, agent_data)
    logger.info(f"Published event: {event.event_type}")
    
    return {"message": f"Agent {agent_id} deregistered successfully"}

# Agent execution endpoints
@app.post("/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, execution_data: Dict[str, Any] = None):
    """Execute an agent"""
    logger.info(f"Executing agent: {agent_id}")
    
    if agent_id not in AGENTS_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = AGENTS_DB[agent_id]
    if agent["status"] != "active":
        raise HTTPException(status_code=400, detail="Agent is not active")
    
    # Mock execution
    execution_id = f"exec_{agent_id}_{datetime.now(timezone.utc).timestamp()}"
    
    # Update agent status
    AGENTS_DB[agent_id]["last_execution"] = datetime.now(timezone.utc).isoformat()
    
    # Publish event (mock)
    event = AgentEvent("agent.executed", agent_id, {
        "execution_id": execution_id,
        "data": execution_data or {}
    })
    logger.info(f"Published event: {event.event_type}")
    
    return {
        "execution_id": execution_id,
        "agent_id": agent_id,
        "status": "started",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent execution status"""
    logger.info(f"Getting status for agent: {agent_id}")
    
    if agent_id not in AGENTS_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = AGENTS_DB[agent_id]
    
    return {
        "agent_id": agent_id,
        "status": agent["status"],
        "last_execution": agent["last_execution"],
        "version": agent["version"]
    }

@app.post("/agents/{agent_id}/stop")
async def stop_agent_execution(agent_id: str):
    """Stop agent execution"""
    logger.info(f"Stopping execution for agent: {agent_id}")
    
    if agent_id not in AGENTS_DB:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Mock stop execution
    # Publish event (mock)
    event = AgentEvent("agent.stopped", agent_id, {})
    logger.info(f"Published event: {event.event_type}")
    
    return {
        "agent_id": agent_id,
        "status": "stopped",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
# Service information
@app.get("/info")
async def service_info():
    """Get service information"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Agent lifecycle management, execution, and coordination service",
        "startup_time": STARTUP_TIME.isoformat(),
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME),
        "endpoints": [
            "/health",
            "/agents",
            "/agents/discover",
            "/agents/types"
        ]
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info("Agent Service is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {SERVICE_NAME}")
    logger.info("Agent Service is shutting down...")

# Main entry point
if __name__ == "__main__":
    host = os.getenv("AGENT_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_SERVICE_PORT", "8001"))
    debug = os.getenv("AGENT_SERVICE_DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 