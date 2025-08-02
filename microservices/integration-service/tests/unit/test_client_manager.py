"""
Unit tests for ClientManager
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.client_manager import ClientManager


class TestClientManager:
    """Test cases for ClientManager."""
    
    @pytest.fixture
    def client_manager(self):
        """Create a ClientManager instance for testing."""
        return ClientManager()
        
    @pytest.fixture
    def mock_auth0_client(self):
        """Mock Auth0 client."""
        mock_client = AsyncMock()
        mock_client.health_check.return_value = {"status": "healthy"}
        return mock_client
        
    @pytest.fixture
    def mock_postgresql_client(self):
        """Mock PostgreSQL client."""
        mock_client = AsyncMock()
        mock_client.health_check.return_value = {"status": "healthy"}
        return mock_client
        
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        mock_client = AsyncMock()
        mock_client.health_check.return_value = {"status": "healthy"}
        return mock_client
        
    @pytest.mark.asyncio
    async def test_initialize_clients(self, client_manager):
        """Test client initialization."""
        with patch('src.core.client_manager.Auth0Client') as mock_auth0_class, \
             patch('src.core.client_manager.PostgreSQLClient') as mock_postgresql_class, \
             patch('src.core.client_manager.RedisClient') as mock_redis_class:
            
            # Mock client instances
            mock_auth0 = AsyncMock()
            mock_postgresql = AsyncMock()
            mock_redis = AsyncMock()
            
            mock_auth0_class.return_value = mock_auth0
            mock_postgresql_class.return_value = mock_postgresql
            mock_redis_class.return_value = mock_redis
            
            # Initialize clients
            await client_manager.initialize_clients()
            
            # Verify clients were created
            mock_auth0_class.assert_called_once()
            mock_postgresql_class.assert_called_once()
            mock_redis_class.assert_called_once()
            
            # Verify clients are stored
            assert client_manager.auth0_client is not None
            assert client_manager.postgresql_client is not None
            assert client_manager.redis_client is not None
            
    @pytest.mark.asyncio
    async def test_get_client(self, client_manager, mock_auth0_client):
        """Test getting specific client."""
        # Set up client
        client_manager.clients["auth0"] = mock_auth0_client
        
        # Get client
        client = await client_manager.get_client("auth0")
        
        assert client is not None
        assert client == mock_auth0_client
        
    @pytest.mark.asyncio
    async def test_get_client_not_found(self, client_manager):
        """Test getting non-existent client."""
        client = await client_manager.get_client("non-existent")
        
        assert client is None
        
    @pytest.mark.asyncio
    async def test_get_all_clients(self, client_manager, mock_auth0_client, mock_postgresql_client, mock_redis_client):
        """Test getting all clients."""
        # Set up clients
        client_manager.clients["auth0"] = mock_auth0_client
        client_manager.clients["postgresql"] = mock_postgresql_client
        client_manager.clients["redis"] = mock_redis_client
        
        # Get all clients
        clients = await client_manager.get_all_clients()
        
        assert len(clients) >= 3
        assert "auth0" in clients
        assert "postgresql" in clients
        assert "redis" in clients
        
    @pytest.mark.asyncio
    async def test_get_client_configs(self, client_manager):
        """Test getting client configurations."""
        configs = await client_manager.get_client_configs()
        
        assert configs is not None
        assert isinstance(configs, dict)
        assert "auth0" in configs
        assert "postgresql" in configs
        assert "redis" in configs
        
    @pytest.mark.asyncio
    async def test_check_client_health(self, client_manager, mock_auth0_client):
        """Test checking client health."""
        # Set up client
        client_manager.clients["auth0"] = mock_auth0_client
        
        # Check health
        health = await client_manager.check_client_health("auth0")
        
        assert health is not None
        assert "status" in health
        assert health["status"] == "healthy"
        
    @pytest.mark.asyncio
    async def test_check_client_health_not_found(self, client_manager):
        """Test checking health of non-existent client."""
        health = await client_manager.check_client_health("non-existent")
        
        assert health is not None
        assert "status" in health
        assert health["status"] == "not_found"
        
    @pytest.mark.asyncio
    async def test_check_all_clients_health(self, client_manager, mock_auth0_client, mock_postgresql_client, mock_redis_client):
        """Test checking health of all clients."""
        # Set up clients
        client_manager.clients["auth0"] = mock_auth0_client
        client_manager.clients["postgresql"] = mock_postgresql_client
        client_manager.clients["redis"] = mock_redis_client
        
        # Check all clients health
        health_status = await client_manager.check_all_clients_health()
        
        assert health_status is not None
        assert "auth0" in health_status
        assert "postgresql" in health_status
        assert "redis" in health_status
        assert health_status["auth0"]["status"] == "healthy"
        assert health_status["postgresql"]["status"] == "healthy"
        assert health_status["redis"]["status"] == "healthy"
        
    @pytest.mark.asyncio
    async def test_test_client_operation(self, client_manager, mock_auth0_client):
        """Test client operation testing."""
        # Set up client
        client_manager.clients["auth0"] = mock_auth0_client
        
        # Test operation
        result = await client_manager.test_client_operation("auth0", "health_check")
        
        assert result is not None
        assert "success" in result
        assert "message" in result
        
    @pytest.mark.asyncio
    async def test_test_client_operation_not_found(self, client_manager):
        """Test operation testing for non-existent client."""
        result = await client_manager.test_client_operation("non-existent")
        
        assert result is not None
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_cleanup(self, client_manager, mock_auth0_client, mock_postgresql_client, mock_redis_client):
        """Test client cleanup."""
        # Set up clients
        client_manager.clients["auth0"] = mock_auth0_client
        client_manager.clients["postgresql"] = mock_postgresql_client
        client_manager.clients["redis"] = mock_redis_client
        
        # Cleanup
        await client_manager.cleanup()
        
        # Verify cleanup was called on clients
        mock_auth0_client.cleanup.assert_called_once()
        mock_postgresql_client.cleanup.assert_called_once()
        mock_redis_client.cleanup.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_health_check(self, client_manager, mock_auth0_client, mock_postgresql_client, mock_redis_client):
        """Test health check."""
        # Set up clients
        client_manager.clients["auth0"] = mock_auth0_client
        client_manager.clients["postgresql"] = mock_postgresql_client
        client_manager.clients["redis"] = mock_redis_client
        
        # Check health
        health = await client_manager.health_check()
        
        assert health is not None
        assert "status" in health
        assert "clients" in health
        assert "total_clients" in health
        assert "healthy_clients" in health
        assert health["total_clients"] >= 3
        assert health["healthy_clients"] >= 3 