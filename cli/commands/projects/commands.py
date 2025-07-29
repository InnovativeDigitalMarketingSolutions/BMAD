"""
Projects CLI Commands

CLI command definitions for projects integration.
"""

import argparse
import sys
from typing import Optional

from cli.core.base_cli import BaseCLI
from .handlers import ProjectsHandlers

class ProjectsCommands(BaseCLI):
    """Projects CLI commands."""
    def __init__(self):
        super().__init__("Projects CLI", "Command-line interface voor project management")
        self.handlers = ProjectsHandlers()

    def setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self.description)
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

        return parser

    def execute_command(self, args: argparse.Namespace) -> bool:
        if args.command == "help" or not args.command:
            self.print_help()
            return True
        elif args.command == "list":
            return self.handlers.list_projects()
        elif args.command == "create":
            return self.handlers.create_project(args.project_id, args.name, args.description)
        elif args.command == "requirement":
            return self.handlers.add_requirement(args.project_id, args.requirement, args.category)
        elif args.command == "story":
            return self.handlers.add_user_story(args.project_id, args.story, args.priority)
        elif args.command == "info":
            return self.handlers.show_project_info()
        else:
            self.log_error(f"Onbekend commando: {args.command}")
            return False

    def print_help(self):
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


def main():
    commands = ProjectsCommands()
    success = commands.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 