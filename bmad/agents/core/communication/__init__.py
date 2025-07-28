"""
BMAD Communication Core Services

This module provides core communication and messaging services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main communication components
from .message_bus import clear_events, get_events, publish, subscribe
from .notification_manager import (
    NotificationManager,
    NotificationType,
    get_notification_manager,
)

__all__ = [
    "NotificationManager",
    "NotificationType",
    "clear_events",
    "get_events",
    "get_notification_manager",
    "publish",
    "subscribe"
]
