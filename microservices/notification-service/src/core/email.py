"""
Email service for the Notification Service.

This module handles email delivery through SendGrid and Mailgun providers.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

from ..models.schemas import NotificationStatus
from ..models.database import Notification, ChannelConfig
from .database import DatabaseService


class EmailService:
    """Email service for notification delivery."""
    
    def __init__(self, database_service: DatabaseService):
        """Initialize email service."""
        self.database_service = database_service
        self.sendgrid_client = None
        self.mailgun_api_key = None
        self.mailgun_domain = None
        self.default_from_email = "noreply@bmad.com"
        self.default_from_name = "BMAD System"
    
    async def initialize(self, sendgrid_api_key: str, mailgun_api_key: str, mailgun_domain: str):
        """Initialize email service with API keys."""
        if sendgrid_api_key and sendgrid_api_key != "your-sendgrid-api-key":
            self.sendgrid_client = SendGridAPIClient(api_key=sendgrid_api_key)
        
        if mailgun_api_key and mailgun_api_key != "your-mailgun-api-key":
            self.mailgun_api_key = mailgun_api_key
            self.mailgun_domain = mailgun_domain
    
    async def send_email(
        self,
        notification: Notification,
        subject: str,
        content: str,
        html_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email notification."""
        try:
            # Get channel configuration
            channel_config = await self.database_service.get_channel_config("email")
            if not channel_config or not channel_config.is_active:
                raise Exception("Email channel is not configured or inactive")
            
            # Update notification status to sent
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.SENT,
                sent_at=datetime.now(timezone.utc)
            )
            
            # Create delivery log
            await self.database_service.create_delivery_log(
                notification.id,
                "email",
                "sent"
            )
            
            # Send email based on provider preference
            config = channel_config.config
            provider = config.get("provider", "sendgrid")
            
            if provider == "sendgrid" and self.sendgrid_client:
                result = await self._send_via_sendgrid(
                    notification.recipient,
                    subject,
                    content,
                    html_content,
                    config
                )
            elif provider == "mailgun" and self.mailgun_api_key:
                result = await self._send_via_mailgun(
                    notification.recipient,
                    subject,
                    content,
                    html_content,
                    config
                )
            else:
                raise Exception(f"Email provider {provider} not configured")
            
            # Update notification status to delivered
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.DELIVERED,
                delivered_at=datetime.now(timezone.utc)
            )
            
            # Update delivery log
            await self.database_service.create_delivery_log(
                notification.id,
                "email",
                "delivered"
            )
            
            return {
                "success": True,
                "provider": provider,
                "message_id": result.get("message_id"),
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
                "email",
                "failed",
                error_message=str(e)
            )
            
            raise Exception(f"Failed to send email: {str(e)}")
    
    async def _send_via_sendgrid(
        self,
        recipient: str,
        subject: str,
        content: str,
        html_content: Optional[str],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email via SendGrid."""
        try:
            from_email = Email(config.get("from_email", self.default_from_email))
            to_email = To(recipient)
            
            if html_content:
                mail_content = HtmlContent(html_content)
            else:
                mail_content = Content("text/plain", content)
            
            mail = Mail(from_email, to_email, subject, mail_content)
            
            # Add custom headers if configured
            if "custom_headers" in config:
                for key, value in config["custom_headers"].items():
                    mail.add_header(key, value)
            
            response = self.sendgrid_client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                return {
                    "success": True,
                    "message_id": response.headers.get("X-Message-Id"),
                    "status_code": response.status_code
                }
            else:
                raise Exception(f"SendGrid API error: {response.status_code} - {response.body}")
                
        except Exception as e:
            raise Exception(f"SendGrid error: {str(e)}")
    
    async def _send_via_mailgun(
        self,
        recipient: str,
        subject: str,
        content: str,
        html_content: Optional[str],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email via Mailgun."""
        try:
            url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
            
            data = {
                "from": config.get("from_email", self.default_from_email),
                "to": recipient,
                "subject": subject,
                "text": content
            }
            
            if html_content:
                data["html"] = html_content
            
            # Add custom headers if configured
            if "custom_headers" in config:
                for key, value in config["custom_headers"].items():
                    data[f"h:{key}"] = value
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=("api", self.mailgun_api_key),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "message_id": result.get("id"),
                        "status_code": response.status_code
                    }
                else:
                    raise Exception(f"Mailgun API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Mailgun error: {str(e)}")
    
    async def send_bulk_email(
        self,
        notifications: List[Notification],
        subject: str,
        content: str,
        html_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send bulk email notifications."""
        results = {
            "total": len(notifications),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process emails in batches to avoid rate limiting
        batch_size = 50
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for notification in batch:
                task = self.send_email(notification, subject, content, html_content)
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
    
    async def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration."""
        try:
            # Check SendGrid configuration
            sendgrid_status = "not_configured"
            if self.sendgrid_client:
                try:
                    # Test with a simple API call
                    response = self.sendgrid_client.client.api_keys.get()
                    sendgrid_status = "configured" if response.status_code == 200 else "error"
                except Exception:
                    sendgrid_status = "error"
            
            # Check Mailgun configuration
            mailgun_status = "not_configured"
            if self.mailgun_api_key and self.mailgun_domain:
                try:
                    url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/stats"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            url,
                            auth=("api", self.mailgun_api_key),
                            timeout=10.0
                        )
                        mailgun_status = "configured" if response.status_code == 200 else "error"
                except Exception:
                    mailgun_status = "error"
            
            return {
                "sendgrid": sendgrid_status,
                "mailgun": mailgun_status,
                "default_from_email": self.default_from_email,
                "default_from_name": self.default_from_name
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "sendgrid": "error",
                "mailgun": "error"
            }
    
    async def get_email_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get email delivery analytics."""
        try:
            # Get delivery logs for email channel
            delivery_logs, total = await self.database_service.get_delivery_logs(
                channel="email"
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
            raise Exception(f"Failed to get email analytics: {str(e)}") 