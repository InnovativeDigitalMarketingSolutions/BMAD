#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Tool Registry Implementation for BMAD
Following official MCP specification: https://modelcontextprotocol.io/docs
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """MCP Tool categories following official specification."""
    SYSTEM = "system"
    DATA = "data"
    NETWORK = "network"
    DEVELOPMENT = "development"
    TESTING = "testing"
    QUALITY = "quality"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    CUSTOM = "custom"

@dataclass
class ToolMetadata:
    """MCP Tool metadata following official specification."""
    name: str
    description: str
    version: str
    category: str
    author: str
    tags: List[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    parameters: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None

class MCPToolRegistry:
    """MCP Tool Registry following official specification."""
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.metadata: Dict[str, ToolMetadata] = {}
        self.executors: Dict[str, Callable] = {}
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        self._initialize_categories()
        
        logger.info("MCP Tool Registry initialized")
    
    def _initialize_categories(self):
        """Initialize tool categories following MCP specification."""
        for category in ToolCategory:
            self.categories[category.value] = []
    
    def register_tool(self, 
                    tool: Any,
                    executor: Optional[Callable] = None,
                    metadata: Optional[ToolMetadata] = None) -> bool:
        """Register MCP tool following official specification."""
        try:
            if not self._validate_tool(tool):
                logger.error(f"Invalid tool definition: {tool.name}")
                return False
            
            # Register tool
            self.tools[tool.name] = tool
            
            # Register executor
            if executor:
                self.executors[tool.name] = executor
            
            # Create or update metadata
            if metadata:
                self.metadata[tool.name] = metadata
            else:
                self.metadata[tool.name] = ToolMetadata(
                    name=tool.name,
                    description=tool.description,
                    version=tool.version,
                    category=tool.category,
                    author="BMAD System",
                    tags=[],
                    dependencies=[],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            # Update categories
            if tool.category not in self.categories:
                self.categories[tool.category] = []
            self.categories[tool.category].append(tool.name)
            
            # Update tags
            for tag in self.metadata[tool.name].tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(tool.name)
            
            logger.info(f"Registered MCP tool: {tool.name} (category: {tool.category})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering tool {tool.name}: {e}")
            return False
    
    def _validate_tool(self, tool: Any) -> bool:
        """Validate tool definition according to MCP specification."""
        required_fields = ["name", "description", "input_schema", "output_schema", "category"]
        
        for field in required_fields:
            if not hasattr(tool, field) or getattr(tool, field) is None:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate schemas
        if not self._validate_schema(tool.input_schema):
            logger.error(f"Invalid input schema for tool: {tool.name}")
            return False
        
        if not self._validate_schema(tool.output_schema):
            logger.error(f"Invalid output schema for tool: {tool.name}")
            return False
        
        return True
    
    def _validate_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate JSON schema according to MCP specification."""
        try:
            if not isinstance(schema, dict):
                return False
            
            if "type" not in schema:
                return False
            
            # Basic schema validation
            schema_type = schema.get("type")
            if schema_type == "object":
                properties = schema.get("properties", {})
                if not isinstance(properties, dict):
                    return False
                
                required = schema.get("required", [])
                if not isinstance(required, list):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister MCP tool."""
        try:
            if tool_name not in self.tools:
                logger.warning(f"Tool not found: {tool_name}")
                return False
            
            # Remove from tools
            tool = self.tools.pop(tool_name)
            
            # Remove from executors
            if tool_name in self.executors:
                del self.executors[tool_name]
            
            # Remove from metadata
            if tool_name in self.metadata:
                metadata = self.metadata.pop(tool_name)
                
                # Remove from categories
                if metadata.category in self.categories:
                    if tool_name in self.categories[metadata.category]:
                        self.categories[metadata.category].remove(tool_name)
                
                # Remove from tags
                for tag in metadata.tags:
                    if tag in self.tags and tool_name in self.tags[tag]:
                        self.tags[tag].remove(tool_name)
            
            logger.info(f"Unregistered MCP tool: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering tool {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get MCP tool by name."""
        return self.tools.get(tool_name)
    
    def get_tools(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Any]:
        """Get MCP tools with optional filtering."""
        tools = list(self.tools.values())
        
        if category:
            tools = [tool for tool in tools if tool.category == category]
        
        if tags:
            tools = [tool for tool in tools if any(tag in self.metadata.get(tool.name, ToolMetadata).tags for tag in tags)]
        
        return tools
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get MCP tool metadata."""
        return self.metadata.get(tool_name)
    
    def update_tool_metadata(self, tool_name: str, metadata: ToolMetadata) -> bool:
        """Update MCP tool metadata."""
        try:
            if tool_name not in self.tools:
                logger.warning(f"Tool not found: {tool_name}")
                return False
            
            metadata.updated_at = datetime.utcnow()
            self.metadata[tool_name] = metadata
            
            logger.info(f"Updated metadata for tool: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata for tool {tool_name}: {e}")
            return False
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get all tool categories."""
        return self.categories.copy()
    
    def get_tags(self) -> Dict[str, List[str]]:
        """Get all tool tags."""
        return self.tags.copy()
    
    def search_tools(self, query: str) -> List[Any]:
        """Search tools by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            metadata = self.metadata.get(tool.name)
            
            # Search in name
            if query_lower in tool.name.lower():
                results.append(tool)
                continue
            
            # Search in description
            if query_lower in tool.description.lower():
                results.append(tool)
                continue
            
            # Search in tags
            if metadata and any(query_lower in tag.lower() for tag in metadata.tags):
                results.append(tool)
                continue
        
        return results
    
    def get_usage_statistics(self, tool_name: str) -> Dict[str, Any]:
        """Get usage statistics for a tool."""
        metadata = self.metadata.get(tool_name)
        if not metadata:
            return {}
        
        return {
            "name": tool_name,
            "usage_count": metadata.usage_count,
            "success_rate": metadata.success_rate,
            "last_used": metadata.last_used.isoformat() if metadata.last_used else None,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat()
        }
    
    def record_tool_usage(self, tool_name: str, success: bool) -> bool:
        """Record tool usage for statistics."""
        try:
            if tool_name not in self.metadata:
                logger.warning(f"Tool metadata not found: {tool_name}")
                return False
            
            metadata = self.metadata[tool_name]
            metadata.usage_count += 1
            metadata.last_used = datetime.utcnow()
            
            # Update success rate
            if metadata.usage_count == 1:
                metadata.success_rate = 1.0 if success else 0.0
            else:
                current_successes = metadata.success_rate * (metadata.usage_count - 1)
                if success:
                    current_successes += 1
                metadata.success_rate = current_successes / metadata.usage_count
            
            logger.debug(f"Recorded usage for tool: {tool_name} (success: {success})")
            return True
            
        except Exception as e:
            logger.error(f"Error recording usage for tool {tool_name}: {e}")
            return False
    
    def get_popular_tools(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular tools by usage count."""
        tools_with_stats = []
        
        for tool_name, metadata in self.metadata.items():
            tools_with_stats.append({
                "name": tool_name,
                "usage_count": metadata.usage_count,
                "success_rate": metadata.success_rate,
                "category": metadata.category
            })
        
        # Sort by usage count (descending)
        tools_with_stats.sort(key=lambda x: x["usage_count"], reverse=True)
        
        return tools_with_stats[:limit]
    
    def export_tool_registry(self, format: str = "json") -> str:
        """Export tool registry to specified format."""
        try:
            export_data = {
                "tools": {},
                "metadata": {},
                "categories": self.categories,
                "tags": self.tags,
                "exported_at": datetime.utcnow().isoformat()
            }
            
            # Export tools
            for name, tool in self.tools.items():
                export_data["tools"][name] = {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "version": tool.version,
                    "input_schema": tool.input_schema,
                    "output_schema": tool.output_schema
                }
            
            # Export metadata
            for name, metadata in self.metadata.items():
                export_data["metadata"][name] = asdict(metadata)
            
            if format.lower() == "json":
                return json.dumps(export_data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting tool registry: {e}")
            return ""
    
    def import_tool_registry(self, data: str, format: str = "json") -> bool:
        """Import tool registry from specified format."""
        try:
            if format.lower() == "json":
                import_data = json.loads(data)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            # Import tools (basic structure)
            for name, tool_data in import_data.get("tools", {}).items():
                # Note: This is a simplified import - in production, you'd want to recreate actual tool objects
                logger.info(f"Imported tool: {name}")
            
            # Import metadata
            for name, metadata_data in import_data.get("metadata", {}).items():
                # Convert string dates back to datetime objects
                if "created_at" in metadata_data:
                    metadata_data["created_at"] = datetime.fromisoformat(metadata_data["created_at"])
                if "updated_at" in metadata_data:
                    metadata_data["updated_at"] = datetime.fromisoformat(metadata_data["updated_at"])
                if "last_used" in metadata_data and metadata_data["last_used"]:
                    metadata_data["last_used"] = datetime.fromisoformat(metadata_data["last_used"])
                
                metadata = ToolMetadata(**metadata_data)
                self.metadata[name] = metadata
            
            logger.info("Tool registry import completed")
            return True
            
        except Exception as e:
            logger.error(f"Error importing tool registry: {e}")
            return False
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics."""
        total_tools = len(self.tools)
        total_usage = sum(metadata.usage_count for metadata in self.metadata.values())
        avg_success_rate = sum(metadata.success_rate for metadata in self.metadata.values()) / total_tools if total_tools > 0 else 0
        
        category_stats = {}
        for category, tools in self.categories.items():
            category_stats[category] = {
                "tool_count": len(tools),
                "usage_count": sum(self.metadata.get(tool_name, ToolMetadata).usage_count for tool_name in tools)
            }
        
        return {
            "total_tools": total_tools,
            "total_usage": total_usage,
            "average_success_rate": avg_success_rate,
            "categories": category_stats,
            "total_tags": len(self.tags),
            "most_popular_tools": self.get_popular_tools(5),
            "last_updated": datetime.utcnow().isoformat()
        }

def get_mcp_tool_registry() -> MCPToolRegistry:
    """Get MCP tool registry instance."""
    return MCPToolRegistry()

def execute_tool(tool_name: str, parameters: Dict[str, Any], registry: MCPToolRegistry) -> Dict[str, Any]:
    """Execute tool through registry."""
    try:
        tool = registry.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool not found: {tool_name}"}
        
        executor = registry.executors.get(tool_name)
        if executor:
            result = executor(parameters)
            registry.record_tool_usage(tool_name, True)
            return {"success": True, "data": result}
        else:
            registry.record_tool_usage(tool_name, False)
            return {"success": False, "error": f"No executor found for tool: {tool_name}"}
            
    except Exception as e:
        registry.record_tool_usage(tool_name, False)
        return {"success": False, "error": str(e)} 