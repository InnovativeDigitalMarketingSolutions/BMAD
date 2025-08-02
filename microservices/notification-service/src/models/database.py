"""
SQLAlchemy database models for the Notification Service.

This module defines the database tables and relationships for notifications,
templates, delivery logs, and channel configurations.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, JSON, 
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class Notification(Base):
    """Notification database model."""
    __tablename__ = "notifications"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    template_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    delivery_logs = relationship("DeliveryLog", back_populates="notification", cascade="all, delete-orphan")


class Template(Base):
    """Template database model."""
    __tablename__ = "templates"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_template: Mapped[Optional[str]] = mapped_column(Text)
    content_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[Dict[str, str]] = mapped_column(JSONB, default=dict)
    language: Mapped[str] = mapped_column(String(10), default="en", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'channel', 'language', 'version', name='uq_template_version'),
    )


class DeliveryLog(Base):
    """Delivery log database model."""
    __tablename__ = "delivery_logs"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_uuid)
    notification_id: Mapped[str] = mapped_column(
        String(255), 
        ForeignKey("notifications.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    
    # Relationships
    notification = relationship("Notification", back_populates="delivery_logs")


class ChannelConfig(Base):
    """Channel configuration database model."""
    __tablename__ = "channel_configs"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_uuid)
    channel: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    ) 