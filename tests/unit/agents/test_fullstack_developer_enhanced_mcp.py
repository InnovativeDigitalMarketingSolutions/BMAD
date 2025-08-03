"""
Test suite for FullstackDeveloper Agent Enhanced MCP and Tracing functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper import FullstackDeveloperAgent


class TestFullstackDeveloperEnhancedMCP:
    """Test enhanced MCP functionality for FullstackDeveloper agent."""

    @pytest.fixture
    def agent(self):
        """Create FullstackDeveloper agent instance."""
        with patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.get_framework_templates_manager') as mock_manager, \
             patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.get_performance_monitor') as mock_monitor, \
             patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.get_advanced_policy_engine') as mock_policy, \
             patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.get_sprite_library') as mock_sprite:
            # Mock all dependencies
            mock_manager.return_value = MagicMock()
            mock_manager.return_value.get_framework_template.return_value = MagicMock()
            mock_monitor.return_value = MagicMock()
            mock_policy.return_value = MagicMock()
            mock_sprite.return_value = MagicMock()
            return FullstackDeveloperAgent()

    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization(self, agent):
        """Test enhanced MCP initialization."""
        with patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = MagicMock()
            mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
            mock_create.return_value = mock_enhanced_mcp
            
            await agent.initialize_enhanced_mcp()
            
            assert agent.enhanced_mcp_enabled is True
            mock_create.assert_called_once_with("FullstackDeveloper")
            mock_enhanced_mcp.initialize_enhanced_mcp.assert_called_once()

    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization_failure(self, agent):
        """Test enhanced MCP initialization failure."""
        with patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = MagicMock()
            mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=False)
            mock_create.return_value = mock_enhanced_mcp
            
            await agent.initialize_enhanced_mcp()
            
            assert agent.enhanced_mcp_enabled is False

    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tools(self, agent):
        """Test enhanced MCP tools usage."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"enhanced_result": "success"})
        
        with patch.object(agent, 'use_fullstack_specific_enhanced_tools') as mock_specific:
            mock_specific.return_value = {"specific_result": "success"}
            
            result = await agent.use_enhanced_mcp_tools({
                "feature_name": "UserAuth",
                "capabilities": ["frontend", "backend"]
            })
            
            assert "core_enhancement" in result
            assert "specific_result" in result
            agent.enhanced_mcp.use_enhanced_mcp_tool.assert_called_once()

    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tools_fallback(self, agent):
        """Test enhanced MCP tools fallback when not available."""
        agent.enhanced_mcp_enabled = False
        
        with patch.object(agent, 'use_fullstack_specific_mcp_tools') as mock_fallback:
            mock_fallback.return_value = {"fallback_result": "success"}
            
            result = await agent.use_enhanced_mcp_tools({
                "feature_name": "UserAuth"
            })
            
            assert result == {"fallback_result": "success"}
            mock_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_use_fullstack_specific_enhanced_tools(self, agent):
        """Test fullstack-specific enhanced MCP tools."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"feature_result": "success"})
        
        result = await agent.use_fullstack_specific_enhanced_tools({
            "feature_name": "UserAuth",
            "complexity": "medium",
            "frontend_requirements": {"components": ["LoginForm"]},
            "backend_requirements": {"apis": ["/api/auth"]}
        })
        
        assert "feature_development" in result
        assert "integration_enhancement" in result
        assert "performance_optimization" in result
        assert agent.enhanced_mcp.use_enhanced_mcp_tool.call_count == 3  # feature, integration, performance

    @pytest.mark.asyncio
    async def test_communicate_with_agents(self, agent):
        """Test enhanced agent communication."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.communicate_with_agents = AsyncMock(return_value={"communication_result": "success"})
        
        result = await agent.communicate_with_agents(
            ["FrontendDeveloper", "BackendDeveloper"],
            {"type": "feature_ready", "feature": "UserAuth"}
        )
        
        assert result["communication_result"] == "success"
        agent.enhanced_mcp.communicate_with_agents.assert_called_once()

    @pytest.mark.asyncio
    async def test_communicate_with_agents_disabled(self, agent):
        """Test agent communication when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        result = await agent.communicate_with_agents(
            ["FrontendDeveloper"],
            {"type": "test"}
        )
        
        assert "error" in result
        assert result["error"] == "Enhanced MCP not available"

    @pytest.mark.asyncio
    async def test_use_external_tools(self, agent):
        """Test external tools usage."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.use_external_tool = AsyncMock(return_value={"tool_result": "success"})
        
        result = await agent.use_external_tools({
            "tool_name": "github",
            "action": "create_pr"
        })
        
        assert result["tool_result"] == "success"
        agent.enhanced_mcp.use_external_tool.assert_called_once()

    @pytest.mark.asyncio
    async def test_enhanced_security_validation(self, agent):
        """Test enhanced security validation."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.enhanced_security_validation = AsyncMock(return_value={"security_result": "validated"})
        
        result = await agent.enhanced_security_validation({
            "auth_method": "multi_factor",
            "security_level": "enterprise"
        })
        
        assert result["security_result"] == "validated"
        agent.enhanced_mcp.enhanced_security_validation.assert_called_once()

    @pytest.mark.asyncio
    async def test_enhanced_performance_optimization(self, agent):
        """Test enhanced performance optimization."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.enhanced_performance_optimization = AsyncMock(return_value={"performance_result": "optimized"})
        
        result = await agent.enhanced_performance_optimization({
            "cache_strategy": "adaptive",
            "target_latency": 50
        })
        
        assert result["performance_result"] == "optimized"
        agent.enhanced_mcp.enhanced_performance_optimization.assert_called_once()

    def test_get_enhanced_performance_summary(self, agent):
        """Test enhanced performance summary retrieval."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.get_performance_summary.return_value = {"total_operations": 25, "avg_latency": 45}
        
        result = agent.get_enhanced_performance_summary()
        
        assert result["total_operations"] == 25
        assert result["avg_latency"] == 45
        agent.enhanced_mcp.get_performance_summary.assert_called_once()

    def test_get_enhanced_performance_summary_disabled(self, agent):
        """Test performance summary when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        result = agent.get_enhanced_performance_summary()
        
        assert result == {}

    def test_get_enhanced_communication_summary(self, agent):
        """Test enhanced communication summary retrieval."""
        agent.enhanced_mcp_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp.get_communication_summary.return_value = {"total_messages": 15, "success_rate": 95}
        
        result = agent.get_enhanced_communication_summary()
        
        assert result["total_messages"] == 15
        assert result["success_rate"] == 95
        agent.enhanced_mcp.get_communication_summary.assert_called_once()

    def test_get_enhanced_communication_summary_disabled(self, agent):
        """Test communication summary when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        result = agent.get_enhanced_communication_summary()
        
        assert result == {}

    @pytest.mark.asyncio
    async def test_run_with_enhanced_mcp(self, agent):
        """Test run method with enhanced MCP initialization."""
        with patch.object(agent, 'initialize_mcp') as mock_init_mcp, \
             patch.object(agent, 'initialize_enhanced_mcp') as mock_init_enhanced, \
             patch.object(agent, 'initialize_tracing') as mock_init_tracing, \
             patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.subscribe') as mock_subscribe, \
             patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.get_context') as mock_get_context, \
             patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.save_context') as mock_save_context:
            
            # Mock context calls
            mock_get_context.return_value = {"architecture": "test"}
            mock_save_context.return_value = True
            
            # Mock the infinite loop to exit early
            with patch('asyncio.sleep', side_effect=KeyboardInterrupt):
                try:
                    await agent.run()
                except KeyboardInterrupt:
                    pass
            
            mock_init_mcp.assert_called_once()
            mock_init_enhanced.assert_called_once()
            mock_init_tracing.assert_called_once()
            mock_subscribe.assert_called()

    @pytest.mark.asyncio
    async def test_initialize_tracing_success(self, agent):
        """Test successful tracing initialization."""
        with patch('bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper.BMADTracer') as mock_tracer_class:
            mock_tracer = MagicMock()
            mock_tracer.initialize = AsyncMock(return_value=True)
            mock_tracer.setup_fullstack_tracing = AsyncMock()
            mock_tracer_class.return_value = mock_tracer
            
            await agent.initialize_tracing()
            
            assert agent.tracing_enabled is True
            mock_tracer.initialize.assert_called_once()
            mock_tracer.setup_fullstack_tracing.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_tracing_failure(self, agent):
        """Test tracing initialization failure."""
        agent.tracer = MagicMock()
        agent.tracer.initialize = AsyncMock(return_value=False)
        
        await agent.initialize_tracing()
        
        assert agent.tracing_enabled is False

    @pytest.mark.asyncio
    async def test_trace_feature_development_success(self, agent):
        """Test successful feature development tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_feature_development = AsyncMock(return_value={"trace_id": "123", "status": "success"})
        
        result = await agent.trace_feature_development({
            "feature_name": "UserAuth",
            "complexity": "medium",
            "frontend_components": ["LoginForm"]
        })
        
        assert result["trace_id"] == "123"
        assert result["status"] == "success"
        agent.tracer.trace_feature_development.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_fullstack_integration_success(self, agent):
        """Test successful fullstack integration tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_fullstack_integration = AsyncMock(return_value={"integration_trace_id": "456", "status": "success"})
        
        result = await agent.trace_fullstack_integration({
            "type": "api_integration",
            "frontend_component": "LoginForm",
            "backend_api": "/api/auth"
        })
        
        assert result["integration_trace_id"] == "456"
        assert result["status"] == "success"
        agent.tracer.trace_fullstack_integration.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_performance_optimization_success(self, agent):
        """Test successful performance optimization tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_performance_optimization = AsyncMock(return_value={"performance_trace_id": "789", "status": "success"})
        
        result = await agent.trace_performance_optimization({
            "type": "general",
            "frontend_optimizations": {"bundle_size": 150},
            "backend_optimizations": {"response_time": 100}
        })
        
        assert result["performance_trace_id"] == "789"
        assert result["status"] == "success"
        agent.tracer.trace_performance_optimization.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_fullstack_error_success(self, agent):
        """Test successful fullstack error tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_fullstack_error = AsyncMock(return_value={"error_trace_id": "999", "status": "success"})
        
        result = await agent.trace_fullstack_error({
            "type": "integration_error",
            "message": "API connection failed",
            "feature_name": "UserAuth"
        })
        
        assert result["error_trace_id"] == "999"
        assert result["status"] == "success"
        agent.tracer.trace_fullstack_error.assert_called_once()

    def test_get_tracing_summary_success(self, agent):
        """Test successful tracing summary retrieval."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.get_tracing_summary.return_value = {"total_traces": 20, "status": "active"}
        
        result = agent.get_tracing_summary()
        
        assert result["total_traces"] == 20
        assert result["status"] == "active"
        agent.tracer.get_tracing_summary.assert_called_once()

    def test_get_tracing_summary_fallback(self, agent):
        """Test tracing summary fallback when tracing is disabled."""
        agent.tracing_enabled = False
        
        result = agent.get_tracing_summary()
        
        assert result == {}

    @pytest.mark.asyncio
    async def test_develop_feature_with_enhanced_mcp_and_tracing(self, agent):
        """Test develop_feature with enhanced MCP and tracing integration."""
        agent.enhanced_mcp_enabled = True
        agent.tracing_enabled = True
        agent.enhanced_mcp = MagicMock()
        agent.tracer = MagicMock()
        agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"enhanced_result": "success"})
        agent.tracer.trace_feature_development = AsyncMock(return_value={"trace_id": "123"})
        
        with patch.object(agent, 'use_enhanced_mcp_tools') as mock_enhanced:
            mock_enhanced.return_value = {"enhanced_mcp_result": "success"}
            
            result = await agent.develop_feature("UserAuth", "User authentication feature")
            
            assert "enhanced_mcp_data" in result
            assert result["enhanced_mcp_enabled"] is True
            assert "tracing_data" in result
            assert result["tracing_enabled"] is True
            mock_enhanced.assert_called_once()
            agent.tracer.trace_feature_development.assert_called_once() 