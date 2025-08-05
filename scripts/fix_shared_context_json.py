#!/usr/bin/env python3
"""
Script to fix corrupted shared_context.json file
"""

import json
import sys
from pathlib import Path

def fix_shared_context_json():
    """Fix the corrupted shared_context.json file."""
    
    file_path = Path("bmad/agents/core/shared_context.json")
    backup_path = Path("bmad/agents/core/shared_context.json.backup")
    fixed_path = Path("bmad/agents/core/shared_context_fixed.json")
    
    print("🔧 Fixing corrupted shared_context.json file...")
    
    # Create backup if it doesn't exist
    if not backup_path.exists():
        print(f"📋 Creating backup: {backup_path}")
        with open(file_path, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
    
    # Read the file and find the corruption
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    print(f"📊 File has {len(lines)} lines")
    
    # Find the last valid JSON structure
    valid_lines = []
    for i, line in enumerate(lines):
        if '"data": %' in line:
            print(f"🚨 Found corruption at line {i+1}: {line.strip()}")
            break
        valid_lines.append(line)
    
    # Remove the incomplete object that starts with the timestamp
    # Find the last complete object
    for i in range(len(valid_lines) - 1, -1, -1):
        line = valid_lines[i].strip()
        if line.startswith('"timestamp"') and '"event"' in line:
            print(f"🔍 Found incomplete object starting at line {i+1}")
            # Remove this incomplete object and everything after it
            valid_lines = valid_lines[:i]
            break
    
    # Remove trailing comma from the last valid object
    if valid_lines and valid_lines[-1].strip().endswith(','):
        valid_lines[-1] = valid_lines[-1].rstrip().rstrip(',') + '\n'
    
    # Add closing brackets
    valid_lines.append("  }\n")
    valid_lines.append("]\n")
    
    # Write the fixed content
    with open(fixed_path, 'w') as f:
        f.writelines(valid_lines)
    
    print(f"✅ Fixed file written to: {fixed_path}")
    print(f"📊 Fixed file has {len(valid_lines)} lines")
    
    # Validate the fixed file
    try:
        with open(fixed_path, 'r') as f:
            data = json.load(f)
        print(f"✅ Fixed file is valid JSON with {len(data)} objects!")
        
        # Replace the original file
        import shutil
        shutil.copy2(fixed_path, file_path)
        print("✅ Original file replaced with fixed version")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Fixed file still has JSON errors: {e}")
        # Show the problematic area
        with open(fixed_path, 'r') as f:
            lines = f.readlines()
        print(f"🔍 Last 5 lines of fixed file:")
        for i, line in enumerate(lines[-5:], len(lines)-4):
            print(f"  {i}: {line.rstrip()}")
        return False

if __name__ == "__main__":
    success = fix_shared_context_json()
    sys.exit(0 if success else 1) 