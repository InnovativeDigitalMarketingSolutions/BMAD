"""
Webhook CLI Handlers

Business logic for webhook CLI commands.
"""

import json
import logging
from typing import Optional

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

logger = logging.getLogger(__name__)


class WebhookHandlers:
    """Handlers for webhook CLI commands."""
    
    def __init__(self):
        """Initialize webhook handlers."""
        pass
        
    def test_webhook(self) -> bool:
        """Test webhook connection."""
        print("🧪 Testing webhook connection...")
        success = test_webhook_connection()
        if success:
            print("✅ Webhook connection successful!")
        else:
            print("❌ Webhook connection failed!")
        return success

    def test_notification_manager(self) -> bool:
        """Test notification manager."""
        print("🧪 Testing notification manager...")
        success = test_notification_connection()
        if success:
            print("✅ Notification manager connection successful!")
        else:
            print("❌ Notification manager connection failed!")
        return success

    def send_message(self, message: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
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

    def send_hitl(self, reason: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
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

    def send_workflow(self, workflow_name: str, status: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
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

    def send_error(self, error_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
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

    def send_success(self, success_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
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

    def send_deployment(self, deployment_name: str, status: str, environment: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
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

    def show_status(self) -> bool:
        """Show webhook and notification system status."""
        print("📊 Webhook Status:")
        webhook_status = get_webhook_status()
        print(json.dumps(webhook_status, indent=2))

        print("\n📊 Notification Manager Status:")
        notification_status = get_notification_status()
        print(json.dumps(notification_status, indent=2))
        return True

    def demo_all(self) -> bool:
        """Run a complete demo of all webhook functionality."""
        print("🎭 Running complete webhook demo...")

        # Test connection
        self.test_webhook()
        print()

        # Send different types of notifications
        self.send_message("Hello from BMAD webhook demo!", channel="general")
        print()

        self.send_hitl("Deployment approval required", channel="alerts")
        print()

        self.send_workflow("feature-development", "started", channel="workflows")
        print()

        self.send_error("Database connection failed", "Production environment", channel="errors")
        print()

        self.send_success("User registration completed", "New user: john.doe@example.com", channel="success")
        print()

        self.send_deployment("frontend-app", "completed", "production", channel="deployments")
        print()

        print("🎉 Demo completed!")
        return True


# Legacy function exports for backward compatibility
def test_webhook() -> bool:
    """Test webhook connection."""
    handlers = WebhookHandlers()
    return handlers.test_webhook()


def test_notification_manager() -> bool:
    """Test notification manager."""
    handlers = WebhookHandlers()
    return handlers.test_notification_manager()


def send_message(message: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
    """Send a webhook message."""
    handlers = WebhookHandlers()
    return handlers.send_message(message, channel, use_manager)


def send_hitl(reason: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
    """Send a HITL alert."""
    handlers = WebhookHandlers()
    return handlers.send_hitl(reason, channel, use_manager)


def send_workflow(workflow_name: str, status: str, channel: Optional[str] = None, use_manager: bool = False) -> bool:
    """Send a workflow notification."""
    handlers = WebhookHandlers()
    return handlers.send_workflow(workflow_name, status, channel, use_manager)


def send_error(error_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
    """Send an error notification."""
    handlers = WebhookHandlers()
    return handlers.send_error(error_message, context, channel, use_manager)


def send_success(success_message: str, context: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
    """Send a success notification."""
    handlers = WebhookHandlers()
    return handlers.send_success(success_message, context, channel, use_manager)


def send_deployment(deployment_name: str, status: str, environment: Optional[str] = None, channel: Optional[str] = None, use_manager: bool = False) -> bool:
    """Send a deployment notification."""
    handlers = WebhookHandlers()
    return handlers.send_deployment(deployment_name, status, environment, channel, use_manager)


def show_status() -> bool:
    """Show webhook and notification system status."""
    handlers = WebhookHandlers()
    return handlers.show_status()


def demo_all() -> bool:
    """Run a complete demo of all webhook functionality."""
    handlers = WebhookHandlers()
    return handlers.demo_all() 