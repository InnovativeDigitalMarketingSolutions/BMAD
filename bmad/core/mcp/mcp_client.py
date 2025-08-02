#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Client Implementation for BMAD
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    category: str
    version: str = "1.0.0"

@dataclass
class MCPContext:
    """MCP Context definition."""
    session_id: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class MCPRequest:
    """MCP Request definition."""
    tool_name: str
    parameters: Dict[str, Any]
    context: MCPContext
    request_id: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class MCPResponse:
    """MCP Response definition."""
    request_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class MCPClient:
    """MCP Client for BMAD system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: Dict[str, MCPTool] = {}
        self.contexts: Dict[str, MCPContext] = {}
        self.requests: Dict[str, MCPRequest] = {}
        self.responses: Dict[str, MCPResponse] = {}
        self.connected = False
        self.session_id = self._generate_session_id()
        
        # Initialize default tools
        self._initialize_default_tools()
        
        logger.info(f"MCP Client initialized with session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"bmad_mcp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
    
    def _initialize_default_tools(self):
        """Initialize default MCP tools."""
        default_tools = [
            MCPTool(
                name="file_system",
                description="File system operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["read", "write", "delete", "list"]},
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["operation", "path"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "data": {"type": "object"},
                        "error": {"type": "string"}
                    }
                },
                category="system"
            ),
            MCPTool(
                name="database",
                description="Database operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["query", "insert", "update", "delete"]},
                        "table": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["operation"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "data": {"type": "array"},
                        "error": {"type": "string"}
                    }
                },
                category="data"
            ),
            MCPTool(
                name="api",
                description="API operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                        "url": {"type": "string"},
                        "headers": {"type": "object"},
                        "data": {"type": "object"}
                    },
                    "required": ["method", "url"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "status_code": {"type": "integer"},
                        "data": {"type": "object"},
                        "error": {"type": "string"}
                    }
                },
                category="external"
            )
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    async def connect(self) -> bool:
        """Connect to MCP server."""
        try:
            # Simulate connection to MCP server
            await asyncio.sleep(0.1)  # Simulate network delay
            self.connected = True
            logger.info("MCP Client connected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MCP server."""
        try:
            self.connected = False
            logger.info("MCP Client disconnected")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {e}")
            return False
    
    def register_tool(self, tool: MCPTool) -> bool:
        """Register a new MCP tool."""
        try:
            self.tools[tool.name] = tool
            logger.info(f"Registered MCP tool: {tool.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register tool {tool.name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister an MCP tool."""
        try:
            if tool_name in self.tools:
                del self.tools[tool_name]
                logger.info(f"Unregistered MCP tool: {tool_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def get_tools(self, category: Optional[str] = None) -> List[MCPTool]:
        """Get available tools, optionally filtered by category."""
        if category:
            return [tool for tool in self.tools.values() if tool.category == category]
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool by name."""
        return self.tools.get(tool_name)
    
    async def create_context(self, 
                           user_id: Optional[str] = None,
                           agent_id: Optional[str] = None,
                           project_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> MCPContext:
        """Create a new MCP context."""
        context = MCPContext(
            session_id=self.session_id,
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id,
            metadata=metadata or {}
        )
        
        context_id = f"context_{len(self.contexts) + 1}"
        self.contexts[context_id] = context
        
        logger.info(f"Created MCP context: {context_id}")
        return context
    
    async def get_context(self, context_id: str) -> Optional[MCPContext]:
        """Get a specific context by ID."""
        return self.contexts.get(context_id)
    
    async def update_context(self, context_id: str, metadata: Dict[str, Any]) -> bool:
        """Update context metadata."""
        try:
            if context_id in self.contexts:
                self.contexts[context_id].metadata.update(metadata)
                self.contexts[context_id].timestamp = datetime.utcnow()
                logger.info(f"Updated MCP context: {context_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update context {context_id}: {e}")
            return False
    
    async def call_tool(self, 
                       tool_name: str,
                       parameters: Dict[str, Any],
                       context: MCPContext) -> MCPResponse:
        """Call an MCP tool."""
        try:
            if not self.connected:
                raise Exception("MCP Client not connected")
            
            if tool_name not in self.tools:
                raise Exception(f"Tool {tool_name} not found")
            
            tool = self.tools[tool_name]
            request_id = f"req_{len(self.requests) + 1}"
            
            # Create request
            request = MCPRequest(
                tool_name=tool_name,
                parameters=parameters,
                context=context,
                request_id=request_id
            )
            self.requests[request_id] = request
            
            # Validate input schema
            if not self._validate_schema(parameters, tool.input_schema):
                return MCPResponse(
                    request_id=request_id,
                    success=False,
                    error="Invalid input parameters"
                )
            
            # Execute tool
            result = await self._execute_tool(tool, parameters, context)
            
            # Create response
            response = MCPResponse(
                request_id=request_id,
                success=result.get("success", False),
                data=result.get("data"),
                error=result.get("error"),
                metadata=result.get("metadata", {})
            )
            self.responses[request_id] = response
            
            logger.info(f"Executed MCP tool {tool_name} with request ID: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return MCPResponse(
                request_id=request_id if 'request_id' in locals() else "unknown",
                success=False,
                error=str(e)
            )
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate data against JSON schema."""
        # Simple schema validation - in production, use a proper JSON schema validator
        try:
            if "type" in schema:
                if schema["type"] == "object":
                    if not isinstance(data, dict):
                        return False
                    
                    if "required" in schema:
                        for field in schema["required"]:
                            if field not in data:
                                return False
                    
                    if "properties" in schema:
                        for field, field_schema in schema["properties"].items():
                            if field in data:
                                if not self._validate_schema(data[field], field_schema):
                                    return False
            
            return True
        except Exception:
            return False
    
    async def _execute_tool(self, tool: MCPTool, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        try:
            if tool.name == "file_system":
                return await self._execute_file_system_tool(parameters)
            elif tool.name == "database":
                return await self._execute_database_tool(parameters)
            elif tool.name == "api":
                return await self._execute_api_tool(parameters)
            else:
                # Custom tool execution
                return await self._execute_custom_tool(tool, parameters, context)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {"tool_name": tool.name}
            }
    
    async def _execute_file_system_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file system operations."""
        operation = parameters.get("operation")
        path = parameters.get("path")
        
        try:
            file_path = Path(path)
            
            if operation == "read":
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8')
                    return {
                        "success": True,
                        "data": {"content": content, "size": len(content)},
                        "metadata": {"operation": "read", "path": str(path)}
                    }
                else:
                    return {
                        "success": False,
                        "error": f"File not found: {path}",
                        "metadata": {"operation": "read", "path": str(path)}
                    }
            
            elif operation == "write":
                content = parameters.get("content", "")
                file_path.write_text(content, encoding='utf-8')
                return {
                    "success": True,
                    "data": {"path": str(path), "size": len(content)},
                    "metadata": {"operation": "write", "path": str(path)}
                }
            
            elif operation == "delete":
                if file_path.exists():
                    file_path.unlink()
                    return {
                        "success": True,
                        "data": {"path": str(path)},
                        "metadata": {"operation": "delete", "path": str(path)}
                    }
                else:
                    return {
                        "success": False,
                        "error": f"File not found: {path}",
                        "metadata": {"operation": "delete", "path": str(path)}
                    }
            
            elif operation == "list":
                if file_path.exists() and file_path.is_dir():
                    files = [f.name for f in file_path.iterdir()]
                    return {
                        "success": True,
                        "data": {"files": files, "count": len(files)},
                        "metadata": {"operation": "list", "path": str(path)}
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Directory not found: {path}",
                        "metadata": {"operation": "list", "path": str(path)}
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "metadata": {"operation": operation, "path": str(path)}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {"operation": operation, "path": str(path)}
            }
    
    async def _execute_database_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database operations."""
        # Placeholder for database operations
        # In production, this would connect to actual database
        return {
            "success": True,
            "data": {"message": "Database operation simulated"},
            "metadata": {"operation": parameters.get("operation"), "table": parameters.get("table")}
        }
    
    async def _execute_api_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API operations."""
        # Placeholder for API operations
        # In production, this would make actual HTTP requests
        return {
            "success": True,
            "data": {"message": "API operation simulated"},
            "metadata": {"method": parameters.get("method"), "url": parameters.get("url")}
        }
    
    async def _execute_custom_tool(self, tool: MCPTool, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute custom tools."""
        # Placeholder for custom tool execution
        return {
            "success": True,
            "data": {"message": f"Custom tool {tool.name} executed"},
            "metadata": {"tool_name": tool.name, "category": tool.category}
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get MCP client statistics."""
        return {
            "connected": self.connected,
            "session_id": self.session_id,
            "tools_count": len(self.tools),
            "contexts_count": len(self.contexts),
            "requests_count": len(self.requests),
            "responses_count": len(self.responses),
            "tools_by_category": {
                category: len([t for t in self.tools.values() if t.category == category])
                for category in set(tool.category for tool in self.tools.values())
            }
        }

# Global MCP client instance
_mcp_client: Optional[MCPClient] = None

def get_mcp_client(config: Optional[Dict[str, Any]] = None) -> MCPClient:
    """Get global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient(config)
    return _mcp_client

async def initialize_mcp_client(config: Optional[Dict[str, Any]] = None) -> MCPClient:
    """Initialize and connect MCP client."""
    client = get_mcp_client(config)
    await client.connect()
    return client 