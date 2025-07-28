#!/usr/bin/env python3
"""
Simple BMAD Runner for Copilot Project
Executes tasks defined in bmad.yaml
"""

import argparse
import subprocess
import sys
import yaml


def load_config(config_path="bmad.yaml"):
    """Load BMAD configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing {config_path}: {e}")
        sys.exit(1)


def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    print(f"🚀 Running: {command}")
    try:
        subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=True,
            capture_output=False,
            text=True
        )
        print("✅ Command completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        return False


def list_tasks(config):
    """List all available tasks"""
    print("📋 Available tasks:")
    for agent in config.get('agents', []):
        print(f"  • {agent['name']:<15} - {agent.get('description', 'No description')}")


def main():
    parser = argparse.ArgumentParser(description="BMAD Runner for Copilot Project")
    parser.add_argument("task", nargs='?', help="Task to run")
    parser.add_argument("--config", default="bmad.yaml", help="Path to config file")
    parser.add_argument("--list", action="store_true", help="List all available tasks")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # List tasks if requested
    if args.list or not args.task:
        list_tasks(config)
        if not args.task:
            return
    
    # Find the requested task
    task = None
    for agent in config.get('agents', []):
        if agent['name'] == args.task:
            task = agent
            break
    
    if not task:
        print(f"❌ Error: Task '{args.task}' not found in configuration")
        print("\nAvailable tasks:")
        list_tasks(config)
        sys.exit(1)
    
    # Run the task
    print(f"🎯 Executing task: {task['name']}")
    if 'description' in task:
        print(f"📝 Description: {task['description']}")
    print("-" * 50)
    
    success = run_command(task['command'])
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()