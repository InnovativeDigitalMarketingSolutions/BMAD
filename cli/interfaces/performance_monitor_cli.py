"""
Performance Monitor CLI Interface

Thin wrapper interface for Performance Monitor CLI functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path
from cli.commands.performance_monitor.commands import PerformanceMonitorCommands
from cli.commands.performance_monitor.handlers import PerformanceMonitorHandlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PerformanceMonitorCLI:
    """CLI for managing agent performance monitoring."""

    def __init__(self):
        self.handlers = PerformanceMonitorHandlers()
        self.commands = PerformanceMonitorCommands()

    async def start_monitoring(self, interval: float = 5.0):
        """Start performance monitoring."""
        return await self.handlers.start_monitoring(interval)

    async def stop_monitoring(self):
        """Stop performance monitoring."""
        return await self.handlers.stop_monitoring()

    async def show_system_summary(self):
        """Show system-wide performance summary."""
        return await self.handlers.show_system_summary()

    async def show_agent_summary(self, agent_name: str):
        """Show performance summary for a specific agent."""
        return await self.handlers.show_agent_summary(agent_name)

    async def list_agents(self):
        """List all monitored agents."""
        return await self.handlers.list_agents()

    async def show_alerts(self, agent_name=None, level=None):
        """Show performance alerts."""
        return await self.handlers.show_alerts(agent_name, level)

    async def create_agent_profile(self, agent_name: str, cpu_warning: float = 70.0,
                                 cpu_critical: float = 85.0, response_warning: float = 5.0,
                                 response_critical: float = 10.0):
        """Create a new agent performance profile."""
        return await self.handlers.create_agent_profile(agent_name, cpu_warning, cpu_critical, response_warning, response_critical)

    async def update_thresholds(self, agent_name: str, metric_type: str,
                              warning=None, critical=None):
        """Update thresholds for an agent."""
        return await self.handlers.update_thresholds(agent_name, metric_type, warning, critical)

    async def export_data(self, format: str = "json", output_file=None):
        """Export performance data."""
        return await self.handlers.export_data(format, output_file)

    async def simulate_task(self, agent_name: str, duration: float = 2.0, success: bool = True):
        """Simulate a task for testing purposes."""
        return await self.handlers.simulate_task(agent_name, duration, success)

def main():
    """Main CLI function."""
    commands = PerformanceMonitorCommands()
    success = commands.main()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 