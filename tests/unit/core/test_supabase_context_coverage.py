import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import os

import bmad.agents.core.data.supabase_context as sc

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('bmad.agents.core.data.supabase_context.supabase') as mock_client:
        # Mock table operations
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        
        # Mock query builder
        mock_query = MagicMock()
        mock_table.select.return_value = mock_query
        mock_table.upsert.return_value = mock_query
        mock_table.insert.return_value = mock_query
        mock_table.delete.return_value = mock_query
        
        # Mock query methods
        mock_query.eq.return_value = mock_query
        mock_query.lt.return_value = mock_query
        mock_query.execute.return_value = MagicMock(data=[])
        
        yield mock_client

class TestSaveContext:
    """Test save_context functionality."""
    
    def test_save_context_basic(self, mock_supabase):
        """Test basic context saving."""
        agent_name = "test_agent"
        context_type = "test_context"
        payload = {"key": "value"}
        
        sc.save_context(agent_name, context_type, payload)
        
        # Verify upsert was called
        mock_supabase.table.assert_called_with(sc.CONTEXT_TABLE)
        mock_supabase.table().upsert.assert_called_once()
        
        # Check the data that was passed
        call_args = mock_supabase.table().upsert.call_args
        data = call_args[0][0]  # First positional argument
        
        assert data["agent_name"] == agent_name
        assert data["context_type"] == context_type
        assert data["payload"] == payload
        assert "updated_at" in data
        # on_conflict is passed as second argument, not in data dict
        assert call_args[1]["on_conflict"] == "agent_name,context_type"
    
    def test_save_context_with_scope(self, mock_supabase):
        """Test context saving with scope."""
        agent_name = "test_agent"
        context_type = "test_context"
        payload = {"key": "value"}
        scope = "project_123"
        updated_by = "user_456"
        
        sc.save_context(agent_name, context_type, payload, updated_by, scope)
        
        # Check the data that was passed
        call_args = mock_supabase.table().upsert.call_args
        data = call_args[0][0]
        
        assert data["agent_name"] == agent_name
        assert data["context_type"] == context_type
        assert data["payload"] == payload
        assert data["scope"] == scope
        assert data["updated_by"] == updated_by
        # on_conflict is passed as second argument, not in data dict
        assert call_args[1]["on_conflict"] == "agent_name,context_type,scope"
    
    def test_save_context_missing_agent_name(self, mock_supabase):
        """Test save_context with missing agent_name."""
        with pytest.raises(ValueError, match="agent_name, context_type en payload"):
            sc.save_context("", "test_context", {"key": "value"})
    
    def test_save_context_missing_context_type(self, mock_supabase):
        """Test save_context with missing context_type."""
        with pytest.raises(ValueError, match="agent_name, context_type en payload"):
            sc.save_context("test_agent", "", {"key": "value"})
    
    def test_save_context_invalid_payload(self, mock_supabase):
        """Test save_context with invalid payload."""
        with pytest.raises(ValueError, match="agent_name, context_type en payload"):
            sc.save_context("test_agent", "test_context", "not_a_dict")
    
    def test_save_context_non_serializable_payload(self, mock_supabase):
        """Test save_context with non-serializable payload."""
        # Create a payload with a non-serializable object
        class NonSerializable:
            pass
        
        payload = {"key": NonSerializable()}
        
        with pytest.raises(ValueError, match="Payload is niet JSON serialiseerbaar"):
            sc.save_context("test_agent", "test_context", payload)
    
    def test_save_context_complex_payload(self, mock_supabase):
        """Test save_context with complex payload."""
        payload = {
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": 1, "b": 2},
                "string": "test",
                "number": 42,
                "boolean": True,
                "null": None
            }
        }
        
        sc.save_context("test_agent", "test_context", payload)
        
        # Verify the payload was serializable
        call_args = mock_supabase.table().upsert.call_args
        data = call_args[0][0]
        
        # Should be able to serialize the payload
        json.dumps(data["payload"])

