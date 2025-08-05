#!/usr/bin/env python3
"""
Comprehensive Test Suite for MCP Tool Registry
Target: Improve coverage from 48% to 75%
"""

import pytest
import json
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from bmad.core.mcp.tool_registry import (
    MCPToolRegistry,
    ToolMetadata,
    ToolCategory,
    get_mcp_tool_registry,
    execute_tool
)

# Mock MCPTool class for testing
class MockMCPTool:
    def __init__(self, name: str, description: str, category: str = "testing", version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.category = category
        self.version = version
        self.input_schema = {"type": "object", "properties": {"test": {"type": "string"}}}
        self.output_schema = {"type": "object", "properties": {"result": {"type": "string"}}}

class TestMCPToolRegistry:
    """Comprehensive test suite for MCPToolRegistry."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = MCPToolRegistry()
        self.test_tool = MockMCPTool("test_tool", "Test tool for validation")
        self.test_metadata = ToolMetadata(
            name="test_tool",
            description="Test tool for validation",
            version="1.0.0",
            category="testing",
            author="Test Author",
            tags=["test", "validation"],
            dependencies=["pytest"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    def test_initialization(self):
        """Test registry initialization."""
        assert self.registry.tools == {}
        assert self.registry.metadata == {}
        assert self.registry.executors == {}
        assert len(self.registry.categories) == len(ToolCategory)
        assert self.registry.tags == {}
    
    def test_initialize_categories(self):
        """Test category initialization."""
        for category in ToolCategory:
            assert category.value in self.registry.categories
            assert isinstance(self.registry.categories[category.value], list)
    
    def test_register_tool_success(self):
        """Test successful tool registration."""
        success = self.registry.register_tool(self.test_tool)
        assert success is True
        assert "test_tool" in self.registry.tools
        assert "test_tool" in self.registry.metadata
        assert "test_tool" in self.registry.categories["testing"]
    
    def test_register_tool_with_executor(self):
        """Test tool registration with executor."""
        mock_executor = Mock(return_value={"result": "success"})
        success = self.registry.register_tool(self.test_tool, executor=mock_executor)
        assert success is True
        assert "test_tool" in self.registry.executors
    
    def test_register_tool_with_metadata(self):
        """Test tool registration with custom metadata."""
        success = self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        assert success is True
        metadata = self.registry.metadata["test_tool"]
        assert metadata.author == "Test Author"
        assert "test" in metadata.tags
    
    def test_register_tool_validation_failure(self):
        """Test tool registration with invalid tool."""
        invalid_tool = Mock()
        invalid_tool.name = "invalid_tool"
        # Missing required fields
        success = self.registry.register_tool(invalid_tool)
        assert success is False
    
    def test_register_tool_duplicate(self):
        """Test registering duplicate tool."""
        # Register first time
        success1 = self.registry.register_tool(self.test_tool)
        assert success1 is True
        
        # Register again (should update)
        success2 = self.registry.register_tool(self.test_tool)
        assert success2 is True
        assert len(self.registry.tools) == 1  # Still only one tool
    
    def test_validate_tool_success(self):
        """Test tool validation with valid tool."""
        assert self.registry._validate_tool(self.test_tool) is True
    
    def test_validate_tool_missing_fields(self):
        """Test tool validation with missing fields."""
        invalid_tool = Mock()
        invalid_tool.name = "invalid"
        # Missing description
        assert self.registry._validate_tool(invalid_tool) is False
    
    def test_validate_schema_success(self):
        """Test schema validation with valid schema."""
        valid_schema = {
            "type": "object",
            "properties": {"test": {"type": "string"}},
            "required": ["test"]
        }
        assert self.registry._validate_schema(valid_schema) is True
    
    def test_validate_schema_invalid_type(self):
        """Test schema validation with invalid type."""
        invalid_schema = "not_a_dict"
        assert self.registry._validate_schema(invalid_schema) is False
    
    def test_validate_schema_missing_type(self):
        """Test schema validation with missing type."""
        invalid_schema = {"properties": {"test": {"type": "string"}}}
        assert self.registry._validate_schema(invalid_schema) is False
    
    def test_validate_schema_invalid_properties(self):
        """Test schema validation with invalid properties."""
        invalid_schema = {
            "type": "object",
            "properties": "not_a_dict"
        }
        assert self.registry._validate_schema(invalid_schema) is False
    
    def test_unregister_tool_success(self):
        """Test successful tool unregistration."""
        # Register tool first
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        # Unregister
        success = self.registry.unregister_tool("test_tool")
        assert success is True
        assert "test_tool" not in self.registry.tools
        assert "test_tool" not in self.registry.metadata
        assert "test_tool" not in self.registry.categories["testing"]
    
    def test_unregister_tool_not_found(self):
        """Test unregistering non-existent tool."""
        success = self.registry.unregister_tool("non_existent")
        assert success is False
    
    def test_get_tool_success(self):
        """Test getting existing tool."""
        self.registry.register_tool(self.test_tool)
        tool = self.registry.get_tool("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"
    
    def test_get_tool_not_found(self):
        """Test getting non-existent tool."""
        tool = self.registry.get_tool("non_existent")
        assert tool is None
    
    def test_get_tools_no_filter(self):
        """Test getting all tools without filter."""
        self.registry.register_tool(self.test_tool)
        tools = self.registry.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
    
    def test_get_tools_with_category_filter(self):
        """Test getting tools filtered by category."""
        self.registry.register_tool(self.test_tool)
        tools = self.registry.get_tools(category="testing")
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
        
        # Test with non-matching category
        tools = self.registry.get_tools(category="development")
        assert len(tools) == 0
    
    def test_get_tools_with_tags_filter(self):
        """Test getting tools filtered by tags."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        tools = self.registry.get_tools(tags=["test"])
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
        
        # Test with non-matching tags
        tools = self.registry.get_tools(tags=["non_existent"])
        assert len(tools) == 0
    
    def test_get_tool_metadata_success(self):
        """Test getting tool metadata."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata is not None
        assert metadata.author == "Test Author"
    
    def test_get_tool_metadata_not_found(self):
        """Test getting metadata for non-existent tool."""
        metadata = self.registry.get_tool_metadata("non_existent")
        assert metadata is None
    
    def test_update_tool_metadata_success(self):
        """Test updating tool metadata."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        updated_metadata = ToolMetadata(
            name="test_tool",
            description="Updated description",
            version="2.0.0",
            category="testing",
            author="Updated Author",
            tags=["updated"],
            dependencies=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        success = self.registry.update_tool_metadata("test_tool", updated_metadata)
        assert success is True
        
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.description == "Updated description"
        assert metadata.author == "Updated Author"
    
    def test_update_tool_metadata_not_found(self):
        """Test updating metadata for non-existent tool."""
        success = self.registry.update_tool_metadata("non_existent", self.test_metadata)
        assert success is False
    
    def test_get_categories(self):
        """Test getting all categories."""
        categories = self.registry.get_categories()
        assert isinstance(categories, dict)
        assert len(categories) == len(ToolCategory)
        # Should return a copy, not the original
        assert categories is not self.registry.categories
    
    def test_get_tags(self):
        """Test getting all tags."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        tags = self.registry.get_tags()
        assert isinstance(tags, dict)
        assert "test" in tags
        assert "validation" in tags
        # Should return a copy, not the original
        assert tags is not self.registry.tags
    
    def test_search_tools_by_name(self):
        """Test searching tools by name."""
        self.registry.register_tool(self.test_tool)
        results = self.registry.search_tools("test")
        assert len(results) == 1
        assert results[0].name == "test_tool"
    
    def test_search_tools_by_description(self):
        """Test searching tools by description."""
        self.registry.register_tool(self.test_tool)
        results = self.registry.search_tools("validation")
        assert len(results) == 1
        assert results[0].name == "test_tool"
    
    def test_search_tools_by_tags(self):
        """Test searching tools by tags."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        results = self.registry.search_tools("test")
        assert len(results) == 1
        assert results[0].name == "test_tool"
    
    def test_search_tools_no_results(self):
        """Test searching tools with no results."""
        self.registry.register_tool(self.test_tool)
        results = self.registry.search_tools("non_existent")
        assert len(results) == 0
    
    def test_search_tools_case_insensitive(self):
        """Test case-insensitive search."""
        self.registry.register_tool(self.test_tool)
        results = self.registry.search_tools("TEST")
        assert len(results) == 1
        assert results[0].name == "test_tool"
    
    def test_get_usage_statistics_success(self):
        """Test getting usage statistics."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        stats = self.registry.get_usage_statistics("test_tool")
        assert "name" in stats
        assert "usage_count" in stats
        assert "success_rate" in stats
        assert stats["name"] == "test_tool"
    
    def test_get_usage_statistics_not_found(self):
        """Test getting usage statistics for non-existent tool."""
        stats = self.registry.get_usage_statistics("non_existent")
        assert stats == {}
    
    def test_record_tool_usage_success(self):
        """Test recording tool usage."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        # Record successful usage
        success = self.registry.record_tool_usage("test_tool", True)
        assert success is True
        
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.usage_count == 1
        assert metadata.success_rate == 1.0
        assert metadata.last_used is not None
    
    def test_record_tool_usage_failure(self):
        """Test recording failed tool usage."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        # Record failed usage
        success = self.registry.record_tool_usage("test_tool", False)
        assert success is True
        
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.usage_count == 1
        assert metadata.success_rate == 0.0
    
    def test_record_tool_usage_multiple(self):
        """Test recording multiple tool usages."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        # Record multiple usages
        self.registry.record_tool_usage("test_tool", True)   # 1/1 = 100%
        self.registry.record_tool_usage("test_tool", False)  # 1/2 = 50%
        self.registry.record_tool_usage("test_tool", True)   # 2/3 = 66.67%
        
        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata.usage_count == 3
        assert abs(metadata.success_rate - 2/3) < 0.01
    
    def test_record_tool_usage_not_found(self):
        """Test recording usage for non-existent tool."""
        success = self.registry.record_tool_usage("non_existent", True)
        assert success is False
    
    def test_get_popular_tools(self):
        """Test getting popular tools."""
        # Create multiple tools with different usage counts
        tool1 = MockMCPTool("tool1", "Tool 1")
        tool2 = MockMCPTool("tool2", "Tool 2")
        tool3 = MockMCPTool("tool3", "Tool 3")
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
        self.registry.register_tool(tool3)
        
        # Record usage
        self.registry.record_tool_usage("tool1", True)  # 1 usage
        self.registry.record_tool_usage("tool2", True)  # 1 usage
        self.registry.record_tool_usage("tool2", True)  # 2 usage
        self.registry.record_tool_usage("tool3", True)  # 1 usage
        self.registry.record_tool_usage("tool3", True)  # 2 usage
        self.registry.record_tool_usage("tool3", True)  # 3 usage
        
        popular = self.registry.get_popular_tools(limit=2)
        assert len(popular) == 2
        assert popular[0]["name"] == "tool3"  # Most popular
        assert popular[0]["usage_count"] == 3
        assert popular[1]["name"] == "tool2"  # Second most popular
        assert popular[1]["usage_count"] == 2
    
    def test_export_tool_registry_json(self):
        """Test exporting tool registry to JSON."""
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        export_data = self.registry.export_tool_registry("json")
        assert export_data != ""
        
        # Parse JSON to verify structure
        parsed = json.loads(export_data)
        assert "tools" in parsed
        assert "metadata" in parsed
        assert "categories" in parsed
        assert "tags" in parsed
        assert "exported_at" in parsed
        assert "test_tool" in parsed["tools"]
    
    def test_export_tool_registry_unsupported_format(self):
        """Test exporting with unsupported format."""
        export_data = self.registry.export_tool_registry("xml")
        assert export_data == ""
    
    def test_import_tool_registry_json(self):
        """Test importing tool registry from JSON."""
        # Create export data
        self.registry.register_tool(self.test_tool, metadata=self.test_metadata)
        export_data = self.registry.export_tool_registry("json")
        
        # Create new registry and import
        new_registry = MCPToolRegistry()
        success = new_registry.import_tool_registry(export_data, "json")
        assert success is True
        
        # Verify import
        metadata = new_registry.get_tool_metadata("test_tool")
        assert metadata is not None
        assert metadata.author == "Test Author"
    
    def test_import_tool_registry_unsupported_format(self):
        """Test importing with unsupported format."""
        success = self.registry.import_tool_registry("invalid", "xml")
        assert success is False
    
    def test_get_registry_statistics(self):
        """Test getting comprehensive registry statistics."""
        # Add multiple tools with different metadata
        tool1 = MockMCPTool("tool1", "Tool 1", "development")
        tool2 = MockMCPTool("tool2", "Tool 2", "testing")
        
        metadata1 = ToolMetadata(
            name="tool1",
            description="Tool 1",
            version="1.0.0",
            category="development",
            author="Test Author",
            tags=["test"],
            dependencies=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        metadata2 = ToolMetadata(
            name="tool2",
            description="Tool 2",
            version="1.0.0",
            category="testing",
            author="Test Author",
            tags=["test"],
            dependencies=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.registry.register_tool(tool1, metadata=metadata1)
        self.registry.register_tool(tool2, metadata=metadata2)
        
        # Record some usage
        self.registry.record_tool_usage("tool1", True)
        self.registry.record_tool_usage("tool2", False)
        
        stats = self.registry.get_registry_statistics()
        assert "total_tools" in stats
        assert "total_usage" in stats
        assert "average_success_rate" in stats
        assert "categories" in stats
        assert "total_tags" in stats
        assert "most_popular_tools" in stats
        assert "last_updated" in stats
        
        assert stats["total_tools"] == 2
        assert stats["total_usage"] == 2
        assert stats["average_success_rate"] == 0.5  # 1 success, 1 failure
    
    def test_get_registry_statistics_empty(self):
        """Test getting statistics for empty registry."""
        stats = self.registry.get_registry_statistics()
        assert stats["total_tools"] == 0
        assert stats["total_usage"] == 0
        assert stats["average_success_rate"] == 0

class TestToolMetadata:
    """Test ToolMetadata dataclass."""
    
    def test_tool_metadata_creation(self):
        """Test creating ToolMetadata instance."""
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool",
            version="1.0.0",
            category="testing",
            author="Test Author",
            tags=["test"],
            dependencies=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        assert metadata.name == "test_tool"
        assert metadata.description == "Test tool"
        assert metadata.version == "1.0.0"
        assert metadata.category == "testing"
        assert metadata.author == "Test Author"
        assert metadata.tags == ["test"]
        assert metadata.usage_count == 0
        assert metadata.success_rate == 0.0
        assert metadata.last_used is None
    
    def test_tool_metadata_with_optional_fields(self):
        """Test ToolMetadata with optional fields."""
        metadata = ToolMetadata(
            name="test_tool",
            description="Test tool",
            version="1.0.0",
            category="testing",
            author="Test Author",
            tags=["test"],
            dependencies=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            usage_count=10,
            success_rate=0.8,
            last_used=datetime.now(timezone.utc),
            parameters={"param1": "value1"},
            examples=[{"input": "test", "output": "result"}]
        )
        
        assert metadata.usage_count == 10
        assert metadata.success_rate == 0.8
        assert metadata.last_used is not None
        assert metadata.parameters == {"param1": "value1"}
        assert metadata.examples == [{"input": "test", "output": "result"}]

class TestToolCategory:
    """Test ToolCategory enum."""
    
    def test_tool_category_values(self):
        """Test ToolCategory enum values."""
        assert ToolCategory.SYSTEM.value == "system"
        assert ToolCategory.DATA.value == "data"
        assert ToolCategory.NETWORK.value == "network"
        assert ToolCategory.DEVELOPMENT.value == "development"
        assert ToolCategory.TESTING.value == "testing"
        assert ToolCategory.QUALITY.value == "quality"
        assert ToolCategory.DEPLOYMENT.value == "deployment"
        assert ToolCategory.DOCUMENTATION.value == "documentation"
        assert ToolCategory.CUSTOM.value == "custom"

class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_mcp_tool_registry(self):
        """Test get_mcp_tool_registry function."""
        registry = get_mcp_tool_registry()
        assert isinstance(registry, MCPToolRegistry)
    
    def test_execute_tool_success(self):
        """Test execute_tool function with success."""
        registry = MCPToolRegistry()
        test_tool = MockMCPTool("test_tool", "Test tool")
        mock_executor = Mock(return_value={"result": "success"})
        
        registry.register_tool(test_tool, executor=mock_executor)
        
        result = execute_tool("test_tool", {"param": "value"}, registry)
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["result"] == "success"
    
    def test_execute_tool_not_found(self):
        """Test execute_tool function with non-existent tool."""
        registry = MCPToolRegistry()
        result = execute_tool("non_existent", {}, registry)
        assert result["success"] is False
        assert "error" in result
        assert "Tool not found" in result["error"]
    
    def test_execute_tool_no_executor(self):
        """Test execute_tool function without executor."""
        registry = MCPToolRegistry()
        test_tool = MockMCPTool("test_tool", "Test tool")
        registry.register_tool(test_tool)  # No executor
        
        result = execute_tool("test_tool", {}, registry)
        assert result["success"] is False
        assert "error" in result
        assert "No executor found" in result["error"]
    
    def test_execute_tool_executor_exception(self):
        """Test execute_tool function with executor exception."""
        registry = MCPToolRegistry()
        test_tool = MockMCPTool("test_tool", "Test tool")
        mock_executor = Mock(side_effect=Exception("Test error"))
        
        registry.register_tool(test_tool, executor=mock_executor)
        
        result = execute_tool("test_tool", {}, registry)
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_tool = MockMCPTool("test_tool", "Test tool for validation")
        self.test_metadata = ToolMetadata(
            name="test_tool",
            description="Test tool for validation",
            version="1.0.0",
            category="testing",
            author="Test Author",
            tags=["test", "validation"],
            dependencies=["pytest"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    def test_register_tool_exception_handling(self):
        """Test exception handling during tool registration."""
        registry = MCPToolRegistry()
        
        # Mock a tool that raises an exception during validation
        with patch.object(registry, '_validate_tool', side_effect=Exception("Validation error")):
            success = registry.register_tool(self.test_tool)
            assert success is False
    
    def test_unregister_tool_exception_handling(self):
        """Test exception handling during tool unregistration."""
        registry = MCPToolRegistry()
        registry.register_tool(self.test_tool)
        
        # Mock an exception during unregistration
        with patch.object(registry, 'tools', side_effect=Exception("Unregister error")):
            success = registry.unregister_tool("test_tool")
            assert success is False
    
    def test_export_registry_exception_handling(self):
        """Test exception handling during registry export."""
        registry = MCPToolRegistry()
        
        # Mock JSON serialization error
        with patch('json.dumps', side_effect=Exception("JSON error")):
            result = registry.export_tool_registry("json")
            assert result == ""
    
    def test_import_registry_exception_handling(self):
        """Test exception handling during registry import."""
        registry = MCPToolRegistry()
        
        # Mock JSON parsing error
        with patch('json.loads', side_effect=Exception("JSON error")):
            success = registry.import_tool_registry("invalid json", "json")
            assert success is False

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_tool = MockMCPTool("test_tool", "Test tool for validation")
        self.test_metadata = ToolMetadata(
            name="test_tool",
            description="Test tool for validation",
            version="1.0.0",
            category="testing",
            author="Test Author",
            tags=["test", "validation"],
            dependencies=["pytest"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    def test_empty_search_query(self):
        """Test searching with empty query."""
        registry = MCPToolRegistry()
        registry.register_tool(self.test_tool)
        
        results = registry.search_tools("")
        assert len(results) == 1  # Should match everything
    
    def test_popular_tools_limit_zero(self):
        """Test getting popular tools with limit 0."""
        registry = MCPToolRegistry()
        registry.register_tool(self.test_tool)
        
        popular = registry.get_popular_tools(limit=0)
        assert len(popular) == 0
    
    def test_popular_tools_limit_greater_than_available(self):
        """Test getting popular tools with limit greater than available."""
        registry = MCPToolRegistry()
        registry.register_tool(self.test_tool)
        
        popular = registry.get_popular_tools(limit=10)
        assert len(popular) == 1  # Should return all available
    
    def test_usage_statistics_with_no_usage(self):
        """Test usage statistics for tool with no usage."""
        registry = MCPToolRegistry()
        registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        stats = registry.get_usage_statistics("test_tool")
        assert stats["usage_count"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["last_used"] is None
    
    def test_registry_statistics_with_single_tool(self):
        """Test registry statistics with single tool."""
        registry = MCPToolRegistry()
        registry.register_tool(self.test_tool, metadata=self.test_metadata)
        
        stats = registry.get_registry_statistics()
        assert stats["total_tools"] == 1
        assert stats["average_success_rate"] == 0.0  # No usage yet

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 