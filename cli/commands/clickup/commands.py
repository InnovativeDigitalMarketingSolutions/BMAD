"""
ClickUp CLI Commands

Command-line argument parsing and dispatch for ClickUp CLI.
"""

import argparse
import os
import sys
from pathlib import Path
from .handlers import ClickUpHandlers

class ClickUpCommands:
    """Command-line interface for ClickUp CLI."""
    
    def __init__(self):
        self.handlers = None  # Will be initialized per command
    
    def setup_parser(self):
        """Setup argument parser."""
        parser = argparse.ArgumentParser(
            description="BMAD ClickUp Workflow CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Voorbeelden:
  python bmad_cli_clickup.py adapt-template bmad-frontend
  python bmad_cli_clickup.py generate-planning bmad-frontend
  python bmad_cli_clickup.py create-sprints bmad-frontend
  python bmad_cli_clickup.py full-workflow bmad-frontend
  python bmad_cli_clickup.py list-projects
            """
        )

        parser.add_argument(
            "command",
            choices=["adapt-template", "generate-planning", "create-sprints", "full-workflow", "list-projects"],
            help="Het commando om uit te voeren"
        )

        parser.add_argument(
            "project_id",
            nargs="?",
            default="bmad-frontend",
            help="Project ID (default: bmad-frontend)"
        )

        return parser
    
    def check_environment(self):
        """Check if required environment variables are set."""
        if not os.getenv("CLICKUP_API_KEY"):
            print("❌ CLICKUP_API_KEY niet gevonden in environment")
            print("Zorg dat je .env file geladen is: source .env")
            return False
        return True
    
    def execute_command(self, args):
        """Execute the parsed command."""
        # Check environment first
        if not self.check_environment():
            return False

        # Initialize handlers with project_id
        self.handlers = ClickUpHandlers(args.project_id)

        # Execute command
        if args.command == "adapt-template":
            return self.handlers.adapt_template()
        elif args.command == "generate-planning":
            return self.handlers.generate_planning()
        elif args.command == "create-sprints":
            return self.handlers.create_sprints()
        elif args.command == "full-workflow":
            return self.handlers.run_full_workflow()
        elif args.command == "list-projects":
            return self.handlers.list_projects()
        else:
            print(f"❌ Onbekend commando: {args.command}")
            return False
    
    def main(self):
        """Main CLI function."""
        parser = self.setup_parser()
        args = parser.parse_args()
        return self.execute_command(args)

# Legacy function for backward compatibility
def main():
    """Main CLI function."""
    commands = ClickUpCommands()
    return commands.main() 