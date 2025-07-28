"""
BMAD Agent Performance Monitor

Dit module biedt real-time performance monitoring, resource tracking, en intelligent scaling
voor BMAD agents. Integreert met OpenTelemetry voor distributed tracing en metrics.
"""

import logging
import time
import json
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import timedelta
from collections import defaultdict, deque

# Import BMAD modules

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    QUEUE_SIZE = "queue_size"
    ACTIVE_TASKS = "active_tasks"

class AlertLevel(Enum):
    """Alert levels for performance issues."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class PerformanceMetric:
    """Represents a single performance metric."""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: float
    agent_name: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Represents a performance alert."""
    alert_id: str
    level: AlertLevel
    message: str
    metric_type: MetricType
    current_value: float
    threshold: float
    agent_name: str
    timestamp: float
    resolved: bool = False
    resolution_time: Optional[float] = None

@dataclass
class AgentPerformanceProfile:
    """Performance profile for an agent."""
    agent_name: str
    baseline_metrics: Dict[MetricType, float] = field(default_factory=dict)
    thresholds: Dict[MetricType, Dict[AlertLevel, float]] = field(default_factory=dict)
    scaling_rules: Dict[str, Any] = field(default_factory=dict)
    monitoring_enabled: bool = True
    auto_scaling_enabled: bool = True

