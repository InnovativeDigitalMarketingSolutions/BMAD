# 📊 BMAD Performance Monitor Integration

## 📋 Overview

De BMAD Performance Monitor integratie biedt real-time performance monitoring, resource tracking, en intelligent scaling voor BMAD agents. Deze integratie maakt het mogelijk om agent performance systematisch te monitoren, alerts te genereren, en automatische scaling beslissingen te nemen.

## 🎯 **ENHANCED MCP PHASE 2 PERFORMANCE INTEGRATION** ✅ **COMPLETE**

### **Enhanced MCP Phase 2 Performance Status**
- **Status**: COMPLETE - 23/23 agents enhanced (100% complete) 🎉
- **Scope**: Enhanced MCP + Performance monitoring integration voor alle agents
- **Success Metrics**: 23/23 agents met enhanced MCP + Performance optimization functionaliteit

### **Enhanced MCP Phase 2 Performance Features**
- **Volledige Enhanced MCP integratie** voor alle agents (23/23)
- **Advanced Performance Monitoring**: Real-time performance monitoring voor alle agent-operaties via MCP
- **Performance Optimization**: Automatische performance optimalisatie via Enhanced MCP tools
- **Inter-agent Performance**: Performance monitoring van agent-communicatie via MCP
- **Enhanced CLI Performance Commands**: Nieuwe performance-gerelateerde CLI commands voor alle agents
- **Performance Tracing**: OpenTelemetry-gebaseerde performance tracing voor alle agent-operaties
- **Performance Validation**: Uitgebreide performance checks en optimization via Enhanced MCP

### **Enhanced MCP Phase 2 Performance Requirements**
- **Python Environment**: Up-to-date Python omgeving met alle dependencies
- **Enhanced MCP Tools**: Alle agents hebben toegang tot enhanced MCP performance tools
- **Performance Monitoring**: Correcte configuratie van performance monitoring endpoints
- **Agent Resources**: Alle agent resources en performance configuraties aanwezig

## 🎯 Features

### ✅ **Real-time Performance Monitoring**
- **System metrics**: CPU, memory, disk I/O, network I/O
- **Agent metrics**: Response time, throughput, error rate, success rate
- **Resource tracking**: Active tasks, queue size, resource utilization
- **Baseline tracking**: Automatische baseline berekening en trending

### ✅ **Intelligent Alerting**
- **Multi-level alerts**: Info, Warning, Critical, Emergency
- **Configurable thresholds**: Per agent en per metric type
- **Smart notifications**: Alert callbacks en integration hooks
- **Alert resolution**: Tracking van alert status en resolution

### ✅ **Performance Analytics**
- **Performance summaries**: Agent en system performance overzichten
- **Trend analysis**: Performance trends en patterns
- **Recommendations**: Automatische performance aanbevelingen
- **Data export**: JSON export van performance data

### ✅ **Auto-scaling Support**
- **Scaling rules**: Configurable scaling policies per agent
- **Resource thresholds**: CPU, memory, en performance thresholds
- **Instance management**: Maximum instances en scaling limits
- **Cost optimization**: Resource utilization en cost tracking

## 🏗️ Architecture

### Core Components

```python
# Performance Monitor
PerformanceMonitor
├── System Monitoring
│   ├── CPU, Memory, Disk, Network tracking
│   ├── Resource utilization analysis
│   └── System health monitoring
├── Agent Monitoring
│   ├── Task tracking and timing
│   ├── Success/error rate calculation
│   ├── Response time measurement
│   └── Queue size estimation
├── Alert Management
│   ├── Threshold checking
│   ├── Alert generation
│   ├── Alert callbacks
│   └── Alert resolution
└── Data Management
    ├── Metrics history
    ├── Baseline calculation
    ├── Performance summaries
    └── Data export
```

### Metric Types

```python
class MetricType(Enum):
    CPU_USAGE = "cpu_usage"           # CPU utilization percentage
    MEMORY_USAGE = "memory_usage"     # Memory utilization percentage
    DISK_IO = "disk_io"              # Disk I/O operations
    NETWORK_IO = "network_io"        # Network I/O operations
    RESPONSE_TIME = "response_time"   # Task response time
    THROUGHPUT = "throughput"        # Tasks per second
    ERROR_RATE = "error_rate"        # Error percentage
    SUCCESS_RATE = "success_rate"    # Success percentage
    QUEUE_SIZE = "queue_size"        # Task queue size
    ACTIVE_TASKS = "active_tasks"    # Currently active tasks
```

