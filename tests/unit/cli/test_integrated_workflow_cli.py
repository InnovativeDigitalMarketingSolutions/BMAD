"""
Unit Tests for Integrated Workflow CLI

Tests the integrated workflow CLI functionality including:
- Workflow listing and execution
- Agent management
- Integration testing
- Performance monitoring
- Configuration management
- Error handling and edge cases
"""

import unittest
import json
from unittest.mock import patch, MagicMock, Mock, call, AsyncMock
from datetime import datetime, timedelta
import pytest
import asyncio

# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Mock zware externe dependencies
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['opentelemetry.sdk.trace'] = MagicMock()
sys.modules['opentelemetry.sdk.trace.export'] = MagicMock()
sys.modules['opentelemetry.sdk.resources'] = MagicMock()
sys.modules['opentelemetry.exporter'] = MagicMock()
sys.modules['opentelemetry.exporter.jaeger'] = MagicMock()
sys.modules['opentelemetry.exporter.jaeger.thrift'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.http'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.http.trace_exporter'] = MagicMock()
sys.modules['opentelemetry.instrumentation'] = MagicMock()
sys.modules['opentelemetry.instrumentation.requests'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['langgraph.graph'] = MagicMock()
sys.modules['langgraph.checkpoint'] = MagicMock()
sys.modules['langgraph.checkpoint.memory'] = MagicMock()

from cli.integrated_workflow_cli import IntegratedWorkflowCLI
from bmad.agents.core.workflow.integrated_workflow_orchestrator import (
    IntegratedWorkflowResult, 
    WorkflowStatus,
    IntegrationLevel
)

class TestIntegratedWorkflowCLI:
    """Test integrated workflow CLI functionality."""

    def setup_method(self):
        """Set up test environment."""
        # We'll create the mock orchestrator and CLI within each test method
        # This ensures proper dependency injection patching
        pass

    @patch('cli.integrated_workflow_cli.IntegratedWorkflowOrchestrator')
    def test_cli_initialization(self, mock_orchestrator_class):
        """Test CLI initialization."""
        cli = IntegratedWorkflowCLI()
        mock_orchestrator_class.assert_called_once()

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_list_workflows_success(self, mock_print):
        """Test successful workflow listing."""
        # Mock workflow list and definitions
        mock_workflows = ["product-development", "ai-development"]
        mock_workflow_def = MagicMock()
        mock_workflow_def.description = "Test workflow description"
        mock_workflow_def.tasks = [MagicMock(), MagicMock()]
        mock_workflow_def.timeout = 300
        mock_workflow_def.max_parallel = 5
        
        self.mock_orchestrator.list_workflows.return_value = mock_workflows
        self.mock_orchestrator.workflow_definitions = {
            "product-development": mock_workflow_def,
            "ai-development": mock_workflow_def
        }
        
        await self.cli.list_workflows()
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🚀 BMAD Integrated Workflows")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("1. product-development")
        mock_print.assert_any_call("   📝 Test workflow description")
        mock_print.assert_any_call("   🔧 2 taken")
        mock_print.assert_any_call("   ⏱️  Timeout: 300s")
        mock_print.assert_any_call("   🔄 Max parallel: 5")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_list_workflows_empty(self, mock_print):
        """Test workflow listing with no workflows."""
        self.mock_orchestrator.list_workflows.return_value = []
        
        await self.cli.list_workflows()
        
        mock_print.assert_any_call("🚀 BMAD Integrated Workflows")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("❌ Geen workflows gevonden")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_list_agents_success(self, mock_print):
        """Test successful agent listing."""
        # Mock agent configs
        mock_config = MagicMock()
        mock_config.integration_level.value = "enhanced"
        mock_config.enable_tracing = True
        mock_config.enable_policy_enforcement = False
        mock_config.enable_cost_tracking = True
        mock_config.enable_workflow_orchestration = True
        mock_config.llm_provider = "openai"
        mock_config.policy_rules = ["rule1", "rule2"]
        
        self.mock_orchestrator.agent_configs = {
            "test-agent": mock_config
        }
        
        await self.cli.list_agents()
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🤖 BMAD Agent Configurations")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("🤖 test-agent")
        mock_print.assert_any_call("   📊 Integration Level: enhanced")
        mock_print.assert_any_call("   🔍 Tracing: ✅")
        mock_print.assert_any_call("   🔒 Policy Enforcement: ❌")
        mock_print.assert_any_call("   💰 Cost Tracking: ✅")
        mock_print.assert_any_call("   🔄 Workflow Orchestration: ✅")
        mock_print.assert_any_call("   🤖 LLM Provider: openai")
        mock_print.assert_any_call("   📋 Policy Rules: rule1, rule2")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_list_agents_empty(self, mock_print):
        """Test agent listing with no agents."""
        self.mock_orchestrator.agent_configs = {}
        
        await self.cli.list_agents()
        
        mock_print.assert_any_call("🤖 BMAD Agent Configurations")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("❌ Geen agent configuraties gevonden")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_execute_workflow_success(self, mock_print):
        """Test successful workflow execution."""
        # Mock workflow result with proper async mock
        mock_result = MagicMock(spec=IntegratedWorkflowResult)
        mock_result.workflow_id = "test-workflow-123"
        mock_result.status = WorkflowStatus.COMPLETED
        mock_result.execution_time = 5.5
        mock_result.agent_results = {
            "task1": {"status": "completed"},
            "task2": {"status": "completed"},
            "task3": {"status": "completed"}
        }
        mock_result.error_details = None
        
        # Use AsyncMock for the async method
        self.mock_orchestrator.execute_integrated_workflow = AsyncMock(return_value=mock_result)
        
        await self.cli.execute_workflow("test-workflow", "enhanced")
        
        # Verify the async method was called correctly
        self.mock_orchestrator.execute_integrated_workflow.assert_called_once_with(
            workflow_name="test-workflow",
            context={},
            integration_level=IntegrationLevel.ENHANCED
        )
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🚀 Executing workflow: test-workflow")
        mock_print.assert_any_call("🔧 Integration Level: enhanced")
        mock_print.assert_any_call("=" * 60)
        mock_print.assert_any_call("🔄 Starting workflow execution...")
        mock_print.assert_any_call("✅ Workflow execution completed!")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_execute_workflow_failure(self, mock_print):
        """Test workflow execution with failure."""
        # Mock workflow result with failure
        mock_result = MagicMock(spec=IntegratedWorkflowResult)
        mock_result.workflow_id = "test-workflow-123"
        mock_result.status = WorkflowStatus.FAILED
        mock_result.execution_time = 2.1
        mock_result.agent_results = {
            "task1": {"status": "completed"},
            "task2": {"status": "failed"},
            "task3": {"status": "failed"}
        }
        mock_result.error_details = "Workflow failed"
        
        # Use AsyncMock for the async method
        self.mock_orchestrator.execute_integrated_workflow = AsyncMock(return_value=mock_result)
        
        await self.cli.execute_workflow("test-workflow", "basic")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🚀 Executing workflow: test-workflow")
        mock_print.assert_any_call("🔧 Integration Level: basic")
        mock_print.assert_any_call("=" * 60)
        mock_print.assert_any_call("🔄 Starting workflow execution...")
        mock_print.assert_any_call("✅ Workflow execution completed!")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_execute_workflow_with_context(self, mock_print):
        """Test workflow execution with context file."""
        mock_result = MagicMock(spec=IntegratedWorkflowResult)
        mock_result.workflow_id = "test-workflow-123"
        mock_result.status = WorkflowStatus.COMPLETED
        mock_result.execution_time = 3.0
        mock_result.agent_results = {
            "task1": {"status": "completed"},
            "task2": {"status": "completed"}
        }
        mock_result.error_details = None
        
        # Use AsyncMock for the async method
        self.mock_orchestrator.execute_integrated_workflow = AsyncMock(return_value=mock_result)
        
        # Mock file reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '{"key": "value"}'
            
            await self.cli.execute_workflow("test-workflow", "enhanced", "context.json")
            
            # Verify context file was loaded
            mock_print.assert_any_call("📄 Loaded context from: context.json")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_test_integrations_success(self, mock_print):
        """Test successful integration testing."""
        # Create mock orchestrator
        mock_orchestrator = MagicMock()
        
        # Patch the orchestrator BEFORE creating the CLI (dependency injection)
        with patch('cli.integrated_workflow_cli.IntegratedWorkflowOrchestrator', return_value=mock_orchestrator):
            # Create a new CLI instance that uses the mocked orchestrator
            cli = IntegratedWorkflowCLI()
            
            # Mock orchestrator methods for individual integration tests
            mock_orchestrator.get_system_performance_summary.return_value = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8
            }
            
            mock_orchestrator.get_component_sprites.return_value = {
                "AgentStatus": {"name": "AgentStatus", "type": "component"}
            }
            
            # Mock component test result
            mock_component_result = {
                "status": "passed",
                "performance_metrics": {"duration": 0.0}
            }
            mock_orchestrator.run_component_tests = AsyncMock(return_value=mock_component_result)
            
            # Mock OpenRouter client
            mock_openrouter_client = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Hello from BMAD!"
            mock_response.cost = 0.001
            mock_response.duration = 0.5
            mock_openrouter_client.generate_response = AsyncMock(return_value=mock_response)
            mock_orchestrator.openrouter_client = mock_openrouter_client
            
            # Mock other integrations
            mock_tracer = MagicMock()
            mock_span = MagicMock()
            mock_span.set_attribute = MagicMock()
            mock_tracer.start_span.return_value.__enter__ = MagicMock(return_value=mock_span)
            mock_tracer.start_span.return_value.__exit__ = MagicMock(return_value=None)
            mock_orchestrator.tracer = mock_tracer
            
            # Mock OPA Policy Engine with proper async mock
            mock_policy_engine = MagicMock()
            mock_policy_result = MagicMock()
            mock_policy_result.allowed = True
            mock_policy_engine.evaluate_policy = AsyncMock(return_value=mock_policy_result)
            mock_orchestrator.policy_engine = mock_policy_engine
            
            # Mock Advanced Policy Engine with proper async mock
            mock_advanced_policy_engine = MagicMock()
            mock_advanced_result = MagicMock()
            mock_advanced_result.allowed = True
            mock_advanced_policy_engine.evaluate_policy = AsyncMock(return_value=mock_advanced_result)
            mock_orchestrator.advanced_policy_engine = mock_advanced_policy_engine
            
            # Mock LangGraph Orchestrator with proper async mock
            mock_langgraph_orchestrator = MagicMock()
            mock_workflow_result = MagicMock()
            mock_workflow_result.duration = 0.5
            mock_workflow_result.status = "completed"
            mock_langgraph_orchestrator.execute_workflow = AsyncMock(return_value=mock_workflow_result)
            mock_orchestrator.langgraph_orchestrator = mock_langgraph_orchestrator
            
            # Mock Prefect Orchestrator with proper async mock
            mock_prefect_orchestrator = MagicMock()
            mock_flow_result = MagicMock()
            mock_flow_result.duration = 0.5
            mock_flow_result.status = "completed"
            mock_prefect_orchestrator.execute_flow = AsyncMock(return_value=mock_flow_result)
            mock_orchestrator.prefect_orchestrator = mock_prefect_orchestrator
            
            await cli.test_integrations()
            
            # Verify output matches actual implementation
            mock_print.assert_any_call("🧪 Testing Repository Integrations")
            mock_print.assert_any_call("=" * 50)
            mock_print.assert_any_call("📊 Testing Performance Monitor...")
            mock_print.assert_any_call("   ✅ Performance Monitor: System monitoring active")
            mock_print.assert_any_call("   💻 CPU Usage: 45.2")
            mock_print.assert_any_call("   🧠 Memory Usage: 67.8")
            mock_print.assert_any_call("🧪 Testing Test Sprites...")
            mock_print.assert_any_call("   ✅ Test Sprites: 1 sprites available")
            mock_print.assert_any_call("   ✅ Component Test: passed")
            mock_print.assert_any_call("   ⏱️  Duration: 0.00s")
            mock_print.assert_any_call("🔗 Testing OpenRouter...")
            mock_print.assert_any_call("   ✅ OpenRouter: Hello from BMAD!")
            mock_print.assert_any_call("   💰 Cost: $0.0010")
            mock_print.assert_any_call("   ⏱️  Duration: 0.5s")
            mock_print.assert_any_call("🔍 Testing OpenTelemetry...")
            mock_print.assert_any_call("   ✅ OpenTelemetry: Tracing working")
            mock_print.assert_any_call("🔒 Testing OPA...")
            mock_print.assert_any_call("   ✅ OPA: Policy evaluation working")
            mock_print.assert_any_call("   🔒 Result: True")
            mock_print.assert_any_call("🔐 Testing Advanced Policy Engine...")
            mock_print.assert_any_call("   ✅ Advanced Policy Engine: Working")
            mock_print.assert_any_call("   🔐 Result: True")
            mock_print.assert_any_call("🔄 Testing LangGraph...")
            mock_print.assert_any_call("   ✅ LangGraph: Workflow execution working")
            mock_print.assert_any_call("   🔄 Result: completed")
            mock_print.assert_any_call("   ⏱️  Duration: 0.5s")
            mock_print.assert_any_call("🚀 Testing Prefect...")
            mock_print.assert_any_call("   ✅ Prefect: Flow execution working")
            mock_print.assert_any_call("   🚀 Result: completed")
            mock_print.assert_any_call("✅ Integration testing completed!")

    @pytest.mark.asyncio
    @patch('builtins.print')
    @patch('integrations.openrouter.openrouter_client.LLMConfig')
    @patch('integrations.opentelemetry.opentelemetry_tracing.TraceLevel')
    @patch('integrations.opa.opa_policy_engine.PolicyRequest')
    async def test_test_integrations_failure(self, mock_policy_request, mock_trace_level, mock_llm_config, mock_print):
        """Test integration testing with failures."""
        # Mock orchestrator methods for individual integration tests with failures
        self.mock_orchestrator.get_system_performance_summary.return_value = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8
        }
        
        self.mock_orchestrator.get_component_sprites.return_value = {
            "AgentStatus": {"name": "AgentStatus", "type": "component"}
        }
        
        # Mock component test result
        mock_component_result = {
            "status": "passed",
            "performance_metrics": {"duration": 0.0}
        }
        self.mock_orchestrator.run_component_tests = AsyncMock(return_value=mock_component_result)
        
        # Mock OpenRouter client with failure
        mock_openrouter_client = MagicMock()
        mock_openrouter_client.generate_response = AsyncMock(side_effect=Exception("Connection timeout"))
        self.mock_orchestrator.openrouter_client = mock_openrouter_client
        
        # Mock other integrations
        self.mock_orchestrator.tracer = MagicMock()
        self.mock_orchestrator.policy_engine = MagicMock()
        self.mock_orchestrator.advanced_policy_engine = MagicMock()
        self.mock_orchestrator.langgraph_orchestrator = MagicMock()
        self.mock_orchestrator.prefect_orchestrator = MagicMock()
        
        await self.cli.test_integrations()
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🧪 Testing Repository Integrations")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("📊 Testing Performance Monitor...")
        mock_print.assert_any_call("   ✅ Performance Monitor: System monitoring active")
        mock_print.assert_any_call("   💻 CPU Usage: 45.2")
        mock_print.assert_any_call("   🧠 Memory Usage: 67.8")
        mock_print.assert_any_call("🧪 Testing Test Sprites...")
        mock_print.assert_any_call("   ✅ Test Sprites: 1 sprites available")
        mock_print.assert_any_call("   ✅ Component Test: passed")
        mock_print.assert_any_call("   ⏱️  Duration: 0.00s")
        mock_print.assert_any_call("🔗 Testing OpenRouter...")
        mock_print.assert_any_call("   ❌ OpenRouter: Connection timeout")
        mock_print.assert_any_call("🔍 Testing OpenTelemetry...")
        mock_print.assert_any_call("   ✅ OpenTelemetry: Tracing working")
        mock_print.assert_any_call("🔒 Testing OPA...")
        mock_print.assert_any_call("   ✅ OPA: Policy evaluation working")
        mock_print.assert_any_call("   🔒 Result: True")
        mock_print.assert_any_call("🔐 Testing Advanced Policy Engine...")
        mock_print.assert_any_call("   ✅ Advanced Policy Engine: Working")
        mock_print.assert_any_call("   🔐 Result: True")
        mock_print.assert_any_call("🔄 Testing LangGraph...")
        mock_print.assert_any_call("   ✅ LangGraph: Workflow execution working")
        mock_print.assert_any_call("   🔄 Result: completed")
        mock_print.assert_any_call("   ⏱️  Duration: 0.5s")
        mock_print.assert_any_call("🚀 Testing Prefect...")
        mock_print.assert_any_call("   ✅ Prefect: Flow execution working")
        mock_print.assert_any_call("   🚀 Result: completed")
        mock_print.assert_any_call("✅ Integration testing completed!")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_show_agent_config_success(self, mock_print):
        """Test successful agent config display."""
        # Mock agent config
        mock_config = MagicMock()
        mock_config.agent_name = "test-agent"
        mock_config.integration_level.value = "enhanced"
        mock_config.enable_tracing = True
        mock_config.enable_policy_enforcement = True
        mock_config.enable_cost_tracking = True
        mock_config.enable_workflow_orchestration = True
        mock_config.llm_provider = "openai"
        mock_config.policy_rules = ["security", "performance"]
        
        self.mock_orchestrator.get_agent_config.return_value = mock_config
        
        await self.cli.show_agent_config("test-agent")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🤖 Agent Configuration: test-agent")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("📊 Integration Level: enhanced")
        mock_print.assert_any_call("🔍 Tracing: ✅")
        mock_print.assert_any_call("🔒 Policy Enforcement: ✅")
        mock_print.assert_any_call("💰 Cost Tracking: ✅")
        mock_print.assert_any_call("🔄 Workflow Orchestration: ✅")
        mock_print.assert_any_call("🤖 LLM Provider: openai")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_show_agent_config_not_found(self, mock_print):
        """Test agent config display for non-existent agent."""
        self.mock_orchestrator.get_agent_config.return_value = None
        
        await self.cli.show_agent_config("non-existent-agent")
        
        mock_print.assert_any_call("❌ Agent 'non-existent-agent' not found")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_list_sprites_success(self, mock_print):
        """Test successful sprite listing."""
        # Mock sprites with original dict format for backward compatibility
        mock_sprites = {
            "test-sprite-1": {"name": "Test Sprite 1", "type": "component"},
            "test-sprite-2": {"name": "Test Sprite 2", "type": "workflow"}
        }
        
        self.mock_orchestrator.get_component_sprites.return_value = mock_sprites
        
        await self.cli.list_sprites()
        
        # Verify output matches original implementation
        mock_print.assert_any_call("🎨 BMAD Test Sprites")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("🎨 Test Sprite 1 (component)")
        mock_print.assert_any_call("🎨 Test Sprite 2 (workflow)")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_list_sprites_empty(self, mock_print):
        """Test sprite listing with no sprites."""
        self.mock_orchestrator.get_component_sprites.return_value = {}
        
        await self.cli.list_sprites()
        
        mock_print.assert_any_call("🎨 BMAD Test Sprites")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("❌ Geen test sprites gevonden")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_test_component_success(self, mock_print):
        """Test successful component testing."""
        # Mock test result
        mock_result = {
            "component_name": "AgentStatus",
            "status": "passed",
            "performance_metrics": {"duration": 2.5}
        }
        
        self.mock_orchestrator.run_component_tests = AsyncMock(return_value=mock_result)
        
        await self.cli.test_component("AgentStatus", "all")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🧪 Testing component: AgentStatus")
        mock_print.assert_any_call("🔧 Test type: all")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("📊 Test Results for AgentStatus")
        mock_print.assert_any_call("   📈 Status: passed")
        mock_print.assert_any_call("✅ Component test passed!")
        mock_print.assert_any_call("   ⏱️  Duration: 2.50s")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_test_component_failure(self, mock_print):
        """Test component testing with failure."""
        # Mock test result with failure
        mock_result = {
            "component_name": "NonExistentComponent",
            "status": "error",
            "error": "Component not found"
        }
        
        self.mock_orchestrator.run_component_tests = AsyncMock(return_value=mock_result)
        
        await self.cli.test_component("NonExistentComponent", "all")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🧪 Testing component: NonExistentComponent")
        mock_print.assert_any_call("🔧 Test type: all")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("📊 Test Results for NonExistentComponent")
        mock_print.assert_any_call("   📈 Status: error")
        mock_print.assert_any_call("❌ Component test failed!")
        mock_print.assert_any_call("💥 Error: Component not found")

    @pytest.mark.asyncio
    @patch('builtins.print')
    @patch('json.dump')
    @patch('builtins.open', create=True)
    async def test_export_sprite_report_json(self, mock_open, mock_json_dump, mock_print):
        """Test sprite report export in JSON format."""
        # Mock sprite report
        mock_report = {
            "sprites": [
                {"name": "AgentStatus", "status": "success"},
                {"name": "MetricsChart", "status": "success"}
            ],
            "summary": {"total": 2, "passed": 2, "failed": 0}
        }
        
        self.mock_orchestrator.export_sprite_test_report.return_value = mock_report
        
        self.cli.export_sprite_report("json", "sprite_report.json")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("📄 Exporting sprite report...")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("✅ Sprite report exported to: sprite_report.json")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_start_performance_monitoring(self, mock_print):
        """Test starting performance monitoring."""
        self.mock_orchestrator.start_performance_monitoring.return_value = True
        
        await self.cli.start_performance_monitoring(10.0)
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("📊 Starting performance monitoring...")
        mock_print.assert_any_call("⏱️  Monitoring interval: 10.0s")
        mock_print.assert_any_call("✅ Performance monitoring started successfully")
        mock_print.assert_any_call("📊 Monitoring active agents and system resources")
        mock_print.assert_any_call("🔔 Alerts will be displayed when thresholds are exceeded")
        self.mock_orchestrator.start_performance_monitoring.assert_called_once_with(10.0)

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_stop_performance_monitoring(self, mock_print):
        """Test stopping performance monitoring."""
        self.mock_orchestrator.stop_performance_monitoring.return_value = True
        
        await self.cli.stop_performance_monitoring()
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🛑 Stopping performance monitoring...")
        mock_print.assert_any_call("✅ Performance monitoring stopped")
        self.mock_orchestrator.stop_performance_monitoring.assert_called_once()

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_show_system_performance(self, mock_print):
        """Test system performance display."""
        # Mock system performance data
        mock_performance = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_io": 1024,
            "network_io": 2048,
            "active_agents": 5,
            "total_alerts": 2
        }
        
        self.mock_orchestrator.get_system_performance_summary.return_value = mock_performance
        
        await self.cli.show_system_performance()
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🖥️  System Performance Summary")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("💻 CPU Usage: 45.2%")
        mock_print.assert_any_call("🧠 Memory Usage: 67.8%")
        mock_print.assert_any_call("💾 Disk I/O: 1,024 bytes")
        mock_print.assert_any_call("🌐 Network I/O: 2,048 bytes")
        mock_print.assert_any_call("🤖 Active Agents: 5")
        mock_print.assert_any_call("⚠️  Total Alerts: 2")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_show_agent_performance(self, mock_print):
        """Test agent performance display."""
        # Mock agent performance data
        mock_performance = {
            "success_rate": 0.95,
            "avg_response_time": 1.2,
            "total_requests": 100,
            "failed_requests": 5,
            "total_cost": 0.15,
            "recent_alerts": []
        }
        
        self.mock_orchestrator.get_agent_performance_metrics.return_value = mock_performance
        
        await self.cli.show_agent_performance("test-agent")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("🤖 Agent Performance Summary: test-agent")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("📊 Success Rate: 95.00%")
        mock_print.assert_any_call("⏱️  Average Response Time: 1.20s")
        mock_print.assert_any_call("🔄 Total Requests: 100")
        mock_print.assert_any_call("❌ Failed Requests: 5")
        mock_print.assert_any_call("💰 Total Cost: $0.1500")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_show_performance_alerts(self, mock_print):
        """Test performance alerts display."""
        # Mock performance alerts
        mock_alerts = [
            {
                "level": "warning",
                "message": "High CPU usage detected",
                "timestamp": 1642248600,  # Unix timestamp
                "agent_name": "test-agent",
                "metric_type": "cpu_usage",
                "resolved": False
            }
        ]
        
        self.mock_orchestrator.get_performance_alerts.return_value = mock_alerts
        
        await self.cli.show_performance_alerts()
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("⚠️  Performance Alerts")
        mock_print.assert_any_call("=" * 50)
        # Note: The actual timestamp format depends on the current time, so we check for the pattern
        # The test uses timestamp 1642248600 which corresponds to 2022-01-15 13:10:00
        mock_print.assert_any_call("[2022-01-15 13:10:00] WARNING")
        mock_print.assert_any_call("   Agent: test-agent")
        mock_print.assert_any_call("   Metric: cpu_usage")
        mock_print.assert_any_call("   Message: High CPU usage detected")

    @pytest.mark.asyncio
    @patch('builtins.print')
    @patch('json.dump')
    @patch('builtins.open', create=True)
    async def test_export_performance_data(self, mock_open, mock_json_dump, mock_print):
        """Test performance data export."""
        # Mock performance data
        mock_data = {
            "system_metrics": {"cpu": "45%", "memory": "67%"},
            "agent_metrics": {"test-agent": {"success_rate": 0.93}},
            "alerts": [{"level": "warning", "message": "High CPU"}]
        }
        
        self.mock_orchestrator.export_performance_data.return_value = mock_data
        
        self.cli.export_performance_data("json", "performance_data.json")
        
        # Verify output matches actual implementation
        mock_print.assert_any_call("📄 Exporting performance data...")
        mock_print.assert_any_call("=" * 50)
        mock_print.assert_any_call("✅ Performance data exported to: performance_data.json")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_update_agent_config_success(self, mock_print):
        """Test successful agent config update."""
        # Mock agent config
        mock_config = MagicMock()
        mock_config.integration_level = IntegrationLevel.ENHANCED
        mock_config.enable_tracing = True
        mock_config.enable_policy_enforcement = True
        mock_config.enable_cost_tracking = True
        mock_config.enable_workflow_orchestration = True
        
        self.mock_orchestrator.get_agent_config.return_value = mock_config
        self.mock_orchestrator.register_agent_config = MagicMock()
        
        await self.cli.update_agent_config(
            "test-agent",
            integration_level="enhanced",
            enable_tracing=True,
            enable_policy=True
        )
        
        # Verify orchestrator method was called
        self.mock_orchestrator.register_agent_config.assert_called_once_with("test-agent", mock_config)
        mock_print.assert_any_call("✅ Agent 'test-agent' configuration updated")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_update_agent_config_failure(self, mock_print):
        """Test agent config update with failure."""
        # Mock agent not found
        self.mock_orchestrator.get_agent_config.return_value = None
        
        await self.cli.update_agent_config("test-agent", enable_tracing=True)
        
        # Verify error handling
        mock_print.assert_any_call("❌ Agent 'test-agent' not found")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_execute_workflow_invalid_integration_level(self, mock_print):
        """Test workflow execution with invalid integration level."""
        await self.cli.execute_workflow("test-workflow", "invalid-level")
        
        mock_print.assert_any_call("❌ Invalid integration level: invalid-level")
        mock_print.assert_any_call("Valid levels: basic, enhanced, full")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_execute_workflow_orchestrator_error(self, mock_print):
        """Test workflow execution with orchestrator error."""
        # Mock orchestrator error
        self.mock_orchestrator.execute_integrated_workflow = AsyncMock(
            side_effect=Exception("Orchestrator error")
        )
        
        await self.cli.execute_workflow("test-workflow", "enhanced")
        
        # Verify error handling
        mock_print.assert_any_call("❌ Workflow execution failed: Orchestrator error")

    @pytest.mark.asyncio
    @patch('builtins.print')
    async def test_workflow_lifecycle(self, mock_print):
        """Test complete workflow lifecycle."""
        # Mock successful workflow execution
        mock_result = MagicMock(spec=IntegratedWorkflowResult)
        mock_result.workflow_id = "test-workflow-123"
        mock_result.status = WorkflowStatus.COMPLETED
        mock_result.execution_time = 3.5
        mock_result.agent_results = {
            "task1": {"status": "completed"},
            "task2": {"status": "completed"}
        }
        mock_result.error_details = None
        
        self.mock_orchestrator.execute_integrated_workflow = AsyncMock(return_value=mock_result)
        
        # Execute workflow
        await self.cli.execute_workflow("test-workflow", "enhanced")
        
        # Verify complete lifecycle
        self.mock_orchestrator.execute_integrated_workflow.assert_called_once()
        mock_print.assert_any_call("🚀 Executing workflow: test-workflow")
        mock_print.assert_any_call("🔧 Integration Level: enhanced")
        mock_print.assert_any_call("=" * 60)
        mock_print.assert_any_call("🔄 Starting workflow execution...")
        mock_print.assert_any_call("✅ Workflow execution completed!")

