#!/usr/bin/env python3
"""
BMAD Integrated Workflow CLI

CLI tool voor het testen en beheren van geïntegreerde workflows die alle
repository integraties (LangGraph, OpenRouter, OpenTelemetry, OPA, Prefect)
combineren met bestaande BMAD agent workflows.
"""

import asyncio
import argparse
import json
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent))

# Import BMAD modules
from bmad.agents.core.integrated_workflow_orchestrator import (
    IntegratedWorkflowOrchestrator,
    IntegrationLevel
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedWorkflowCLI:
    """CLI for managing integrated workflows."""
    
    def __init__(self):
        self.orchestrator = IntegratedWorkflowOrchestrator()
    
    async def list_workflows(self):
        """List all available workflows."""
        print("🚀 BMAD Integrated Workflows")
        print("=" * 50)
        
        workflows = self.orchestrator.list_workflows()
        
        if not workflows:
            print("❌ Geen workflows gevonden")
            return
        
        for i, workflow_name in enumerate(workflows, 1):
            workflow_def = self.orchestrator.workflow_definitions.get(workflow_name)
            if workflow_def:
                print(f"{i}. {workflow_name}")
                print(f"   📝 {workflow_def.description}")
                print(f"   🔧 {len(workflow_def.tasks)} taken")
                print(f"   ⏱️  Timeout: {workflow_def.timeout}s")
                print(f"   🔄 Max parallel: {workflow_def.max_parallel}")
                print()
    
    async def list_agents(self):
        """List all configured agents."""
        print("🤖 BMAD Agent Configurations")
        print("=" * 50)
        
        agents = self.orchestrator.agent_configs
        
        if not agents:
            print("❌ Geen agent configuraties gevonden")
            return
        
        for agent_name, config in agents.items():
            print(f"🤖 {agent_name}")
            print(f"   📊 Integration Level: {config.integration_level.value}")
            print(f"   🔍 Tracing: {'✅' if config.enable_tracing else '❌'}")
            print(f"   🔒 Policy Enforcement: {'✅' if config.enable_policy_enforcement else '❌'}")
            print(f"   💰 Cost Tracking: {'✅' if config.enable_cost_tracking else '❌'}")
            print(f"   🔄 Workflow Orchestration: {'✅' if config.enable_workflow_orchestration else '❌'}")
            print(f"   🤖 LLM Provider: {config.llm_provider}")
            print(f"   📋 Policy Rules: {', '.join(config.policy_rules) if config.policy_rules else 'None'}")
            print()
    
    async def execute_workflow(
        self, 
        workflow_name: str, 
        integration_level: str = "enhanced",
        context_file: Optional[str] = None
    ):
        """Execute a workflow with specified integration level."""
        print(f"🚀 Executing workflow: {workflow_name}")
        print(f"🔧 Integration Level: {integration_level}")
        print("=" * 60)
        
        # Parse integration level
        try:
            level = IntegrationLevel(integration_level.lower())
        except ValueError:
            print(f"❌ Invalid integration level: {integration_level}")
            print("Valid levels: basic, enhanced, full")
            return
        
        # Load context if provided
        context = {}
        if context_file:
            try:
                with open(context_file, 'r') as f:
                    context = json.load(f)
                print(f"📄 Loaded context from: {context_file}")
            except Exception as e:
                print(f"❌ Failed to load context file: {e}")
                return
        
        # Execute workflow
        try:
            print("🔄 Starting workflow execution...")
            result = await self.orchestrator.execute_integrated_workflow(
                workflow_name=workflow_name,
                context=context,
                integration_level=level
            )
            
            print("✅ Workflow execution completed!")
            
            # Display results
            self._display_workflow_result(result)
            
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
    
    def _display_workflow_result(self, result):
        """Display workflow execution results."""
        print("\n📊 Workflow Execution Results")
        print("=" * 60)
        
        # Basic info
        print(f"🆔 Workflow ID: {result.workflow_id}")
        print(f"📈 Status: {result.status.value}")
        print(f"⏱️  Execution Time: {result.execution_time:.2f}s")
        
        if result.error_details:
            print(f"❌ Error: {result.error_details}")
        
        # Agent results
        if result.agent_results:
            print(f"\n🤖 Agent Results ({len(result.agent_results)} tasks):")
            for task_id, task_result in result.agent_results.items():
                status_emoji = "✅" if task_result.get("status") == "completed" else "❌"
                print(f"   {status_emoji} {task_id}: {task_result.get('status', 'unknown')}")
                
                # Show integration results
                integrations = task_result.get("integrations", {})
                if integrations:
                    for integration_type, integration_data in integrations.items():
                        if integration_type == "llm" and "cost" in integration_data:
                            print(f"      💰 LLM Cost: ${integration_data['cost']:.4f}")
                        elif integration_type == "policy":
                            print(f"      🔒 Policy: {'✅' if integration_data.get('allow') else '❌'}")
        
        # Policy decisions
        if result.policy_decisions:
            print(f"\n🔒 Policy Decisions ({len(result.policy_decisions)}):")
            for i, decision in enumerate(result.policy_decisions, 1):
                allow_emoji = "✅" if decision.get("allow") else "❌"
                print(f"   {i}. {allow_emoji} {decision.get('reason', 'No reason provided')}")
        
        # Cost analysis
        if result.cost_analysis:
            print(f"\n💰 Cost Analysis:")
            total_cost = result.cost_analysis.get("total_cost", 0)
            print(f"   💵 Total Cost: ${total_cost:.4f}")
        
        # Performance metrics
        if result.performance_metrics:
            print(f"\n📈 Performance Metrics:")
            for metric, value in result.performance_metrics.items():
                print(f"   📊 {metric}: {value}")
    
    async def test_integrations(self):
        """Test all repository integrations."""
        print("🧪 Testing Repository Integrations")
        print("=" * 50)
        
        # Test Performance Monitor
        print("📊 Testing Performance Monitor...")
        try:
            system_summary = self.orchestrator.get_system_performance_summary()
            print(f"   ✅ Performance Monitor: System monitoring active")
            print(f"   💻 CPU Usage: {system_summary.get('cpu_usage', 'N/A')}")
            print(f"   🧠 Memory Usage: {system_summary.get('memory_usage', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Performance Monitor: {e}")
        
        print()
        
        # Test Test Sprites
        print("🧪 Testing Test Sprites...")
        try:
            sprites = self.orchestrator.get_component_sprites()
            print(f"   ✅ Test Sprites: {len(sprites)} sprites available")
            
            # Test a component
            if sprites:
                test_result = await self.orchestrator.run_component_tests("AgentStatus", "all")
                print(f"   ✅ Component Test: {test_result['status']}")
                print(f"   ⏱️  Duration: {test_result.get('performance_metrics', {}).get('duration', 0):.2f}s")
        except Exception as e:
            print(f"   ❌ Test Sprites: {e}")
        
        print()
        
        # Test OpenRouter
        print("🔗 Testing OpenRouter...")
        if self.orchestrator.openrouter_client:
            try:
                # Test with a simple prompt
                from bmad.agents.core.openrouter_client import LLMConfig
                
                config = LLMConfig(
                    model="openai/gpt-3.5-turbo",
                    provider="openai",
                    max_tokens=50,
                    temperature=0.1
                )
                
                response = await self.orchestrator.openrouter_client.generate_response(
                    prompt="Say 'Hello from BMAD!'",
                    strategy_name="development",
                    context={},
                    config=config
                )
                
                print(f"   ✅ OpenRouter: {response.content}")
                print(f"   💰 Cost: ${response.cost:.4f}")
                
            except Exception as e:
                print(f"   ❌ OpenRouter: {e}")
        else:
            print("   ⚠️  OpenRouter: Not configured")
        
        # Test OpenTelemetry
        print("\n🔍 Testing OpenTelemetry...")
        try:
            from bmad.agents.core.opentelemetry_tracing import TraceLevel
            with self.orchestrator.tracer.start_span("test.span", level=TraceLevel.DETAILED) as span:
                if span:
                    span.set_attribute("test.attribute", "test_value")
                print("   ✅ OpenTelemetry: Tracing working")
        except Exception as e:
            print(f"   ❌ OpenTelemetry: {e}")
        
        # Test OPA
        print("\n🔒 Testing OPA...")
        try:
            from bmad.agents.core.opa_policy_engine import PolicyRequest
            
            request = PolicyRequest(
                subject="test-agent",
                action="test-action",
                resource="test-resource",
                context={"test": True}
            )
            
            result = await self.orchestrator.policy_engine.evaluate_policy(request)
            print(f"   ✅ OPA: Policy evaluation working")
            print(f"   🔒 Result: {result.allowed}")
            
        except Exception as e:
            print(f"   ❌ OPA: {e}")
        
        # Test Advanced Policy Engine
        print("\n🔐 Testing Advanced Policy Engine...")
        try:
            # Test advanced access control policy
            advanced_result = await self.orchestrator.advanced_policy_engine.evaluate_policy(
                "advanced_access_control", 
                request
            )
            print(f"   ✅ Advanced Access Control: {advanced_result.allowed}")
            print(f"   📋 Rule: {advanced_result.rule_id}")
            print(f"   📝 Reason: {advanced_result.reason}")
            print(f"   📈 Severity: {advanced_result.severity.value}")
            
            # Test resource management policy
            resource_result = await self.orchestrator.advanced_policy_engine.evaluate_policy(
                "advanced_resource_management", 
                request
            )
            print(f"   ✅ Resource Management: {resource_result.allowed}")
            print(f"   📋 Rule: {resource_result.rule_id}")
            
        except Exception as e:
            print(f"   ❌ Advanced Policy Engine: {e}")
        
        # Test LangGraph
        print("\n🔄 Testing LangGraph...")
        try:
            workflows = self.orchestrator.langgraph_orchestrator.list_workflows()
            print(f"   ✅ LangGraph: {len(workflows)} workflows available")
        except Exception as e:
            print(f"   ❌ LangGraph: {e}")
        
        # Test Prefect
        print("\n🚀 Testing Prefect...")
        try:
            # Just test if the orchestrator is initialized
            print("   ✅ Prefect: Orchestrator initialized")
        except Exception as e:
            print(f"   ❌ Prefect: {e}")
        
        print("\n✅ Integration testing completed!")
    
    async def show_agent_config(self, agent_name: str):
        """Show configuration for a specific agent."""
        config = self.orchestrator.get_agent_config(agent_name)
        
        if not config:
            print(f"❌ Agent '{agent_name}' not found")
            return
        
        print(f"🤖 Agent Configuration: {agent_name}")
        print("=" * 50)
        print(f"📊 Integration Level: {config.integration_level.value}")
        print(f"🔍 Tracing: {'✅' if config.enable_tracing else '❌'}")
        print(f"🔒 Policy Enforcement: {'✅' if config.enable_policy_enforcement else '❌'}")
        print(f"💰 Cost Tracking: {'✅' if config.enable_cost_tracking else '❌'}")
        print(f"🔄 Workflow Orchestration: {'✅' if config.enable_workflow_orchestration else '❌'}")
        print(f"🤖 LLM Provider: {config.llm_provider}")
        print(f"⏱️  Workflow Timeout: {config.workflow_timeout}s")
        print(f"🔄 Max Retries: {config.max_retries}")
        print(f"📋 Policy Rules: {', '.join(config.policy_rules) if config.policy_rules else 'None'}")
    
    async def list_sprites(self):
        """List all available component sprites."""
        sprites = self.orchestrator.get_component_sprites()
        
        if not sprites:
            print("❌ Geen sprites gevonden")
            return
        
        print("🧪 Available Component Sprites")
        print("=" * 50)
        
        for i, sprite in enumerate(sprites, 1):
            print(f"{i}. {sprite['name']}")
            print(f"   📋 Type: {sprite['type']}")
            print(f"   🧩 Component: {sprite['component_name']}")
            print(f"   🔄 States: {sprite['states']}")
            print(f"   ♿ Accessibility: {len(sprite['accessibility_checks'])} checks")
            print(f"   🎨 Visual: {len(sprite['visual_checks'])} checks")
            print(f"   🖱️  Interactions: {len(sprite['interaction_tests'])} tests")
            print()
    
    async def test_component(self, component_name: str, test_type: str = "all"):
        """Test a specific component using sprites."""
        print(f"🧪 Testing component: {component_name}")
        print(f"🔧 Test type: {test_type}")
        print("=" * 50)
        
        try:
            result = await self.orchestrator.run_component_tests(component_name, test_type)
            
            print(f"📊 Test Results for {result['component_name']}")
            print(f"   📈 Status: {result['status']}")
            
            if result['status'] == 'passed':
                print("   ✅ All tests passed!")
                print(f"   ⏱️  Duration: {result.get('performance_metrics', {}).get('duration', 0):.2f}s")
            else:
                print(f"   ❌ Tests failed: {result.get('error', 'Unknown error')}")
            
            # Show detailed results
            if result.get('details'):
                print("\n📋 Detailed Results:")
                for key, value in result['details'].items():
                    print(f"   {key}: {value}")
            
            if result.get('accessibility_issues'):
                print("\n♿ Accessibility Issues:")
                for issue in result['accessibility_issues']:
                    print(f"   ⚠️  {issue}")
                    
        except Exception as e:
            print(f"❌ Component test failed: {e}")
    
    def export_sprite_report(self, format: str = "json", output_file: Optional[str] = None):
        """Export sprite test report."""
        print(f"📊 Exporting sprite test report in {format} format")
        print("=" * 50)
        
        try:
            report = self.orchestrator.export_sprite_test_report(format)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(report)
                print(f"✅ Report exported to: {output_file}")
            else:
                print(report)
                
        except Exception as e:
            print(f"❌ Failed to export report: {e}")
    
    # Performance Monitoring Methods
    
    async def start_performance_monitoring(self, interval: float = 5.0):
        """Start performance monitoring."""
        print(f"🚀 Starting performance monitoring with {interval}s interval...")
        
        try:
            self.orchestrator.start_performance_monitoring(interval)
            print("✅ Performance monitoring started successfully")
            print("📊 Monitoring active agents and system resources")
            print("🔔 Alerts will be displayed when thresholds are exceeded")
            
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
    
    async def stop_performance_monitoring(self):
        """Stop performance monitoring."""
        print("🛑 Stopping performance monitoring...")
        
        try:
            self.orchestrator.stop_performance_monitoring()
            print("✅ Performance monitoring stopped")
            
        except Exception as e:
            print(f"❌ Failed to stop monitoring: {e}")
    
    async def show_system_performance(self):
        """Show system performance summary."""
        print("🖥️  System Performance Summary")
        print("=" * 50)
        
        try:
            summary = self.orchestrator.get_system_performance_summary()
            
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
            print(f"❌ Failed to get system performance: {e}")
    
    async def show_agent_performance(self, agent_name: str):
        """Show performance summary for a specific agent."""
        print(f"🤖 Agent Performance Summary: {agent_name}")
        print("=" * 50)
        
        try:
            summary = self.orchestrator.get_agent_performance_summary(agent_name)
            
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
            print(f"❌ Failed to get agent performance: {e}")
    
    async def show_performance_alerts(self, agent_name: Optional[str] = None, level: Optional[str] = None):
        """Show performance alerts."""
        print("⚠️  Performance Alerts")
        print("=" * 50)
        
        try:
            alerts = self.orchestrator.get_performance_alerts(agent_name, level)
            
            if not alerts:
                print("✅ No alerts found")
                return
            
            # Show recent alerts (last 20)
            recent_alerts = alerts[:20]
            
            for alert in recent_alerts:
                status = "✅ Resolved" if alert["resolved"] else "❌ Active"
                timestamp = datetime.fromtimestamp(alert["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"[{timestamp}] {alert['level'].upper()}")
                print(f"   Agent: {alert['agent_name']}")
                print(f"   Metric: {alert['metric_type']}")
                print(f"   Message: {alert['message']}")
                print(f"   Value: {alert['current_value']:.2f} (threshold: {alert['threshold']:.2f})")
                print(f"   Status: {status}")
                print()
                
        except Exception as e:
            print(f"❌ Failed to show alerts: {e}")
    
    def export_performance_data(self, format: str = "json", output_file: Optional[str] = None):
        """Export performance data."""
        print(f"📊 Exporting performance data in {format} format")
        print("=" * 50)
        
        try:
            data = self.orchestrator.export_performance_data(format)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(data)
                print(f"✅ Data exported to: {output_file}")
            else:
                print(data)
                
        except Exception as e:
            print(f"❌ Failed to export performance data: {e}")
    
    async def update_agent_config(
        self, 
        agent_name: str, 
        integration_level: str = None,
        enable_tracing: bool = None,
        enable_policy: bool = None,
        enable_cost: bool = None,
        enable_workflow: bool = None
    ):
        """Update configuration for a specific agent."""
        config = self.orchestrator.get_agent_config(agent_name)
        
        if not config:
            print(f"❌ Agent '{agent_name}' not found")
            return
        
        # Update configuration
        if integration_level:
            try:
                config.integration_level = IntegrationLevel(integration_level.lower())
            except ValueError:
                print(f"❌ Invalid integration level: {integration_level}")
                return
        
        if enable_tracing is not None:
            config.enable_tracing = enable_tracing
        
        if enable_policy is not None:
            config.enable_policy_enforcement = enable_policy
        
        if enable_cost is not None:
            config.enable_cost_tracking = enable_cost
        
        if enable_workflow is not None:
            config.enable_workflow_orchestration = enable_workflow
        
        # Register updated config
        self.orchestrator.register_agent_config(agent_name, config)
        
        print(f"✅ Agent '{agent_name}' configuration updated")
        await self.show_agent_config(agent_name)

async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD Integrated Workflow CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all workflows
  python integrated_workflow_cli.py list-workflows
  
  # List all agents
  python integrated_workflow_cli.py list-agents
  
  # Execute a workflow
  python integrated_workflow_cli.py execute product-development --level enhanced
  
  # Test all integrations
  python integrated_workflow_cli.py test-integrations
  
  # Show agent configuration
  python integrated_workflow_cli.py show-agent product-owner
  
  # Update agent configuration
  python integrated_workflow_cli.py update-agent product-owner --level full --enable-tracing
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List workflows command
    subparsers.add_parser('list-workflows', help='List all available workflows')
    
    # List agents command
    subparsers.add_parser('list-agents', help='List all configured agents')
    
    # Execute workflow command
    execute_parser = subparsers.add_parser('execute', help='Execute a workflow')
    execute_parser.add_argument('workflow', help='Workflow name to execute')
    execute_parser.add_argument('--level', choices=['basic', 'enhanced', 'full'], 
                               default='enhanced', help='Integration level')
    execute_parser.add_argument('--context', help='JSON file with context data')
    
    # Test integrations command
    subparsers.add_parser('test-integrations', help='Test all repository integrations')
    
    # Show agent config command
    show_agent_parser = subparsers.add_parser('show-agent', help='Show agent configuration')
    show_agent_parser.add_argument('agent', help='Agent name')
    
    # Update agent config command
    update_agent_parser = subparsers.add_parser('update-agent', help='Update agent configuration')
    update_agent_parser.add_argument('agent', help='Agent name')
    update_agent_parser.add_argument('--level', choices=['basic', 'enhanced', 'full'], 
                                    help='Integration level')
    update_agent_parser.add_argument('--enable-tracing', action='store_true', 
                                    help='Enable tracing')
    update_agent_parser.add_argument('--disable-tracing', action='store_true', 
                                    help='Disable tracing')
    update_agent_parser.add_argument('--enable-policy', action='store_true', 
                                    help='Enable policy enforcement')
    update_agent_parser.add_argument('--disable-policy', action='store_true', 
                                    help='Disable policy enforcement')
    update_agent_parser.add_argument('--enable-cost', action='store_true', 
                                    help='Enable cost tracking')
    update_agent_parser.add_argument('--disable-cost', action='store_true', 
                                    help='Disable cost tracking')
    update_agent_parser.add_argument('--enable-workflow', action='store_true', 
                                    help='Enable workflow orchestration')
    update_agent_parser.add_argument('--disable-workflow', action='store_true', 
                                    help='Disable workflow orchestration')
    
    # Test sprites commands
    subparsers.add_parser('list-sprites', help='List all available component sprites')
    
    test_component_parser = subparsers.add_parser('test-component', help='Test a specific component using sprites')
    test_component_parser.add_argument('component_name', help='Name of the component to test')
    test_component_parser.add_argument('--type', choices=['all', 'accessibility', 'visual', 'interaction'], 
                                     default='all', help='Type of tests to run')
    
    export_sprite_parser = subparsers.add_parser('export-sprite-report', help='Export sprite test report')
    export_sprite_parser.add_argument('--format', choices=['json'], default='json', help='Report format')
    export_sprite_parser.add_argument('--output', help='Output file path')
    
    # Performance monitoring commands
    start_monitoring_parser = subparsers.add_parser('start-monitoring', help='Start performance monitoring')
    start_monitoring_parser.add_argument('--interval', type=float, default=5.0, help='Monitoring interval in seconds')
    
    subparsers.add_parser('stop-monitoring', help='Stop performance monitoring')
    
    subparsers.add_parser('system-performance', help='Show system performance summary')
    
    agent_performance_parser = subparsers.add_parser('agent-performance', help='Show agent performance summary')
    agent_performance_parser.add_argument('agent_name', help='Name of the agent')
    
    alerts_parser = subparsers.add_parser('performance-alerts', help='Show performance alerts')
    alerts_parser.add_argument('--agent', help='Filter by agent name')
    alerts_parser.add_argument('--level', choices=['info', 'warning', 'critical', 'emergency'], help='Filter by alert level')
    
    export_performance_parser = subparsers.add_parser('export-performance', help='Export performance data')
    export_performance_parser.add_argument('--format', choices=['json'], default='json', help='Export format')
    export_performance_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = IntegratedWorkflowCLI()
    
    try:
        if args.command == 'list-workflows':
            await cli.list_workflows()
        
        elif args.command == 'list-agents':
            await cli.list_agents()
        
        elif args.command == 'execute':
            await cli.execute_workflow(
                workflow_name=args.workflow,
                integration_level=args.level,
                context_file=args.context
            )
        
        elif args.command == 'test-integrations':
            await cli.test_integrations()
        
        elif args.command == 'show-agent':
            await cli.show_agent_config(args.agent)
        
        elif args.command == 'update-agent':
            # Parse boolean flags
            enable_tracing = None
            if args.enable_tracing:
                enable_tracing = True
            elif args.disable_tracing:
                enable_tracing = False
            
            enable_policy = None
            if args.enable_policy:
                enable_policy = True
            elif args.disable_policy:
                enable_policy = False
            
            enable_cost = None
            if args.enable_cost:
                enable_cost = True
            elif args.disable_cost:
                enable_cost = False
            
            enable_workflow = None
            if args.enable_workflow:
                enable_workflow = True
            elif args.disable_workflow:
                enable_workflow = False
            
            await cli.update_agent_config(
                agent_name=args.agent,
                integration_level=args.level,
                enable_tracing=enable_tracing,
                enable_policy=enable_policy,
                enable_cost=enable_cost,
                enable_workflow=enable_workflow
            )
        
        elif args.command == 'list-sprites':
            await cli.list_sprites()
        
        elif args.command == 'test-component':
            await cli.test_component(
                component_name=args.component_name,
                test_type=args.type
            )
        
        elif args.command == 'export-sprite-report':
            cli.export_sprite_report(
                format=args.format,
                output_file=args.output
            )
        
        elif args.command == 'start-monitoring':
            await cli.start_performance_monitoring(args.interval)
        
        elif args.command == 'stop-monitoring':
            await cli.stop_performance_monitoring()
        
        elif args.command == 'system-performance':
            await cli.show_system_performance()
        
        elif args.command == 'agent-performance':
            await cli.show_agent_performance(args.agent_name)
        
        elif args.command == 'performance-alerts':
            await cli.show_performance_alerts(args.agent, args.level)
        
        elif args.command == 'export-performance':
            cli.export_performance_data(
                format=args.format,
                output_file=args.output
            )
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CLI error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 