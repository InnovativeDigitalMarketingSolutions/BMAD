"""
Notification Manager - Unified interface for Slack and Webhook notifications.
"""

import logging
import os
from enum import Enum
from typing import Any, Dict, Optional

# Import notification systems
try:
    from .slack_notify import send_human_in_loop_alert, send_slack_message
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from .webhook_notify import (
        get_webhook_status,
        send_webhook_deployment_notification,
        send_webhook_error_notification,
        send_webhook_hitl_alert,
        send_webhook_message,
        send_webhook_success_notification,
        send_webhook_workflow_notification,
        test_webhook_connection,
    )
    WEBHOOK_AVAILABLE = True
except ImportError:
    WEBHOOK_AVAILABLE = False

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications."""
    SLACK = "slack"
    WEBHOOK = "webhook"
    AUTO = "auto"  # Automatically choose best available

class NotificationManager:
    """Unified notification manager supporting both Slack and Webhook."""

    def __init__(self, default_type: NotificationType = NotificationType.AUTO):
        self.default_type = default_type
        self.notification_type = self._determine_notification_type()

    def _determine_notification_type(self) -> NotificationType:
        """Determine which notification type to use."""
        if self.default_type == NotificationType.AUTO:
            # Check environment variables
            if os.getenv("WEBHOOK_URL") and WEBHOOK_AVAILABLE:
                return NotificationType.WEBHOOK
            if os.getenv("SLACK_WEBHOOK_URL") and SLACK_AVAILABLE:
                return NotificationType.SLACK
            # Default to webhook if available
            return NotificationType.WEBHOOK if WEBHOOK_AVAILABLE else NotificationType.SLACK
        return self.default_type

    def send_message(self, text: str, channel: Optional[str] = None,
                    use_api: bool = False, **kwargs) -> bool:
        """Send a message using the configured notification system."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_message(text, channel=channel, **kwargs)
            if self.notification_type == NotificationType.SLACK:
                return send_slack_message(text, channel=channel, use_api=use_api, **kwargs)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def send_hitl_alert(self, reason: str, channel: Optional[str] = None,
                       use_api: bool = False, **kwargs) -> bool:
        """Send a Human-in-the-Loop alert."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_hitl_alert(reason, channel=channel, **kwargs)
            if self.notification_type == NotificationType.SLACK:
                return send_human_in_loop_alert(reason, channel=channel, use_api=use_api, **kwargs)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to send HITL alert: {e}")
            return False

    def send_workflow_notification(self, workflow_name: str, status: str,
                                 channel: Optional[str] = None, **kwargs) -> bool:
        """Send a workflow status notification."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_workflow_notification(workflow_name, status, channel, **kwargs)
            if self.notification_type == NotificationType.SLACK:
                # For Slack, use regular message with workflow formatting
                text = f"🔄 **Workflow Update**: {workflow_name} - {status}"
                return send_slack_message(text, channel=channel, use_api=False, **kwargs)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to send workflow notification: {e}")
            return False

    def send_error_notification(self, error_message: str, context: Optional[str] = None,
                               channel: Optional[str] = None, **kwargs) -> bool:
        """Send an error notification."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_error_notification(error_message, context, channel, **kwargs)
            if self.notification_type == NotificationType.SLACK:
                # For Slack, use regular message with error formatting
                text = f"❌ **Error**: {error_message}"
                if context:
                    text += f"\n**Context**: {context}"
                return send_slack_message(text, channel=channel, use_api=False, **kwargs)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            return False

    def send_success_notification(self, success_message: str, context: Optional[str] = None,
                                 channel: Optional[str] = None, **kwargs) -> bool:
        """Send a success notification."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_success_notification(success_message, context, channel, **kwargs)
            if self.notification_type == NotificationType.SLACK:
                # For Slack, use regular message with success formatting
                text = f"✅ **Success**: {success_message}"
                if context:
                    text += f"\n**Context**: {context}"
                return send_slack_message(text, channel=channel, use_api=False, **kwargs)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to send success notification: {e}")
            return False

    def send_deployment_notification(self, deployment_name: str, status: str,
                                   environment: Optional[str] = None,
                                   channel: Optional[str] = None, **kwargs) -> bool:
        """Send a deployment notification."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_deployment_notification(deployment_name, status, environment, channel, **kwargs)
            if self.notification_type == NotificationType.SLACK:
                # For Slack, use regular message with deployment formatting
                status_emoji = {
                    "started": "🚀",
                    "completed": "✅",
                    "failed": "❌",
                    "rolled_back": "🔄"
                }.get(status, "ℹ️")
                text = f"{status_emoji} **Deployment**: {deployment_name} - {status}"
                if environment:
                    text += f"\n**Environment**: {environment}"
                return send_slack_message(text, channel=channel, use_api=False, **kwargs)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to send deployment notification: {e}")
            return False

    def test_connection(self, channel: Optional[str] = None) -> bool:
        """Test the notification system connection."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return test_webhook_connection(channel)
            if self.notification_type == NotificationType.SLACK:
                # For Slack, send a test message
                return send_slack_message("🧪 Test message from BMAD", channel=channel, use_api=False)
            logger.error(f"Unknown notification type: {self.notification_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to test connection: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get the status of the notification system."""
        status = {
            "type": self.notification_type.value,
            "slack_available": SLACK_AVAILABLE,
            "webhook_available": WEBHOOK_AVAILABLE,
            "slack_configured": bool(os.getenv("SLACK_WEBHOOK_URL") or os.getenv("SLACK_BOT_TOKEN")),
            "webhook_configured": bool(os.getenv("WEBHOOK_URL")),
            "default_type": self.default_type.value
        }

        # Add webhook-specific status if available
        if WEBHOOK_AVAILABLE:
            try:
                webhook_status = get_webhook_status()
                status["webhook_details"] = webhook_status
            except Exception as e:
                status["webhook_details"] = {"error": str(e)}

        return status

# Global notification manager instance
_notification_manager = None

def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager

def send_notification(text: str, channel: Optional[str] = None,
                     notification_type: Optional[NotificationType] = None, **kwargs) -> bool:
    """Send a notification using the global manager."""
    if notification_type:
        # Create temporary manager with specific type
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.send_message(text, channel=channel, **kwargs)

def send_hitl_notification(reason: str, channel: Optional[str] = None,
                          notification_type: Optional[NotificationType] = None, **kwargs) -> bool:
    """Send a HITL notification using the global manager."""
    if notification_type:
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.send_hitl_alert(reason, channel=channel, **kwargs)

def send_workflow_notification(workflow_name: str, status: str, channel: Optional[str] = None,
                              notification_type: Optional[NotificationType] = None, **kwargs) -> bool:
    """Send a workflow notification using the global manager."""
    if notification_type:
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.send_workflow_notification(workflow_name, status, channel=channel, **kwargs)

def send_error_notification(error_message: str, context: Optional[str] = None,
                           channel: Optional[str] = None,
                           notification_type: Optional[NotificationType] = None, **kwargs) -> bool:
    """Send an error notification using the global manager."""
    if notification_type:
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.send_error_notification(error_message, context, channel=channel, **kwargs)

def send_success_notification(success_message: str, context: Optional[str] = None,
                             channel: Optional[str] = None,
                             notification_type: Optional[NotificationType] = None, **kwargs) -> bool:
    """Send a success notification using the global manager."""
    if notification_type:
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.send_success_notification(success_message, context, channel=channel, **kwargs)

def send_deployment_notification(deployment_name: str, status: str,
                                environment: Optional[str] = None,
                                channel: Optional[str] = None,
                                notification_type: Optional[NotificationType] = None, **kwargs) -> bool:
    """Send a deployment notification using the global manager."""
    if notification_type:
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.send_deployment_notification(deployment_name, status, environment, channel=channel, **kwargs)

def test_notification_connection(channel: Optional[str] = None,
                                notification_type: Optional[NotificationType] = None) -> bool:
    """Test notification connection using the global manager."""
    if notification_type:
        manager = NotificationManager(notification_type)
    else:
        manager = get_notification_manager()

    return manager.test_connection(channel)

def get_notification_status() -> Dict[str, Any]:
    """Get notification system status using the global manager."""
    manager = get_notification_manager()
    return manager.get_status()

# Add missing functions that tests expect
def send_webhook_message(text: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a webhook message directly."""
    try:
        if WEBHOOK_AVAILABLE:
            from .webhook_notify import send_webhook_message as _send_webhook_message
            return _send_webhook_message(text, channel=channel, **kwargs)
        logger.error("Webhook notifications not available")
        return False
    except Exception as e:
        logger.error(f"Failed to send webhook message: {e}")
        return False

def send_slack_message(text: str, channel: Optional[str] = None, use_api: bool = False, **kwargs) -> bool:
    """Send a Slack message directly."""
    try:
        if SLACK_AVAILABLE:
            from .slack_notify import send_slack_message as _send_slack_message
            return _send_slack_message(text, channel=channel, use_api=use_api, **kwargs)
        logger.error("Slack notifications not available")
        return False
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")
        return False

def send_webhook_hitl_alert(reason: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a webhook HITL alert directly."""
    try:
        if WEBHOOK_AVAILABLE:
            from .webhook_notify import send_webhook_hitl_alert as _send_webhook_hitl_alert
            return _send_webhook_hitl_alert(reason, channel=channel, **kwargs)
        logger.error("Webhook notifications not available")
        return False
    except Exception as e:
        logger.error(f"Failed to send webhook HITL alert: {e}")
        return False

def send_human_in_loop_alert(reason: str, channel: Optional[str] = None, use_api: bool = False, **kwargs) -> bool:
    """Send a human-in-the-loop alert directly."""
    try:
        if SLACK_AVAILABLE:
            from .slack_notify import send_human_in_loop_alert as _send_human_in_loop_alert
            return _send_human_in_loop_alert(reason, channel=channel, use_api=use_api, **kwargs)
        logger.error("Slack notifications not available")
        return False
    except Exception as e:
        logger.error(f"Failed to send human-in-loop alert: {e}")
        return False

def send_webhook_workflow_notification(workflow_name: str, status: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a webhook workflow notification directly."""
    try:
        if WEBHOOK_AVAILABLE:
            from .webhook_notify import send_webhook_workflow_notification as _send_webhook_workflow_notification
            return _send_webhook_workflow_notification(workflow_name, status, channel, **kwargs)
        logger.error("Webhook notifications not available")
        return False
    except Exception as e:
        logger.error(f"Failed to send webhook workflow notification: {e}")
        return False