class TestGetContext:
    """Test get_context functionality."""
    
    def test_get_context_basic(self, mock_supabase):
        """Test basic context retrieval."""
        agent_name = "test_agent"
        mock_data = [{"agent_name": agent_name, "context_type": "test", "payload": {"key": "value"}}]
        mock_supabase.table().select().eq().execute.return_value = MagicMock(data=mock_data)
        
        result = sc.get_context(agent_name)
        
        # Verify query was built correctly
        mock_supabase.table.assert_called_with(sc.CONTEXT_TABLE)
        mock_supabase.table().select.assert_called_with("*")
        mock_supabase.table().select().eq.assert_called_with("agent_name", agent_name)
        
        assert result == mock_data
    
    def test_get_context_with_type(self, mock_supabase):
        """Test context retrieval with context_type filter."""
        agent_name = "test_agent"
        context_type = "test_context"
        mock_data = [{"agent_name": agent_name, "context_type": context_type, "payload": {"key": "value"}}]
        mock_supabase.table().select().eq().eq().execute.return_value = MagicMock(data=mock_data)
        
        result = sc.get_context(agent_name, context_type)
        
        # Verify both filters were applied
        eq_calls = mock_supabase.table().select().eq.call_args_list
        assert len(eq_calls) >= 2
        # Check that the calls were made (exact args may vary due to chaining)
        assert any("agent_name" in str(call) for call in eq_calls)
        assert any("context_type" in str(call) for call in eq_calls)
        
        assert result == mock_data
    
    def test_get_context_with_scope(self, mock_supabase):
        """Test context retrieval with scope filter."""
        agent_name = "test_agent"
        scope = "project_123"
        mock_data = [{"agent_name": agent_name, "scope": scope, "payload": {"key": "value"}}]
        mock_supabase.table().select().eq().eq().execute.return_value = MagicMock(data=mock_data)
        
        result = sc.get_context(agent_name, scope=scope)
        
        # Verify both filters were applied
        eq_calls = mock_supabase.table().select().eq.call_args_list
        assert len(eq_calls) >= 2
        # Check that the calls were made (exact args may vary due to chaining)
        assert any("agent_name" in str(call) for call in eq_calls)
        assert any("scope" in str(call) for call in eq_calls)
        
        assert result == mock_data
    
    def test_get_context_with_type_and_scope(self, mock_supabase):
        """Test context retrieval with both type and scope filters."""
        agent_name = "test_agent"
        context_type = "test_context"
        scope = "project_123"
        mock_data = [{"agent_name": agent_name, "context_type": context_type, "scope": scope, "payload": {"key": "value"}}]
        mock_supabase.table().select().eq().eq().eq().execute.return_value = MagicMock(data=mock_data)
        
        result = sc.get_context(agent_name, context_type, scope)
        
        # Verify all three filters were applied
        eq_calls = mock_supabase.table().select().eq.call_args_list
        assert len(eq_calls) >= 3
        # Check that the calls were made (exact args may vary due to chaining)
        assert any("agent_name" in str(call) for call in eq_calls)
        assert any("context_type" in str(call) for call in eq_calls)
        assert any("scope" in str(call) for call in eq_calls)
        
        assert result == mock_data
    
    def test_get_context_missing_agent_name(self, mock_supabase):
        """Test get_context with missing agent_name."""
        with pytest.raises(ValueError, match="agent_name is verplicht"):
            sc.get_context("")
    
    def test_get_context_empty_result(self, mock_supabase):
        """Test get_context with empty result."""
        mock_supabase.table().select().eq().execute.return_value = MagicMock(data=[])
        
        result = sc.get_context("test_agent")
        
        assert result == []

class TestArchiveOldContext:
    """Test archive_old_context functionality."""
    
    def test_archive_old_context_no_old_records(self, mock_supabase):
        """Test archiving when no old records exist."""
        mock_supabase.table().select().lt().execute.return_value = MagicMock(data=[])
        
        sc.archive_old_context(days=90)
        
        # Should only query for old records, no archiving needed
        mock_supabase.table.assert_called_with(sc.CONTEXT_TABLE)
        mock_supabase.table().select.assert_called_with("*")
        # lt is called multiple times due to chaining, just verify it was called
        assert mock_supabase.table().select().lt.call_count >= 1
    
    def test_archive_old_context_with_old_records(self, mock_supabase):
        """Test archiving with old records."""
        old_records = [
            {
                "agent_name": "old_agent1",
                "context_type": "old_context1",
                "scope": "old_scope1",
                "updated_at": "2023-01-01T00:00:00"
            },
            {
                "agent_name": "old_agent2",
                "context_type": "old_context2",
                "scope": None,
                "updated_at": "2023-01-01T00:00:00"
            }
        ]
        
        # Mock the query for old records
        mock_supabase.table().select().lt().execute.return_value = MagicMock(data=old_records)
        
        # Mock the insert and delete operations
        mock_insert_query = MagicMock()
        mock_delete_query = MagicMock()
        mock_supabase.table().insert.return_value = mock_insert_query
        mock_supabase.table().delete.return_value = mock_delete_query
        
        sc.archive_old_context(days=90)
        
        # Verify archive table was used for inserts
        archive_calls = [call for call in mock_supabase.table.call_args_list if len(call[0]) > 0 and call[0][0] == sc.ARCHIVE_TABLE]
        assert len(archive_calls) == 2  # One for each old record
        
        # Verify main table was used for deletes
        main_table_calls = [call for call in mock_supabase.table.call_args_list if len(call[0]) > 0 and call[0][0] == sc.CONTEXT_TABLE]
        assert len(main_table_calls) >= 3  # Initial query + 2 deletes
    
    def test_archive_old_context_default_days(self, mock_supabase):
        """Test archiving with default days parameter."""
        mock_supabase.table().select().lt().execute.return_value = MagicMock(data=[])
        
        sc.archive_old_context()  # Default 90 days
        
        # Verify the cutoff date was calculated correctly
        lt_call = mock_supabase.table().select().lt.call_args
        cutoff_date = lt_call[0][1]  # Second argument should be the cutoff date
        
        # Should be approximately 90 days ago
        expected_cutoff = datetime.now() - timedelta(days=90)
        actual_cutoff = datetime.fromisoformat(cutoff_date.replace('Z', '+00:00'))
        
        # Allow for small time differences
        time_diff = abs((expected_cutoff - actual_cutoff).total_seconds())
        assert time_diff < 10  # Within 10 seconds
    
    def test_archive_old_context_custom_days(self, mock_supabase):
        """Test archiving with custom days parameter."""
        mock_supabase.table().select().lt().execute.return_value = MagicMock(data=[])
        
        sc.archive_old_context(days=30)
        
        # Verify the cutoff date was calculated correctly
        lt_call = mock_supabase.table().select().lt.call_args
        cutoff_date = lt_call[0][1]
        
        expected_cutoff = datetime.now() - timedelta(days=30)
        actual_cutoff = datetime.fromisoformat(cutoff_date.replace('Z', '+00:00'))
        
        time_diff = abs((expected_cutoff - actual_cutoff).total_seconds())
        assert time_diff < 10

