"""
Performance Monitor CLI Commands

Command-line argument parsing and dispatch for Performance Monitor CLI.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from .handlers import PerformanceMonitorHandlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PerformanceMonitorCommands:
    """Command-line interface for Performance Monitor CLI."""
    
    def __init__(self):
        self.handlers = PerformanceMonitorHandlers()
    
    def setup_parser(self):
        """Setup argument parser."""
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

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Start monitoring command
        start_parser = subparsers.add_parser("start-monitoring", help="Start performance monitoring")
        start_parser.add_argument("--interval", type=float, default=5.0, help="Monitoring interval in seconds")

        # Stop monitoring command
        subparsers.add_parser("stop-monitoring", help="Stop performance monitoring")

        # System summary command
        subparsers.add_parser("system-summary", help="Show system performance summary")

        # Agent summary command
        agent_summary_parser = subparsers.add_parser("agent-summary", help="Show agent performance summary")
        agent_summary_parser.add_argument("agent_name", help="Name of the agent")

        # List agents command
        subparsers.add_parser("list-agents", help="List all monitored agents")

        # Show alerts command
        alerts_parser = subparsers.add_parser("show-alerts", help="Show performance alerts")
        alerts_parser.add_argument("--agent", help="Filter by agent name")
        alerts_parser.add_argument("--level", choices=["warning", "critical"], help="Filter by alert level")

        # Create profile command
        create_profile_parser = subparsers.add_parser("create-profile", help="Create agent performance profile")
        create_profile_parser.add_argument("agent_name", help="Name of the agent")
        create_profile_parser.add_argument("--cpu-warning", type=float, default=70.0, help="CPU warning threshold")
        create_profile_parser.add_argument("--cpu-critical", type=float, default=85.0, help="CPU critical threshold")
        create_profile_parser.add_argument("--response-warning", type=float, default=5.0, help="Response time warning threshold")
        create_profile_parser.add_argument("--response-critical", type=float, default=10.0, help="Response time critical threshold")

        # Update thresholds command
        update_thresholds_parser = subparsers.add_parser("update-thresholds", help="Update agent thresholds")
        update_thresholds_parser.add_argument("agent_name", help="Name of the agent")
        update_thresholds_parser.add_argument("metric_type", help="Metric type to update")
        update_thresholds_parser.add_argument("--warning", type=float, help="Warning threshold")
        update_thresholds_parser.add_argument("--critical", type=float, help="Critical threshold")

        # Export data command
        export_parser = subparsers.add_parser("export-data", help="Export performance data")
        export_parser.add_argument("--format", choices=["json"], default="json", help="Export format")
        export_parser.add_argument("--output", help="Output file path")

        # Simulate task command
        simulate_parser = subparsers.add_parser("simulate-task", help="Simulate a task for testing")
        simulate_parser.add_argument("agent_name", help="Name of the agent")
        simulate_parser.add_argument("--duration", type=float, default=2.0, help="Task duration in seconds")
        simulate_parser.add_argument("--success", type=bool, default=True, help="Task success status")

        return parser
    
    def execute_command(self, args):
        """Execute the parsed command."""
        if not args.command:
            self.setup_parser().print_help()
            return

        try:
            if args.command == "start-monitoring":
                return asyncio.run(self.handlers.start_monitoring(args.interval))

            elif args.command == "stop-monitoring":
                return asyncio.run(self.handlers.stop_monitoring())

            elif args.command == "system-summary":
                return asyncio.run(self.handlers.show_system_summary())

            elif args.command == "agent-summary":
                return asyncio.run(self.handlers.show_agent_summary(args.agent_name))

            elif args.command == "list-agents":
                return asyncio.run(self.handlers.list_agents())

            elif args.command == "show-alerts":
                return asyncio.run(self.handlers.show_alerts(args.agent, args.level))

            elif args.command == "create-profile":
                return asyncio.run(self.handlers.create_agent_profile(
                    agent_name=args.agent_name,
                    cpu_warning=args.cpu_warning,
                    cpu_critical=args.cpu_critical,
                    response_warning=args.response_warning,
                    response_critical=args.response_critical
                ))

            elif args.command == "update-thresholds":
                return asyncio.run(self.handlers.update_thresholds(
                    agent_name=args.agent_name,
                    metric_type=args.metric_type,
                    warning=args.warning,
                    critical=args.critical
                ))

            elif args.command == "export-data":
                return asyncio.run(self.handlers.export_data(format=args.format, output_file=args.output))

            elif args.command == "simulate-task":
                return asyncio.run(self.handlers.simulate_task(
                    agent_name=args.agent_name,
                    duration=args.duration,
                    success=args.success
                ))

        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"CLI error: {e}", exc_info=True)
    
    def main(self):
        """Main CLI function."""
        parser = self.setup_parser()
        args = parser.parse_args()
        return self.execute_command(args)

# Legacy function for backward compatibility
async def main():
    """Main CLI function."""
    commands = PerformanceMonitorCommands()
    return commands.main() 