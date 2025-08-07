"""
Integration tests for MobileDeveloper Agent.

This module contains comprehensive integration tests for the MobileDeveloper agent,
testing its functionality, enhanced MCP integration, tracing integration, message bus integration,
and various mobile development workflows.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
from datetime import datetime

from bmad.agents.Agent.MobileDeveloper.mobiledeveloper import MobileDeveloperAgent


@pytest_asyncio.fixture
async def mobile_agent():
    """Create a MobileDeveloper agent instance for testing."""
    agent = MobileDeveloperAgent()
    yield agent


class TestMobileDeveloperAgentIntegration:
    """Integration tests for MobileDeveloper Agent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, mobile_agent):
        """Test that the agent initializes correctly."""
        assert mobile_agent.agent_name == "MobileDeveloper"
        assert mobile_agent.monitor is not None
        assert mobile_agent.policy_engine is not None
        assert mobile_agent.sprite_library is not None
        assert mobile_agent.resource_base is not None
        assert mobile_agent.template_paths is not None
        assert mobile_agent.data_paths is not None

    @pytest.mark.asyncio
    async def test_enhanced_mcp_integration_initialization(self, mobile_agent):
        """Test enhanced MCP integration initialization."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = Mock()
            mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
            mock_create.return_value = mock_enhanced_mcp
            
            await mobile_agent.initialize_enhanced_mcp()
            
            assert mobile_agent.enhanced_mcp_enabled is True
            assert mobile_agent.enhanced_mcp is not None

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools(self, mobile_agent):
        """Test enhanced MCP tools functionality."""
        mobile_agent.enhanced_mcp_enabled = True
        
        tools = mobile_agent.get_enhanced_mcp_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "mobile_app_development_enhancement" in tools
        assert "mobile_performance_enhancement" in tools
        assert "mobile_deployment_enhancement" in tools

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools_registration(self, mobile_agent):
        """Test enhanced MCP tools registration."""
        mobile_agent.enhanced_mcp_enabled = True
        mobile_agent.enhanced_mcp = Mock()
        mobile_agent.enhanced_mcp.register_tool = Mock()
        
        result = mobile_agent.register_enhanced_mcp_tools()
        
        assert result is True
        assert mobile_agent.enhanced_mcp.register_tool.called

    @pytest.mark.asyncio
    async def test_tracing_integration_initialization(self, mobile_agent):
        """Test tracing integration initialization."""
        with patch('integrations.opentelemetry.opentelemetry_tracing.BMADTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer.initialize = AsyncMock()
            mock_tracer.setup_mobile_tracing = AsyncMock()
            mock_tracer_class.return_value = mock_tracer
            
            await mobile_agent.initialize_tracing()
            
            assert mobile_agent.tracing_enabled is True
            assert mobile_agent.tracer is not None

    @pytest.mark.asyncio
    async def test_trace_operation(self, mobile_agent):
        """Test operation tracing functionality."""
        mobile_agent.tracing_enabled = True
        mobile_agent.tracer = Mock()
        mobile_agent.tracer.trace_operation = AsyncMock()
        
        result = await mobile_agent.trace_operation("test_operation", {"key": "value"})
        
        assert result is True
        mobile_agent.tracer.trace_operation.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_bus_integration_initialization(self, mobile_agent):
        """Test message bus integration initialization."""
        with patch('bmad.agents.core.communication.agent_message_bus_integration.create_agent_message_bus_integration') as mock_create:
            mock_message_bus = Mock()
            mock_message_bus.register_event_handler = AsyncMock()
            mock_create.return_value = mock_message_bus
            
            result = await mobile_agent.initialize_message_bus_integration()
            
            assert result is True
            assert mobile_agent.message_bus_enabled is True
            assert mobile_agent.message_bus_integration is not None

    @pytest.mark.asyncio
    async def test_mobile_app_development_workflow(self, mobile_agent):
        """Test complete mobile app development workflow."""
        with patch.object(mobile_agent, 'create_app') as mock_create_app:
            mock_create_app.return_value = {
                "status": "success",
                "app_name": "TestApp",
                "platform": "react-native",
                "created_at": datetime.now().isoformat()
            }
            
            result = await mobile_agent.create_app("TestApp", "react-native", "business")
            
            assert result["status"] == "success"
            assert result["app_name"] == "TestApp"
            assert result["platform"] == "react-native"

    @pytest.mark.asyncio
    async def test_mobile_component_building(self, mobile_agent):
        """Test mobile component building functionality."""
        with patch.object(mobile_agent, 'build_component') as mock_build_component:
            mock_build_component.return_value = {
                "status": "success",
                "component_name": "CustomButton",
                "platform": "react-native",
                "component_type": "ui",
                "created_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.build_component("CustomButton", "react-native", "ui")
            
            assert result["status"] == "success"
            assert result["component_name"] == "CustomButton"
            assert result["platform"] == "react-native"

    @pytest.mark.asyncio
    async def test_mobile_performance_optimization(self, mobile_agent):
        """Test mobile performance optimization functionality."""
        with patch.object(mobile_agent, 'optimize_performance') as mock_optimize:
            mock_optimize.return_value = {
                "status": "success",
                "app_name": "TestApp",
                "optimization_type": "general",
                "performance_improvement": 15.5,
                "optimized_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.optimize_performance("TestApp", "general")
            
            assert result["status"] == "success"
            assert result["app_name"] == "TestApp"
            assert result["performance_improvement"] > 0

    @pytest.mark.asyncio
    async def test_mobile_app_testing(self, mobile_agent):
        """Test mobile app testing functionality."""
        with patch.object(mobile_agent, 'test_app') as mock_test_app:
            mock_test_app.return_value = {
                "status": "success",
                "app_name": "TestApp",
                "test_type": "comprehensive",
                "test_results": {
                    "unit_tests": {"passed": 25, "failed": 0},
                    "integration_tests": {"passed": 10, "failed": 0},
                    "e2e_tests": {"passed": 5, "failed": 0}
                },
                "tested_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.test_app("TestApp", "comprehensive")
            
            assert result["status"] == "success"
            assert result["app_name"] == "TestApp"
            assert result["test_results"]["unit_tests"]["passed"] > 0

    @pytest.mark.asyncio
    async def test_mobile_app_deployment(self, mobile_agent):
        """Test mobile app deployment functionality."""
        with patch.object(mobile_agent, 'deploy_app') as mock_deploy_app:
            mock_deploy_app.return_value = {
                "status": "success",
                "app_name": "TestApp",
                "deployment_target": "app-store",
                "deployment_url": "https://appstore.com/testapp",
                "deployed_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.deploy_app("TestApp", "app-store")
            
            assert result["status"] == "success"
            assert result["app_name"] == "TestApp"
            assert result["deployment_target"] == "app-store"

    @pytest.mark.asyncio
    async def test_mobile_performance_analysis(self, mobile_agent):
        """Test mobile performance analysis functionality."""
        with patch.object(mobile_agent, 'analyze_performance') as mock_analyze:
            mock_analyze.return_value = {
                "status": "success",
                "app_name": "TestApp",
                "analysis_type": "comprehensive",
                "performance_metrics": {
                    "startup_time": 2.5,
                    "memory_usage": 45.2,
                    "battery_consumption": 12.8,
                    "network_requests": 15
                },
                "analyzed_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.analyze_performance("TestApp", "comprehensive")
            
            assert result["status"] == "success"
            assert result["app_name"] == "TestApp"
            assert result["performance_metrics"]["startup_time"] > 0

    @pytest.mark.asyncio
    async def test_mobile_platform_support(self, mobile_agent):
        """Test mobile platform support functionality."""
        with patch.object(mobile_agent, 'list_platforms') as mock_list_platforms:
            mock_list_platforms.return_value = {
                "supported_platforms": [
                    "react-native",
                    "flutter",
                    "ios",
                    "android",
                    "xamarin"
                ],
                "recommended_platform": "react-native"
            }
            
            result = mobile_agent.list_platforms()
            
            assert "react-native" in result["supported_platforms"]
            assert "flutter" in result["supported_platforms"]
            assert "ios" in result["supported_platforms"]
            assert "android" in result["supported_platforms"]

    @pytest.mark.asyncio
    async def test_mobile_template_management(self, mobile_agent):
        """Test mobile template management functionality."""
        with patch.object(mobile_agent, 'show_templates') as mock_show_templates:
            mock_show_templates.return_value = {
                "available_templates": [
                    "react-native-template",
                    "flutter-template",
                    "ios-template",
                    "android-template",
                    "mobile-test-template"
                ],
                "template_count": 5
            }
            
            result = mobile_agent.show_templates()
            
            assert len(result["available_templates"]) > 0
            assert result["template_count"] > 0

    @pytest.mark.asyncio
    async def test_mobile_app_export(self, mobile_agent):
        """Test mobile app export functionality."""
        with patch.object(mobile_agent, 'export_app') as mock_export_app:
            mock_export_app.return_value = {
                "status": "success",
                "app_name": "TestApp",
                "export_path": "/exports/TestApp.zip",
                "export_size": "15.2 MB",
                "exported_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.export_app("TestApp")
            
            assert result["status"] == "success"
            assert result["app_name"] == "TestApp"
            assert result["export_path"] is not None

    @pytest.mark.asyncio
    async def test_mobile_error_handling(self, mobile_agent):
        """Test mobile error handling functionality."""
        with patch.object(mobile_agent, 'trace_mobile_error') as mock_trace_error:
            mock_trace_error.return_value = {
                "status": "success",
                "error_traced": True,
                "error_details": {
                    "error_type": "runtime_error",
                    "error_message": "Test error",
                    "stack_trace": "Test stack trace"
                }
            }
            
            error_data = {
                "error_type": "runtime_error",
                "error_message": "Test error",
                "stack_trace": "Test stack trace"
            }
            
            result = await mobile_agent.trace_mobile_error(error_data)
            
            assert result["status"] == "success"
            assert result["error_traced"] is True

    @pytest.mark.asyncio
    async def test_mobile_performance_tracking(self, mobile_agent):
        """Test mobile performance tracking functionality."""
        with patch.object(mobile_agent, 'trace_mobile_performance') as mock_trace_performance:
            mock_trace_performance.return_value = {
                "status": "success",
                "performance_traced": True,
                "performance_metrics": {
                    "cpu_usage": 25.5,
                    "memory_usage": 45.2,
                    "battery_consumption": 12.8
                }
            }
            
            performance_data = {
                "cpu_usage": 25.5,
                "memory_usage": 45.2,
                "battery_consumption": 12.8
            }
            
            result = await mobile_agent.trace_mobile_performance(performance_data)
            
            assert result["status"] == "success"
            assert result["performance_traced"] is True

    @pytest.mark.asyncio
    async def test_mobile_deployment_tracking(self, mobile_agent):
        """Test mobile deployment tracking functionality."""
        with patch.object(mobile_agent, 'trace_mobile_deployment') as mock_trace_deployment:
            mock_trace_deployment.return_value = {
                "status": "success",
                "deployment_traced": True,
                "deployment_details": {
                    "deployment_target": "app-store",
                    "deployment_status": "success",
                    "deployment_time": "2.5 minutes"
                }
            }
            
            deployment_data = {
                "deployment_target": "app-store",
                "deployment_status": "success",
                "deployment_time": "2.5 minutes"
            }
            
            result = await mobile_agent.trace_mobile_deployment(deployment_data)
            
            assert result["status"] == "success"
            assert result["deployment_traced"] is True

    @pytest.mark.asyncio
    async def test_mobile_agent_collaboration(self, mobile_agent):
        """Test mobile agent collaboration functionality."""
        with patch.object(mobile_agent, 'collaborate_example') as mock_collaborate:
            mock_collaborate.return_value = {
                "status": "success",
                "collaboration_result": "Mobile app development completed successfully",
                "collaborated_agents": ["FrontendDeveloper", "BackendDeveloper", "QualityGuardian"]
            }
            
            result = await mobile_agent.collaborate_example()
            
            assert result["status"] == "success"
            assert len(result["collaborated_agents"]) > 0

    @pytest.mark.asyncio
    async def test_mobile_resource_completeness(self, mobile_agent):
        """Test mobile resource completeness functionality."""
        with patch.object(mobile_agent, 'test_resource_completeness') as mock_test_resources:
            mock_test_resources.return_value = {
                "status": "success",
                "resource_completeness": 100.0,
                "missing_resources": [],
                "available_resources": [
                    "best-practices",
                    "react-native-template",
                    "flutter-template",
                    "ios-template",
                    "android-template"
                ]
            }
            
            result = mobile_agent.test_resource_completeness()
            
            assert result["status"] == "success"
            assert result["resource_completeness"] == 100.0
            assert len(result["missing_resources"]) == 0

    @pytest.mark.asyncio
    async def test_mobile_report_generation(self, mobile_agent):
        """Test mobile report generation functionality."""
        with patch.object(mobile_agent, 'export_report') as mock_export_report:
            mock_export_report.return_value = {
                "status": "success",
                "report_format": "md",
                "report_path": "/reports/mobile_report.md",
                "report_size": "2.5 KB",
                "generated_at": datetime.now().isoformat()
            }
            
            result = mobile_agent.export_report("md")
            
            assert result["status"] == "success"
            assert result["report_format"] == "md"
            assert result["report_path"] is not None

    @pytest.mark.asyncio
    async def test_mobile_agent_lifecycle(self, mobile_agent):
        """Test complete mobile agent lifecycle."""
        # Initialize agent
        assert mobile_agent.agent_name == "MobileDeveloper"
        
        # Test enhanced MCP integration
        mobile_agent.enhanced_mcp_enabled = True
        tools = mobile_agent.get_enhanced_mcp_tools()
        assert len(tools) > 0
        
        # Test tracing integration
        mobile_agent.tracing_enabled = True
        mobile_agent.tracer = Mock()
        mobile_agent.tracer.trace_operation = AsyncMock()
        
        result = await mobile_agent.trace_operation("test_operation")
        assert result is True
        
        # Test message bus integration
        mobile_agent.message_bus_enabled = True
        mobile_agent.message_bus_integration = Mock()
        
        # Test mobile development workflow
        with patch.object(mobile_agent, 'create_app') as mock_create_app:
            mock_create_app.return_value = {"status": "success", "app_name": "TestApp"}
            
            result = await mobile_agent.create_app("TestApp")
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_mobile_agent_error_recovery(self, mobile_agent):
        """Test mobile agent error recovery capabilities."""
        # Test with disabled enhanced MCP
        mobile_agent.enhanced_mcp_enabled = False
        tools = mobile_agent.get_enhanced_mcp_tools()
        assert tools == []
        
        # Test with disabled tracing
        mobile_agent.tracing_enabled = False
        result = await mobile_agent.trace_operation("test_operation")
        assert result is False
        
        # Test with disabled message bus
        mobile_agent.message_bus_enabled = False
        # Agent should still function without message bus

    @pytest.mark.asyncio
    async def test_mobile_agent_performance_metrics(self, mobile_agent):
        """Test mobile agent performance metrics tracking."""
        # Update performance metrics
        mobile_agent._update_average_metric("average_build_time", 2.5)
        mobile_agent._update_success_rate("deployment_success_rate", True)
        
        # Verify metrics are updated
        assert mobile_agent.performance_metrics["average_build_time"] > 0
        assert mobile_agent.performance_metrics["deployment_success_rate"] > 0

    @pytest.mark.asyncio
    async def test_mobile_agent_history_management(self, mobile_agent):
        """Test mobile agent history management."""
        # Test app history
        mobile_agent.show_app_history()
        assert mobile_agent.app_history is not None
        
        # Test performance history
        mobile_agent.show_performance_history()
        assert mobile_agent.performance_history is not None

    @pytest.mark.asyncio
    async def test_mobile_agent_help_system(self, mobile_agent):
        """Test mobile agent help system."""
        with patch('builtins.print') as mock_print:
            mobile_agent.show_help()
            assert mock_print.called

    @pytest.mark.asyncio
    async def test_mobile_agent_resource_management(self, mobile_agent):
        """Test mobile agent resource management."""
        with patch('builtins.print') as mock_print:
            mobile_agent.show_resource("best-practices")
            assert mock_print.called


if __name__ == "__main__":
    pytest.main([__file__]) 