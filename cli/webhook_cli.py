#!/usr/bin/env python3
"""
Webhook CLI Tool - Test and manage webhook notifications.
"""

import argparse
import json
import os
import sys
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bmad.agents.core.communication.notification_manager import (
    get_notification_status,
    send_deployment_notification,
    send_error_notification,
    send_hitl_notification,
    send_notification,
    send_success_notification,
    send_workflow_notification,
    test_notification_connection,
)
from integrations.webhook.webhook_notify import (
    get_webhook_status,
    send_webhook_deployment_notification,
    send_webhook_error_notification,
    send_webhook_hitl_alert,
    send_webhook_message,
    send_webhook_success_notification,
    send_webhook_workflow_notification,
    test_webhook_connection,
)


class WebhookCLI:
    """Webhook CLI class for BMAD webhook management."""
    
    def __init__(self):
        """Initialize Webhook CLI."""
        pass
        
    def test_webhook(self):
        """Test webhook connection."""
        return test_webhook()
    
    def test_notification_manager(self):
        """Test notification manager."""
        return test_notification_manager()
    
    def send_message(self, message: str, channel: Optional[str] = None, use_manager: bool = False):
        """Send a webhook message."""
        return send_message(message, channel, use_manager)
    
    def send_hitl(self, reason: str, channel: Optional[str] = None, use_manager: bool = False):
        """Send a HITL alert."""
        return send_hitl(reason, channel, use_manager)
    
    def send_workflow(self, workflow_name: str, status: str, channel: Optional[str] = None, use_manager: bool = False):
        """Send a workflow notification."""
        return send_workflow(workflow_name, status, channel, use_manager)
    
    def send_error(self, error_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False):
        """Send an error notification."""
        return send_error(error_message, context, channel, use_manager)
    
    def send_success(self, success_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False):
        """Send a success notification."""
        return send_success(success_message, context, channel, use_manager)
    
    def send_deployment(self, deployment_name: str, status: str, environment: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False):
        """Send a deployment notification."""
        return send_deployment(deployment_name, status, environment, channel, use_manager)
    
    def get_status(self):
        """Get webhook and notification status."""
        return show_status()
    
    def demo_all(self):
        """Run a complete demo of all webhook functionality."""
        return demo_all()
    
    def show_help(self):
        """Show help information."""
        print_help()


def print_help():
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


def test_webhook():
    """Test webhook connection."""
    print("🧪 Testing webhook connection...")
    success = test_webhook_connection()
    if success:
        print("✅ Webhook connection successful!")
    else:
        print("❌ Webhook connection failed!")
    return success


def test_notification_manager():
    """Test notification manager."""
    print("🧪 Testing notification manager...")
    success = test_notification_connection()
    if success:
        print("✅ Notification manager connection successful!")
    else:
        print("❌ Notification manager connection failed!")
    return success


def send_message(message: str, channel: Optional[str] = None, use_manager: bool = False):
    """Send a webhook message."""
    print(f"📤 Sending message: {message}")

    if use_manager:
        success = send_notification(message, channel=channel)
    else:
        success = send_webhook_message(message, channel=channel)

    if success:
        print("✅ Message sent successfully!")
    else:
        print("❌ Failed to send message!")
    return success


def send_hitl(reason: str, channel: Optional[str] = None, use_manager: bool = False):
    """Send a HITL alert."""
    print(f"🚨 Sending HITL alert: {reason}")

    if use_manager:
        success = send_hitl_notification(reason, channel=channel)
    else:
        success = send_webhook_hitl_alert(reason, channel=channel)

    if success:
        print("✅ HITL alert sent successfully!")
    else:
        print("❌ Failed to send HITL alert!")
    return success


def send_workflow(workflow_name: str, status: str, channel: Optional[str] = None, use_manager: bool = False):
    """Send a workflow notification."""
    print(f"🔄 Sending workflow notification: {workflow_name} - {status}")

    if use_manager:
        success = send_workflow_notification(workflow_name, status, channel=channel)
    else:
        success = send_webhook_workflow_notification(workflow_name, status, channel=channel)

    if success:
        print("✅ Workflow notification sent successfully!")
    else:
        print("❌ Failed to send workflow notification!")
    return success


def send_error(error_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False):
    """Send an error notification."""
    print(f"❌ Sending error notification: {error_message}")

    if use_manager:
        success = send_error_notification(error_message, context, channel=channel)
    else:
        success = send_webhook_error_notification(error_message, context, channel=channel)

    if success:
        print("✅ Error notification sent successfully!")
    else:
        print("❌ Failed to send error notification!")
    return success


