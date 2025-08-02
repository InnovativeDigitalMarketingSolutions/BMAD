"""
Main FastAPI application for the API Gateway service.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.core import (
    RouterManager,
    AuthManager,
    RateLimiter,
    LoadBalancer,
    CircuitBreakerManager,
    CacheManager,
    ConfigManager
)
from src.core.auth_manager import AuthConfig
from src.core.rate_limiter import RateLimitConfig
from src.core.load_balancer import LoadBalancerConfig
from src.core.cache_manager import CacheConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global managers
router_manager: RouterManager = None
auth_manager: AuthManager = None
rate_limiter: RateLimiter = None
load_balancer: LoadBalancer = None
circuit_breaker_manager: CircuitBreakerManager = None
cache_manager: CacheManager = None
config_manager: ConfigManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting API Gateway...")
    
    try:
        # Initialize managers
        await initialize_managers()
        
        # Load initial configurations
        await load_initial_configs()
        
        logger.info("API Gateway started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start API Gateway: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down API Gateway...")
        await cleanup_managers()
        logger.info("API Gateway shutdown complete")


async def initialize_managers():
    """Initialize all core managers."""
    global router_manager, auth_manager, rate_limiter, load_balancer, circuit_breaker_manager, cache_manager, config_manager
    
    # Initialize Config Manager first
    config_manager = ConfigManager()
    await config_manager.initialize()
    
    # Initialize Auth Manager
    auth_config = AuthConfig(
        secret_key="your-secret-key-here",  # Should come from environment
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7
    )
    auth_manager = AuthManager(auth_config)
    await auth_manager.initialize()
    
    # Initialize Rate Limiter
    rate_limit_config = RateLimitConfig(
        default_requests_per_minute=100,
        enable_ip_limiting=True,
        enable_user_limiting=True,
        enable_global_limiting=True
    )
    rate_limiter = RateLimiter(rate_limit_config)
    await rate_limiter.initialize()
    
    # Initialize Load Balancer
    load_balancer_config = LoadBalancerConfig(
        strategy="round_robin",
        health_check_interval=30,
        health_check_timeout=5
    )
    load_balancer = LoadBalancer(load_balancer_config)
    await load_balancer.initialize()
    
    # Initialize Circuit Breaker Manager
    circuit_breaker_manager = CircuitBreakerManager()
    await circuit_breaker_manager.initialize()
    
    # Initialize Cache Manager
    cache_config = CacheConfig(
        redis_url="redis://localhost:6379",
        default_ttl=300,
        enable_stats=True
    )
    cache_manager = CacheManager(cache_config)
    await cache_manager.initialize()
    
    # Initialize Router Manager
    router_manager = RouterManager()
    # Router will be initialized with configs in load_initial_configs()


async def load_initial_configs():
    """Load initial service and route configurations."""
    global router_manager
    
    # Default service configurations
    services_config = {
        "agent-service": {
            "url": "http://agent-service:8001",
            "health_check": "/health",
            "timeout": 30,
            "retries": 3
        },
        "integration-service": {
            "url": "http://integration-service:8002",
            "health_check": "/health",
            "timeout": 30,
            "retries": 3
        },
        "context-service": {
            "url": "http://context-service:8003",
            "health_check": "/health",
            "timeout": 30,
            "retries": 3
        },
        "workflow-service": {
            "url": "http://workflow-service:8004",
            "health_check": "/health",
            "timeout": 30,
            "retries": 3
        }
    }
    
    # Default route configurations
    routes_config = [
        {
            "path": "/api/v1/agents",
            "service": "agent-service",
            "method": "GET",
            "timeout": 30,
            "retries": 3,
            "cache_ttl": 60,
            "rate_limit": 100,
            "auth_required": True
        },
        {
            "path": "/api/v1/integrations",
            "service": "integration-service",
            "method": "GET",
            "timeout": 30,
            "retries": 3,
            "cache_ttl": 300,
            "rate_limit": 50,
            "auth_required": True
        },
        {
            "path": "/api/v1/contexts",
            "service": "context-service",
            "method": "GET",
            "timeout": 30,
            "retries": 3,
            "cache_ttl": 60,
            "rate_limit": 200,
            "auth_required": True
        },
        {
            "path": "/api/v1/workflows",
            "service": "workflow-service",
            "method": "GET",
            "timeout": 30,
            "retries": 3,
            "cache_ttl": 120,
            "rate_limit": 50,
            "auth_required": True
        }
    ]
    
    # Initialize router with configurations
    await router_manager.initialize(services_config, routes_config)
    
    # Update config manager with default configs
    await config_manager.update_services_config(services_config)
    await config_manager.update_routes_config(routes_config)


async def cleanup_managers():
    """Cleanup all managers."""
    global router_manager, auth_manager, rate_limiter, load_balancer, circuit_breaker_manager, cache_manager, config_manager
    
    cleanup_tasks = []
    
    if router_manager:
        cleanup_tasks.append(router_manager.cleanup())
    if rate_limiter:
        cleanup_tasks.append(rate_limiter.cleanup())
    if load_balancer:
        cleanup_tasks.append(load_balancer.cleanup())
    if cache_manager:
        cleanup_tasks.append(cache_manager.cleanup())
    if config_manager:
        cleanup_tasks.append(config_manager.cleanup())
    
    if cleanup_tasks:
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)


# Create FastAPI application
app = FastAPI(
    title="BMAD API Gateway",
    description="Centralized API Gateway for BMAD microservices",
    version="1.0.0",
    lifespan=lifespan
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


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe."""
    try:
        # Check if all managers are initialized
        managers_ready = all([
            router_manager and router_manager._initialized,
            auth_manager and auth_manager._initialized,
            rate_limiter and rate_limiter._initialized,
            load_balancer and load_balancer._initialized,
            circuit_breaker_manager and circuit_breaker_manager._initialized,
            cache_manager and cache_manager._initialized,
            config_manager and config_manager._initialized
        ])
        
        if managers_ready:
            return {"status": "ready"}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "error": "Managers not initialized"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e)}
        )


