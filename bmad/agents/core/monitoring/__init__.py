"""
BMAD Monitoring Core Services

This module provides core monitoring and observability services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main monitoring components
from .monitoring import (
    HealthChecker,
    MetricsCollector,
    StructuredLogger,
    increment_counter,
    log_event,
    measure_time,
    record_metric,
)

# Create global instances
_metrics_collector = None
_health_checker = None
_structured_logger = None

def get_metrics_collector():
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_health_checker():
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

def get_structured_logger():
    """Get the global structured logger instance."""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredLogger()
    return _structured_logger

# Global instances for backward compatibility
metrics_collector = get_metrics_collector()
health_checker = get_health_checker()
structured_logger = get_structured_logger()

__all__ = [
    "HealthChecker",
    "MetricsCollector", 
    "StructuredLogger",
    "increment_counter",
    "log_event",
    "measure_time",
    "record_metric",
    "metrics_collector",
    "health_checker",
    "structured_logger",
    "get_metrics_collector",
    "get_health_checker",
    "get_structured_logger"
]
