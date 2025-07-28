"""
BMAD AI Core Services

This module provides core AI and machine learning services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main AI components
from .confidence_scoring import (
    ConfidenceScoring,
    confidence_scoring,
    create_review_request,
    format_confidence_message,
)
from .llm_client import (
    ask_openai,
    ask_openai_with_confidence,
    assess_complexity,
    assess_security_risk,
    calculate_confidence,
)

__all__ = [
    "ConfidenceScoring",
    "ask_openai",
    "ask_openai_with_confidence",
    "assess_complexity",
    "assess_security_risk",
    "calculate_confidence",
    "confidence_scoring",
    "create_review_request",
    "format_confidence_message"
]
