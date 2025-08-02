"""
Context Service - Main FastAPI Application

This module provides the main FastAPI application for the Context Service,
including context management, layering, analytics, and sharing functionality.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="BMAD Context Service",
    description="Enhanced context management and persistence service",
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
SERVICE_NAME = "context-service"
SERVICE_VERSION = "1.0.0"
STARTUP_TIME = datetime.now(timezone.utc)

# Pydantic models
class HealthStatus(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str

class ServiceHealth(BaseModel):
    status: str
    uptime: str
    checks: Dict[str, str]

class ContextLayer(BaseModel):
    layer_id: str
    context_id: str
    layer_type: str
    data: Dict[str, Any]
    created_at: str
    updated_at: str

class ContextAnalytics(BaseModel):
    context_id: str
    total_layers: int
    total_size_mb: float
    access_count: int
    last_accessed: str
    created_at: str

# Mock data for development (replace with database)
CONTEXTS_DB = {
    "agent_execution_001": {
        "id": "agent_execution_001",
        "name": "Agent Execution Context",
        "type": "agent_execution",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "size_mb": 2.5,
        "layer_count": 3,
        "access_count": 15
    },
    "workflow_session_001": {
        "id": "workflow_session_001",
        "name": "Workflow Session Context",
        "type": "workflow_session",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "size_mb": 5.2,
        "layer_count": 5,
        "access_count": 8
    },
    "user_session_001": {
        "id": "user_session_001",
        "name": "User Session Context",
        "type": "user_session",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "size_mb": 1.8,
        "layer_count": 2,
        "access_count": 25
    }
}

# Context layers data
CONTEXT_LAYERS = {
    "agent_execution_001": {
        "layer_1": {
            "layer_id": "layer_1",
            "context_id": "agent_execution_001",
            "layer_type": "input_data",
            "data": {"user_input": "test input", "parameters": {"param1": "value1"}},
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        "layer_2": {
            "layer_id": "layer_2",
            "context_id": "agent_execution_001",
            "layer_type": "agent_state",
            "data": {"agent_id": "architect", "status": "executing", "progress": 0.5},
            "created_at": "2025-01-01T00:01:00Z",
            "updated_at": "2025-01-01T00:01:00Z"
        },
        "layer_3": {
            "layer_id": "layer_3",
            "context_id": "agent_execution_001",
            "layer_type": "output_data",
            "data": {"result": "success", "output": "Generated architecture"},
            "created_at": "2025-01-01T00:02:00Z",
            "updated_at": "2025-01-01T00:02:00Z"
        }
    },
    "workflow_session_001": {
        "layer_1": {
            "layer_id": "layer_1",
            "context_id": "workflow_session_001",
            "layer_type": "workflow_definition",
            "data": {"workflow_id": "wf_001", "steps": ["step1", "step2", "step3"]},
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    }
}

# Context analytics data
CONTEXT_ANALYTICS = {
    "agent_execution_001": {
        "context_id": "agent_execution_001",
        "total_layers": 3,
        "total_size_mb": 2.5,
        "access_count": 15,
        "last_accessed": "2025-01-01T00:02:00Z",
        "created_at": "2025-01-01T00:00:00Z"
    },
    "workflow_session_001": {
        "context_id": "workflow_session_001",
        "total_layers": 5,
        "total_size_mb": 5.2,
        "access_count": 8,
        "last_accessed": "2025-01-01T00:01:30Z",
        "created_at": "2025-01-01T00:00:00Z"
    },
    "user_session_001": {
        "context_id": "user_session_001",
        "total_layers": 2,
        "total_size_mb": 1.8,
        "access_count": 25,
        "last_accessed": "2025-01-01T00:02:15Z",
        "created_at": "2025-01-01T00:00:00Z"
    }
}

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
    
    # Check context service health
    active_contexts = sum(1 for context in CONTEXTS_DB.values() if context["status"] == "active")
    total_contexts = len(CONTEXTS_DB)
    
    checks = {
        "database": "healthy",
        "redis": "healthy",
        "service_discovery": "healthy",
        "context_service": "healthy" if active_contexts == total_contexts else "degraded"
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

# Context management endpoints
@app.get("/contexts", response_model=List[Dict[str, Any]])
async def list_contexts():
    """List all contexts"""
    logger.info("Listing all contexts")
    return list(CONTEXTS_DB.values())

@app.get("/contexts/{context_id}", response_model=Dict[str, Any])
async def get_context(context_id: str):
    """Get context details by ID"""
    logger.info(f"Getting context details for {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    # Update access count
    CONTEXTS_DB[context_id]["access_count"] += 1
    CONTEXTS_DB[context_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    return CONTEXTS_DB[context_id]

@app.post("/contexts", response_model=Dict[str, Any])
async def create_context(context_data: Dict[str, Any]):
    """Create a new context"""
    logger.info(f"Creating new context: {context_data.get('name', 'Unknown')}")
    
    context_id = context_data.get("id")
    if not context_id:
        raise HTTPException(status_code=400, detail="Context ID is required")
    
    if context_id in CONTEXTS_DB:
        raise HTTPException(status_code=409, detail="Context already exists")
    
    # Add metadata
    now = datetime.now(timezone.utc).isoformat()
    context_data["created_at"] = now
    context_data["updated_at"] = now
    context_data["status"] = "active"
    context_data["size_mb"] = 0.0
    context_data["layer_count"] = 0
    context_data["access_count"] = 0
    
    CONTEXTS_DB[context_id] = context_data
    
    # Initialize empty layers and analytics
    CONTEXT_LAYERS[context_id] = {}
    CONTEXT_ANALYTICS[context_id] = {
        "context_id": context_id,
        "total_layers": 0,
        "total_size_mb": 0.0,
        "access_count": 0,
        "last_accessed": now,
        "created_at": now
    }
    
    logger.info(f"Context {context_id} created successfully")
    
    return context_data

@app.put("/contexts/{context_id}", response_model=Dict[str, Any])
async def update_context(context_id: str, context_data: Dict[str, Any]):
    """Update context details"""
    logger.info(f"Updating context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    # Update fields
    context_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    CONTEXTS_DB[context_id].update(context_data)
    
    logger.info(f"Context {context_id} updated successfully")
    
    return CONTEXTS_DB[context_id]

@app.delete("/contexts/{context_id}")
async def delete_context(context_id: str):
    """Delete a context"""
    logger.info(f"Deleting context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    context_data = CONTEXTS_DB.pop(context_id)
    
    # Clean up related data
    CONTEXT_LAYERS.pop(context_id, None)
    CONTEXT_ANALYTICS.pop(context_id, None)
    
    logger.info(f"Context {context_id} deleted successfully")
    
    return {"message": f"Context {context_id} deleted successfully"}

# Context layers endpoints
@app.get("/contexts/{context_id}/layers", response_model=List[Dict[str, Any]])
async def list_context_layers(context_id: str):
    """List all layers for a context"""
    logger.info(f"Listing layers for context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    layers = CONTEXT_LAYERS.get(context_id, {})
    return list(layers.values())

@app.post("/contexts/{context_id}/layers", response_model=Dict[str, Any])
async def add_context_layer(context_id: str, layer_data: Dict[str, Any]):
    """Add a new layer to a context"""
    logger.info(f"Adding layer to context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    layer_id = layer_data.get("layer_id")
    if not layer_id:
        raise HTTPException(status_code=400, detail="Layer ID is required")
    
    if context_id not in CONTEXT_LAYERS:
        CONTEXT_LAYERS[context_id] = {}
    
    if layer_id in CONTEXT_LAYERS[context_id]:
        raise HTTPException(status_code=409, detail="Layer already exists")
    
    # Add metadata
    now = datetime.now(timezone.utc).isoformat()
    layer_data["created_at"] = now
    layer_data["updated_at"] = now
    
    CONTEXT_LAYERS[context_id][layer_id] = layer_data
    
    # Update context metadata
    CONTEXTS_DB[context_id]["layer_count"] += 1
    CONTEXTS_DB[context_id]["updated_at"] = now
    
    # Update analytics
    if context_id in CONTEXT_ANALYTICS:
        CONTEXT_ANALYTICS[context_id]["total_layers"] += 1
        CONTEXT_ANALYTICS[context_id]["last_accessed"] = now
    
    logger.info(f"Layer {layer_id} added to context {context_id}")
    
    return layer_data

@app.get("/contexts/{context_id}/layers/{layer_id}", response_model=Dict[str, Any])
async def get_context_layer(context_id: str, layer_id: str):
    """Get layer details"""
    logger.info(f"Getting layer {layer_id} for context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    if context_id not in CONTEXT_LAYERS or layer_id not in CONTEXT_LAYERS[context_id]:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    return CONTEXT_LAYERS[context_id][layer_id]

@app.put("/contexts/{context_id}/layers/{layer_id}", response_model=Dict[str, Any])
async def update_context_layer(context_id: str, layer_id: str, layer_data: Dict[str, Any]):
    """Update a context layer"""
    logger.info(f"Updating layer {layer_id} for context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    if context_id not in CONTEXT_LAYERS or layer_id not in CONTEXT_LAYERS[context_id]:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    # Update fields
    layer_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    CONTEXT_LAYERS[context_id][layer_id].update(layer_data)
    
    # Update context metadata
    CONTEXTS_DB[context_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    logger.info(f"Layer {layer_id} updated for context {context_id}")
    
    return CONTEXT_LAYERS[context_id][layer_id]

@app.delete("/contexts/{context_id}/layers/{layer_id}")
async def remove_context_layer(context_id: str, layer_id: str):
    """Remove a layer from a context"""
    logger.info(f"Removing layer {layer_id} from context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    if context_id not in CONTEXT_LAYERS or layer_id not in CONTEXT_LAYERS[context_id]:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    layer_data = CONTEXT_LAYERS[context_id].pop(layer_id)
    
    # Update context metadata
    CONTEXTS_DB[context_id]["layer_count"] -= 1
    CONTEXTS_DB[context_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Update analytics
    if context_id in CONTEXT_ANALYTICS:
        CONTEXT_ANALYTICS[context_id]["total_layers"] -= 1
    
    logger.info(f"Layer {layer_id} removed from context {context_id}")
    
    return {"message": f"Layer {layer_id} removed from context {context_id}"}

# Context analytics endpoints
@app.get("/contexts/{context_id}/analytics", response_model=ContextAnalytics)
async def get_context_analytics(context_id: str):
    """Get analytics for a specific context"""
    logger.info(f"Getting analytics for context: {context_id}")
    
    if context_id not in CONTEXTS_DB:
        raise HTTPException(status_code=404, detail="Context not found")
    
    if context_id not in CONTEXT_ANALYTICS:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return ContextAnalytics(**CONTEXT_ANALYTICS[context_id])

@app.get("/contexts/analytics/summary", response_model=Dict[str, Any])
async def get_analytics_summary():
    """Get system-wide analytics summary"""
    logger.info("Getting analytics summary")
    
    total_contexts = len(CONTEXTS_DB)
    total_layers = sum(len(layers) for layers in CONTEXT_LAYERS.values())
    total_size_mb = sum(context["size_mb"] for context in CONTEXTS_DB.values())
    total_access_count = sum(context["access_count"] for context in CONTEXTS_DB.values())
    
    summary = {
        "total_contexts": total_contexts,
        "total_layers": total_layers,
        "total_size_mb": total_size_mb,
        "total_access_count": total_access_count,
        "average_layers_per_context": total_layers / total_contexts if total_contexts > 0 else 0,
        "average_size_mb_per_context": total_size_mb / total_contexts if total_contexts > 0 else 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return summary

@app.get("/contexts/analytics/trends", response_model=Dict[str, Any])
async def get_analytics_trends():
    """Get usage trends"""
    logger.info("Getting analytics trends")
    
    # Mock trends data
    trends = {
        "context_creation_trend": [
            {"date": "2025-01-01", "count": 5},
            {"date": "2025-01-02", "count": 8},
            {"date": "2025-01-03", "count": 12}
        ],
        "layer_usage_trend": [
            {"date": "2025-01-01", "count": 15},
            {"date": "2025-01-02", "count": 22},
            {"date": "2025-01-03", "count": 35}
        ],
        "access_trend": [
            {"date": "2025-01-01", "count": 45},
            {"date": "2025-01-02", "count": 67},
            {"date": "2025-01-03", "count": 89}
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return trends

# Service information
@app.get("/info")
async def service_info():
    """Get service information"""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Enhanced context management and persistence service",
        "startup_time": STARTUP_TIME.isoformat(),
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME),
        "contexts_count": len(CONTEXTS_DB),
        "total_layers": sum(len(layers) for layers in CONTEXT_LAYERS.values()),
        "endpoints": [
            "/health",
            "/contexts",
            "/contexts/{id}/layers",
            "/contexts/{id}/analytics",
            "/contexts/analytics/summary"
        ]
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info("Context Service is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {SERVICE_NAME}")
    logger.info("Context Service is shutting down...")

# Main entry point
if __name__ == "__main__":
    host = os.getenv("CONTEXT_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("CONTEXT_SERVICE_PORT", "8003"))
    debug = os.getenv("CONTEXT_SERVICE_DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 