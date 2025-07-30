import uuid
from unittest.mock import patch, MagicMock
from bmad.agents.core.data.supabase_context import save_context, get_context

def test_save_and_get_context():
    agent_name = f"TestAgent_{uuid.uuid4()}"
    context_type = "test"
    test_data = {"foo": "bar", "number": 42}
    
    # Mock only the Supabase client to prevent real API calls
    with patch('bmad.agents.core.data.supabase_context.supabase') as mock_supabase:
        # Mock the table operations
        mock_table = MagicMock()
        mock_upsert = MagicMock()
        mock_execute = MagicMock()
        mock_select = MagicMock()
        mock_eq = MagicMock()
        
        # Setup the mock chain for save_context
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = mock_execute
        
        # Setup the mock chain for get_context
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.eq.return_value = mock_eq
        mock_eq.execute.return_value = MagicMock(data=[{
            "agent_name": agent_name,
            "context_type": context_type,
            "payload": test_data,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }])
        
        mock_supabase.table.return_value = mock_table
        
        # Sla context op
        save_context(agent_name, context_type, test_data)
        # Haal context op
        result = get_context(agent_name, context_type)
        assert result, "Context ophalen faalde."
        # Supabase geeft een lijst van dicts terug
        assert result[0]["payload"]["foo"] == "bar"
        assert result[0]["payload"]["number"] == 42 