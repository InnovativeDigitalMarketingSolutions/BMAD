#!/usr/bin/env python3
"""
Tests for BMAD Message Bus System
"""

import asyncio
import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from bmad.core.message_bus import (
    MessageBus,
    get_message_bus,
    publish_event,
    subscribe_to_event,
    EventTypes,
    AgentMessageBusIntegration,
    create_agent_integration
)

class TestMessageBus:
    """Test MessageBus class"""
    
    @pytest.fixture
    def message_bus(self):
        """Create a message bus instance for testing"""
        return MessageBus(use_redis=False)
    
    @pytest.fixture
    def event_data(self):
        """Sample event data"""
        return {
            "test_key": "test_value",
            "number": 42,
            "nested": {"key": "value"}
        }
    
    @pytest.mark.asyncio
    async def test_publish_event(self, message_bus, event_data):
        """Test publishing an event"""
        # Subscribe to test event
        received_events = []
        
        async def test_handler(event):
            received_events.append(event)
        
        await message_bus.subscribe("test_event", test_handler)
        
        # Publish event
        success = await message_bus.publish("test_event", event_data, "TestAgent")
        
        assert success is True
        assert len(received_events) == 1
        assert received_events[0].event_type == "test_event"
        assert received_events[0].data == event_data
        assert received_events[0].source_agent == "TestAgent"
    
    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe(self, message_bus):
        """Test subscribing and unsubscribing from events"""
        received_events = []
        
        async def test_handler(event):
            received_events.append(event)
        
        # Subscribe
        success = await message_bus.subscribe("test_event", test_handler)
        assert success is True
        
        # Publish event
        await message_bus.publish("test_event", {"data": "test"}, "TestAgent")
        assert len(received_events) == 1
        
        # Unsubscribe
        success = await message_bus.unsubscribe("test_event", test_handler)
        assert success is True
        
        # Publish another event
        await message_bus.publish("test_event", {"data": "test2"}, "TestAgent")
        assert len(received_events) == 1  # Should not receive the second event
    
    @pytest.mark.asyncio
    async def test_get_events(self, message_bus, event_data):
        """Test getting recent events"""
        # Publish multiple events
        await message_bus.publish("event1", event_data, "Agent1")
        await message_bus.publish("event2", event_data, "Agent2")
        await message_bus.publish("event1", event_data, "Agent3")
        
        # Get all events
        events = await message_bus.get_events()
        assert len(events) == 3
        
        # Get events by type
        event1_events = await message_bus.get_events("event1")
        assert len(event1_events) == 2
        
        # Get events with limit
        limited_events = await message_bus.get_events(limit=2)
        assert len(limited_events) == 2
    
    @pytest.mark.asyncio
    async def test_event_persistence(self, message_bus, event_data, tmp_path):
        """Test event persistence to file"""
        # Set custom event file path
        message_bus.event_file = tmp_path / "test_events.json"
        
        # Publish event
        await message_bus.publish("test_event", event_data, "TestAgent")
        
        # Check if file was created
        assert message_bus.event_file.exists()
        
        # Load events from file
        with open(message_bus.event_file, 'r') as f:
            data = json.load(f)
        
        assert "events" in data
        assert len(data["events"]) == 1
        assert data["events"][0]["event_type"] == "test_event"

class TestEventTypes:
    """Test EventTypes class"""
    
    def test_event_types_exist(self):
        """Test that event types are defined"""
        assert hasattr(EventTypes, 'USER_STORY_CREATED')
        assert hasattr(EventTypes, 'FEEDBACK_COLLECTED')
        assert hasattr(EventTypes, 'QUALITY_GATE_PASSED')
        assert hasattr(EventTypes, 'AGENT_STARTED')
    
    def test_event_categories(self):
        """Test event categories"""
        from bmad.core.message_bus import get_events_by_category, EVENT_CATEGORIES
        
        # Test getting events by category
        feedback_events = get_events_by_category("feedback")
        assert len(feedback_events) > 0
        assert EventTypes.FEEDBACK_COLLECTED in feedback_events
        
        # Test all categories exist
        for category in EVENT_CATEGORIES:
            events = get_events_by_category(category)
            assert len(events) > 0

