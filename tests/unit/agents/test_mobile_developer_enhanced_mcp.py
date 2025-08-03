"""
Test suite for MobileDeveloper Agent Enhanced MCP Phase 2 and Tracing functionality.
"""

import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from bmad.agents.Agent.MobileDeveloper.mobiledeveloper import MobileDeveloperAgent


class TestMobileDeveloperEnhancedMCP:
    """Test cases for MobileDeveloper Agent Enhanced MCP Phase 2 and Tracing functionality."""

    @pytest_asyncio.fixture
    async def agent(self):
        """Create a MobileDeveloper agent instance for testing."""
        agent = MobileDeveloperAgent()
        
        # Mock dependencies
        with patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.get_performance_monitor'), \
             patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.get_advanced_policy_engine'), \
             patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.get_sprite_library'), \
             patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.get_context'), \
             patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.save_context'):
            
            yield agent

    @pytest.mark.asyncio
    async def test_initialize_enhanced_mcp_success(self, agent):
        """Test successful enhanced MCP initialization."""
        mock_enhanced_mcp = MagicMock()
        mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
        
        with patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.create_enhanced_mcp_integration', return_value=mock_enhanced_mcp):
            await agent.initialize_enhanced_mcp()
            
            assert agent.enhanced_mcp == mock_enhanced_mcp
            assert agent.enhanced_mcp_enabled is True

    @pytest.mark.asyncio
    async def test_initialize_enhanced_mcp_failure(self, agent):
        """Test enhanced MCP initialization failure."""
        mock_enhanced_mcp = MagicMock()
        mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=False)
        
        with patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.create_enhanced_mcp_integration', return_value=mock_enhanced_mcp):
            await agent.initialize_enhanced_mcp()
            
            assert agent.enhanced_mcp == mock_enhanced_mcp
            assert agent.enhanced_mcp_enabled is False

    @pytest.mark.asyncio
    async def test_initialize_tracing_success(self, agent):
        """Test successful tracing initialization."""
        mock_tracer = MagicMock()
        mock_tracer.initialize = AsyncMock(return_value=True)
        mock_tracer.setup_mobile_tracing = AsyncMock()
        
        with patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.BMADTracer', return_value=mock_tracer):
            await agent.initialize_tracing()
            
            assert agent.tracer == mock_tracer
            assert agent.tracing_enabled is True
            mock_tracer.setup_mobile_tracing.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_tracing_failure(self, agent):
        """Test tracing initialization failure."""
        mock_tracer = MagicMock()
        mock_tracer.initialize = AsyncMock(return_value=False)
        
        with patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.BMADTracer', return_value=mock_tracer):
            await agent.initialize_tracing()
            
            assert agent.tracer == mock_tracer
            assert agent.tracing_enabled is False

    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tools(self, agent):
        """Test enhanced MCP tools usage."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"core_result": "success"})
        
        agent.use_mobile_specific_enhanced_tools = AsyncMock(return_value={"specific_result": "success"})
        
        result = await agent.use_enhanced_mcp_tools({"test": "data"})
        
        assert "core_enhancement" in result
        assert "specific_result" in result

    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tools_disabled(self, agent):
        """Test enhanced MCP tools when disabled."""
        agent.enhanced_mcp_enabled = False
        agent.use_mobile_specific_mcp_tools = AsyncMock(return_value={"fallback": "success"})
        
        result = await agent.use_enhanced_mcp_tools({"test": "data"})
        
        assert result == {"fallback": "success"}

    @pytest.mark.asyncio
    async def test_use_mobile_specific_enhanced_tools(self, agent):
        """Test mobile-specific enhanced MCP tools."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"result": "success"})
        
        result = await agent.use_mobile_specific_enhanced_tools({
            "app_name": "TestApp",
            "platform": "react-native"
        })
        
        assert "app_development" in result
        assert "performance_optimization" in result
        assert "deployment_enhancement" in result

    @pytest.mark.asyncio
    async def test_communicate_with_agents_success(self, agent):
        """Test successful agent communication."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.communicate_with_agents = AsyncMock(return_value={"status": "success"})
        
        result = await agent.communicate_with_agents(["FrontendDeveloper"], {"message": "test"})
        
        assert result == {"status": "success"}

    @pytest.mark.asyncio
    async def test_communicate_with_agents_disabled(self, agent):
        """Test agent communication when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        result = await agent.communicate_with_agents(["FrontendDeveloper"], {"message": "test"})
        
        assert result == {"error": "Enhanced MCP not available"}

    @pytest.mark.asyncio
    async def test_use_external_tools_success(self, agent):
        """Test successful external tool usage."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.use_external_tool = AsyncMock(return_value={"tool_result": "success"})
        
        result = await agent.use_external_tools({"tool": "config"})
        
        assert result == {"tool_result": "success"}

    @pytest.mark.asyncio
    async def test_enhanced_security_validation(self, agent):
        """Test enhanced security validation."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.enhanced_security_validation = AsyncMock(return_value={"security": "validated"})
        
        result = await agent.enhanced_security_validation({"platform": "ios"})
        
        assert result == {"security": "validated"}

    @pytest.mark.asyncio
    async def test_enhanced_performance_optimization(self, agent):
        """Test enhanced performance optimization."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.enhanced_performance_optimization = AsyncMock(return_value={"performance": "optimized"})
        
        result = await agent.enhanced_performance_optimization({"type": "general"})
        
        assert result == {"performance": "optimized"}

    def test_get_enhanced_performance_summary(self, agent):
        """Test enhanced performance summary retrieval."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.get_performance_summary = MagicMock(return_value={"summary": "data"})
        
        result = agent.get_enhanced_performance_summary()
        
        assert result == {"summary": "data"}

    def test_get_enhanced_communication_summary(self, agent):
        """Test enhanced communication summary retrieval."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.get_communication_summary = MagicMock(return_value={"communication": "data"})
        
        result = agent.get_enhanced_communication_summary()
        
        assert result == {"communication": "data"}

    @pytest.mark.asyncio
    async def test_trace_app_development(self, agent):
        """Test app development tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_app_development = AsyncMock(return_value={"trace": "data"})
        
        result = await agent.trace_app_development({
            "app_name": "TestApp",
            "platform": "react-native"
        })
        
        assert result == {"trace": "data"}

    @pytest.mark.asyncio
    async def test_trace_mobile_performance(self, agent):
        """Test mobile performance tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_mobile_performance = AsyncMock(return_value={"performance_trace": "data"})
        
        result = await agent.trace_mobile_performance({
            "type": "general",
            "platform": "react-native"
        })
        
        assert result == {"performance_trace": "data"}

    @pytest.mark.asyncio
    async def test_trace_mobile_deployment(self, agent):
        """Test mobile deployment tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_mobile_deployment = AsyncMock(return_value={"deployment_trace": "data"})
        
        result = await agent.trace_mobile_deployment({
            "target": "app-store",
            "platform": "ios"
        })
        
        assert result == {"deployment_trace": "data"}

    @pytest.mark.asyncio
    async def test_trace_mobile_error(self, agent):
        """Test mobile error tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_mobile_error = AsyncMock(return_value={"error_trace": "data"})
        
        result = await agent.trace_mobile_error({
            "type": "crash",
            "message": "Test error"
        })
        
        assert result == {"error_trace": "data"}

    def test_get_tracing_summary(self, agent):
        """Test tracing summary retrieval."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.get_tracing_summary = MagicMock(return_value={"tracing_summary": "data"})
        
        result = agent.get_tracing_summary()
        
        assert result == {"tracing_summary": "data"}

    @pytest.mark.asyncio
    async def test_create_app_with_enhanced_mcp_and_tracing(self, agent):
        """Test create_app method with enhanced MCP and tracing integration."""
        agent.enhanced_mcp_enabled = True
        agent.tracing_enabled = True
        agent.tracer = MagicMock()  # Add tracer mock
        
        # Mock enhanced MCP
        agent.use_enhanced_mcp_tools = AsyncMock(return_value={"enhanced": "data"})
        
        # Mock tracing
        agent.trace_app_development = AsyncMock(return_value={"trace": "data"})
        
        # Mock Supabase context
        with patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.get_context'), \
             patch('bmad.agents.Agent.MobileDeveloper.mobiledeveloper.save_context'):
            
            result = await agent.create_app("TestApp", "react-native", "business")
            
            assert result["status"] == "success"
            assert result["enhanced_mcp_enabled"] is True
            assert result["tracing_enabled"] is True
            assert "enhanced_mcp_data" in result
            assert "tracing_data" in result

    @pytest.mark.asyncio
    async def test_run_with_enhanced_mcp(self, agent):
        """Test run method with enhanced MCP initialization."""
        agent.initialize_mcp = AsyncMock()
        agent.initialize_enhanced_mcp = AsyncMock()
        agent.initialize_tracing = AsyncMock()
        agent.collaborate_example = AsyncMock()
        
        await agent.run()
        
        agent.initialize_mcp.assert_called_once()
        agent.initialize_enhanced_mcp.assert_called_once()
        agent.initialize_tracing.assert_called_once()
        agent.collaborate_example.assert_called_once() 