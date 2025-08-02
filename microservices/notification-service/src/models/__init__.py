"""
Data models for the Notification Service.

This package contains Pydantic schemas for API requests/responses
and SQLAlchemy models for database operations.
"""

from .schemas import *
from .database import *

__all__ = [
    # Schemas
    "HealthStatus",
    "ServiceHealth",
    "NotificationCreate",
    "NotificationResponse",
    "NotificationList",
    "TemplateCreate",
    "TemplateResponse",
    "TemplateList",
    "ChannelConfig",
    "DeliveryLog",
    "AnalyticsResponse",
    "ErrorResponse",
    "SuccessResponse",
    
    # Database Models
    "Notification",
    "Template",
    "DeliveryLog",
    "ChannelConfig",
] 