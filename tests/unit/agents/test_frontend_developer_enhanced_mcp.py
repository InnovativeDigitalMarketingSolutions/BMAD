"""
Test suite for FrontendDeveloper Agent Enhanced MCP Integration.

Tests the enhanced MCP capabilities for Phase 2 features including:
- Enhanced MCP tool integration
- Frontend-specific enhanced tools
- Inter-agent communication
- External tool integration
- Security validation
- Performance optimization
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

from bmad.agents.Agent.FrontendDeveloper.frontenddeveloper import FrontendDeveloperAgent


@pytest.fixture
def agent():
    """Create FrontendDeveloper agent instance."""
    with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_framework_templates_manager') as mock_manager, \
         patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_performance_monitor') as mock_monitor, \
         patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_advanced_policy_engine') as mock_policy, \
         patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.get_sprite_library') as mock_sprite:

        # Mock all dependencies
        mock_manager.return_value = MagicMock()
        mock_manager.return_value.get_framework_template.return_value = MagicMock()
        mock_monitor.return_value = MagicMock()
        mock_policy.return_value = MagicMock()
        mock_sprite.return_value = MagicMock()

        return FrontendDeveloperAgent()


@pytest.mark.asyncio
async def test_initialize_enhanced_mcp_success(agent):
    """Test successful enhanced MCP initialization."""
    with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_enhanced_mcp_integration') as mock_create:
        mock_enhanced_mcp = MagicMock()
        mock_enhanced_mcp.initialize_enhanced_mcp = AsyncMock(return_value=True)
        mock_create.return_value = mock_enhanced_mcp
        
        await agent.initialize_enhanced_mcp()
        
        assert agent.enhanced_mcp_enabled is True
        assert agent.enhanced_mcp is not None
        mock_create.assert_called_once_with("FrontendDeveloper")


@pytest.mark.asyncio
async def test_initialize_enhanced_mcp_failure(agent):
    """Test enhanced MCP initialization failure."""
    with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.create_enhanced_mcp_integration') as mock_create:
        mock_create.side_effect = Exception("Enhanced MCP creation failed")
        
        await agent.initialize_enhanced_mcp()
        
        assert agent.enhanced_mcp_enabled is False
        assert agent.enhanced_mcp is None


@pytest.mark.asyncio
async def test_use_enhanced_mcp_tools_success(agent):
    """Test successful enhanced MCP tools usage."""
    # Setup enhanced MCP
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"core_enhancement": "success"})
    
    # Mock frontend-specific enhanced tools
    with patch.object(agent, 'use_frontend_specific_enhanced_tools') as mock_frontend:
        mock_frontend.return_value = {"frontend_enhancement": "success"}
        
        result = await agent.use_enhanced_mcp_tools({
            "component_name": "Button",
            "capabilities": ["accessibility"],
            "performance_metrics": {"score": 95}
        })
        
        assert "core_enhancement" in result
        assert "frontend_enhancement" in result
        agent.enhanced_mcp.use_enhanced_mcp_tool.assert_called_once()


@pytest.mark.asyncio
async def test_use_enhanced_mcp_tools_fallback(agent):
    """Test enhanced MCP tools fallback to standard MCP."""
    agent.enhanced_mcp_enabled = False
    
    with patch.object(agent, 'use_frontend_specific_mcp_tools') as mock_frontend:
        mock_frontend.return_value = {"standard_enhancement": "success"}
        
        result = await agent.use_enhanced_mcp_tools({
            "component_name": "Button"
        })
        
        assert "standard_enhancement" in result
        mock_frontend.assert_called_once()


@pytest.mark.asyncio
async def test_use_frontend_specific_enhanced_tools(agent):
    """Test frontend-specific enhanced MCP tools."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(side_effect=[
        {"enhanced_component_development": "success"},
        {"enhanced_accessibility_testing": "success"},
        {"enhanced_design_system_integration": "success"},
        {"enhanced_frontend_performance": "success"}
    ])
    
    result = await agent.use_frontend_specific_enhanced_tools({
        "component_name": "Button",
        "framework": "react",
        "ui_library": "shadcn/ui"
    })
    
    assert "enhanced_component_development" in result
    assert "enhanced_accessibility_testing" in result
    assert "enhanced_design_system_integration" in result
    assert "enhanced_frontend_performance" in result
    assert agent.enhanced_mcp.use_enhanced_mcp_tool.call_count == 4


