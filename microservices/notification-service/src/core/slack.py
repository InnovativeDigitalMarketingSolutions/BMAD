"""
Slack service for the Notification Service.

This module handles Slack notifications through webhook integration.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
import json

from ..models.schemas import NotificationStatus
from ..models.database import Notification, ChannelConfig
from .database import DatabaseService


class SlackService:
    """Slack service for notification delivery."""
    
    def __init__(self, database_service: DatabaseService):
        """Initialize Slack service."""
        self.database_service = database_service
        self.default_webhook_url = None
        self.default_channel = "#general"
        self.default_username = "BMAD Bot"
        self.default_icon_emoji = ":robot_face:"
    
    async def initialize(self, slack_webhook_url: str):
        """Initialize Slack service with webhook URL."""
        if slack_webhook_url and slack_webhook_url != "your-slack-webhook-url":
            self.default_webhook_url = slack_webhook_url
    
    async def send_slack_message(
        self,
        notification: Notification,
        content: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send Slack notification."""
        try:
            # Get channel configuration
            channel_config = await self.database_service.get_channel_config("slack")
            if not channel_config or not channel_config.is_active:
                raise Exception("Slack channel is not configured or inactive")
            
            # Update notification status to sent
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.SENT,
                sent_at=datetime.now(timezone.utc)
            )
            
            # Create delivery log
            await self.database_service.create_delivery_log(
                notification.id,
                "slack",
                "sent"
            )
            
            # Send Slack message
            config = channel_config.config
            webhook_url = config.get("webhook_url", self.default_webhook_url)
            
            if not webhook_url:
                raise Exception("Slack webhook URL not configured")
            
            result = await self._send_via_webhook(
                webhook_url,
                content,
                channel or config.get("default_channel", self.default_channel),
                username or config.get("username", self.default_username),
                icon_emoji or config.get("icon_emoji", self.default_icon_emoji),
                attachments
            )
            
            # Update notification status to delivered
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.DELIVERED,
                delivered_at=datetime.now(timezone.utc)
            )
            
            # Update delivery log
            await self.database_service.create_delivery_log(
                notification.id,
                "slack",
                "delivered"
            )
            
            return {
                "success": True,
                "provider": "slack",
                "channel": channel,
                "delivered_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            # Update notification status to failed
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.FAILED
            )
            
            # Create delivery log for failure
            await self.database_service.create_delivery_log(
                notification.id,
                "slack",
                "failed",
                error_message=str(e)
            )
            
            raise Exception(f"Failed to send Slack message: {str(e)}")
    
    async def _send_via_webhook(
        self,
        webhook_url: str,
        text: str,
        channel: str,
        username: str,
        icon_emoji: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send message via Slack webhook."""
        try:
            payload = {
                "text": text,
                "channel": channel,
                "username": username,
                "icon_emoji": icon_emoji
            }
            
            if attachments:
                payload["attachments"] = attachments
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "response": response.text
                    }
                else:
                    raise Exception(f"Slack webhook error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            raise Exception("Slack webhook request timed out")
        except httpx.RequestError as e:
            raise Exception(f"Slack webhook request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Slack message delivery error: {str(e)}")
    
    async def send_bulk_slack_messages(
        self,
        notifications: List[Notification],
        content: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send bulk Slack notifications."""
        results = {
            "total": len(notifications),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process Slack messages in batches
        batch_size = 20  # Slack has rate limits
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for notification in batch:
                task = self.send_slack_message(
                    notification,
                    content,
                    channel,
                    username,
                    icon_emoji
                )
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append(str(result))
                else:
                    results["successful"] += 1
            
            # Rate limiting delay between batches
            if i + batch_size < len(notifications):
                await asyncio.sleep(1)
        
        return results
    
    async def create_slack_attachment(
        self,
        title: str,
        text: str,
        color: str = "good",
        fields: Optional[List[Dict[str, str]]] = None,
        footer: Optional[str] = None,
        footer_icon: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a Slack attachment."""
        attachment = {
            "title": title,
            "text": text,
            "color": color
        }
        
        if fields:
            attachment["fields"] = fields
        
        if footer:
            attachment["footer"] = footer
        
        if footer_icon:
            attachment["footer_icon"] = footer_icon
        
        if timestamp:
            attachment["ts"] = int(timestamp.timestamp())
        
        return attachment
    
    async def send_notification_with_attachment(
        self,
        notification: Notification,
        title: str,
        text: str,
        color: str = "good",
        fields: Optional[List[Dict[str, str]]] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send Slack notification with rich attachment."""
        attachment = await self.create_slack_attachment(
            title=title,
            text=text,
            color=color,
            fields=fields,
            footer="BMAD System",
            footer_icon=":robot_face:",
            timestamp=datetime.now(timezone.utc)
        )
        
        return await self.send_slack_message(
            notification,
            "",  # Empty text since we're using attachment
            channel=channel,
            attachments=[attachment]
        )
    
    async def test_slack_configuration(self) -> Dict[str, Any]:
        """Test Slack configuration."""
        try:
            if not self.default_webhook_url:
                return {
                    "slack": "not_configured",
                    "default_channel": self.default_channel,
                    "default_username": self.default_username
                }
            
            # Test webhook with a simple message
            test_payload = {
                "text": "🧪 BMAD Notification Service test message",
                "channel": self.default_channel,
                "username": self.default_username,
                "icon_emoji": self.default_icon_emoji
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.default_webhook_url,
                    json=test_payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        "slack": "configured",
                        "default_channel": self.default_channel,
                        "default_username": self.default_username,
                        "test_message": "sent"
                    }
                else:
                    return {
                        "slack": "error",
                        "error": f"Webhook test failed: {response.status_code}",
                        "default_channel": self.default_channel,
                        "default_username": self.default_username
                    }
                    
        except Exception as e:
            return {
                "slack": "error",
                "error": str(e),
                "default_channel": self.default_channel,
                "default_username": self.default_username
            }
    
    async def get_slack_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get Slack delivery analytics."""
        try:
            # Get delivery logs for Slack channel
            delivery_logs, total = await self.database_service.get_delivery_logs(
                channel="slack"
            )
            
            # Filter by date range if provided
            if start_date or end_date:
                filtered_logs = []
                for log in delivery_logs:
                    if start_date and log.created_at < start_date:
                        continue
                    if end_date and log.created_at > end_date:
                        continue
                    filtered_logs.append(log)
                delivery_logs = filtered_logs
            
            # Calculate statistics
            total_sent = len(delivery_logs)
            successful = sum(1 for log in delivery_logs if log.status == "delivered")
            failed = sum(1 for log in delivery_logs if log.status == "failed")
            
            success_rate = (successful / total_sent * 100) if total_sent > 0 else 0
            
            return {
                "total_sent": total_sent,
                "successful": successful,
                "failed": failed,
                "success_rate": round(success_rate, 2),
                "start_date": start_date,
                "end_date": end_date
            }
            
        except Exception as e:
            raise Exception(f"Failed to get Slack analytics: {str(e)}")
    
    async def send_alert_notification(
        self,
        notification: Notification,
        alert_type: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send alert notification with appropriate formatting."""
        # Map severity to colors
        color_map = {
            "info": "#36a64f",      # Green
            "warning": "#ffa500",   # Orange
            "error": "#ff0000",     # Red
            "critical": "#8b0000"   # Dark red
        }
        
        color = color_map.get(severity, "#36a64f")
        
        # Create fields for metadata
        fields = []
        if metadata:
            for key, value in metadata.items():
                fields.append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })
        
        # Create attachment
        attachment = await self.create_slack_attachment(
            title=f"🚨 {alert_type.upper()} Alert",
            text=message,
            color=color,
            fields=fields,
            footer="BMAD Alert System",
            footer_icon=":warning:",
            timestamp=datetime.now(timezone.utc)
        )
        
        return await self.send_slack_message(
            notification,
            "",  # Empty text since we're using attachment
            attachments=[attachment]
        ) 