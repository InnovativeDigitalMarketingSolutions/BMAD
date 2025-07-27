"""
BMAD Slack Integration Module

This module provides Slack integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .slack_notify import send_slack_message

__all__ = [
    "send_slack_message"
] 