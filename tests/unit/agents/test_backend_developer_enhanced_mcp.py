"""
Test Enhanced MCP Integration for BackendDeveloper Agent

This module tests the enhanced MCP capabilities added in Phase 2.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

# Mock the framework templates manager before importing the agent
with patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.get_framework_templates_manager') as mock_manager:
    mock_manager.return_value = MagicMock()
    mock_manager.return_value.get_template.return_value = MagicMock()
    
    from bmad.agents.Agent.BackendDeveloper.backenddeveloper import BackendDeveloperAgent


class TestBackendDeveloperEnhancedMCP:
    """Test enhanced MCP integration for BackendDeveloper agent."""
    
    @pytest.fixture
    def agent(self):
        """Create BackendDeveloper agent instance."""
        with patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.get_framework_templates_manager') as mock_manager, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.get_performance_monitor') as mock_monitor, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.get_advanced_policy_engine') as mock_policy, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.get_sprite_library') as mock_sprite, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.BMADTracer') as mock_tracer, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.PrefectWorkflowOrchestrator') as mock_workflow:
            
            # Mock all dependencies
            mock_manager.return_value = MagicMock()
            mock_manager.return_value.get_template.return_value = MagicMock()
            mock_monitor.return_value = MagicMock()
            mock_policy.return_value = MagicMock()
            mock_sprite.return_value = MagicMock()
            mock_tracer.return_value = MagicMock()
            mock_workflow.return_value = MagicMock()
            
            return BackendDeveloperAgent()
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization(self, agent):
        """Test enhanced MCP initialization."""
        with patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = AsyncMock()
            mock_enhanced_mcp.initialize_enhanced_mcp.return_value = True
            mock_create.return_value = mock_enhanced_mcp
            
            await agent.initialize_enhanced_mcp()
            
            assert agent.enhanced_mcp is not None
            assert agent.enhanced_mcp_enabled is True
            mock_create.assert_called_once_with(agent.agent_name)
            mock_enhanced_mcp.initialize_enhanced_mcp.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization_failure(self, agent):
        """Test enhanced MCP initialization failure."""
        with patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.create_enhanced_mcp_integration') as mock_create:
            mock_enhanced_mcp = AsyncMock()
            mock_enhanced_mcp.initialize_enhanced_mcp.return_value = False
            mock_create.return_value = mock_enhanced_mcp
            
            await agent.initialize_enhanced_mcp()
            
            assert agent.enhanced_mcp is not None
            assert agent.enhanced_mcp_enabled is False
    
    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tools(self, agent):
        """Test enhanced MCP tools usage."""
        # Mock enhanced MCP
        agent.enhanced_mcp = AsyncMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock enhanced tool calls
        agent.enhanced_mcp.use_enhanced_mcp_tool.return_value = {"result": "success"}
        
        agent_data = {
            "capabilities": ["api_development", "database_design"],
            "performance_metrics": {"response_time": 50}
        }
        
        result = await agent.use_enhanced_mcp_tools(agent_data)
        
        assert result is not None
        assert "core_enhancement" in result
        agent.enhanced_mcp.use_enhanced_mcp_tool.assert_called()
    
    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tools_fallback(self, agent):
        """Test enhanced MCP tools fallback to standard MCP."""
        agent.enhanced_mcp_enabled = False
        
        with patch.object(agent, 'use_backend_specific_mcp_tools') as mock_standard:
            mock_standard.return_value = {"standard_result": "success"}
            
            agent_data = {"capabilities": ["api_development"]}
            result = await agent.use_enhanced_mcp_tools(agent_data)
            
            assert result == {"standard_result": "success"}
            mock_standard.assert_called_once_with(agent_data)
    
    @pytest.mark.asyncio
    async def test_use_backend_specific_enhanced_tools(self, agent):
        """Test backend-specific enhanced MCP tools."""
        # Mock enhanced MCP
        agent.enhanced_mcp = AsyncMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock enhanced tool calls
        agent.enhanced_mcp.use_enhanced_mcp_tool.return_value = {"enhanced_result": "success"}
        
        backend_data = {
            "endpoint": "/api/v1/users",
            "method": "GET",
            "framework": "fastapi",
            "database_type": "postgresql",
            "security_level": "enterprise",
            "performance_metrics": {"latency": 50}
        }
        
        result = await agent.use_backend_specific_enhanced_tools(backend_data)
        
        assert result is not None
        assert "enhanced_api_development" in result
        assert "enhanced_database_design" in result
        assert "enhanced_security_implementation" in result
        assert "enhanced_performance_optimization" in result
        
        # Verify tool calls
        assert agent.enhanced_mcp.use_enhanced_mcp_tool.call_count == 4
    
    @pytest.mark.asyncio
    async def test_communicate_with_agents(self, agent):
        """Test enhanced inter-agent communication."""
        # Mock enhanced MCP
        agent.enhanced_mcp = AsyncMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock communication result
        agent.enhanced_mcp.communicate_with_agents.return_value = {
            "FrontendDeveloper": {"status": "received"},
            "TestEngineer": {"status": "received"}
        }
        
        target_agents = ["FrontendDeveloper", "TestEngineer"]
        message = {
            "type": "collaboration",
            "content": {"message": "API ready for testing"}
        }
        
        result = await agent.communicate_with_agents(target_agents, message)
        
        assert result is not None
        assert "FrontendDeveloper" in result
        assert "TestEngineer" in result
        agent.enhanced_mcp.communicate_with_agents.assert_called_once_with(target_agents, message)
    
    @pytest.mark.asyncio
    async def test_communicate_with_agents_disabled(self, agent):
        """Test inter-agent communication when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        target_agents = ["FrontendDeveloper"]
        message = {"type": "collaboration", "content": {"message": "test"}}
        
        result = await agent.communicate_with_agents(target_agents, message)
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_use_external_tools(self, agent):
        """Test enhanced external tool integration."""
        # Mock enhanced MCP
        agent.enhanced_mcp = AsyncMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock external tool result
        agent.enhanced_mcp.use_external_tools.return_value = {
            "tool_discovery": {"tools": ["github", "gitlab"]},
            "tool_execution": {"status": "success"}
        }
        
        tool_config = {
            "tool_name": "github",
            "category": "development",
            "auth": {"token": "test_token"}
        }
        
        result = await agent.use_external_tools(tool_config)
        
        assert result is not None
        assert "tool_discovery" in result
        assert "tool_execution" in result
        agent.enhanced_mcp.use_external_tools.assert_called_once_with(tool_config)
    
    @pytest.mark.asyncio
    async def test_enhanced_security_validation(self, agent):
        """Test enhanced security validation."""
        # Mock enhanced MCP
        agent.enhanced_mcp = AsyncMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock security validation result
        agent.enhanced_mcp.enhanced_security_validation.return_value = {
            "authentication": {"status": "validated"},
            "authorization": {"status": "authorized"},
            "threat_detection": {"status": "clear"}
        }
        
        security_data = {
            "auth_method": "multi_factor",
            "security_level": "enterprise",
            "compliance": ["gdpr", "sox"],
            "model": "rbac",
            "indicators": ["suspicious_activity"]
        }
        
        result = await agent.enhanced_security_validation(security_data)
        
        assert result is not None
        assert "authentication" in result
        assert "authorization" in result
        assert "threat_detection" in result
        agent.enhanced_mcp.enhanced_security_validation.assert_called_once_with(security_data)
    
    @pytest.mark.asyncio
    async def test_enhanced_performance_optimization(self, agent):
        """Test enhanced performance optimization."""
        # Mock enhanced MCP
        agent.enhanced_mcp = AsyncMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock performance optimization result
        agent.enhanced_mcp.enhanced_performance_optimization.return_value = {
            "memory_optimization": {"status": "optimized"},
            "processing_optimization": {"status": "optimized"},
            "response_time_optimization": {"status": "optimized"}
        }
        
        performance_data = {
            "cache_strategy": "adaptive",
            "memory_usage": {"current": 50, "peak": 80},
            "target_latency": 50
        }
        
        result = await agent.enhanced_performance_optimization(performance_data)
        
        assert result is not None
        assert "memory_optimization" in result
        assert "processing_optimization" in result
        assert "response_time_optimization" in result
        agent.enhanced_mcp.enhanced_performance_optimization.assert_called_once_with(performance_data)
    
    def test_get_enhanced_performance_summary(self, agent):
        """Test enhanced performance summary retrieval."""
        # Mock enhanced MCP
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock performance summary
        agent.enhanced_mcp.get_performance_summary.return_value = {
            "core_enhancement": {
                "average_time": 25.5,
                "min_time": 20.0,
                "max_time": 30.0,
                "total_calls": 10
            }
        }
        
        result = agent.get_enhanced_performance_summary()
        
        assert result is not None
        assert "core_enhancement" in result
        agent.enhanced_mcp.get_performance_summary.assert_called_once()
    
    def test_get_enhanced_performance_summary_disabled(self, agent):
        """Test performance summary when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        result = agent.get_enhanced_performance_summary()
        
        assert result == {}
    
    def test_get_enhanced_communication_summary(self, agent):
        """Test enhanced communication summary retrieval."""
        # Mock enhanced MCP
        agent.enhanced_mcp = MagicMock()
        agent.enhanced_mcp_enabled = True
        
        # Mock communication summary
        agent.enhanced_mcp.get_communication_summary.return_value = {
            "total_communications": 5,
            "communication_partners": ["FrontendDeveloper", "TestEngineer"],
            "recent_communications": {
                "BackendDeveloper_FrontendDeveloper": {
                    "result": {"status": "success"},
                    "timestamp": "2025-08-01T10:00:00"
                }
            }
        }
        
        result = agent.get_enhanced_communication_summary()
        
        assert result is not None
        assert "total_communications" in result
        assert "communication_partners" in result
        assert "recent_communications" in result
        agent.enhanced_mcp.get_communication_summary.assert_called_once()
    
    def test_get_enhanced_communication_summary_disabled(self, agent):
        """Test communication summary when enhanced MCP is disabled."""
        agent.enhanced_mcp_enabled = False
        
        result = agent.get_enhanced_communication_summary()
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_run_with_enhanced_mcp(self, agent):
        """Test agent run with enhanced MCP initialization."""
        with patch.object(agent, 'initialize_mcp') as mock_init_mcp, \
             patch.object(agent, 'initialize_enhanced_mcp') as mock_init_enhanced, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.subscribe') as mock_subscribe:
            
            mock_init_mcp.return_value = None
            mock_init_enhanced.return_value = None
            mock_subscribe.return_value = None
            
            # Mock the event loop to avoid infinite loop
            with patch('asyncio.sleep') as mock_sleep:
                mock_sleep.side_effect = KeyboardInterrupt()
                
                try:
                    await agent.run()
                except KeyboardInterrupt:
                    pass
            
            mock_init_mcp.assert_called_once()
            mock_init_enhanced.assert_called_once()
            assert mock_subscribe.call_count == 4  # 4 event subscriptions 

    @pytest.mark.asyncio
    async def test_run_with_enhanced_mcp_initialization(self, agent):
        """Test run method with enhanced MCP initialization."""
        with patch.object(agent, 'initialize_mcp') as mock_init_mcp, \
             patch.object(agent, 'initialize_enhanced_mcp') as mock_init_enhanced, \
             patch.object(agent, 'initialize_tracing') as mock_init_tracing, \
             patch('bmad.agents.Agent.BackendDeveloper.backenddeveloper.subscribe') as mock_subscribe:
            
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
        agent.tracer = MagicMock()
        agent.tracer.initialize = AsyncMock(return_value=True)
        agent.tracer.setup_backend_tracing = AsyncMock()
        
        await agent.initialize_tracing()
        
        assert agent.tracing_enabled is True
        agent.tracer.initialize.assert_called_once()
        agent.tracer.setup_backend_tracing.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_tracing_failure(self, agent):
        """Test tracing initialization failure."""
        agent.tracer = MagicMock()
        agent.tracer.initialize = AsyncMock(return_value=False)
        
        await agent.initialize_tracing()
        
        assert agent.tracing_enabled is False

    @pytest.mark.asyncio
    async def test_trace_api_development_success(self, agent):
        """Test successful API development tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_api_development = AsyncMock(return_value={"trace_id": "123", "status": "success"})
        
        result = await agent.trace_api_development({
            "endpoint": "/api/v1/users",
            "method": "GET",
            "framework": "fastapi"
        })
        
        assert result["trace_id"] == "123"
        assert result["status"] == "success"
        agent.tracer.trace_api_development.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_database_operation_success(self, agent):
        """Test successful database operation tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_database_operation = AsyncMock(return_value={"db_trace_id": "456", "status": "success"})
        
        result = await agent.trace_database_operation({
            "type": "query",
            "table": "users",
            "complexity": "simple"
        })
        
        assert result["db_trace_id"] == "456"
        assert result["status"] == "success"
        agent.tracer.trace_database_operation.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_api_deployment_success(self, agent):
        """Test successful API deployment tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_api_deployment = AsyncMock(return_value={"deployment_trace_id": "789", "status": "success"})
        
        result = await agent.trace_api_deployment({
            "endpoint": "/api/v1/users",
            "environment": "production",
            "type": "manual"
        })
        
        assert result["deployment_trace_id"] == "789"
        assert result["status"] == "success"
        agent.tracer.trace_api_deployment.assert_called_once()

    @pytest.mark.asyncio
    async def test_trace_backend_error_success(self, agent):
        """Test successful backend error tracing."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_backend_error = AsyncMock(return_value={"error_trace_id": "999", "status": "success"})
        
        result = await agent.trace_backend_error({
            "type": "validation_error",
            "message": "Invalid input",
            "endpoint": "/api/v1/users"
        })
        
        assert result["error_trace_id"] == "999"
        assert result["status"] == "success"
        agent.tracer.trace_backend_error.assert_called_once()

    def test_get_tracing_summary_success(self, agent):
        """Test successful tracing summary retrieval."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.get_tracing_summary.return_value = {"total_traces": 15, "status": "active"}
        
        result = agent.get_tracing_summary()
        
        assert result["total_traces"] == 15
        assert result["status"] == "active"
        agent.tracer.get_tracing_summary.assert_called_once()

    def test_get_tracing_summary_fallback(self, agent):
        """Test tracing summary fallback when tracing is disabled."""
        agent.tracing_enabled = False
        
        result = agent.get_tracing_summary()
        
        assert result == {}

    @pytest.mark.asyncio
    async def test_build_api_with_tracing(self, agent):
        """Test build_api with tracing integration."""
        agent.tracing_enabled = True
        agent.tracer = MagicMock()
        agent.tracer.trace_api_development = AsyncMock(return_value={"trace_id": "123"})
        
        with patch.object(agent, 'use_enhanced_mcp_tools') as mock_enhanced:
            mock_enhanced.return_value = {"enhanced_mcp_result": "success"}
            
            result = await agent.build_api("/api/v1/users")
            
            assert "tracing_data" in result
            assert result["tracing_enabled"] is True
            agent.tracer.trace_api_development.assert_called_once() 