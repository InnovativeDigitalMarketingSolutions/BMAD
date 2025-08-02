import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
import threading
import time

import bmad.agents.core.communication.message_bus as mb

@pytest.fixture
def temp_context_file():
    """Temporary context file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"events": []}, f)
        temp_path = f.name
    
    # Store original path
    original_path = mb.SHARED_CONTEXT_PATH
    
    # Patch the path
    mb.SHARED_CONTEXT_PATH = Path(temp_path)
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass
    
    # Restore original path
    mb.SHARED_CONTEXT_PATH = original_path

@pytest.fixture
def reset_subscribers():
    """Reset subscribers before and after each test."""
    original_subscribers = mb._subscribers.copy()
    mb._subscribers.clear()
    yield
    mb._subscribers.clear()
    mb._subscribers.update(original_subscribers)

class TestMessageBusPublish:
    """Test publish functionality."""
    
    def test_publish_new_event(self, temp_context_file, reset_subscribers):
        """Test publishing a new event."""
        event = "test_event"
        data = {"key": "value"}
        
        mb.publish(event, data)
        
        # Check if file was written
        with open(temp_context_file, 'r') as f:
            context = json.load(f)
        
        assert len(context["events"]) == 1
        assert context["events"][0]["event"] == event
        assert context["events"][0]["data"] == data
        assert "timestamp" in context["events"][0]
    
    def test_publish_multiple_events(self, temp_context_file, reset_subscribers):
        """Test publishing multiple events."""
        mb.publish("event1", {"data": 1})
        mb.publish("event2", {"data": 2})
        mb.publish("event3", {"data": 3})
        
        with open(temp_context_file, 'r') as f:
            context = json.load(f)
        
        assert len(context["events"]) == 3
        assert context["events"][0]["event"] == "event1"
        assert context["events"][1]["event"] == "event2"
        assert context["events"][2]["event"] == "event3"
    
    def test_publish_to_nonexistent_file(self, reset_subscribers):
        """Test publishing when context file doesn't exist."""
        # Use a path in a writable directory
        with patch.object(mb, 'SHARED_CONTEXT_PATH', Path('/tmp/test_message_bus.json')):
            mb.publish("test_event", {"data": "test"})
            
            # Should create the file
            assert mb.SHARED_CONTEXT_PATH.exists()
            
            with open(mb.SHARED_CONTEXT_PATH, 'r') as f:
                context = json.load(f)
            
            assert len(context["events"]) == 1
            assert context["events"][0]["event"] == "test_event"
            
            # Cleanup
            try:
                mb.SHARED_CONTEXT_PATH.unlink()
            except:
                pass
    
    def test_publish_with_subscriber_callback(self, temp_context_file, reset_subscribers):
        """Test publishing with subscriber callback."""
        callback_called = False
        callback_data = None
        
        def test_callback(event_obj):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = event_obj
        
        mb.subscribe("test_event", test_callback)
        mb.publish("test_event", {"data": "test"})
        
        assert callback_called
        assert callback_data["event"] == "test_event"
        assert callback_data["data"] == {"data": "test"}
    
    def test_publish_with_subscriber_error(self, temp_context_file, reset_subscribers, caplog):
        """Test publishing when subscriber callback raises an error."""
        def error_callback(event_obj):
            raise ValueError("Test error")
        
        mb.subscribe("test_event", error_callback)
        mb.publish("test_event", {"data": "test"})
        
        # Should log error but not crash
        assert "Fout in subscriber callback" in caplog.text
        assert "Test error" in caplog.text
    
    def test_publish_threading_safety(self, temp_context_file, reset_subscribers):
        """Test that publish is thread-safe."""
        def publish_events():
            for i in range(10):
                mb.publish(f"event_{i}", {"data": i})
                time.sleep(0.001)  # Small delay
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=publish_events)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all events were written
        with open(temp_context_file, 'r') as f:
            context = json.load(f)
        
        assert len(context["events"]) == 50  # 5 threads * 10 events each