### Alert Levels

```python
class AlertLevel(Enum):
    INFO = "info"           # Informational alerts
    WARNING = "warning"     # Performance warnings
    CRITICAL = "critical"   # Critical performance issues
    EMERGENCY = "emergency" # Emergency situations
```

## 🚀 Quick Start

### 1. **Installation**

De Performance Monitor integratie is al geïnstalleerd als onderdeel van de BMAD setup:

```bash
# Performance monitor is automatisch beschikbaar
python3 performance_monitor_cli.py system-summary
```

### 2. **Start Monitoring**

```bash
# Start performance monitoring
python3 performance_monitor_cli.py start-monitoring --interval 5

# Of via de integrated workflow CLI
python3 integrated_workflow_cli.py start-monitoring --interval 5
```

### 3. **View Performance Data**

```bash
# System performance summary
python3 performance_monitor_cli.py system-summary

# Agent performance summary
python3 performance_monitor_cli.py agent-summary ProductOwner

# Performance alerts
python3 performance_monitor_cli.py show-alerts
```

### 4. **Export Performance Data**

```bash
# Export performance data
python3 performance_monitor_cli.py export-data --format json --output performance.json
```

## 📚 Usage Examples

### **Creating Agent Performance Profiles**

```python
from bmad.agents.core.agent_performance_monitor import (
    AgentPerformanceProfile, MetricType, AlertLevel, get_performance_monitor
)

monitor = get_performance_monitor()

# Create a performance profile for a custom agent
profile = AgentPerformanceProfile(
    agent_name="CustomAgent",
    thresholds={
        MetricType.CPU_USAGE: {
            AlertLevel.WARNING: 70.0,
            AlertLevel.CRITICAL: 85.0
        },
        MetricType.RESPONSE_TIME: {
            AlertLevel.WARNING: 5.0,
            AlertLevel.CRITICAL: 10.0
        },
        MetricType.ERROR_RATE: {
            AlertLevel.WARNING: 5.0,
            AlertLevel.CRITICAL: 10.0
        }
    },
    scaling_rules={
        "cpu_threshold": 75.0,
        "memory_threshold": 80.0,
        "max_instances": 3
    }
)

monitor.register_agent_profile(profile)
```

### **Task Performance Tracking**

```python
# Start tracking a task
task_id = "workflow_123_task_456"
monitor.start_task_tracking("ProductOwner", task_id)

# Execute the task
try:
    # ... task execution ...
    result = "success"
except Exception as e:
    result = "failure"

# End tracking
monitor.end_task_tracking("ProductOwner", task_id, success=(result == "success"))
```

### **Performance Analysis**

```python
# Get agent performance summary
summary = monitor.get_agent_performance_summary("ProductOwner")

print(f"Agent: {summary['agent_name']}")
print(f"Current CPU: {summary['current_metrics']['cpu_usage']['value']}%")
print(f"Response Time: {summary['current_metrics']['response_time']['value']}s")
print(f"Error Rate: {summary['current_metrics']['error_rate']['value']}%")

# Get recommendations
for recommendation in summary['recommendations']:
    print(f"💡 {recommendation}")
```

### **Integration with BMAD Orchestrator**

```python
from bmad.agents.core.integrated_workflow_orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Start performance monitoring
orchestrator.start_performance_monitoring(interval=5.0)

# Get system performance
system_summary = orchestrator.get_system_performance_summary()
print(f"System CPU: {system_summary['cpu_usage']}%")
print(f"Active Agents: {system_summary['active_agents']}")

# Get agent performance
agent_summary = orchestrator.get_agent_performance_summary("ProductOwner")
print(f"Agent Status: {agent_summary['monitoring_enabled']}")

# Get performance alerts
alerts = orchestrator.get_performance_alerts(agent_name="ProductOwner", level="warning")
for alert in alerts:
    print(f"Alert: {alert['message']}")
```

## 🛠️ CLI Commands

### **Performance Monitor CLI**

