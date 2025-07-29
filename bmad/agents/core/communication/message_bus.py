import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List

SHARED_CONTEXT_PATH = Path(__file__).parent.parent / "shared_context.json"
LOCK = threading.Lock()

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

_subscribers: Dict[str, List[Callable]] = {}

def publish(event, data):
    """Publiceer een event met data naar de shared context en roep subscribers aan."""
    with LOCK:
        if SHARED_CONTEXT_PATH.exists():
            with open(SHARED_CONTEXT_PATH) as f:
                context = json.load(f)
        else:
            context = {"events": []}
        event_obj = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        context["events"].append(event_obj)
        with open(SHARED_CONTEXT_PATH, "w") as f:
            json.dump(context, f, indent=2)
    logging.info(f"[MessageBus] Event gepubliceerd: {event}")
    # Notify subscribers
    for callback in _subscribers.get(event, []):
        try:
            callback(event_obj)
        except Exception as e:
            logging.exception(f"[MessageBus] Fout in subscriber callback: {e}")

def subscribe(event_type: str, callback: Callable):
    """Abonneer een callback op een specifiek event_type."""
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(callback)
    logging.info(f"[MessageBus] Subscriber toegevoegd voor event: {event_type}")

def unsubscribe(event_type: str, callback: Callable):
    """Verwijder een callback van een specifiek event_type."""
    if event_type in _subscribers and callback in _subscribers[event_type]:
        _subscribers[event_type].remove(callback)
        logging.info(f"[MessageBus] Subscriber verwijderd voor event: {event_type}")

def get_events(event_type=None, since=None):
    """Haal events op, optioneel gefilterd op type en tijd."""
    if not SHARED_CONTEXT_PATH.exists():
        return []
    with open(SHARED_CONTEXT_PATH) as f:
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
    logging.info("[MessageBus] Alle events gewist.")
