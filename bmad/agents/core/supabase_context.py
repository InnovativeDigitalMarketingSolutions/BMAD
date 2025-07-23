import os
from typing import Any, Dict, Optional
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://sjdupcpozyaipljqpyrc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqZHVwY3BvenlhaXBsanFweXJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjE1MDY3MywiZXhwIjoyMDY3NzI2NjczfQ.2CPCBCpbvYuiJo7pLO_WrrHx5dauq2Kg37beArDWBxM")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CONTEXT_TABLE = "bm_ad_context"

def save_context(agent_name: str, context_type: str, payload: Dict[str, Any], updated_by: Optional[str] = None) -> None:
    """
    Sla context op voor een agent in Supabase.
    :param agent_name: Naam van de agent (str)
    :param context_type: Type context (str)
    :param payload: Contextdata (dict, wordt opgeslagen als jsonb)
    :param updated_by: Wie de update uitvoert (optioneel)
    """
    if not agent_name or not context_type or not isinstance(payload, dict):
        raise ValueError("agent_name, context_type en payload (dict) zijn verplicht")
    data = {
        "agent_name": agent_name,
        "context_type": context_type,
        "payload": payload,
        "updated_by": updated_by,
    }
    # Gebruik on_conflict als string
    supabase.table(CONTEXT_TABLE).upsert(data, on_conflict="agent_name,context_type").execute()

def get_context(agent_name: str, context_type: Optional[str] = None) -> Any:
    """
    Haal context op voor een specifieke agent (en optioneel context_type).
    :param agent_name: Naam van de agent (str)
    :param context_type: Type context (optioneel)
    :return: Lijst van context records
    """
    if not agent_name:
        raise ValueError("agent_name is verplicht")
    query = supabase.table(CONTEXT_TABLE).select("*").eq("agent_name", agent_name)
    if context_type:
        query = query.eq("context_type", context_type)
    result = query.execute()
    return result.data 