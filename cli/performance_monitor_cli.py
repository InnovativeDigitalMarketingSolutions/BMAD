#!/usr/bin/env python3
"""
BMAD Performance Monitor CLI

CLI tool voor het monitoren van agent performance, metrics bekijken, en alerts beheren.
Integreert met de BMAD Performance Monitor voor real-time agent monitoring.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import time

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent))

# Import BMAD modules
from bmad.agents.core.agent_performance_monitor import (
    AgentPerformanceProfile,
    MetricType,
    AlertLevel,
    get_performance_monitor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceMonitorCLI:
    """CLI for managing agent performance monitoring."""
    
    def __init__(self):
        self.monitor = get_performance_monitor()
    
    async def start_monitoring(self, interval: float = 5.0):
        """Start performance monitoring."""
        print(f"🚀 Starting performance monitoring with {interval}s interval...")
        
        try:
            self.monitor.start_monitoring(interval)
            print("✅ Performance monitoring started successfully")
            print("📊 Monitoring active agents and system resources")
            print("🔔 Alerts will be displayed when thresholds are exceeded")
            
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
    
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
                with open(output_file, 'w') as f:
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

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD Performance Monitor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start monitoring
  python performance_monitor_cli.py start-monitoring --interval 5
  
  # Show system summary
  python performance_monitor_cli.py system-summary
  
  # Show agent summary
  python performance_monitor_cli.py agent-summary ProductOwner
  
  # List all agents
  python performance_monitor_cli.py list-agents
  
  # Show alerts
  python performance_monitor_cli.py show-alerts
  python performance_monitor_cli.py show-alerts --agent ProductOwner --level warning
  
  # Create agent profile
  python performance_monitor_cli.py create-profile MyAgent --cpu-warning 60 --cpu-critical 80
  
  # Update thresholds
  python performance_monitor_cli.py update-thresholds ProductOwner cpu_usage --warning 65 --critical 85
  
  # Export data
  python performance_monitor_cli.py export-data --format json --output performance.json
  
  # Simulate task
  python performance_monitor_cli.py simulate-task ProductOwner --duration 3 --success true
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start monitoring command
    start_parser = subparsers.add_parser('start-monitoring', help='Start performance monitoring')
    start_parser.add_argument('--interval', type=float, default=5.0, help='Monitoring interval in seconds')
    
    # Stop monitoring command
    subparsers.add_parser('stop-monitoring', help='Stop performance monitoring')
    
    # System summary command
    subparsers.add_parser('system-summary', help='Show system performance summary')
    
    # Agent summary command
    agent_summary_parser = subparsers.add_parser('agent-summary', help='Show agent performance summary')
    agent_summary_parser.add_argument('agent_name', help='Name of the agent')
    
    # List agents command
    subparsers.add_parser('list-agents', help='List all monitored agents')
    
    # Show alerts command
    alerts_parser = subparsers.add_parser('show-alerts', help='Show performance alerts')
    alerts_parser.add_argument('--agent', help='Filter by agent name')
    alerts_parser.add_argument('--level', choices=[l.value for l in AlertLevel], help='Filter by alert level')
    
    # Create profile command
    create_profile_parser = subparsers.add_parser('create-profile', help='Create agent performance profile')
    create_profile_parser.add_argument('agent_name', help='Name of the agent')
    create_profile_parser.add_argument('--cpu-warning', type=float, default=70.0, help='CPU warning threshold')
    create_profile_parser.add_argument('--cpu-critical', type=float, default=85.0, help='CPU critical threshold')
    create_profile_parser.add_argument('--response-warning', type=float, default=5.0, help='Response time warning threshold')
    create_profile_parser.add_argument('--response-critical', type=float, default=10.0, help='Response time critical threshold')
    
    # Update thresholds command
    update_thresholds_parser = subparsers.add_parser('update-thresholds', help='Update agent thresholds')
    update_thresholds_parser.add_argument('agent_name', help='Name of the agent')
    update_thresholds_parser.add_argument('metric_type', help='Metric type to update')
    update_thresholds_parser.add_argument('--warning', type=float, help='Warning threshold')
    update_thresholds_parser.add_argument('--critical', type=float, help='Critical threshold')
    
    # Export data command
    export_parser = subparsers.add_parser('export-data', help='Export performance data')
    export_parser.add_argument('--format', choices=['json'], default='json', help='Export format')
    export_parser.add_argument('--output', help='Output file path')
    
    # Simulate task command
    simulate_parser = subparsers.add_parser('simulate-task', help='Simulate a task for testing')
    simulate_parser.add_argument('agent_name', help='Name of the agent')
    simulate_parser.add_argument('--duration', type=float, default=2.0, help='Task duration in seconds')
    simulate_parser.add_argument('--success', type=bool, default=True, help='Task success status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PerformanceMonitorCLI()
    
    try:
        if args.command == 'start-monitoring':
            await cli.start_monitoring(args.interval)
        
        elif args.command == 'stop-monitoring':
            await cli.stop_monitoring()
        
        elif args.command == 'system-summary':
            await cli.show_system_summary()
        
        elif args.command == 'agent-summary':
            await cli.show_agent_summary(args.agent_name)
        
        elif args.command == 'list-agents':
            await cli.list_agents()
        
        elif args.command == 'show-alerts':
            await cli.show_alerts(args.agent, args.level)
        
        elif args.command == 'create-profile':
            await cli.create_agent_profile(
                agent_name=args.agent_name,
                cpu_warning=args.cpu_warning,
                cpu_critical=args.cpu_critical,
                response_warning=args.response_warning,
                response_critical=args.response_critical
            )
        
        elif args.command == 'update-thresholds':
            await cli.update_thresholds(
                agent_name=args.agent_name,
                metric_type=args.metric_type,
                warning=args.warning,
                critical=args.critical
            )
        
        elif args.command == 'export-data':
            await cli.export_data(format=args.format, output_file=args.output)
        
        elif args.command == 'simulate-task':
            await cli.simulate_task(
                agent_name=args.agent_name,
                duration=args.duration,
                success=args.success
            )
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CLI error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 