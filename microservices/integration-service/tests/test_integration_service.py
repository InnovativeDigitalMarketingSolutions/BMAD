"""
Tests for the BMAD Integration Service

This module contains comprehensive tests for the Integration Service API endpoints,
including integration management, health checks, and monitoring functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Import the FastAPI app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.main import app

# Create test client
client = TestClient(app)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "integration-service"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    def test_readiness_check(self):
        """Test readiness probe endpoint"""
        response = client.get("/health/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert "uptime" in data
        assert "checks" in data
        assert data["checks"]["database"] == "healthy"
        assert data["checks"]["redis"] == "healthy"
        assert data["checks"]["service_discovery"] == "healthy"
        assert "external_services" in data["checks"]
    
    def test_liveness_check(self):
        """Test liveness probe endpoint"""
        response = client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "integration-service"
        assert data["version"] == "1.0.0"

class TestIntegrationManagement:
    """Test integration management endpoints"""
    
    def test_list_integrations(self):
        """Test listing all integrations"""
        response = client.get("/integrations")
        assert response.status_code == 200
        
        integrations = response.json()
        assert isinstance(integrations, list)
        assert len(integrations) >= 4  # We have auth0, postgresql, redis, stripe
        
        # Check that all integrations have required fields
        for integration in integrations:
            assert "id" in integration
            assert "name" in integration
            assert "type" in integration
            assert "status" in integration
            assert "version" in integration
            assert "health" in integration
    
    def test_get_integration_success(self):
        """Test getting integration details successfully"""
        response = client.get("/integrations/auth0")
        assert response.status_code == 200
        
        integration = response.json()
        assert integration["id"] == "auth0"
        assert integration["name"] == "Auth0 Authentication"
        assert integration["type"] == "authentication"
        assert integration["status"] == "active"
    
    def test_get_integration_not_found(self):
        """Test getting non-existent integration"""
        response = client.get("/integrations/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_register_integration_success(self):
        """Test registering a new integration successfully"""
        new_integration = {
            "id": "test_integration",
            "name": "Test Integration",
            "type": "testing",
            "version": "1.0.0",
            "config": {
                "api_key": "test_key",
                "endpoint": "https://api.test.com"
            }
        }
        
        response = client.post("/integrations", json=new_integration)
        assert response.status_code == 200
        
        integration = response.json()
        assert integration["id"] == "test_integration"
        assert integration["name"] == "Test Integration"
        assert integration["status"] == "active"
        assert integration["health"] == "unknown"
        assert "created_at" in integration
    
    def test_register_integration_missing_id(self):
        """Test registering integration without ID"""
        new_integration = {
            "name": "Test Integration",
            "type": "testing"
        }
        
        response = client.post("/integrations", json=new_integration)
        assert response.status_code == 400
        assert response.json()["detail"] == "Integration ID is required"
    
    def test_register_integration_already_exists(self):
        """Test registering integration that already exists"""
        new_integration = {
            "id": "auth0",  # This already exists
            "name": "Another Auth0",
            "type": "authentication"
        }
        
        response = client.post("/integrations", json=new_integration)
        assert response.status_code == 409
        assert response.json()["detail"] == "Integration already exists"
    
    def test_update_integration_success(self):
        """Test updating integration successfully"""
        update_data = {
            "name": "Updated Auth0",
            "version": "2.0.0"
        }
        
        response = client.put("/integrations/auth0", json=update_data)
        assert response.status_code == 200
        
        integration = response.json()
        assert integration["name"] == "Updated Auth0"
        assert integration["version"] == "2.0.0"
    
    def test_update_integration_not_found(self):
        """Test updating non-existent integration"""
        update_data = {"name": "Updated"}
        
        response = client.put("/integrations/nonexistent", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_deregister_integration_success(self):
        """Test deregistering integration successfully"""
        # First register a test integration
        test_integration = {
            "id": "temp_integration",
            "name": "Temporary Integration",
            "type": "temporary"
        }
        client.post("/integrations", json=test_integration)
        
        # Now deregister it
        response = client.delete("/integrations/temp_integration")
        assert response.status_code == 200
        assert "deregistered successfully" in response.json()["message"]
    
    def test_deregister_integration_not_found(self):
        """Test deregistering non-existent integration"""
        response = client.delete("/integrations/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"

class TestIntegrationHealth:
    """Test integration health endpoints"""
    
    def test_check_integration_health_success(self):
        """Test checking integration health successfully"""
        response = client.get("/integrations/postgresql/health")
        assert response.status_code == 200
        
        health = response.json()
        assert health["integration_id"] == "postgresql"
        assert "status" in health
        assert "health" in health
        assert "last_check" in health
        assert "response_time" in health
        assert "error_count" in health
        assert "success_rate" in health
    
    def test_check_integration_health_not_found(self):
        """Test checking health for non-existent integration"""
        response = client.get("/integrations/nonexistent/health")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_get_integration_status_success(self):
        """Test getting integration status successfully"""
        response = client.get("/integrations/redis/status")
        assert response.status_code == 200
        
        status = response.json()
        assert status["integration_id"] == "redis"
        assert "status" in status
        assert "health" in status
        assert "last_check" in status
        assert "response_time" in status
        assert "error_count" in status
        assert "success_rate" in status
    
    def test_get_integration_status_not_found(self):
        """Test getting status for non-existent integration"""
        response = client.get("/integrations/nonexistent/status")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_test_integration_success(self):
        """Test testing integration connection successfully"""
        response = client.post("/integrations/stripe/test")
        assert response.status_code == 200
        
        result = response.json()
        assert result["integration_id"] == "stripe"
        assert result["status"] == "success"
        assert "test_time" in result
        assert "response_time" in result
        assert "details" in result
    
    def test_test_integration_not_found(self):
        """Test testing non-existent integration"""
        response = client.post("/integrations/nonexistent/test")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"

class TestRateLimiting:
    """Test rate limiting endpoints"""
    
    def test_get_rate_limit_status_success(self):
        """Test getting rate limit status successfully"""
        response = client.get("/integrations/auth0/rate-limit")
        assert response.status_code == 200
        
        rate_limit = response.json()
        assert rate_limit["integration_id"] == "auth0"
        assert "current_usage" in rate_limit
        assert "limit" in rate_limit
        assert "reset_time" in rate_limit
        assert "remaining" in rate_limit
    
    def test_get_rate_limit_status_not_found(self):
        """Test getting rate limit status for non-existent integration"""
        response = client.get("/integrations/nonexistent/rate-limit")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_get_cache_statistics_success(self):
        """Test getting cache statistics successfully"""
        response = client.get("/integrations/postgresql/cache")
        assert response.status_code == 200
        
        cache_stats = response.json()
        assert cache_stats["integration_id"] == "postgresql"
        assert "cache_hits" in cache_stats
        assert "cache_misses" in cache_stats
        assert "hit_rate" in cache_stats
        assert "total_requests" in cache_stats
        assert "cache_size" in cache_stats
        assert "last_updated" in cache_stats
    
    def test_get_cache_statistics_not_found(self):
        """Test getting cache statistics for non-existent integration"""
        response = client.get("/integrations/nonexistent/cache")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_clear_cache_success(self):
        """Test clearing cache successfully"""
        response = client.post("/integrations/redis/cache/clear")
        assert response.status_code == 200
        
        result = response.json()
        assert result["integration_id"] == "redis"
        assert result["action"] == "cache_cleared"
        assert "timestamp" in result
        assert "message" in result
    
    def test_clear_cache_not_found(self):
        """Test clearing cache for non-existent integration"""
        response = client.post("/integrations/nonexistent/cache/clear")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"

class TestCircuitBreaker:
    """Test circuit breaker endpoints"""
    
    def test_get_circuit_breaker_status_success(self):
        """Test getting circuit breaker status successfully"""
        response = client.get("/integrations/stripe/circuit-breaker")
        assert response.status_code == 200
        
        circuit_breaker = response.json()
        assert circuit_breaker["integration_id"] == "stripe"
        assert "state" in circuit_breaker
        assert "failure_count" in circuit_breaker
        assert "threshold" in circuit_breaker
        assert "timeout" in circuit_breaker
        assert "last_failure" in circuit_breaker
    
    def test_get_circuit_breaker_status_not_found(self):
        """Test getting circuit breaker status for non-existent integration"""
        response = client.get("/integrations/nonexistent/circuit-breaker")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"
    
    def test_reset_circuit_breaker_success(self):
        """Test resetting circuit breaker successfully"""
        response = client.post("/integrations/auth0/circuit-breaker/reset")
        assert response.status_code == 200
        
        result = response.json()
        assert result["integration_id"] == "auth0"
        assert result["action"] == "circuit_breaker_reset"
        assert "timestamp" in result
        assert "message" in result
    
    def test_reset_circuit_breaker_not_found(self):
        """Test resetting circuit breaker for non-existent integration"""
        response = client.post("/integrations/nonexistent/circuit-breaker/reset")
        assert response.status_code == 404
        assert response.json()["detail"] == "Integration not found"

class TestServiceInformation:
    """Test service information endpoints"""
    
    def test_service_info(self):
        """Test getting service information"""
        response = client.get("/info")
        assert response.status_code == 200
        
        info = response.json()
        assert info["service"] == "integration-service"
        assert info["version"] == "1.0.0"
        assert "description" in info
        assert "startup_time" in info
        assert "uptime" in info
        assert "integrations_count" in info
        assert "endpoints" in info
        assert isinstance(info["endpoints"], list)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/integrations",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = client.post("/integrations", data="{}")
        assert response.status_code == 400  # FastAPI returns 400 for invalid JSON
    
    def test_large_payload(self):
        """Test handling of large payload"""
        large_data = {"data": "x" * 10000}
        response = client.post("/integrations/stripe/test", json=large_data)
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__]) 