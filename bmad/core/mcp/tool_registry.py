#!/usr/bin/env python3
"""
MCP Tool Registry for BMAD
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from .mcp_client import MCPTool, MCPContext, MCPResponse

logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    """Tool metadata for registry."""
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

class MCPToolRegistry:
    """MCP Tool Registry for managing and discovering tools."""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.metadata: Dict[str, ToolMetadata] = {}
        self.executors: Dict[str, Callable] = {}
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        
        # Initialize default categories
        self._initialize_categories()
        
        logger.info("MCP Tool Registry initialized")
    
    def _initialize_categories(self):
        """Initialize default tool categories."""
        self.categories = {
            "system": ["file_system", "process", "network"],
            "data": ["database", "cache", "storage"],
            "external": ["api", "webhook", "integration"],
            "development": ["code_analysis", "testing", "deployment"],
            "ai": ["llm", "embedding", "vector_search"],
            "monitoring": ["logging", "metrics", "alerting"],
            "security": ["authentication", "authorization", "encryption"]
        }
    
    def register_tool(self, 
                     tool: MCPTool,
                     executor: Optional[Callable] = None,
                     metadata: Optional[ToolMetadata] = None) -> bool:
        """Register a new tool in the registry."""
        try:
            # Register tool
            self.tools[tool.name] = tool
            
            # Register executor
            if executor:
                self.executors[tool.name] = executor
            
            # Register metadata
            if metadata:
                self.metadata[tool.name] = metadata
            else:
                # Create default metadata
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
            
            # Update category mapping
            if tool.category not in self.categories:
                self.categories[tool.category] = []
            if tool.name not in self.categories[tool.category]:
                self.categories[tool.category].append(tool.name)
            
            logger.info(f"Registered tool: {tool.name} in category: {tool.category}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool.name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the registry."""
        try:
            if tool_name in self.tools:
                # Remove from tools
                del self.tools[tool_name]
                
                # Remove from executors
                if tool_name in self.executors:
                    del self.executors[tool_name]
                
                # Remove from metadata
                if tool_name in self.metadata:
                    del self.metadata[tool_name]
                
                # Remove from categories
                for category, tools in self.categories.items():
                    if tool_name in tools:
                        tools.remove(tool_name)
                
                # Remove from tags
                for tag, tools in self.tags.items():
                    if tool_name in tools:
                        tools.remove(tool_name)
                
                logger.info(f"Unregistered tool: {tool_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def get_tools(self, category: Optional[str] = None) -> List[MCPTool]:
        """Get available tools, optionally filtered by category."""
        if category:
            return [tool for tool in self.tools.values() if tool.category == category]
        return list(self.tools.values())
    
    def get_tools_by_category(self, category: str) -> List[MCPTool]:
        """Get all tools in a category."""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_tools_by_tag(self, tag: str) -> List[MCPTool]:
        """Get all tools with a specific tag."""
        tool_names = self.tags.get(tag, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def search_tools(self, query: str) -> List[MCPTool]:
        """Search tools by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for tool in self.tools.values():
            # Search in name
            if query_lower in tool.name.lower():
                results.append(tool)
                continue
            
            # Search in description
            if query_lower in tool.description.lower():
                results.append(tool)
                continue
            
            # Search in tags
            metadata = self.metadata.get(tool.name)
            if metadata and any(query_lower in tag.lower() for tag in metadata.tags):
                results.append(tool)
                continue
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self.categories.keys())
    
    def get_tags(self) -> List[str]:
        """Get all available tags."""
        return list(self.tags.keys())
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get tool metadata."""
        return self.metadata.get(tool_name)
    
    async def execute_tool(self, 
                          tool_name: str,
                          parameters: Dict[str, Any],
                          context: MCPContext) -> MCPResponse:
        """Execute a tool."""
        try:
            if tool_name not in self.tools:
                return MCPResponse(
                    request_id=f"req_{datetime.utcnow().timestamp()}",
                    success=False,
                    error=f"Tool {tool_name} not found"
                )
            
            tool = self.tools[tool_name]
            executor = self.executors.get(tool_name)
            
            if not executor:
                return MCPResponse(
                    request_id=f"req_{datetime.utcnow().timestamp()}",
                    success=False,
                    error=f"No executor found for tool {tool_name}"
                )
            
            # Update usage statistics
            if tool_name in self.metadata:
                self.metadata[tool_name].usage_count += 1
                self.metadata[tool_name].updated_at = datetime.utcnow()
            
            # Execute tool
            result = await executor(parameters, context)
            
            # Update success rate
            if tool_name in self.metadata:
                metadata = self.metadata[tool_name]
                if result.success:
                    metadata.success_rate = (metadata.success_rate * (metadata.usage_count - 1) + 1) / metadata.usage_count
                else:
                    metadata.success_rate = (metadata.success_rate * (metadata.usage_count - 1)) / metadata.usage_count
            
            logger.info(f"Executed tool {tool_name} successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return MCPResponse(
                request_id=f"req_{datetime.utcnow().timestamp()}",
                success=False,
                error=str(e)
            )
    
    def add_tag(self, tool_name: str, tag: str) -> bool:
        """Add a tag to a tool."""
        try:
            if tool_name not in self.tools:
                return False
            
            if tag not in self.tags:
                self.tags[tag] = []
            
            if tool_name not in self.tags[tag]:
                self.tags[tag].append(tool_name)
            
            # Update metadata
            if tool_name in self.metadata:
                if tag not in self.metadata[tool_name].tags:
                    self.metadata[tool_name].tags.append(tag)
            
            logger.info(f"Added tag {tag} to tool {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add tag {tag} to tool {tool_name}: {e}")
            return False
    
    def remove_tag(self, tool_name: str, tag: str) -> bool:
        """Remove a tag from a tool."""
        try:
            if tag in self.tags and tool_name in self.tags[tag]:
                self.tags[tag].remove(tool_name)
            
            if tool_name in self.metadata and tag in self.metadata[tool_name].tags:
                self.metadata[tool_name].tags.remove(tag)
            
            logger.info(f"Removed tag {tag} from tool {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove tag {tag} from tool {tool_name}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_tools = len(self.tools)
        total_categories = len(self.categories)
        total_tags = len(self.tags)
        
        # Calculate average success rate
        success_rates = [meta.success_rate for meta in self.metadata.values() if meta.usage_count > 0]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        
        # Most used tools
        most_used = sorted(
            self.metadata.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )[:5]
        
        # Tools by category
        tools_by_category = {
            category: len(tools) for category, tools in self.categories.items()
        }
        
        return {
            "total_tools": total_tools,
            "total_categories": total_categories,
            "total_tags": total_tags,
            "average_success_rate": avg_success_rate,
            "most_used_tools": [
                {
                    "name": meta.name,
                    "usage_count": meta.usage_count,
                    "success_rate": meta.success_rate
                }
                for meta in most_used
            ],
            "tools_by_category": tools_by_category
        }
    
    def export_registry(self, file_path: str) -> bool:
        """Export registry to JSON file."""
        try:
            export_data = {
                "tools": {
                    name: {
                        "tool": asdict(tool),
                        "metadata": asdict(self.metadata.get(name, ToolMetadata(
                            name=name,
                            description=tool.description,
                            version=tool.version,
                            category=tool.category,
                            author="BMAD System",
                            tags=[],
                            dependencies=[],
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )))
                    }
                    for name, tool in self.tools.items()
                },
                "categories": self.categories,
                "tags": self.tags,
                "exported_at": datetime.utcnow().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported registry to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export registry: {e}")
            return False
    
    def import_registry(self, file_path: str) -> bool:
        """Import registry from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Clear existing registry
            self.tools.clear()
            self.metadata.clear()
            self.categories.clear()
            self.tags.clear()
            
            # Import tools and metadata
            for name, data in import_data.get("tools", {}).items():
                tool_data = data["tool"]
                metadata_data = data["metadata"]
                
                # Recreate tool
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    input_schema=tool_data["input_schema"],
                    output_schema=tool_data["output_schema"],
                    category=tool_data["category"],
                    version=tool_data["version"]
                )
                self.tools[name] = tool
                
                # Recreate metadata
                metadata = ToolMetadata(
                    name=metadata_data["name"],
                    description=metadata_data["description"],
                    version=metadata_data["version"],
                    category=metadata_data["category"],
                    author=metadata_data["author"],
                    tags=metadata_data["tags"],
                    dependencies=metadata_data["dependencies"],
                    created_at=datetime.fromisoformat(metadata_data["created_at"]),
                    updated_at=datetime.fromisoformat(metadata_data["updated_at"]),
                    usage_count=metadata_data["usage_count"],
                    success_rate=metadata_data["success_rate"]
                )
                self.metadata[name] = metadata
            
            # Import categories and tags
            self.categories = import_data.get("categories", {})
            self.tags = import_data.get("tags", {})
            
            logger.info(f"Imported registry from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import registry: {e}")
            return False

# Global tool registry instance
_tool_registry: Optional[MCPToolRegistry] = None

def get_tool_registry() -> MCPToolRegistry:
    """Get global tool registry instance."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = MCPToolRegistry()
    return _tool_registry

def register_tool(tool: MCPTool, executor: Optional[Callable] = None, metadata: Optional[ToolMetadata] = None) -> bool:
    """Register a tool in the global registry."""
    registry = get_tool_registry()
    return registry.register_tool(tool, executor, metadata)

def get_tool(tool_name: str) -> Optional[MCPTool]:
    """Get a tool from the global registry."""
    registry = get_tool_registry()
    return registry.get_tool(tool_name)

def get_tools_by_category(category: str) -> List[MCPTool]:
    """Get tools by category from the global registry."""
    registry = get_tool_registry()
    return registry.get_tools_by_category(category)

async def execute_tool(tool_name: str, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
    """Execute a tool from the global registry."""
    registry = get_tool_registry()
    return await registry.execute_tool(tool_name, parameters, context) 