"""
BMAD OpenTelemetry Tracing

Dit module biedt distributed tracing en observability voor BMAD agents.
Integreert met OpenTelemetry voor end-to-end tracing van agent workflows en performance monitoring.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
import opentelemetry
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
# from opentelemetry.instrumentation.aiohttp import AioHttpClientInstrumentor  # Not available for Python 3.13
# from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor  # Not available for Python 3.13
from prometheus_client import start_http_server, Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

class TraceLevel(Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    DEBUG = "debug"

class ExporterType(Enum):
    CONSOLE = "console"
    JAEGER = "jaeger"
    OTLP = "otlp"
    PROMETHEUS = "prometheus"

@dataclass
class TracingConfig:
    """Configuration for OpenTelemetry tracing."""
    service_name: str = "bmad-agents"
    service_version: str = "1.0.0"
    environment: str = "development"
    trace_level: TraceLevel = TraceLevel.DETAILED
    exporters: List[ExporterType] = field(default_factory=lambda: [ExporterType.CONSOLE])
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831
    otlp_endpoint: str = "http://localhost:4317"
    prometheus_port: int = 8000
    sample_rate: float = 1.0
    max_attributes: int = 32
    max_events: int = 128
    max_links: int = 32

@dataclass
class AgentSpan:
    """Represents a span for agent execution."""
    agent_name: str
    task_name: str
    workflow_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: Status = Status(StatusCode.UNSET)
    error: Optional[str] = None

class BMADTracer:
    """
    OpenTelemetry tracer voor BMAD agents met custom metrics en spans.
    """
    
    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        self.metrics = {}
        
        # Initialize tracing
        self._initialize_tracing()
        
        # Initialize metrics
        self._initialize_metrics()
        
        # Instrument HTTP clients
        self._instrument_http_clients()
        
        logger.info(f"BMAD Tracer geïnitialiseerd voor service: {config.service_name}")
    
    def _initialize_tracing(self):
        """Initialize OpenTelemetry tracing."""
        # Create resource
        resource = Resource.create({
            "service.name": self.config.service_name,
            "service.version": self.config.service_version,
            "service.environment": self.config.environment,
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(
            resource=resource,
            sampler=opentelemetry.sdk.trace.sampling.TraceIdRatioBased(self.config.sample_rate)
        )
        
        # Add span processors based on exporters
        for exporter_type in self.config.exporters:
            if exporter_type == ExporterType.CONSOLE:
                processor = BatchSpanProcessor(ConsoleSpanExporter())
                self.tracer_provider.add_span_processor(processor)
                
            elif exporter_type == ExporterType.JAEGER:
                exporter = JaegerExporter(
                    agent_host_name=self.config.jaeger_host,
                    agent_port=self.config.jaeger_port,
                )
                processor = BatchSpanProcessor(exporter)
                self.tracer_provider.add_span_processor(processor)
                
            elif exporter_type == ExporterType.OTLP:
                exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
                processor = BatchSpanProcessor(exporter)
                self.tracer_provider.add_span_processor(processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Create tracer
        self.tracer = trace.get_tracer(self.config.service_name)
    
    def _initialize_metrics(self):
        """Initialize Prometheus metrics."""
        # Agent execution metrics
        self.metrics["agent_executions"] = Counter(
            "bmad_agent_executions_total",
            "Total number of agent executions",
            ["agent_name", "task_name", "status"]
        )
        
        self.metrics["agent_duration"] = Histogram(
            "bmad_agent_duration_seconds",
            "Agent execution duration in seconds",
            ["agent_name", "task_name"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        self.metrics["workflow_executions"] = Counter(
            "bmad_workflow_executions_total",
            "Total number of workflow executions",
            ["workflow_name", "status"]
        )
        
        self.metrics["workflow_duration"] = Histogram(
            "bmad_workflow_duration_seconds",
            "Workflow execution duration in seconds",
            ["workflow_name"],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 1800.0]
        )
        
        self.metrics["active_agents"] = Gauge(
            "bmad_active_agents",
            "Number of currently active agents",
            ["agent_name"]
        )
        
        self.metrics["llm_calls"] = Counter(
            "bmad_llm_calls_total",
            "Total number of LLM API calls",
            ["provider", "model", "status"]
        )
        
        self.metrics["llm_tokens"] = Counter(
            "bmad_llm_tokens_total",
            "Total number of tokens used",
            ["provider", "model", "direction"]
        )
        
        # Start Prometheus server if configured
        if ExporterType.PROMETHEUS in self.config.exporters:
            start_http_server(self.config.prometheus_port)
            logger.info(f"Prometheus metrics server gestart op poort {self.config.prometheus_port}")
    
    def _instrument_http_clients(self):
        """Instrument HTTP clients for automatic tracing."""
        try:
            RequestsInstrumentor().instrument()
            logger.info("HTTP clients geïnstrumenteerd voor tracing")
        except Exception as e:
            logger.warning(f"HTTP client instrumentation failed: {e}")
    
    @contextmanager
    def trace_agent_execution(
        self,
        agent_name: str,
        task_name: str,
        workflow_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager voor het traceren van agent uitvoering.
        
        Args:
            agent_name: Name of the agent
            task_name: Name of the task being executed
            workflow_id: Optional workflow ID for context
            attributes: Additional attributes to add to the span
        """
        if not self.tracer:
            yield
            return
        
        span_name = f"{agent_name}.{task_name}"
        span_attributes = {
            "agent.name": agent_name,
            "task.name": task_name,
            "bmad.component": "agent",
        }
        
        if workflow_id:
            span_attributes["workflow.id"] = workflow_id
        
        if attributes:
            span_attributes.update(attributes)
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name, attributes=span_attributes) as span:
            try:
                # Update metrics
                self.metrics["active_agents"].labels(agent_name=agent_name).inc()
                
                # Execute the agent
                yield span
                
                # Mark as successful
                span.set_status(Status(StatusCode.OK))
                self.metrics["agent_executions"].labels(
                    agent_name=agent_name,
                    task_name=task_name,
                    status="success"
                ).inc()
                
            except Exception as e:
                # Mark as failed
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                
                self.metrics["agent_executions"].labels(
                    agent_name=agent_name,
                    task_name=task_name,
                    status="error"
                ).inc()
                
                raise
            
            finally:
                # Update duration metrics
                duration = time.time() - start_time
                self.metrics["agent_duration"].labels(
                    agent_name=agent_name,
                    task_name=task_name
                ).observe(duration)
                
                self.metrics["active_agents"].labels(agent_name=agent_name).dec()
                
                # Add duration attribute
                span.set_attribute("duration.seconds", duration)
    
    @contextmanager
    def trace_workflow_execution(
        self,
        workflow_name: str,
        workflow_id: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager voor het traceren van workflow uitvoering.
        
        Args:
            workflow_name: Name of the workflow
            workflow_id: Unique workflow ID
            attributes: Additional attributes to add to the span
        """
        if not self.tracer:
            yield
            return
        
        span_name = f"workflow.{workflow_name}"
        span_attributes = {
            "workflow.name": workflow_name,
            "workflow.id": workflow_id,
            "bmad.component": "workflow",
        }
        
        if attributes:
            span_attributes.update(attributes)
        
        start_time = time.time()
        
        with self.tracer.start_as_current_span(span_name, attributes=span_attributes) as span:
            try:
                # Execute the workflow
                yield span
                
                # Mark as successful
                span.set_status(Status(StatusCode.OK))
                self.metrics["workflow_executions"].labels(
                    workflow_name=workflow_name,
                    status="success"
                ).inc()
                
            except Exception as e:
                # Mark as failed
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                
                self.metrics["workflow_executions"].labels(
                    workflow_name=workflow_name,
                    status="error"
                ).inc()
                
                raise
            
            finally:
                # Update duration metrics
                duration = time.time() - start_time
                self.metrics["workflow_duration"].labels(
                    workflow_name=workflow_name
                ).observe(duration)
                
                # Add duration attribute
                span.set_attribute("duration.seconds", duration)
    
    def trace_llm_call(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        status: str = "success",
        error: Optional[str] = None
    ):
        """
        Trace an LLM API call.
        
        Args:
            provider: LLM provider name
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            status: Call status (success/error)
            error: Error message if failed
        """
        if not self.tracer:
            return
        
        span_name = f"llm.{provider}.{model}"
        span_attributes = {
            "llm.provider": provider,
            "llm.model": model,
            "llm.prompt_tokens": prompt_tokens,
            "llm.completion_tokens": completion_tokens,
            "llm.total_tokens": prompt_tokens + completion_tokens,
            "bmad.component": "llm",
        }
        
        if error:
            span_attributes["llm.error"] = error
        
        with self.tracer.start_as_current_span(span_name, attributes=span_attributes) as span:
            # Update metrics
            self.metrics["llm_calls"].labels(
                provider=provider,
                model=model,
                status=status
            ).inc()
            
            self.metrics["llm_tokens"].labels(
                provider=provider,
                model=model,
                direction="prompt"
            ).inc(prompt_tokens)
            
            self.metrics["llm_tokens"].labels(
                provider=provider,
                model=model,
                direction="completion"
            ).inc(completion_tokens)
            
            if status == "error":
                span.set_status(Status(StatusCode.ERROR, error))
            else:
                span.set_status(Status(StatusCode.OK))
    
    def add_span_event(
        self,
        span,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ):
        """Add an event to the current span."""
        if span and self.config.trace_level in [TraceLevel.DETAILED, TraceLevel.DEBUG]:
            span.add_event(name, attributes=attributes, timestamp=timestamp)
    
    def add_span_attribute(self, span, key: str, value: Any):
        """Add an attribute to the current span."""
        if span:
            span.set_attribute(key, value)
    
    def create_child_span(
        self,
        name: str,
        parent_span=None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Create a child span."""
        if not self.tracer:
            return None
        
        if parent_span:
            context = trace.set_span_in_context(parent_span)
            return self.tracer.start_span(name, attributes=attributes, context=context)
        else:
            return self.tracer.start_span(name, attributes=attributes)
    
    @contextmanager
    def start_span(self, name: str, level: TraceLevel = TraceLevel.DETAILED, parent=None, attributes: Optional[Dict[str, Any]] = None):
        """Start a span as a context manager."""
        if not self.tracer:
            yield None
            return
        
        # Add level-specific attributes
        span_attributes = attributes or {}
        span_attributes["trace.level"] = level.value
        
        if parent:
            context = trace.set_span_in_context(parent)
            span = self.tracer.start_span(name, attributes=span_attributes, context=context)
        else:
            span = self.tracer.start_span(name, attributes=span_attributes)
        
        try:
            yield span
        finally:
            span.end()
    
    def get_trace_id(self) -> Optional[str]:
        """Get the current trace ID."""
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            return format(current_span.get_span_context().trace_id, "032x")
        return None
    
    def get_span_id(self) -> Optional[str]:
        """Get the current span ID."""
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            return format(current_span.get_span_context().span_id, "016x")
        return None
    
    def export_traces(self):
        """Force export of all pending traces."""
        if self.tracer_provider:
            self.tracer_provider.force_flush()
    
    def shutdown(self):
        """Shutdown the tracer and export remaining traces."""
        if self.tracer_provider:
            self.export_traces()
            self.tracer_provider.shutdown()

# Global tracer instance
_global_tracer: Optional[BMADTracer] = None

def initialize_tracing(config: TracingConfig) -> BMADTracer:
    """Initialize global tracing."""
    global _global_tracer
    _global_tracer = BMADTracer(config)
    return _global_tracer

def get_tracer() -> Optional[BMADTracer]:
    """Get the global tracer instance."""
    return _global_tracer

def trace_agent(agent_name: str, task_name: str, workflow_id: Optional[str] = None):
    """Decorator for tracing agent functions."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if not tracer:
                return await func(*args, **kwargs)
            
            with tracer.trace_agent_execution(agent_name, task_name, workflow_id):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if not tracer:
                return func(*args, **kwargs)
            
            with tracer.trace_agent_execution(agent_name, task_name, workflow_id):
                return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def trace_workflow(workflow_name: str, workflow_id: str):
    """Decorator for tracing workflow functions."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if not tracer:
                return await func(*args, **kwargs)
            
            with tracer.trace_workflow_execution(workflow_name, workflow_id):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            if not tracer:
                return func(*args, **kwargs)
            
            with tracer.trace_workflow_execution(workflow_name, workflow_id):
                return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 