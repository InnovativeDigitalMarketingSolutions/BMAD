#!/usr/bin/env python3
"""
Delivery Service voor Notification Service
Orchestreert alle delivery kanalen (email, SMS, Slack, webhook)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .database import DatabaseService
from .template import TemplateService
from .email import EmailService
from .sms import SMSService
from .slack import SlackService
from .webhook import WebhookService

logger = logging.getLogger(__name__)

class DeliveryStatus(str, Enum):
    """Delivery status enum."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"

class DeliveryPriority(str, Enum):
    """Delivery priority enum."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class DeliveryRequest(BaseModel):
    """Delivery request model."""
    template_id: str = Field(..., description="Template ID")
    channel: str = Field(..., description="Delivery channel (email, sms, slack, webhook)")
    recipient: str = Field(..., description="Recipient identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Template context")
    priority: DeliveryPriority = Field(default=DeliveryPriority.NORMAL, description="Delivery priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled delivery time")
    retry_count: int = Field(default=0, description="Retry count")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DeliveryResponse(BaseModel):
    """Delivery response model."""
    delivery_id: str = Field(..., description="Delivery ID")
    status: DeliveryStatus = Field(..., description="Delivery status")
    message: str = Field(..., description="Status message")
    channel_response: Optional[Dict[str, Any]] = Field(None, description="Channel-specific response")
    retry_count: int = Field(default=0, description="Current retry count")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")

class BulkDeliveryRequest(BaseModel):
    """Bulk delivery request model."""
    template_id: str = Field(..., description="Template ID")
    channel: str = Field(..., description="Delivery channel")
    recipients: List[str] = Field(..., description="List of recipients")
    context: Dict[str, Any] = Field(default_factory=dict, description="Template context")
    priority: DeliveryPriority = Field(default=DeliveryPriority.NORMAL, description="Delivery priority")
    batch_size: int = Field(default=100, description="Batch size for processing")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class BulkDeliveryResponse(BaseModel):
    """Bulk delivery response model."""
    batch_id: str = Field(..., description="Batch ID")
    total_recipients: int = Field(..., description="Total number of recipients")
    successful_deliveries: int = Field(..., description="Number of successful deliveries")
    failed_deliveries: int = Field(..., description="Number of failed deliveries")
    delivery_ids: List[str] = Field(..., description="List of delivery IDs")
    status: DeliveryStatus = Field(..., description="Overall batch status")

class DeliveryService:
    """Orchestration service for all delivery channels."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize delivery service."""
        self.db_service = db_service
        self.template_service = TemplateService(db_service)
        self.email_service = EmailService(db_service)
        self.sms_service = SMSService(db_service)
        self.slack_service = SlackService(db_service)
        self.webhook_service = WebhookService(db_service)
        
        # Delivery channel mapping
        self.channel_services = {
            "email": self.email_service,
            "sms": self.sms_service,
            "slack": self.slack_service,
            "webhook": self.webhook_service
        }
        
        # Priority delays (in seconds)
        self.priority_delays = {
            DeliveryPriority.LOW: 300,      # 5 minutes
            DeliveryPriority.NORMAL: 60,    # 1 minute
            DeliveryPriority.HIGH: 10,      # 10 seconds
            DeliveryPriority.URGENT: 0      # Immediate
        }
        
        logger.info("Delivery Service initialized")
    
    async def deliver_notification(self, request: DeliveryRequest) -> DeliveryResponse:
        """Deliver a single notification."""
        try:
            logger.info(f"Processing delivery request: {request.template_id} -> {request.channel}")
            
            # Validate channel
            if request.channel not in self.channel_services:
                raise ValueError(f"Unsupported channel: {request.channel}")
            
            # Get channel service
            channel_service = self.channel_services[request.channel]
            
            # Create delivery record
            delivery_id = await self._create_delivery_record(request)
            
            # Process delivery
            result = await self._process_delivery(request, channel_service, delivery_id)
            
            # Update delivery record
            await self._update_delivery_record(delivery_id, result)
            
            logger.info(f"Delivery completed: {delivery_id} -> {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"Delivery failed: {str(e)}")
            return DeliveryResponse(
                delivery_id=request.template_id,
                status=DeliveryStatus.FAILED,
                message=f"Delivery failed: {str(e)}",
                retry_count=request.retry_count
            )
    
    async def deliver_bulk_notifications(self, request: BulkDeliveryRequest) -> BulkDeliveryResponse:
        """Deliver notifications in bulk."""
        try:
            logger.info(f"Processing bulk delivery: {request.template_id} -> {len(request.recipients)} recipients")
            
            # Validate channel
            if request.channel not in self.channel_services:
                raise ValueError(f"Unsupported channel: {request.channel}")
            
            # Create batch record
            batch_id = await self._create_batch_record(request)
            
            # Process in batches
            delivery_ids = []
            successful_count = 0
            failed_count = 0
            
            for i in range(0, len(request.recipients), request.batch_size):
                batch_recipients = request.recipients[i:i + request.batch_size]
                
                # Process batch
                batch_results = await self._process_batch(
                    request, batch_recipients, batch_id
                )
                
                delivery_ids.extend(batch_results["delivery_ids"])
                successful_count += batch_results["successful"]
                failed_count += batch_results["failed"]
                
                # Add delay between batches to avoid rate limiting
                if i + request.batch_size < len(request.recipients):
                    await asyncio.sleep(1)
            
            # Determine overall status
            overall_status = DeliveryStatus.DELIVERED if failed_count == 0 else DeliveryStatus.FAILED
            
            result = BulkDeliveryResponse(
                batch_id=batch_id,
                total_recipients=len(request.recipients),
                successful_deliveries=successful_count,
                failed_deliveries=failed_count,
                delivery_ids=delivery_ids,
                status=overall_status
            )
            
            logger.info(f"Bulk delivery completed: {batch_id} -> {successful_count}/{len(request.recipients)} successful")
            return result
            
        except Exception as e:
            logger.error(f"Bulk delivery failed: {str(e)}")
            return BulkDeliveryResponse(
                batch_id=request.template_id,
                total_recipients=len(request.recipients),
                successful_deliveries=0,
                failed_deliveries=len(request.recipients),
                delivery_ids=[],
                status=DeliveryStatus.FAILED
            )
    
    async def retry_failed_deliveries(self, max_retries: int = 3) -> Dict[str, Any]:
        """Retry failed deliveries."""
        try:
            logger.info(f"Retrying failed deliveries (max: {max_retries})")
            
            # Get failed deliveries
            failed_deliveries = await self.db_service.get_failed_deliveries(max_retries)
            
            retry_count = 0
            success_count = 0
            
            for delivery in failed_deliveries:
                try:
                    # Create retry request
                    retry_request = DeliveryRequest(
                        template_id=delivery["template_id"],
                        channel=delivery["channel"],
                        recipient=delivery["recipient"],
                        context=delivery["context"],
                        priority=DeliveryPriority(delivery["priority"]),
                        retry_count=delivery["retry_count"] + 1,
                        max_retries=delivery["max_retries"],
                        metadata=delivery["metadata"]
                    )
                    
                    # Retry delivery
                    result = await self.deliver_notification(retry_request)
                    
                    if result.status == DeliveryStatus.DELIVERED:
                        success_count += 1
                    
                    retry_count += 1
                    
                    # Add delay between retries
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Retry failed for delivery {delivery['id']}: {str(e)}")
            
            logger.info(f"Retry completed: {success_count}/{retry_count} successful")
            return {
                "retry_count": retry_count,
                "success_count": success_count,
                "failed_count": retry_count - success_count
            }
            
        except Exception as e:
            logger.error(f"Retry process failed: {str(e)}")
            return {
                "retry_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "error": str(e)
            }
    
    async def get_delivery_status(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery status."""
        try:
            return await self.db_service.get_delivery_by_id(delivery_id)
        except Exception as e:
            logger.error(f"Failed to get delivery status: {str(e)}")
            return None
    
    async def get_delivery_statistics(self, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None,
                                    channel: Optional[str] = None) -> Dict[str, Any]:
        """Get delivery statistics."""
        try:
            return await self.db_service.get_delivery_statistics(
                start_date=start_date,
                end_date=end_date,
                channel=channel
            )
        except Exception as e:
            logger.error(f"Failed to get delivery statistics: {str(e)}")
            return {}
    
    async def _create_delivery_record(self, request: DeliveryRequest) -> str:
        """Create delivery record in database."""
        delivery_data = {
            "template_id": request.template_id,
            "channel": request.channel,
            "recipient": request.recipient,
            "context": request.context,
            "priority": request.priority.value,
            "status": DeliveryStatus.PENDING.value,
            "retry_count": request.retry_count,
            "max_retries": request.max_retries,
            "metadata": request.metadata,
            "scheduled_at": request.scheduled_at or datetime.utcnow()
        }
        
        return await self.db_service.create_delivery(delivery_data)
    
    async def _create_batch_record(self, request: BulkDeliveryRequest) -> str:
        """Create batch record in database."""
        batch_data = {
            "template_id": request.template_id,
            "channel": request.channel,
            "total_recipients": len(request.recipients),
            "status": DeliveryStatus.PENDING.value,
            "metadata": request.metadata,
            "created_at": datetime.utcnow()
        }
        
        return await self.db_service.create_batch(batch_data)
    
    async def _process_delivery(self, 
                              request: DeliveryRequest,
                              channel_service: Any,
                              delivery_id: str) -> DeliveryResponse:
        """Process individual delivery."""
        try:
            # Render template
            template_content = await self.template_service.render_template(
                request.template_id, request.context
            )
            
            # Send via channel service
            channel_response = await channel_service.send_notification(
                recipient=request.recipient,
                content=template_content,
                metadata=request.metadata
            )
            
            # Determine status
            if channel_response.get("success", False):
                status = DeliveryStatus.DELIVERED
                message = "Notification delivered successfully"
            else:
                status = DeliveryStatus.FAILED
                message = channel_response.get("error", "Delivery failed")
            
            return DeliveryResponse(
                delivery_id=delivery_id,
                status=status,
                message=message,
                channel_response=channel_response,
                retry_count=request.retry_count,
                delivered_at=datetime.utcnow() if status == DeliveryStatus.DELIVERED else None
            )
            
        except Exception as e:
            logger.error(f"Delivery processing failed: {str(e)}")
            return DeliveryResponse(
                delivery_id=delivery_id,
                status=DeliveryStatus.FAILED,
                message=f"Processing failed: {str(e)}",
                retry_count=request.retry_count
            )
    
    async def _process_batch(self, 
                           request: BulkDeliveryRequest,
                           recipients: List[str],
                           batch_id: str) -> Dict[str, Any]:
        """Process batch of deliveries."""
        delivery_ids = []
        successful_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                # Create individual delivery request
                delivery_request = DeliveryRequest(
                    template_id=request.template_id,
                    channel=request.channel,
                    recipient=recipient,
                    context=request.context,
                    priority=request.priority,
                    metadata=request.metadata
                )
                
                # Process delivery
                result = await self.deliver_notification(delivery_request)
                delivery_ids.append(result.delivery_id)
                
                if result.status == DeliveryStatus.DELIVERED:
                    successful_count += 1
                else:
                    failed_count += 1
                
            except Exception as e:
                logger.error(f"Batch delivery failed for {recipient}: {str(e)}")
                failed_count += 1
        
        return {
            "delivery_ids": delivery_ids,
            "successful": successful_count,
            "failed": failed_count
        }
    
    async def _update_delivery_record(self, delivery_id: str, result: DeliveryResponse) -> None:
        """Update delivery record with result."""
        update_data = {
            "status": result.status.value,
            "message": result.message,
            "channel_response": result.channel_response,
            "retry_count": result.retry_count,
            "delivered_at": result.delivered_at
        }
        
        await self.db_service.update_delivery(delivery_id, update_data) 