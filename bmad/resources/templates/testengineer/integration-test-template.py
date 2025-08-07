
"""
Integration Test Template voor BMAD TestEngineer Agent

Dit template bevat een uitgebreide integration test structuur voor het testen van
samenwerking tussen verschillende componenten en modules.

Best Practices:
- Test de integratie tussen meerdere componenten
- Gebruik realistische test scenarios
- Test data flow tussen componenten
- Verifieer error handling bij integratie
- Test zowel succesvolle als falende scenarios
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

# Mock componenten voor integration testing
class DatabaseService:
    """Mock database service voor integration tests."""
    
    def __init__(self):
        self.data = {}
        self.connection_status = "connected"
    
    async def connect(self) -> bool:
        """Simuleer database connectie."""
        await asyncio.sleep(0.1)  # Simuleer network delay
        self.connection_status = "connected"
        return True
    
    async def disconnect(self) -> bool:
        """Simuleer database disconnectie."""
        await asyncio.sleep(0.1)
        self.connection_status = "disconnected"
        return True
    
    async def save_data(self, key: str, value: Any) -> bool:
        """Simuleer data opslaan."""
        if self.connection_status != "connected":
            return False
        self.data[key] = value
        return True
    
    async def get_data(self, key: str) -> Optional[Any]:
        """Simuleer data ophalen."""
        if self.connection_status != "connected":
            return None
        return self.data.get(key)

class APIService:
    """Mock API service voor integration tests."""
    
    def __init__(self):
        self.endpoints = {}
        self.request_count = 0
    
    async def register_endpoint(self, path: str, handler: callable) -> bool:
        """Registreer een API endpoint."""
        self.endpoints[path] = handler
        return True
    
    async def make_request(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simuleer API request."""
        self.request_count += 1
        
        if path not in self.endpoints:
            return {"error": "Endpoint not found", "status": 404}
        
        try:
            handler = self.endpoints[path]
            result = await handler(data)
            return {"data": result, "status": 200}
        except Exception as e:
            return {"error": str(e), "status": 500}

