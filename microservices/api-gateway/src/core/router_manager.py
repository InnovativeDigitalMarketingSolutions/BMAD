"""
Router Manager for API Gateway service routing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from enum import Enum

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RouteType(str, Enum):
    """Route types for different services."""
    AGENT = "agent"
    INTEGRATION = "integration"
    CONTEXT = "context"
    WORKFLOW = "workflow"
    AUTH = "auth"


class RouteMethod(str, Enum):
    """HTTP methods for routing."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ServiceConfig:
    """Configuration for a service."""
    name: str
    url: str
    health_check: str
    timeout: int = 30
    retries: int = 3
    weight: int = 1
    enabled: bool = True


class RouteRule(BaseModel):
    """Routing rule configuration."""
    path: str = Field(..., description="Request path pattern")
    service: str = Field(..., description="Target service name")
    method: RouteMethod = Field(RouteMethod.GET, description="HTTP method")
    timeout: int = Field(30, description="Request timeout in seconds")
    retries: int = Field(3, description="Number of retries")
    cache_ttl: int = Field(0, description="Cache TTL in seconds")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    auth_required: bool = Field(True, description="Authentication required")
    transform_request: bool = Field(False, description="Transform request")
    transform_response: bool = Field(False, description="Transform response")


class RouterManager:
    """Manages request routing to backend services."""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.routes: Dict[str, RouteRule] = {}
        self.http_client: Optional[httpx.AsyncClient] = None
        self._initialized = False
        
    async def initialize(self, services_config: Dict[str, Any], routes_config: List[Dict[str, Any]]):
        """Initialize the router with service and route configurations."""
        try:
            # Initialize services
            for service_name, config in services_config.items():
                self.services[service_name] = ServiceConfig(
                    name=service_name,
                    url=config["url"],
                    health_check=config.get("health_check", "/health"),
                    timeout=config.get("timeout", 30),
                    retries=config.get("retries", 3),
                    weight=config.get("weight", 1),
                    enabled=config.get("enabled", True)
                )
            
            # Initialize routes
            for route_config in routes_config:
                route = RouteRule(**route_config)
                self.routes[route.path] = route
            
            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
            
            self._initialized = True
            logger.info(f"Router initialized with {len(self.services)} services and {len(self.routes)} routes")
            
        except Exception as e:
            logger.error(f"Failed to initialize router: {e}")
            raise
    
    async def route_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        body: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Route a request to the appropriate service."""
        if not self._initialized:
            raise RuntimeError("Router not initialized")
        
        try:
            # Find matching route
            route = self._find_route(path, method)
            if not route:
                return {
                    "status_code": 404,
                    "body": {"error": "Route not found"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Get service configuration
            service = self.services.get(route.service)
            if not service or not service.enabled:
                return {
                    "status_code": 503,
                    "body": {"error": "Service unavailable"},
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Build target URL
            target_url = self._build_target_url(service.url, path)
            
            # Prepare request
            request_headers = self._prepare_headers(headers, route)
            
            # Make request
            response = await self._make_request(
                method=method,
                url=target_url,
                headers=request_headers,
                query_params=query_params,
                body=body,
                timeout=route.timeout,
                retries=route.retries
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return {
                "status_code": 500,
                "body": {"error": "Internal server error"},
                "headers": {"Content-Type": "application/json"}
            }
    
    def _find_route(self, path: str, method: str) -> Optional[RouteRule]:
        """Find matching route for path and method."""
        # Simple path matching (can be enhanced with regex or more sophisticated matching)
        for route_path, route in self.routes.items():
            if path.startswith(route_path) and route.method.value == method:
                return route
        return None
    
    def _build_target_url(self, service_url: str, path: str) -> str:
        """Build target URL for the service."""
        # Remove the route prefix from the path
        for route_path in self.routes.keys():
            if path.startswith(route_path):
                remaining_path = path[len(route_path):]
                return urljoin(service_url, remaining_path)
        return urljoin(service_url, path)
    
    def _prepare_headers(self, headers: Dict[str, str], route: RouteRule) -> Dict[str, str]:
        """Prepare headers for the request."""
        # Remove gateway-specific headers
        filtered_headers = {k: v for k, v in headers.items() 
                          if not k.lower().startswith(('x-gateway-', 'x-forwarded-'))}
        
        # Add gateway headers
        filtered_headers.update({
            "X-Gateway-Route": route.path,
            "X-Gateway-Service": route.service
        })
        
        return filtered_headers
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        body: Optional[bytes],
        timeout: int,
        retries: int
    ) -> Dict[str, Any]:
        """Make HTTP request to backend service."""
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")
        
        for attempt in range(retries + 1):
            try:
                response = await self.http_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    content=body,
                    timeout=timeout
                )
                
                return {
                    "status_code": response.status_code,
                    "body": response.content,
                    "headers": dict(response.headers)
                }
                
            except httpx.TimeoutException:
                if attempt == retries:
                    logger.error(f"Request timeout after {retries} retries: {url}")
                    return {
                        "status_code": 504,
                        "body": {"error": "Gateway timeout"},
                        "headers": {"Content-Type": "application/json"}
                    }
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                
            except httpx.RequestError as e:
                if attempt == retries:
                    logger.error(f"Request error after {retries} retries: {e}")
                    return {
                        "status_code": 502,
                        "body": {"error": "Bad gateway"},
                        "headers": {"Content-Type": "application/json"}
                    }
                await asyncio.sleep(0.1 * (attempt + 1))
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service."""
        service = self.services.get(service_name)
        if not service:
            return {"status": "unknown", "error": "Service not found"}
        
        try:
            health_url = urljoin(service.url, service.health_check)
            response = await self.http_client.get(health_url, timeout=5)
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all services."""
        health_status = {}
        
        for service_name in self.services.keys():
            health_status[service_name] = await self.get_service_health(service_name)
        
        return health_status
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all configured routes."""
        return [
            {
                "path": route.path,
                "service": route.service,
                "method": route.method.value,
                "timeout": route.timeout,
                "retries": route.retries,
                "cache_ttl": route.cache_ttl,
                "rate_limit": route.rate_limit,
                "auth_required": route.auth_required
            }
            for route in self.routes.values()
        ]
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get all configured services."""
        return [
            {
                "name": service.name,
                "url": service.url,
                "health_check": service.health_check,
                "timeout": service.timeout,
                "retries": service.retries,
                "weight": service.weight,
                "enabled": service.enabled
            }
            for service in self.services.values()
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the router."""
        try:
            services_health = await self.get_all_services_health()
            healthy_services = sum(1 for health in services_health.values() 
                                 if health.get("status") == "healthy")
            total_services = len(self.services)
            
            # Determine status based on healthy services
            if healthy_services == 0:
                status = "unhealthy"
            elif healthy_services == total_services:
                status = "healthy"
            else:
                status = "degraded"
            
            result = {
                "status": status,
                "total_services": total_services,
                "healthy_services": healthy_services,
                "services": services_health
            }
            
            # Add error field if all services are unhealthy
            if healthy_services == 0:
                result["error"] = "All services are unhealthy"
            
            return result
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.http_client:
            await self.http_client.aclose() 