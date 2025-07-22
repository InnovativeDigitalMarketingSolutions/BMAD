import json
import threading
from pathlib import Path
from datetime import datetime

SHARED_CONTEXT_PATH = Path(__file__).parent.parent / "shared_context.json"
LOCK = threading.Lock()


def publish(event, data):
    """Publiceer een event met data naar de shared context."""
    with LOCK:
        if SHARED_CONTEXT_PATH.exists():
            with open(SHARED_CONTEXT_PATH, "r") as f:
                context = json.load(f)
        else:
            context = {"events": []}
        context["events"].append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        })
        with open(SHARED_CONTEXT_PATH, "w") as f:
            json.dump(context, f, indent=2)


def get_events(event_type=None, since=None):
    """Haal events op, optioneel gefilterd op type en tijd."""
    if not SHARED_CONTEXT_PATH.exists():
        return []
    with open(SHARED_CONTEXT_PATH, "r") as f:
        context = json.load(f)
    events = context.get("events", [])
    if event_type:
        events = [e for e in events if e["event"] == event_type]
    if since:
        events = [e for e in events if e["timestamp"] > since]
    return events


def clear_events():
    """Wis alle events (voor test/reset doeleinden)."""
    with LOCK:
        with open(SHARED_CONTEXT_PATH, "w") as f:
            json.dump({"events": []}, f, indent=2)
