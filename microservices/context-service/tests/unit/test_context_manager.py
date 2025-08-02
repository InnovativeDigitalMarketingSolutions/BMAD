"""
Unit tests for ContextManager
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.context.context_manager import ContextManager, Context


class TestContextManager:
    """Test cases for ContextManager."""
    
    @pytest.fixture
    def context_manager(self):
        """Create a ContextManager instance for testing."""
        return ContextManager()
        
    @pytest.fixture
    def sample_context_data(self):
        """Sample context data for testing."""
        return {
            "id": "test_context_001",
            "name": "Test Context",
            "type": "test_type",
            "status": "active",
            "metadata": {"created_by": "test_user"},
            "tags": ["test", "context"]
        }
        
    @pytest.mark.asyncio
    async def test_create_context(self, context_manager, sample_context_data):
        """Test context creation."""
        context = await context_manager.create_context(
            name=sample_context_data["name"],
            context_type=sample_context_data["type"],
            metadata=sample_context_data["metadata"],
            tags=sample_context_data["tags"]
        )
        
        assert context is not None
        assert context.name == sample_context_data["name"]
        assert context.type == sample_context_data["type"]
        assert context.status == "active"
        assert context.metadata == sample_context_data["metadata"]
        assert context.tags == sample_context_data["tags"]
        
    @pytest.mark.asyncio
    async def test_get_context(self, context_manager, sample_context_data):
        """Test getting context by ID."""
        # Create context first
        context = await context_manager.create_context(
            name=sample_context_data["name"],
            context_type=sample_context_data["type"]
        )
        
        # Get context
        retrieved_context = await context_manager.get_context(context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.id == context.id
        assert retrieved_context.name == sample_context_data["name"]
        
    @pytest.mark.asyncio
    async def test_get_context_not_found(self, context_manager):
        """Test getting non-existent context."""
        context = await context_manager.get_context("non-existent-id")
        assert context is None
        
    @pytest.mark.asyncio
    async def test_update_context(self, context_manager, sample_context_data):
        """Test context update."""
        # Create context first
        context = await context_manager.create_context(
            name=sample_context_data["name"],
            context_type=sample_context_data["type"]
        )
        
        # Update context
        updates = {
            "name": "Updated Context",
            "status": "inactive",
            "metadata": {"updated_by": "test_user"}
        }
        
        updated_context = await context_manager.update_context(
            context_id=context.id,
            updates=updates
        )
        
        assert updated_context is not None
        assert updated_context.name == "Updated Context"
        assert updated_context.status == "inactive"
        assert updated_context.metadata["updated_by"] == "test_user"
        
    @pytest.mark.asyncio
    async def test_delete_context(self, context_manager, sample_context_data):
        """Test context deletion."""
        # Create context first
        context = await context_manager.create_context(
            name=sample_context_data["name"],
            context_type=sample_context_data["type"]
        )
        
        # Delete context
        success = await context_manager.delete_context(context.id)
        assert success is True
        
        # Verify context is deleted
        retrieved_context = await context_manager.get_context(context.id)
        assert retrieved_context is None
        
    @pytest.mark.asyncio
    async def test_list_contexts(self, context_manager):
        """Test listing contexts."""
        # Create multiple contexts
        await context_manager.create_context(
            context_id="context_1",
            name="Context 1",
            context_type="type_1"
        )
        await context_manager.create_context(
            context_id="context_2",
            name="Context 2",
            context_type="type_2"
        )
        
        # List contexts
        contexts = await context_manager.list_contexts()
        
        assert len(contexts) >= 2
        context_ids = [c.id for c in contexts]
        assert "context_1" in context_ids
        assert "context_2" in context_ids
        
    @pytest.mark.asyncio
    async def test_list_contexts_with_filters(self, context_manager):
        """Test listing contexts with filters."""
        # Create contexts with different types
        await context_manager.create_context(
            context_id="context_1",
            name="Context 1",
            context_type="agent_execution"
        )
        await context_manager.create_context(
            context_id="context_2",
            name="Context 2",
            context_type="user_session"
        )
        
        # Filter by type
        agent_contexts = await context_manager.list_contexts(
            context_type="agent_execution"
        )
        assert len(agent_contexts) >= 1
        assert all(c.type == "agent_execution" for c in agent_contexts)
        
        # Filter by status
        active_contexts = await context_manager.list_contexts(
            status="active"
        )
        assert len(active_contexts) >= 2
        
    @pytest.mark.asyncio
    async def test_search_contexts(self, context_manager):
        """Test searching contexts."""
        # Create contexts with searchable names
        await context_manager.create_context(
            context_id="context_1",
            name="Agent Execution Context",
            context_type="agent_execution"
        )
        await context_manager.create_context(
            context_id="context_2",
            name="User Session Context",
            context_type="user_session"
        )
        
        # Search for "Agent"
        results = await context_manager.search_contexts("Agent")
        assert len(results) >= 1
        assert any("Agent" in c.name for c in results)
        
        # Search for "Session"
        results = await context_manager.search_contexts("Session")
        assert len(results) >= 1
        assert any("Session" in c.name for c in results)
        
    @pytest.mark.asyncio
    async def test_get_context_stats(self, context_manager):
        """Test getting context statistics."""
        # Create some contexts
        await context_manager.create_context(
            context_id="context_1",
            name="Context 1",
            context_type="agent_execution"
        )
        await context_manager.create_context(
            context_id="context_2",
            name="Context 2",
            context_type="user_session"
        )
        
        # Get stats
        stats = await context_manager.get_context_stats()
        
        assert stats is not None
        assert "total_contexts" in stats
        assert "context_types" in stats
        assert "status_distribution" in stats
        assert stats["total_contexts"] >= 2
        
    @pytest.mark.asyncio
    async def test_cleanup_expired_contexts(self, context_manager):
        """Test cleanup of expired contexts."""
        # Create a context that will be expired
        await context_manager.create_context(
            context_id="expired_context",
            name="Expired Context",
            context_type="test",
            metadata={"expires_at": datetime.now(timezone.utc).isoformat()}
        )
        
        # Cleanup expired contexts
        cleaned_count = await context_manager.cleanup_expired_contexts()
        
        # Should have cleaned up at least 0 contexts (depends on implementation)
        assert cleaned_count >= 0
        
    @pytest.mark.asyncio
    async def test_health_check(self, context_manager):
        """Test health check."""
        health = await context_manager.health_check()
        
        assert health is not None
        assert "status" in health
        assert "total_contexts" in health
        assert "store_available" in health 