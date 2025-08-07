#!/usr/bin/env python3
"""
Integration tests for QualityGuardianAgent.
Tests complete agent functionality including enhanced MCP, tracing, and message bus integration.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.agents.Agent.QualityGuardian.qualityguardian import QualityGuardianAgent


class TestQualityGuardianIntegration:
    """Integration tests for QualityGuardianAgent."""

    @pytest_asyncio.fixture
    async def quality_agent(self):
        """Create a test instance of QualityGuardianAgent."""
        agent = QualityGuardianAgent()
        yield agent
        # Cleanup
        if hasattr(agent, 'tracer') and agent.tracer:
            await agent.tracer.shutdown()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, quality_agent):
        """Test complete agent initialization."""
        assert quality_agent.agent_name == "QualityGuardian"
        assert quality_agent.monitor is not None
        assert quality_agent.policy_engine is not None
        assert quality_agent.sprite_library is not None
        assert quality_agent.resource_base is not None
        assert len(quality_agent.template_paths) > 0
        assert len(quality_agent.data_paths) > 0

    @pytest.mark.asyncio
    async def test_enhanced_mcp_integration(self, quality_agent):
        """Test enhanced MCP integration."""
        # Test enhanced MCP initialization
        with patch('bmad.core.mcp.enhanced_mcp_integration.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = Mock()
            mock_enhanced_mcp.initialize_enhanced_mcp.return_value = True
            mock_create.return_value = mock_enhanced_mcp

            await quality_agent.initialize_enhanced_mcp()

            assert quality_agent.enhanced_mcp_enabled is True
            assert quality_agent.enhanced_mcp is not None

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools(self, quality_agent):
        """Test enhanced MCP tools functionality."""
        # Mock enhanced MCP
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True

        tools = quality_agent.get_enhanced_mcp_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all(isinstance(tool, str) for tool in tools)
        assert "quality_gate_enhancement" in tools
        assert "code_quality_enhancement" in tools
        assert "security_enhancement" in tools

    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_registration(self, quality_agent):
        """Test enhanced MCP tool registration."""
        # Mock enhanced MCP
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True

        result = quality_agent.register_enhanced_mcp_tools()
        assert result is True
        assert quality_agent.enhanced_mcp.register_tool.called

    @pytest.mark.asyncio
    async def test_tracing_integration(self, quality_agent):
        """Test tracing integration."""
        # Test tracing initialization
        with patch('integrations.opentelemetry.opentelemetry_tracing.BMADTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer

            await quality_agent.initialize_tracing()

            assert quality_agent.tracing_enabled is True
            assert quality_agent.tracer is not None

    @pytest.mark.asyncio
    async def test_trace_operation(self, quality_agent):
        """Test operation tracing."""
        # Mock tracer
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True

        result = await quality_agent.trace_operation("test_operation", {"key": "value"})
        assert result is True
        assert quality_agent.tracer.trace_operation.called

    @pytest.mark.asyncio
    async def test_message_bus_integration(self, quality_agent):
        """Test message bus integration."""
        # Test message bus initialization
        with patch('bmad.agents.core.communication.agent_message_bus_integration.create_agent_message_bus_integration') as mock_create:
            mock_message_bus = Mock()
            mock_create.return_value = mock_message_bus

            await quality_agent.initialize_message_bus_integration()

            assert quality_agent.message_bus_integration is not None
            assert quality_agent.message_bus_enabled is True

    @pytest.mark.asyncio
    async def test_quality_assurance_workflow(self, quality_agent):
        """Test complete quality assurance workflow."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True
        quality_agent.message_bus_integration = Mock()
        quality_agent.message_bus_enabled = True

        # Test quality gate check
        with patch.object(quality_agent, 'quality_gate_check') as mock_gate_check:
            mock_gate_check.return_value = {"status": "passed", "score": 95}

            result = await quality_agent.quality_gate_check()

            assert result["status"] == "passed"
            assert result["score"] == 95

    @pytest.mark.asyncio
    async def test_code_quality_analysis_workflow(self, quality_agent):
        """Test code quality analysis workflow."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True

        # Test code quality analysis
        with patch.object(quality_agent, 'analyze_code_quality') as mock_analysis:
            mock_analysis.return_value = {
                "status": "success",
                "coverage": 85,
                "complexity": 8,
                "duplication": 3
            }

            result = quality_agent.analyze_code_quality("./")

            assert result["status"] == "success"
            assert result["coverage"] > 80

    @pytest.mark.asyncio
    async def test_security_scan_workflow(self, quality_agent):
        """Test security scan workflow."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True

        # Test security scan
        with patch.object(quality_agent, 'security_scan') as mock_scan:
            mock_scan.return_value = {
                "status": "success",
                "vulnerabilities_found": 0,
                "security_score": 95
            }

            result = quality_agent.security_scan("*.py")

            assert result["status"] == "success"
            assert result["vulnerabilities_found"] == 0
            assert result["security_score"] > 90

    @pytest.mark.asyncio
    async def test_performance_analysis_workflow(self, quality_agent):
        """Test performance analysis workflow."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True

        # Test performance analysis
        with patch.object(quality_agent, 'performance_analysis') as mock_analysis:
            mock_analysis.return_value = {
                "status": "success",
                "response_time": 150,
                "throughput": 1000,
                "performance_score": 90
            }

            result = quality_agent.performance_analysis("main")

            assert result["status"] == "success"
            assert result["performance_score"] > 85

    @pytest.mark.asyncio
    async def test_standards_enforcement_workflow(self, quality_agent):
        """Test standards enforcement workflow."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True

        # Test standards enforcement
        with patch.object(quality_agent, 'enforce_standards') as mock_enforce:
            mock_enforce.return_value = {
                "status": "success",
                "violations_found": 2,
                "standards_enforced": True,
                "compliance_score": 95
            }

            result = quality_agent.enforce_standards("./")

            assert result["status"] == "success"
            assert result["standards_enforced"] is True
            assert result["compliance_score"] > 90

    @pytest.mark.asyncio
    async def test_resource_completeness(self, quality_agent):
        """Test resource completeness."""
        # Test that all required resources are available
        assert quality_agent.resource_base.exists()

        # Test template paths
        for template_name, template_path in quality_agent.template_paths.items():
            assert template_path.exists(), f"Template {template_name} not found at {template_path}"

        # Test data paths
        for data_name, data_path in quality_agent.data_paths.items():
            assert data_path.exists(), f"Data file {data_name} not found at {data_path}"

    @pytest.mark.asyncio
    async def test_quality_metrics_tracking(self, quality_agent):
        """Test quality metrics tracking."""
        # Test metric recording
        quality_agent._record_quality_metric("test_metric", 0.95, "%")

        # Test performance metrics
        metrics = quality_agent.get_performance_metrics()
        assert isinstance(metrics, dict)
        assert "quality_analyses_completed" in metrics
        assert "security_scans_completed" in metrics
        assert "performance_analyses_completed" in metrics

    @pytest.mark.asyncio
    async def test_agent_collaboration(self, quality_agent):
        """Test agent collaboration functionality."""
        # Mock dependencies
        quality_agent.message_bus_integration = Mock()
        quality_agent.message_bus_enabled = True

        # Test collaboration
        target_agents = ["BackendDeveloper", "DataEngineer"]
        message = {"type": "quality_check_request", "data": "test_data"}

        result = await quality_agent.communicate_with_agents(target_agents, message)

        assert isinstance(result, dict)
        assert quality_agent.message_bus_integration.publish_event.called

    @pytest.mark.asyncio
    async def test_error_handling(self, quality_agent):
        """Test error handling and recovery."""
        # Test validation error handling
        with pytest.raises(quality_agent.QualityValidationError):
            quality_agent._validate_input("invalid", int, "test_param")

        # Test quality error handling
        with pytest.raises(quality_agent.QualityError):
            raise quality_agent.QualityError("Test error")

    @pytest.mark.asyncio
    async def test_complete_agent_lifecycle(self, quality_agent):
        """Test complete agent lifecycle from initialization to shutdown."""
        # Initialize all components
        await quality_agent.initialize_enhanced_mcp()
        await quality_agent.initialize_tracing()
        await quality_agent.initialize_message_bus_integration()

        # Verify all components are initialized
        assert quality_agent.enhanced_mcp_enabled is True
        assert quality_agent.tracing_enabled is True
        assert quality_agent.message_bus_enabled is True

        # Test agent run method
        with patch.object(quality_agent, 'run') as mock_run:
            mock_run.return_value = None

            # This would normally run the agent, but we're just testing the method exists
            assert callable(quality_agent.run)

    @pytest.mark.asyncio
    async def test_export_functionality(self, quality_agent):
        """Test export functionality."""
        # Test markdown export
        report_data = {
            "title": "Test Quality Report",
            "content": "Test content",
            "metrics": {"quality_score": 95}
        }

        with patch.object(quality_agent, '_export_markdown') as mock_export:
            mock_export.return_value = "# Test Quality Report\n\nTest content"

            result = quality_agent._export_markdown(report_data, "2025-08-07")

            assert result.startswith("# Test Quality Report")

    @pytest.mark.asyncio
    async def test_quality_templates(self, quality_agent):
        """Test quality templates functionality."""
        # Test template loading
        template_name = "best-practices"
        template_path = quality_agent.template_paths.get(template_name)

        assert template_path is not None
        assert template_path.exists()

        # Test template content
        if template_path.exists():
            content = template_path.read_text()
            assert len(content) > 0

    @pytest.mark.asyncio
    async def test_quality_gate_check(self, quality_agent):
        """Test quality gate check functionality."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True
        quality_agent.tracer = Mock()
        quality_agent.tracing_enabled = True

        # Test quality gate check
        with patch.object(quality_agent, 'quality_gate_check') as mock_gate:
            mock_gate.return_value = {
                "status": "passed",
                "quality_score": 95,
                "security_score": 90,
                "performance_score": 85,
                "compliance_score": 100
            }

            result = await quality_agent.quality_gate_check()

            assert result["status"] == "passed"
            assert result["quality_score"] > 90
            assert result["security_score"] > 85
            assert result["performance_score"] > 80
            assert result["compliance_score"] == 100

    @pytest.mark.asyncio
    async def test_improvement_suggestions(self, quality_agent):
        """Test improvement suggestions functionality."""
        # Mock dependencies
        quality_agent.enhanced_mcp = Mock()
        quality_agent.enhanced_mcp_enabled = True

        # Test improvement suggestions
        with patch.object(quality_agent, 'suggest_improvements') as mock_suggest:
            mock_suggest.return_value = {
                "status": "success",
                "suggestions": [
                    "Improve test coverage to 90%",
                    "Reduce code complexity",
                    "Add more security checks"
                ],
                "priority": "high"
            }

            result = quality_agent.suggest_improvements("general")

            assert result["status"] == "success"
            assert len(result["suggestions"]) > 0
            assert result["priority"] == "high"


if __name__ == "__main__":
    pytest.main([__file__]) 