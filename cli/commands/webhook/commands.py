"""
Webhook CLI Commands

CLI command definitions for webhook integration.
"""

import argparse
import sys
from typing import Optional

from cli.core.base_cli import BaseCLI
from .handlers import WebhookHandlers


class WebhookCommands(BaseCLI):
    """Webhook CLI commands."""
    
    def __init__(self):
        """Initialize webhook commands."""
        super().__init__("Webhook CLI", "Test and manage webhook notifications")
        self.handlers = WebhookHandlers()
        
    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser for webhook CLI."""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Voorbeelden:
  python webhook_cli.py test
  python webhook_cli.py message "Hello from BMAD!"
  python webhook_cli.py hitl "Deployment approval required" --channel alerts
  python webhook_cli.py workflow "feature-dev" "started" --channel workflows
  python webhook_cli.py error "Database connection failed" --context "Production"
  python webhook_cli.py success "User registration completed" --context "New user"
  python webhook_cli.py deployment "frontend-app" "completed" --environment production
  python webhook_cli.py status
  python webhook_cli.py demo
            """
        )

        parser.add_argument(
            "command",
            choices=[
                "test", "test-manager", "message", "hitl", "workflow",
                "error", "success", "deployment", "status", "demo", "help"
            ],
            help="Command to execute"
        )

        parser.add_argument("--message", "-m", help="Message to send")
        parser.add_argument("--channel", "-c", help="Channel to send to")
        parser.add_argument("--reason", "-r", help="Reason for HITL alert")
        parser.add_argument("--workflow", "-w", help="Workflow name")
        parser.add_argument("--status", "-s", help="Status (for workflow/deployment)")
        parser.add_argument("--context", help="Additional context")
        parser.add_argument("--environment", "-e", help="Environment (for deployment)")
        parser.add_argument("--use-manager", action="store_true", help="Use notification manager instead of direct webhook")
        
        return parser
        
    def execute_command(self, args: argparse.Namespace) -> bool:
        """Execute the webhook CLI command."""
        if args.command == "help":
            self.print_help()
            return True
        elif args.command == "test":
            return self.handlers.test_webhook()
        elif args.command == "test-manager":
            return self.handlers.test_notification_manager()
        elif args.command == "message":
            if not args.message:
                self.log_error("--message is required for 'message' command")
                return False
            return self.handlers.send_message(args.message, args.channel, args.use_manager)
        elif args.command == "hitl":
            if not args.reason:
                self.log_error("--reason is required for 'hitl' command")
                return False
            return self.handlers.send_hitl(args.reason, args.channel, args.use_manager)
        elif args.command == "workflow":
            if not args.workflow or not args.status:
                self.log_error("--workflow and --status are required for 'workflow' command")
                return False
            return self.handlers.send_workflow(args.workflow, args.status, args.channel, args.use_manager)
        elif args.command == "error":
            if not args.message:
                self.log_error("--message is required for 'error' command")
                return False
            return self.handlers.send_error(args.message, args.context, args.channel, args.use_manager)
        elif args.command == "success":
            if not args.message:
                self.log_error("--message is required for 'success' command")
                return False
            return self.handlers.send_success(args.message, args.context, args.channel, args.use_manager)
        elif args.command == "deployment":
            if not args.workflow or not args.status:
                self.log_error("--workflow and --status are required for 'deployment' command")
                return False
            return self.handlers.send_deployment(args.workflow, args.status, args.environment, args.channel, args.use_manager)
        elif args.command == "status":
            return self.handlers.show_status()
        elif args.command == "demo":
            return self.handlers.demo_all()
        else:
            self.log_error(f"Onbekend commando: {args.command}")
            return False
            
    def print_help(self):
        """Print help information."""
        help_text = """
BMAD Webhook CLI - Webhook Management
====================================

Beschikbare commando's:
  test                      - Test webhook connection
  test-manager              - Test notification manager
  message <message>         - Send webhook message
  hitl <reason>             - Send HITL alert
  workflow <name> <status>  - Send workflow notification
  error <message>           - Send error notification
  success <message>         - Send success notification
  deployment <name> <status> - Send deployment notification
  status                    - Get webhook and notification status
  demo                      - Run complete demo
  help                      - Toon deze help

Opties:
  --channel, -c             - Channel to send to
  --use-manager             - Use notification manager instead of direct webhook
  --context                 - Additional context (for error/success)
  --environment, -e         - Environment (for deployment)
  --reason, -r              - Reason for HITL alert
  --workflow, -w            - Workflow name
  --status, -s              - Status (for workflow/deployment)

Voorbeelden:
  python webhook_cli.py test
  python webhook_cli.py message "Hello from BMAD!"
  python webhook_cli.py hitl "Deployment approval required" --channel alerts
  python webhook_cli.py workflow "feature-dev" "started" --channel workflows
  python webhook_cli.py error "Database connection failed" --context "Production"
  python webhook_cli.py success "User registration completed" --context "New user"
  python webhook_cli.py deployment "frontend-app" "completed" --environment production
  python webhook_cli.py status
  python webhook_cli.py demo
        """
        print(help_text)


def main():
    """Main CLI function."""
    commands = WebhookCommands()
    success = commands.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 