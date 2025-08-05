#!/usr/bin/env python3
"""
Script to restore shared_context.json from backup while fixing corruption
"""

import json
import sys
from pathlib import Path

def restore_shared_context_json():
    """Restore shared_context.json from backup while fixing corruption."""
    
    backup_path = Path("bmad/agents/core/shared_context.json.backup")
    current_path = Path("bmad/agents/core/shared_context.json")
    
    print("🔧 Restoring shared_context.json from backup...")
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Read the backup file
    with open(backup_path, 'r') as f:
        content = f.read()
    
    print(f"📊 Backup file has {len(content)} characters")
    
    # Find the corruption point - look for the incomplete data field
    corruption_marker = '"data": %'
    corruption_index = content.find(corruption_marker)
    
    if corruption_index == -1:
        print("✅ No corruption found, backup is clean")
        # Copy backup to current
        with open(current_path, 'w') as f:
            f.write(content)
        return True
    
    print(f"🚨 Found corruption at character {corruption_index}")
    
    # Get content before corruption
    valid_content = content[:corruption_index]
    
    # Find the last complete event object
    # Look for the last complete event structure that ends with "},"
    lines = valid_content.split('\n')
    last_complete_line = -1
    
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line == '},':
            last_complete_line = i
            break
    
    if last_complete_line == -1:
        print("❌ Could not find last complete event")
        return False
    
    # Get content up to the last complete event
    clean_lines = lines[:last_complete_line + 1]
    clean_content = '\n'.join(clean_lines)
    
    # Remove trailing comma and add closing brackets
    clean_content = clean_content.rstrip().rstrip(',') + '\n  }\n]\n'
    
    # Write the restored content
    with open(current_path, 'w') as f:
        f.write(clean_content)
    
    print(f"✅ Restored file written to: {current_path}")
    
    # Validate the restored file
    try:
        with open(current_path, 'r') as f:
            data = json.load(f)
        
        event_count = len(data.get('events', []))
        print(f"✅ Restored file is valid JSON with {event_count} events!")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Restored file still has JSON errors: {e}")
        # Show the problematic area
        with open(current_path, 'r') as f:
            lines = f.readlines()
        print(f"🔍 Last 5 lines of restored file:")
        for i, line in enumerate(lines[-5:], len(lines)-4):
            print(f"  {i}: {line.rstrip()}")
        return False

if __name__ == "__main__":
    success = restore_shared_context_json()
    sys.exit(0 if success else 1) 