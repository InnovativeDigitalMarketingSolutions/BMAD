import pytest
import uuid
from bmad.agents.core.supabase_context import save_context, get_context

def test_save_and_get_context():
    agent_name = f"TestAgent_{uuid.uuid4()}"
    context_type = "test"
    test_data = {"foo": "bar", "number": 42}
    # Sla context op
    save_context(agent_name, context_type, test_data)
    # Haal context op
    result = get_context(agent_name, context_type)
    assert result, "Context ophalen faalde."
    # Supabase geeft een lijst van dicts terug
    assert result[0]["payload"]["foo"] == "bar"
    assert result[0]["payload"]["number"] == 42 