class IntegrationManager:
    """Manager voor integration testing."""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.api_service = APIService()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialiseer alle services."""
        try:
            # Connect database
            db_connected = await self.db_service.connect()
            if not db_connected:
                return False
            
            # Register API endpoints
            await self.api_service.register_endpoint("/data", self.handle_data_request)
            await self.api_service.register_endpoint("/status", self.handle_status_request)
            
            self.is_initialized = True
            return True
        except Exception:
            return False
    
    async def handle_data_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data API request."""
        if not self.is_initialized:
            raise Exception("Manager not initialized")
        
        key = data.get("key")
        value = data.get("value")
        
        if not key:
            raise ValueError("Key is required")
        
        # Save to database
        saved = await self.db_service.save_data(key, value)
        if not saved:
            raise Exception("Failed to save data")
        
        return {"key": key, "value": value, "saved": True}
    
    async def handle_status_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status API request."""
        if not self.is_initialized:
            raise Exception("Manager not initialized")
        
        return {
            "status": "healthy",
            "db_connected": self.db_service.connection_status == "connected",
            "api_requests": self.api_service.request_count,
            "initialized": self.is_initialized
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.db_service.disconnect()
        self.is_initialized = False

# Test Fixtures
@pytest.fixture
async def integration_manager():
    """Fixture voor integration manager."""
    manager = IntegrationManager()
    yield manager
    await manager.cleanup()

@pytest.fixture
def sample_integration_data():
    """Fixture voor integration test data."""
    return {
        "user_data": {"id": 1, "name": "Test User", "email": "test@example.com"},
        "config_data": {"setting1": "value1", "setting2": "value2"},
        "metrics_data": {"cpu": 75.5, "memory": 512, "disk": 1024}
    }

# Integration Tests
class TestDatabaseAPIIntegration:
    """Test suite voor database-API integratie."""
    
    @pytest.mark.asyncio
    async def test_full_integration_flow(self, integration_manager, sample_integration_data):
        """Test volledige integratie flow."""
        # Initialize manager
        initialized = await integration_manager.initialize()
        assert initialized is True
        assert integration_manager.is_initialized is True
        
        # Test data flow: API -> Database
        for key, value in sample_integration_data.items():
            # Make API request
            api_response = await integration_manager.api_service.make_request(
                "/data", {"key": key, "value": value}
            )
            
            assert api_response["status"] == 200
            assert api_response["data"]["saved"] is True
            
            # Verify data in database
            db_data = await integration_manager.db_service.get_data(key)
            assert db_data == value
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, integration_manager):
        """Test error handling in integratie scenario."""
        # Initialize manager
        await integration_manager.initialize()
        
        # Test invalid API request
        api_response = await integration_manager.api_service.make_request(
            "/data", {"key": "", "value": "test"}  # Invalid key
        )
        
        assert api_response["status"] == 500
        assert "Key is required" in api_response["error"]
    
    @pytest.mark.asyncio
    async def test_database_disconnection_handling(self, integration_manager):
        """Test handling van database disconnectie."""
        # Initialize manager
        await integration_manager.initialize()
        
        # Disconnect database
        await integration_manager.db_service.disconnect()
        
        # Try to make API request
        api_response = await integration_manager.api_service.make_request(
            "/data", {"key": "test", "value": "test"}
        )
        
        assert api_response["status"] == 500
        assert "Failed to save data" in api_response["error"]

class TestServiceCommunication:
    """Test suite voor service communicatie."""
    
    @pytest.mark.asyncio
    async def test_api_endpoint_registration(self, integration_manager):
        """Test API endpoint registratie."""
        await integration_manager.initialize()
        
        # Test custom endpoint
        async def custom_handler(data):
            return {"custom": "response", "data": data}
        
        registered = await integration_manager.api_service.register_endpoint("/custom", custom_handler)
        assert registered is True
        
        # Test custom endpoint
        response = await integration_manager.api_service.make_request("/custom", {"test": "data"})
        assert response["status"] == 200
        assert response["data"]["custom"] == "response"
    
    @pytest.mark.asyncio
    async def test_status_endpoint_integration(self, integration_manager):
        """Test status endpoint integratie."""
        await integration_manager.initialize()
        
        # Make some API calls first
        await integration_manager.api_service.make_request("/data", {"key": "test1", "value": "value1"})
        await integration_manager.api_service.make_request("/data", {"key": "test2", "value": "value2"})
        
        # Check status
        status_response = await integration_manager.api_service.make_request("/status", {})
        assert status_response["status"] == 200
        
        status_data = status_response["data"]
        assert status_data["status"] == "healthy"
        assert status_data["db_connected"] is True
        assert status_data["api_requests"] == 3  # 2 data requests + 1 status request
        assert status_data["initialized"] is True

class TestConcurrentIntegration:
    """Test suite voor concurrente integratie scenarios."""
    
    @pytest.mark.asyncio
    async def test_concurrent_data_operations(self, integration_manager):
        """Test gelijktijdige data operaties."""
        await integration_manager.initialize()
        
        # Create multiple concurrent requests
        async def make_request(key, value):
            return await integration_manager.api_service.make_request("/data", {"key": key, "value": value})
        
        # Execute concurrent requests
        tasks = [
            make_request(f"key_{i}", f"value_{i}")
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        for result in results:
            assert result["status"] == 200
            assert result["data"]["saved"] is True
        
        # Verify all data is in database
        for i in range(10):
            db_data = await integration_manager.db_service.get_data(f"key_{i}")
            assert db_data == f"value_{i}"
    
    @pytest.mark.asyncio
    async def test_concurrent_status_requests(self, integration_manager):
        """Test gelijktijdige status requests."""
        await integration_manager.initialize()
        
        # Create multiple concurrent status requests
        async def get_status():
            return await integration_manager.api_service.make_request("/status", {})
        
        tasks = [get_status() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Verify all status requests succeeded
        for result in results:
            assert result["status"] == 200
            assert result["data"]["status"] == "healthy"

# Performance Integration Tests
class TestIntegrationPerformance:
    """Test suite voor integration performance."""
    
    @pytest.mark.asyncio
    async def test_integration_performance(self, integration_manager):
        """Test performance van integratie scenario."""
        import time
        
        start_time = time.time()
        
        # Initialize
        await integration_manager.initialize()
        
        # Perform multiple operations
        for i in range(100):
            await integration_manager.api_service.make_request(
                "/data", {"key": f"perf_key_{i}", "value": f"perf_value_{i}"}
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance (should complete within 5 seconds)
        assert execution_time < 5.0, f"Integration performance test failed: {execution_time:.3f}s"
        
        # Verify all data was saved
        for i in range(100):
            data = await integration_manager.db_service.get_data(f"perf_key_{i}")
            assert data == f"perf_value_{i}"

# Error Recovery Tests
class TestIntegrationErrorRecovery:
    """Test suite voor error recovery in integratie."""
    
    @pytest.mark.asyncio
    async def test_recovery_after_database_failure(self, integration_manager):
        """Test recovery na database failure."""
        await integration_manager.initialize()
        
        # Disconnect database
        await integration_manager.db_service.disconnect()
        
        # Try operation (should fail)
        response = await integration_manager.api_service.make_request(
            "/data", {"key": "test", "value": "test"}
        )
        assert response["status"] == 500
        
        # Reconnect database
        await integration_manager.db_service.connect()
        
        # Try operation again (should succeed)
        response = await integration_manager.api_service.make_request(
            "/data", {"key": "test", "value": "test"}
        )
        assert response["status"] == 200
        assert response["data"]["saved"] is True
