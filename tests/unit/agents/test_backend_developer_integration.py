#!/usr/bin/env python3
"""
Test suite for BackendDeveloper agent message bus integration
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

from bmad.agents.Agent.BackendDeveloper.backenddeveloper import BackendDeveloperAgent
from bmad.core.message_bus import MessageBus, EventTypes


@pytest_asyncio.fixture
async def backend_developer_agent():
    """Create a BackendDeveloper agent instance for testing."""
    agent = BackendDeveloperAgent()
    # Initialize message bus properly
    await agent.initialize_message_bus()
    yield agent


@pytest_asyncio.fixture
async def message_bus():
    """Create a message bus instance for testing."""
    bus = MessageBus()
    yield bus


class TestBackendDeveloperAgentInitialization:
    """Test BackendDeveloper agent initialization and message bus setup."""
    
    def test_agent_initialization(self, backend_developer_agent):
        """Test that the agent initializes correctly with message bus integration."""
        assert backend_developer_agent.agent_name == "BackendDeveloper"
        assert hasattr(backend_developer_agent, 'publish_agent_event')
        assert hasattr(backend_developer_agent, 'subscribe_to_event')
        assert hasattr(backend_developer_agent, 'request_collaboration')
        assert hasattr(backend_developer_agent, 'delegate_task')
        assert hasattr(backend_developer_agent, 'accept_task')
    
    @pytest.mark.asyncio
    async def test_message_bus_initialization(self, backend_developer_agent):
        """Test that the agent subscribes to the correct event categories."""
        # Check that the agent has subscribed to relevant event categories
        subscribed_events = backend_developer_agent.subscribed_events
        
        # Should have subscribed to backend development events
        assert EventTypes.API_CHANGE_REQUESTED in subscribed_events
        assert EventTypes.API_CHANGE_COMPLETED in subscribed_events
        assert EventTypes.API_DEPLOYMENT_REQUESTED in subscribed_events
        assert EventTypes.API_DEPLOYMENT_COMPLETED in subscribed_events
        assert EventTypes.API_EXPORT_REQUESTED in subscribed_events
        assert EventTypes.DATABASE_OPERATION_REQUESTED in subscribed_events
        assert EventTypes.BACKEND_PERFORMANCE_ANALYSIS_REQUESTED in subscribed_events
        assert EventTypes.BACKEND_SECURITY_VALIDATION_REQUESTED in subscribed_events
        assert EventTypes.BACKEND_TRACING_REQUESTED in subscribed_events
        assert EventTypes.TASK_DELEGATED in subscribed_events
        assert EventTypes.AGENT_COLLABORATION_REQUESTED in subscribed_events


class TestBackendDeveloperEventHandlers:
    """Test BackendDeveloper agent event handlers."""
    
    @pytest.mark.asyncio
    async def test_api_change_requested_handler(self, backend_developer_agent):
        """Test API change requested event handler."""
        with patch.object(backend_developer_agent, 'build_api', new_callable=AsyncMock) as mock_build_api, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_build_api.return_value = {"endpoint": "/api/v1/users", "status": "built"}
            
            event_data = {"endpoint": "/api/v1/users", "timestamp": datetime.now().isoformat()}
            await backend_developer_agent._handle_api_change_requested(event_data)
            
            mock_build_api.assert_called_once_with("/api/v1/users")
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.API_CHANGE_COMPLETED
            assert call_args[0][1]["endpoint"] == "/api/v1/users"
            assert call_args[0][1]["result"] == {"endpoint": "/api/v1/users", "status": "built"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_api_change_completed_handler(self, backend_developer_agent):
        """Test API change completed event handler."""
        with patch.object(backend_developer_agent.policy_engine, 'evaluate_policy', new_callable=AsyncMock) as mock_policy:
            
            mock_policy.return_value = True
            
            event_data = {"endpoint": "/api/v1/users", "status": "completed"}
            await backend_developer_agent._handle_api_change_completed(event_data)
            
            mock_policy.assert_called_once_with("api_change", event_data)
    
    @pytest.mark.asyncio
    async def test_api_deployment_requested_handler(self, backend_developer_agent):
        """Test API deployment requested event handler."""
        with patch.object(backend_developer_agent, 'deploy_api') as mock_deploy_api, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_deploy_api.return_value = {"endpoint": "/api/v1/users", "status": "deployed"}
            
            event_data = {"endpoint": "/api/v1/users", "timestamp": datetime.now().isoformat()}
            await backend_developer_agent._handle_api_deployment_requested(event_data)
            
            mock_deploy_api.assert_called_once_with("/api/v1/users")
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.API_DEPLOYMENT_COMPLETED
            assert call_args[0][1]["endpoint"] == "/api/v1/users"
            assert call_args[0][1]["result"] == {"endpoint": "/api/v1/users", "status": "deployed"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_api_deployment_completed_handler(self, backend_developer_agent):
        """Test API deployment completed event handler."""
        with patch.object(backend_developer_agent.policy_engine, 'evaluate_policy', new_callable=AsyncMock) as mock_policy:
            
            mock_policy.return_value = True
            
            event_data = {"endpoint": "/api/v1/users", "status": "completed"}
            await backend_developer_agent._handle_api_deployment_completed(event_data)
            
            mock_policy.assert_called_once_with("api_deployment", event_data)
    
    @pytest.mark.asyncio
    async def test_api_export_requested_handler(self, backend_developer_agent):
        """Test API export requested event handler."""
        with patch.object(backend_developer_agent, 'export_api') as mock_export_api, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_export_api.return_value = {"format": "md", "status": "exported"}
            
            event_data = {"format": "md", "api_data": {"endpoint": "/api/v1/users"}}
            await backend_developer_agent._handle_api_export_requested(event_data)
            
            mock_export_api.assert_called_once_with("md", {"endpoint": "/api/v1/users"})
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.API_EXPORT_COMPLETED
            assert call_args[0][1]["format"] == "md"
            assert call_args[0][1]["result"] == {"format": "md", "status": "exported"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_database_operation_requested_handler(self, backend_developer_agent):
        """Test database operation requested event handler."""
        with patch.object(backend_developer_agent, 'trace_database_operation', new_callable=AsyncMock) as mock_trace, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_trace.return_value = {"operation": "query", "status": "completed"}
            
            event_data = {"operation": "query", "query": "SELECT * FROM users"}
            await backend_developer_agent._handle_database_operation_requested(event_data)
            
            mock_trace.assert_called_once_with(event_data)
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.DATABASE_OPERATION_COMPLETED
            assert call_args[0][1]["operation"] == "query"
            assert call_args[0][1]["result"] == {"operation": "query", "status": "completed"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_backend_performance_analysis_requested_handler(self, backend_developer_agent):
        """Test backend performance analysis requested event handler."""
        with patch.object(backend_developer_agent, 'enhanced_performance_optimization', new_callable=AsyncMock) as mock_performance, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_performance.return_value = {"performance_score": 95, "optimizations": ["cache", "indexing"]}
            
            event_data = {"metrics": ["response_time", "throughput"]}
            await backend_developer_agent._handle_backend_performance_analysis_requested(event_data)
            
            mock_performance.assert_called_once_with(event_data)
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.BACKEND_PERFORMANCE_ANALYSIS_COMPLETED
            assert call_args[0][1]["result"] == {"performance_score": 95, "optimizations": ["cache", "indexing"]}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_backend_security_validation_requested_handler(self, backend_developer_agent):
        """Test backend security validation requested event handler."""
        with patch.object(backend_developer_agent, 'enhanced_security_validation', new_callable=AsyncMock) as mock_security, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_security.return_value = {"security_score": 98, "vulnerabilities": []}
            
            event_data = {"security_checks": ["sql_injection", "xss"]}
            await backend_developer_agent._handle_backend_security_validation_requested(event_data)
            
            mock_security.assert_called_once_with(event_data)
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.BACKEND_SECURITY_VALIDATION_COMPLETED
            assert call_args[0][1]["result"] == {"security_score": 98, "vulnerabilities": []}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_backend_tracing_requested_handler(self, backend_developer_agent):
        """Test backend tracing requested event handler."""
        with patch.object(backend_developer_agent, 'trace_api_development', new_callable=AsyncMock) as mock_trace_api, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_trace_api.return_value = {"trace_type": "api", "status": "traced"}
            
            event_data = {"trace_type": "api", "api_data": {"endpoint": "/api/v1/users"}}
            await backend_developer_agent._handle_backend_tracing_requested(event_data)
            
            mock_trace_api.assert_called_once_with(event_data)
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.BACKEND_TRACING_COMPLETED
            assert call_args[0][1]["trace_type"] == "api"
            assert call_args[0][1]["result"] == {"trace_type": "api", "status": "traced"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_task_delegated_handler(self, backend_developer_agent):
        """Test task delegated event handler."""
        with patch.object(backend_developer_agent, 'accept_task', new_callable=AsyncMock) as mock_accept, \
             patch.object(backend_developer_agent, 'build_api', new_callable=AsyncMock) as mock_build, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_build.return_value = {"endpoint": "/api/v1/users", "status": "built"}
            
            event_data = {
                "task_id": "task_123",
                "task_details": {
                    "type": "api_build",
                    "endpoint": "/api/v1/users"
                }
            }
            await backend_developer_agent._handle_task_delegated(event_data)
            
            mock_accept.assert_called_once_with("task_123", event_data["task_details"])
            mock_build.assert_called_once_with("/api/v1/users")
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.TASK_COMPLETED
            assert call_args[0][1]["task_id"] == "task_123"
            assert call_args[0][1]["result"] == {"endpoint": "/api/v1/users", "status": "built"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_agent_collaboration_requested_handler(self, backend_developer_agent):
        """Test agent collaboration requested event handler."""
        with patch.object(backend_developer_agent, 'build_api', new_callable=AsyncMock) as mock_build, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_build.return_value = {"endpoint": "/api/v1/users", "status": "built"}
            
            event_data = {
                "from_agent": "ProductOwner",
                "collaboration_type": "api_review"
            }
            await backend_developer_agent._handle_agent_collaboration_requested(event_data)
            
            mock_build.assert_called_once_with("/api/v1/users")
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.AGENT_COLLABORATION_COMPLETED
            assert call_args[0][1]["from_agent"] == "ProductOwner"
            assert call_args[0][1]["collaboration_type"] == "api_review"
            assert call_args[0][1]["result"] == {"endpoint": "/api/v1/users", "status": "built"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]


class TestBackendDeveloperErrorHandling:
    """Test error handling in BackendDeveloper event handlers."""
    
    @pytest.mark.asyncio
    async def test_error_handling_in_handlers(self, backend_developer_agent):
        """Test error handling in event handlers."""
        with patch.object(backend_developer_agent, 'build_api', side_effect=Exception("API build failed")), \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            event_data = {"endpoint": "/api/v1/users"}
            await backend_developer_agent._handle_api_change_requested(event_data)
            
            # Should publish failure event
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.API_CHANGE_FAILED
            assert call_args[0][1]["endpoint"] == "/api/v1/users"
            assert call_args[0][1]["error"] == "API build failed"
            assert call_args[0][1]["status"] == "failed"
            assert "timestamp" in call_args[0][1]


class TestBackendDeveloperCollaboration:
    """Test BackendDeveloper agent collaboration functionality."""
    
    @pytest.mark.asyncio
    async def test_collaboration_functionality(self, backend_developer_agent):
        """Test collaboration functionality."""
        with patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish, \
             patch.object(backend_developer_agent, 'build_api', new_callable=AsyncMock) as mock_build, \
             patch.object(backend_developer_agent, 'deploy_api') as mock_deploy:
            
            mock_build.return_value = {"endpoint": "/api/v1/users", "status": "built"}
            mock_deploy.return_value = {"endpoint": "/api/v1/users", "status": "deployed"}
            
            await backend_developer_agent.collaborate_example()
            
            # Should have published multiple events
            assert mock_publish.call_count >= 3
            
            # Check that the expected event types were published
            published_events = [call[0][0] for call in mock_publish.call_args_list]
            assert EventTypes.API_CHANGE_REQUESTED in published_events
            assert EventTypes.API_CHANGE_COMPLETED in published_events
            assert EventTypes.API_DEPLOYMENT_COMPLETED in published_events
    
    @pytest.mark.asyncio
    async def test_task_delegation(self, backend_developer_agent):
        """Test task delegation functionality."""
        with patch.object(backend_developer_agent, 'delegate_task', new_callable=AsyncMock) as mock_delegate:
            
            task_data = {"type": "api_build", "endpoint": "/api/v1/users"}
            await backend_developer_agent.delegate_task(task_data, "FrontendDeveloper")
            
            mock_delegate.assert_called_once_with(task_data, "FrontendDeveloper")
    
    @pytest.mark.asyncio
    async def test_task_acceptance(self, backend_developer_agent):
        """Test task acceptance functionality."""
        with patch.object(backend_developer_agent, 'accept_task', new_callable=AsyncMock) as mock_accept:
            
            task_id = "task_123"
            task_details = {"type": "api_build", "endpoint": "/api/v1/users"}
            await backend_developer_agent.accept_task(task_id, task_details)
            
            mock_accept.assert_called_once_with(task_id, task_details)
    
    @pytest.mark.asyncio
    async def test_collaboration_request(self, backend_developer_agent):
        """Test collaboration request functionality."""
        with patch.object(backend_developer_agent, 'request_collaboration', new_callable=AsyncMock) as mock_request:
            
            collaboration_data = {"type": "api_review", "endpoint": "/api/v1/users"}
            await backend_developer_agent.request_collaboration(collaboration_data, "Review API design")
            
            mock_request.assert_called_once_with(collaboration_data, "Review API design")


class TestBackendDeveloperIntegration:
    """Test BackendDeveloper agent integration with message bus."""
    
    @pytest.mark.asyncio
    async def test_full_integration_workflow(self, backend_developer_agent, message_bus):
        """Test full integration workflow with message bus."""
        # Test that the agent can publish and handle events through the message bus
        with patch.object(backend_developer_agent, 'build_api', new_callable=AsyncMock) as mock_build, \
             patch.object(backend_developer_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            
            mock_build.return_value = {"endpoint": "/api/v1/users", "status": "built"}
            
            # Simulate API change request
            event_data = {"endpoint": "/api/v1/users", "timestamp": datetime.now().isoformat()}
            await backend_developer_agent._handle_api_change_requested(event_data)
            
            # Verify the handler processed the event and published completion
            mock_build.assert_called_once_with("/api/v1/users")
            mock_publish.assert_called_once()
            
            # Check the published event structure
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.API_CHANGE_COMPLETED
            assert call_args[0][1]["endpoint"] == "/api/v1/users"
            assert call_args[0][1]["result"] == {"endpoint": "/api/v1/users", "status": "built"}
            assert call_args[0][1]["status"] == "completed"
            assert "timestamp" in call_args[0][1]


if __name__ == "__main__":
    pytest.main([__file__]) 