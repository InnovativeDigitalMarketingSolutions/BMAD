"""
Tests for the BMAD Context Service

This module contains comprehensive tests for the Context Service API endpoints,
including context management, layering, analytics, and sharing functionality.
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
        assert data["service"] == "context-service"
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
        assert "context_service" in data["checks"]
    
    def test_liveness_check(self):
        """Test liveness probe endpoint"""
        response = client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "context-service"
        assert data["version"] == "1.0.0"

class TestContextManagement:
    """Test context management endpoints"""
    
    def test_list_contexts(self):
        """Test listing all contexts"""
        response = client.get("/contexts")
        assert response.status_code == 200
        
        contexts = response.json()
        assert isinstance(contexts, list)
        assert len(contexts) >= 3  # We have agent_execution_001, workflow_session_001, user_session_001
        
        # Check that all contexts have required fields
        for context in contexts:
            assert "id" in context
            assert "name" in context
            assert "type" in context
            assert "status" in context
            assert "size_mb" in context
            assert "layer_count" in context
            assert "access_count" in context
    
    def test_get_context_success(self):
        """Test getting context details successfully"""
        response = client.get("/contexts/agent_execution_001")
        assert response.status_code == 200
        
        context = response.json()
        assert context["id"] == "agent_execution_001"
        assert context["name"] == "Agent Execution Context"
        assert context["type"] == "agent_execution"
        assert context["status"] == "active"
    
    def test_get_context_not_found(self):
        """Test getting non-existent context"""
        response = client.get("/contexts/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Context not found"
    
    def test_create_context_success(self):
        """Test creating a new context successfully"""
        new_context = {
            "id": "test_context",
            "name": "Test Context",
            "type": "testing",
            "description": "A test context"
        }
        
        response = client.post("/contexts", json=new_context)
        assert response.status_code == 200
        
        context = response.json()
        assert context["id"] == "test_context"
        assert context["name"] == "Test Context"
        assert context["status"] == "active"
        assert context["size_mb"] == 0.0
        assert context["layer_count"] == 0
        assert context["access_count"] == 0
        assert "created_at" in context
    
    def test_create_context_missing_id(self):
        """Test creating context without ID"""
        new_context = {
            "name": "Test Context",
            "type": "testing"
        }
        
        response = client.post("/contexts", json=new_context)
        assert response.status_code == 400
        assert response.json()["detail"] == "Context ID is required"
    
    def test_create_context_already_exists(self):
        """Test creating context that already exists"""
        new_context = {
            "id": "agent_execution_001",  # This already exists
            "name": "Another Agent Context",
            "type": "agent_execution"
        }
        
        response = client.post("/contexts", json=new_context)
        assert response.status_code == 409
        assert response.json()["detail"] == "Context already exists"
    
    def test_update_context_success(self):
        """Test updating context successfully"""
        update_data = {
            "name": "Updated Agent Context",
            "description": "Updated description"
        }
        
        response = client.put("/contexts/agent_execution_001", json=update_data)
        assert response.status_code == 200
        
        context = response.json()
        assert context["name"] == "Updated Agent Context"
        assert context["description"] == "Updated description"
        assert "updated_at" in context
    
    def test_update_context_not_found(self):
        """Test updating non-existent context"""
        update_data = {"name": "Updated"}
        
        response = client.put("/contexts/nonexistent", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Context not found"
    
    def test_delete_context_success(self):
        """Test deleting context successfully"""
        # First create a test context
        test_context = {
            "id": "temp_context",
            "name": "Temporary Context",
            "type": "temporary"
        }
        client.post("/contexts", json=test_context)
        
        # Now delete it
        response = client.delete("/contexts/temp_context")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    def test_delete_context_not_found(self):
        """Test deleting non-existent context"""
        response = client.delete("/contexts/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Context not found"

class TestContextLayers:
    """Test context layers endpoints"""
    
    def test_list_context_layers_success(self):
        """Test listing context layers successfully"""
        response = client.get("/contexts/agent_execution_001/layers")
        assert response.status_code == 200
        
        layers = response.json()
        assert isinstance(layers, list)
        assert len(layers) >= 3  # We have layer_1, layer_2, layer_3
        
        # Check that all layers have required fields
        for layer in layers:
            assert "layer_id" in layer
            assert "context_id" in layer
            assert "layer_type" in layer
            assert "data" in layer
            assert "created_at" in layer
            assert "updated_at" in layer
    
    def test_list_context_layers_not_found(self):
        """Test listing layers for non-existent context"""
        response = client.get("/contexts/nonexistent/layers")
        assert response.status_code == 404
        assert response.json()["detail"] == "Context not found"
    
    def test_add_context_layer_success(self):
        """Test adding context layer successfully"""
        # First create a test context
        test_context = {
            "id": "test_context_layers",
            "name": "Test Context for Layers",
            "type": "testing"
        }
        client.post("/contexts", json=test_context)
        
        # Add a layer
        layer_data = {
            "layer_id": "test_layer",
            "layer_type": "test_data",
            "data": {"key": "value", "test": True}
        }
        
        response = client.post("/contexts/test_context_layers/layers", json=layer_data)
        assert response.status_code == 200
        
        layer = response.json()
        assert layer["layer_id"] == "test_layer"
        assert layer["context_id"] == "test_context_layers"
        assert layer["layer_type"] == "test_data"
        assert layer["data"]["key"] == "value"
        assert "created_at" in layer
    
    def test_add_context_layer_missing_id(self):
        """Test adding layer without layer ID"""
        layer_data = {
            "layer_type": "test_data",
            "data": {"key": "value"}
        }
        
        response = client.post("/contexts/agent_execution_001/layers", json=layer_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Layer ID is required"
    
    def test_add_context_layer_context_not_found(self):
        """Test adding layer to non-existent context"""
        layer_data = {
            "layer_id": "test_layer",
            "layer_type": "test_data",
            "data": {"key": "value"}
        }
        
        response = client.post("/contexts/nonexistent/layers", json=layer_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Context not found"
    
    def test_get_context_layer_success(self):
        """Test getting context layer successfully"""
        response = client.get("/contexts/agent_execution_001/layers/layer_1")
        assert response.status_code == 200
        
        layer = response.json()
        assert layer["layer_id"] == "layer_1"
        assert layer["context_id"] == "agent_execution_001"
        assert layer["layer_type"] == "input_data"
        assert "data" in layer
    
    def test_get_context_layer_not_found(self):
        """Test getting non-existent layer"""
        response = client.get("/contexts/agent_execution_001/layers/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Layer not found"
    
    def test_update_context_layer_success(self):
        """Test updating context layer successfully"""
        update_data = {
            "data": {"updated": True, "new_value": "test"}
        }
        
        response = client.put("/contexts/agent_execution_001/layers/layer_1", json=update_data)
        assert response.status_code == 200
        
        layer = response.json()
        assert layer["data"]["updated"] == True
        assert layer["data"]["new_value"] == "test"
        assert "updated_at" in layer
    
    def test_remove_context_layer_success(self):
        """Test removing context layer successfully"""
        # First add a test layer
        test_context = {
            "id": "test_context_remove",
            "name": "Test Context for Remove",
            "type": "testing"
        }
        client.post("/contexts", json=test_context)
        
        layer_data = {
            "layer_id": "remove_layer",
            "layer_type": "test_data",
            "data": {"key": "value"}
        }
        client.post("/contexts/test_context_remove/layers", json=layer_data)
        
        # Now remove it
        response = client.delete("/contexts/test_context_remove/layers/remove_layer")
        assert response.status_code == 200
        assert "removed from context" in response.json()["message"]

class TestContextAnalytics:
    """Test context analytics endpoints"""
    
    def test_get_context_analytics_success(self):
        """Test getting context analytics successfully"""
        response = client.get("/contexts/agent_execution_001/analytics")
        assert response.status_code == 200
        
        analytics = response.json()
        assert analytics["context_id"] == "agent_execution_001"
        assert "total_layers" in analytics
        assert "total_size_mb" in analytics
        assert "access_count" in analytics
        assert "last_accessed" in analytics
        assert "created_at" in analytics
    
    def test_get_context_analytics_not_found(self):
        """Test getting analytics for non-existent context"""
        response = client.get("/contexts/nonexistent/analytics")
        assert response.status_code == 404
        assert response.json()["detail"] == "Context not found"
    
    def test_get_analytics_summary(self):
        """Test getting analytics summary"""
        response = client.get("/contexts/analytics/summary")
        assert response.status_code == 200
        
        summary = response.json()
        assert "total_contexts" in summary
        assert "total_layers" in summary
        assert "total_size_mb" in summary
        assert "total_access_count" in summary
        assert "average_layers_per_context" in summary
        assert "average_size_mb_per_context" in summary
        assert "timestamp" in summary
    
    def test_get_analytics_trends(self):
        """Test getting analytics trends"""
        response = client.get("/contexts/analytics/trends")
        assert response.status_code == 200
        
        trends = response.json()
        assert "context_creation_trend" in trends
        assert "layer_usage_trend" in trends
        assert "access_trend" in trends
        assert "timestamp" in trends
        
        # Check trend data structure
        for trend_name in ["context_creation_trend", "layer_usage_trend", "access_trend"]:
            trend_data = trends[trend_name]
            assert isinstance(trend_data, list)
            for item in trend_data:
                assert "date" in item
                assert "count" in item

class TestServiceInformation:
    """Test service information endpoints"""
    
    def test_service_info(self):
        """Test getting service information"""
        response = client.get("/info")
        assert response.status_code == 200
        
        info = response.json()
        assert info["service"] == "context-service"
        assert info["version"] == "1.0.0"
        assert "description" in info
        assert "startup_time" in info
        assert "uptime" in info
        assert "contexts_count" in info
        assert "total_layers" in info
        assert "endpoints" in info
        assert isinstance(info["endpoints"], list)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/contexts",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = client.post("/contexts", data="{}")
        assert response.status_code == 400  # FastAPI returns 400 for invalid JSON
    
    def test_large_payload(self):
        """Test handling of large payload"""
        large_data = {"data": "x" * 10000}
        response = client.post("/contexts/agent_execution_001/layers", json=large_data)
        assert response.status_code == 400  # Missing layer_id

if __name__ == "__main__":
    pytest.main([__file__]) 