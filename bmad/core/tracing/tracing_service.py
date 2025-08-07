"""
BMAD Tracing Service
Centralized tracing service that integrates with BMADTracer for comprehensive operation tracking.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from integrations.opentelemetry.opentelemetry_tracing import BMADTracer, TracingConfig

logger = logging.getLogger(__name__)

class TracingService:
    """
    Centralized tracing service for BMAD components.
    Provides a unified interface for tracing operations across all agents and services.
    """
    
    def __init__(self, service_name: str = "bmad-tracing-service", config: Optional[TracingConfig] = None):
        """
        Initialize the tracing service.
        
        Args:
            service_name: Name of the service for tracing identification
            config: Optional tracing configuration
        """
        self.service_name = service_name
        self.config = config or TracingConfig()
        self.tracer: Optional[BMADTracer] = None
        self._initialize_tracer()
        
    def _initialize_tracer(self):
        """Initialize the BMADTracer instance."""
        try:
            self.tracer = BMADTracer(config=self.config)
            logger.info(f"Tracing service initialized for {self.service_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize tracing service: {e}")
            self.tracer = None
    
    def start_span(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Start a new tracing span.
        
        Args:
            operation_name: Name of the operation being traced
            attributes: Optional attributes for the span
            
        Returns:
            Span ID if successful, None otherwise
        """
        if not self.tracer:
            return None
            
        try:
            span_id = self.tracer.start_span(operation_name, attributes or {})
            logger.debug(f"Started span {span_id} for operation {operation_name}")
            return span_id
        except Exception as e:
            logger.warning(f"Failed to start span for {operation_name}: {e}")
            return None
    
    def end_span(self, span_id: str, attributes: Optional[Dict[str, Any]] = None):
        """
        End a tracing span.
        
        Args:
            span_id: ID of the span to end
            attributes: Optional attributes to add before ending
        """
        if not self.tracer:
            return
            
        try:
            self.tracer.end_span(span_id, attributes or {})
            logger.debug(f"Ended span {span_id}")
        except Exception as e:
            logger.warning(f"Failed to end span {span_id}: {e}")
    
    def record_event(self, event_name: str, attributes: Optional[Dict[str, Any]] = None, span_id: Optional[str] = None):
        """
        Record an event in the current or specified span.
        
        Args:
            event_name: Name of the event
            attributes: Optional attributes for the event
            span_id: Optional span ID to record event in
        """
        if not self.tracer:
            return
            
        try:
            self.tracer.record_event(event_name, attributes or {}, span_id)
            logger.debug(f"Recorded event {event_name}")
        except Exception as e:
            logger.warning(f"Failed to record event {event_name}: {e}")
    
    def add_attribute(self, key: str, value: Any, span_id: Optional[str] = None):
        """
        Add an attribute to the current or specified span.
        
        Args:
            key: Attribute key
            value: Attribute value
            span_id: Optional span ID to add attribute to
        """
        if not self.tracer:
            return
            
        try:
            self.tracer.add_attribute(key, value, span_id)
            logger.debug(f"Added attribute {key}={value}")
        except Exception as e:
            logger.warning(f"Failed to add attribute {key}: {e}")
    
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager for tracing operations.
        
        Args:
            operation_name: Name of the operation
            attributes: Optional attributes for the span
        """
        return TracingContext(self, operation_name, attributes)
    
    def get_trace_id(self) -> Optional[str]:
        """
        Get the current trace ID.
        
        Returns:
            Current trace ID if available, None otherwise
        """
        if not self.tracer:
            return None
            
        try:
            return self.tracer.get_trace_id()
        except Exception as e:
            logger.warning(f"Failed to get trace ID: {e}")
            return None
    
    def is_enabled(self) -> bool:
        """
        Check if tracing is enabled.
        
        Returns:
            True if tracing is enabled, False otherwise
        """
        return self.tracer is not None


class TracingContext:
    """Context manager for tracing operations."""
    
    def __init__(self, tracing_service: TracingService, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        self.tracing_service = tracing_service
        self.operation_name = operation_name
        self.attributes = attributes or {}
        self.span_id: Optional[str] = None
    
    def __enter__(self):
        self.span_id = self.tracing_service.start_span(self.operation_name, self.attributes)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span_id:
            end_attributes = {}
            if exc_type:
                end_attributes["error"] = True
                end_attributes["error_type"] = exc_type.__name__
                if exc_val:
                    end_attributes["error_message"] = str(exc_val)
            
            self.tracing_service.end_span(self.span_id, end_attributes)


# Global tracing service instance
_global_tracing_service: Optional[TracingService] = None

def get_tracing_service(service_name: str = "bmad-tracing-service") -> TracingService:
    """
    Get or create the global tracing service instance.
    
    Args:
        service_name: Name of the service for tracing identification
        
    Returns:
        TracingService instance
    """
    global _global_tracing_service
    
    if _global_tracing_service is None:
        _global_tracing_service = TracingService(service_name)
    
    return _global_tracing_service

def initialize_tracing_service(service_name: str = "bmad-tracing-service", config: Optional[TracingConfig] = None) -> TracingService:
    """
    Initialize the global tracing service.
    
    Args:
        service_name: Name of the service for tracing identification
        config: Optional tracing configuration
        
    Returns:
        Initialized TracingService instance
    """
    global _global_tracing_service
    
    _global_tracing_service = TracingService(service_name, config)
    return _global_tracing_service 