```bash
# Start/Stop monitoring
python3 performance_monitor_cli.py start-monitoring --interval 5
python3 performance_monitor_cli.py stop-monitoring

# System and agent summaries
python3 performance_monitor_cli.py system-summary
python3 performance_monitor_cli.py agent-summary ProductOwner

# List monitored agents
python3 performance_monitor_cli.py list-agents

# View alerts
python3 performance_monitor_cli.py show-alerts
python3 performance_monitor_cli.py show-alerts --agent ProductOwner --level warning

# Create agent profiles
python3 performance_monitor_cli.py create-profile MyAgent --cpu-warning 60 --cpu-critical 80

# Update thresholds
python3 performance_monitor_cli.py update-thresholds ProductOwner cpu_usage --warning 65 --critical 85

# Export data
python3 performance_monitor_cli.py export-data --format json --output performance.json

# Simulate tasks for testing
python3 performance_monitor_cli.py simulate-task ProductOwner --duration 3 --success true
```

### **Integrated Workflow CLI**

```bash
# Performance monitoring commands
python3 integrated_workflow_cli.py start-monitoring --interval 5
python3 integrated_workflow_cli.py stop-monitoring
python3 integrated_workflow_cli.py system-performance
python3 integrated_workflow_cli.py agent-performance ProductOwner
python3 integrated_workflow_cli.py performance-alerts --agent ProductOwner --level warning
python3 integrated_workflow_cli.py export-performance --format json --output performance.json
```

### **Enhanced MCP Phase 2 Performance Commands**

```bash
# Test Enhanced MCP performance integration voor alle agents
python -m bmad.agents.Agent.AiDeveloper.aideveloper performance-optimization
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper performance-optimization
python -m bmad.agents.Agent.FrontendDeveloper.frontenddeveloper performance-optimization
# ... (voor alle 23 agents)

# Test performance monitoring via Enhanced MCP
python -m bmad.agents.Agent.AiDeveloper.aideveloper enhanced-mcp
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper enhanced-mcp
# ... (voor alle 23 agents)

# Test performance tracing
python -m bmad.agents.Agent.AiDeveloper.aideveloper tracing
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper tracing
# ... (voor alle 23 agents)

# Test performance validation
python -m bmad.agents.Agent.QualityGuardian.qualityguardian performance-validation
python -m bmad.agents.Agent.TestEngineer.testengineer performance-validation
# ... (voor performance-focused agents)
```

## 🎨 Default Agent Profiles

De integratie komt met pre-configured performance profiles voor BMAD agents:

### **ProductOwner Profile**
- **CPU Warning**: 60%, **Critical**: 80%
- **Response Time Warning**: 3s, **Critical**: 8s
- **Error Rate Warning**: 3%, **Critical**: 8%
- **Auto-scaling**: Enabled, Max 3 instances
- **Enhanced MCP Phase 2**: Volledige Enhanced MCP + Performance optimization

### **Architect Profile**
- **CPU Warning**: 70%, **Critical**: 85%
- **Response Time Warning**: 5s, **Critical**: 12s
- **Error Rate Warning**: 2%, **Critical**: 5%
- **Auto-scaling**: Enabled, Max 2 instances
- **Enhanced MCP Phase 2**: Volledige Enhanced MCP + Performance optimization

### **TestEngineer Profile**
- **CPU Warning**: 80%, **Critical**: 90%
- **Response Time Warning**: 10s, **Critical**: 20s
- **Error Rate Warning**: 5%, **Critical**: 10%
- **Auto-scaling**: Enabled, Max 5 instances
- **Enhanced MCP Phase 2**: Volledige Enhanced MCP + Performance optimization

### **All Other Agents (23/23)**
- **Enhanced MCP Phase 2**: Volledige Enhanced MCP + Performance optimization
- **Performance Monitoring**: Real-time performance monitoring via MCP
- **Performance Optimization**: Automatische performance optimalisatie
- **Performance Tracing**: OpenTelemetry-gebaseerde performance tracing

## 🔧 Configuration

### **Monitoring Configuration**

```python
# Performance monitor configuration
monitor_config = {
    "monitoring_interval": 5.0,  # seconds
    "metrics_history_size": 1000,  # number of metrics to keep
    "baseline_smoothing": 0.1,  # smoothing factor for baselines
    "alert_cooldown": 300,  # seconds between repeated alerts
    "max_alerts": 1000  # maximum number of alerts to store
}
```

