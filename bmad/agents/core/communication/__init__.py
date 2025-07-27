"""
BMAD Communication Core Services

This module provides core communication and messaging services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main communication components
from .message_bus import publish, subscribe, get_events, clear_events
from .notification_manager import NotificationManager, NotificationType, get_notification_manager

__all__ = [
    "publish",
    "subscribe",
    "get_events",
    "clear_events",
    "NotificationManager",
    "NotificationType",
    "get_notification_manager"
] 