@pytest.mark.asyncio
async def test_communicate_with_agents_success(agent):
    """Test successful inter-agent communication."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.communicate_with_agents = AsyncMock(return_value={"communication": "success"})
    
    result = await agent.communicate_with_agents(
        ["BackendDeveloper", "UXUIDesigner"],
        {"type": "collaboration", "message": "Component design"}
    )
    
    assert result["communication"] == "success"
    agent.enhanced_mcp.communicate_with_agents.assert_called_once()


@pytest.mark.asyncio
async def test_communicate_with_agents_fallback(agent):
    """Test inter-agent communication fallback."""
    agent.enhanced_mcp_enabled = False
    
    result = await agent.communicate_with_agents(
        ["BackendDeveloper"],
        {"type": "collaboration", "message": "Component design"}
    )
    
    assert result == {}


@pytest.mark.asyncio
async def test_use_external_tools_success(agent):
    """Test successful external tool integration."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.use_external_tools = AsyncMock(return_value={"external_tool": "success"})
    
    result = await agent.use_external_tools({
        "tool": "figma",
        "action": "parse",
        "file_id": "test123"
    })
    
    assert result["external_tool"] == "success"
    agent.enhanced_mcp.use_external_tools.assert_called_once()


@pytest.mark.asyncio
async def test_enhanced_security_validation(agent):
    """Test enhanced security validation."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.enhanced_security_validation = AsyncMock(return_value={"security": "validated"})
    
    result = await agent.enhanced_security_validation({
        "auth_method": "multi_factor",
        "security_level": "enterprise"
    })
    
    assert result["security"] == "validated"
    agent.enhanced_mcp.enhanced_security_validation.assert_called_once()


@pytest.mark.asyncio
async def test_enhanced_performance_optimization(agent):
    """Test enhanced performance optimization."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.enhanced_performance_optimization = AsyncMock(return_value={"performance": "optimized"})
    
    result = await agent.enhanced_performance_optimization({
        "cache_strategy": "adaptive",
        "target_latency": 50
    })
    
    assert result["performance"] == "optimized"
    agent.enhanced_mcp.enhanced_performance_optimization.assert_called_once()


def test_get_enhanced_performance_summary_success(agent):
    """Test enhanced performance summary retrieval."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.get_performance_summary.return_value = {"performance": "summary"}
    
    result = agent.get_enhanced_performance_summary()
    
    assert result["performance"] == "summary"
    agent.enhanced_mcp.get_performance_summary.assert_called_once()


def test_get_enhanced_performance_summary_fallback(agent):
    """Test enhanced performance summary fallback."""
    agent.enhanced_mcp_enabled = False
    
    result = agent.get_enhanced_performance_summary()
    
    assert result == {}


def test_get_enhanced_communication_summary_success(agent):
    """Test enhanced communication summary retrieval."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.get_communication_summary.return_value = {"communication": "summary"}
    
    result = agent.get_enhanced_communication_summary()
    
    assert result["communication"] == "summary"
    agent.enhanced_mcp.get_communication_summary.assert_called_once()


def test_get_enhanced_communication_summary_fallback(agent):
    """Test enhanced communication summary fallback."""
    agent.enhanced_mcp_enabled = False
    
    result = agent.get_enhanced_communication_summary()
    
    assert result == {}


@pytest.mark.asyncio
async def test_build_shadcn_component_with_enhanced_mcp(agent):
    """Test build_shadcn_component with enhanced MCP integration."""
    agent.enhanced_mcp_enabled = True
    agent.enhanced_mcp = MagicMock()
    agent.enhanced_mcp.use_enhanced_mcp_tool = AsyncMock(return_value={"enhanced_result": "success"})
    
    with patch.object(agent, 'use_enhanced_mcp_tools') as mock_enhanced:
        mock_enhanced.return_value = {"enhanced_mcp_result": "success"}
        
        result = await agent.build_shadcn_component("Button")
        
        assert "enhanced_mcp_result" in result
        assert result["enhanced_mcp_enabled"] is True
        mock_enhanced.assert_called_once()