class TestAgentMessageBusIntegration:
    """Test AgentMessageBusIntegration class"""
    
    @pytest.fixture
    def agent_integration(self):
        """Create an agent integration instance"""
        return AgentMessageBusIntegration("TestAgent")
    
    @pytest.mark.asyncio
    async def test_initialization(self, agent_integration):
        """Test agent integration initialization"""
        success = await agent_integration.initialize_message_bus()
        assert success is True
        assert len(agent_integration.subscribed_events) > 0
    
    @pytest.mark.asyncio
    async def test_publish_agent_event(self, agent_integration):
        """Test publishing agent events"""
        await agent_integration.initialize_message_bus()
        
        event_data = {"test": "data"}
        success = await agent_integration.publish_agent_event(
            EventTypes.FEEDBACK_COLLECTED,
            event_data
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_request_collaboration(self, agent_integration):
        """Test requesting collaboration"""
        await agent_integration.initialize_message_bus()
        
        task = {"type": "feedback_analysis", "data": "test"}
        success = await agent_integration.request_collaboration("OtherAgent", task)
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_delegate_task(self, agent_integration):
        """Test delegating tasks"""
        await agent_integration.initialize_message_bus()
        
        task = {"type": "feedback_analysis", "data": "test"}
        success = await agent_integration.delegate_task("OtherAgent", task)
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_accept_task(self, agent_integration):
        """Test accepting tasks"""
        await agent_integration.initialize_message_bus()
        
        task_details = {"type": "feedback_analysis", "data": "test"}
        success = await agent_integration.accept_task("task_123", task_details)
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_complete_task(self, agent_integration):
        """Test completing tasks"""
        await agent_integration.initialize_message_bus()
        
        result = {"status": "completed", "data": "result"}
        success = await agent_integration.complete_task("task_123", result)
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_custom_event_handler(self, agent_integration):
        """Test custom event handlers"""
        await agent_integration.initialize_message_bus()
        
        received_events = []
        
        async def custom_handler(event):
            received_events.append(event)
        
        await agent_integration.register_event_handler(
            EventTypes.FEEDBACK_COLLECTED,
            custom_handler
        )
        
        # Publish event that should trigger handler
        await agent_integration.publish_agent_event(
            EventTypes.FEEDBACK_COLLECTED,
            {"test": "data"}
        )
        
        # Wait a bit for async processing
        await asyncio.sleep(0.1)
        
        # Check that the handler was registered
        assert EventTypes.FEEDBACK_COLLECTED in agent_integration.event_handlers
        assert agent_integration.event_handlers[EventTypes.FEEDBACK_COLLECTED] == custom_handler

class TestMessageBusIntegration:
    """Test message bus integration functions"""
    
    @pytest.mark.asyncio
    async def test_get_message_bus_singleton(self):
        """Test that get_message_bus returns singleton"""
        bus1 = get_message_bus()
        bus2 = get_message_bus()
        assert bus1 is bus2
    
    @pytest.mark.asyncio
    async def test_publish_event_function(self):
        """Test publish_event convenience function"""
        event_data = {"test": "data"}
        success = await publish_event("test_event", event_data, "TestAgent")
        assert success is True
    
    @pytest.mark.asyncio
    async def test_subscribe_to_event_function(self):
        """Test subscribe_to_event convenience function"""
        async def test_handler(event):
            pass
        
        success = await subscribe_to_event("test_event", test_handler)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_create_agent_integration(self):
        """Test create_agent_integration function"""
        integration = await create_agent_integration("TestAgent", ["feedback"])
        assert isinstance(integration, AgentMessageBusIntegration)
        assert integration.agent_name == "TestAgent"

class TestMessageBusErrorHandling:
    """Test message bus error handling"""
    
    @pytest.mark.asyncio
    async def test_publish_event_with_invalid_data(self):
        """Test publishing event with invalid data"""
        # This should not raise an exception
        success = await publish_event("test_event", None, "TestAgent")
        # The message bus handles None data gracefully, so this should succeed
        assert success is True
    
    @pytest.mark.asyncio
    async def test_subscribe_with_invalid_handler(self):
        """Test subscribing with invalid handler"""
        # This should not raise an exception
        success = await subscribe_to_event("test_event", None)
        # The message bus handles None handlers gracefully, so this should succeed
        assert success is True
    
    @pytest.mark.asyncio
    async def test_agent_integration_with_invalid_agent_name(self):
        """Test agent integration with invalid agent name"""
        integration = AgentMessageBusIntegration("")
        success = await integration.initialize_message_bus()
        # Should still work but log warnings
        assert success is True

if __name__ == "__main__":
    pytest.main([__file__]) 