@app.get("/health/live")
async def liveness_check():
    """Liveness probe."""
    return {"status": "alive"}


# Authentication endpoints
@app.post("/auth/login")
async def login(request: Request):
    """User login endpoint."""
    try:
        body = await request.json()
        user_id = body.get("user_id")
        email = body.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=400, detail="user_id and email are required")
        
        # Create tokens
        access_token = auth_manager.create_access_token(
            user_id=user_id,
            email=email,
            roles=["user"],
            permissions=["read", "write"]
        )
        refresh_token = auth_manager.create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/refresh")
async def refresh_token(request: Request):
    """Refresh access token."""
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="refresh_token is required")
        
        # Validate and refresh token
        new_access_token = auth_manager.refresh_access_token(refresh_token)
        
        if not new_access_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth/logout")
async def logout(request: Request):
    """User logout endpoint."""
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_manager.extract_token_from_header(auth_header)
            if token:
                auth_manager.blacklist_token(token)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/auth/validate")
async def validate_token(request: Request):
    """Validate JWT token."""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = auth_manager.extract_token_from_header(auth_header)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        payload = auth_manager.validate_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "valid": True,
            "user_id": payload.sub,
            "email": payload.email,
            "roles": payload.roles,
            "permissions": payload.permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Service routing endpoint
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(request: Request, path: str):
    """Route requests to appropriate services."""
    try:
        # Extract request details
        method = request.method
        headers = dict(request.headers)
        query_params = dict(request.query_params)
        
        # Get request body
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Check authentication
        auth_header = headers.get("Authorization")
        user_id = None
        if auth_header:
            token = auth_manager.extract_token_from_header(auth_header)
            if token:
                payload = auth_manager.validate_token(token)
                if payload:
                    user_id = payload.sub
        
        # Check rate limiting
        client_ip = request.client.host if request.client else "unknown"
        rate_limit_results = await rate_limiter.check_multiple_limits(
            user_id=user_id,
            ip_address=client_ip
        )
        
        if not rate_limiter.is_request_allowed(rate_limit_results):
            retry_after = rate_limiter.get_retry_after(rate_limit_results)
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)} if retry_after else {}
            )
        
        # Check cache for GET requests
        if method == "GET":
            cached_response = await cache_manager.get_cached_response(
                method, path, query_params, headers
            )
            if cached_response:
                return Response(
                    content=cached_response["body"],
                    headers=cached_response["headers"],
                    media_type="application/json"
                )
        
        # Route request
        response = await router_manager.route_request(
            method=method,
            path=path,
            headers=headers,
            query_params=query_params,
            body=body
        )
        
        # Cache successful GET responses
        if method == "GET" and response["status_code"] == 200:
            await cache_manager.cache_response(
                method=method,
                path=path,
                query_params=query_params,
                headers=headers,
                response_body=response["body"],
                response_headers=response["headers"]
            )
        
        # Add rate limit headers
        rate_limit_headers = rate_limiter.get_rate_limit_headers(rate_limit_results)
        response["headers"].update(rate_limit_headers)
        
        return Response(
            content=response["body"],
            status_code=response["status_code"],
            headers=response["headers"]
        )
        
    except Exception as e:
        logger.error(f"Request routing error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


# Configuration endpoints
@app.get("/config")
async def get_config():
    """Get gateway configuration."""
    try:
        return await config_manager.export_configs()
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/config")
async def update_config(request: Request):
    """Update gateway configuration."""
    try:
        configs = await request.json()
        success = await config_manager.import_configs(configs)
        
        if success:
            return {"message": "Configuration updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update configuration")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/config/routes")
async def get_routes():
    """Get routing configuration."""
    try:
        return {"routes": config_manager.get_routes_config()}
    except Exception as e:
        logger.error(f"Error getting routes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/config/routes")
async def update_routes(request: Request):
    """Update routing configuration."""
    try:
        body = await request.json()
        routes = body.get("routes", [])
        
        success = await config_manager.update_routes_config(routes)
        
        if success:
            # Reinitialize router with new routes
            services_config = config_manager.get_services_config()
            await router_manager.initialize(services_config, routes)
            
            return {"message": "Routes updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update routes")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating routes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Monitoring endpoints
@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics."""
    try:
        metrics = {
            "router": await router_manager.health_check(),
            "auth": await auth_manager.health_check(),
            "rate_limiter": await rate_limiter.health_check(),
            "load_balancer": await load_balancer.health_check(),
            "circuit_breakers": await circuit_breaker_manager.health_check(),
            "cache": await cache_manager.health_check(),
            "config": await config_manager.health_check()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/info")
async def get_info():
    """Get service information."""
    return {
        "service": "BMAD API Gateway",
        "version": "1.0.0",
        "description": "Centralized API Gateway for BMAD microservices",
        "features": [
            "Request routing",
            "Load balancing",
            "Authentication",
            "Rate limiting",
            "Caching",
            "Circuit breaker",
            "Health monitoring"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 