"""
BMAD LangGraph Integration Module

This module provides LangGraph integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .langgraph_workflow import LangGraphWorkflowOrchestrator

__all__ = [
    "LangGraphWorkflowOrchestrator"
]
