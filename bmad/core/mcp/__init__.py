#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Module for BMAD
"""

from .mcp_client import (
    MCPClient,
    MCPTool,
    MCPContext,
    MCPRequest,
    MCPResponse,
    get_mcp_client,
    initialize_mcp_client
)

from .tool_registry import (
    MCPToolRegistry,
    ToolMetadata,
    get_tool_registry,
    register_tool,
    get_tool,
    get_tools_by_category,
    execute_tool
)

from .framework_integration import (
    FrameworkMCPIntegration,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration,
    call_framework_tool
)

__all__ = [
    # MCP Client
    "MCPClient",
    "MCPTool", 
    "MCPContext",
    "MCPRequest",
    "MCPResponse",
    "get_mcp_client",
    "initialize_mcp_client",
    
    # Tool Registry
    "MCPToolRegistry",
    "ToolMetadata",
    "get_tool_registry",
    "register_tool",
    "get_tool",
    "get_tools_by_category",
    "execute_tool",
    
    # Framework Integration
    "FrameworkMCPIntegration",
    "get_framework_mcp_integration",
    "initialize_framework_mcp_integration",
    "call_framework_tool"
]

__version__ = "1.0.0"
__author__ = "BMAD System"
__description__ = "MCP (Model Context Protocol) integration for BMAD framework templates" 