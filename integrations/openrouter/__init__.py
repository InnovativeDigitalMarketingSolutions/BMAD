"""
BMAD OpenRouter Integration Module

This module provides OpenRouter integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .openrouter_client import OpenRouterClient

__all__ = [
    "OpenRouterClient"
]
