"""
Webhook service for the Notification Service.

This module handles HTTP webhook delivery to external services.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
import json
import hashlib
import hmac

from ..models.schemas import NotificationStatus
from ..models.database import Notification, ChannelConfig
from .database import DatabaseService


class WebhookService:
    """Webhook service for notification delivery."""
    
    def __init__(self, database_service: DatabaseService):
        """Initialize webhook service."""
        self.database_service = database_service
        self.default_timeout = 30
        self.default_retry_attempts = 3
        self.default_retry_delay = 5
    
    async def send_webhook(
        self,
        notification: Notification,
        webhook_url: str,
        payload: Dict[str, Any],
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_attempts: Optional[int] = None,
        secret_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send webhook notification."""
        try:
            # Get channel configuration
            channel_config = await self.database_service.get_channel_config("webhook")
            if not channel_config or not channel_config.is_active:
                raise Exception("Webhook channel is not configured or inactive")
            
            # Update notification status to sent
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.SENT,
                sent_at=datetime.now(timezone.utc)
            )
            
            # Create delivery log
            await self.database_service.create_delivery_log(
                notification.id,
                "webhook",
                "sent"
            )
            
            # Send webhook
            config = channel_config.config
            timeout = timeout or config.get("timeout", self.default_timeout)
            retry_attempts = retry_attempts or config.get("retry_attempts", self.default_retry_attempts)
            
            result = await self._send_webhook_request(
                webhook_url,
                payload,
                method,
                headers,
                timeout,
                retry_attempts,
                secret_key
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
                "webhook",
                "delivered"
            )
            
            return {
                "success": True,
                "provider": "webhook",
                "url": webhook_url,
                "status_code": result.get("status_code"),
                "response": result.get("response"),
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
                "webhook",
                "failed",
                error_message=str(e)
            )
            
            raise Exception(f"Failed to send webhook: {str(e)}")
    
    async def _send_webhook_request(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        secret_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send webhook request with retry logic."""
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "BMAD-Notification-Service/1.0"
        }
        
        if headers:
            default_headers.update(headers)
        
        # Add signature if secret key is provided
        if secret_key:
            signature = self._generate_signature(payload, secret_key)
            default_headers["X-BMAD-Signature"] = signature
        
        # Prepare request data
        request_data = {
            "url": webhook_url,
            "method": method.upper(),
            "headers": default_headers,
            "timeout": timeout
        }
        
        if method.upper() == "GET":
            request_data["params"] = payload
        else:
            request_data["json"] = payload
        
        # Retry logic
        last_exception = None
        for attempt in range(retry_attempts):
            try:
                async with httpx.AsyncClient() as client:
                    if method.upper() == "GET":
                        response = await client.get(**request_data)
                    elif method.upper() == "POST":
                        response = await client.post(**request_data)
                    elif method.upper() == "PUT":
                        response = await client.put(**request_data)
                    elif method.upper() == "PATCH":
                        response = await client.patch(**request_data)
                    else:
                        raise Exception(f"Unsupported HTTP method: {method}")
                    
                    # Check if response is successful (2xx status codes)
                    if 200 <= response.status_code < 300:
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "response": response.text,
                            "headers": dict(response.headers)
                        }
                    else:
                        raise Exception(f"HTTP {response.status_code}: {response.text}")
                        
            except httpx.TimeoutException:
                last_exception = Exception(f"Webhook request timed out (attempt {attempt + 1})")
            except httpx.RequestError as e:
                last_exception = Exception(f"Webhook request error (attempt {attempt + 1}): {str(e)}")
            except Exception as e:
                last_exception = e
            
            # Wait before retry (exponential backoff)
            if attempt < retry_attempts - 1:
                delay = (2 ** attempt) * self.default_retry_delay
                await asyncio.sleep(delay)
        
        # All retries failed
        raise last_exception or Exception("Webhook request failed after all retries")
    
    def _generate_signature(self, payload: Dict[str, Any], secret_key: str) -> str:
        """Generate HMAC signature for webhook payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def send_bulk_webhooks(
        self,
        notifications: List[Notification],
        webhook_url: str,
        payload_template: Dict[str, Any],
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send bulk webhook notifications."""
        results = {
            "total": len(notifications),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process webhooks in batches
        batch_size = 50
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for notification in batch:
                # Customize payload for each notification
                payload = payload_template.copy()
                payload.update({
                    "notification_id": notification.id,
                    "recipient": notification.recipient,
                    "content": notification.content,
                    "channel": notification.channel,
                    "created_at": notification.created_at.isoformat(),
                    "metadata": notification.metadata
                })
                
                task = self.send_webhook(
                    notification,
                    webhook_url,
                    payload,
                    method,
                    headers
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
    
    async def test_webhook_endpoint(
        self,
        webhook_url: str,
        test_payload: Optional[Dict[str, Any]] = None,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """Test webhook endpoint connectivity and response."""
        try:
            if not test_payload:
                test_payload = {
                    "test": True,
                    "message": "BMAD Notification Service webhook test",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            default_headers = {
                "Content-Type": "application/json",
                "User-Agent": "BMAD-Notification-Service/1.0"
            }
            
            if headers:
                default_headers.update(headers)
            
            request_data = {
                "url": webhook_url,
                "method": method.upper(),
                "headers": default_headers,
                "timeout": timeout
            }
            
            if method.upper() == "GET":
                request_data["params"] = test_payload
            else:
                request_data["json"] = test_payload
            
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(**request_data)
                elif method.upper() == "POST":
                    response = await client.post(**request_data)
                else:
                    raise Exception(f"Unsupported HTTP method: {method}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.text,
                    "response_time": response.elapsed.total_seconds(),
                    "headers": dict(response.headers)
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Webhook endpoint timed out",
                "url": webhook_url
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Webhook request error: {str(e)}",
                "url": webhook_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": webhook_url
            }
    
    async def get_webhook_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get webhook delivery analytics."""
        try:
            # Get delivery logs for webhook channel
            delivery_logs, total = await self.database_service.get_delivery_logs(
                channel="webhook"
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
            raise Exception(f"Failed to get webhook analytics: {str(e)}")
    
    async def create_webhook_payload(
        self,
        notification: Notification,
        event_type: str = "notification",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Create standardized webhook payload."""
        payload = {
            "event_type": event_type,
            "notification_id": notification.id,
            "recipient": notification.recipient,
            "content": notification.content,
            "channel": notification.channel,
            "status": notification.status,
            "created_at": notification.created_at.isoformat(),
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "delivered_at": notification.delivered_at.isoformat() if notification.delivered_at else None
        }
        
        if include_metadata and notification.metadata:
            payload["metadata"] = notification.metadata
        
        if notification.user_id:
            payload["user_id"] = notification.user_id
        
        if notification.template_id:
            payload["template_id"] = notification.template_id
        
        return payload
    
    async def validate_webhook_url(self, webhook_url: str) -> Dict[str, Any]:
        """Validate webhook URL format and accessibility."""
        try:
            # Basic URL validation
            if not webhook_url.startswith(('http://', 'https://')):
                return {
                    "valid": False,
                    "error": "URL must start with http:// or https://"
                }
            
            # Test connectivity
            test_result = await self.test_webhook_endpoint(webhook_url)
            
            if test_result["success"]:
                return {
                    "valid": True,
                    "accessible": True,
                    "status_code": test_result["status_code"],
                    "response_time": test_result["response_time"]
                }
            else:
                return {
                    "valid": True,  # URL format is valid
                    "accessible": False,
                    "error": test_result["error"]
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            } 