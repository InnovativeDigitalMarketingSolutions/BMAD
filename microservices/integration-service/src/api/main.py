"""
Integration Service - Main FastAPI Application

This module provides the main FastAPI application for the Integration Service,
including external service management, health checks, and integration monitoring.
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
    title="BMAD Integration Service",
    description="External service integrations and API management service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize client manager
from ..core.client_manager import ClientManager
client_manager = ClientManager()

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
SERVICE_NAME = "integration-service"
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

class IntegrationStatus(BaseModel):
    integration_id: str
    status: str
    health: str
    last_check: str
    response_time: Optional[float]
    error_count: int
    success_rate: float

class RateLimitStatus(BaseModel):
    integration_id: str
    current_usage: int
    limit: int
    reset_time: str
    remaining: int

class CircuitBreakerStatus(BaseModel):
    integration_id: str
    state: str  # closed, open, half-open
    failure_count: int
    threshold: int
    timeout: int
    last_failure: Optional[str]

# Mock data for development (replace with database)
INTEGRATIONS_DB = {
    "auth0": {
        "id": "auth0",
        "name": "Auth0 Authentication",
        "type": "authentication",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "config": {
            "domain": "example.auth0.com",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret"
        },
        "health": "healthy",
        "last_check": "2025-01-01T00:00:00Z",
        "response_time": 45.2,
        "error_count": 0,
        "success_rate": 99.8
    },
    "postgresql": {
        "id": "postgresql",
        "name": "PostgreSQL Database",
        "type": "database",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "config": {
            "url": "postgresql://user:password@localhost:5432/database",
            "pool_size": 10,
            "max_overflow": 20
        },
        "health": "healthy",
        "last_check": "2025-01-01T00:00:00Z",
        "response_time": 12.5,
        "error_count": 0,
        "success_rate": 99.9
    },
    "redis": {
        "id": "redis",
        "name": "Redis Cache",
        "type": "cache",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "config": {
            "url": "redis://localhost:6379",
            "max_connections": 50
        },
        "health": "healthy",
        "last_check": "2025-01-01T00:00:00Z",
        "response_time": 2.1,
        "error_count": 0,
        "success_rate": 99.9
    },
    "stripe": {
        "id": "stripe",
        "name": "Stripe Billing",
        "type": "billing",
        "status": "active",
        "version": "1.0.0",
        "created_at": "2025-01-01T00:00:00Z",
        "config": {
            "secret_key": "sk_test_...",
            "publishable_key": "pk_test_..."
        },
        "health": "healthy",
        "last_check": "2025-01-01T00:00:00Z",
        "response_time": 150.3,
        "error_count": 0,
        "success_rate": 99.5
    }
}

# Rate limiting data
RATE_LIMITS = {
    "auth0": {"current_usage": 45, "limit": 100, "reset_time": "2025-01-01T01:00:00Z", "remaining": 55},
    "postgresql": {"current_usage": 120, "limit": 1000, "reset_time": "2025-01-01T01:00:00Z", "remaining": 880},
    "redis": {"current_usage": 890, "limit": 1000, "reset_time": "2025-01-01T01:00:00Z", "remaining": 110},
    "stripe": {"current_usage": 15, "limit": 100, "reset_time": "2025-01-01T01:00:00Z", "remaining": 85}
}

# Circuit breaker data
CIRCUIT_BREAKERS = {
    "auth0": {"state": "closed", "failure_count": 0, "threshold": 5, "timeout": 60, "last_failure": None},
    "postgresql": {"state": "closed", "failure_count": 0, "threshold": 5, "timeout": 60, "last_failure": None},
    "redis": {"state": "closed", "failure_count": 0, "threshold": 5, "timeout": 60, "last_failure": None},
    "stripe": {"state": "closed", "failure_count": 0, "threshold": 5, "timeout": 60, "last_failure": None}
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
    
    # Check external service health
    healthy_integrations = sum(1 for integration in INTEGRATIONS_DB.values() if integration["health"] == "healthy")
    total_integrations = len(INTEGRATIONS_DB)
    
    checks = {
        "database": "healthy",
        "redis": "healthy",
        "service_discovery": "healthy",
        "external_services": "healthy" if healthy_integrations == total_integrations else "degraded"
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

# Integration management endpoints
@app.get("/integrations", response_model=List[Dict[str, Any]])
async def list_integrations():
    """List all registered integrations"""
    logger.info("Listing all integrations")
    return list(INTEGRATIONS_DB.values())

@app.get("/integrations/{integration_id}", response_model=Dict[str, Any])
async def get_integration(integration_id: str):
    """Get integration details by ID"""
    logger.info(f"Getting integration details for {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return INTEGRATIONS_DB[integration_id]

@app.post("/integrations", response_model=Dict[str, Any])
async def register_integration(integration_data: Dict[str, Any]):
    """Register a new integration"""
    logger.info(f"Registering new integration: {integration_data.get('name', 'Unknown')}")
    
    integration_id = integration_data.get("id")
    if not integration_id:
        raise HTTPException(status_code=400, detail="Integration ID is required")
    
    if integration_id in INTEGRATIONS_DB:
        raise HTTPException(status_code=409, detail="Integration already exists")
    
    # Add metadata
    integration_data["created_at"] = datetime.now(timezone.utc).isoformat()
    integration_data["status"] = "active"
    integration_data["health"] = "unknown"
    integration_data["last_check"] = datetime.now(timezone.utc).isoformat()
    integration_data["response_time"] = 0.0
    integration_data["error_count"] = 0
    integration_data["success_rate"] = 0.0
    
    INTEGRATIONS_DB[integration_id] = integration_data
    
    # Initialize rate limiting and circuit breaker
    RATE_LIMITS[integration_id] = {"current_usage": 0, "limit": 100, "reset_time": "2025-01-01T01:00:00Z", "remaining": 100}
    CIRCUIT_BREAKERS[integration_id] = {"state": "closed", "failure_count": 0, "threshold": 5, "timeout": 60, "last_failure": None}
    
    logger.info(f"Integration {integration_id} registered successfully")
    
    return integration_data

@app.put("/integrations/{integration_id}", response_model=Dict[str, Any])
async def update_integration(integration_id: str, integration_data: Dict[str, Any]):
    """Update integration details"""
    logger.info(f"Updating integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Update fields
    INTEGRATIONS_DB[integration_id].update(integration_data)
    
    logger.info(f"Integration {integration_id} updated successfully")
    
    return INTEGRATIONS_DB[integration_id]

@app.delete("/integrations/{integration_id}")
async def deregister_integration(integration_id: str):
    """Deregister an integration"""
    logger.info(f"Deregistering integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration_data = INTEGRATIONS_DB.pop(integration_id)
    
    # Clean up rate limiting and circuit breaker data
    RATE_LIMITS.pop(integration_id, None)
    CIRCUIT_BREAKERS.pop(integration_id, None)
    
    logger.info(f"Integration {integration_id} deregistered successfully")
    
    return {"message": f"Integration {integration_id} deregistered successfully"}

# Integration health endpoints
@app.get("/integrations/{integration_id}/health", response_model=Dict[str, Any])
async def check_integration_health(integration_id: str):
    """Check integration health"""
    logger.info(f"Checking health for integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration = INTEGRATIONS_DB[integration_id]
    
    # Mock health check
    health_status = {
        "integration_id": integration_id,
        "status": integration["status"],
        "health": integration["health"],
        "last_check": datetime.now(timezone.utc).isoformat(),
        "response_time": integration["response_time"],
        "error_count": integration["error_count"],
        "success_rate": integration["success_rate"]
    }
    
    return health_status

@app.get("/integrations/{integration_id}/status", response_model=IntegrationStatus)
async def get_integration_status(integration_id: str):
    """Get integration status"""
    logger.info(f"Getting status for integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration = INTEGRATIONS_DB[integration_id]
    
    return IntegrationStatus(
        integration_id=integration_id,
        status=integration["status"],
        health=integration["health"],
        last_check=integration["last_check"],
        response_time=integration["response_time"],
        error_count=integration["error_count"],
        success_rate=integration["success_rate"]
    )

@app.post("/integrations/{integration_id}/test")
async def test_integration(integration_id: str):
    """Test integration connection"""
    logger.info(f"Testing integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Test the actual client if available
    client = await client_manager.get_client(integration_id)
    if client:
        # Test specific client operation
        test_result = await client_manager.test_client_operation(integration_id, "health_check")
        return {
            "integration_id": integration_id,
            "test_time": datetime.now(timezone.utc).isoformat(),
            "status": "success" if test_result.get("success") else "failed",
            "response_time": 45.2,
            "details": test_result
        }
    
    # Fallback to mock connection test
    test_result = {
        "integration_id": integration_id,
        "test_time": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        "response_time": 45.2,
        "details": "Connection test successful"
    }
    
    # Update integration health
    INTEGRATIONS_DB[integration_id]["health"] = "healthy"
    INTEGRATIONS_DB[integration_id]["last_check"] = test_result["test_time"]
    INTEGRATIONS_DB[integration_id]["response_time"] = test_result["response_time"]
    
    logger.info(f"Integration {integration_id} test completed successfully")
    
    return test_result

# Rate limiting endpoints
@app.get("/integrations/{integration_id}/rate-limit", response_model=RateLimitStatus)
async def get_rate_limit_status(integration_id: str):
    """Get rate limit status for integration"""
    logger.info(f"Getting rate limit status for integration: {integration_id}")
    
    if integration_id not in RATE_LIMITS:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    rate_limit = RATE_LIMITS[integration_id]
    
    return RateLimitStatus(
        integration_id=integration_id,
        current_usage=rate_limit["current_usage"],
        limit=rate_limit["limit"],
        reset_time=rate_limit["reset_time"],
        remaining=rate_limit["remaining"]
    )

@app.get("/integrations/{integration_id}/cache", response_model=Dict[str, Any])
async def get_cache_statistics(integration_id: str):
    """Get cache statistics for integration"""
    logger.info(f"Getting cache statistics for integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Mock cache statistics
    cache_stats = {
        "integration_id": integration_id,
        "cache_hits": 1250,
        "cache_misses": 45,
        "hit_rate": 96.5,
        "total_requests": 1295,
        "cache_size": "2.5MB",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    
    return cache_stats

@app.post("/integrations/{integration_id}/cache/clear")
async def clear_cache(integration_id: str):
    """Clear cache for integration"""
    logger.info(f"Clearing cache for integration: {integration_id}")
    
    if integration_id not in INTEGRATIONS_DB:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Mock cache clear
    result = {
        "integration_id": integration_id,
        "action": "cache_cleared",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Cache cleared successfully"
    }
    
    logger.info(f"Cache cleared for integration {integration_id}")
    
    return result

# Circuit breaker endpoints
@app.get("/integrations/{integration_id}/circuit-breaker", response_model=CircuitBreakerStatus)
async def get_circuit_breaker_status(integration_id: str):
    """Get circuit breaker status for integration"""
    logger.info(f"Getting circuit breaker status for integration: {integration_id}")
    
    if integration_id not in CIRCUIT_BREAKERS:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    circuit_breaker = CIRCUIT_BREAKERS[integration_id]
    
    return CircuitBreakerStatus(
        integration_id=integration_id,
        state=circuit_breaker["state"],
        failure_count=circuit_breaker["failure_count"],
        threshold=circuit_breaker["threshold"],
        timeout=circuit_breaker["timeout"],
        last_failure=circuit_breaker["last_failure"]
    )

@app.post("/integrations/{integration_id}/circuit-breaker/reset")
async def reset_circuit_breaker(integration_id: str):
    """Reset circuit breaker for integration"""
    logger.info(f"Resetting circuit breaker for integration: {integration_id}")
    
    if integration_id not in CIRCUIT_BREAKERS:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Reset circuit breaker
    CIRCUIT_BREAKERS[integration_id]["state"] = "closed"
    CIRCUIT_BREAKERS[integration_id]["failure_count"] = 0
    CIRCUIT_BREAKERS[integration_id]["last_failure"] = None
    
    result = {
        "integration_id": integration_id,
        "action": "circuit_breaker_reset",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Circuit breaker reset successfully"
    }
    
    logger.info(f"Circuit breaker reset for integration {integration_id}")
    
    return result

# Client management endpoints
@app.get("/clients")
async def list_clients():
    """List all configured external service clients"""
    clients = await client_manager.get_all_clients()
    configs = await client_manager.get_client_configs()
    
    client_list = []
    for client_type, client in clients.items():
        config = configs.get(client_type, {})
        client_list.append({
            "type": client_type,
            "status": "initialized",
            "config": config
        })
    
    return {
        "clients": client_list,
        "total_count": len(client_list)
    }

@app.get("/clients/{client_type}/health")
async def check_client_health(client_type: str):
    """Check health of a specific client"""
    health_result = await client_manager.check_client_health(client_type)
    return health_result

@app.get("/clients/health")
async def check_all_clients_health():
    """Check health of all clients"""
    health_results = await client_manager.check_all_clients_health()
    return {
        "clients": health_results,
        "total_count": len(health_results),
        "healthy_count": sum(1 for result in health_results.values() if result.get("status") == "healthy")
    }

@app.post("/clients/{client_type}/test")
async def test_client_operation(client_type: str, operation: str = "health_check"):
    """Test a specific client operation"""
    test_result = await client_manager.test_client_operation(client_type, operation)
    return test_result

# Service information
@app.get("/info")
async def service_info():
    """Get service information"""
    clients = await client_manager.get_all_clients()
    
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "External service integrations and API management service",
        "startup_time": STARTUP_TIME.isoformat(),
        "uptime": str(datetime.now(timezone.utc) - STARTUP_TIME),
        "integrations_count": len(INTEGRATIONS_DB),
        "clients_count": len(clients),
        "endpoints": [
            "/health",
            "/integrations",
            "/integrations/{id}/health",
            "/integrations/{id}/rate-limit",
            "/integrations/{id}/circuit-breaker",
            "/clients",
            "/clients/{type}/health",
            "/clients/health",
            "/clients/{type}/test"
        ]
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info("Integration Service is starting up...")
    
    # Initialize external service clients
    await client_manager.initialize_clients()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {SERVICE_NAME}")
    logger.info("Integration Service is shutting down...")
    
    # Cleanup external service clients
    await client_manager.cleanup()

# Main entry point
if __name__ == "__main__":
    host = os.getenv("INTEGRATION_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("INTEGRATION_SERVICE_PORT", "8002"))
    debug = os.getenv("INTEGRATION_SERVICE_DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 