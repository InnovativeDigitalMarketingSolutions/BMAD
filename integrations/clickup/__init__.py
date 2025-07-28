"""
BMAD ClickUp Integration Module

This module provides ClickUp integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .bmad_clickup_workflow import BMADClickUpWorkflow
from .clickup_integration import ClickUpIntegration

__all__ = [
    "BMADClickUpWorkflow",
    "ClickUpIntegration"
]