class TestMessageBusSubscribe:
    """Test subscribe functionality."""
    
    def test_subscribe_new_event_type(self, reset_subscribers):
        """Test subscribing to a new event type."""
        def test_callback(event_obj):
            pass
        
        mb.subscribe("new_event", test_callback)
        
        assert "new_event" in mb._subscribers
        assert len(mb._subscribers["new_event"]) == 1
        assert mb._subscribers["new_event"][0] == test_callback
    
    def test_subscribe_existing_event_type(self, reset_subscribers):
        """Test subscribing to an existing event type."""
        def callback1(event_obj):
            pass
        
        def callback2(event_obj):
            pass
        
        mb.subscribe("existing_event", callback1)
        mb.subscribe("existing_event", callback2)
        
        assert len(mb._subscribers["existing_event"]) == 2
        assert mb._subscribers["existing_event"][0] == callback1
        assert mb._subscribers["existing_event"][1] == callback2
    
    def test_subscribe_multiple_callbacks(self, reset_subscribers):
        """Test subscribing multiple callbacks to same event."""
        callbacks = []
        for i in range(5):
            def make_callback(num):
                def callback(event_obj):
                    pass
                return callback
            callbacks.append(make_callback(i))
            mb.subscribe("multi_event", callbacks[i])
        
        assert len(mb._subscribers["multi_event"]) == 5

class TestMessageBusGetEvents:
    """Test get_events functionality."""
    
    def test_get_events_empty_file(self, temp_context_file):
        """Test getting events from empty file."""
        events = mb.get_events()
        assert events == []
    
    def test_get_events_nonexistent_file(self):
        """Test getting events when file doesn't exist."""
        with patch.object(mb, 'SHARED_CONTEXT_PATH', Path('/nonexistent/path.json')):
            events = mb.get_events()
            assert events == []
    
    @pytest.mark.asyncio
    async @pytest.mark.asyncio
    async def test_get_events_with_data(self, temp_context_file):
        """Test getting events with data."""
        # Create some test events
        test_events = [
            {"timestamp": "2023-01-01T10:00:00", "event": "event1", "data": {"a": 1}},
            {"timestamp": "2023-01-01T11:00:00", "event": "event2", "data": {"b": 2}},
            {"timestamp": "2023-01-01T12:00:00", "event": "event1", "data": {"c": 3}}
        ]
        
        with open(temp_context_file, 'w') as f:
            json.dump({"events": test_events}, f)
        
        events = mb.get_events()
        assert len(events) == 3
        assert events[0]["event"] == "event1"
        assert events[1]["event"] == "event2"
        assert events[2]["event"] == "event1"
    
    def test_get_events_filter_by_type(self, temp_context_file):
        """Test filtering events by type."""
        test_events = [
            {"timestamp": "2023-01-01T10:00:00", "event": "event1", "data": {"a": 1}},
            {"timestamp": "2023-01-01T11:00:00", "event": "event2", "data": {"b": 2}},
            {"timestamp": "2023-01-01T12:00:00", "event": "event1", "data": {"c": 3}}
        ]
        
        with open(temp_context_file, 'w') as f:
            json.dump({"events": test_events}, f)
        
        events = mb.get_events(event_type="event1")
        assert len(events) == 2
        assert all(e["event"] == "event1" for e in events)
    
    def test_get_events_filter_by_time(self, temp_context_file):
        """Test filtering events by time."""
        test_events = [
            {"timestamp": "2023-01-01T10:00:00", "event": "event1", "data": {"a": 1}},
            {"timestamp": "2023-01-01T11:00:00", "event": "event2", "data": {"b": 2}},
            {"timestamp": "2023-01-01T12:00:00", "event": "event3", "data": {"c": 3}}
        ]
        
        with open(temp_context_file, 'w') as f:
            json.dump({"events": test_events}, f)
        
        # Filter events after 10:30
        events = mb.get_events(since="2023-01-01T10:30:00")
        assert len(events) == 2
        assert events[0]["event"] == "event2"
        assert events[1]["event"] == "event3"
    
    def test_get_events_filter_by_type_and_time(self, temp_context_file):
        """Test filtering events by both type and time."""
        test_events = [
            {"timestamp": "2023-01-01T10:00:00", "event": "event1", "data": {"a": 1}},
            {"timestamp": "2023-01-01T11:00:00", "event": "event1", "data": {"b": 2}},
            {"timestamp": "2023-01-01T12:00:00", "event": "event2", "data": {"c": 3}}
        ]
        
        with open(temp_context_file, 'w') as f:
            json.dump({"events": test_events}, f)
        
        # Filter event1 events after 10:30
        events = mb.get_events(event_type="event1", since="2023-01-01T10:30:00")
        assert len(events) == 1
        assert events[0]["event"] == "event1"
        assert events[0]["data"] == {"b": 2}