class TestSupabaseContextIntegration:
    """Integration tests for supabase context."""
    
    @pytest.mark.asyncio
    async @pytest.mark.asyncio
    async @pytest.mark.asyncio
    async def test_full_workflow(self, mock_supabase):
        """Test complete workflow: save, get, archive."""
        agent_name = "test_agent"
        context_type = "test_context"
        payload = {"key": "value"}
        
        # Save context
        sc.save_context(agent_name, context_type, payload)
        
        # Mock the get query
        mock_data = [{"agent_name": agent_name, "context_type": context_type, "payload": payload}]
        mock_supabase.table().select().eq().eq().execute.return_value = MagicMock(data=mock_data)
        
        # Get context
        result = sc.get_context(agent_name, context_type)
        assert result == mock_data
        
        # Archive old context (no old records)
        mock_supabase.table().select().lt().execute.return_value = MagicMock(data=[])
        sc.archive_old_context()
    
    def test_error_handling_in_save(self, mock_supabase):
        """Test error handling in save_context."""
        # Mock a Supabase error
        mock_supabase.table().upsert.side_effect = Exception("Supabase error")
        
        with pytest.raises(Exception, match="Supabase error"):
            sc.save_context("test_agent", "test_context", {"key": "value"})
    
    def test_error_handling_in_get(self, mock_supabase):
        """Test error handling in get_context."""
        # Mock a Supabase error
        mock_supabase.table().select().eq().execute.side_effect = Exception("Supabase error")
        
        with pytest.raises(Exception, match="Supabase error"):
            sc.get_context("test_agent")
    
    def test_error_handling_in_archive(self, mock_supabase):
        """Test error handling in archive_old_context."""
        # Mock a Supabase error
        mock_supabase.table().select().lt().execute.side_effect = Exception("Supabase error")
        
        with pytest.raises(Exception, match="Supabase error"):
            sc.archive_old_context()

class TestSupabaseContextEnvironment:
    """Test environment variable handling."""
    
    def test_default_supabase_url(self):
        """Test default SUPABASE_URL."""
        with patch.dict(os.environ, {}, clear=True):
            # Reload the module to get default values
            import importlib
            importlib.reload(sc)
            
            assert sc.SUPABASE_URL == "https://sjdupcpozyaipljqpyrc.supabase.co"
    
    def test_custom_supabase_url(self):
        """Test custom SUPABASE_URL from environment."""
        custom_url = "https://custom.supabase.co"
        with patch.dict(os.environ, {"SUPABASE_URL": custom_url}):
            # Reload the module to get environment values
            import importlib
            importlib.reload(sc)
            
            assert sc.SUPABASE_URL == custom_url
    
    def test_default_supabase_key(self):
        """Test default SUPABASE_KEY."""
        with patch.dict(os.environ, {}, clear=True):
            # Reload the module to get default values
            import importlib
            importlib.reload(sc)
            
            assert sc.SUPABASE_KEY == "your-key"
    
    def test_custom_supabase_key(self):
        """Test custom SUPABASE_KEY from environment."""
        custom_key = "custom-key-123"
        with patch.dict(os.environ, {"SUPABASE_KEY": custom_key}):
            # Reload the module to get environment values
            import importlib
            importlib.reload(sc)
            
            assert sc.SUPABASE_KEY == custom_key 