class TestMainFunction:
    """Test main function functionality."""

    @patch('cli.integrated_workflow_cli.IntegratedWorkflowCLI')
    @patch('argparse.ArgumentParser')
    @pytest.mark.asyncio
    async def test_main_list_workflows(self, mock_parser_class, mock_cli_class):
        """Test main function with list-workflows command."""
        # Mock argument parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(
            command='list-workflows',
            workflow_name=None,
            integration_level=None,
            context_file=None
        )
        
        # Mock CLI
        mock_cli = AsyncMock()
        mock_cli_class.return_value = mock_cli
        
        # Import and run main function
        from cli.integrated_workflow_cli import main
        await main()
        
        # Verify CLI method was called
        mock_cli.list_workflows.assert_called_once()

    @patch('cli.integrated_workflow_cli.IntegratedWorkflowCLI')
    @patch('argparse.ArgumentParser')
    @pytest.mark.asyncio
    async def test_main_execute_workflow(self, mock_parser_class, mock_cli_class):
        """Test main function with execute-workflow command."""
        # Mock argument parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(
            command='execute',
            workflow='test-workflow',
            level='enhanced',
            context=None
        )
        
        # Mock CLI
        mock_cli = AsyncMock()
        mock_cli_class.return_value = mock_cli
        
        # Import and run main function
        from cli.integrated_workflow_cli import main
        await main()
        
        # Verify CLI method was called with named arguments
        mock_cli.execute_workflow.assert_called_once_with(workflow_name='test-workflow', integration_level='enhanced', context_file=None) 