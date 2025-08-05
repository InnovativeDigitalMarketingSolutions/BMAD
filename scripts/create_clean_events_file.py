#!/usr/bin/env python3
"""
Create clean events file from backup
"""

import json
import sys
from pathlib import Path

def create_clean_events_file():
    """Create a clean events file from the backup."""
    
    backup_path = Path("bmad/agents/core/shared_context.json.backup")
    current_path = Path("bmad/agents/core/shared_context.json")
    
    print("🔧 Creating clean events file...")
    
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Read the backup file
    with open(backup_path, 'r') as f:
        content = f.read()
    
    print(f"📊 Backup file has {len(content)} characters")
    
    # Find the corruption point
    lines = content.split('\n')
    corruption_line = -1
    
    for i, line in enumerate(lines):
        if '"data":' in line and '%' in line:
            corruption_line = i
            break
    
    if corruption_line == -1:
        print("✅ No corruption found, backup is clean")
        # Copy backup to current
        import shutil
        shutil.copy2(backup_path, current_path)
        return True
    
    print(f"🚨 Found corruption at line {corruption_line + 1}")
    
    # Get content before corruption
    valid_lines = lines[:corruption_line]
    
    # Find the last complete event
    last_complete_line = -1
    
    for i in range(len(valid_lines) - 1, -1, -1):
        line = valid_lines[i].strip()
        if line == '},':
            last_complete_line = i
            break
    
    if last_complete_line == -1:
        print("❌ Could not find last complete event")
        return False
    
    print(f"✅ Found last complete event at line {last_complete_line + 1}")
    
    # Get content up to the last complete event
    final_lines = valid_lines[:last_complete_line + 1]
    
    # Remove trailing comma from the last line
    if final_lines and final_lines[-1].strip() == '},':
        final_lines[-1] = final_lines[-1].replace('},', '}')
    
    # Add closing brackets
    final_lines.append('  }')
    final_lines.append(']')
    
    # Join the lines
    recovered_content = '\n'.join(final_lines)
    
    # Write the recovered content
    with open(current_path, 'w') as f:
        f.write(recovered_content)
    
    print(f"✅ Clean file written to: {current_path}")
    
    # Validate the recovered file
    try:
        with open(current_path, 'r') as f:
            data = json.load(f)
        
        event_count = len(data.get('events', []))
        print(f"✅ Clean file is valid JSON with {event_count} events!")
        
        # Show some statistics
        if event_count > 0:
            events = data.get('events', [])
            event_types = {}
            for event in events:
                event_type = event.get('event', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            print(f"📈 Event types recovered:")
            for event_type, count in sorted(event_types.items()):
                print(f"  - {event_type}: {count} events")
            
            # Show time range
            if events:
                timestamps = [event.get('timestamp', '') for event in events if event.get('timestamp')]
                if timestamps:
                    timestamps.sort()
                    print(f"📅 Time range: {timestamps[0]} to {timestamps[-1]}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Clean file still has JSON errors: {e}")
        return False

if __name__ == "__main__":
    success = create_clean_events_file()
    sys.exit(0 if success else 1) 