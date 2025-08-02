"""
Database service for the Notification Service.

This module handles all database operations including notifications,
templates, delivery logs, and channel configurations.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from ..models.database import Base, Notification, Template, DeliveryLog, ChannelConfig
from ..models.schemas import NotificationCreate, TemplateCreate, NotificationStatus


class DatabaseService:
    """Database service for notification operations."""
    
    def __init__(self, database_url: str):
        """Initialize database service."""
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        
    async def initialize(self):
        """Initialize database connection and create tables."""
        try:
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
        except Exception as e:
            raise Exception(f"Failed to initialize database: {str(e)}")
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        if not self.session_factory:
            raise Exception("Database not initialized")
        return self.session_factory()
    
    # Notification operations
    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification."""
        async with await self.get_session() as session:
            try:
                notification = Notification(
                    user_id=notification_data.user_id,
                    channel=notification_data.channel.value,
                    template_id=notification_data.template_id,
                    subject=notification_data.subject,
                    content=notification_data.content,
                    recipient=notification_data.recipient,
                    notification_metadata=notification_data.metadata,
                    scheduled_at=notification_data.scheduled_at
                )
                
                session.add(notification)
                await session.commit()
                await session.refresh(notification)
                return notification
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to create notification: {str(e)}")
    
    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    select(Notification)
                    .options(selectinload(Notification.delivery_logs))
                    .where(Notification.id == notification_id)
                )
                return result.scalar_one_or_none()
                
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get notification: {str(e)}")
    
    async def get_notifications(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Notification], int]:
        """Get notifications with pagination and filters."""
        async with await self.get_session() as session:
            try:
                # Build query
                query = select(Notification)
                
                # Add filters
                conditions = []
                if user_id:
                    conditions.append(Notification.user_id == user_id)
                if channel:
                    conditions.append(Notification.channel == channel)
                if status:
                    conditions.append(Notification.status == status)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                # Get total count
                count_query = select(func.count()).select_from(query.subquery())
                total_result = await session.execute(count_query)
                total = total_result.scalar()
                
                # Add pagination and ordering
                query = query.order_by(desc(Notification.created_at))
                query = query.offset((page - 1) * size).limit(size)
                
                result = await session.execute(query)
                notifications = result.scalars().all()
                
                return list(notifications), total
                
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get notifications: {str(e)}")
    
    async def update_notification_status(
        self,
        notification_id: str,
        status: NotificationStatus,
        sent_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None
    ) -> Optional[Notification]:
        """Update notification status."""
        async with await self.get_session() as session:
            try:
                update_data = {"status": status.value}
                if sent_at:
                    update_data["sent_at"] = sent_at
                if delivered_at:
                    update_data["delivered_at"] = delivered_at
                
                result = await session.execute(
                    update(Notification)
                    .where(Notification.id == notification_id)
                    .values(**update_data)
                    .returning(Notification)
                )
                
                await session.commit()
                return result.scalar_one_or_none()
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to update notification status: {str(e)}")
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete notification."""
        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    delete(Notification).where(Notification.id == notification_id)
                )
                await session.commit()
                return result.rowcount > 0
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to delete notification: {str(e)}")
    
    # Template operations
    async def create_template(self, template_data: TemplateCreate) -> Template:
        """Create a new template."""
        async with await self.get_session() as session:
            try:
                template = Template(
                    name=template_data.name,
                    description=template_data.description,
                    channel=template_data.channel.value,
                    subject_template=template_data.subject_template,
                    content_template=template_data.content_template,
                    variables=template_data.variables,
                    language=template_data.language,
                    version=template_data.version,
                    is_active=template_data.is_active
                )
                
                session.add(template)
                await session.commit()
                await session.refresh(template)
                return template
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to create template: {str(e)}")
    
    async def get_template(self, template_id: str) -> Optional[Template]:
        """Get template by ID."""
        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    select(Template).where(Template.id == template_id)
                )
                return result.scalar_one_or_none()
                
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get template: {str(e)}")
    
    async def get_templates(
        self,
        channel: Optional[str] = None,
        language: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Template], int]:
        """Get templates with pagination and filters."""
        async with await self.get_session() as session:
            try:
                # Build query
                query = select(Template)
                
                # Add filters
                conditions = []
                if channel:
                    conditions.append(Template.channel == channel)
                if language:
                    conditions.append(Template.language == language)
                if is_active is not None:
                    conditions.append(Template.is_active == is_active)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                # Get total count
                count_query = select(func.count()).select_from(query.subquery())
                total_result = await session.execute(count_query)
                total = total_result.scalar()
                
                # Add pagination and ordering
                query = query.order_by(desc(Template.created_at))
                query = query.offset((page - 1) * size).limit(size)
                
                result = await session.execute(query)
                templates = result.scalars().all()
                
                return list(templates), total
                
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get templates: {str(e)}")
    
    async def update_template(self, template_id: str, update_data: Dict[str, Any]) -> Optional[Template]:
        """Update template."""
        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    update(Template)
                    .where(Template.id == template_id)
                    .values(**update_data)
                    .returning(Template)
                )
                
                await session.commit()
                return result.scalar_one_or_none()
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to update template: {str(e)}")
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    delete(Template).where(Template.id == template_id)
                )
                await session.commit()
                return result.rowcount > 0
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to delete template: {str(e)}")
    
    # Delivery log operations
    async def create_delivery_log(
        self,
        notification_id: str,
        channel: str,
        status: str,
        error_message: Optional[str] = None,
        retry_count: int = 0
    ) -> DeliveryLog:
        """Create delivery log entry."""
        async with await self.get_session() as session:
            try:
                delivery_log = DeliveryLog(
                    notification_id=notification_id,
                    channel=channel,
                    status=status,
                    error_message=error_message,
                    retry_count=retry_count,
                    delivered_at=datetime.now(timezone.utc) if status == "delivered" else None
                )
                
                session.add(delivery_log)
                await session.commit()
                await session.refresh(delivery_log)
                return delivery_log
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to create delivery log: {str(e)}")
    
    async def get_delivery_logs(
        self,
        notification_id: Optional[str] = None,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[DeliveryLog], int]:
        """Get delivery logs with pagination and filters."""
        async with await self.get_session() as session:
            try:
                # Build query
                query = select(DeliveryLog)
                
                # Add filters
                conditions = []
                if notification_id:
                    conditions.append(DeliveryLog.notification_id == notification_id)
                if channel:
                    conditions.append(DeliveryLog.channel == channel)
                if status:
                    conditions.append(DeliveryLog.status == status)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                # Get total count
                count_query = select(func.count()).select_from(query.subquery())
                total_result = await session.execute(count_query)
                total = total_result.scalar()
                
                # Add pagination and ordering
                query = query.order_by(desc(DeliveryLog.created_at))
                query = query.offset((page - 1) * size).limit(size)
                
                result = await session.execute(query)
                delivery_logs = result.scalars().all()
                
                return list(delivery_logs), total
                
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get delivery logs: {str(e)}")
    
    # Channel configuration operations
    async def get_channel_config(self, channel: str) -> Optional[ChannelConfig]:
        """Get channel configuration."""
        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    select(ChannelConfig).where(ChannelConfig.channel == channel)
                )
                return result.scalar_one_or_none()
                
            except SQLAlchemyError as e:
                raise Exception(f"Failed to get channel config: {str(e)}")
    
    async def update_channel_config(
        self,
        channel: str,
        config: Dict[str, Any],
        is_active: Optional[bool] = None,
        rate_limit_per_minute: Optional[int] = None
    ) -> Optional[ChannelConfig]:
        """Update channel configuration."""
        async with await self.get_session() as session:
            try:
                update_data = {"config": config}
                if is_active is not None:
                    update_data["is_active"] = is_active
                if rate_limit_per_minute is not None:
                    update_data["rate_limit_per_minute"] = rate_limit_per_minute
                
                result = await session.execute(
                    update(ChannelConfig)
                    .where(ChannelConfig.channel == channel)
                    .values(**update_data)
                    .returning(ChannelConfig)
                )
                
                await session.commit()
                return result.scalar_one_or_none()
                
            except SQLAlchemyError as e:
                await session.rollback()
                raise Exception(f"Failed to update channel config: {str(e)}") 