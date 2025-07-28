import os
import json
from typing import Any, Dict, Optional
from supabase import create_client, Client
from datetime import datetime, timedelta

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://sjdupcpozyaipljqpyrc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CONTEXT_TABLE = "bm_ad_context"
ARCHIVE_TABLE = "bm_ad_context_archive"

# --- Context scoping ---
def save_context(agent_name: str, context_type: str, payload: Dict[str, Any], updated_by: Optional[str] = None, scope: Optional[str] = None) -> None:
    """
    Sla context op voor een agent in Supabase, optioneel met scope (project/workflow/klant).
    """
    if not agent_name or not context_type or not isinstance(payload, dict):
        raise ValueError("agent_name, context_type en payload (dict) zijn verplicht")
    # Basisvalidatie: payload moet JSON serialiseerbaar zijn
    try:
        json.dumps(payload)
    except Exception:
        raise ValueError("Payload is niet JSON serialiseerbaar")
    data = {
        "agent_name": agent_name,
        "context_type": context_type,
        "payload": payload,
        "updated_by": updated_by,
        "updated_at": datetime.now().isoformat(),
    }
    if scope is not None:
        data["scope"] = scope
        on_conflict = "agent_name,context_type,scope"
    else:
        on_conflict = "agent_name,context_type"
    supabase.table(CONTEXT_TABLE).upsert(data, on_conflict=on_conflict).execute()


def get_context(agent_name: str, context_type: Optional[str] = None, scope: Optional[str] = None) -> Any:
    """
    Haal context op voor een specifieke agent (en optioneel context_type/scope).
    """
    if not agent_name:
        raise ValueError("agent_name is verplicht")
    query = supabase.table(CONTEXT_TABLE).select("*").eq("agent_name", agent_name)
    if context_type:
        query = query.eq("context_type", context_type)
    if scope:
        query = query.eq("scope", scope)
    result = query.execute()
    return result.data

# --- Automatische archivering van oude context ---
def archive_old_context(days: int = 90):
    """
    Archiveer context records ouder dan X dagen naar ARCHIVE_TABLE.
    """
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    old_context = supabase.table(CONTEXT_TABLE).select("*").lt("updated_at", cutoff).execute().data
    if old_context:
        for record in old_context:
            supabase.table(ARCHIVE_TABLE).insert(record).execute()
            supabase.table(CONTEXT_TABLE).delete().eq("agent_name", record["agent_name"]).eq("context_type", record["context_type"]).eq("scope", record.get("scope")).execute() 