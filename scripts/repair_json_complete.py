#!/usr/bin/env python3
"""
Script to completely repair the shared_context.json file
"""

import json
import sys
from pathlib import Path

def repair_json_complete():
    """Completely repair the shared_context.json file."""
    
    backup_path = Path("bmad/agents/core/shared_context.json.backup")
    current_path = Path("bmad/agents/core/shared_context.json")
    
    print("🔧 Completely repairing shared_context.json...")
    
    # Read the backup file
    with open(backup_path, 'r') as f:
        content = f.read()
    
    print(f"📊 Backup file has {len(content)} characters")
    
    # Find the corruption point
    corruption_marker = '"data": %'
    corruption_index = content.find(corruption_marker)
    
    if corruption_index == -1:
        print("✅ No corruption found")
        return True
    
    print(f"🚨 Found corruption at character {corruption_index}")
    
    # Get content before corruption
    valid_content = content[:corruption_index]
    
    # Find the last complete event by looking for the pattern
    # We need to find where the last complete event ends
    lines = valid_content.split('\n')
    
    # Look for the last complete event structure
    # A complete event ends with "},"
    last_complete_line = -1
    
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line == '},':
            # This is a complete event
            last_complete_line = i
            break
    
    if last_complete_line == -1:
        print("❌ Could not find last complete event")
        return False
    
    print(f"✅ Found last complete event at line {last_complete_line}")
    
    # Get the valid content up to the last complete event
    valid_lines = lines[:last_complete_line + 1]
    
    # Remove the trailing comma from the last line
    if valid_lines and valid_lines[-1].strip() == '},':
        valid_lines[-1] = valid_lines[-1].replace('},', '}')
    
    # Add closing brackets
    valid_lines.append('  }')
    valid_lines.append(']')
    
    # Join the lines
    repaired_content = '\n'.join(valid_lines)
    
    # Write the repaired content
    with open(current_path, 'w') as f:
        f.write(repaired_content)
    
    print(f"✅ Repaired file written to: {current_path}")
    
    # Validate the repaired file
    try:
        with open(current_path, 'r') as f:
            data = json.load(f)
        
        event_count = len(data.get('events', []))
        print(f"✅ Repaired file is valid JSON with {event_count} events!")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Repaired file still has JSON errors: {e}")
        # Show the problematic area
        with open(current_path, 'r') as f:
            lines = f.readlines()
        print(f"🔍 Last 10 lines of repaired file:")
        for i, line in enumerate(lines[-10:], len(lines)-9):
            print(f"  {i}: {line.rstrip()}")
        return False

if __name__ == "__main__":
    success = repair_json_complete()
    sys.exit(0 if success else 1) 