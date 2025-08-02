"""
SMS service for the Notification Service.

This module handles SMS delivery through Twilio provider.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from ..models.schemas import NotificationStatus
from ..models.database import Notification, ChannelConfig
from .database import DatabaseService


class SMSService:
    """SMS service for notification delivery."""
    
    def __init__(self, database_service: DatabaseService):
        """Initialize SMS service."""
        self.database_service = database_service
        self.twilio_client = None
        self.default_from_number = "+1234567890"
    
    async def initialize(self, twilio_account_sid: str, twilio_auth_token: str):
        """Initialize SMS service with Twilio credentials."""
        if (twilio_account_sid and twilio_auth_token and 
            twilio_account_sid != "your-twilio-account-sid" and 
            twilio_auth_token != "your-twilio-auth-token"):
            self.twilio_client = Client(twilio_account_sid, twilio_auth_token)
    
    async def send_sms(
        self,
        notification: Notification,
        content: str
    ) -> Dict[str, Any]:
        """Send SMS notification."""
        try:
            # Get channel configuration
            channel_config = await self.database_service.get_channel_config("sms")
            if not channel_config or not channel_config.is_active:
                raise Exception("SMS channel is not configured or inactive")
            
            # Update notification status to sent
            await self.database_service.update_notification_status(
                notification.id,
                NotificationStatus.SENT,
                sent_at=datetime.now(timezone.utc)
            )
            
            # Create delivery log
            await self.database_service.create_delivery_log(
                notification.id,
                "sms",
                "sent"
            )
            
            # Send SMS via Twilio
            config = channel_config.config
            from_number = config.get("from_number", self.default_from_number)
            
            result = await self._send_via_twilio(
                notification.recipient,
                content,
                from_number
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
                "sms",
                "delivered"
            )
            
            return {
                "success": True,
                "provider": "twilio",
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
                "sms",
                "failed",
                error_message=str(e)
            )
            
            raise Exception(f"Failed to send SMS: {str(e)}")
    
    async def _send_via_twilio(
        self,
        recipient: str,
        content: str,
        from_number: str
    ) -> Dict[str, Any]:
        """Send SMS via Twilio."""
        try:
            if not self.twilio_client:
                raise Exception("Twilio client not initialized")
            
            # Validate phone number format
            if not self._is_valid_phone_number(recipient):
                raise Exception(f"Invalid phone number format: {recipient}")
            
            # Send message
            message = self.twilio_client.messages.create(
                body=content,
                from_=from_number,
                to=recipient
            )
            
            return {
                "success": True,
                "message_id": message.sid,
                "status": message.status,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except TwilioException as e:
            raise Exception(f"Twilio error: {str(e)}")
        except Exception as e:
            raise Exception(f"SMS delivery error: {str(e)}")
    
    def _is_valid_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format."""
        import re
        # Basic phone number validation (E.164 format)
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone_number))
    
    async def send_bulk_sms(
        self,
        notifications: List[Notification],
        content: str
    ) -> Dict[str, Any]:
        """Send bulk SMS notifications."""
        results = {
            "total": len(notifications),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process SMS in batches to avoid rate limiting
        batch_size = 10  # Twilio has stricter rate limits for SMS
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i + batch_size]
            
            # Process batch sequentially to respect rate limits
            for notification in batch:
                try:
                    await self.send_sms(notification, content)
                    results["successful"] += 1
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(str(e))
                
                # Rate limiting delay between messages
                await asyncio.sleep(0.1)
            
            # Rate limiting delay between batches
            if i + batch_size < len(notifications):
                await asyncio.sleep(1)
        
        return results
    
    async def test_sms_configuration(self) -> Dict[str, Any]:
        """Test SMS configuration."""
        try:
            if not self.twilio_client:
                return {
                    "twilio": "not_configured",
                    "default_from_number": self.default_from_number
                }
            
            # Test Twilio account
            try:
                # Get account info to test credentials
                account = self.twilio_client.api.accounts(self.twilio_client.account_sid).fetch()
                twilio_status = "configured" if account.status == "active" else "inactive"
            except Exception:
                twilio_status = "error"
            
            return {
                "twilio": twilio_status,
                "default_from_number": self.default_from_number,
                "account_sid": self.twilio_client.account_sid if self.twilio_client else None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "twilio": "error"
            }
    
    async def get_sms_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get SMS delivery analytics."""
        try:
            # Get delivery logs for SMS channel
            delivery_logs, total = await self.database_service.get_delivery_logs(
                channel="sms"
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
            raise Exception(f"Failed to get SMS analytics: {str(e)}")
    
    async def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Validate phone number using Twilio Lookup API."""
        try:
            if not self.twilio_client:
                raise Exception("Twilio client not initialized")
            
            # Use Twilio Lookup API to validate phone number
            phone_number_obj = self.twilio_client.lookups.v2.phone_numbers(phone_number).fetch()
            
            return {
                "valid": True,
                "phone_number": phone_number_obj.phone_number,
                "country_code": phone_number_obj.country_code,
                "national_format": phone_number_obj.national_format,
                "international_format": phone_number_obj.international_format,
                "carrier": phone_number_obj.carrier.get("name") if phone_number_obj.carrier else None
            }
            
        except TwilioException as e:
            return {
                "valid": False,
                "error": str(e),
                "phone_number": phone_number
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "phone_number": phone_number
            }
    
    async def get_sms_pricing(self, phone_number: str) -> Dict[str, Any]:
        """Get SMS pricing information."""
        try:
            if not self.twilio_client:
                raise Exception("Twilio client not initialized")
            
            # Get pricing information for the phone number
            pricing = self.twilio_client.pricing.v2.messaging.countries(phone_number[:2]).fetch()
            
            return {
                "country_code": phone_number[:2],
                "outbound_sms_prices": pricing.outbound_sms_prices,
                "inbound_sms_prices": pricing.inbound_sms_prices,
                "price_unit": pricing.price_unit
            }
            
        except TwilioException as e:
            raise Exception(f"Failed to get SMS pricing: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get SMS pricing: {str(e)}") 