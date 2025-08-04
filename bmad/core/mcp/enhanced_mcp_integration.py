"""
Enhanced MCP Integration Module for Phase 2

This module provides enhanced MCP capabilities including:
- Advanced tool integration
- Inter-agent communication
- External tool adapters
- Security enhancement
- Performance optimization
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

from .mcp_client import MCPClient, MCPContext, MCPTool
from .framework_integration import FrameworkMCPIntegration

logger = logging.getLogger(__name__)

class EnhancedMCPIntegration:
    """
    Enhanced MCP Integration for Phase 2 capabilities.
    
    Provides advanced MCP features including:
    - Enhanced tool integration
    - Inter-agent communication
    - External tool adapters
    - Security enhancement
    - Performance optimization
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.mcp_client: Optional[MCPClient] = None
        self.framework_integration: Optional[FrameworkMCPIntegration] = None
        self.enhanced_enabled = False
        self.communication_cache = {}
        self.performance_metrics = {}
        
        logger.info(f"Enhanced MCP Integration initialized for {agent_name}")
    
    async def initialize_enhanced_mcp(self) -> bool:
        """Initialize enhanced MCP capabilities."""
        try:
            # Initialize base MCP client
            self.mcp_client = await self._get_enhanced_mcp_client()
            self.framework_integration = self._get_enhanced_framework_integration()
            
            # Initialize enhanced capabilities
            await self._initialize_enhanced_capabilities()
            
            self.enhanced_enabled = True
            logger.info(f"Enhanced MCP capabilities initialized for {self.agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Enhanced MCP initialization failed for {self.agent_name}: {e}")
            self.enhanced_enabled = False
            return False
    
    async def _get_enhanced_mcp_client(self) -> MCPClient:
        """Get enhanced MCP client with advanced capabilities."""
        # Enhanced client with additional features
        client = MCPClient()
        await client.initialize_enhanced()
        return client
    
    def _get_enhanced_framework_integration(self) -> FrameworkMCPIntegration:
        """Get enhanced framework integration."""
        return FrameworkMCPIntegration()
    
    async def _initialize_enhanced_capabilities(self):
        """Initialize enhanced MCP capabilities."""
        # Initialize communication capabilities
        await self._initialize_communication()
        
        # Initialize external tool adapters
        await self._initialize_external_tools()
        
        # Initialize security enhancement
        await self._initialize_security()
        
        # Initialize performance optimization
        await self._initialize_performance()
    
    async def _initialize_communication(self):
        """Initialize inter-agent communication capabilities."""
        try:
            communication_tool = MCPTool(
                name="agent_communication",
                description="Enhanced inter-agent communication",
                input_schema={
                    "type": "object",
                    "properties": {
                        "target_agent": {"type": "string"},
                        "message_type": {"type": "string"},
                        "message_content": {"type": "object"},
                        "communication_mode": {"type": "string"}
                    }
                },
                output_schema={"type": "object"},
                category="communication"
            )
            self.mcp_client.register_tool(communication_tool)
            logger.info("Inter-agent communication initialized")
        except Exception as e:
            logger.warning(f"Communication initialization failed: {e}")
    
    async def _initialize_external_tools(self):
        """Initialize external tool adapter capabilities."""
        try:
            discovery_tool = MCPTool(
                name="external_tool_discovery",
                description="Enhanced external tool discovery",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tool_category": {"type": "string"},
                        "integration_type": {"type": "string"},
                        "authentication": {"type": "object"}
                    }
                },
                output_schema={"type": "object"},
                category="external_tools"
            )
            self.mcp_client.register_tool(discovery_tool)
            
            execution_tool = MCPTool(
                name="external_tool_execution",
                description="Enhanced external tool execution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string"},
                        "parameters": {"type": "object"},
                        "execution_mode": {"type": "string"}
                    }
                },
                output_schema={"type": "object"},
                category="external_tools"
            )
            self.mcp_client.register_tool(execution_tool)
            logger.info("External tool adapters initialized")
        except Exception as e:
            logger.warning(f"External tools initialization failed: {e}")
    
    async def _initialize_security(self):
        """Initialize security enhancement capabilities."""
        try:
            auth_tool = MCPTool(
                name="advanced_authentication",
                description="Advanced authentication capabilities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "auth_method": {"type": "string"},
                        "security_level": {"type": "string"},
                        "compliance": {"type": "array"}
                    }
                },
                output_schema={"type": "object"},
                category="security"
            )
            self.mcp_client.register_tool(auth_tool)
            
            authz_tool = MCPTool(
                name="enhanced_authorization",
                description="Enhanced authorization capabilities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "authorization_model": {"type": "string"},
                        "permission_granularity": {"type": "string"},
                        "audit_trail": {"type": "boolean"}
                    }
                },
                output_schema={"type": "object"},
                category="security"
            )
            self.mcp_client.register_tool(authz_tool)
            
            threat_tool = MCPTool(
                name="threat_detection",
                description="Real-time threat detection",
                input_schema={
                    "type": "object",
                    "properties": {
                        "detection_type": {"type": "string"},
                        "threat_indicators": {"type": "array"},
                        "response_automation": {"type": "boolean"}
                    }
                },
                output_schema={"type": "object"},
                category="security"
            )
            self.mcp_client.register_tool(threat_tool)
            logger.info("Security enhancement initialized")
        except Exception as e:
            logger.warning(f"Security initialization failed: {e}")
    
    async def _initialize_performance(self):
        """Initialize performance optimization capabilities."""
        try:
            memory_tool = MCPTool(
                name="memory_optimization",
                description="Intelligent memory optimization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "optimization_type": {"type": "string"},
                        "cache_strategy": {"type": "string"},
                        "memory_usage": {"type": "object"}
                    }
                },
                output_schema={"type": "object"},
                category="performance"
            )
            self.mcp_client.register_tool(memory_tool)
            
            processing_tool = MCPTool(
                name="processing_optimization",
                description="Parallel processing optimization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "optimization_type": {"type": "string"},
                        "thread_management": {"type": "string"},
                        "resource_allocation": {"type": "string"}
                    }
                },
                output_schema={"type": "object"},
                category="performance"
            )
            self.mcp_client.register_tool(processing_tool)
            
            response_tool = MCPTool(
                name="response_time_optimization",
                description="Response time optimization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "target_latency": {"type": "number"},
                        "optimization_strategy": {"type": "string"},
                        "load_balancing": {"type": "boolean"}
                    }
                },
                output_schema={"type": "object"},
                category="performance"
            )
            self.mcp_client.register_tool(response_tool)
            logger.info("Performance optimization initialized")
        except Exception as e:
            logger.warning(f"Performance initialization failed: {e}")
    
    async def use_enhanced_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use enhanced MCP tool with advanced capabilities."""
        if not self.enhanced_enabled or not self.mcp_client:
            logger.warning("Enhanced MCP not available, falling back to local tools")
            return None
        
        try:
            # Create enhanced context
            context = await self.mcp_client.create_enhanced_context(
                agent_id=self.agent_name,
                tool_name=tool_name,
                parameters=parameters
            )
            
            # Execute enhanced tool call
            response = await self.mcp_client.call_enhanced_tool(tool_name, parameters, context)
            
            if response.success:
                # Record performance metrics
                self._record_performance_metric(tool_name, response.execution_time)
                logger.info(f"Enhanced MCP tool {tool_name} executed successfully")
                return response.data
            else:
                logger.error(f"Enhanced MCP tool {tool_name} failed: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"Enhanced MCP tool {tool_name} execution failed: {e}")
            return None
    
    async def communicate_with_agents(self, target_agents: List[str], message: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced inter-agent communication via MCP."""
        if not self.enhanced_enabled:
            logger.warning("Enhanced MCP not available for agent communication")
            return {}
        
        communication_results = {}
        
        for agent_name in target_agents:
            try:
                result = await self.use_enhanced_mcp_tool("agent_communication", {
                    "target_agent": agent_name,
                    "message_type": message.get("type", "collaboration"),
                    "message_content": message.get("content", {}),
                    "communication_mode": "enhanced",
                    "timestamp": datetime.now().isoformat(),
                    "source_agent": self.agent_name
                })
                
                if result:
                    communication_results[agent_name] = result
                    # Cache communication result
                    self.communication_cache[f"{self.agent_name}_{agent_name}"] = {
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"Communication with {agent_name} failed: {e}")
                communication_results[agent_name] = {"error": str(e)}
        
        return communication_results
    
    async def use_external_tools(self, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced external tool integration via MCP adapters."""
        if not self.enhanced_enabled:
            logger.warning("Enhanced MCP not available for external tools")
            return {}
        
        external_results = {}
        
        try:
            # External tool discovery
            discovery_result = await self.use_enhanced_mcp_tool("external_tool_discovery", {
                "tool_category": tool_config.get("category", "development"),
                "integration_type": "enhanced",
                "authentication": tool_config.get("auth", {}),
                "agent_context": self.agent_name
            })
            
            if discovery_result:
                external_results["tool_discovery"] = discovery_result
            
            # External tool execution
            execution_result = await self.use_enhanced_mcp_tool("external_tool_execution", {
                "tool_name": tool_config.get("tool_name", ""),
                "parameters": tool_config.get("parameters", {}),
                "execution_mode": "enhanced",
                "agent_context": self.agent_name
            })
            
            if execution_result:
                external_results["tool_execution"] = execution_result
                
        except Exception as e:
            logger.error(f"External tool usage failed: {e}")
            external_results["error"] = str(e)
        
        return external_results
    
    async def enhanced_security_validation(self, security_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced security validation and controls."""
        if not self.enhanced_enabled:
            logger.warning("Enhanced MCP not available for security validation")
            return {}
        
        security_results = {}
        
        try:
            # Advanced authentication
            auth_result = await self.use_enhanced_mcp_tool("advanced_authentication", {
                "auth_method": security_data.get("auth_method", "multi_factor"),
                "security_level": security_data.get("security_level", "enterprise"),
                "compliance": security_data.get("compliance", ["gdpr", "sox", "iso27001"]),
                "agent_context": self.agent_name
            })
            
            if auth_result:
                security_results["authentication"] = auth_result
            
            # Authorization enhancement
            authz_result = await self.use_enhanced_mcp_tool("enhanced_authorization", {
                "authorization_model": security_data.get("model", "rbac"),
                "permission_granularity": "fine_grained",
                "audit_trail": True,
                "agent_context": self.agent_name
            })
            
            if authz_result:
                security_results["authorization"] = authz_result
            
            # Threat detection
            threat_result = await self.use_enhanced_mcp_tool("threat_detection", {
                "detection_type": "real_time",
                "threat_indicators": security_data.get("indicators", []),
                "response_automation": True,
                "agent_context": self.agent_name
            })
            
            if threat_result:
                security_results["threat_detection"] = threat_result
                
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            security_results["error"] = str(e)
        
        return security_results
    
    async def enhanced_performance_optimization(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced performance optimization for agents."""
        if not self.enhanced_enabled:
            logger.warning("Enhanced MCP not available for performance optimization")
            return {}
        
        performance_results = {}
        
        try:
            # Memory optimization
            memory_result = await self.use_enhanced_mcp_tool("memory_optimization", {
                "optimization_type": "intelligent_caching",
                "cache_strategy": performance_data.get("cache_strategy", "adaptive"),
                "memory_usage": performance_data.get("memory_usage", {}),
                "agent_context": self.agent_name
            })
            
            if memory_result:
                performance_results["memory_optimization"] = memory_result
            
            # Processing optimization
            processing_result = await self.use_enhanced_mcp_tool("processing_optimization", {
                "optimization_type": "parallel_processing",
                "thread_management": "intelligent",
                "resource_allocation": "dynamic",
                "agent_context": self.agent_name
            })
            
            if processing_result:
                performance_results["processing_optimization"] = processing_result
            
            # Response time optimization
            response_result = await self.use_enhanced_mcp_tool("response_time_optimization", {
                "target_latency": performance_data.get("target_latency", 50),
                "optimization_strategy": "predictive_caching",
                "load_balancing": True,
                "agent_context": self.agent_name
            })
            
            if response_result:
                performance_results["response_time_optimization"] = response_result
                
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            performance_results["error"] = str(e)
        
        return performance_results
    
    def _record_performance_metric(self, tool_name: str, execution_time: float):
        """Record performance metrics for analysis."""
        if tool_name not in self.performance_metrics:
            self.performance_metrics[tool_name] = []
        
        self.performance_metrics[tool_name].append({
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 metrics per tool
        if len(self.performance_metrics[tool_name]) > 100:
            self.performance_metrics[tool_name] = self.performance_metrics[tool_name][-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for the agent."""
        summary = {}
        
        for tool_name, metrics in self.performance_metrics.items():
            if metrics:
                execution_times = [m["execution_time"] for m in metrics]
                summary[tool_name] = {
                    "average_time": sum(execution_times) / len(execution_times),
                    "min_time": min(execution_times),
                    "max_time": max(execution_times),
                    "total_calls": len(execution_times)
                }
        
        return summary
    
    def get_communication_summary(self) -> Dict[str, Any]:
        """Get communication summary for the agent."""
        summary = {
            "total_communications": len(self.communication_cache),
            "recent_communications": {},
            "communication_partners": list(set([
                key.split("_")[1] for key in self.communication_cache.keys()
            ]))
        }
        
        # Get recent communications (last 10)
        recent_keys = sorted(self.communication_cache.keys(), 
                           key=lambda k: self.communication_cache[k]["timestamp"])[-10:]
        
        for key in recent_keys:
            summary["recent_communications"][key] = self.communication_cache[key]
        
        return summary

# Factory function for creating enhanced MCP integration
def create_enhanced_mcp_integration(agent_name: str) -> EnhancedMCPIntegration:
    """Create enhanced MCP integration instance for an agent."""
    return EnhancedMCPIntegration(agent_name) 