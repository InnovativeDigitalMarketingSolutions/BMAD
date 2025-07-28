"""
BMAD Monitoring & Metrics

Dit module biedt monitoring, metrics en observability voor BMAD agents.
Implementeert Prometheus metrics, structured logging en health checks.
"""

import importlib
import json
import logging
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"  # gauge, counter, histogram

@dataclass
class HealthCheck:
    """Represents a health check result."""
    name: str
    status: str  # healthy, unhealthy, degraded
    message: str
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """
    Collects and manages metrics for BMAD agents.
    """

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()

        # Metric prefixes
        self.prefixes = {
            "agent": "bmad_agent",
            "workflow": "bmad_workflow",
            "llm": "bmad_llm",
            "cache": "bmad_cache",
            "api": "bmad_api",
            "database": "bmad_database"
        }

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None,
                     metric_type: str = "gauge", prefix: str = "bmad"):
        """
        Record een nieuwe metric.
        
        :param name: Metric naam
        :param value: Metric waarde
        :param labels: Optional labels
        :param metric_type: Type metric
        :param prefix: Metric prefix
        """
        with self.lock:
            full_name = f"{prefix}_{name}"
            metric = Metric(
                name=full_name,
                value=value,
                timestamp=time.time(),
                labels=labels or {},
                metric_type=metric_type
            )

            self.metrics[full_name].append(metric)

            # Keep only last 1000 metrics per name
            if len(self.metrics[full_name]) > 1000:
                self.metrics[full_name] = self.metrics[full_name][-1000:]

    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None,
                          prefix: str = "bmad"):
        """
        Increment een counter metric.
        
        :param name: Counter naam
        :param labels: Optional labels
        :param prefix: Metric prefix
        """
        with self.lock:
            full_name = f"{prefix}_{name}"
            self.counters[full_name] += 1
            counter_value = self.counters[full_name]

        # Record metric outside of lock to avoid deadlock
        self.record_metric(name, counter_value, labels, "counter", prefix)

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None,
                        prefix: str = "bmad"):
        """
        Record een histogram metric.
        
        :param name: Histogram naam
        :param value: Waarde
        :param labels: Optional labels
        :param prefix: Metric prefix
        """
        with self.lock:
            full_name = f"{prefix}_{name}"
            self.histograms[full_name].append(value)

            # Calculate percentiles
            if len(self.histograms[full_name]) > 0:
                sorted_values = sorted(self.histograms[full_name])
                p50 = sorted_values[len(sorted_values) // 2]
                p95 = sorted_values[int(len(sorted_values) * 0.95)]
                p99 = sorted_values[int(len(sorted_values) * 0.99)]
            else:
                p50 = p95 = p99 = 0

        # Record metrics outside of lock to avoid deadlock
        if len(self.histograms[full_name]) > 0:
            self.record_metric(f"{name}_p50", p50, labels, "gauge", prefix)
            self.record_metric(f"{name}_p95", p95, labels, "gauge", prefix)
            self.record_metric(f"{name}_p99", p99, labels, "gauge", prefix)

    @contextmanager
    def measure_time(self, name: str, labels: Optional[Dict[str, str]] = None,
                    prefix: str = "bmad"):
        """
        Context manager voor timing measurements.
        
        :param name: Timing metric naam
        :param labels: Optional labels
        :param prefix: Metric prefix
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_histogram(name, duration, labels, prefix)

    def get_metrics(self, name_filter: Optional[str] = None,
                   time_window: Optional[timedelta] = None) -> Dict[str, List[Metric]]:
        """
        Haal metrics op met optionele filtering.
        
        :param name_filter: Filter op metric naam
        :param time_window: Filter op tijd window
        :return: Gefilterde metrics
        """
        with self.lock:
            if time_window:
                cutoff_time = time.time() - time_window.total_seconds()

            filtered_metrics = {}
            for name, metrics in self.metrics.items():
                if name_filter and name_filter not in name:
                    continue

                if time_window:
                    filtered_metrics[name] = [
                        m for m in metrics if m.timestamp >= cutoff_time
                    ]
                else:
                    filtered_metrics[name] = metrics

            return filtered_metrics

    def get_prometheus_format(self) -> str:
        """
        Export metrics in Prometheus format.
        
        :return: Prometheus formatted metrics string
        """
        with self.lock:
            lines = []

            for name, metrics in self.metrics.items():
                if not metrics:
                    continue

                # Get latest metric
                latest = metrics[-1]

                # Format labels
                if latest.labels:
                    label_str = ",".join([f'{k}="{v}"' for k, v in latest.labels.items()])
                    metric_line = f"{name}{{{label_str}}} {latest.value}"
                else:
                    metric_line = f"{name} {latest.value}"

                lines.append(metric_line)

            return "\n".join(lines)

    def clear_old_metrics(self, max_age_hours: int = 24):
        """
        Verwijder oude metrics.
        
        :param max_age_hours: Maximum leeftijd in uren
        """
        with self.lock:
            cutoff_time = time.time() - (max_age_hours * 3600)

            for name in list(self.metrics.keys()):
                self.metrics[name] = [
                    m for m in self.metrics[name] if m.timestamp >= cutoff_time
                ]

                # Remove empty metric lists
                if not self.metrics[name]:
                    del self.metrics[name]

class HealthChecker:
    """
    Performs health checks for various BMAD components.
    Uses lazy loading to avoid circular imports and async wrapper pattern.
    """

    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_functions: Dict[str, Callable] = {}
        self.last_check: Dict[str, float] = {}
        self.check_interval = 300  # 5 minuten
        self._loop = None

        # Register default health checks
        self._register_default_checks()

    def register_check(self, name: str, check_function: Callable):
        """
        Registreer een health check functie.
        
        :param name: Health check naam
        :param check_function: Functie die health check uitvoert (sync of async)
        """
        self.check_functions[name] = check_function
        logger.info(f"Health check geregistreerd: {name}")

    def _register_default_checks(self):
        """Registreer default health checks."""
        # Basic system health checks
        self.register_check("system", self._check_system)
        self.register_check("python_modules", self._check_python_modules)

        # External service checks (lazy loaded)
        self.register_check("redis", self._check_redis_lazy)
        self.register_check("database", self._check_database_lazy)
        self.register_check("llm_api", self._check_llm_api_lazy)
        self.register_check("agents", self._check_agents_lazy)

    def _check_system(self) -> HealthCheck:
        """Check basic system health."""
        try:
            import psutil

            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            status = "healthy"
            if cpu_percent > 90 or memory.percent > 90:
                status = "degraded"

            return HealthCheck(
                name="system",
                status=status,
                message=f"System OK - CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%",
                timestamp=time.time(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available
                }
            )
        except ImportError:
            return HealthCheck(
                name="system",
                status="degraded",
                message="psutil not available for system monitoring",
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                name="system",
                status="unhealthy",
                message=f"System check error: {e}",
                timestamp=time.time()
            )

    def _check_python_modules(self) -> HealthCheck:
        """Check if required Python modules are available."""
        try:
            required_modules = [
                "openai", "requests", "redis", "asyncio",
                "threading", "json", "logging"
            ]

            missing_modules = []
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)

            if missing_modules:
                return HealthCheck(
                    name="python_modules",
                    status="unhealthy",
                    message=f"Missing modules: {', '.join(missing_modules)}",
                    timestamp=time.time(),
                    details={"missing_modules": missing_modules}
                )
            return HealthCheck(
                name="python_modules",
                status="healthy",
                message="All required modules available",
                timestamp=time.time(),
                details={"available_modules": required_modules}
            )
        except Exception as e:
            return HealthCheck(
                name="python_modules",
                status="unhealthy",
                message=f"Module check error: {e}",
                timestamp=time.time()
            )

    def _check_redis_lazy(self) -> HealthCheck:
        """Lazy loaded Redis health check."""
        try:
            # Lazy import to avoid circular dependencies
            redis_module = importlib.import_module("bmad.agents.core.redis_cache")
            cache = getattr(redis_module, "cache", None)

            if cache and hasattr(cache, "enabled") and cache.enabled:
                if hasattr(cache, "client") and cache.client:
                    # Try to ping Redis
                    try:
                        cache.client.ping()
                        return HealthCheck(
                            name="redis",
                            status="healthy",
                            message="Redis connection OK",
                            timestamp=time.time()
                        )
                    except Exception as e:
                        return HealthCheck(
                            name="redis",
                            status="unhealthy",
                            message=f"Redis ping failed: {e}",
                            timestamp=time.time()
                        )
                else:
                    return HealthCheck(
                        name="redis",
                        status="degraded",
                        message="Redis enabled but client not available",
                        timestamp=time.time()
                    )
            else:
                return HealthCheck(
                    name="redis",
                    status="healthy",
                    message="Redis not configured (optional)",
                    timestamp=time.time()
                )
        except ImportError:
            return HealthCheck(
                name="redis",
                status="healthy",
                message="Redis module not available (optional)",
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                name="redis",
                status="unhealthy",
                message=f"Redis check error: {e}",
                timestamp=time.time()
            )

    def _check_database_lazy(self) -> HealthCheck:
        """Lazy loaded database health check."""
        try:
            # Lazy import to avoid circular dependencies
            pool_module = importlib.import_module("bmad.agents.core.connection_pool")
            pool_manager = getattr(pool_module, "pool_manager", None)

            if pool_manager and hasattr(pool_manager, "health_check"):
                # This is async, so we need to handle it properly
                return HealthCheck(
                    name="database",
                    status="healthy",
                    message="Database pool manager available",
                    timestamp=time.time(),
                    details={"note": "Async health check available"}
                )
            return HealthCheck(
                name="database",
                status="healthy",
                message="Database not configured (optional)",
                timestamp=time.time()
            )
        except ImportError:
            return HealthCheck(
                name="database",
                status="healthy",
                message="Database module not available (optional)",
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                name="database",
                status="unhealthy",
                message=f"Database check error: {e}",
                timestamp=time.time()
            )

    def _check_llm_api_lazy(self) -> HealthCheck:
        """Lazy loaded LLM API health check."""
        try:
            # Lazy import to avoid circular dependencies
            llm_module = importlib.import_module("bmad.agents.core.llm_client")
            api_key = getattr(llm_module, "OPENAI_API_KEY", None)

            if not api_key:
                return HealthCheck(
                    name="llm_api",
                    status="unhealthy",
                    message="OpenAI API key not configured",
                    timestamp=time.time()
                )

            # Try to import OpenAI
            try:
                # Simple API test (this could be async, but we'll keep it simple for now)
                return HealthCheck(
                    name="llm_api",
                    status="healthy",
                    message="OpenAI API key configured",
                    timestamp=time.time(),
                    details={"note": "API connectivity not tested"}
                )
            except ImportError:
                return HealthCheck(
                    name="llm_api",
                    status="degraded",
                    message="OpenAI library not available",
                    timestamp=time.time()
                )
        except ImportError:
            return HealthCheck(
                name="llm_api",
                status="healthy",
                message="LLM module not available (optional)",
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                name="llm_api",
                status="unhealthy",
                message=f"LLM API check error: {e}",
                timestamp=time.time()
            )

    def _check_agents_lazy(self) -> HealthCheck:
        """Lazy loaded agent system health check."""
        try:
            # Check if core modules are available (lazy import)
            required_modules = [
                "bmad.agents.core.advanced_workflow",
                "bmad.agents.core.confidence_scoring",
                "bmad.agents.core.llm_client"
            ]

            available_modules = []
            missing_modules = []

            for module_name in required_modules:
                try:
                    importlib.import_module(module_name)
                    available_modules.append(module_name.split(".")[-1])
                except ImportError:
                    missing_modules.append(module_name.split(".")[-1])

            if missing_modules:
                return HealthCheck(
                    name="agents",
                    status="degraded",
                    message=f"Some agent modules missing: {', '.join(missing_modules)}",
                    timestamp=time.time(),
                    details={
                        "available_modules": available_modules,
                        "missing_modules": missing_modules
                    }
                )
            return HealthCheck(
                name="agents",
                status="healthy",
                message="All agent modules available",
                timestamp=time.time(),
                details={"available_modules": available_modules}
            )
        except Exception as e:
            return HealthCheck(
                name="agents",
                status="unhealthy",
                message=f"Agent system check error: {e}",
                timestamp=time.time()
            )

    def run_health_check(self, name: str) -> HealthCheck:
        """
        Voer een specifieke health check uit.
        
        :param name: Health check naam
        :return: Health check resultaat
        """
        if name not in self.check_functions:
            return HealthCheck(
                name=name,
                status="unhealthy",
                message=f"Health check '{name}' not found",
                timestamp=time.time()
            )

        try:
            check_function = self.check_functions[name]
            result = check_function()

            self.health_checks[name] = result
            self.last_check[name] = time.time()

            return result

        except Exception as e:
            result = HealthCheck(
                name=name,
                status="unhealthy",
                message=f"Health check error: {e}",
                timestamp=time.time()
            )
            self.health_checks[name] = result
            return result

    def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """
        Voer alle health checks uit.
        
        :return: Dict met health check resultaten
        """
        results = {}
        for name in self.check_functions.keys():
            results[name] = self.run_health_check(name)
        return results

    def get_health_status(self) -> Dict[str, Any]:
        """
        Haal overall health status op.
        
        :return: Health status overzicht
        """
        # Run basic checks if none exist
        if not self.health_checks:
            self.run_all_health_checks()

        healthy_count = sum(1 for check in self.health_checks.values()
                          if check.status == "healthy")
        total_count = len(self.health_checks)

        return {
            "overall_status": "healthy" if healthy_count == total_count else "unhealthy",
            "healthy_checks": healthy_count,
            "total_checks": total_count,
            "checks": {name: {
                "status": check.status,
                "message": check.message,
                "timestamp": check.timestamp
            } for name, check in self.health_checks.items()}
        }

class StructuredLogger:
    """
    Structured logging voor BMAD agents.
    """

    def __init__(self):
        self.logger = logging.getLogger("bmad")
        self._setup_logging()

    def _setup_logging(self):
        """Setup structured logging."""
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"module": "%(name)s", "message": "%(message)s"}'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler("bmad.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.setLevel(logging.INFO)

    def log_event(self, event_type: str, message: str, **kwargs):
        """
        Log een gestructureerd event.
        
        :param event_type: Type event
        :param message: Event message
        :param kwargs: Extra event data
        """
        event_data = {
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }

        self.logger.info(json.dumps(event_data))

    def log_agent_action(self, agent_name: str, action: str, **kwargs):
        """
        Log een agent actie.
        
        :param agent_name: Naam van de agent
        :param action: Actie die uitgevoerd wordt
        :param kwargs: Extra actie data
        """
        self.log_event("agent_action", f"Agent {agent_name} executed {action}",
                      agent=agent_name, action=action, **kwargs)

    def log_workflow_event(self, workflow_id: str, event: str, **kwargs):
        """
        Log een workflow event.
        
        :param workflow_id: Workflow ID
        :param event: Event type
        :param kwargs: Extra event data
        """
        self.log_event("workflow_event", f"Workflow {workflow_id}: {event}",
                      workflow_id=workflow_id, event=event, **kwargs)

    def log_performance(self, operation: str, duration: float, **kwargs):
        """
        Log performance data.
        
        :param operation: Operatie naam
        :param duration: Duur in seconden
        :param kwargs: Extra performance data
        """
        self.log_event("performance", f"Operation {operation} took {duration:.3f}s",
                      operation=operation, duration=duration, **kwargs)

# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
structured_logger = StructuredLogger()

# Convenience functions
def record_metric(name: str, value: float, **kwargs):
    """Convenience functie voor metric recording."""
    metrics_collector.record_metric(name, value, **kwargs)

def increment_counter(name: str, **kwargs):
    """Convenience functie voor counter increment."""
    metrics_collector.increment_counter(name, **kwargs)

def measure_time(name: str, **kwargs):
    """Convenience functie voor timing measurements."""
    return metrics_collector.measure_time(name, **kwargs)

def log_event(event_type: str, message: str, **kwargs):
    """Convenience functie voor event logging."""
    structured_logger.log_event(event_type, message, **kwargs)

class PerformanceMonitor:
    """
    Enhanced Performance Monitor voor BMAD agents.
    Met real-time metrics, alerting, en performance profiling.
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self.structured_logger = StructuredLogger()
        
        # Performance profiles
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Real-time monitoring
        self.performance_alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "response_time": 5.0,  # seconds
            "memory_usage": 512,   # MB
            "cpu_usage": 80,       # percentage
            "error_rate": 0.05     # 5%
        }
        
        # Performance history
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        logger.info("Performance Monitor geïnitialiseerd")
    
    def register_agent_profile(self, agent_name: str, profile: Dict[str, Any]):
        """Register performance profile voor een agent."""
        self.agent_profiles[agent_name] = profile
        logger.info(f"Performance profile geregistreerd voor agent: {agent_name}")
    
    def record_agent_performance(self, agent_name: str, operation: str, 
                               duration: float, success: bool = True, 
                               memory_usage: Optional[float] = None,
                               cpu_usage: Optional[float] = None):
        """Record agent performance metrics."""
        timestamp = time.time()
        
        # Record basic metrics
        self.metrics_collector.record_metric(
            f"agent_{operation}_duration",
            duration,
            {"agent": agent_name, "success": str(success)},
            prefix="bmad"
        )
        
        if memory_usage:
            self.metrics_collector.record_metric(
                f"agent_memory_usage",
                memory_usage,
                {"agent": agent_name},
                prefix="bmad"
            )
        
        if cpu_usage:
            self.metrics_collector.record_metric(
                f"agent_cpu_usage",
                cpu_usage,
                {"agent": agent_name},
                prefix="bmad"
            )
        
        # Store in history
        performance_record = {
            "timestamp": timestamp,
            "agent": agent_name,
            "operation": operation,
            "duration": duration,
            "success": success,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage
        }
        
        self.performance_history[agent_name].append(performance_record)
        
        # Keep only last 1000 records per agent
        if len(self.performance_history[agent_name]) > 1000:
            self.performance_history[agent_name] = self.performance_history[agent_name][-1000:]
        
        # Check for performance alerts
        self._check_performance_alerts(agent_name, performance_record)
        
        # Log performance event
        self.structured_logger.log_performance(
            operation=f"{agent_name}.{operation}",
            duration=duration,
            agent=agent_name,
            success=success
        )
    
    def _check_performance_alerts(self, agent_name: str, record: Dict[str, Any]):
        """Check for performance alerts."""
        profile = self.agent_profiles.get(agent_name, {})
        
        alerts = []
        
        # Response time alert
        if record["duration"] > profile.get("response_time_threshold", self.alert_thresholds["response_time"]):
            alerts.append({
                "type": "response_time",
                "severity": "warning",
                "message": f"Agent {agent_name} operation {record['operation']} took {record['duration']:.2f}s"
            })
        
        # Memory usage alert
        if record.get("memory_usage") and record["memory_usage"] > profile.get("memory_threshold", self.alert_thresholds["memory_usage"]):
            alerts.append({
                "type": "memory_usage",
                "severity": "warning",
                "message": f"Agent {agent_name} using {record['memory_usage']:.1f}MB memory"
            })
        
        # CPU usage alert
        if record.get("cpu_usage") and record["cpu_usage"] > profile.get("cpu_threshold", self.alert_thresholds["cpu_usage"]):
            alerts.append({
                "type": "cpu_usage",
                "severity": "warning",
                "message": f"Agent {agent_name} using {record['cpu_usage']:.1f}% CPU"
            })
        
        # Add alerts
        for alert in alerts:
            alert["timestamp"] = record["timestamp"]
            alert["agent"] = agent_name
            self.performance_alerts.append(alert)
            
            # Keep only last 100 alerts
            if len(self.performance_alerts) > 100:
                self.performance_alerts = self.performance_alerts[-100:]
            
            logger.warning(f"Performance Alert: {alert['message']}")
    
    def get_agent_performance_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get performance summary voor een agent."""
        history = self.performance_history.get(agent_name, [])
        
        if not history:
            return {"agent": agent_name, "no_data": True}
        
        # Calculate metrics
        durations = [r["duration"] for r in history]
        success_count = sum(1 for r in history if r["success"])
        total_count = len(history)
        
        return {
            "agent": agent_name,
            "total_operations": total_count,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "recent_alerts": [a for a in self.performance_alerts if a["agent"] == agent_name][-5:]
        }
    
    def get_system_performance_summary(self) -> Dict[str, Any]:
        """Get overall system performance summary."""
        import psutil
        
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Agent metrics
        agent_summaries = {}
        for agent_name in self.agent_profiles.keys():
            agent_summaries[agent_name] = self.get_agent_performance_summary(agent_name)
        
        return {
            "system": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "memory_available": memory.available / (1024**3),  # GB
                "timestamp": time.time()
            },
            "agents": agent_summaries,
            "recent_alerts": self.performance_alerts[-10:],
            "total_alerts": len(self.performance_alerts)
        }
