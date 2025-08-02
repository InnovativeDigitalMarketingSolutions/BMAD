#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Package for BMAD
Following official MCP specification: https://modelcontextprotocol.io/docs
"""

# Core MCP Classes
from .mcp_client import (
    MCPClient,
    MCPTool,
    MCPContext,
    MCPRequest,
    MCPResponse,
    MCPServerInfo,
    MCPVersion,
    MCPMessageType,
    get_mcp_client,
    initialize_mcp_client
)

# Tool Registry
from .tool_registry import (
    MCPToolRegistry,
    ToolMetadata,
    ToolCategory,
    get_mcp_tool_registry,
    execute_tool
)

# Framework Integration
from .framework_integration import (
    FrameworkMCPIntegration,
    FrameworkTool,
    FrameworkType,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)

# Version information
__version__ = "1.1.0"
__author__ = "BMAD Development Team"
__description__ = "MCP (Model Context Protocol) implementation for BMAD system"

# Export all public classes and functions
__all__ = [
    # Core MCP Classes
    "MCPClient",
    "MCPTool", 
    "MCPContext",
    "MCPRequest",
    "MCPResponse",
    "MCPServerInfo",
    "MCPVersion",
    "MCPMessageType",
    "get_mcp_client",
    "initialize_mcp_client",
    
    # Tool Registry
    "MCPToolRegistry",
    "ToolMetadata",
    "ToolCategory",
    "get_mcp_tool_registry",
    "execute_tool",
    
    # Framework Integration
    "FrameworkMCPIntegration",
    "FrameworkTool",
    "FrameworkType",
    "get_framework_mcp_integration",
    "initialize_framework_mcp_integration"
] 