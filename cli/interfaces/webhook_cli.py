"""
Webhook CLI Interface

Thin wrapper interface for webhook CLI commands.
"""

import sys
from typing import Optional

from cli.commands.webhook.commands import WebhookCommands
from cli.commands.webhook.handlers import WebhookHandlers


class WebhookCLI:
    """Webhook CLI class for BMAD webhook management."""
    
    def __init__(self):
        """Initialize Webhook CLI."""
        self.commands = WebhookCommands()
        self.handlers = WebhookHandlers()
        
    def test_webhook(self) -> bool:
        """Test webhook connection."""
        return self.handlers.test_webhook()
    
    def test_notification_manager(self) -> bool:
        """Test notification manager."""
        return self.handlers.test_notification_manager()
    
    def send_message(self, message: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
        """Send a webhook message."""
        return self.handlers.send_message(message, channel, use_manager)
    
    def send_hitl(self, reason: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
        """Send a HITL alert."""
        return self.handlers.send_hitl(reason, channel, use_manager)
    
    def send_workflow(self, workflow_name: str, status: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
        """Send a workflow notification."""
        return self.handlers.send_workflow(workflow_name, status, channel, use_manager)
    
    def send_error(self, error_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
        """Send an error notification."""
        return self.handlers.send_error(error_message, context, channel, use_manager)
    
    def send_success(self, success_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
        """Send a success notification."""
        return self.handlers.send_success(success_message, context, channel, use_manager)
    
    def send_deployment(self, deployment_name: str, status: str, environment: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
        """Send a deployment notification."""
        return self.handlers.send_deployment(deployment_name, status, environment, channel, use_manager)
    
    def get_status(self) -> bool:
        """Get webhook and notification status."""
        return self.handlers.show_status()
    
    def demo_all(self) -> bool:
        """Run a complete demo of all webhook functionality."""
        return self.handlers.demo_all()
    
    def show_help(self):
        """Show help information."""
        self.commands.print_help()


def main():
    """Main CLI function."""
    commands = WebhookCommands()
    success = commands.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 