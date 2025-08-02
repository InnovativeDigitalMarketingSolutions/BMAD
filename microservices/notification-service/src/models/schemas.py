"""
Pydantic schemas for the Notification Service API.

This module defines the request and response models for all API endpoints.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class ServiceHealth(BaseModel):
    """Health check response model."""
    status: HealthStatus
    timestamp: datetime
    service: str = "notification-service"
    version: str = "1.0.0"
    uptime: Optional[float] = None
    dependencies: Dict[str, HealthStatus] = {}


class NotificationChannel(str, Enum):
    """Notification channel enumeration."""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Notification status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationCreate(BaseModel):
    """Create notification request model."""
    user_id: Optional[str] = None
    channel: NotificationChannel
    template_id: Optional[str] = None
    subject: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=10000)
    recipient: str = Field(..., min_length=1, max_length=255)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None

    @field_validator('recipient')
    @classmethod
    def validate_recipient(cls, v: str) -> str:
        """Validate recipient based on channel."""
        if not v:
            raise ValueError("Recipient cannot be empty")
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content length."""
        if len(v) > 10000:
            raise ValueError("Content too long (max 10000 characters)")
        return v


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: str
    user_id: Optional[str]
    channel: NotificationChannel
    template_id: Optional[str]
    subject: Optional[str]
    content: str
    recipient: str
    metadata: Dict[str, Any]
    status: NotificationStatus
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationList(BaseModel):
    """Notification list response model."""
    notifications: List[NotificationResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class BulkNotificationCreate(BaseModel):
    """Bulk notification creation request model."""
    notifications: List[NotificationCreate] = Field(..., min_items=1, max_items=100)
    template_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None

    @field_validator('notifications')
    @classmethod
    def validate_notifications(cls, v: List[NotificationCreate]) -> List[NotificationCreate]:
        """Validate notifications list."""
        if len(v) > 100:
            raise ValueError("Cannot send more than 100 notifications at once")
        return v


class TemplateCreate(BaseModel):
    """Create template request model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    channel: NotificationChannel
    subject_template: Optional[str] = None
    content_template: str = Field(..., min_length=1, max_length=10000)
    variables: Dict[str, str] = Field(default_factory=dict)
    language: str = Field(default="en", min_length=2, max_length=5)
    version: int = Field(default=1, ge=1)
    is_active: bool = True

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate template name."""
        if not v.strip():
            raise ValueError("Template name cannot be empty")
        return v.strip()

    @field_validator('content_template')
    @classmethod
    def validate_content_template(cls, v: str) -> str:
        """Validate content template."""
        if len(v) > 10000:
            raise ValueError("Content template too long (max 10000 characters)")
        return v


class TemplateResponse(BaseModel):
    """Template response model."""
    id: str
    name: str
    description: Optional[str]
    channel: NotificationChannel
    subject_template: Optional[str]
    content_template: str
    variables: Dict[str, str]
    language: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateList(BaseModel):
    """Template list response model."""
    templates: List[TemplateResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class TemplateTest(BaseModel):
    """Template test request model."""
    variables: Dict[str, Any] = Field(default_factory=dict)
    recipient: str = Field(..., min_length=1, max_length=255)


class ChannelConfig(BaseModel):
    """Channel configuration model."""
    id: str
    channel: NotificationChannel
    config: Dict[str, Any]
    is_active: bool
    rate_limit_per_minute: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeliveryLog(BaseModel):
    """Delivery log model."""
    id: str
    notification_id: str
    channel: NotificationChannel
    status: NotificationStatus
    error_message: Optional[str]
    retry_count: int
    delivered_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    """Analytics response model."""
    total_notifications: int
    sent_notifications: int
    delivered_notifications: int
    failed_notifications: int
    success_rate: float
    channel_breakdown: Dict[str, Dict[str, int]]
    time_period: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class ChannelStatus(BaseModel):
    """Channel status model."""
    channel: NotificationChannel
    is_active: bool
    rate_limit_per_minute: int
    current_rate: int
    last_delivery: Optional[datetime]
    error_count: int
    success_rate: float


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Success response model."""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 