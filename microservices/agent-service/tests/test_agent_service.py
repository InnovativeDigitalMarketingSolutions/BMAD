"""
Tests for the BMAD Agent Service

This module contains comprehensive tests for the Agent Service API endpoints,
including health checks, agent management, and execution functionality.
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

# Ensure the app is properly initialized
app.dependency_overrides = {}

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
        assert data["service"] == "agent-service"
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
    
    def test_liveness_check(self):
        """Test liveness probe endpoint"""
        response = client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "agent-service"
        assert data["version"] == "1.0.0"

class TestAgentManagement:
    """Test agent management endpoints"""
    
    def test_list_agents(self):
        """Test listing all agents"""
        response = client.get("/agents")
        assert response.status_code == 200
        
        agents = response.json()
        assert isinstance(agents, list)
        assert len(agents) >= 3  # We have architect, backend, frontend
        
        # Check that all agents have required fields
        for agent in agents:
            assert "id" in agent
            assert "name" in agent
            assert "type" in agent
            assert "status" in agent
            assert "version" in agent
    
    def test_get_agent_success(self):
        """Test getting agent details successfully"""
        response = client.get("/agents/architect")
        assert response.status_code == 200
        
        agent = response.json()
        assert agent["id"] == "architect"
        assert agent["name"] == "Architect"
        assert agent["type"] == "system_design"
        assert agent["status"] == "active"
    
    def test_get_agent_not_found(self):
        """Test getting non-existent agent"""
        response = client.get("/agents/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"
    
    def test_register_agent_success(self):
        """Test registering a new agent successfully"""
        new_agent = {
            "id": "test_agent",
            "name": "Test Agent",
            "type": "testing",
            "version": "1.0.0"
        }
        
        response = client.post("/agents", json=new_agent)
        assert response.status_code == 200
        
        agent = response.json()
        assert agent["id"] == "test_agent"
        assert agent["name"] == "Test Agent"
        assert agent["status"] == "active"
        assert "created_at" in agent
    
    def test_register_agent_missing_id(self):
        """Test registering agent without ID"""
        new_agent = {
            "name": "Test Agent",
            "type": "testing"
        }
        
        response = client.post("/agents", json=new_agent)
        assert response.status_code == 400
        assert response.json()["detail"] == "Agent ID is required"
    
    def test_register_agent_already_exists(self):
        """Test registering agent that already exists"""
        new_agent = {
            "id": "architect",  # This already exists
            "name": "Another Architect",
            "type": "system_design"
        }
        
        response = client.post("/agents", json=new_agent)
        assert response.status_code == 409
        assert response.json()["detail"] == "Agent already exists"
    
    def test_update_agent_success(self):
        """Test updating agent successfully"""
        update_data = {
            "name": "Updated Architect",
            "version": "2.0.0"
        }
        
        response = client.put("/agents/architect", json=update_data)
        assert response.status_code == 200
        
        agent = response.json()
        assert agent["name"] == "Updated Architect"
        assert agent["version"] == "2.0.0"
    
    def test_update_agent_not_found(self):
        """Test updating non-existent agent"""
        update_data = {"name": "Updated"}
        
        response = client.put("/agents/nonexistent", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"
    
    def test_deregister_agent_success(self):
        """Test deregistering agent successfully"""
        # First register a test agent
        test_agent = {
            "id": "temp_agent",
            "name": "Temporary Agent",
            "type": "temporary"
        }
        client.post("/agents", json=test_agent)
        
        # Now deregister it
        response = client.delete("/agents/temp_agent")
        assert response.status_code == 200
        assert "deregistered successfully" in response.json()["message"]
    
    def test_deregister_agent_not_found(self):
        """Test deregistering non-existent agent"""
        response = client.delete("/agents/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"

class TestAgentExecution:
    """Test agent execution endpoints"""
    
    def test_execute_agent_success(self):
        """Test executing agent successfully"""
        response = client.post("/agents/backend/execute")
        assert response.status_code == 200
        
        result = response.json()
        assert "execution_id" in result
        assert result["agent_id"] == "backend"
        assert result["status"] == "started"
        assert "timestamp" in result
    
    def test_execute_agent_with_data(self):
        """Test executing agent with execution data"""
        execution_data = {
            "task": "build_api",
            "parameters": {"endpoint": "/users"}
        }
        
        response = client.post("/agents/backend/execute", json=execution_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["agent_id"] == "backend"
        assert result["status"] == "started"
    
    def test_execute_agent_not_found(self):
        """Test executing non-existent agent"""
        response = client.post("/agents/nonexistent/execute")
        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"
    
    def test_get_agent_status_success(self):
        """Test getting agent status successfully"""
        response = client.get("/agents/frontend/status")
        assert response.status_code == 200
        
        status = response.json()
        assert status["agent_id"] == "frontend"
        assert "status" in status
        assert "version" in status
    
    def test_get_agent_status_not_found(self):
        """Test getting status for non-existent agent"""
        response = client.get("/agents/nonexistent/status")
        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"
    
    def test_stop_agent_execution_success(self):
        """Test stopping agent execution successfully"""
        response = client.post("/agents/frontend/stop")
        assert response.status_code == 200
        
        result = response.json()
        assert result["agent_id"] == "frontend"
        assert result["status"] == "stopped"
        assert "timestamp" in result
    
    def test_stop_agent_execution_not_found(self):
        """Test stopping execution for non-existent agent"""
        response = client.post("/agents/nonexistent/stop")
        assert response.status_code == 404
        assert response.json()["detail"] == "Agent not found"

class TestAgentDiscovery:
    """Test agent discovery endpoints"""
    
    def test_discover_agents(self):
        """Test discovering available agents"""
        response = client.get("/agents/discover")
        assert response.status_code == 200
        
        data = response.json()
        assert "discovered_agents" in data
        assert "total_count" in data
        assert "timestamp" in data
        
        agents = data["discovered_agents"]
        assert isinstance(agents, list)
        
        # Check that discovered agents have required fields
        for agent in agents:
            assert "id" in agent
            assert "name" in agent
            assert "type" in agent
            assert "version" in agent
    
    def test_list_agent_types(self):
        """Test listing agent types"""
        response = client.get("/agents/types")
        assert response.status_code == 200
        
        data = response.json()
        assert "agent_types" in data
        assert "total_types" in data
        assert "timestamp" in data
        
        types = data["agent_types"]
        assert isinstance(types, list)
        assert len(types) > 0

class TestServiceInformation:
    """Test service information endpoints"""
    
    def test_service_info(self):
        """Test getting service information"""
        response = client.get("/info")
        assert response.status_code == 200
        
        info = response.json()
        assert info["service"] == "agent-service"
        assert info["version"] == "1.0.0"
        assert "description" in info
        assert "startup_time" in info
        assert "uptime" in info
        assert "endpoints" in info
        assert isinstance(info["endpoints"], list)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/agents",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = client.post("/agents", data="{}")
        assert response.status_code == 400  # FastAPI returns 400 for invalid JSON
    
    def test_large_payload(self):
        """Test handling of large payload"""
        large_data = {"data": "x" * 10000}
        response = client.post("/agents/backend/execute", json=large_data)
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__]) 