@pytest.mark.asyncio
async def test_run_with_enhanced_mcp_initialization(agent):
    """Test run method with enhanced MCP initialization."""
    with patch.object(agent, 'initialize_mcp') as mock_init_mcp, \
         patch.object(agent, 'initialize_enhanced_mcp') as mock_init_enhanced, \
         patch.object(agent, 'initialize_tracing') as mock_init_tracing, \
         patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.subscribe') as mock_subscribe, \
         patch.object(agent, 'collaborate_example') as mock_collaborate:
        
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
        mock_collaborate.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_tracing_success(agent):
    """Test successful tracing initialization."""
    with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.BMADTracer') as mock_tracer_class:
        mock_tracer = MagicMock()
        mock_tracer.initialize = AsyncMock(return_value=True)
        mock_tracer.setup_frontend_tracing = AsyncMock()
        mock_tracer_class.return_value = mock_tracer
        
        await agent.initialize_tracing()
        
        assert agent.tracing_enabled is True
        assert agent.tracer is not None
        mock_tracer.initialize.assert_called_once()
        mock_tracer.setup_frontend_tracing.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_tracing_failure(agent):
    """Test tracing initialization failure."""
    with patch('bmad.agents.Agent.FrontendDeveloper.frontenddeveloper.BMADTracer') as mock_tracer_class:
        mock_tracer_class.side_effect = Exception("Tracing creation failed")
        
        await agent.initialize_tracing()
        
        assert agent.tracing_enabled is False
        assert agent.tracer is None


@pytest.mark.asyncio
async def test_trace_component_development_success(agent):
    """Test successful component development tracing."""
    agent.tracing_enabled = True
    agent.tracer = MagicMock()
    agent.tracer.trace_component_development = AsyncMock(return_value={"trace_id": "123", "status": "success"})
    
    result = await agent.trace_component_development("Button", {
        "phase": "build",
        "framework": "react",
        "ui_library": "shadcn/ui"
    })
    
    assert result["trace_id"] == "123"
    assert result["status"] == "success"
    agent.tracer.trace_component_development.assert_called_once()


@pytest.mark.asyncio
async def test_trace_user_interaction_success(agent):
    """Test successful user interaction tracing."""
    agent.tracing_enabled = True
    agent.tracer = MagicMock()
    agent.tracer.trace_user_interaction = AsyncMock(return_value={"interaction_id": "456", "status": "success"})
    
    result = await agent.trace_user_interaction({
        "type": "click",
        "component_name": "Button",
        "behavior": {"duration": 100}
    })
    
    assert result["interaction_id"] == "456"
    assert result["status"] == "success"
    agent.tracer.trace_user_interaction.assert_called_once()


@pytest.mark.asyncio
async def test_trace_performance_metrics_success(agent):
    """Test successful performance metrics tracing."""
    agent.tracing_enabled = True
    agent.tracer = MagicMock()
    agent.tracer.trace_performance_metrics = AsyncMock(return_value={"performance_id": "789", "status": "success"})
    
    result = await agent.trace_performance_metrics({
        "bundle_size": 150,
        "load_time": 200,
        "render_time": 50
    })
    
    assert result["performance_id"] == "789"
    assert result["status"] == "success"
    agent.tracer.trace_performance_metrics.assert_called_once()


@pytest.mark.asyncio
async def test_trace_error_event_success(agent):
    """Test successful error event tracing."""
    agent.tracing_enabled = True
    agent.tracer = MagicMock()
    agent.tracer.trace_error_event = AsyncMock(return_value={"error_id": "999", "status": "success"})
    
    result = await agent.trace_error_event({
        "type": "render_error",
        "message": "Component failed to render",
        "component_name": "Button"
    })
    
    assert result["error_id"] == "999"
    assert result["status"] == "success"
    agent.tracer.trace_error_event.assert_called_once()


def test_get_tracing_summary_success(agent):
    """Test successful tracing summary retrieval."""
    agent.tracing_enabled = True
    agent.tracer = MagicMock()
    agent.tracer.get_tracing_summary.return_value = {"total_traces": 10, "status": "active"}
    
    result = agent.get_tracing_summary()
    
    assert result["total_traces"] == 10
    assert result["status"] == "active"
    agent.tracer.get_tracing_summary.assert_called_once()


def test_get_tracing_summary_fallback(agent):
    """Test tracing summary fallback when tracing is disabled."""
    agent.tracing_enabled = False
    
    result = agent.get_tracing_summary()
    
    assert result == {}


@pytest.mark.asyncio
async def test_build_shadcn_component_with_tracing(agent):
    """Test build_shadcn_component with tracing integration."""
    agent.tracing_enabled = True
    agent.tracer = MagicMock()
    agent.tracer.trace_component_development = AsyncMock(return_value={"trace_id": "123"})
    
    with patch.object(agent, 'use_enhanced_mcp_tools') as mock_enhanced:
        mock_enhanced.return_value = {"enhanced_mcp_result": "success"}
        
        result = await agent.build_shadcn_component("Button")
        
        assert "tracing_data" in result
        assert result["tracing_enabled"] is True
        agent.tracer.trace_component_development.assert_called_once() 