def send_success(success_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False):
    """Send a success notification."""
    print(f"✅ Sending success notification: {success_message}")

    if use_manager:
        success = send_success_notification(success_message, context, channel=channel)
    else:
        success = send_webhook_success_notification(success_message, context, channel=channel)

    if success:
        print("✅ Success notification sent successfully!")
    else:
        print("❌ Failed to send success notification!")
    return success


def send_deployment(deployment_name: str, status: str, environment: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False):
    """Send a deployment notification."""
    print(f"🚀 Sending deployment notification: {deployment_name} - {status}")

    if use_manager:
        success = send_deployment_notification(deployment_name, status, environment, channel=channel)
    else:
        success = send_webhook_deployment_notification(deployment_name, status, environment, channel=channel)

    if success:
        print("✅ Deployment notification sent successfully!")
    else:
        print("❌ Failed to send deployment notification!")
    return success


def show_status():
    """Show webhook and notification system status."""
    print("📊 Webhook Status:")
    webhook_status = get_webhook_status()
    print(json.dumps(webhook_status, indent=2))

    print("\n📊 Notification Manager Status:")
    notification_status = get_notification_status()
    print(json.dumps(notification_status, indent=2))
    return True


def demo_all():
    """Run a complete demo of all webhook functionality."""
    print("🎭 Running complete webhook demo...")

    # Test connection
    test_webhook()
    print()

    # Send different types of notifications
    send_message("Hello from BMAD webhook demo!", channel="general")
    print()

    send_hitl("Deployment approval required", channel="alerts")
    print()

    send_workflow("feature-development", "started", channel="workflows")
    print()

    send_error("Database connection failed", "Production environment", channel="errors")
    print()

    send_success("User registration completed", "New user: john.doe@example.com", channel="success")
    print()

    send_deployment("frontend-app", "completed", "production", channel="deployments")
    print()

    print("🎉 Demo completed!")
    return True


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Webhook CLI Tool")
    parser.add_argument("command", choices=[
        "test", "test-manager", "message", "hitl", "workflow",
        "error", "success", "deployment", "status", "demo", "help"
    ], help="Command to execute")

    parser.add_argument("--message", "-m", help="Message to send")
    parser.add_argument("--channel", "-c", help="Channel to send to")
    parser.add_argument("--reason", "-r", help="Reason for HITL alert")
    parser.add_argument("--workflow", "-w", help="Workflow name")
    parser.add_argument("--status", "-s", help="Status (for workflow/deployment)")
    parser.add_argument("--context", help="Additional context")
    parser.add_argument("--environment", "-e", help="Environment (for deployment)")
    parser.add_argument("--use-manager", action="store_true", help="Use notification manager instead of direct webhook")

    args = parser.parse_args()

    if args.command == "help":
        print_help()
        return True
    elif args.command == "test":
        return test_webhook()
    elif args.command == "test-manager":
        return test_notification_manager()
    elif args.command == "message":
        if not args.message:
            print("❌ Error: --message is required for 'message' command")
            return False
        return send_message(args.message, args.channel, args.use_manager)
    elif args.command == "hitl":
        if not args.reason:
            print("❌ Error: --reason is required for 'hitl' command")
            return False
        return send_hitl(args.reason, args.channel, args.use_manager)
    elif args.command == "workflow":
        if not args.workflow or not args.status:
            print("❌ Error: --workflow and --status are required for 'workflow' command")
            return False
        return send_workflow(args.workflow, args.status, args.channel, args.use_manager)
    elif args.command == "error":
        if not args.message:
            print("❌ Error: --message is required for 'error' command")
            return False
        return send_error(args.message, args.context, args.channel, args.use_manager)
    elif args.command == "success":
        if not args.message:
            print("❌ Error: --message is required for 'success' command")
            return False
        return send_success(args.message, args.context, args.channel, args.use_manager)
    elif args.command == "deployment":
        if not args.workflow or not args.status:
            print("❌ Error: --workflow and --status are required for 'deployment' command")
            return False
        return send_deployment(args.workflow, args.status, args.environment, args.channel, args.use_manager)
    elif args.command == "status":
        return show_status()
    elif args.command == "demo":
        return demo_all()
    else:
        print(f"❌ Onbekend commando: {args.command}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