class TestMessageBusClearEvents:
    """Test clear_events functionality."""
    
    def test_clear_events_empty_file(self, temp_context_file):
        """Test clearing events from empty file."""
        mb.clear_events()
        
        with open(temp_context_file, 'r') as f:
            context = json.load(f)
        
        assert context["events"] == []
    
    @pytest.mark.asyncio
    async @pytest.mark.asyncio
    async def test_clear_events_with_data(self, temp_context_file):
        """Test clearing events with existing data."""
        # Add some events first
        test_events = [
            {"timestamp": "2023-01-01T10:00:00", "event": "event1", "data": {"a": 1}},
            {"timestamp": "2023-01-01T11:00:00", "event": "event2", "data": {"b": 2}}
        ]
        
        with open(temp_context_file, 'w') as f:
            json.dump({"events": test_events}, f)
        
        # Verify events exist
        with open(temp_context_file, 'r') as f:
            context = json.load(f)
        assert len(context["events"]) == 2
        
        # Clear events
        mb.clear_events()
        
        # Verify events are cleared
        with open(temp_context_file, 'r') as f:
            context = json.load(f)
        assert context["events"] == []
    
    def test_clear_events_nonexistent_file(self):
        """Test clearing events when file doesn't exist."""
        with patch.object(mb, 'SHARED_CONTEXT_PATH', Path('/tmp/test_clear_events.json')):
            mb.clear_events()
            
            # Should create the file with empty events
            assert mb.SHARED_CONTEXT_PATH.exists()
            
            with open(mb.SHARED_CONTEXT_PATH, 'r') as f:
                context = json.load(f)
            
            assert context["events"] == []
            
            # Cleanup
            try:
                mb.SHARED_CONTEXT_PATH.unlink()
            except:
                pass

class TestMessageBusIntegration:
    """Integration tests for message bus."""
    
    @pytest.mark.asyncio
    async @pytest.mark.asyncio
    async @pytest.mark.asyncio
    async def test_full_workflow(self, temp_context_file, reset_subscribers):
        """Test complete message bus workflow."""
        # Subscribe to events
        received_events = []
        def event_callback(event_obj):
            received_events.append(event_obj)
        
        mb.subscribe("workflow_event", event_callback)
        
        # Publish events
        mb.publish("workflow_event", {"step": 1, "data": "start"})
        mb.publish("workflow_event", {"step": 2, "data": "process"})
        mb.publish("workflow_event", {"step": 3, "data": "complete"})
        
        # Check subscribers were called
        assert len(received_events) == 3
        assert received_events[0]["data"]["step"] == 1
        assert received_events[1]["data"]["step"] == 2
        assert received_events[2]["data"]["step"] == 3
        
        # Check events were saved to file
        events = mb.get_events("workflow_event")
        assert len(events) == 3
        
        # Clear events
        mb.clear_events()
        events = mb.get_events()
        assert events == []
    
    def test_multiple_event_types(self, temp_context_file, reset_subscribers):
        """Test handling multiple event types."""
        event1_calls = []
        event2_calls = []
        
        def callback1(event_obj):
            event1_calls.append(event_obj)
        
        def callback2(event_obj):
            event2_calls.append(event_obj)
        
        mb.subscribe("event1", callback1)
        mb.subscribe("event2", callback2)
        
        # Publish mixed events
        mb.publish("event1", {"data": "a"})
        mb.publish("event2", {"data": "b"})
        mb.publish("event1", {"data": "c"})
        
        # Check callbacks
        assert len(event1_calls) == 2
        assert len(event2_calls) == 1
        assert event1_calls[0]["data"]["data"] == "a"
        assert event1_calls[1]["data"]["data"] == "c"
        assert event2_calls[0]["data"]["data"] == "b"
        
        # Check file filtering
        event1_events = mb.get_events("event1")
        event2_events = mb.get_events("event2")
        assert len(event1_events) == 2
        assert len(event2_events) == 1 