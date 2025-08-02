"""
Integration Service Tests

This module contains tests for the Integration Service API endpoints and client management.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from src.api.main import app
from src.core.client_manager import ClientManager

# Test client
client = TestClient(app)

class TestIntegrationService:
    """Test cases for Integration Service."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "integration-service"
        assert data["version"] == "1.0.0"
        
    def test_readiness_check(self):
        """Test readiness check endpoint."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert "uptime" in data
        assert "checks" in data
        
    def test_liveness_check(self):
        """Test liveness check endpoint."""
        response = client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        
    def test_list_integrations(self):
        """Test list integrations endpoint."""
        response = client.get("/integrations")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check integration structure
        integration = data[0]
        assert "id" in integration
        assert "name" in integration
        assert "type" in integration
        assert "status" in integration
        
    def test_get_integration(self):
        """Test get integration endpoint."""
        # First get list to find an integration ID
        list_response = client.get("/integrations")
        integrations = list_response.json()
        
        if integrations:
            integration_id = integrations[0]["id"]
            response = client.get(f"/integrations/{integration_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == integration_id
            assert "name" in data
            assert "type" in data
            assert "status" in data
            
    def test_get_integration_not_found(self):
        """Test get integration with non-existent ID."""
        response = client.get("/integrations/non-existent-id")
        assert response.status_code == 404
        
    def test_register_integration(self):
        """Test register integration endpoint."""
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {
                "url": "https://test.example.com",
                "api_key": "test-key"
            }
        }
        
        response = client.post("/integrations", json=integration_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == integration_data["name"]
        assert data["type"] == integration_data["type"]
        assert "id" in data
        assert "created_at" in data
        
    def test_update_integration(self):
        """Test update integration endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        # Update the integration
        update_data = {
            "name": "Updated Test Integration",
            "config": {"url": "https://updated.example.com"}
        }
        
        response = client.put(f"/integrations/{integration_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["config"]["url"] == update_data["config"]["url"]
        
    def test_delete_integration(self):
        """Test delete integration endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        # Delete the integration
        response = client.delete(f"/integrations/{integration_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/integrations/{integration_id}")
        assert get_response.status_code == 404
        
    def test_check_integration_health(self):
        """Test check integration health endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.get(f"/integrations/{integration_id}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        
    def test_get_integration_status(self):
        """Test get integration status endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.get(f"/integrations/{integration_id}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert "status" in data
        assert "health" in data
        assert "last_check" in data
        
    def test_test_integration(self):
        """Test test integration endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.post(f"/integrations/{integration_id}/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert "test_time" in data
        assert "status" in data
        assert "response_time" in data
        
    def test_get_rate_limit_status(self):
        """Test get rate limit status endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.get(f"/integrations/{integration_id}/rate-limit")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert "current_usage" in data
        assert "limit" in data
        assert "reset_time" in data
        assert "remaining" in data
        
    def test_get_cache_statistics(self):
        """Test get cache statistics endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.get(f"/integrations/{integration_id}/cache")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert "cache_hits" in data
        assert "cache_misses" in data
        assert "hit_rate" in data
        
    def test_clear_cache(self):
        """Test clear cache endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.post(f"/integrations/{integration_id}/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert data["action"] == "cache_cleared"
        assert "timestamp" in data
        
    def test_get_circuit_breaker_status(self):
        """Test get circuit breaker status endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.get(f"/integrations/{integration_id}/circuit-breaker")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert "state" in data
        assert "failure_count" in data
        assert "threshold" in data
        assert "timeout" in data
        
    def test_reset_circuit_breaker(self):
        """Test reset circuit breaker endpoint."""
        # First register an integration
        integration_data = {
            "name": "Test Integration",
            "type": "test",
            "config": {"url": "https://test.example.com"}
        }
        
        register_response = client.post("/integrations", json=integration_data)
        integration_id = register_response.json()["id"]
        
        response = client.post(f"/integrations/{integration_id}/circuit-breaker/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["integration_id"] == integration_id
        assert data["action"] == "circuit_breaker_reset"
        assert "timestamp" in data
        
    def test_list_clients(self):
        """Test list clients endpoint."""
        response = client.get("/clients")
        assert response.status_code == 200
        
        data = response.json()
        assert "clients" in data
        assert "total_count" in data
        assert isinstance(data["clients"], list)
        
    def test_check_client_health(self):
        """Test check client health endpoint."""
        response = client.get("/clients/auth0/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "client_type" in data
        
    def test_check_all_clients_health(self):
        """Test check all clients health endpoint."""
        response = client.get("/clients/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "clients" in data
        assert "total_count" in data
        assert "healthy_count" in data
        
    def test_test_client_operation(self):
        """Test test client operation endpoint."""
        response = client.post("/clients/auth0/test", params={"operation": "health_check"})
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "client_type" in data
        assert "operation" in data
        
    def test_service_info(self):
        """Test service info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "integration-service"
        assert data["version"] == "1.0.0"
        assert "startup_time" in data
        assert "uptime" in data
        assert "integrations_count" in data
        assert "clients_count" in data
        assert "endpoints" in data

class TestClientManager:
    """Test cases for Client Manager."""
    
    @pytest.fixture
    async def client_manager(self):
        """Create a client manager instance for testing."""
        manager = ClientManager()
        yield manager
        await manager.cleanup()
        
    @pytest.mark.asyncio
    async def test_initialize_clients(self, client_manager):
        """Test client initialization."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'AUTH0_ENABLED': 'true',
            'AUTH0_DOMAIN': 'test.auth0.com',
            'AUTH0_CLIENT_ID': 'test-client-id',
            'AUTH0_CLIENT_SECRET': 'test-client-secret'
        }):
            await client_manager.initialize_clients()
            
            # Check that Auth0 client was initialized
            auth0_client = await client_manager.get_client("auth0")
            assert auth0_client is not None
            assert auth0_client.domain == "test.auth0.com"
            
    @pytest.mark.asyncio
    async def test_get_client(self, client_manager):
        """Test getting a specific client."""
        # Mock a client
        mock_client = MagicMock()
        client_manager.clients["test"] = mock_client
        
        client = await client_manager.get_client("test")
        assert client == mock_client
        
        # Test non-existent client
        client = await client_manager.get_client("non-existent")
        assert client is None
        
    @pytest.mark.asyncio
    async def test_get_all_clients(self, client_manager):
        """Test getting all clients."""
        # Mock clients
        mock_client1 = MagicMock()
        mock_client2 = MagicMock()
        client_manager.clients = {
            "client1": mock_client1,
            "client2": mock_client2
        }
        
        clients = await client_manager.get_all_clients()
        assert len(clients) == 2
        assert "client1" in clients
        assert "client2" in clients
        
    @pytest.mark.asyncio
    async def test_get_client_configs(self, client_manager):
        """Test getting client configurations."""
        # Mock configs
        client_manager.client_configs = {
            "test": {"type": "test", "config": "value"}
        }
        
        configs = await client_manager.get_client_configs()
        assert configs["test"]["type"] == "test"
        
    @pytest.mark.asyncio
    async def test_check_client_health(self, client_manager):
        """Test checking client health."""
        # Mock client with health_check method
        mock_client = MagicMock()
        mock_client.health_check = AsyncMock(return_value={"status": "healthy"})
        client_manager.clients["test"] = mock_client
        
        health_result = await client_manager.check_client_health("test")
        assert health_result["status"] == "healthy"
        
        # Test non-existent client
        health_result = await client_manager.check_client_health("non-existent")
        assert health_result["status"] == "not_initialized"
        
    @pytest.mark.asyncio
    async def test_check_all_clients_health(self, client_manager):
        """Test checking all clients health."""
        # Mock clients
        mock_client1 = MagicMock()
        mock_client1.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_client2 = MagicMock()
        mock_client2.health_check = AsyncMock(return_value={"status": "unhealthy"})
        
        client_manager.clients = {
            "client1": mock_client1,
            "client2": mock_client2
        }
        
        health_results = await client_manager.check_all_clients_health()
        assert len(health_results) == 2
        assert health_results["client1"]["status"] == "healthy"
        assert health_results["client2"]["status"] == "unhealthy"
        
    @pytest.mark.asyncio
    async def test_test_client_operation(self, client_manager):
        """Test testing client operations."""
        # Mock client with list_users method
        mock_client = MagicMock()
        mock_client.list_users = AsyncMock(return_value=[{"id": "1"}])
        client_manager.clients["auth0"] = mock_client
        
        result = await client_manager.test_client_operation("auth0", "list_users")
        assert result["success"] is True
        assert result["result"] == 1
        
        # Test unknown operation
        result = await client_manager.test_client_operation("auth0", "unknown_operation")
        assert result["success"] is False
        assert "Unknown operation" in result["error"]
        
    @pytest.mark.asyncio
    async def test_cleanup(self, client_manager):
        """Test client cleanup."""
        # Mock clients with cleanup methods
        mock_client1 = MagicMock()
        mock_client1.disconnect = AsyncMock()
        mock_client2 = MagicMock()
        mock_client2.close = AsyncMock()
        
        client_manager.clients = {
            "client1": mock_client1,
            "client2": mock_client2
        }
        
        await client_manager.cleanup()
        
        # Verify cleanup methods were called
        mock_client1.disconnect.assert_called_once()
        mock_client2.close.assert_called_once()
        
        # Verify clients were cleared
        assert len(client_manager.clients) == 0 