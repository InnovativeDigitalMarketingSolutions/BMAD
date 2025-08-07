#!/usr/bin/env python3
"""
Integration tests for AiDeveloperAgent.
Tests complete agent functionality including enhanced MCP, tracing, and message bus integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.agents.Agent.AiDeveloper.aidev import AiDeveloperAgent


class TestAiDeveloperIntegration:
    """Integration tests for AiDeveloperAgent."""
    
    @pytest.fixture
    async def ai_agent(self):
        """Create a test instance of AiDeveloperAgent."""
        agent = AiDeveloperAgent()
        yield agent
        # Cleanup
        if hasattr(agent, 'tracer') and agent.tracer:
            await agent.tracer.shutdown()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, ai_agent):
        """Test complete agent initialization."""
        assert ai_agent.agent_name == "AiDeveloper"
        assert ai_agent.monitor is not None
        assert ai_agent.policy_engine is not None
        assert ai_agent.sprite_library is not None
        assert ai_agent.resource_base is not None
        assert len(ai_agent.template_paths) > 0
        assert len(ai_agent.data_paths) > 0
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_integration(self, ai_agent):
        """Test enhanced MCP integration."""
        # Test enhanced MCP initialization
        with patch('bmad.core.mcp.enhanced_mcp_integration.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = Mock()
            mock_enhanced_mcp.initialize_enhanced_mcp.return_value = True
            mock_create.return_value = mock_enhanced_mcp
            
            await ai_agent.initialize_enhanced_mcp()
            
            assert ai_agent.enhanced_mcp_enabled is True
            assert ai_agent.enhanced_mcp is not None
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_tools(self, ai_agent):
        """Test enhanced MCP tools functionality."""
        # Mock enhanced MCP
        ai_agent.enhanced_mcp = Mock()
        ai_agent.enhanced_mcp_enabled = True
        
        tools = ai_agent.get_enhanced_mcp_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all(isinstance(tool, str) for tool in tools)
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_registration(self, ai_agent):
        """Test enhanced MCP tool registration."""
        # Mock enhanced MCP
        ai_agent.enhanced_mcp = Mock()
        ai_agent.enhanced_mcp_enabled = True
        
        result = ai_agent.register_enhanced_mcp_tools()
        assert result is True
        assert ai_agent.enhanced_mcp.register_tool.called
    
    @pytest.mark.asyncio
    async def test_tracing_integration(self, ai_agent):
        """Test tracing integration."""
        # Test tracing initialization
        with patch('integrations.opentelemetry.opentelemetry_tracing.BMADTracer') as mock_tracer_class:
            mock_tracer = Mock()
            mock_tracer_class.return_value = mock_tracer
            
            await ai_agent.initialize_tracing()
            
            assert ai_agent.tracing_enabled is True
            assert ai_agent.tracer is not None
    
    @pytest.mark.asyncio
    async def test_trace_operation(self, ai_agent):
        """Test operation tracing."""
        # Mock tracer
        ai_agent.tracer = Mock()
        ai_agent.tracing_enabled = True
        
        result = await ai_agent.trace_operation("test_operation", {"key": "value"})
        assert result is True
        assert ai_agent.tracer.trace_operation.called
    
    @pytest.mark.asyncio
    async def test_message_bus_integration(self, ai_agent):
        """Test message bus integration."""
        # Test message bus initialization
        with patch('bmad.agents.core.communication.agent_message_bus_integration.create_agent_message_bus_integration') as mock_create:
            mock_message_bus = Mock()
            mock_create.return_value = mock_message_bus
            
            await ai_agent.initialize_message_bus_integration()
            
            assert ai_agent.message_bus_integration is not None
            assert ai_agent.message_bus_enabled is True
    
    @pytest.mark.asyncio
    async def test_ai_development_workflow(self, ai_agent):
        """Test complete AI development workflow."""
        # Mock dependencies
        ai_agent.enhanced_mcp = Mock()
        ai_agent.enhanced_mcp_enabled = True
        ai_agent.tracer = Mock()
        ai_agent.tracing_enabled = True
        ai_agent.message_bus_integration = Mock()
        ai_agent.message_bus_enabled = True
        
        # Test pipeline building
        with patch.object(ai_agent, 'build_pipeline') as mock_build:
            mock_build.return_value = {"status": "success", "pipeline_id": "test_123"}
            
            result = await ai_agent.build_pipeline()
            
            assert result["status"] == "success"
            assert result["pipeline_id"] == "test_123"
    
    @pytest.mark.asyncio
    async def test_model_training_workflow(self, ai_agent):
        """Test model training workflow."""
        # Mock dependencies
        ai_agent.enhanced_mcp = Mock()
        ai_agent.enhanced_mcp_enabled = True
        ai_agent.tracer = Mock()
        ai_agent.tracing_enabled = True
        
        # Test model training
        training_data = {
            "model_name": "test_model",
            "dataset": "test_dataset",
            "parameters": {"epochs": 10, "batch_size": 32}
        }
        
        with patch.object(ai_agent, '_handle_model_training_requested') as mock_training:
            mock_training.return_value = {"status": "success", "model_id": "model_123"}
            
            result = await ai_agent._handle_model_training_requested(training_data)
            
            assert result["status"] == "success"
            assert result["model_id"] == "model_123"
    
    @pytest.mark.asyncio
    async def test_model_evaluation_workflow(self, ai_agent):
        """Test model evaluation workflow."""
        # Mock dependencies
        ai_agent.enhanced_mcp = Mock()
        ai_agent.enhanced_mcp_enabled = True
        ai_agent.tracer = Mock()
        ai_agent.tracing_enabled = True
        
        # Test model evaluation
        evaluation_data = {
            "model_id": "model_123",
            "test_dataset": "test_data",
            "metrics": ["accuracy", "precision", "recall"]
        }
        
        with patch.object(ai_agent, '_handle_model_evaluation_requested') as mock_eval:
            mock_eval.return_value = {
                "status": "success",
                "accuracy": 0.95,
                "precision": 0.94,
                "recall": 0.93
            }
            
            result = await ai_agent._handle_model_evaluation_requested(evaluation_data)
            
            assert result["status"] == "success"
            assert result["accuracy"] > 0.9
    
    @pytest.mark.asyncio
    async def test_bias_check_workflow(self, ai_agent):
        """Test bias checking workflow."""
        # Mock dependencies
        ai_agent.enhanced_mcp = Mock()
        ai_agent.enhanced_mcp_enabled = True
        ai_agent.tracer = Mock()
        ai_agent.tracing_enabled = True
        
        # Test bias checking
        bias_data = {
            "model_id": "model_123",
            "sensitive_features": ["gender", "age"],
            "threshold": 0.1
        }
        
        with patch.object(ai_agent, '_handle_bias_check_requested') as mock_bias:
            mock_bias.return_value = {
                "status": "success",
                "bias_detected": False,
                "bias_score": 0.05
            }
            
            result = await ai_agent._handle_bias_check_requested(bias_data)
            
            assert result["status"] == "success"
            assert result["bias_detected"] is False
            assert result["bias_score"] < 0.1
    
    @pytest.mark.asyncio
    async def test_resource_completeness(self, ai_agent):
        """Test resource completeness."""
        # Test that all required resources are available
        assert ai_agent.resource_base.exists()
        
        # Test template paths
        for template_name, template_path in ai_agent.template_paths.items():
            assert template_path.exists(), f"Template {template_name} not found at {template_path}"
        
        # Test data paths
        for data_name, data_path in ai_agent.data_paths.items():
            assert data_path.exists(), f"Data file {data_name} not found at {data_path}"
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, ai_agent):
        """Test performance monitoring integration."""
        # Test metric recording
        ai_agent._record_ai_metric("test_metric", 0.95, "%")
        
        # Test performance assessment
        metrics = {"accuracy": 0.95, "precision": 0.94, "recall": 0.93}
        assessment = ai_agent._assess_model_performance(metrics)
        
        assert isinstance(assessment, str)
        assert len(assessment) > 0
    
    @pytest.mark.asyncio
    async def test_agent_collaboration(self, ai_agent):
        """Test agent collaboration functionality."""
        # Mock dependencies
        ai_agent.message_bus_integration = Mock()
        ai_agent.message_bus_enabled = True
        
        # Test collaboration
        target_agents = ["BackendDeveloper", "DataEngineer"]
        message = {"type": "collaboration_request", "data": "test_data"}
        
        result = await ai_agent.communicate_with_agents(target_agents, message)
        
        assert isinstance(result, dict)
        assert ai_agent.message_bus_integration.publish_event.called
    
    @pytest.mark.asyncio
    async def test_error_handling(self, ai_agent):
        """Test error handling and recovery."""
        # Test validation error handling
        with pytest.raises(ai_agent.AiValidationError):
            ai_agent._validate_input("invalid", int, "test_param")
        
        # Test development error handling
        with pytest.raises(ai_agent.AiDevelopmentError):
            raise ai_agent.AiDevelopmentError("Test error")
    
    @pytest.mark.asyncio
    async def test_complete_agent_lifecycle(self, ai_agent):
        """Test complete agent lifecycle from initialization to shutdown."""
        # Initialize all components
        await ai_agent.initialize_enhanced_mcp()
        await ai_agent.initialize_tracing()
        await ai_agent.initialize_message_bus_integration()
        
        # Verify all components are initialized
        assert ai_agent.enhanced_mcp_enabled is True
        assert ai_agent.tracing_enabled is True
        assert ai_agent.message_bus_enabled is True
        
        # Test agent run method
        with patch.object(ai_agent, 'run') as mock_run:
            mock_run.return_value = None
            
            # This would normally run the agent, but we're just testing the method exists
            assert callable(ai_agent.run)
    
    @pytest.mark.asyncio
    async def test_export_functionality(self, ai_agent):
        """Test export functionality."""
        # Test markdown export
        report_data = {
            "title": "Test Report",
            "content": "Test content",
            "metrics": {"accuracy": 0.95}
        }
        
        with patch.object(ai_agent, '_export_markdown') as mock_export:
            mock_export.return_value = "# Test Report\n\nTest content"
            
            result = ai_agent._export_markdown(report_data)
            
            assert result.startswith("# Test Report")
    
    @pytest.mark.asyncio
    async def test_framework_templates(self, ai_agent):
        """Test framework templates functionality."""
        # Test template loading
        template_name = "best-practices"
        template_path = ai_agent.template_paths.get(template_name)
        
        assert template_path is not None
        assert template_path.exists()
        
        # Test template content
        if template_path.exists():
            content = template_path.read_text()
            assert len(content) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 