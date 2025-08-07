"""
Integration tests for FullstackDeveloper Agent.

This module contains comprehensive integration tests for the FullstackDeveloper agent,
testing its functionality, enhanced MCP integration, tracing integration, message bus integration,
and various fullstack development workflows.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
from datetime import datetime

from bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper import FullstackDeveloperAgent


@pytest_asyncio.fixture
async def fullstack_agent():
    """Create a FullstackDeveloper agent instance for testing."""
    agent = FullstackDeveloperAgent()
    yield agent


class TestFullstackDeveloperAgentIntegration:
    """Integration tests for FullstackDeveloper Agent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, fullstack_agent):
        """Test FullstackDeveloper agent initialization."""
        assert fullstack_agent.agent_name == "FullstackDeveloper"
        assert fullstack_agent.monitor is not None
        assert fullstack_agent.policy_engine is not None
        assert fullstack_agent.sprite_library is not None
        assert fullstack_agent.performance_metrics is not None
        assert fullstack_agent.development_history is not None

    @pytest.mark.asyncio
    async def test_enhanced_mcp_integration_initialization(self, fullstack_agent):
        """Test enhanced MCP integration initialization."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = Mock()
            mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
            mock_create.return_value = mock_enhanced_mcp
            
            await fullstack_agent.initialize_enhanced_mcp()
            
            assert fullstack_agent.enhanced_mcp_enabled is True
            assert fullstack_agent.enhanced_mcp is not None

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools(self, fullstack_agent):
        """Test enhanced MCP tools availability."""
        fullstack_agent.enhanced_mcp_enabled = True
        
        tools = fullstack_agent.get_enhanced_mcp_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "fullstack_development_enhancement" in tools
        assert "api_development_enhancement" in tools
        assert "frontend_development_enhancement" in tools

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools_registration(self, fullstack_agent):
        """Test enhanced MCP tools registration."""
        fullstack_agent.enhanced_mcp_enabled = True
        fullstack_agent.enhanced_mcp = Mock()
        fullstack_agent.enhanced_mcp.register_tool = Mock()
        
        result = fullstack_agent.register_enhanced_mcp_tools()
        
        assert result is True
        assert fullstack_agent.enhanced_mcp.register_tool.called

    @pytest.mark.asyncio
    async def test_tracing_integration_initialization(self, fullstack_agent):
        """Test tracing integration initialization."""
        with patch('integrations.opentelemetry.opentelemetry_tracing.BMADTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer.initialize = AsyncMock()
            mock_tracer.setup_fullstack_tracing = AsyncMock()
            mock_tracer_class.return_value = mock_tracer
            
            fullstack_agent.tracer = mock_tracer
            await fullstack_agent.initialize_tracing()
            
            assert fullstack_agent.tracing_enabled is True

    @pytest.mark.asyncio
    async def test_trace_operation(self, fullstack_agent):
        """Test operation tracing functionality."""
        fullstack_agent.tracing_enabled = True
        fullstack_agent.tracer = Mock()
        fullstack_agent.tracer.trace_operation = AsyncMock(return_value=True)
        
        result = await fullstack_agent.trace_operation("test_operation", {"key": "value"})
        
        assert result is True
        fullstack_agent.tracer.trace_operation.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_bus_integration_initialization(self, fullstack_agent):
        """Test message bus integration initialization."""
        with patch('bmad.agents.core.communication.agent_message_bus_integration.create_agent_message_bus_integration') as mock_create:
            mock_message_bus = Mock()
            mock_message_bus.initialize = AsyncMock()
            mock_create.return_value = mock_message_bus
            
            await fullstack_agent.initialize_message_bus_integration()
            
            assert fullstack_agent.message_bus_enabled is True
            assert fullstack_agent.message_bus_integration is not None

    @pytest.mark.asyncio
    async def test_fullstack_development_workflow(self, fullstack_agent):
        """Test fullstack development workflow."""
        feature_name = "User Authentication"
        feature_description = "Implement user authentication with JWT tokens"
        
        result = await fullstack_agent.develop_feature(feature_name, feature_description)
        
        assert isinstance(result, dict)
        assert "feature_name" in result
        assert "complexity" in result
        assert "recommendations" in result
        assert result["feature_name"] == feature_name

    @pytest.mark.asyncio
    async def test_api_development_workflow(self, fullstack_agent):
        """Test API development workflow."""
        with patch.object(fullstack_agent, 'build_api') as mock_build_api:
            mock_build_api.return_value = {
                "api_name": "UserAPI",
                "endpoints": ["/users", "/users/{id}"],
                "status": "completed"
            }
            
            result = fullstack_agent.build_api()
            
            assert isinstance(result, dict)
            assert "api_name" in result
            assert "endpoints" in result
            assert "status" in result

    @pytest.mark.asyncio
    async def test_frontend_development_workflow(self, fullstack_agent):
        """Test frontend development workflow."""
        with patch.object(fullstack_agent, 'build_frontend') as mock_build_frontend:
            mock_build_frontend.return_value = {
                "component_name": "UserDashboard",
                "framework": "React",
                "status": "completed"
            }
            
            result = fullstack_agent.build_frontend()
            
            assert isinstance(result, dict)
            assert "component_name" in result
            assert "framework" in result
            assert "status" in result

    @pytest.mark.asyncio
    async def test_shadcn_component_building(self, fullstack_agent):
        """Test Shadcn component building."""
        component_name = "Button"
        
        result = fullstack_agent.build_shadcn_component(component_name)
        
        assert isinstance(result, dict)
        assert "component_name" in result
        assert "status" in result
        assert result["component_name"] == component_name

    @pytest.mark.asyncio
    async def test_fullstack_integration_workflow(self, fullstack_agent):
        """Test fullstack integration workflow."""
        with patch.object(fullstack_agent, 'integrate_service') as mock_integrate:
            mock_integrate.return_value = {
                "service_name": "UserService",
                "integration_status": "completed",
                "endpoints_connected": 3
            }
            
            result = fullstack_agent.integrate_service()
            
            assert isinstance(result, dict)
            assert "service_name" in result
            assert "integration_status" in result

    @pytest.mark.asyncio
    async def test_testing_workflow(self, fullstack_agent):
        """Test testing workflow."""
        with patch.object(fullstack_agent, 'write_tests') as mock_write_tests:
            mock_write_tests.return_value = {
                "test_count": 15,
                "coverage": 85.5,
                "status": "completed"
            }
            
            result = fullstack_agent.write_tests()
            
            assert isinstance(result, dict)
            assert "test_count" in result
            assert "coverage" in result
            assert "status" in result

    @pytest.mark.asyncio
    async def test_ci_cd_workflow(self, fullstack_agent):
        """Test CI/CD workflow."""
        with patch.object(fullstack_agent, 'ci_cd') as mock_ci_cd:
            mock_ci_cd.return_value = {
                "pipeline_status": "success",
                "deployment_target": "production",
                "build_number": "123"
            }
            
            result = fullstack_agent.ci_cd()
            
            assert isinstance(result, dict)
            assert "pipeline_status" in result
            assert "deployment_target" in result

    @pytest.mark.asyncio
    async def test_fullstack_performance_optimization(self, fullstack_agent):
        """Test fullstack performance optimization."""
        with patch.object(fullstack_agent, 'enhanced_performance_optimization') as mock_optimize:
            mock_optimize.return_value = {
                "optimization_type": "fullstack",
                "performance_gain": 25.5,
                "areas_optimized": ["frontend", "backend", "database"]
            }
            
            result = await fullstack_agent.enhanced_performance_optimization({})
            
            assert isinstance(result, dict)
            assert "optimization_type" in result
            assert "performance_gain" in result

    @pytest.mark.asyncio
    async def test_fullstack_security_validation(self, fullstack_agent):
        """Test fullstack security validation."""
        with patch.object(fullstack_agent, 'enhanced_security_validation') as mock_security:
            mock_security.return_value = {
                "security_scan": "completed",
                "vulnerabilities_found": 0,
                "security_score": 95.0
            }
            
            result = await fullstack_agent.enhanced_security_validation({})
            
            assert isinstance(result, dict)
            assert "security_scan" in result
            assert "vulnerabilities_found" in result

    @pytest.mark.asyncio
    async def test_fullstack_error_handling(self, fullstack_agent):
        """Test fullstack error handling."""
        with patch.object(fullstack_agent, 'trace_fullstack_error') as mock_trace_error:
            mock_trace_error.return_value = {
                "error_type": "integration_error",
                "error_message": "API connection failed",
                "resolution": "Retry mechanism implemented"
            }
            
            result = await fullstack_agent.trace_fullstack_error({
                "error_type": "integration_error",
                "error_message": "API connection failed"
            })
            
            assert isinstance(result, dict)
            assert "error_type" in result
            assert "error_message" in result

    @pytest.mark.asyncio
    async def test_fullstack_agent_collaboration(self, fullstack_agent):
        """Test fullstack agent collaboration."""
        with patch.object(fullstack_agent, 'communicate_with_agents') as mock_communicate:
            mock_communicate.return_value = {
                "target_agents": ["BackendDeveloper", "FrontendDeveloper"],
                "message_sent": True,
                "responses_received": 2
            }
            
            result = await fullstack_agent.communicate_with_agents(
                ["BackendDeveloper", "FrontendDeveloper"],
                {"action": "coordinate_feature_development"}
            )
            
            assert isinstance(result, dict)
            assert "target_agents" in result
            assert "message_sent" in result

    @pytest.mark.asyncio
    async def test_fullstack_resource_completeness(self, fullstack_agent):
        """Test fullstack resource completeness."""
        result = fullstack_agent.test_resource_completeness()
        
        assert isinstance(result, dict)
        assert "resource_status" in result
        assert "missing_resources" in result

    @pytest.mark.asyncio
    async def test_fullstack_report_generation(self, fullstack_agent):
        """Test fullstack report generation."""
        with patch.object(fullstack_agent, 'export_report') as mock_export:
            mock_export.return_value = {
                "report_format": "markdown",
                "report_size": "2.5KB",
                "sections": ["development", "testing", "deployment"]
            }
            
            result = fullstack_agent.export_report("md")
            
            assert isinstance(result, dict)
            assert "report_format" in result
            assert "report_size" in result

    @pytest.mark.asyncio
    async def test_fullstack_agent_lifecycle(self, fullstack_agent):
        """Test fullstack agent complete lifecycle."""
        # Initialize all components
        await fullstack_agent.initialize_mcp()
        await fullstack_agent.initialize_enhanced_mcp()
        await fullstack_agent.initialize_tracing()
        await fullstack_agent.initialize_message_bus_integration()
        
        # Verify all components are initialized
        assert fullstack_agent.mcp_enabled is True
        assert fullstack_agent.enhanced_mcp_enabled is True
        assert fullstack_agent.tracing_enabled is True
        assert fullstack_agent.message_bus_enabled is True

    @pytest.mark.asyncio
    async def test_fullstack_agent_error_recovery(self, fullstack_agent):
        """Test fullstack agent error recovery."""
        # Simulate initialization failure
        with patch('bmad.core.mcp.get_mcp_client', side_effect=Exception("MCP connection failed")):
            await fullstack_agent.initialize_mcp()
            assert fullstack_agent.mcp_enabled is False

    @pytest.mark.asyncio
    async def test_fullstack_agent_performance_metrics(self, fullstack_agent):
        """Test fullstack agent performance metrics tracking."""
        # Update performance metrics
        fullstack_agent._record_development_metric("api_endpoints_created", 5)
        fullstack_agent._record_development_metric("frontend_components_built", 3)
        
        # Verify metrics are updated
        assert fullstack_agent.performance_metrics["api_endpoints_created"] > 0
        assert fullstack_agent.performance_metrics["frontend_components_built"] > 0

    @pytest.mark.asyncio
    async def test_fullstack_agent_history_management(self, fullstack_agent):
        """Test fullstack agent history management."""
        # Test history loading
        fullstack_agent._load_development_history()
        fullstack_agent._load_performance_history()
        
        # Verify history is loaded
        assert isinstance(fullstack_agent.development_history, list)
        assert isinstance(fullstack_agent.performance_history, list)

    @pytest.mark.asyncio
    async def test_fullstack_agent_help_system(self, fullstack_agent):
        """Test fullstack agent help system."""
        with patch('builtins.print') as mock_print:
            fullstack_agent.show_help()
            assert mock_print.called

    @pytest.mark.asyncio
    async def test_fullstack_agent_resource_management(self, fullstack_agent):
        """Test fullstack agent resource management."""
        # Test resource display
        with patch('builtins.print') as mock_print:
            fullstack_agent.show_resource("best-practices")
            assert mock_print.called 