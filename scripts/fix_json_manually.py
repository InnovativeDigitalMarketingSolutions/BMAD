#!/usr/bin/env python3
"""
Script to manually fix the shared_context.json file
"""

import json
import sys
from pathlib import Path

def fix_json_manually():
    """Manually fix the shared_context.json file."""
    
    backup_path = Path("bmad/agents/core/shared_context.json.backup")
    current_path = Path("bmad/agents/core/shared_context.json")
    
    print("🔧 Manually fixing shared_context.json...")
    
    # Read the backup file
    with open(backup_path, 'r') as f:
        lines = f.readlines()
    
    print(f"📊 Backup file has {len(lines)} lines")
    
    # Find the last complete event
    # Look for the pattern where we have a complete event structure
    last_complete_index = -1
    
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line == '},':
            # Check if this is a complete event by looking back
            if i > 0 and '},' in lines[i-1]:
                last_complete_index = i
                break
    
    if last_complete_index == -1:
        print("❌ Could not find last complete event")
        return False
    
    print(f"✅ Found last complete event at line {last_complete_index}")
    
    # Get the valid content
    valid_lines = lines[:last_complete_index + 1]
    
    # Remove the trailing comma from the last line
    if valid_lines and valid_lines[-1].strip() == '},':
        valid_lines[-1] = valid_lines[-1].replace('},', '}')
    
    # Add closing brackets
    valid_lines.append('  }\n')
    valid_lines.append(']\n')
    
    # Write the fixed content
    with open(current_path, 'w') as f:
        f.writelines(valid_lines)
    
    print(f"✅ Fixed file written to: {current_path}")
    
    # Validate the fixed file
    try:
        with open(current_path, 'r') as f:
            data = json.load(f)
        
        event_count = len(data.get('events', []))
        print(f"✅ Fixed file is valid JSON with {event_count} events!")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Fixed file still has JSON errors: {e}")
        return False

if __name__ == "__main__":
    success = fix_json_manually()
    sys.exit(0 if success else 1) 