### **Threshold Configuration**

```python
# Default thresholds per metric type
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
        AlertLevel.WARNING: 5.0,
        AlertLevel.CRITICAL: 10.0,
        AlertLevel.EMERGENCY: 30.0
    },
    MetricType.ERROR_RATE: {
        AlertLevel.WARNING: 5.0,
        AlertLevel.CRITICAL: 10.0,
        AlertLevel.EMERGENCY: 20.0
    }
}
```

## 📊 Performance Data

### **Performance Summary Structure**

```python
{
    "agent_name": "ProductOwner",
    "monitoring_enabled": True,
    "auto_scaling_enabled": True,
    "baseline_metrics": {
        "cpu_usage": 45.2,
        "response_time": 2.1,
        "error_rate": 1.5
    },
    "current_metrics": {
        "cpu_usage": {"value": 52.3, "unit": "%"},
        "response_time": {"value": 2.8, "unit": "seconds"},
        "error_rate": {"value": 2.1, "unit": "%"},
        "success_rate": {"value": 97.9, "unit": "%"},
        "active_tasks": {"value": 3, "unit": "count"}
    },
    "alerts": [
        {
            "level": "warning",
            "message": "CPU usage is 52.3% (threshold: 60.0%)",
            "timestamp": 1640995200.0,
            "resolved": False
        }
    ],
    "recommendations": [
        "Consider scaling up CPU resources or optimizing task distribution"
    ]
}
```

### **Alert Structure**

```python
{
    "alert_id": "ProductOwner_cpu_usage_1640995200",
    "level": "warning",
    "message": "CPU usage is 75.2% (threshold: 70.0%)",
    "agent_name": "ProductOwner",
    "metric_type": "cpu_usage",
    "current_value": 75.2,
    "threshold": 70.0,
    "timestamp": 1640995200.0,
    "resolved": False
}
```

## 🔗 Integration Points

### **BMAD Orchestrator Integration**

De Performance Monitor is volledig geïntegreerd met de BMAD Orchestrator:

```python
# Automatic task tracking
async def _execute_task_with_integrations(self, task, workflow_id, context, integration_level, parent_span):
    # Start performance tracking
    task_id = f"{workflow_id}_{task.id}"
    self.performance_monitor.start_task_tracking(task.agent, task_id)
    
    try:
        # Execute task
        result = await self._execute_agent_task(task, context)
        # End tracking with success
        self.performance_monitor.end_task_tracking(task.agent, task_id, success=True)
        return result
    except Exception as e:
        # End tracking with failure
        self.performance_monitor.end_task_tracking(task.agent, task_id, success=False)
        raise
```

### **Alert Callbacks**

```python
# Custom alert handler
def handle_performance_alert(alert):
    if alert.level == AlertLevel.CRITICAL:
        # Send notification
        send_slack_notification(f"Critical alert: {alert.message}")
        
        # Auto-scale if needed
        if alert.metric_type == MetricType.CPU_USAGE:
            scale_up_agent(alert.agent_name)

# Register alert callback
monitor.add_alert_callback(handle_performance_alert)
```

### **CI/CD Integration**

```yaml
# GitHub Actions workflow
- name: Performance Monitoring
  run: |
    python3 integrated_workflow_cli.py start-monitoring --interval 10
    
    # Run tests
    python3 integrated_workflow_cli.py execute product-development
    
    # Check performance
    python3 integrated_workflow_cli.py system-performance
    
    # Export performance data
    python3 integrated_workflow_cli.py export-performance --output performance_report.json
```

## 🚀 Advanced Features

### **Custom Metric Collection**

```python
class CustomPerformanceMonitor(PerformanceMonitor):
    async def _collect_custom_metrics(self, agent_name: str):
        """Collect custom metrics for an agent."""
        # Custom metric collection logic
        custom_metric = await self._calculate_custom_metric(agent_name)
        self._record_metric(agent_name, MetricType.CUSTOM, custom_metric, "units")
    
    async def _calculate_custom_metric(self, agent_name: str) -> float:
        """Calculate a custom performance metric."""
        # Implementation here
        return 42.0
```

### **Performance Trend Analysis**

