"""
BMAD Figma Integration Module

This module provides Figma integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .figma_client import FigmaClient
from .figma_slack_notifier import FigmaSlackNotifier

__all__ = [
    "FigmaClient",
    "FigmaSlackNotifier"
] 