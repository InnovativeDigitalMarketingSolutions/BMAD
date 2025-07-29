"""
LangGraph CLI Commands

Command-line argument parsing and dispatch for LangGraph CLI.
"""

import argparse
import asyncio
import sys
from .handlers import LangGraphHandlers

class LangGraphCommands:
    """Command-line interface for LangGraph CLI."""
    
    def __init__(self):
        self.handlers = LangGraphHandlers()
    
    def setup_parser(self):
        """Setup argument parser."""
        parser = argparse.ArgumentParser(
            description="BMAD LangGraph Workflow CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Voorbeelden:
  python langgraph_cli.py demo demo_workflow
  python langgraph_cli.py demo simple_workflow
  python langgraph_cli.py status workflow_123
  python langgraph_cli.py list
  python langgraph_cli.py test
            """
        )

        parser.add_argument(
            "command",
            choices=["demo", "status", "list", "test", "help"],
            help="Het commando om uit te voeren"
        )

        parser.add_argument(
            "workflow_name",
            nargs="?",
            help="Workflow name or ID"
        )

        return parser
    
    def execute_command(self, args):
        """Execute the parsed command."""
        if args.command == "help":
            self.show_help()
            return True
        elif args.command == "demo":
            if not args.workflow_name:
                args.workflow_name = "demo_workflow"
            return asyncio.run(self.handlers.run_workflow_demo(args.workflow_name))
        elif args.command == "status":
            if not args.workflow_name:
                print("❌ Workflow ID required for status command")
                return False
            return self.handlers.show_workflow_status(args.workflow_name)
        elif args.command == "list":
            return self.handlers.list_workflows()
        elif args.command == "test":
            return self.handlers.test_langgraph_integration()
        else:
            print(f"❌ Onbekend commando: {args.command}")
            return False
    
    def show_help(self):
        """Show help information."""
        help_text = """
BMAD LangGraph CLI - Workflow Management
=======================================

Beschikbare commando's:
  demo <workflow_name>     - Run workflow demonstration
  status <workflow_id>     - Show workflow status
  list                     - List all workflows
  test                     - Test LangGraph integration
  help                     - Show this help

Voorbeelden:
  python langgraph_cli.py demo demo_workflow
  python langgraph_cli.py demo simple_workflow
  python langgraph_cli.py status workflow_123
  python langgraph_cli.py list
  python langgraph_cli.py test
        """
        print(help_text)
    
    def main(self):
        """Main CLI function."""
        parser = self.setup_parser()
        args = parser.parse_args()
        return self.execute_command(args)

# Legacy function for backward compatibility
def main():
    """Main CLI function."""
    commands = LangGraphCommands()
    return commands.main() 