```python
# Analyze performance trends
def analyze_performance_trends(agent_name: str, time_window: timedelta = timedelta(hours=1)):
    """Analyze performance trends for an agent."""
    metrics = monitor.metrics_history[f"{agent_name}_cpu_usage"]
    
    # Calculate trend
    recent_metrics = [m for m in metrics if m.timestamp >= time.time() - time_window.total_seconds()]
    
    if len(recent_metrics) >= 2:
        trend = (recent_metrics[-1].value - recent_metrics[0].value) / len(recent_metrics)
        return {
            "trend": trend,
            "direction": "increasing" if trend > 0 else "decreasing",
            "magnitude": abs(trend)
        }
    
    return {"trend": 0, "direction": "stable", "magnitude": 0}
```

### **Predictive Scaling**

```python
# Predictive scaling based on trends
def predict_scaling_needs(agent_name: str) -> Dict[str, Any]:
    """Predict scaling needs based on performance trends."""
    trends = analyze_performance_trends(agent_name)
    
    if trends["direction"] == "increasing" and trends["magnitude"] > 5:
        return {
            "action": "scale_up",
            "reason": "Increasing performance trend detected",
            "urgency": "high" if trends["magnitude"] > 10 else "medium"
        }
    
    return {"action": "maintain", "reason": "Stable performance", "urgency": "low"}
```

## 🐛 Troubleshooting

### **Common Issues**

1. **No metrics being collected**
   ```bash
   # Check if monitoring is active
   python3 performance_monitor_cli.py system-summary
   
   # Start monitoring if needed
   python3 performance_monitor_cli.py start-monitoring
   ```

2. **High CPU usage from monitoring**
   ```bash
   # Increase monitoring interval
   python3 performance_monitor_cli.py start-monitoring --interval 10
   
   # Check system resources
   python3 performance_monitor_cli.py system-summary
   ```

3. **Missing agent profiles**
   ```bash
   # List current agents
   python3 performance_monitor_cli.py list-agents
   
   # Create missing profile
   python3 performance_monitor_cli.py create-profile MissingAgent
   ```

### **Debug Mode**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 performance_monitor_cli.py agent-summary ProductOwner
```

## 📈 Performance

### **Monitoring Overhead**

- **CPU overhead**: ~1-2% for basic monitoring
- **Memory overhead**: ~10-20MB for metrics storage
- **Network overhead**: Minimal (local monitoring)
- **Storage overhead**: ~1MB per 1000 metrics

### **Scalability**

- **Agents supported**: Unlimited (limited by system resources)
- **Metrics per agent**: 1000 historical metrics
- **Alerts stored**: 1000 recent alerts
- **Monitoring interval**: 1-60 seconds configurable

## 🔮 Future Enhancements

### **Enhanced MCP Phase 2 Completed** ✅
- **23/23 agents enhanced** met volledige Enhanced MCP + Performance integration
- **Advanced performance monitoring** via Enhanced MCP tools
- **Performance optimization** voor alle agent-operaties
- **Performance tracing** via OpenTelemetry
- **Enhanced CLI commands** voor performance management

### **Planned Features**

1. **Machine Learning Integration**
   - Anomaly detection
   - Predictive scaling
   - Performance forecasting

2. **Advanced Analytics**
   - Performance correlation analysis
   - Bottleneck identification
   - Optimization recommendations

3. **Distributed Monitoring**
   - Multi-node monitoring
   - Cross-agent correlation
   - Cluster-wide metrics

4. **Integration Enhancements**
   - Prometheus metrics export
   - Grafana dashboard integration
   - Slack/Teams notifications

### **Roadmap**

- **Q1 2024**: Machine learning integration
- **Q2 2024**: Advanced analytics and correlation
- **Q3 2024**: Distributed monitoring support
- **Q4 2024**: Enterprise integrations

## 📞 Support

Voor vragen of problemen met de Performance Monitor integratie:

1. **Documentation**: Bekijk deze README
2. **CLI Help**: `python3 performance_monitor_cli.py --help`
3. **Integration Help**: `python3 integrated_workflow_cli.py --help`
4. **Issues**: Open een issue in de BMAD repository

---

**📊 Performance Monitor Integration** - Empowering BMAD with real-time performance insights and intelligent scaling! 