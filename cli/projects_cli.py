#!/usr/bin/env python3
"""
BMAD Project CLI
Command-line interface voor project management
"""

import argparse
import sys
from pathlib import Path

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent))

from bmad.projects.project_manager import project_manager


class ProjectsCLI:
    """Projects CLI class for BMAD project management."""
    
    def __init__(self):
        """Initialize Projects CLI."""
        self.project_manager = project_manager
        
    def list_projects(self):
        """List all projects."""
        return list_projects()
    
    def create_project(self, project_id: str, name: str, description: str = ""):
        """Create a new project."""
        return create_project(project_id, name, description)
    
    def add_requirement(self, project_id: str, requirement: str, category: str = "general"):
        """Add requirement to project."""
        return add_requirement(project_id, requirement, category)
    
    def add_user_story(self, project_id: str, story: str, priority: str = "medium"):
        """Add user story to project."""
        return add_user_story(project_id, story, priority)
    
    def show_project_info(self):
        """Show project information."""
        return show_project_info()
    
    def show_help(self):
        """Show help information."""
        print_help()


def print_help():
    """Print help information."""
    help_text = """
BMAD Projects CLI - Project Management
======================================

Beschikbare commando's:
  list                     - Toon alle projecten
  create <id> <name>       - Maak nieuw project aan
  requirement <id> <text>  - Voeg requirement toe
  story <id> <text>        - Voeg user story toe
  info                     - Toon project informatie
  help                     - Toon deze help

Voorbeelden:
  python projects_cli.py list
  python projects_cli.py create my-project "My Project"
  python projects_cli.py requirement my-project "Must be fast"
  python projects_cli.py story my-project "As a user I want to..."
        """
    print(help_text)


def list_projects():
    """List all projects."""
    print("📋 Available Projects:")
    print("🚧 This function is a placeholder. Actual project listing would go here.")
    print("   To implement this, you would need to:")
    print("   1. Connect to the project manager.")
    print("   2. Query all available projects.")
    print("   3. Display project names, IDs, and status.")
    return True


def create_project(project_id: str, name: str, description: str = ""):
    """Create a new project."""
    print(f"🚀 Creating project: {project_id}")
    print(f"   Name: {name}")
    print(f"   Description: {description}")
    print("🚧 This function is a placeholder. Actual project creation would go here.")
    return True


def add_requirement(project_id: str, requirement: str, category: str = "general"):
    """Add requirement to project."""
    print(f"📝 Adding requirement to project: {project_id}")
    print(f"   Requirement: {requirement}")
    print(f"   Category: {category}")
    print("🚧 This function is a placeholder. Actual requirement addition would go here.")
    return True


def add_user_story(project_id: str, story: str, priority: str = "medium"):
    """Add user story to project."""
    print(f"📖 Adding user story to project: {project_id}")
    print(f"   Story: {story}")
    print(f"   Priority: {priority}")
    print("🚧 This function is a placeholder. Actual user story addition would go here.")
    return True


def show_project_info():
    """Show project information."""
    print("📊 Project Information:")
    print("🚧 This function is a placeholder. Actual project info would go here.")
    return True


def main():
    parser = argparse.ArgumentParser(description="BMAD Project Manager")
    subparsers = parser.add_subparsers(dest="command", help="Beschikbare commando's")

    # List projects
    subparsers.add_parser("list", help="Toon alle projecten")

    # Create project
    create_parser = subparsers.add_parser("create", help="Maak nieuw project aan")
    create_parser.add_argument("project_id", help="Unieke project identifier")
    create_parser.add_argument("name", help="Project naam")
    create_parser.add_argument("--description", "-d", default="", help="Project beschrijving")

    # Add requirement
    req_parser = subparsers.add_parser("requirement", help="Voeg requirement toe")
    req_parser.add_argument("project_id", help="Project ID")
    req_parser.add_argument("requirement", help="Requirement tekst")
    req_parser.add_argument("--category", "-c", default="general", help="Requirement categorie")

    # Add user story
    story_parser = subparsers.add_parser("story", help="Voeg user story toe")
    story_parser.add_argument("project_id", help="Project ID")
    story_parser.add_argument("story", help="User story tekst")
    story_parser.add_argument("--priority", "-p", default="medium", help="Prioriteit (low/medium/high)")

    # Show project info
    subparsers.add_parser("info", help="Toon project informatie")

    # Help command
    subparsers.add_parser("help", help="Toon help informatie")

    args = parser.parse_args()

    # Execute command
    if args.command == "help" or not args.command:
        print_help()
        return True
    elif args.command == "list":
        return list_projects()
    elif args.command == "create":
        return create_project(args.project_id, args.name, args.description)
    elif args.command == "requirement":
        return add_requirement(args.project_id, args.requirement, args.category)
    elif args.command == "story":
        return add_user_story(args.project_id, args.story, args.priority)
    elif args.command == "info":
        return show_project_info()
    else:
        print(f"❌ Onbekend commando: {args.command}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
