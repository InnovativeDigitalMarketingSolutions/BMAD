"""
BMAD Webhook Integration Module

This module provides webhook integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .webhook_notify import WebhookNotifier

__all__ = [
    "WebhookNotifier"
]
