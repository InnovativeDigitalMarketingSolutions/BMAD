#!/usr/bin/env python3
"""
MCP Agent Mixin - Standardized MCP Integration for BMAD Agents
Following official MCP specification: https://modelcontextprotocol.io/docs
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

from .mcp_client import MCPClient, MCPContext, MCPResponse
from .framework_integration import FrameworkMCPIntegration, get_framework_mcp_integration
from .dependency_manager import DependencyManager

logger = logging.getLogger(__name__)

@dataclass
class MCPAgentConfig:
    """Configuration for MCP agent integration."""
    agent_name: str
    agent_type: str
    mcp_enabled: bool = True
    auto_initialize: bool = True
    tool_categories: List[str] = None
    custom_tools: List[str] = None
    error_handling: str = "graceful"  # graceful, strict, silent
    
    def __post_init__(self):
        if self.tool_categories is None:
            self.tool_categories = ["development", "testing", "quality"]
        if self.custom_tools is None:
            self.custom_tools = []

class MCPAgentMixin:
    """
    Mixin voor gestandaardiseerde MCP integratie in BMAD agents.
    
    Deze mixin biedt:
    - Gestandaardiseerde MCP initialisatie
    - Dependency isolation en lazy loading
    - Consistent error handling
    - Tool usage patterns
    - Performance monitoring
    """
    
    def __init__(self, mcp_config: Optional[MCPAgentConfig] = None):
        """Initialize MCP agent mixin."""
        # MCP components
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled: bool = False
        self.mcp_config: MCPAgentConfig = mcp_config or MCPAgentConfig(
            agent_name=getattr(self, 'agent_name', 'UnknownAgent'),
            agent_type=getattr(self, '__class__.__name__', 'UnknownType')
        )
        
        # Dependency management
        self.dependency_manager = DependencyManager()
        
        # Check and log dependency status
        self._check_dependencies()
        
        # Performance tracking
        self.mcp_performance_metrics = {
            "initialization_time": 0,
            "tool_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "last_execution": None
        }
        
        # Auto-initialize if configured
        if self.mcp_config.auto_initialize and self.mcp_config.mcp_enabled:
            asyncio.create_task(self.initialize_mcp())
    
    def _check_dependencies(self):
        """Check and log dependency status for the agent."""
        warnings = self.dependency_manager.get_dependency_warnings()
        for warning in warnings:
            logger.warning(f"{self.mcp_config.agent_name}: {warning}")
        
        if warnings:
            logger.info(f"{self.mcp_config.agent_name}: {len(warnings)} dependencies missing, some features may be degraded")
    
    def get_dependency_status(self) -> Dict[str, Any]:
        """
        Get detailed dependency status for the agent.
        
        Returns:
            Dict: Dependency status information
        """
        return {
            "agent_name": self.mcp_config.agent_name,
            "missing_dependencies": self.dependency_manager.get_missing_dependencies(),
            "degraded_features": self.dependency_manager.get_degraded_features(),
            "dependency_warnings": self.dependency_manager.get_dependency_warnings(),
            "recommendations": self.dependency_manager.get_dependency_recommendations(),
            "dependency_health": len(self.dependency_manager.get_missing_dependencies()) == 0,
            "health_report": self.dependency_manager.get_dependency_health_report()
        }
    
    async def initialize_mcp(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Gestandaardiseerde MCP initialisatie voor agents.
        
        Args:
            config: Optional configuration overrides
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        start_time = datetime.utcnow()
        
        try:
            # Update config if provided
            if config:
                for key, value in config.items():
                    if hasattr(self.mcp_config, key):
                        setattr(self.mcp_config, key, value)
            
            # Check if MCP is enabled
            if not self.mcp_config.mcp_enabled:
                logger.info(f"MCP disabled for agent: {self.mcp_config.agent_name}")
                return False
            
            # Initialize MCP client
            from .mcp_client import get_mcp_client
            self.mcp_client = get_mcp_client()
            
            # Connect to MCP server
            connected = await self.mcp_client.connect()
            if not connected:
                logger.error(f"Failed to connect MCP client for agent: {self.mcp_config.agent_name}")
                return False
            
            # Initialize framework integration
            self.mcp_integration = get_framework_mcp_integration()
            integration_success = await self.mcp_integration.initialize(self.mcp_client)
            
            if not integration_success:
                logger.error(f"Failed to initialize MCP integration for agent: {self.mcp_config.agent_name}")
                return False
            
            # Enable MCP
            self.mcp_enabled = True
            
            # Track performance
            self.mcp_performance_metrics["initialization_time"] = (
                datetime.utcnow() - start_time
            ).total_seconds()
            
            logger.info(f"MCP initialized successfully for agent: {self.mcp_config.agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing MCP for agent {self.mcp_config.agent_name}: {e}")
            
            # Handle based on error handling strategy
            if self.mcp_config.error_handling == "strict":
                raise
            elif self.mcp_config.error_handling == "silent":
                pass
            else:  # graceful
                self.mcp_enabled = False
            
            return False
    
    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gestandaardiseerde MCP tool usage voor agents.
        
        Args:
            tool_name: Name of the MCP tool to use
            parameters: Tool parameters
            
        Returns:
            Optional[Dict]: Tool execution result or None if failed
        """
        if not self.mcp_enabled or not self.mcp_integration:
            logger.warning(f"MCP not available for agent: {self.mcp_config.agent_name}")
            return None
        
        start_time = datetime.utcnow()
        self.mcp_performance_metrics["tool_executions"] += 1
        
        try:
            # Create context
            context = await self.mcp_client.create_context(
                user_id=f"{self.mcp_config.agent_name.lower()}_user",
                agent_id=self.mcp_config.agent_name,
                project_id=f"{self.mcp_config.agent_type.lower()}_project",
                metadata={
                    "tool_name": tool_name,
                    "agent_type": self.mcp_config.agent_type,
                    "execution_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Execute tool
            response = await self.mcp_integration.call_framework_tool(tool_name, parameters, context)
            
            # Track performance
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.mcp_performance_metrics["last_execution"] = datetime.utcnow()
            
            if response.success:
                self.mcp_performance_metrics["successful_executions"] += 1
                logger.debug(f"MCP tool {tool_name} executed successfully in {execution_time:.3f}s")
                return response.data
            else:
                self.mcp_performance_metrics["failed_executions"] += 1
                logger.error(f"MCP tool {tool_name} failed: {response.error}")
                
                # Handle based on error handling strategy
                if self.mcp_config.error_handling == "strict":
                    raise Exception(f"MCP tool {tool_name} failed: {response.error}")
                
                return None
                
        except Exception as e:
            self.mcp_performance_metrics["failed_executions"] += 1
            logger.error(f"Error using MCP tool {tool_name} for agent {self.mcp_config.agent_name}: {e}")
            
            # Handle based on error handling strategy
            if self.mcp_config.error_handling == "strict":
                raise
            elif self.mcp_config.error_handling == "silent":
                pass
            
            return None
    
    async def use_multiple_mcp_tools(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple MCP tools in sequence.
        
        Args:
            tool_calls: List of tool call specifications
                [{"tool": "tool_name", "parameters": {...}}, ...]
                
        Returns:
            Dict: Results from all tool executions
        """
        results = {}
        
        for i, tool_call in enumerate(tool_calls):
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})
            
            if not tool_name:
                logger.warning(f"Missing tool name in tool call {i}")
                continue
            
            result = await self.use_mcp_tool(tool_name, parameters)
            results[tool_name] = result
        
        return results
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """
        Get comprehensive MCP status information.
        
        Returns:
            Dict: MCP status and performance metrics
        """
        return {
            "agent_name": self.mcp_config.agent_name,
            "agent_type": self.mcp_config.agent_type,
            "mcp_enabled": self.mcp_enabled,
            "mcp_client_connected": self.mcp_client.connected if self.mcp_client else False,
            "mcp_integration_available": self.mcp_integration is not None,
            "tool_categories": self.mcp_config.tool_categories,
            "custom_tools": self.mcp_config.custom_tools,
            "error_handling": self.mcp_config.error_handling,
            "performance_metrics": self.mcp_performance_metrics.copy(),
            "available_tools": self._get_available_tools(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_available_tools(self) -> List[str]:
        """Get list of available MCP tools for this agent."""
        if not self.mcp_integration:
            return []
        
        tools = []
        for tool in self.mcp_integration.get_framework_tools():
            if tool.framework_type.value in self.mcp_config.tool_categories:
                tools.append(tool.name)
        
        # Add custom tools
        tools.extend(self.mcp_config.custom_tools)
        
        return tools
    
    async def enhanced_operation(self, operation_name: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform enhanced operation using MCP tools.
        
        Args:
            operation_name: Name of the operation
            operation_data: Operation data
            
        Returns:
            Dict: Enhanced operation result with MCP insights
        """
        result = {
            "operation": operation_name,
            "agent": self.mcp_config.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": operation_data,
            "mcp_enhanced": False
        }
        
        if not self.mcp_enabled:
            return result
        
        try:
            # Determine which MCP tools to use based on operation
            tool_calls = self._determine_tool_calls(operation_name, operation_data)
            
            if tool_calls:
                mcp_results = await self.use_multiple_mcp_tools(tool_calls)
                result["mcp_enhanced"] = True
                result["mcp_insights"] = mcp_results
            
        except Exception as e:
            logger.error(f"Error in enhanced operation {operation_name}: {e}")
            if self.mcp_config.error_handling == "strict":
                raise
        
        return result
    
    def _determine_tool_calls(self, operation_name: str, operation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine which MCP tools to call based on operation and data.
        
        Args:
            operation_name: Name of the operation
            operation_data: Operation data
            
        Returns:
            List[Dict]: List of tool call specifications
        """
        tool_calls = []
        
        # Code-related operations
        if "code" in operation_name.lower() or "code" in operation_data:
            tool_calls.append({
                "tool": "code_analysis",
                "parameters": {
                    "code": operation_data.get("code", ""),
                    "language": operation_data.get("language", "python"),
                    "analysis_type": "quality"
                }
            })
            
            tool_calls.append({
                "tool": "test_generation",
                "parameters": {
                    "code": operation_data.get("code", ""),
                    "language": operation_data.get("language", "python"),
                    "framework": "pytest",
                    "test_type": "unit"
                }
            })
        
        # Quality-related operations
        if "quality" in operation_name.lower() or "quality" in operation_data:
            tool_calls.append({
                "tool": "quality_gate",
                "parameters": {
                    "metrics": operation_data.get("metrics", {}),
                    "thresholds": operation_data.get("thresholds", {})
                }
            })
        
        # Documentation-related operations
        if "documentation" in operation_name.lower() or "documentation" in operation_data:
            tool_calls.append({
                "tool": "documentation_generator",
                "parameters": {
                    "source": operation_data.get("source", ""),
                    "output_format": "markdown",
                    "include_examples": True
                }
            })
        
        return tool_calls
    
    async def cleanup_mcp(self) -> bool:
        """
        Cleanup MCP resources.
        
        Returns:
            bool: True if cleanup successful
        """
        try:
            if self.mcp_client:
                await self.mcp_client.disconnect()
            
            self.mcp_enabled = False
            logger.info(f"MCP cleanup completed for agent: {self.mcp_config.agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error during MCP cleanup for agent {self.mcp_config.agent_name}: {e}")
            return False

def create_mcp_agent_config(agent_name: str, agent_type: str, **kwargs) -> MCPAgentConfig:
    """
    Factory function to create MCP agent configuration.
    
    Args:
        agent_name: Name of the agent
        agent_type: Type of the agent
        **kwargs: Additional configuration options
        
    Returns:
        MCPAgentConfig: Configured agent configuration
    """
    return MCPAgentConfig(agent_name=agent_name, agent_type=agent_type, **kwargs) 