"""
Unit Tests for Enhanced Context Manager

Tests the enhanced context management functionality including:
- Context layering and priority resolution
- Context persistence and retrieval
- Context sharing between agents
- Context versioning and analytics
- Context optimization and cleanup
- Error handling and edge cases
"""

import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock, call
from datetime import datetime, timedelta
from pathlib import Path
import pytest
import threading
import time

# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from bmad.agents.core.communication.enhanced_context_manager import (
    EnhancedContextManager,
    ContextLayerManager,
    ContextEntry,
    ContextLayer,
    ContextType,
    CONTEXT_STORAGE_PATH
)


class TestContextEntry(unittest.TestCase):
    """Test ContextEntry data class functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.now = datetime.now()
        self.entry = ContextEntry(
            id="test-id",
            layer=ContextLayer.SESSION,
            context_type=ContextType.STATE,
            key="test_key",
            value="test_value",
            metadata={"test": "metadata"},
            created_at=self.now,
            updated_at=self.now,
            expires_at=self.now + timedelta(hours=1),
            version=1
        )
    
    def test_context_entry_creation(self):
        """Test ContextEntry creation with all fields."""
        self.assertEqual(self.entry.id, "test-id")
        self.assertEqual(self.entry.layer, ContextLayer.SESSION)
        self.assertEqual(self.entry.context_type, ContextType.STATE)
        self.assertEqual(self.entry.key, "test_key")
        self.assertEqual(self.entry.value, "test_value")
        self.assertEqual(self.entry.metadata, {"test": "metadata"})
        self.assertEqual(self.entry.version, 1)
    
    def test_context_entry_to_dict(self):
        """Test ContextEntry serialization to dictionary."""
        data = self.entry.to_dict()
        
        self.assertEqual(data["id"], "test-id")
        self.assertEqual(data["layer"], ContextLayer.SESSION.value)
        self.assertEqual(data["context_type"], ContextType.STATE.value)
        self.assertEqual(data["key"], "test_key")
        self.assertEqual(data["value"], "test_value")
        self.assertEqual(data["metadata"], {"test": "metadata"})
        self.assertEqual(data["version"], 1)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("expires_at", data)
    
    def test_context_entry_from_dict(self):
        """Test ContextEntry deserialization from dictionary."""
        data = self.entry.to_dict()
        restored_entry = ContextEntry.from_dict(data)
        
        self.assertEqual(restored_entry.id, self.entry.id)
        self.assertEqual(restored_entry.layer, self.entry.layer)
        self.assertEqual(restored_entry.context_type, self.entry.context_type)
        self.assertEqual(restored_entry.key, self.entry.key)
        self.assertEqual(restored_entry.value, self.entry.value)
        self.assertEqual(restored_entry.metadata, self.entry.metadata)
        self.assertEqual(restored_entry.version, self.entry.version)
    
    def test_context_entry_without_expiry(self):
        """Test ContextEntry creation without expiry."""
        entry = ContextEntry(
            id="test-id",
            layer=ContextLayer.GLOBAL,
            context_type=ContextType.CONFIGURATION,
            key="test_key",
            value="test_value",
            metadata={},
            created_at=self.now,
            updated_at=self.now
        )
        
        self.assertIsNone(entry.expires_at)
        data = entry.to_dict()
        self.assertIsNone(data["expires_at"])


class TestContextLayerManager(unittest.TestCase):
    """Test ContextLayerManager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.layer_manager = ContextLayerManager()
        self.test_key = "test_key"
        self.test_value = "test_value"
    
    def test_set_context_basic(self):
        """Test basic context setting."""
        entry_id = self.layer_manager.set_context(
            self.test_key, self.test_value, ContextLayer.SESSION
        )
        
        self.assertIsInstance(entry_id, str)
        self.assertEqual(len(entry_id), 36)  # UUID length
        
        # Verify context was set
        value = self.layer_manager.get_context(self.test_key)
        self.assertEqual(value, self.test_value)
    
    def test_set_context_with_metadata(self):
        """Test context setting with metadata."""
        metadata = {"source": "test", "priority": "high"}
        entry_id = self.layer_manager.set_context(
            self.test_key, self.test_value, ContextLayer.SESSION,
            metadata=metadata
        )
        
        entry = self.layer_manager.get_context_entry(self.test_key)
        self.assertEqual(entry.metadata, metadata)
    
    def test_set_context_with_ttl(self):
        """Test context setting with TTL."""
        entry_id = self.layer_manager.set_context(
            self.test_key, self.test_value, ContextLayer.SESSION,
            ttl_seconds=1
        )
        
        entry = self.layer_manager.get_context_entry(self.test_key)
        self.assertIsNotNone(entry.expires_at)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should not be found when expired
        value = self.layer_manager.get_context(self.test_key)
        self.assertIsNone(value)
    
    def test_layer_priority_resolution(self):
        """Test layer priority resolution (highest priority wins)."""
        # Set in multiple layers
        self.layer_manager.set_context(self.test_key, "global_value", ContextLayer.GLOBAL)
        self.layer_manager.set_context(self.test_key, "session_value", ContextLayer.SESSION)
        
        # Should get session value (highest priority)
        value = self.layer_manager.get_context(self.test_key)
        self.assertEqual(value, "session_value")
    
    def test_get_context_specific_layer(self):
        """Test getting context from specific layer."""
        self.layer_manager.set_context(self.test_key, "global_value", ContextLayer.GLOBAL)
        self.layer_manager.set_context(self.test_key, "session_value", ContextLayer.SESSION)
        
        # Get from specific layer
        value = self.layer_manager.get_context(self.test_key, layer=ContextLayer.GLOBAL)
        self.assertEqual(value, "global_value")
    
    def test_update_context(self):
        """Test context updating."""
        entry_id = self.layer_manager.set_context(
            self.test_key, self.test_value, ContextLayer.SESSION
        )
        
        # Update the context
        success = self.layer_manager.update_context(
            self.test_key, "updated_value", ContextLayer.SESSION
        )
        
        self.assertTrue(success)
        value = self.layer_manager.get_context(self.test_key)
        self.assertEqual(value, "updated_value")
        
        # Check version increment
        entry = self.layer_manager.get_context_entry(self.test_key)
        self.assertEqual(entry.version, 2)
    
    def test_update_context_not_found(self):
        """Test updating non-existent context."""
        success = self.layer_manager.update_context(
            "non_existent", "value", ContextLayer.SESSION
        )
        
        self.assertFalse(success)
    
    def test_delete_context(self):
        """Test context deletion."""
        self.layer_manager.set_context(self.test_key, self.test_value, ContextLayer.SESSION)
        
        # Delete the context
        success = self.layer_manager.delete_context(self.test_key)
        
        self.assertTrue(success)
        value = self.layer_manager.get_context(self.test_key)
        self.assertIsNone(value)
    
    def test_delete_context_specific_layer(self):
        """Test deleting context from specific layer."""
        self.layer_manager.set_context(self.test_key, "global_value", ContextLayer.GLOBAL)
        self.layer_manager.set_context(self.test_key, "session_value", ContextLayer.SESSION)
        
        # Delete from session layer only
        success = self.layer_manager.delete_context(self.test_key, layer=ContextLayer.SESSION)
        
        self.assertTrue(success)
        # Should still get global value
        value = self.layer_manager.get_context(self.test_key)
        self.assertEqual(value, "global_value")
    
    def test_clear_layer(self):
        """Test clearing entire layer."""
        self.layer_manager.set_context("key1", "value1", ContextLayer.SESSION)
        self.layer_manager.set_context("key2", "value2", ContextLayer.SESSION)
        self.layer_manager.set_context("key3", "value3", ContextLayer.GLOBAL)
        
        # Clear session layer
        count = self.layer_manager.clear_layer(ContextLayer.SESSION)
        
        self.assertEqual(count, 2)
        self.assertIsNone(self.layer_manager.get_context("key1"))
        self.assertIsNone(self.layer_manager.get_context("key2"))
        # Global should still exist
        self.assertEqual(self.layer_manager.get_context("key3"), "value3")
    
    def test_get_layer_contexts(self):
        """Test getting all contexts from a layer."""
        self.layer_manager.set_context("key1", "value1", ContextLayer.SESSION, ContextType.STATE)
        self.layer_manager.set_context("key2", "value2", ContextLayer.SESSION, ContextType.CONFIGURATION)
        self.layer_manager.set_context("key3", "value3", ContextLayer.GLOBAL)
        
        # Get all session contexts
        contexts = self.layer_manager.get_layer_contexts(ContextLayer.SESSION)
        
        self.assertEqual(len(contexts), 2)
        self.assertEqual(contexts["key1"], "value1")
        self.assertEqual(contexts["key2"], "value2")
    
    def test_get_layer_contexts_filtered(self):
        """Test getting layer contexts filtered by type."""
        self.layer_manager.set_context("key1", "value1", ContextLayer.SESSION, ContextType.STATE)
        self.layer_manager.set_context("key2", "value2", ContextLayer.SESSION, ContextType.CONFIGURATION)
        
        # Get only state contexts
        contexts = self.layer_manager.get_layer_contexts(
            ContextLayer.SESSION, context_type=ContextType.STATE
        )
        
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts["key1"], "value1")
    
    def test_subscribe_and_notify(self):
        """Test event subscription and notification."""
        events_received = []
        
        def callback(entry):
            events_received.append(entry)
        
        self.layer_manager.subscribe("context_set", callback)
        
        # Set context to trigger event
        self.layer_manager.set_context(self.test_key, self.test_value, ContextLayer.SESSION)
        
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].key, self.test_key)
        self.assertEqual(events_received[0].value, self.test_value)
    
    def test_unsubscribe(self):
        """Test event unsubscription."""
        events_received = []
        
        def callback(entry):
            events_received.append(entry)
        
        self.layer_manager.subscribe("context_set", callback)
        self.layer_manager.unsubscribe("context_set", callback)
        
        # Set context - should not trigger event
        self.layer_manager.set_context(self.test_key, self.test_value, ContextLayer.SESSION)
        
        self.assertEqual(len(events_received), 0)
    
    def test_analytics_update_operation(self):
        """Test analytics for update operation specifically."""
        # Set up context
        self.layer_manager.set_context("update_key", "original_value", ContextLayer.SESSION, ContextType.STATE)
        
        # Update context
        success = self.layer_manager.update_context("update_key", "updated_value")
        self.assertTrue(success)
        
        analytics = self.layer_manager.get_context_analytics()
        ops = analytics["operations"]
        
        # Check that update operation was recorded
        self.assertIn("update_SESSION_state", ops)
        self.assertEqual(ops["update_SESSION_state"], 1)

    def test_analytics_combined_operations(self):
        """Test analytics for combined operations."""
        # Set up contexts
        self.layer_manager.set_context("key1", "value1", ContextLayer.SESSION, ContextType.STATE)
        self.layer_manager.set_context("key2", "value2", ContextLayer.GLOBAL, ContextType.CONFIGURATION)
        
        # Get context
        value = self.layer_manager.get_context("key1")
        self.assertEqual(value, "value1")
        
        # Update context
        success = self.layer_manager.update_context("key1", "updated_value")
        self.assertTrue(success)
        
        # Delete context
        success = self.layer_manager.delete_context("key2")
        self.assertTrue(success)
        
        # Get analytics
        analytics = self.layer_manager.get_context_analytics()
        ops = analytics["operations"]
        
        # Verify all operations were recorded
        self.assertGreater(ops.get("set_SESSION_state", 0), 0)
        self.assertGreater(ops.get("set_GLOBAL_configuration", 0), 0)
        self.assertGreater(ops.get("get_SESSION_state", 0), 0)
        self.assertGreater(ops.get("update_SESSION_state", 0), 0)
        self.assertGreater(ops.get("delete_GLOBAL_configuration", 0), 0)

    def test_analytics_delete_operation(self):
        """Test analytics for delete operation specifically."""
        # Set up context
        self.layer_manager.set_context("delete_key", "delete_value", ContextLayer.GLOBAL, ContextType.CONFIGURATION)
        
        # Delete context
        success = self.layer_manager.delete_context("delete_key")
        self.assertTrue(success)
        
        analytics = self.layer_manager.get_context_analytics()
        ops = analytics["operations"]
        
        # Check that delete operation was recorded
        self.assertIn("delete_GLOBAL_configuration", ops)
        self.assertEqual(ops["delete_GLOBAL_configuration"], 1)

    def test_analytics_basic(self):
        """Test basic analytics functionality."""
        # Single operation
        self.layer_manager.set_context("test_key", "test_value", ContextLayer.SESSION, ContextType.STATE)
        
        analytics = self.layer_manager.get_context_analytics()
        
        self.assertIn("operations", analytics)
        self.assertIn("layers", analytics)
        
        # Check that we have at least one operation
        ops = analytics["operations"]
        self.assertGreater(len(ops), 0)
        
        # Check that the operation was recorded
        self.assertIn("set_SESSION_state", ops)
        self.assertEqual(ops["set_SESSION_state"], 1)

    def test_analytics_tracking(self):
        """Test analytics tracking."""
        # Perform various operations
        self.layer_manager.set_context("key1", "value1", ContextLayer.SESSION, ContextType.STATE)
        self.layer_manager.set_context("key2", "value2", ContextLayer.GLOBAL, ContextType.CONFIGURATION)
        self.layer_manager.get_context("key1")
        self.layer_manager.update_context("key1", "updated_value")
        self.layer_manager.delete_context("key2")
        
        analytics = self.layer_manager.get_context_analytics()
        
        self.assertIn("operations", analytics)
        self.assertIn("layers", analytics)
        
        # Check operation counts
        ops = analytics["operations"]
        self.assertGreater(ops.get("set_SESSION_state", 0), 0)
        self.assertGreater(ops.get("set_GLOBAL_configuration", 0), 0)
        self.assertGreater(ops.get("get_SESSION_state", 0), 0)
        self.assertGreater(ops.get("update_SESSION_state", 0), 0)
        self.assertGreater(ops.get("delete_GLOBAL_configuration", 0), 0)


