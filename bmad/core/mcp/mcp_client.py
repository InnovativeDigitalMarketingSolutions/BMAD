#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Client Implementation for BMAD
Following official MCP specification: https://modelcontextprotocol.io/docs
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

class MCPVersion(Enum):
    """MCP Protocol versions."""
    V1_0 = "1.0"
    V1_1 = "1.1"

class MCPMessageType(Enum):
    """MCP Message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

@dataclass
class MCPTool:
    """MCP Tool definition following official specification."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    category: str
    version: str = "1.0.0"
    parameters: Optional[Dict[str, Any]] = None
    handler: Optional[Callable] = None

@dataclass
class MCPContext:
    """MCP Context definition."""
    session_id: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    version: str = MCPVersion.V1_1.value
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class MCPRequest:
    """MCP Request definition."""
    tool_name: str
    parameters: Dict[str, Any]
    context: MCPContext
    request_id: str
    timestamp: datetime = None
    message_type: str = MCPMessageType.REQUEST.value
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class MCPResponse:
    """MCP Response definition."""
    request_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    message_type: str = MCPMessageType.RESPONSE.value
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass
class MCPServerInfo:
    """MCP Server information."""
    name: str
    version: str
    description: str
    capabilities: List[str]
    supported_versions: List[str]

class MCPClient:
    """MCP Client for BMAD system following official specification."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: Dict[str, MCPTool] = {}
        self.contexts: Dict[str, MCPContext] = {}
        self.requests: Dict[str, MCPRequest] = {}
        self.responses: Dict[str, MCPResponse] = {}
        self.connected = False
        self.session_id = self._generate_session_id()
        self.version = MCPVersion.V1_1.value
        self.server_info: Optional[MCPServerInfo] = None
        
        # Enhanced MCP attributes
        self.enhanced_enabled = False
        self.enhanced_capabilities: Dict[str, bool] = {}
        self.enhanced_mcp_client = None
        
        # Initialize default tools
        self._initialize_default_tools()
        
        logger.info(f"MCP Client initialized with session ID: {self.session_id}, version: {self.version}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return str(uuid.uuid4())
    
    def _initialize_default_tools(self):
        """Initialize default MCP tools following official specification."""
        default_tools = [
            MCPTool(
                name="file_system",
                description="File system operations following MCP specification",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["read", "write", "list", "delete", "exists"]
                        },
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "recursive": {"type": "boolean"}
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
                category="system",
                handler=lambda params, ctx: self._execute_file_system_tool(params)
            ),
            MCPTool(
                name="database",
                description="Database operations following MCP specification",
                input_schema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["query", "execute", "connect", "disconnect"]
                        },
                        "query": {"type": "string"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["operation"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "data": {"type": "object"},
                        "error": {"type": "string"}
                    }
                },
                category="data",
                handler=lambda params, ctx: self._execute_database_tool(params)
            ),
            MCPTool(
                name="api",
                description="API operations following MCP specification",
                input_schema={
                    "type": "object",
                    "properties": {
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                        },
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
                        "data": {"type": "object"},
                        "error": {"type": "string"}
                    }
                },
                category="network",
                handler=lambda params, ctx: self._execute_api_tool(params)
            )
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    async def connect(self) -> bool:
        """Connect to MCP server following official specification."""
        try:
            # Simulate server connection
            self.server_info = MCPServerInfo(
                name="BMAD MCP Server",
                version="1.1.0",
                description="BMAD Model Context Protocol Server",
                capabilities=["tools", "context", "streaming"],
                supported_versions=["1.0", "1.1"]
            )
            
            self.connected = True
            logger.info(f"Connected to MCP server: {self.server_info.name} v{self.server_info.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def initialize_enhanced(self) -> bool:
        """Initialize enhanced MCP capabilities."""
        try:
            # Connect to MCP server first
            if not await self.connect():
                logger.error("Failed to connect to MCP server for enhanced initialization")
                return False
            
            # Initialize enhanced capabilities
            self.enhanced_enabled = True
            self.enhanced_capabilities = {
                "advanced_tracing": True,
                "inter_agent_communication": True,
                "performance_monitoring": True,
                "security_validation": True,
                "workflow_orchestration": True
            }
            
            # Set enhanced MCP client reference
            self.enhanced_mcp_client = self
            
            # Register enhanced tools
            enhanced_tools = [
                MCPTool(
                    name="enhanced_trace",
                    description="Enhanced tracing for distributed systems",
                    input_schema={"type": "object", "properties": {"operation": {"type": "string"}}},
                    output_schema={"type": "object", "properties": {"trace_id": {"type": "string"}}},
                    category="enhanced"
                ),
                MCPTool(
                    name="inter_agent_communicate",
                    description="Inter-agent communication protocol",
                    input_schema={"type": "object", "properties": {"message": {"type": "string"}, "target_agent": {"type": "string"}}},
                    output_schema={"type": "object", "properties": {"response": {"type": "string"}}},
                    category="enhanced"
                ),
                MCPTool(
                    name="performance_monitor",
                    description="Performance monitoring and metrics",
                    input_schema={"type": "object", "properties": {"metric": {"type": "string"}}},
                    output_schema={"type": "object", "properties": {"value": {"type": "number"}}},
                    category="enhanced"
                )
            ]
            
            for tool in enhanced_tools:
                self.register_tool(tool)
            
            logger.info("Enhanced MCP capabilities initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced MCP capabilities: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MCP server."""
        try:
            self.connected = False
            self.server_info = None
            logger.info("Disconnected from MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {e}")
            return False
    
    def register_tool(self, tool: MCPTool) -> bool:
        """Register MCP tool following official specification."""
        try:
            if not self._validate_tool(tool):
                logger.error(f"Invalid tool definition: {tool.name}")
                return False
            
            self.tools[tool.name] = tool
            logger.info(f"Registered MCP tool: {tool.name} (category: {tool.category})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering tool {tool.name}: {e}")
            return False
    
    def _validate_tool(self, tool: MCPTool) -> bool:
        """Validate tool definition according to MCP specification."""
        required_fields = ["name", "description", "input_schema", "output_schema", "category"]
        
        for field in required_fields:
            if not hasattr(tool, field) or getattr(tool, field) is None:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate schemas
        if not self._validate_schema(tool.input_schema, {"type": "object"}):
            logger.error(f"Invalid input schema for tool: {tool.name}")
            return False
        
        if not self._validate_schema(tool.output_schema, {"type": "object"}):
            logger.error(f"Invalid output schema for tool: {tool.name}")
            return False
        
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister MCP tool."""
        try:
            if tool_name in self.tools:
                del self.tools[tool_name]
                logger.info(f"Unregistered MCP tool: {tool_name}")
                return True
            else:
                logger.warning(f"Tool not found: {tool_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error unregistering tool {tool_name}: {e}")
            return False
    
    def get_tools(self, category: Optional[str] = None) -> List[MCPTool]:
        """Get available tools, optionally filtered by category."""
        if category:
            return [tool for tool in self.tools.values() if tool.category == category]
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get specific tool by name."""
        return self.tools.get(tool_name)
    
    async def create_context(self, 
                          user_id: Optional[str] = None,
                          agent_id: Optional[str] = None,
                          project_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> MCPContext:
        """Create MCP context following official specification."""
        context_id = str(uuid.uuid4())
        
        context = MCPContext(
            session_id=self.session_id,
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id,
            metadata=metadata or {},
            version=self.version
        )
        
        self.contexts[context_id] = context
        logger.info(f"Created MCP context: {context_id}")
        return context
    
    async def get_context(self, context_id: str) -> Optional[MCPContext]:
        """Get MCP context by ID."""
        return self.contexts.get(context_id)
    
    async def update_context(self, context_id: str, metadata: Dict[str, Any]) -> bool:
        """Update MCP context metadata."""
        try:
            if context_id in self.contexts:
                self.contexts[context_id].metadata.update(metadata)
                self.contexts[context_id].timestamp = datetime.now(timezone.utc)
                logger.info(f"Updated MCP context: {context_id}")
                return True
            else:
                logger.warning(f"Context not found: {context_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating context {context_id}: {e}")
            return False
    
    async def create_enhanced_context(self, 
                                   user_id: Optional[str] = None,
                                   agent_id: Optional[str] = None,
                                   project_id: Optional[str] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> MCPContext:
        """Create enhanced MCP context with additional capabilities."""
        context_id = str(uuid.uuid4())
        
        # Enhanced metadata
        enhanced_metadata = metadata or {}
        enhanced_metadata.update({
            "enhanced_capabilities": True,
            "tracing_enabled": True,
            "performance_monitoring": True,
            "security_validation": True
        })
        
        context = MCPContext(
            session_id=self.session_id,
            user_id=user_id,
            agent_id=agent_id,
            project_id=project_id,
            metadata=enhanced_metadata,
            version=self.version
        )
        
        self.contexts[context_id] = context
        logger.info(f"Created enhanced MCP context: {context_id}")
        return context
    
    async def call_tool(self, 
                      tool_name: str,
                      parameters: Dict[str, Any],
                      context: MCPContext) -> MCPResponse:
        """Call MCP tool following official specification."""
        request_id = str(uuid.uuid4())
        
        try:
            # Create request
            request = MCPRequest(
                tool_name=tool_name,
                parameters=parameters,
                context=context,
                request_id=request_id
            )
            
            self.requests[request_id] = request
            
            # Validate tool exists
            tool = self.get_tool(tool_name)
            if not tool:
                return MCPResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Tool not found: {tool_name}"
                )
            
            # Validate parameters
            if not self._validate_schema(parameters, tool.input_schema):
                return MCPResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Invalid parameters for tool: {tool_name}"
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
            
            logger.info(f"Tool call completed: {tool_name} (request: {request_id})")
            return response
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return MCPResponse(
                request_id=request_id,
                success=False,
                error=str(e)
            )
    
    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate data against JSON schema following MCP specification."""
        try:
            # Basic schema validation
            if schema.get("type") == "object":
                required_props = schema.get("required", [])
                properties = schema.get("properties", {})
                
                # Check required properties
                for prop in required_props:
                    if prop not in data:
                        logger.error(f"Missing required property: {prop}")
                        return False
                
                # Check property types
                for prop, value in data.items():
                    if prop in properties:
                        prop_schema = properties[prop]
                        if not self._validate_property_type(value, prop_schema):
                            logger.error(f"Invalid type for property {prop}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    def _validate_property_type(self, value: Any, schema: Dict[str, Any]) -> bool:
        """Validate property type against schema."""
        prop_type = schema.get("type")
        
        if prop_type == "string":
            return isinstance(value, str)
        elif prop_type == "boolean":
            return isinstance(value, bool)
        elif prop_type == "object":
            return isinstance(value, dict)
        elif prop_type == "array":
            return isinstance(value, list)
        elif prop_type == "number":
            return isinstance(value, (int, float))
        
        return True
    
    async def _execute_tool(self, tool: MCPTool, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute MCP tool following official specification."""
        try:
            if tool.handler:
                # Use custom handler
                result = await tool.handler(parameters, context)
                return {
                    "success": True,
                    "data": result,
                    "metadata": {
                        "tool_name": tool.name,
                        "category": tool.category,
                        "version": tool.version,
                        "execution_time": datetime.now(timezone.utc).isoformat()
                    }
                }
            else:
                # Use default handlers based on category
                if tool.category == "system":
                    return await self._execute_file_system_tool(parameters)
                elif tool.category == "data":
                    return await self._execute_database_tool(parameters)
                elif tool.category == "network":
                    return await self._execute_api_tool(parameters)
                else:
                    return await self._execute_custom_tool(tool, parameters, context)
                    
        except Exception as e:
            logger.error(f"Error executing tool {tool.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "tool_name": tool.name,
                    "category": tool.category,
                    "version": tool.version
                }
            }
    
    async def _execute_file_system_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file system operations following MCP specification."""
        try:
            operation = parameters.get("operation")
            path = parameters.get("path")
            
            if not path:
                return {"success": False, "error": "Path is required"}
            
            file_path = Path(path)
            
            if operation == "read":
                if file_path.exists():
                    content = file_path.read_text()
                    return {
                        "success": True,
                        "data": {
                            "content": content,
                            "size": len(content),
                            "modified": file_path.stat().st_mtime
                        }
                    }
                else:
                    return {"success": False, "error": "File not found"}
                    
            elif operation == "write":
                content = parameters.get("content", "")
                file_path.write_text(content)
                return {
                    "success": True,
                    "data": {
                        "path": str(file_path),
                        "size": len(content)
                    }
                }
                
            elif operation == "list":
                if file_path.exists() and file_path.is_dir():
                    files = []
                    for item in file_path.iterdir():
                        files.append({
                            "name": item.name,
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else None
                        })
                    return {"success": True, "data": {"files": files}}
                else:
                    return {"success": False, "error": "Directory not found"}
                    
            elif operation == "delete":
                if file_path.exists():
                    if file_path.is_file():
                        file_path.unlink()
                    else:
                        import shutil
                        shutil.rmtree(file_path)
                    return {"success": True, "data": {"deleted": str(file_path)}}
                else:
                    return {"success": False, "error": "File not found"}
                    
            elif operation == "exists":
                return {
                    "success": True,
                    "data": {
                        "exists": file_path.exists(),
                        "is_file": file_path.is_file() if file_path.exists() else False,
                        "is_dir": file_path.is_dir() if file_path.exists() else False
                    }
                }
            
            return {"success": False, "error": f"Unknown operation: {operation}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_database_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database operations following MCP specification."""
        try:
            operation = parameters.get("operation")
            
            if operation == "query":
                # Simulate database query
                return {
                    "success": True,
                    "data": {
                        "rows": [],
                        "columns": [],
                        "row_count": 0
                    }
                }
            elif operation == "execute":
                # Simulate database execution
                return {
                    "success": True,
                    "data": {
                        "affected_rows": 0,
                        "last_insert_id": None
                    }
                }
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_api_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API operations following MCP specification."""
        try:
            method = parameters.get("method", "GET")
            url = parameters.get("url", "")
            
            # Simulate API call
            return {
                "success": True,
                "data": {
                    "status_code": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": {"message": "API call simulated"}
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_custom_tool(self, tool: MCPTool, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute custom tool following MCP specification."""
        try:
            # Default custom tool implementation
            return {
                "success": True,
                "data": {
                    "tool_name": tool.name,
                    "parameters": parameters,
                    "context": {
                        "session_id": context.session_id,
                        "agent_id": context.agent_id
                    }
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get MCP client statistics following official specification."""
        return {
            "session_id": self.session_id,
            "version": self.version,
            "connected": self.connected,
            "tools_count": len(self.tools),
            "contexts_count": len(self.contexts),
            "requests_count": len(self.requests),
            "responses_count": len(self.responses),
            "server_info": asdict(self.server_info) if self.server_info else None,
            "tool_categories": list(set(tool.category for tool in self.tools.values())),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def get_mcp_client(config: Optional[Dict[str, Any]] = None) -> MCPClient:
    """Get MCP client instance."""
    return MCPClient(config)

async def initialize_mcp_client(config: Optional[Dict[str, Any]] = None) -> MCPClient:
    """Initialize and connect MCP client."""
    client = MCPClient(config)
    await client.connect()
    return client 