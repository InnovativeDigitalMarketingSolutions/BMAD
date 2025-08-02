"""
Unit tests voor RouterManager
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.router_manager import RouterManager, ServiceConfig, RouteRule, RouteMethod


class TestRouterManager:
    """Test cases voor RouterManager."""
    
    @pytest.fixture
    def router_manager(self):
        """Create a RouterManager instance for testing."""
        return RouterManager()
        
    @pytest.fixture
    def sample_services_config(self):
        """Sample services configuration for testing."""
        return {
            "agent-service": {
                "url": "http://agent-service:8001",
                "health_check": "/health",
                "timeout": 30,
                "retries": 3,
                "weight": 1,
                "enabled": True
            },
            "integration-service": {
                "url": "http://integration-service:8002",
                "health_check": "/health",
                "timeout": 30,
                "retries": 3,
                "weight": 1,
                "enabled": True
            }
        }
        
    @pytest.fixture
    def sample_routes_config(self):
        """Sample routes configuration for testing."""
        return [
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
            }
        ]
        
    @pytest.mark.asyncio
    async def test_initialize(self, router_manager, sample_services_config, sample_routes_config):
        """Test router manager initialization."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        assert router_manager._initialized is True
        assert len(router_manager.services) == 2
        assert len(router_manager.routes) == 2
        assert router_manager.http_client is not None
        
    @pytest.mark.asyncio
    async def test_initialize_with_empty_configs(self, router_manager):
        """Test initialization with empty configurations."""
        await router_manager.initialize({}, [])
        
        assert router_manager._initialized is True
        assert len(router_manager.services) == 0
        assert len(router_manager.routes) == 0
        
    @pytest.mark.asyncio
    async def test_route_request_success(self, router_manager, sample_services_config, sample_routes_config):
        """Test successful request routing."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        # Mock HTTP client response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "success"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        with patch.object(router_manager.http_client, 'request', return_value=mock_response):
            result = await router_manager.route_request(
                method="GET",
                path="/api/v1/agents",
                headers={"Authorization": "Bearer token"},
                query_params={},
                body=None
            )
            
            assert result["status_code"] == 200
            assert result["body"] == b'{"status": "success"}'
            
    @pytest.mark.asyncio
    async def test_route_request_not_found(self, router_manager, sample_services_config, sample_routes_config):
        """Test routing when route is not found."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        result = await router_manager.route_request(
            method="GET",
            path="/api/v1/unknown",
            headers={},
            query_params={},
            body=None
        )
        
        assert result["status_code"] == 404
        assert "error" in result["body"]
        
    @pytest.mark.asyncio
    async def test_route_request_service_unavailable(self, router_manager, sample_services_config, sample_routes_config):
        """Test routing when service is unavailable."""
        # Disable a service
        sample_services_config["agent-service"]["enabled"] = False
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        result = await router_manager.route_request(
            method="GET",
            path="/api/v1/agents",
            headers={},
            query_params={},
            body=None
        )
        
        assert result["status_code"] == 503
        assert "error" in result["body"]
        
    @pytest.mark.asyncio
    async def test_route_request_timeout(self, router_manager, sample_services_config, sample_routes_config):
        """Test request routing with timeout."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        with patch.object(router_manager.http_client, 'request', side_effect=Exception("Timeout")):
            result = await router_manager.route_request(
                method="GET",
                path="/api/v1/agents",
                headers={},
                query_params={},
                body=None
            )
            
            assert result["status_code"] == 500
            assert "error" in result["body"]
            
    @pytest.mark.asyncio
    async def test_get_service_health_healthy(self, router_manager, sample_services_config, sample_routes_config):
        """Test getting health status for healthy service."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        with patch.object(router_manager.http_client, 'get', return_value=mock_response):
            health = await router_manager.get_service_health("agent-service")
            
            assert health["status"] == "healthy"
            assert health["status_code"] == 200
            assert "response_time" in health
            
    @pytest.mark.asyncio
    async def test_get_service_health_unhealthy(self, router_manager, sample_services_config, sample_routes_config):
        """Test getting health status for unhealthy service."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        with patch.object(router_manager.http_client, 'get', side_effect=Exception("Connection failed")):
            health = await router_manager.get_service_health("agent-service")
            
            assert health["status"] == "unhealthy"
            assert "error" in health
            
    @pytest.mark.asyncio
    async def test_get_service_health_not_found(self, router_manager, sample_services_config, sample_routes_config):
        """Test getting health status for non-existent service."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        health = await router_manager.get_service_health("unknown-service")
        
        assert health["status"] == "unknown"
        assert "error" in health
        
    @pytest.mark.asyncio
    async def test_get_all_services_health(self, router_manager, sample_services_config, sample_routes_config):
        """Test getting health status for all services."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        with patch.object(router_manager.http_client, 'get', return_value=mock_response):
            health_status = await router_manager.get_all_services_health()
            
            assert len(health_status) == 2
            assert "agent-service" in health_status
            assert "integration-service" in health_status
            assert health_status["agent-service"]["status"] == "healthy"
            
    def test_get_routes(self, router_manager, sample_services_config, sample_routes_config):
        """Test getting all configured routes."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        routes = router_manager.get_routes()
        
        assert len(routes) == 2
        assert routes[0]["path"] == "/api/v1/agents"
        assert routes[0]["service"] == "agent-service"
        assert routes[1]["path"] == "/api/v1/integrations"
        assert routes[1]["service"] == "integration-service"
        
    def test_get_services(self, router_manager, sample_services_config, sample_routes_config):
        """Test getting all configured services."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        services = router_manager.get_services()
        
        assert len(services) == 2
        assert services[0]["name"] == "agent-service"
        assert services[0]["url"] == "http://agent-service:8001"
        assert services[1]["name"] == "integration-service"
        assert services[1]["url"] == "http://integration-service:8002"
        
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, router_manager, sample_services_config, sample_routes_config):
        """Test health check when all services are healthy."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        with patch.object(router_manager.http_client, 'get', return_value=mock_response):
            health = await router_manager.health_check()
            
            assert health["status"] == "healthy"
            assert health["total_services"] == 2
            assert health["healthy_services"] == 2
            assert "services" in health
            
    @pytest.mark.asyncio
    async def test_health_check_degraded(self, router_manager, sample_services_config, sample_routes_config):
        """Test health check when some services are unhealthy."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        # Mock one service healthy, one unhealthy
        def mock_get(url, timeout=None):
            mock_response = MagicMock()
            if "agent-service" in url:
                mock_response.status_code = 200
            else:
                raise Exception("Connection failed")
            mock_response.elapsed.total_seconds.return_value = 0.1
            return mock_response
        
        with patch.object(router_manager.http_client, 'get', side_effect=mock_get):
            health = await router_manager.health_check()
            
            assert health["status"] == "degraded"
            assert health["total_services"] == 2
            assert health["healthy_services"] == 1
            
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, router_manager, sample_services_config, sample_routes_config):
        """Test health check when all services are unhealthy."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        with patch.object(router_manager.http_client, 'get', side_effect=Exception("Connection failed")):
            health = await router_manager.health_check()
            
            assert health["status"] == "unhealthy"
            assert "error" in health
            
    @pytest.mark.asyncio
    async def test_cleanup(self, router_manager, sample_services_config, sample_routes_config):
        """Test cleanup of resources."""
        await router_manager.initialize(sample_services_config, sample_routes_config)
        
        # Mock the aclose method
        with patch.object(router_manager.http_client, 'aclose') as mock_aclose:
            await router_manager.cleanup()
            mock_aclose.assert_called_once()
            
    def test_find_route_exact_match(self, router_manager, sample_services_config, sample_routes_config):
        """Test finding route with exact match."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        route = router_manager._find_route("/api/v1/agents", "GET")
        
        assert route is not None
        assert route.path == "/api/v1/agents"
        assert route.service == "agent-service"
        
    def test_find_route_no_match(self, router_manager, sample_services_config, sample_routes_config):
        """Test finding route with no match."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        route = router_manager._find_route("/api/v1/unknown", "GET")
        
        assert route is None
        
    def test_find_route_wrong_method(self, router_manager, sample_services_config, sample_routes_config):
        """Test finding route with wrong HTTP method."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        route = router_manager._find_route("/api/v1/agents", "POST")
        
        assert route is None
        
    def test_build_target_url(self, router_manager, sample_services_config, sample_routes_config):
        """Test building target URL."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        target_url = router_manager._build_target_url("http://agent-service:8001", "/api/v1/agents/123")
        
        assert target_url == "http://agent-service:8001/123"
        
    def test_prepare_headers(self, router_manager, sample_services_config, sample_routes_config):
        """Test preparing headers for request."""
        asyncio.run(router_manager.initialize(sample_services_config, sample_routes_config))
        
        route = router_manager.routes["/api/v1/agents"]
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}
        
        prepared_headers = router_manager._prepare_headers(headers, route)
        
        assert "Authorization" in prepared_headers
        assert "Content-Type" in prepared_headers
        assert "X-Gateway-Route" in prepared_headers
        assert "X-Gateway-Service" in prepared_headers 