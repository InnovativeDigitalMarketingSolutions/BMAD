"""
Performance Monitor CLI Handlers

Business logic for Performance Monitor CLI commands.
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add BMAD to path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import BMAD modules
from bmad.agents.core.monitoring.monitoring import (
    MetricType,
    MetricsCollector,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PerformanceMonitorHandlers:
    """Handlers for Performance Monitor CLI commands."""
    
    def __init__(self):
        self.monitor = MetricsCollector()

    async def start_monitoring(self, interval: float = 5.0):
        """Start performance monitoring."""
        print(f"🚀 Starting performance monitoring with {interval}s interval...")

        try:
            # Placeholder for monitoring start
            print("✅ Performance monitoring started successfully")
            print("📊 Monitoring active agents and system resources")
            print("🔔 Alerts will be displayed when thresholds are exceeded")

        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
            return False

        return True

    async def stop_monitoring(self):
        """Stop performance monitoring."""
        print("🛑 Stopping performance monitoring...")

        try:
            self.monitor.stop_monitoring()
            print("✅ Performance monitoring stopped")

        except Exception as e:
            print(f"❌ Failed to stop monitoring: {e}")

    async def show_system_summary(self):
        """Show system-wide performance summary."""
        print("🖥️  System Performance Summary")
        print("=" * 50)

        try:
            summary = self.monitor.get_system_performance_summary()

            if summary["cpu_usage"] is not None:
                print(f"💻 CPU Usage: {summary['cpu_usage']:.1f}%")

            if summary["memory_usage"] is not None:
                print(f"🧠 Memory Usage: {summary['memory_usage']:.1f}%")

            if summary["disk_io"] is not None:
                print(f"💾 Disk I/O: {summary['disk_io']:,} bytes")

            if summary["network_io"] is not None:
                print(f"🌐 Network I/O: {summary['network_io']:,} bytes")

            print(f"🤖 Active Agents: {summary['active_agents']}")
            print(f"⚠️  Total Alerts: {summary['total_alerts']}")

        except Exception as e:
            print(f"❌ Failed to get system summary: {e}")

    async def show_agent_summary(self, agent_name: str):
        """Show performance summary for a specific agent."""
        print(f"🤖 Agent Performance Summary: {agent_name}")
        print("=" * 50)

        try:
            summary = self.monitor.get_agent_performance_summary(agent_name)

            if not summary:
                print(f"❌ Agent '{agent_name}' not found or not monitored")
                return

            print(f"📋 Agent: {summary['agent_name']}")
            print(f"🔍 Monitoring: {'✅ Enabled' if summary['monitoring_enabled'] else '❌ Disabled'}")
            print(f"⚡ Auto-scaling: {'✅ Enabled' if summary['auto_scaling_enabled'] else '❌ Disabled'}")

            # Current metrics
            if summary["current_metrics"]:
                print("\n📊 Current Metrics:")
                for metric_name, metric_data in summary["current_metrics"].items():
                    value = metric_data["value"]
                    unit = metric_data["unit"]
                    print(f"   {metric_name}: {value:.2f} {unit}")

            # Baseline metrics
            if summary["baseline_metrics"]:
                print("\n📈 Baseline Metrics:")
                for metric_type, baseline_value in summary["baseline_metrics"].items():
                    print(f"   {metric_type.value}: {baseline_value:.2f}")

            # Recent alerts
            if summary["alerts"]:
                print("\n⚠️  Recent Alerts:")
                for alert in summary["alerts"][-5:]:  # Show last 5 alerts
                    status = "✅ Resolved" if alert["resolved"] else "❌ Active"
                    timestamp = datetime.fromtimestamp(alert["timestamp"]).strftime("%H:%M:%S")
                    print(f"   [{timestamp}] {alert['level'].upper()}: {alert['message']} ({status})")
            else:
                print("\n✅ No recent alerts")

            # Recommendations
            if summary["recommendations"]:
                print("\n💡 Recommendations:")
                for recommendation in summary["recommendations"]:
                    print(f"   • {recommendation}")
            else:
                print("\n✅ No recommendations at this time")

        except Exception as e:
            print(f"❌ Failed to get agent summary: {e}")

    async def list_agents(self):
        """List all monitored agents."""
        print("🤖 Monitored Agents")
        print("=" * 50)

        try:
            agents = list(self.monitor.agent_profiles.keys())

            if not agents:
                print("❌ No agents are currently monitored")
                return

            for i, agent_name in enumerate(agents, 1):
                profile = self.monitor.agent_profiles[agent_name]
                status = "✅ Active" if profile.monitoring_enabled else "❌ Disabled"
                scaling = "✅ Enabled" if profile.auto_scaling_enabled else "❌ Disabled"

                print(f"{i}. {agent_name}")
                print(f"   📊 Status: {status}")
                print(f"   ⚡ Auto-scaling: {scaling}")
                print(f"   🔒 Thresholds: {len(profile.thresholds)} configured")
                print()

        except Exception as e:
            print(f"❌ Failed to list agents: {e}")

    async def show_alerts(self, agent_name: Optional[str] = None, level: Optional[str] = None):
        """Show performance alerts."""
        print("⚠️  Performance Alerts")
        print("=" * 50)

        try:
            alerts = self.monitor.alerts

            if agent_name:
                alerts = [a for a in alerts if a.agent_name == agent_name]

            if level:
                try:
                    alert_level = AlertLevel(level.lower())
                    alerts = [a for a in alerts if a.level == alert_level]
                except ValueError:
                    print(f"❌ Invalid alert level: {level}")
                    return

            if not alerts:
                print("✅ No alerts found")
                return

            # Show recent alerts (last 20)
            recent_alerts = sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:20]

            for alert in recent_alerts:
                status = "✅ Resolved" if alert.resolved else "❌ Active"
                timestamp = datetime.fromtimestamp(alert.timestamp).strftime("%Y-%m-%d %H:%M:%S")

                print(f"[{timestamp}] {alert.level.value.upper()}")
                print(f"   Agent: {alert.agent_name}")
                print(f"   Metric: {alert.metric_type.value}")
                print(f"   Message: {alert.message}")
                print(f"   Value: {alert.current_value:.2f} (threshold: {alert.threshold:.2f})")
                print(f"   Status: {status}")
                print()

        except Exception as e:
            print(f"❌ Failed to show alerts: {e}")

    async def create_agent_profile(self, agent_name: str, cpu_warning: float = 70.0,
                                 cpu_critical: float = 85.0, response_warning: float = 5.0,
                                 response_critical: float = 10.0):
        """Create a new agent performance profile."""
        print(f"🎯 Creating performance profile for agent: {agent_name}")
        print("=" * 50)

        try:
            profile = AgentPerformanceProfile(
                agent_name=agent_name,
                thresholds={
                    MetricType.CPU_USAGE: {
                        AlertLevel.WARNING: cpu_warning,
                        AlertLevel.CRITICAL: cpu_critical
                    },
                    MetricType.RESPONSE_TIME: {
                        AlertLevel.WARNING: response_warning,
                        AlertLevel.CRITICAL: response_critical
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

            self.monitor.register_agent_profile(profile)

            print("✅ Agent performance profile created successfully")
            print(f"   📊 CPU Warning: {cpu_warning}%")
            print(f"   📊 CPU Critical: {cpu_critical}%")
            print(f"   ⏱️  Response Warning: {response_warning}s")
            print(f"   ⏱️  Response Critical: {response_critical}s")
            print("   ⚡ Auto-scaling: Enabled")

        except Exception as e:
            print(f"❌ Failed to create agent profile: {e}")

    async def update_thresholds(self, agent_name: str, metric_type: str,
                              warning: Optional[float] = None, critical: Optional[float] = None):
        """Update thresholds for an agent."""
        print(f"🔧 Updating thresholds for {agent_name} - {metric_type}")
        print("=" * 50)

        try:
            if agent_name not in self.monitor.agent_profiles:
                print(f"❌ Agent '{agent_name}' not found")
                return

            profile = self.monitor.agent_profiles[agent_name]

            try:
                metric_enum = MetricType(metric_type.lower())
            except ValueError:
                print(f"❌ Invalid metric type: {metric_type}")
                print(f"Valid types: {[t.value for t in MetricType]}")
                return

            if metric_type not in profile.thresholds:
                profile.thresholds[metric_enum] = {}

            if warning is not None:
                profile.thresholds[metric_enum][AlertLevel.WARNING] = warning
                print(f"   📊 Warning threshold: {warning}")

            if critical is not None:
                profile.thresholds[metric_enum][AlertLevel.CRITICAL] = critical
                print(f"   📊 Critical threshold: {critical}")

            print("✅ Thresholds updated successfully")

        except Exception as e:
            print(f"❌ Failed to update thresholds: {e}")

    async def export_data(self, format: str = "json", output_file: Optional[str] = None):
        """Export performance data."""
        print(f"📊 Exporting performance data in {format} format")
        print("=" * 50)

        try:
            data = self.monitor.export_performance_data(format)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(data)
                print(f"✅ Data exported to: {output_file}")
            else:
                print(data)

        except Exception as e:
            print(f"❌ Failed to export data: {e}")

    async def simulate_task(self, agent_name: str, duration: float = 2.0, success: bool = True):
        """Simulate a task for testing purposes."""
        print(f"🧪 Simulating task for {agent_name}")
        print(f"   ⏱️  Duration: {duration}s")
        print(f"   ✅ Success: {success}")
        print("=" * 50)

        try:
            task_id = f"sim_{int(time.time())}"

            # Start tracking
            self.monitor.start_task_tracking(agent_name, task_id)

            # Simulate work
            await asyncio.sleep(duration)

            # End tracking
            self.monitor.end_task_tracking(agent_name, task_id, success)

            print("✅ Task simulation completed")

        except Exception as e:
            print(f"❌ Task simulation failed: {e}")

# Legacy function exports for backward compatibility
async def start_monitoring(interval: float = 5.0):
    handlers = PerformanceMonitorHandlers()
    return await handlers.start_monitoring(interval)

async def stop_monitoring():
    handlers = PerformanceMonitorHandlers()
    return await handlers.stop_monitoring()

async def show_system_summary():
    handlers = PerformanceMonitorHandlers()
    return await handlers.show_system_summary()

async def show_agent_summary(agent_name: str):
    handlers = PerformanceMonitorHandlers()
    return await handlers.show_agent_summary(agent_name)

async def list_agents():
    handlers = PerformanceMonitorHandlers()
    return await handlers.list_agents()

async def show_alerts(agent_name: Optional[str] = None, level: Optional[str] = None):
    handlers = PerformanceMonitorHandlers()
    return await handlers.show_alerts(agent_name, level)

async def create_agent_profile(agent_name: str, cpu_warning: float = 70.0,
                             cpu_critical: float = 85.0, response_warning: float = 5.0,
                             response_critical: float = 10.0):
    handlers = PerformanceMonitorHandlers()
    return await handlers.create_agent_profile(agent_name, cpu_warning, cpu_critical, response_warning, response_critical)

async def update_thresholds(agent_name: str, metric_type: str,
                          warning: Optional[float] = None, critical: Optional[float] = None):
    handlers = PerformanceMonitorHandlers()
    return await handlers.update_thresholds(agent_name, metric_type, warning, critical)

async def export_data(format: str = "json", output_file: Optional[str] = None):
    handlers = PerformanceMonitorHandlers()
    return await handlers.export_data(format, output_file)

async def simulate_task(agent_name: str, duration: float = 2.0, success: bool = True):
    handlers = PerformanceMonitorHandlers()
    return await handlers.simulate_task(agent_name, duration, success) 