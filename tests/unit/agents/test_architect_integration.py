#!/usr/bin/env python3
"""
Test suite for Architect Agent Message Bus Integration
Tests the integration of Architect agent with the new message bus system
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from bmad.agents.Agent.Architect.architect import ArchitectAgent
from bmad.core.message_bus import EventTypes, get_message_bus


@pytest_asyncio.fixture
async def architect_agent():
    """Create an Architect agent instance for testing."""
    agent = ArchitectAgent()
    yield agent


class TestArchitectAgentIntegration:
    """Test Architect agent message bus integration."""
    
    def test_agent_initialization(self, architect_agent):
        """Test that the agent initializes correctly."""
        assert architect_agent.agent_name == "Architect"
        assert hasattr(architect_agent, 'publish_agent_event')
        assert hasattr(architect_agent, 'subscribe_to_event')
        assert hasattr(architect_agent, 'request_collaboration')
        assert hasattr(architect_agent, 'delegate_task')
        assert hasattr(architect_agent, 'accept_task')
    
    @pytest.mark.asyncio
    async def test_message_bus_initialization(self, architect_agent):
        """Test message bus initialization."""
        await architect_agent.initialize_message_bus()
        
        # Check that agent has the required event handlers
        assert hasattr(architect_agent, '_handle_api_design_requested')
        assert hasattr(architect_agent, '_handle_system_design_requested')
        assert hasattr(architect_agent, '_handle_architecture_review_requested')
        assert hasattr(architect_agent, '_handle_tech_stack_evaluation_requested')
        assert hasattr(architect_agent, '_handle_pipeline_advice_requested')
        assert hasattr(architect_agent, '_handle_task_delegated')
    
    @pytest.mark.asyncio
    async def test_event_handler_registration(self, architect_agent):
        """Test that event handlers are registered correctly."""
        await architect_agent.initialize_message_bus()
        
        # Check that specific event handlers are registered
        assert hasattr(architect_agent, '_handle_api_design_requested')
        assert hasattr(architect_agent, '_handle_system_design_requested')
        assert hasattr(architect_agent, '_handle_architecture_review_requested')
        assert hasattr(architect_agent, '_handle_tech_stack_evaluation_requested')
        assert hasattr(architect_agent, '_handle_pipeline_advice_requested')
        assert hasattr(architect_agent, '_handle_task_delegated')
    
    @pytest.mark.asyncio
    async def test_api_design_handler(self, architect_agent):
        """Test API design request handler."""
        event_data = {
            "request_id": "test-123",
            "requirements": {"endpoint": "/api/users", "method": "GET"}
        }
        
        with patch.object(architect_agent, 'design_api', new_callable=AsyncMock) as mock_design:
            mock_design.return_value = {"api_design": "test_design"}
            
            with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                await architect_agent._handle_api_design_requested(event_data)
                
                mock_design.assert_called_once_with(event_data.get("requirements", {}))
                mock_publish.assert_called_once_with(EventTypes.API_DESIGN_COMPLETED, {
                    "request_id": "test-123",
                    "api_design": {"api_design": "test_design"},
                    "status": "completed"
                })
    
    @pytest.mark.asyncio
    async def test_system_design_handler(self, architect_agent):
        """Test system design request handler."""
        event_data = {
            "request_id": "test-456",
            "requirements": {"system_type": "web_application"}
        }
        
        with patch.object(architect_agent, 'design_system', new_callable=AsyncMock) as mock_design:
            mock_design.return_value = {"system_design": "test_system"}
            
            with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                await architect_agent._handle_system_design_requested(event_data)
                
                mock_design.assert_called_once()
                mock_publish.assert_called_once_with(EventTypes.SYSTEM_DESIGN_COMPLETED, {
                    "request_id": "test-456",
                    "system_design": {"system_design": "test_system"},
                    "status": "completed"
                })
    
    @pytest.mark.asyncio
    async def test_architecture_review_handler(self, architect_agent):
        """Test architecture review request handler."""
        event_data = {
            "request_id": "test-789",
            "architecture": {"type": "microservices"}
        }
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent._handle_architecture_review_requested(event_data)
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.ARCHITECTURE_REVIEW_COMPLETED
            assert call_args[0][1]["request_id"] == "test-789"
            assert call_args[0][1]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_tech_stack_evaluation_handler(self, architect_agent):
        """Test tech stack evaluation request handler."""
        event_data = {
            "request_id": "test-101",
            "tech_stack": ["python", "react", "postgresql"]
        }
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent._handle_tech_stack_evaluation_requested(event_data)
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.TECH_STACK_EVALUATION_COMPLETED
            assert call_args[0][1]["request_id"] == "test-101"
            assert call_args[0][1]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_pipeline_advice_handler(self, architect_agent):
        """Test pipeline advice request handler."""
        event_data = {
            "request_id": "test-202",
            "pipeline_config": "test_pipeline_config"
        }
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent._handle_pipeline_advice_requested(event_data)
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.PIPELINE_ADVICE_COMPLETED
            assert call_args[0][1]["request_id"] == "test-202"
            assert call_args[0][1]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_task_delegated_handler(self, architect_agent):
        """Test task delegation handler."""
        event_data = {
            "task_id": "task-123",
            "task_type": "architecture_review",
            "assigned_to": "Architect"
        }
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent._handle_task_delegated(event_data)
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.TASK_COMPLETED
            assert call_args[0][1]["task_id"] == "task-123"
            assert call_args[0][1]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_run_async_integration(self, architect_agent):
        """Test run_async method integration."""
        with patch.object(architect_agent, 'initialize_message_bus', new_callable=AsyncMock) as mock_init:
            await architect_agent.run_async()
            
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collaboration_functionality(self, architect_agent):
        """Test collaboration functionality."""
        collaboration_data = {
            "type": "architecture_review",
            "agents": ["ProductOwner", "BackendDeveloper"],
            "requirements": {"review_type": "system_design"}
        }
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent.request_collaboration(collaboration_data, "Review system architecture")
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.AGENT_COLLABORATION_REQUESTED
            assert "from_agent" in call_args[0][1]
            assert call_args[0][1]["from_agent"] == "Architect"
    
    @pytest.mark.asyncio
    async def test_task_delegation(self, architect_agent):
        """Test task delegation functionality."""
        task_data = {
            "type": "api_design",
            "requirements": {"endpoint": "/api/users"}
        }
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent.delegate_task(task_data, "BackendDeveloper")
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.TASK_DELEGATED
            assert "from_agent" in call_args[0][1]
            assert call_args[0][1]["from_agent"] == "Architect"
    
    @pytest.mark.asyncio
    async def test_task_acceptance(self, architect_agent):
        """Test task acceptance functionality."""
        task_id = "task-456"
        task_details = {"id": task_id, "type": "architecture_review"}
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent.accept_task(task_id, task_details)
            
            # Check that the method was called with the correct event type
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args
            assert call_args[0][0] == EventTypes.TASK_ACCEPTED
            assert call_args[0][1]["task_id"] == task_id
            assert call_args[0][1]["accepted_by"] == "Architect"
    
    @pytest.mark.asyncio
    async def test_error_handling_in_handlers(self, architect_agent):
        """Test error handling in event handlers."""
        event_data = {"request_id": "test-error"}
        
        with patch.object(architect_agent, 'design_api', side_effect=Exception("Test error")):
            with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                await architect_agent._handle_api_design_requested(event_data)
                
                # Check that the method was called with the correct event type
                mock_publish.assert_called_once()
                call_args = mock_publish.call_args
                assert call_args[0][0] == EventTypes.API_DESIGN_FAILED
                assert call_args[0][1]["request_id"] == "test-error"
                assert call_args[0][1]["status"] == "failed"
    
    @pytest.mark.asyncio
    async def test_event_publishing(self, architect_agent):
        """Test event publishing functionality."""
        event_data = {"test": "data"}
        
        with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await architect_agent.publish_agent_event(EventTypes.ARCHITECTURE_DESIGN_COMPLETED, event_data)
            
            mock_publish.assert_called_once_with(EventTypes.ARCHITECTURE_DESIGN_COMPLETED, event_data)
    
    @pytest.mark.asyncio
    async def test_event_subscription(self, architect_agent):
        """Test event subscription functionality."""
        with patch.object(architect_agent, 'subscribe_to_event', new_callable=AsyncMock) as mock_subscribe:
            await architect_agent.subscribe_to_event(EventTypes.API_DESIGN_REQUESTED, AsyncMock())
            
            mock_subscribe.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_category_subscription(self, architect_agent):
        """Test category subscription functionality."""
        with patch.object(architect_agent, 'subscribe_to_event_category', new_callable=AsyncMock) as mock_subscribe:
            await architect_agent.subscribe_to_event_category("architecture")
            
            mock_subscribe.assert_called_once_with("architecture")


class TestArchitectAgentEventHandlers:
    """Test specific event handler implementations."""
    
    @pytest.mark.asyncio
    async def test_handle_api_design_requested_success(self, architect_agent):
        """Test successful API design request handling."""
        event_data = {
            "request_id": "api-123",
            "requirements": {"endpoint": "/api/users", "method": "GET"}
        }
        
        with patch.object(architect_agent, 'design_api', new_callable=AsyncMock) as mock_design:
            mock_design.return_value = {"api": "design"}
            
            with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                await architect_agent._handle_api_design_requested(event_data)
                
                mock_design.assert_called_once_with({"endpoint": "/api/users", "method": "GET"})
                mock_publish.assert_called_once_with(EventTypes.API_DESIGN_COMPLETED, {
                    "request_id": "api-123",
                    "api_design": {"api": "design"},
                    "status": "completed"
                })
    
    @pytest.mark.asyncio
    async def test_handle_system_design_requested_success(self, architect_agent):
        """Test successful system design request handling."""
        event_data = {
            "request_id": "sys-123",
            "requirements": {"system_type": "web_application"}
        }
        
        with patch.object(architect_agent, 'design_system', new_callable=AsyncMock) as mock_design:
            mock_design.return_value = {"system": "design"}
            
            with patch.object(architect_agent, 'publish_agent_event', new_callable=AsyncMock) as mock_publish:
                await architect_agent._handle_system_design_requested(event_data)
                
                mock_design.assert_called_once()
                mock_publish.assert_called_once_with(EventTypes.SYSTEM_DESIGN_COMPLETED, {
                    "request_id": "sys-123",
                    "system_design": {"system": "design"},
                    "status": "completed"
                })


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 