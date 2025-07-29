"""
Figma CLI Commands

CLI command definitions for Figma integration.
"""

import argparse
from typing import List, Optional

from cli.core.base_cli import BaseCLI
from .handlers import FigmaHandlers


class FigmaCommands(BaseCLI):
    """Figma CLI commands."""
    
    def __init__(self):
        """Initialize Figma commands."""
        super().__init__("Figma CLI", "Generate components and documentation from Figma designs")
        self.handlers = FigmaHandlers()
        
    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser for Figma CLI."""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Voorbeelden:
  python figma_cli.py test <file_id>
  python figma_cli.py components <file_id>
  python figma_cli.py analyze <file_id>
  python figma_cli.py document <file_id>
  python figma_cli.py monitor <file_id>
            """
        )

        parser.add_argument(
            "command",
            choices=["test", "components", "analyze", "document", "monitor", "help"],
            help="Het commando om uit te voeren"
        )

        parser.add_argument(
            "file_id",
            nargs="?",
            help="Figma file ID"
        )

        parser.add_argument(
            "--output",
            help="Output file or directory"
        )
        
        return parser
        
    def execute_command(self, args: argparse.Namespace) -> bool:
        """Execute the Figma CLI command."""
        # Check environment
        if not self._check_environment():
            return False
            
        # Execute command
        if args.command == "help":
            self.print_help()
            return True
        elif args.command == "test":
            if not args.file_id:
                self.log_error("File ID required for test command")
                return False
            return self.handlers.test_connection(args.file_id)
        elif args.command == "components":
            if not args.file_id:
                self.log_error("File ID required for components command")
                return False
            return self.handlers.generate_components(args.file_id, args.output or "components")
        elif args.command == "analyze":
            if not args.file_id:
                self.log_error("File ID required for analyze command")
                return False
            return self.handlers.analyze_design(args.file_id)
        elif args.command == "document":
            if not args.file_id:
                self.log_error("File ID required for document command")
                return False
            return self.handlers.generate_documentation(args.file_id, args.output)
        elif args.command == "monitor":
            if not args.file_id:
                self.log_error("File ID required for monitor command")
                return False
            return self.handlers.start_monitoring(args.file_id)
        else:
            self.log_error(f"Onbekend commando: {args.command}")
            return False
            
    def _check_environment(self) -> bool:
        """Check if required environment variables are set."""
        import os
        if not os.getenv("FIGMA_API_TOKEN"):
            self.log_error("FIGMA_API_TOKEN niet gevonden in environment")
            self.log_info("Zorg dat je .env file geladen is: source .env")
            return False
        return True 