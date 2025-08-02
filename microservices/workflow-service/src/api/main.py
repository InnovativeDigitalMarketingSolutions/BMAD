"""
Workflow Service - Main FastAPI Application

This module provides the main FastAPI application for the Workflow Service,
including workflow management, execution, monitoring, and orchestration functionality.
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
    title="BMAD Workflow Service",
    description="Workflow orchestration and management service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize core components
from ..core.workflow_manager import WorkflowManager, Workflow, WorkflowExecution, WorkflowType, WorkflowStatus
from ..core.workflow_store import WorkflowStore
from ..core.workflow_validator import WorkflowValidator
from ..core.state_manager import StateManager

# Initialize components (will be configured in startup)
workflow_validator = WorkflowValidator()
workflow_store = None
workflow_manager = None
state_manager = None

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
SERVICE_NAME = "workflow-service"
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

class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_type: str
    steps: Optional[List[Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class WorkflowUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workflow_type: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class ExecutionRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None

# Health check endpoints
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )

@app.get("/health/ready", response_model=ServiceHealth)
async def readiness_check():
    """Readiness probe endpoint."""
    checks = {}
    
    # Check workflow manager
    if workflow_manager:
        try:
            health = await workflow_manager.health_check()
            checks["workflow_manager"] = health["status"]
        except Exception as e:
            checks["workflow_manager"] = f"error: {str(e)}"
    else:
        checks["workflow_manager"] = "not_initialized"
        
    # Check state manager
    if state_manager:
        try:
            health = await state_manager.health_check()
            checks["state_manager"] = health["status"]
        except Exception as e:
            checks["state_manager"] = f"error: {str(e)}"
    else:
        checks["state_manager"] = "not_initialized"
        
    # Check store
    if workflow_store:
        try:
            health = await workflow_store.health_check()
            checks["workflow_store"] = health["status"]
        except Exception as e:
            checks["workflow_store"] = f"error: {str(e)}"
    else:
        checks["workflow_store"] = "not_initialized"
        
    # Determine overall status
    overall_status = "healthy"
    for check_status in checks.values():
        if check_status != "healthy":
            overall_status = "unhealthy"
            break
            
    uptime = str(datetime.now(timezone.utc) - STARTUP_TIME)
    
    return ServiceHealth(
        status=overall_status,
        uptime=uptime,
        checks=checks
    )

@app.get("/health/live", response_model=HealthStatus)
async def liveness_check():
    """Liveness probe endpoint."""
    return HealthStatus(
        status="alive",
        timestamp=datetime.now(timezone.utc).isoformat(),
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )

# Workflow management endpoints
@app.get("/workflows", response_model=List[Dict[str, Any]])
async def list_workflows(
    workflow_type: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 100
):
    """List workflows with optional filtering."""
    try:
        # Validate parameters
        if workflow_type:
            validation = workflow_validator.validate_workflow_id(workflow_type)
            if not validation.is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid workflow type: {validation.errors}")
                
        if status:
            validation = workflow_validator.validate_workflow_id(status)
            if not validation.is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid status: {validation.errors}")
                
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            
        # Validate pagination
        validation = workflow_validator.validate_pagination_params(limit, 0)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid pagination: {validation.errors}")
            
        # Get workflows
        workflows = await workflow_manager.list_workflows(
            workflow_type=WorkflowType(workflow_type) if workflow_type else None,
            status=WorkflowStatus(status) if status else None,
            tags=tag_list,
            limit=limit
        )
        
        return [workflow.dict() for workflow in workflows]
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(request: WorkflowCreateRequest):
    """Create a new workflow."""
    try:
        # Validate request
        validation = workflow_validator.validate_workflow_data(request.dict())
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Validation failed: {validation.errors}")
            
        # Sanitize data
        sanitized_data = workflow_validator.sanitize_workflow_data(request.dict())
        
        # Create workflow
        workflow = await workflow_manager.create_workflow(
            name=sanitized_data["name"],
            workflow_type=WorkflowType(sanitized_data["workflow_type"]),
            description=sanitized_data.get("description"),
            steps=sanitized_data.get("steps"),
            config=sanitized_data.get("config"),
            metadata=sanitized_data.get("metadata"),
            tags=sanitized_data.get("tags")
        )
        
        return workflow.dict()
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(workflow_id: str):
    """Get workflow by ID."""
    try:
        # Validate workflow ID
        validation = workflow_validator.validate_workflow_id(workflow_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid workflow ID: {validation.errors}")
            
        # Get workflow
        workflow = await workflow_manager.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        return workflow.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def update_workflow(workflow_id: str, request: WorkflowUpdateRequest):
    """Update workflow."""
    try:
        # Validate workflow ID
        validation = workflow_validator.validate_workflow_id(workflow_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid workflow ID: {validation.errors}")
            
        # Validate request
        validation = workflow_validator.validate_workflow_data(request.dict(exclude_unset=True))
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Validation failed: {validation.errors}")
            
        # Sanitize data
        sanitized_data = workflow_validator.sanitize_workflow_data(request.dict(exclude_unset=True))
        
        # Update workflow
        workflow = await workflow_manager.update_workflow(workflow_id, sanitized_data)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        return workflow.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow."""
    try:
        # Validate workflow ID
        validation = workflow_validator.validate_workflow_id(workflow_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid workflow ID: {validation.errors}")
            
        # Delete workflow
        success = await workflow_manager.delete_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        return {"message": "Workflow deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Workflow execution endpoints
@app.post("/workflows/{workflow_id}/execute", response_model=Dict[str, Any])
async def execute_workflow(workflow_id: str, request: ExecutionRequest):
    """Execute a workflow."""
    try:
        # Validate workflow ID
        validation = workflow_validator.validate_workflow_id(workflow_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid workflow ID: {validation.errors}")
            
        # Validate execution request
        validation = workflow_validator.validate_execution_data(request.dict())
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Validation failed: {validation.errors}")
            
        # Execute workflow
        execution = await workflow_manager.execute_workflow(
            workflow_id=workflow_id,
            input_data=request.input_data
        )
        
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        return execution.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions", response_model=List[Dict[str, Any]])
async def list_executions(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """List workflow executions."""
    try:
        # Validate parameters
        if workflow_id:
            validation = workflow_validator.validate_workflow_id(workflow_id)
            if not validation.is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid workflow ID: {validation.errors}")
                
        if status:
            validation = workflow_validator.validate_workflow_id(status)
            if not validation.is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid status: {validation.errors}")
                
        # Validate pagination
        validation = workflow_validator.validate_pagination_params(limit, 0)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid pagination: {validation.errors}")
            
        # Get executions
        executions = await workflow_manager.list_executions(
            workflow_id=workflow_id,
            status=WorkflowStatus(status) if status else None,
            limit=limit
        )
        
        return [execution.dict() for execution in executions]
        
    except Exception as e:
        logger.error(f"Failed to list executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions/{execution_id}", response_model=Dict[str, Any])
async def get_execution(execution_id: str):
    """Get execution by ID."""
    try:
        # Validate execution ID
        validation = workflow_validator.validate_execution_id(execution_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid execution ID: {validation.errors}")
            
        # Get execution
        execution = await workflow_manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
            
        return execution.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel workflow execution."""
    try:
        # Validate execution ID
        validation = workflow_validator.validate_execution_id(execution_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid execution ID: {validation.errors}")
            
        # Cancel execution
        success = await workflow_manager.cancel_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
            
        return {"message": "Execution cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel execution {execution_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics and monitoring endpoints
@app.get("/workflows/{workflow_id}/stats", response_model=Dict[str, Any])
async def get_workflow_stats(workflow_id: str):
    """Get workflow statistics."""
    try:
        # Validate workflow ID
        validation = workflow_validator.validate_workflow_id(workflow_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid workflow ID: {validation.errors}")
            
        # Get workflow
        workflow = await workflow_manager.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
            
        # Get executions for this workflow
        executions = await workflow_manager.list_executions(workflow_id=workflow_id)
        
        # Calculate statistics
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
        failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])
        
        stats = {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
            "average_duration_seconds": workflow.average_duration_seconds,
            "last_execution": executions[0].started_at.isoformat() if executions else None
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow stats {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=Dict[str, Any])
async def get_system_stats():
    """Get system-wide statistics."""
    try:
        stats = await workflow_manager.get_workflow_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service information endpoint
@app.get("/info")
async def service_info():
    """Get service information."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "startup_time": STARTUP_TIME.isoformat(),
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME),
        "endpoints": {
            "health": "/health",
            "readiness": "/health/ready",
            "liveness": "/health/live",
            "workflows": "/workflows",
            "executions": "/executions",
            "stats": "/stats"
        },
        "features": [
            "Workflow management (CRUD)",
            "Workflow execution",
            "Execution monitoring",
            "State management",
            "Analytics and statistics",
            "Health monitoring"
        ]
    }

# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info("Workflow Service is starting up...")
    
    # Initialize core components
    global workflow_store, workflow_manager, state_manager
    
    # Initialize workflow store if database URLs are configured
    postgres_url = os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL")
    
    if postgres_url and redis_url:
        try:
            workflow_store = WorkflowStore(postgres_url, redis_url)
            await workflow_store.connect()
            logger.info("Workflow store initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize workflow store: {e}")
            workflow_store = None
    
    # Initialize workflow manager
    workflow_manager = WorkflowManager(workflow_store)
    logger.info("Workflow manager initialized")
    
    # Initialize state manager
    state_manager = StateManager(workflow_store)
    logger.info("State manager initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {SERVICE_NAME}")
    logger.info("Workflow Service is shutting down...")
    
    # Cleanup core components
    if workflow_store:
        await workflow_store.disconnect()
        logger.info("Workflow store disconnected")

# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 