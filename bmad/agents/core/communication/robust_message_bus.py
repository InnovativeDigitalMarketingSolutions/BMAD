#!/usr/bin/env python3
"""
Robust Message Bus Implementation
Addresses root cause of JSON corruption with atomic operations and validation
"""

import json
import logging
import threading
import tempfile
import shutil
import os
import fcntl
import contextlib
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

SHARED_CONTEXT_PATH = Path(__file__).parent.parent / "shared_context.json"
LOCK = threading.Lock()

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

_subscribers: Dict[str, List[Callable]] = {}

@contextlib.contextmanager
def file_lock(filepath: Path):
    """Enhanced file locking with proper cleanup."""
    lock_file = Path(f"{filepath}.lock")
    with open(lock_file, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            if lock_file.exists():
                lock_file.unlink()

def safe_write_json(data: dict, filepath: Path) -> bool:
    """Safely write JSON data with atomic operation and validation."""
    # Create backup before writing
    backup_path = create_backup(filepath)
    
    # Write to temporary file first
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        # Validate data before writing
        if not validate_json_data(data):
            logging.error(f"[RobustMessageBus] Invalid JSON data structure")
            return False
        
        # Write to temporary file
        json.dump(data, temp_file, indent=2)
        temp_file.close()
        
        # Validate the written file
        if not validate_json_file(temp_file.name):
            logging.error(f"[RobustMessageBus] Invalid JSON written to temp file")
            os.unlink(temp_file.name)
            return False
        
        # Atomic move to target file
        shutil.move(temp_file.name, filepath)
        
        # Final validation
        if not validate_json_file(filepath):
            logging.error(f"[RobustMessageBus] Invalid JSON in final file, restoring backup")
            restore_backup(filepath, backup_path)
            return False
        
        logging.info(f"[RobustMessageBus] Successfully wrote JSON to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"[RobustMessageBus] Error writing JSON: {e}")
        # Cleanup on failure
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        # Restore from backup if available
        if backup_path and backup_path.exists():
            restore_backup(filepath, backup_path)
        return False

def validate_json_data(data: dict) -> bool:
    """Validate JSON data structure."""
    try:
        # Check if it's a dict
        if not isinstance(data, dict):
            return False
        
        # Check if it has events key
        if 'events' not in data:
            return False
        
        # Check if events is a list
        if not isinstance(data['events'], list):
            return False
        
        # Validate each event
        for event in data['events']:
            if not isinstance(event, dict):
                return False
            if 'timestamp' not in event or 'event' not in event or 'data' not in event:
                return False
        
        return True
    except Exception:
        return False

def validate_json_file(filepath: str) -> bool:
    """Validate JSON file integrity."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return validate_json_data(data)
    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
        logging.error(f"[RobustMessageBus] JSON validation failed: {e}")
        return False

def create_backup(filepath: Path) -> Optional[Path]:
    """Create automatic backup before writing."""
    try:
        if filepath.exists():
            backup_path = Path(f"{filepath}.backup")
            shutil.copy2(filepath, backup_path)
            logging.info(f"[RobustMessageBus] Created backup: {backup_path}")
            return backup_path
    except Exception as e:
        logging.error(f"[RobustMessageBus] Failed to create backup: {e}")
    return None

def restore_backup(filepath: Path, backup_path: Path) -> bool:
    """Restore file from backup."""
    try:
        if backup_path.exists():
            shutil.copy2(backup_path, filepath)
            logging.info(f"[RobustMessageBus] Restored from backup: {backup_path}")
            return True
    except Exception as e:
        logging.error(f"[RobustMessageBus] Failed to restore from backup: {e}")
    return False

def load_context_safely() -> dict:
    """Safely load context with validation and recovery."""
    try:
        if not SHARED_CONTEXT_PATH.exists():
            return {"events": []}
        
        # Try to load the file
        if validate_json_file(str(SHARED_CONTEXT_PATH)):
            with open(SHARED_CONTEXT_PATH, 'r') as f:
                return json.load(f)
        else:
            # Try to recover from backup
            backup_path = Path(f"{SHARED_CONTEXT_PATH}.backup")
            if backup_path.exists() and validate_json_file(str(backup_path)):
                logging.warning(f"[RobustMessageBus] Restoring from backup due to corruption")
                restore_backup(SHARED_CONTEXT_PATH, backup_path)
                with open(SHARED_CONTEXT_PATH, 'r') as f:
                    return json.load(f)
            else:
                logging.error(f"[RobustMessageBus] Both main file and backup are corrupted")
                return {"events": []}
                
    except Exception as e:
        logging.error(f"[RobustMessageBus] Error loading context: {e}")
        return {"events": []}

def publish(event: str, data: dict) -> bool:
    """Publiceer een event met data naar de shared context met robuuste error handling."""
    try:
        with file_lock(SHARED_CONTEXT_PATH):
            # Load context safely
            context = load_context_safely()
            
            # Create event object
            event_obj = {
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "data": data
            }
            
            # Add event to context
            context["events"].append(event_obj)
            
            # Write context safely
            if not safe_write_json(context, SHARED_CONTEXT_PATH):
                logging.error(f"[RobustMessageBus] Failed to write event: {event}")
                return False
            
            logging.info(f"[RobustMessageBus] Event gepubliceerd: {event}")
            
            # Notify subscribers
            for callback in _subscribers.get(event, []):
                try:
                    callback(event_obj)
                except Exception as e:
                    logging.exception(f"[RobustMessageBus] Fout in subscriber callback: {e}")
            
            return True
            
    except Exception as e:
        logging.error(f"[RobustMessageBus] Error publishing event {event}: {e}")
        return False

def subscribe(event_type: str, callback: Callable) -> None:
    """Abonneer een callback op een specifiek event_type."""
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(callback)
    logging.info(f"[RobustMessageBus] Subscriber toegevoegd voor event: {event_type}")

def unsubscribe(event_type: str, callback: Callable) -> None:
    """Verwijder een callback van een specifiek event_type."""
    if event_type in _subscribers and callback in _subscribers[event_type]:
        _subscribers[event_type].remove(callback)
        logging.info(f"[RobustMessageBus] Subscriber verwijderd voor event: {event_type}")

def get_events(event_type: Optional[str] = None, since: Optional[str] = None) -> List[dict]:
    """Haal events op, optioneel gefilterd op type en tijd."""
    try:
        context = load_context_safely()
        events = context.get("events", [])
        
        if event_type:
            events = [e for e in events if e["event"] == event_type]
        if since:
            events = [e for e in events if e["timestamp"] > since]
        
        return events
    except Exception as e:
        logging.error(f"[RobustMessageBus] Error getting events: {e}")
        return []

def clear_events() -> bool:
    """Wis alle events (voor test/reset doeleinden) met robuuste error handling."""
    try:
        with file_lock(SHARED_CONTEXT_PATH):
            if not safe_write_json({"events": []}, SHARED_CONTEXT_PATH):
                return False
            
            logging.info("[RobustMessageBus] Alle events gewist.")
            return True
    except Exception as e:
        logging.error(f"[RobustMessageBus] Error clearing events: {e}")
        return False

def get_statistics() -> dict:
    """Get statistics about the message bus."""
    try:
        context = load_context_safely()
        events = context.get("events", [])
        
        event_types = {}
        for event in events:
            event_type = event.get("event", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "total_events": len(events),
            "event_types": event_types,
            "file_size": SHARED_CONTEXT_PATH.stat().st_size if SHARED_CONTEXT_PATH.exists() else 0,
            "backup_exists": Path(f"{SHARED_CONTEXT_PATH}.backup").exists()
        }
    except Exception as e:
        logging.error(f"[RobustMessageBus] Error getting statistics: {e}")
        return {"error": str(e)} 