class TestEnhancedContextManager(unittest.TestCase):
    """Test EnhancedContextManager functionality."""
    
    def setUp(self):
        """Set up test environment with temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_storage_path = CONTEXT_STORAGE_PATH
        
        # Patch the storage path
        self.storage_patcher = patch(
            'bmad.agents.core.communication.enhanced_context_manager.CONTEXT_STORAGE_PATH',
            Path(self.temp_dir)
        )
        self.storage_patcher.start()
        
        # Create storage directory
        Path(self.temp_dir).mkdir(exist_ok=True)
        
        # Disable cleanup thread for tests
        self.context_manager = EnhancedContextManager(disable_cleanup=True)
    
    def tearDown(self):
        """Clean up test environment."""
        self.storage_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_set_context_with_persistence(self):
        """Test context setting with persistence."""
        entry_id = self.context_manager.set_context(
            "test_key", "test_value", ContextLayer.SESSION
        )
        
        # Verify context was set
        value = self.context_manager.get_context("test_key")
        self.assertEqual(value, "test_value")
        
        # Verify persistence file was created
        persistence_file = Path(self.temp_dir) / f"{entry_id}.json"
        self.assertTrue(persistence_file.exists())
    
    def test_set_context_without_persistence(self):
        """Test context setting without persistence."""
        entry_id = self.context_manager.set_context(
            "test_key", "test_value", ContextLayer.SESSION, persist=False
        )
        
        # Verify context was set
        value = self.context_manager.get_context("test_key")
        self.assertEqual(value, "test_value")
        
        # Verify no persistence file was created
        persistence_file = Path(self.temp_dir) / f"{entry_id}.json"
        self.assertFalse(persistence_file.exists())
    
    def test_update_context_with_persistence(self):
        """Test context updating with persistence."""
        entry_id = self.context_manager.set_context(
            "test_key", "test_value", ContextLayer.SESSION
        )
        
        # Update context
        success = self.context_manager.update_context(
            "test_key", "updated_value", persist=True
        )
        
        self.assertTrue(success)
        
        # Verify persistence file was updated
        persistence_file = Path(self.temp_dir) / f"{entry_id}.json"
        self.assertTrue(persistence_file.exists())
        
        with open(persistence_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["value"], "updated_value")
    
    def test_delete_context_with_persistence(self):
        """Test context deletion with persistence."""
        entry_id = self.context_manager.set_context(
            "test_key", "test_value", ContextLayer.SESSION
        )
        
        # Verify persistence file exists
        persistence_file = Path(self.temp_dir) / f"{entry_id}.json"
        self.assertTrue(persistence_file.exists())
        
        # Delete context
        success = self.context_manager.delete_context("test_key", persist=True)
        
        self.assertTrue(success)
        
        # Verify persistence file was removed
        self.assertFalse(persistence_file.exists())
    
    def test_load_persisted_contexts(self):
        """Test loading persisted contexts."""
        # Create a persisted context file
        entry = ContextEntry(
            id="test-id",
            layer=ContextLayer.SESSION,
            context_type=ContextType.STATE,
            key="persisted_key",
            value="persisted_value",
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        persistence_file = Path(self.temp_dir) / "test-id.json"
        with open(persistence_file, 'w') as f:
            json.dump(entry.to_dict(), f)
        
        # Create new manager (should load persisted contexts)
        new_manager = EnhancedContextManager(disable_cleanup=True)
        
        # Verify context was loaded
        value = new_manager.get_context("persisted_key")
        self.assertEqual(value, "persisted_value")
    
    def test_load_expired_persisted_contexts(self):
        """Test loading expired persisted contexts."""
        # Create an expired persisted context file
        entry = ContextEntry(
            id="test-id",
            layer=ContextLayer.SESSION,
            context_type=ContextType.STATE,
            key="expired_key",
            value="expired_value",
            metadata={},
            created_at=datetime.now() - timedelta(hours=2),
            updated_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1)
        )
        
        persistence_file = Path(self.temp_dir) / "test-id.json"
        with open(persistence_file, 'w') as f:
            json.dump(entry.to_dict(), f)
        
        # Create new manager (should not load expired contexts)
        new_manager = EnhancedContextManager(disable_cleanup=True)
        
        # Verify context was not loaded
        value = new_manager.get_context("expired_key")
        self.assertIsNone(value)
        
        # Verify persistence file was removed
        self.assertFalse(persistence_file.exists())
    
    def test_get_analytics(self):
        """Test getting comprehensive analytics."""
        # Perform some operations
        self.context_manager.set_context("key1", "value1", ContextLayer.SESSION)
        self.context_manager.get_context("key1")
        self.context_manager.update_context("key1", "updated_value")
        
        analytics = self.context_manager.get_analytics()
        
        self.assertIn("operations", analytics)
        self.assertIn("layers", analytics)
        self.assertIn("manager_info", analytics)
        
        manager_info = analytics["manager_info"]
        self.assertTrue(manager_info["persistence_enabled"])
        self.assertFalse(manager_info["auto_cleanup_enabled"])  # Disabled in tests
        self.assertEqual(manager_info["cleanup_interval"], 300)
    
    def test_subscribe_and_unsubscribe(self):
        """Test event subscription and unsubscription."""
        events_received = []
        
        def callback(entry):
            events_received.append(entry)
        
        self.context_manager.subscribe("context_set", callback)
        
        # Set context to trigger event
        self.context_manager.set_context("test_key", "test_value", ContextLayer.SESSION)
        
        self.assertEqual(len(events_received), 1)
        
        # Unsubscribe
        self.context_manager.unsubscribe("context_set", callback)
        
        # Set another context - should not trigger event
        self.context_manager.set_context("test_key2", "test_value2", ContextLayer.SESSION)
        
        self.assertEqual(len(events_received), 1)  # Still only 1 event


class TestEnhancedContextManagerIntegration(unittest.TestCase):
    """Integration tests for EnhancedContextManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_storage_path = CONTEXT_STORAGE_PATH
        
        # Patch the storage path
        self.storage_patcher = patch(
            'bmad.agents.core.communication.enhanced_context_manager.CONTEXT_STORAGE_PATH',
            Path(self.temp_dir)
        )
        self.storage_patcher.start()
        
        Path(self.temp_dir).mkdir(exist_ok=True)
        # Disable cleanup thread for tests
        self.context_manager = EnhancedContextManager(disable_cleanup=True)
    
    def tearDown(self):
        """Clean up test environment."""
        self.storage_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complex_workflow_scenario(self):
        """Test complex workflow scenario with multiple layers and types."""
        # Simulate a complex workflow
        workflow_id = "workflow-123"
        
        # Set global configuration
        self.context_manager.set_context(
            "api_timeout", 30, ContextLayer.GLOBAL, ContextType.CONFIGURATION
        )
        
        # Set user preferences
        self.context_manager.set_context(
            "theme", "dark", ContextLayer.USER, ContextType.PREFERENCES
        )
        
        # Set workflow state
        self.context_manager.set_context(
            "current_step", "validation", ContextLayer.WORKFLOW, ContextType.WORKFLOW,
            metadata={"workflow_id": workflow_id}
        )
        
        # Set session data
        self.context_manager.set_context(
            "user_token", "abc123", ContextLayer.SESSION, ContextType.STATE,
            ttl_seconds=3600
        )
        
        # Verify layer priority resolution
        self.context_manager.set_context(
            "api_timeout", 60, ContextLayer.SESSION, ContextType.CONFIGURATION
        )
        
        # Should get session value (highest priority)
        timeout = self.context_manager.get_context("api_timeout")
        self.assertEqual(timeout, 60)
        
        # Get from specific layer
        global_timeout = self.context_manager.get_context("api_timeout", layer=ContextLayer.GLOBAL)
        self.assertEqual(global_timeout, 30)
        
        # Get workflow contexts
        workflow_contexts = self.context_manager.get_layer_contexts(
            ContextLayer.WORKFLOW, context_type=ContextType.WORKFLOW
        )
        self.assertEqual(workflow_contexts["current_step"], "validation")
        
        # Update workflow state
        self.context_manager.update_context(
            "current_step", "completed", ContextLayer.WORKFLOW,
            metadata={"workflow_id": workflow_id, "status": "success"}
        )
        
        # Verify update
        step = self.context_manager.get_context("current_step")
        self.assertEqual(step, "completed")
        
        # Get analytics
        analytics = self.context_manager.get_analytics()
        self.assertIn("operations", analytics)
        self.assertIn("layers", analytics)
    
    def test_concurrent_access(self):
        """Test concurrent access to context manager."""
        import threading
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Set context
                self.context_manager.set_context(
                    f"key_{worker_id}", f"value_{worker_id}", ContextLayer.SESSION
                )
                
                # Get context
                value = self.context_manager.get_context(f"key_{worker_id}")
                results.append((worker_id, value))
                
                # Update context
                self.context_manager.update_context(
                    f"key_{worker_id}", f"updated_value_{worker_id}"
                )
                
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        
        # Verify all results are correct
        self.assertEqual(len(results), 10)
        for worker_id, value in results:
            self.assertEqual(value, f"value_{worker_id}")
        
        # Verify all contexts were set and updated
        for i in range(10):
            value = self.context_manager.get_context(f"key_{i}")
            self.assertEqual(value, f"updated_value_{i}")


if __name__ == "__main__":
    unittest.main() 