class PerformanceMonitor:
    """
    Real-time performance monitoring for BMAD agents.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[PerformanceAlert] = []
        self.agent_profiles: Dict[str, AgentPerformanceProfile] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.start_times: Dict[str, float] = {}
        self.task_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
        
        # Resource monitoring
        self.process = psutil.Process()
        self.last_cpu_time = self.process.cpu_times()
        self.last_disk_io = psutil.disk_io_counters()
        self.last_network_io = psutil.net_io_counters()
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        logger.info("Agent Performance Monitor geïnitialiseerd")
    
    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds."""
        default_thresholds = {
            MetricType.CPU_USAGE: {
                AlertLevel.WARNING: 70.0,
                AlertLevel.CRITICAL: 85.0,
                AlertLevel.EMERGENCY: 95.0
            },
            MetricType.MEMORY_USAGE: {
                AlertLevel.WARNING: 80.0,
                AlertLevel.CRITICAL: 90.0,
                AlertLevel.EMERGENCY: 95.0
            },
            MetricType.RESPONSE_TIME: {
                AlertLevel.WARNING: 5.0,  # seconds
                AlertLevel.CRITICAL: 10.0,
                AlertLevel.EMERGENCY: 30.0
            },
            MetricType.ERROR_RATE: {
                AlertLevel.WARNING: 5.0,  # percentage
                AlertLevel.CRITICAL: 10.0,
                AlertLevel.EMERGENCY: 20.0
            },
            MetricType.QUEUE_SIZE: {
                AlertLevel.WARNING: 100,
                AlertLevel.CRITICAL: 500,
                AlertLevel.EMERGENCY: 1000
            }
        }
        
        self.default_thresholds = default_thresholds
    
    def register_agent_profile(self, profile: AgentPerformanceProfile):
        """Register a performance profile for an agent."""
        self.agent_profiles[profile.agent_name] = profile
        
        # Initialize metrics history for this agent
        for metric_type in MetricType:
            self.metrics_history[f"{profile.agent_name}_{metric_type.value}"] = deque(maxlen=1000)
        
        logger.info(f"Performance profile geregistreerd voor agent: {profile.agent_name}")
    
    def start_monitoring(self, interval: float = 5.0):
        """Start real-time performance monitoring."""
        if self.monitoring_active:
            logger.warning("Performance monitoring is al actief")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"Performance monitoring gestart met interval: {interval}s")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Performance monitoring gestopt")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._collect_agent_metrics()
                self._check_thresholds()
                self._update_baselines()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Collect system-wide performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_metric("system", MetricType.CPU_USAGE, cpu_percent, "%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._record_metric("system", MetricType.MEMORY_USAGE, memory.percent, "%")
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io and self.last_disk_io:
                read_bytes = disk_io.read_bytes - self.last_disk_io.read_bytes
                write_bytes = disk_io.write_bytes - self.last_disk_io.write_bytes
                self._record_metric("system", MetricType.DISK_IO, read_bytes + write_bytes, "bytes")
            self.last_disk_io = disk_io
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io and self.last_network_io:
                bytes_sent = network_io.bytes_sent - self.last_network_io.bytes_sent
                bytes_recv = network_io.bytes_recv - self.last_network_io.bytes_recv
                self._record_metric("system", MetricType.NETWORK_IO, bytes_sent + bytes_recv, "bytes")
            self.last_network_io = network_io
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_agent_metrics(self):
        """Collect agent-specific performance metrics."""
        for agent_name, profile in self.agent_profiles.items():
            if not profile.monitoring_enabled:
                continue
            
            try:
                # Calculate success and error rates
                total_tasks = self.success_counts[agent_name] + self.error_counts[agent_name]
                if total_tasks > 0:
                    success_rate = (self.success_counts[agent_name] / total_tasks) * 100
                    error_rate = (self.error_counts[agent_name] / total_tasks) * 100
                    
                    self._record_metric(agent_name, MetricType.SUCCESS_RATE, success_rate, "%")
                    self._record_metric(agent_name, MetricType.ERROR_RATE, error_rate, "%")
                
                # Active tasks
                active_tasks = self.task_counts[agent_name]
                self._record_metric(agent_name, MetricType.ACTIVE_TASKS, active_tasks, "count")
                
                # Queue size (simulated for now)
                queue_size = self._estimate_queue_size(agent_name)
                self._record_metric(agent_name, MetricType.QUEUE_SIZE, queue_size, "count")
                
            except Exception as e:
                logger.error(f"Error collecting metrics for agent {agent_name}: {e}")
    
    def _estimate_queue_size(self, agent_name: str) -> int:
        """Estimate queue size for an agent."""
        # This is a simplified estimation
        # In a real implementation, this would query the actual queue
        base_size = 10
        active_tasks = self.task_counts[agent_name]
        return max(0, base_size - active_tasks)
    
    def _record_metric(self, agent_name: str, metric_type: MetricType, value: float, unit: str):
        """Record a performance metric."""
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=time.time(),
            agent_name=agent_name
        )
        
        # Store in history
        key = f"{agent_name}_{metric_type.value}"
        self.metrics_history[key].append(metric)
        
        # Log metric
        logger.debug(f"Metric recorded: {agent_name} {metric_type.value} = {value} {unit}")
    
    def _check_thresholds(self):
        """Check if any metrics exceed thresholds."""
        for agent_name, profile in self.agent_profiles.items():
            if not profile.monitoring_enabled:
                continue
            
            thresholds = profile.thresholds or self.default_thresholds
            
            for metric_type, alert_levels in thresholds.items():
                current_value = self._get_current_metric_value(agent_name, metric_type)
                if current_value is None:
                    continue
                
                for alert_level, threshold in alert_levels.items():
                    if self._should_trigger_alert(metric_type, current_value, threshold):
                        self._create_alert(agent_name, metric_type, alert_level, current_value, threshold)
    
    def _get_current_metric_value(self, agent_name: str, metric_type: MetricType) -> Optional[float]:
        """Get the current value for a metric."""
        key = f"{agent_name}_{metric_type.value}"
        if key in self.metrics_history and self.metrics_history[key]:
            return self.metrics_history[key][-1].value
        return None
    
    def _should_trigger_alert(self, metric_type: MetricType, current_value: float, threshold: float) -> bool:
        """Determine if an alert should be triggered."""
        if metric_type in [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE, MetricType.ERROR_RATE]:
            return current_value >= threshold
        elif metric_type in [MetricType.RESPONSE_TIME, MetricType.QUEUE_SIZE]:
            return current_value >= threshold
        elif metric_type == MetricType.SUCCESS_RATE:
            return current_value <= threshold
        return False
    
    def _create_alert(self, agent_name: str, metric_type: MetricType, level: AlertLevel, 
                     current_value: float, threshold: float):
        """Create a performance alert."""
        alert_id = f"{agent_name}_{metric_type.value}_{int(time.time())}"
        
        messages = {
            MetricType.CPU_USAGE: f"CPU usage is {current_value:.1f}% (threshold: {threshold:.1f}%)",
            MetricType.MEMORY_USAGE: f"Memory usage is {current_value:.1f}% (threshold: {threshold:.1f}%)",
            MetricType.RESPONSE_TIME: f"Response time is {current_value:.2f}s (threshold: {threshold:.2f}s)",
            MetricType.ERROR_RATE: f"Error rate is {current_value:.1f}% (threshold: {threshold:.1f}%)",
            MetricType.QUEUE_SIZE: f"Queue size is {current_value} (threshold: {threshold})",
            MetricType.SUCCESS_RATE: f"Success rate is {current_value:.1f}% (threshold: {threshold:.1f}%)"
        }
        
        message = messages.get(metric_type, f"{metric_type.value} threshold exceeded")
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            level=level,
            message=message,
            metric_type=metric_type,
            current_value=current_value,
            threshold=threshold,
            agent_name=agent_name,
            timestamp=time.time()
        )
        
        self.alerts.append(alert)
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        logger.warning(f"Performance alert: {message} for {agent_name}")
    
    def _update_baselines(self):
        """Update baseline metrics for agents."""
        for agent_name, profile in self.agent_profiles.items():
            for metric_type in MetricType:
                current_value = self._get_current_metric_value(agent_name, metric_type)
                if current_value is not None:
                    # Simple moving average for baseline
                    if metric_type not in profile.baseline_metrics:
                        profile.baseline_metrics[metric_type] = current_value
                    else:
                        alpha = 0.1  # Smoothing factor
                        profile.baseline_metrics[metric_type] = (
                            alpha * current_value + 
                            (1 - alpha) * profile.baseline_metrics[metric_type]
                        )
    
    def start_task_tracking(self, agent_name: str, task_id: str):
        """Start tracking a task for an agent."""
        self.start_times[task_id] = time.time()
        self.task_counts[agent_name] += 1
        
        logger.debug(f"Started tracking task {task_id} for agent {agent_name}")
    
    def end_task_tracking(self, agent_name: str, task_id: str, success: bool = True):
        """End tracking a task for an agent."""
        if task_id in self.start_times:
            start_time = self.start_times[task_id]
            duration = time.time() - start_time
            
            # Record response time
            self._record_metric(agent_name, MetricType.RESPONSE_TIME, duration, "seconds")
            
            # Update counts
            if success:
                self.success_counts[agent_name] += 1
            else:
                self.error_counts[agent_name] += 1
            
            # Clean up
            del self.start_times[task_id]
            self.task_counts[agent_name] = max(0, self.task_counts[agent_name] - 1)
            
            logger.debug(f"Ended tracking task {task_id} for agent {agent_name} (success: {success})")
    
    def get_agent_performance_summary(self, agent_name: str, 
                                    time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get a performance summary for an agent."""
        if agent_name not in self.agent_profiles:
            return {}
        
        profile = self.agent_profiles[agent_name]
        summary = {
            "agent_name": agent_name,
            "monitoring_enabled": profile.monitoring_enabled,
            "auto_scaling_enabled": profile.auto_scaling_enabled,
            "baseline_metrics": profile.baseline_metrics,
            "current_metrics": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Current metrics
        for metric_type in MetricType:
            current_value = self._get_current_metric_value(agent_name, metric_type)
            if current_value is not None:
                summary["current_metrics"][metric_type.value] = {
                    "value": current_value,
                    "unit": self._get_metric_unit(metric_type)
                }
        
        # Recent alerts
        cutoff_time = time.time() - (time_window.total_seconds() if time_window else 3600)
        recent_alerts = [
            alert for alert in self.alerts 
            if alert.agent_name == agent_name and alert.timestamp >= cutoff_time
        ]
        summary["alerts"] = [
            {
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "resolved": alert.resolved
            }
            for alert in recent_alerts
        ]
        
        # Performance recommendations
        summary["recommendations"] = self._generate_recommendations(agent_name, summary)
        
        return summary
    
    def _get_metric_unit(self, metric_type: MetricType) -> str:
        """Get the unit for a metric type."""
        units = {
            MetricType.CPU_USAGE: "%",
            MetricType.MEMORY_USAGE: "%",
            MetricType.DISK_IO: "bytes",
            MetricType.NETWORK_IO: "bytes",
            MetricType.RESPONSE_TIME: "seconds",
            MetricType.THROUGHPUT: "tasks/second",
            MetricType.ERROR_RATE: "%",
            MetricType.SUCCESS_RATE: "%",
            MetricType.QUEUE_SIZE: "count",
            MetricType.ACTIVE_TASKS: "count"
        }
        return units.get(metric_type, "unknown")
    
    def _generate_recommendations(self, agent_name: str, summary: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        current_metrics = summary["current_metrics"]
        summary["baseline_metrics"]
        
        # CPU recommendations
        if "cpu_usage" in current_metrics:
            cpu_usage = current_metrics["cpu_usage"]["value"]
            if cpu_usage > 80:
                recommendations.append("Consider scaling up CPU resources or optimizing task distribution")
            elif cpu_usage < 20:
                recommendations.append("Consider scaling down CPU resources to reduce costs")
        
        # Memory recommendations
        if "memory_usage" in current_metrics:
            memory_usage = current_metrics["memory_usage"]["value"]
            if memory_usage > 85:
                recommendations.append("High memory usage detected. Consider memory optimization or scaling")
        
        # Response time recommendations
        if "response_time" in current_metrics:
            response_time = current_metrics["response_time"]["value"]
            if response_time > 10:
                recommendations.append("Slow response times detected. Consider task optimization or parallelization")
        
        # Error rate recommendations
        if "error_rate" in current_metrics:
            error_rate = current_metrics["error_rate"]["value"]
            if error_rate > 5:
                recommendations.append("High error rate detected. Review error handling and task logic")
        
        return recommendations
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add a callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def get_system_performance_summary(self) -> Dict[str, Any]:
        """Get system-wide performance summary."""
        return {
            "cpu_usage": self._get_current_metric_value("system", MetricType.CPU_USAGE),
            "memory_usage": self._get_current_metric_value("system", MetricType.MEMORY_USAGE),
            "disk_io": self._get_current_metric_value("system", MetricType.DISK_IO),
            "network_io": self._get_current_metric_value("system", MetricType.NETWORK_IO),
            "active_agents": len([p for p in self.agent_profiles.values() if p.monitoring_enabled]),
            "total_alerts": len([a for a in self.alerts if not a.resolved])
        }
    
    def export_performance_data(self, format: str = "json") -> str:
        """Export performance data."""
        if format == "json":
            data = {
                "timestamp": time.time(),
                "system_summary": self.get_system_performance_summary(),
                "agent_summaries": {
                    name: self.get_agent_performance_summary(name)
                    for name in self.agent_profiles.keys()
                },
                "recent_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "level": alert.level.value,
                        "message": alert.message,
                        "agent_name": alert.agent_name,
                        "timestamp": alert.timestamp,
                        "resolved": alert.resolved
                    }
                    for alert in self.alerts[-100:]  # Last 100 alerts
                ]
            }
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def create_default_agent_profiles():
    """Create default performance profiles for BMAD agents."""
    monitor = get_performance_monitor()
    
    # Product Owner profile
    product_owner_profile = AgentPerformanceProfile(
        agent_name="ProductOwner",
        thresholds={
            MetricType.CPU_USAGE: {AlertLevel.WARNING: 60.0, AlertLevel.CRITICAL: 80.0},
            MetricType.RESPONSE_TIME: {AlertLevel.WARNING: 3.0, AlertLevel.CRITICAL: 8.0},
            MetricType.ERROR_RATE: {AlertLevel.WARNING: 3.0, AlertLevel.CRITICAL: 8.0}
        },
        scaling_rules={
            "cpu_threshold": 70.0,
            "memory_threshold": 80.0,
            "max_instances": 3
        }
    )
    monitor.register_agent_profile(product_owner_profile)
    
    # Architect profile
    architect_profile = AgentPerformanceProfile(
        agent_name="Architect",
        thresholds={
            MetricType.CPU_USAGE: {AlertLevel.WARNING: 70.0, AlertLevel.CRITICAL: 85.0},
            MetricType.RESPONSE_TIME: {AlertLevel.WARNING: 5.0, AlertLevel.CRITICAL: 12.0},
            MetricType.ERROR_RATE: {AlertLevel.WARNING: 2.0, AlertLevel.CRITICAL: 5.0}
        },
        scaling_rules={
            "cpu_threshold": 75.0,
            "memory_threshold": 85.0,
            "max_instances": 2
        }
    )
    monitor.register_agent_profile(architect_profile)
    
    # TestEngineer profile
    testengineer_profile = AgentPerformanceProfile(
        agent_name="TestEngineer",
        thresholds={
            MetricType.CPU_USAGE: {AlertLevel.WARNING: 80.0, AlertLevel.CRITICAL: 90.0},
            MetricType.RESPONSE_TIME: {AlertLevel.WARNING: 10.0, AlertLevel.CRITICAL: 20.0},
            MetricType.ERROR_RATE: {AlertLevel.WARNING: 5.0, AlertLevel.CRITICAL: 10.0}
        },
        scaling_rules={
            "cpu_threshold": 85.0,
            "memory_threshold": 90.0,
            "max_instances": 5
        }
    )
    monitor.register_agent_profile(testengineer_profile)
    
    logger.info("Default agent performance profiles created")

# Initialize default profiles when module is imported
if __name__ != "__main__":
    create_default_agent_profiles() 