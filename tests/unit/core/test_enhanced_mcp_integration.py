#!/usr/bin/env python3
"""
Unit tests for Enhanced MCP Integration Module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from bmad.core.mcp.enhanced_mcp_integration import EnhancedMCPIntegration, create_enhanced_mcp_integration
from bmad.core.mcp.mcp_client import MCPClient, MCPTool, MCPContext
from bmad.core.mcp.framework_integration import FrameworkMCPIntegration

class TestEnhancedMCPIntegration:
    """Test class for Enhanced MCP Integration."""
    
    def setup_method(self):
        """Setup method for each test."""
        self.agent_name = "TestAgent"
        self.enhanced_mcp = EnhancedMCPIntegration(self.agent_name)
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test enhanced MCP initialization."""
        with patch.object(self.enhanced_mcp, '_get_enhanced_mcp_client') as mock_get_client, \
             patch.object(self.enhanced_mcp, '_get_enhanced_framework_integration') as mock_get_framework, \
             patch.object(self.enhanced_mcp, '_initialize_enhanced_capabilities') as mock_init_capabilities:
            
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            mock_framework = Mock()
            mock_get_framework.return_value = mock_framework
            
            mock_init_capabilities.return_value = None
            
            result = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            assert result is True
            assert self.enhanced_mcp.enhanced_enabled is True
            assert self.enhanced_mcp.mcp_client == mock_client
            assert self.enhanced_mcp.framework_integration == mock_framework
    
    @pytest.mark.asyncio
    async def test_initialization_failure(self):
        """Test enhanced MCP initialization failure."""
        with patch.object(self.enhanced_mcp, '_get_enhanced_mcp_client', side_effect=Exception("Test error")):
            result = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            assert result is False
            assert self.enhanced_mcp.enhanced_enabled is False
    
    @pytest.mark.asyncio
    async def test_get_enhanced_mcp_client(self):
        """Test getting enhanced MCP client."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.MCPClient') as mock_mcp_client_class:
            mock_client = AsyncMock()
            mock_mcp_client_class.return_value = mock_client
            
            result = await self.enhanced_mcp._get_enhanced_mcp_client()
            
            assert result == mock_client
            mock_client.initialize_enhanced.assert_called_once()
    
    def test_get_enhanced_framework_integration(self):
        """Test getting enhanced framework integration."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.FrameworkMCPIntegration') as mock_framework_class:
            mock_framework = Mock()
            mock_framework_class.return_value = mock_framework
            
            result = self.enhanced_mcp._get_enhanced_framework_integration()
            
            assert result == mock_framework
            mock_framework_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_enhanced_capabilities(self):
        """Test initialization of enhanced capabilities."""
        with patch.object(self.enhanced_mcp, '_initialize_communication') as mock_comm, \
             patch.object(self.enhanced_mcp, '_initialize_external_tools') as mock_external, \
             patch.object(self.enhanced_mcp, '_initialize_security') as mock_security, \
             patch.object(self.enhanced_mcp, '_initialize_performance') as mock_performance:
            
            await self.enhanced_mcp._initialize_enhanced_capabilities()
            
            mock_comm.assert_called_once()
            mock_external.assert_called_once()
            mock_security.assert_called_once()
            mock_performance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_communication(self):
        """Test communication initialization."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.MCPTool') as mock_tool_class:
            mock_tool = Mock()
            mock_tool_class.return_value = mock_tool
            
            await self.enhanced_mcp._initialize_communication()
            
            mock_tool_class.assert_called_once()
            # Verify tool registration would happen here
    
    @pytest.mark.asyncio
    async def test_initialize_external_tools(self):
        """Test external tools initialization."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.MCPTool') as mock_tool_class:
            mock_tool = Mock()
            mock_tool_class.return_value = mock_tool
            
            await self.enhanced_mcp._initialize_external_tools()
            
            # Should create external tool adapters
            assert mock_tool_class.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_initialize_security(self):
        """Test security initialization."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.MCPTool') as mock_tool_class:
            mock_tool = Mock()
            mock_tool_class.return_value = mock_tool
            
            await self.enhanced_mcp._initialize_security()
            
            # Should create security enhancement tools
            assert mock_tool_class.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_initialize_performance(self):
        """Test performance initialization."""
        with patch('bmad.core.mcp.enhanced_mcp_integration.MCPTool') as mock_tool_class:
            mock_tool = Mock()
            mock_tool_class.return_value = mock_tool
            
            await self.enhanced_mcp._initialize_performance()
            
            # Should create performance optimization tools
            assert mock_tool_class.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tool_success(self):
        """Test successful enhanced MCP tool usage."""
        self.enhanced_mcp.enhanced_enabled = True
        self.enhanced_mcp.mcp_client = AsyncMock()
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = {"result": "success"}
        mock_response.execution_time = 1.0
        
        self.enhanced_mcp.mcp_client.create_enhanced_context.return_value = Mock()
        self.enhanced_mcp.mcp_client.call_enhanced_tool.return_value = mock_response
        
        result = await self.enhanced_mcp.use_enhanced_mcp_tool("test_tool", {"param": "value"})
        
        assert result == {"result": "success"}
        self.enhanced_mcp.mcp_client.call_enhanced_tool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tool_not_enabled(self):
        """Test enhanced MCP tool usage when not enabled."""
        self.enhanced_mcp.enhanced_enabled = False
        
        result = await self.enhanced_mcp.use_enhanced_mcp_tool("test_tool", {"param": "value"})
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_use_enhanced_mcp_tool_failure(self):
        """Test enhanced MCP tool usage failure."""
        self.enhanced_mcp.enhanced_enabled = True
        self.enhanced_mcp.framework_integration = Mock()
        
        mock_response = Mock()
        mock_response.success = False
        mock_response.error = "Tool not found"
        
        self.enhanced_mcp.framework_integration.call_framework_tool.return_value = mock_response
        
        result = await self.enhanced_mcp.use_enhanced_mcp_tool("test_tool", {"param": "value"})
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_communicate_with_agents(self):
        """Test inter-agent communication."""
        self.enhanced_mcp.enhanced_enabled = True
        self.enhanced_mcp.mcp_client = AsyncMock()
        
        # Mock the use_enhanced_mcp_tool method
        with patch.object(self.enhanced_mcp, 'use_enhanced_mcp_tool') as mock_use_tool:
            mock_use_tool.return_value = {"status": "sent", "agent": "Agent1"}
            
            target_agents = ["Agent1", "Agent2"]
            message = {"type": "info", "content": "test message"}
            
            result = await self.enhanced_mcp.communicate_with_agents(target_agents, message)
            
            assert "Agent1" in result
            assert result["Agent1"]["status"] == "sent"
            assert mock_use_tool.call_count == 2  # Called for each agent
    
    @pytest.mark.asyncio
    async def test_use_external_tools(self):
        """Test external tools usage."""
        self.enhanced_mcp.enhanced_enabled = True
        
        # Mock the use_enhanced_mcp_tool method
        with patch.object(self.enhanced_mcp, 'use_enhanced_mcp_tool') as mock_use_tool:
            mock_use_tool.side_effect = [
                {"discovered_tools": ["external_api"]},  # discovery result
                {"status": "executed", "tool_name": "external_api"}  # execution result
            ]
            
            tool_config = {
                "tool_name": "external_api",
                "endpoint": "https://api.example.com",
                "method": "POST"
            }
            
            result = await self.enhanced_mcp.use_external_tools(tool_config)
            
            assert "tool_discovery" in result
            assert "tool_execution" in result
            assert mock_use_tool.call_count == 2
    
    @pytest.mark.asyncio
    async def test_enhanced_security_validation(self):
        """Test enhanced security validation."""
        self.enhanced_mcp.enhanced_enabled = True
        
        # Mock the use_enhanced_mcp_tool method
        with patch.object(self.enhanced_mcp, 'use_enhanced_mcp_tool') as mock_use_tool:
            mock_use_tool.return_value = {
                "validation_result": "passed",
                "security_level": "enhanced",
                "permissions_validated": ["read", "write"]
            }
            
            security_data = {
                "permissions": ["read", "write"],
                "user_id": "test_user",
                "resource": "test_resource"
            }
            
            result = await self.enhanced_mcp.enhanced_security_validation(security_data)
            
            assert "authentication" in result
            assert "authorization" in result
            assert "threat_detection" in result
            assert result["authentication"]["security_level"] == "enhanced"
    
    @pytest.mark.asyncio
    async def test_enhanced_performance_optimization(self):
        """Test enhanced performance optimization."""
        self.enhanced_mcp.enhanced_enabled = True
        
        # Mock the use_enhanced_mcp_tool method
        with patch.object(self.enhanced_mcp, 'use_enhanced_mcp_tool') as mock_use_tool:
            mock_use_tool.return_value = {
                "optimization_result": "improved",
                "performance_improved": True,
                "recommendations": ["Reduce memory usage", "Optimize CPU usage"]
            }
            
            performance_data = {
                "execution_time": 1.5,
                "memory_usage": 512,
                "cpu_usage": 75.0
            }
            
            result = await self.enhanced_mcp.enhanced_performance_optimization(performance_data)
            
            assert "memory_optimization" in result
            assert "processing_optimization" in result
            assert "response_time_optimization" in result
            assert result["memory_optimization"]["performance_improved"] is True
    
    def test_record_performance_metric(self):
        """Test recording performance metrics."""
        tool_name = "test_tool"
        execution_time = 1.25
        
        self.enhanced_mcp._record_performance_metric(tool_name, execution_time)
        
        assert tool_name in self.enhanced_mcp.performance_metrics
        assert len(self.enhanced_mcp.performance_metrics[tool_name]) == 1
        assert self.enhanced_mcp.performance_metrics[tool_name][0]["execution_time"] == execution_time
    
    def test_get_performance_summary(self):
        """Test getting performance summary."""
        # Add some test metrics
        self.enhanced_mcp.performance_metrics = {
            "tool1": [{"execution_time": 1.0, "timestamp": "2023-01-01T00:00:00"}],
            "tool2": [{"execution_time": 2.0, "timestamp": "2023-01-01T00:00:00"}]
        }
        
        summary = self.enhanced_mcp.get_performance_summary()
        
        assert "tool1" in summary
        assert "tool2" in summary
        assert summary["tool1"]["average_time"] == 1.0
        assert summary["tool2"]["average_time"] == 2.0
    
    def test_get_communication_summary(self):
        """Test getting communication summary."""
        # Add some test communication data
        self.enhanced_mcp.communication_cache = {
            "Agent1_Agent2": {"result": "success", "timestamp": "2023-01-01T00:00:00"},
            "Agent1_Agent3": {"result": "success", "timestamp": "2023-01-01T00:01:00"}
        }
        
        summary = self.enhanced_mcp.get_communication_summary()
        
        assert "total_communications" in summary
        assert "communication_partners" in summary
        assert summary["total_communications"] == 2
        assert "Agent2" in summary["communication_partners"]
        assert "Agent3" in summary["communication_partners"]

class TestCreateEnhancedMCPIntegration:
    """Test factory function for creating enhanced MCP integration."""
    
    def test_create_enhanced_mcp_integration(self):
        """Test creating enhanced MCP integration instance."""
        agent_name = "TestAgent"
        
        result = create_enhanced_mcp_integration(agent_name)
        
        assert isinstance(result, EnhancedMCPIntegration)
        assert result.agent_name == agent_name
        assert result.enhanced_enabled is False

class TestEnhancedMCPIntegrationWorkflow:
    """Test complete workflow of enhanced MCP integration."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete enhanced MCP workflow."""
        enhanced_mcp = EnhancedMCPIntegration("WorkflowAgent")
        
        # Mock all dependencies
        with patch.object(enhanced_mcp, '_get_enhanced_mcp_client') as mock_get_client, \
             patch.object(enhanced_mcp, '_get_enhanced_framework_integration') as mock_get_framework, \
             patch.object(enhanced_mcp, '_initialize_enhanced_capabilities') as mock_init_capabilities:
            
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            
            mock_framework = Mock()
            mock_get_framework.return_value = mock_framework
            
            # Initialize
            result = await enhanced_mcp.initialize_enhanced_mcp()
            assert result is True
            
            # Test tool usage
            with patch.object(enhanced_mcp, 'use_enhanced_mcp_tool') as mock_use_tool:
                mock_use_tool.return_value = {"result": "success"}
                tool_result = await enhanced_mcp.use_enhanced_mcp_tool("test_tool", {})
                assert tool_result == {"result": "success"}
            
            # Test communication
            with patch.object(enhanced_mcp, 'use_enhanced_mcp_tool') as mock_use_tool:
                mock_use_tool.return_value = {"status": "sent", "agent": "Agent1"}
                comm_result = await enhanced_mcp.communicate_with_agents(["Agent1"], {"message": "test"})
                assert "Agent1" in comm_result
            
            # Test performance summary
            summary = enhanced_mcp.get_performance_summary()
            assert isinstance(summary, dict) 