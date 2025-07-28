"""
Webhook-based notification system as an alternative to Slack.
Supports multiple webhook endpoints and provides similar functionality.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookNotifier:
    """Webhook-based notification system."""

    def __init__(self):
        self.webhook_urls = self._load_webhook_config()
        self.default_channel = os.getenv("WEBHOOK_DEFAULT_CHANNEL", "general")

    def _load_webhook_config(self) -> Dict[str, str]:
        """Load webhook configuration from environment variables."""
        config = {}

        # Load from environment variables
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            config["default"] = webhook_url

        # Load channel-specific webhooks
        for key, value in os.environ.items():
            if key.startswith("WEBHOOK_URL_"):
                channel = key.replace("WEBHOOK_URL_", "").lower()
                config[channel] = value

        return config

    def send_webhook_message(self, message: str, channel: Optional[str] = None,
                           use_api: bool = True, attachments: Optional[List[Dict]] = None,
                           **kwargs) -> bool:
        """
        Send a message via webhook.
        
        Args:
            message: The message to send
            channel: Channel name (optional)
            use_api: Whether to actually send (for testing)
            attachments: List of attachment objects
            **kwargs: Additional webhook payload data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not use_api:
            logger.info(f"[WEBHOOK] Message (not sent): {message}")
            return True

        if not self.webhook_urls:
            logger.warning("[WEBHOOK] No webhook URLs configured")
            return False

        # Determine webhook URL
        webhook_url = None
        if channel and channel in self.webhook_urls:
            webhook_url = self.webhook_urls[channel]
        elif "default" in self.webhook_urls:
            webhook_url = self.webhook_urls["default"]
        else:
            logger.error(f"[WEBHOOK] No webhook URL found for channel: {channel}")
            return False

        # Prepare payload
        payload = {
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "channel": channel or self.default_channel,
            "source": "BMAD",
            **kwargs
        }

        # Add attachments if provided
        if attachments:
            payload["attachments"] = attachments

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"[WEBHOOK] Message sent successfully to {channel}")
            return True

        except Exception as e:
            logger.error(f"[WEBHOOK] Failed to send message: {e}")
            return False

    def send_message(self, message: str, channel: Optional[str] = None,
                    use_api: bool = True, **kwargs) -> bool:
        """Alias for send_webhook_message for compatibility."""
        return self.send_webhook_message(message, channel, use_api, **kwargs)

    def send_human_in_loop_alert(self, reason: str, channel: Optional[str] = None,
                                user_mention: Optional[str] = None,
                                alert_id: Optional[str] = None,
                                use_api: bool = True) -> bool:
        """
        Send a Human-in-the-Loop alert.
        
        Args:
            reason: Reason for the HITL alert
            channel: Channel to send to
            user_mention: User to mention
            alert_id: Unique alert ID
            use_api: Whether to actually send
            
        Returns:
            bool: True if successful
        """
        message = "🚨 **Human-in-the-Loop Alert**\n"
        message += f"**Reason:** {reason}\n"
        if user_mention:
            message += f"**User:** {user_mention}\n"
        if alert_id:
            message += f"**Alert ID:** {alert_id}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "\nPlease review and approve/reject this action."

        return self.send_webhook_message(
            message,
            channel=channel,
            use_api=use_api,
            alert_type="hitl",
            alert_id=alert_id
        )

    def send_webhook_hitl_alert(self, reason: str, channel: Optional[str] = None,
                               user_mention: Optional[str] = None,
                               alert_id: Optional[str] = None,
                               use_api: bool = True) -> bool:
        """Alias for send_human_in_loop_alert for consistency."""
        return self.send_human_in_loop_alert(reason, channel, user_mention, alert_id, use_api)

    def send_workflow_notification(self, workflow_name: str, status: str,
                                 channel: Optional[str] = None,
                                 use_api: bool = True) -> bool:
        """
        Send workflow status notification.
        
        Args:
            workflow_name: Name of the workflow
            status: Current status
            channel: Channel to send to
            use_api: Whether to actually send
            
        Returns:
            bool: True if successful
        """
        status_emoji = {
            "started": "🚀",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
            "resumed": "▶️"
        }.get(status, "ℹ️")

        message = f"{status_emoji} **Workflow Update**\n"
        message += f"**Workflow:** {workflow_name}\n"
        message += f"**Status:** {status}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_webhook_message(
            message,
            channel=channel,
            use_api=use_api,
            notification_type="workflow",
            workflow_name=workflow_name,
            status=status
        )

    def send_webhook_workflow_notification(self, workflow_name: str, status: str,
                                         channel: Optional[str] = None,
                                         use_api: bool = True) -> bool:
        """Alias for send_workflow_notification for consistency."""
        return self.send_workflow_notification(workflow_name, status, channel, use_api)

    def send_error_notification(self, error_message: str, context: Optional[str] = None,
                               channel: Optional[str] = None, use_api: bool = True) -> bool:
        """
        Send an error notification.
        
        Args:
            error_message: The error message
            context: Additional context about the error
            channel: Channel to send to
            use_api: Whether to actually send
            
        Returns:
            bool: True if successful
        """
        message = "❌ **Error Notification**\n"
        message += f"**Error:** {error_message}\n"
        if context:
            message += f"**Context:** {context}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_webhook_message(
            message,
            channel=channel,
            use_api=use_api,
            notification_type="error"
        )

    def send_success_notification(self, success_message: str, context: Optional[str] = None,
                                 channel: Optional[str] = None, use_api: bool = True) -> bool:
        """
        Send a success notification.
        
        Args:
            success_message: The success message
            context: Additional context about the success
            channel: Channel to send to
            use_api: Whether to actually send
            
        Returns:
            bool: True if successful
        """
        message = "✅ **Success Notification**\n"
        message += f"**Message:** {success_message}\n"
        if context:
            message += f"**Context:** {context}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_webhook_message(
            message,
            channel=channel,
            use_api=use_api,
            notification_type="success"
        )

    def send_deployment_notification(self, deployment_name: str, status: str,
                                   environment: Optional[str] = None,
                                   channel: Optional[str] = None, use_api: bool = True) -> bool:
        """
        Send a deployment notification.
        
        Args:
            deployment_name: Name of the deployment
            status: Deployment status
            environment: Environment name
            channel: Channel to send to
            use_api: Whether to actually send
            
        Returns:
            bool: True if successful
        """
        status_emoji = {
            "started": "🚀",
            "completed": "✅",
            "failed": "❌",
            "rolled_back": "🔄"
        }.get(status, "ℹ️")

        message = f"{status_emoji} **Deployment Update**\n"
        message += f"**Deployment:** {deployment_name}\n"
        message += f"**Status:** {status}\n"
        if environment:
            message += f"**Environment:** {environment}\n"
        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_webhook_message(
            message,
            channel=channel,
            use_api=use_api,
            notification_type="deployment",
            deployment_name=deployment_name,
            status=status,
            environment=environment
        )

    def test_connection(self, channel: Optional[str] = None) -> bool:
        """
        Test webhook connection.
        
        Args:
            channel: Channel to test (optional)
            
        Returns:
            bool: True if connection successful
        """
        test_message = f"🧪 **Webhook Test**\nThis is a test message from BMAD.\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_webhook_message(
            test_message,
            channel=channel,
            use_api=True,
            notification_type="test"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get the status of the webhook system."""
        return {
            "webhook_urls": list(self.webhook_urls.keys()),
            "default_channel": self.default_channel,
            "configured": len(self.webhook_urls) > 0,
            "available_channels": list(self.webhook_urls.keys())
        }

# Global instance
webhook_notifier = WebhookNotifier()

# Convenience functions (similar to Slack interface)
def send_webhook_message(message: str, channel: Optional[str] = None,
                        use_api: bool = True, **kwargs) -> bool:
    """Send a webhook message."""
    return webhook_notifier.send_webhook_message(message, channel, use_api, **kwargs)

def send_webhook_hitl_alert(reason: str, channel: Optional[str] = None,
                           user_mention: Optional[str] = None,
                           alert_id: Optional[str] = None,
                           use_api: bool = True) -> bool:
    """Send a webhook HITL alert."""
    return webhook_notifier.send_webhook_hitl_alert(
        reason, channel, user_mention, alert_id, use_api
    )

def send_webhook_workflow_notification(workflow_name: str, status: str,
                                     channel: Optional[str] = None,
                                     use_api: bool = True) -> bool:
    """Send a webhook workflow notification."""
    return webhook_notifier.send_webhook_workflow_notification(
        workflow_name, status, channel, use_api
    )

def send_webhook_error_notification(error_message: str, context: Optional[str] = None,
                                   channel: Optional[str] = None, use_api: bool = True) -> bool:
    """Send a webhook error notification."""
    return webhook_notifier.send_error_notification(
        error_message, context, channel, use_api
    )

def send_webhook_success_notification(success_message: str, context: Optional[str] = None,
                                     channel: Optional[str] = None, use_api: bool = True) -> bool:
    """Send a webhook success notification."""
    return webhook_notifier.send_success_notification(
        success_message, context, channel, use_api
    )

def send_webhook_deployment_notification(deployment_name: str, status: str,
                                        environment: Optional[str] = None,
                                        channel: Optional[str] = None, use_api: bool = True) -> bool:
    """Send a webhook deployment notification."""
    return webhook_notifier.send_deployment_notification(
        deployment_name, status, environment, channel, use_api
    )

def test_webhook_connection(channel: Optional[str] = None) -> bool:
    """Test webhook connection."""
    return webhook_notifier.test_connection(channel)

def get_webhook_status() -> Dict[str, Any]:
    """Get webhook system status."""
    return webhook_notifier.get_status()
