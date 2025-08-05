
#!/usr/bin/env python3
"""
JSON File Integrity Monitor
Monitors shared_context.json for corruption and automatically recovers
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime

SHARED_CONTEXT_PATH = Path("bmad/agents/core/shared_context.json")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def validate_json_file(filepath: Path) -> bool:
    """Validate JSON file integrity."""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except Exception as e:
        logging.error(f"JSON validation failed: {e}")
        return False

def monitor_file_integrity():
    """Monitor file integrity continuously."""
    print("🔍 Starting JSON file integrity monitor...")
    
    while True:
        try:
            if SHARED_CONTEXT_PATH.exists():
                if not validate_json_file(SHARED_CONTEXT_PATH):
                    logging.error("🚨 JSON corruption detected!")
                    
                    # Try to restore from backup
                    backup_path = Path(f"{SHARED_CONTEXT_PATH}.backup")
                    if backup_path.exists() and validate_json_file(backup_path):
                        import shutil
                        shutil.copy2(backup_path, SHARED_CONTEXT_PATH)
                        logging.info("✅ Restored from backup")
                    else:
                        logging.error("❌ Backup also corrupted")
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            break
        except Exception as e:
            logging.error(f"Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_file_integrity()
