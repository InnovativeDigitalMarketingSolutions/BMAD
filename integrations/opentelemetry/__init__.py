"""
BMAD OpenTelemetry Integration Module

This module provides OpenTelemetry integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .opentelemetry_tracing import BMADTracer, TraceLevel, TracingConfig

__all__ = [
    "BMADTracer",
    "TraceLevel",
    "TracingConfig"
]
