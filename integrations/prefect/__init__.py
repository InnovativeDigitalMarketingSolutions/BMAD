"""
BMAD Prefect Integration Module

This module provides Prefect integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .prefect_workflow import PrefectWorkflowOrchestrator, PrefectWorkflowConfig

__all__ = [
    "PrefectWorkflowOrchestrator",
    "PrefectWorkflowConfig"
] 