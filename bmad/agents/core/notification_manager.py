"""
Notification Manager - Unified interface for Slack and Webhook notifications.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

# Import notification systems
try:
    from .slack_notify import send_slack_message, send_human_in_loop_alert
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

try:
    from .webhook_notify import send_webhook_message, send_webhook_hitl_alert, send_webhook_workflow_notification
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
            elif os.getenv("SLACK_WEBHOOK_URL") and SLACK_AVAILABLE:
                return NotificationType.SLACK
            else:
                # Default to webhook if available
                return NotificationType.WEBHOOK if WEBHOOK_AVAILABLE else NotificationType.SLACK
        else:
            return self.default_type
    
    def send_message(self, text: str, channel: Optional[str] = None, 
                    use_api: bool = False, **kwargs) -> bool:
        """Send a message using the configured notification system."""
        try:
            if self.notification_type == NotificationType.WEBHOOK:
                return send_webhook_message(text, channel=channel, **kwargs)
            elif self.notification_type == NotificationType.SLACK:
                return send_slack_message(text, channel=channel, use_api=use_api, **kwargs)
            else:
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
            elif self.notification_type == NotificationType.SLACK:
                return send_human_in_loop_alert(reason, channel=channel, use_api=use_api, **kwargs)
            else:
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
            elif self.notification_type == NotificationType.SLACK:
                # For Slack, use regular message with workflow formatting
                text = f"🔄 **Workflow Update**: {workflow_name} - {status}"
                return send_slack_message(text, channel=channel, use_api=False, **kwargs)
            else:
                logger.error(f"Unknown notification type: {self.notification_type}")
                return False
        except Exception as e:
            logger.error(f"Failed to send workflow notification: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the notification system."""
        return {
            "type": self.notification_type.value,
            "slack_available": SLACK_AVAILABLE,
            "webhook_available": WEBHOOK_AVAILABLE,
            "slack_configured": bool(os.getenv("SLACK_WEBHOOK_URL") or os.getenv("SLACK_BOT_TOKEN")),
            "webhook_configured": bool(os.getenv("WEBHOOK_URL")),
            "default_type": self.default_type.value
        }

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