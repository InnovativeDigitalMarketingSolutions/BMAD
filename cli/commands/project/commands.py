"""
Project CLI Commands

CLI command definitions for project integration.
"""

import argparse
import sys
from typing import Optional

from cli.core.base_cli import BaseCLI
from .handlers import ProjectHandlers

class ProjectCommands(BaseCLI):
    """Project CLI commands."""
    def __init__(self):
        super().__init__("Project CLI", "Beheer BMAD projecten en ClickUp configuraties")
        self.handlers = ProjectHandlers()

    def setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=self.description)
        subparsers = parser.add_subparsers(dest="command", help="Beschikbare commando's")

        # List projects command
        subparsers.add_parser("list", help="Toon alle projecten")

        # Create project command
        create_parser = subparsers.add_parser("create", help="Maak nieuw project aan")
        create_parser.add_argument("project_id", help="Unieke project identifier")
        create_parser.add_argument("name", help="Project naam")
        create_parser.add_argument("--description", "-d", default="", help="Project beschrijving")
        create_parser.add_argument("--folder-id", help="ClickUp folder ID")
        create_parser.add_argument("--list-id", help="ClickUp list ID")

        # Set active project command
        active_parser = subparsers.add_parser("active", help="Stel actief project in")
        active_parser.add_argument("project_id", help="Project ID om actief te maken")

        # Show project command
        show_parser = subparsers.add_parser("show", help="Toon project details")
        show_parser.add_argument("project_id", nargs="?", help="Project ID (gebruikt actief project als niet opgegeven)")

        # Update project command
        update_parser = subparsers.add_parser("update", help="Update project configuratie")
        update_parser.add_argument("project_id", help="Project ID")
        update_parser.add_argument("--name", help="Nieuwe project naam")
        update_parser.add_argument("--description", "-d", help="Nieuwe project beschrijving")
        update_parser.add_argument("--folder-id", help="Nieuwe ClickUp folder ID")
        update_parser.add_argument("--list-id", help="Nieuwe ClickUp list ID")

        # Delete project command
        delete_parser = subparsers.add_parser("delete", help="Verwijder project")
        delete_parser.add_argument("project_id", help="Project ID om te verwijderen")

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
            return self.handlers.create_project(
                args.project_id,
                args.name,
                args.description,
                args.folder_id,
                args.list_id
            )
        elif args.command == "active":
            return self.handlers.set_active_project(args.project_id)
        elif args.command == "show":
            return self.handlers.show_project(args.project_id)
        elif args.command == "update":
            return self.handlers.update_project(
                args.project_id,
                args.name,
                args.description,
                args.folder_id,
                args.list_id
            )
        elif args.command == "delete":
            return self.handlers.delete_project(args.project_id)
        else:
            self.log_error(f"Onbekend commando: {args.command}")
            return False

    def print_help(self):
        help_text = """
BMAD Project Management CLI
===========================

Beschikbare commando's:
  list                     - Toon alle projecten
  create <id> <name>       - Maak nieuw project aan
  active <id>              - Stel actief project in
  show [id]                - Toon project details
  update <id>              - Update project configuratie
  delete <id>              - Verwijder project
  help                     - Toon deze help

Voorbeelden:
  python project_cli.py list
  python project_cli.py create my-project "My Project"
  python project_cli.py active my-project
  python project_cli.py show my-project
        """
        print(help_text)


def main():
    commands = ProjectCommands()
    success = commands.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 