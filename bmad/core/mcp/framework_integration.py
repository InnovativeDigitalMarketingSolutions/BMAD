#!/usr/bin/env python3
"""
MCP Integration for Framework Templates
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from .mcp_client import MCPClient, MCPTool, MCPContext, MCPResponse
from .tool_registry import MCPToolRegistry, ToolMetadata, register_tool, get_tool_registry, execute_tool

logger = logging.getLogger(__name__)

class FrameworkMCPIntegration:
    """MCP Integration for Framework Templates."""
    
    def __init__(self):
        self.mcp_client: Optional[MCPClient] = None
        self.tool_registry: Optional[MCPToolRegistry] = None
        self.framework_tools: Dict[str, MCPTool] = {}
        self.integration_enabled = False
        
        logger.info("Framework MCP Integration initialized")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize MCP integration."""
        try:
            # Initialize MCP client
            self.mcp_client = MCPClient(config)
            await self.mcp_client.connect()
            
            # Initialize tool registry
            self.tool_registry = get_tool_registry()
            
            # Register framework-specific tools
            await self._register_framework_tools()
            
            self.integration_enabled = True
            logger.info("Framework MCP Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Framework MCP Integration: {e}")
            return False
    
    async def _register_framework_tools(self):
        """Register framework-specific MCP tools."""
        framework_tools = [
            # Development Tools
            MCPTool(
                name="code_analysis",
                description="Code analysis and quality assessment",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                        "analysis_type": {"type": "string", "enum": ["quality", "security", "performance"]}
                    },
                    "required": ["code", "language"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "score": {"type": "number"},
                        "issues": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                category="development"
            ),
            
            # Testing Tools
            MCPTool(
                name="test_generation",
                description="Automated test generation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                        "framework": {"type": "string"},
                        "test_type": {"type": "string", "enum": ["unit", "integration", "e2e"]}
                    },
                    "required": ["code", "language"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "tests": {"type": "array"},
                        "coverage": {"type": "number"}
                    }
                },
                category="development"
            ),
            
            # Quality Tools
            MCPTool(
                name="quality_gate",
                description="Quality gate validation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code_changes": {"type": "array"},
                        "quality_threshold": {"type": "number"},
                        "checks": {"type": "array"}
                    },
                    "required": ["code_changes"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "passed": {"type": "boolean"},
                        "score": {"type": "number"},
                        "violations": {"type": "array"}
                    }
                },
                category="monitoring"
            ),
            
            # Deployment Tools
            MCPTool(
                name="deployment_check",
                description="Deployment readiness check",
                input_schema={
                    "type": "object",
                    "properties": {
                        "application": {"type": "string"},
                        "environment": {"type": "string"},
                        "checks": {"type": "array"}
                    },
                    "required": ["application", "environment"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "ready": {"type": "boolean"},
                        "issues": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                category="development"
            ),
            
            # Documentation Tools
            MCPTool(
                name="documentation_generator",
                description="Automated documentation generation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                        "doc_type": {"type": "string", "enum": ["api", "code", "user"]}
                    },
                    "required": ["code", "language"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "documentation": {"type": "string"},
                        "format": {"type": "string"}
                    }
                },
                category="development"
            )
        ]
        
        # Register tools with executors
        for tool in framework_tools:
            metadata = ToolMetadata(
                name=tool.name,
                description=tool.description,
                version=tool.version,
                category=tool.category,
                author="BMAD Framework",
                tags=["framework", "automation"],
                dependencies=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Get appropriate executor
            executor = self._get_tool_executor(tool.name)
            
            # Register tool
            success = register_tool(tool, executor, metadata)
            if success:
                self.framework_tools[tool.name] = tool
                logger.info(f"Registered framework tool: {tool.name}")
            else:
                logger.error(f"Failed to register framework tool: {tool.name}")
    
    def _get_tool_executor(self, tool_name: str):
        """Get executor function for a tool."""
        executors = {
            "code_analysis": self._execute_code_analysis,
            "test_generation": self._execute_test_generation,
            "quality_gate": self._execute_quality_gate,
            "deployment_check": self._execute_deployment_check,
            "documentation_generator": self._execute_documentation_generator
        }
        return executors.get(tool_name, self._execute_default_tool)
    
    async def _execute_code_analysis(self, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
        """Execute code analysis tool."""
        try:
            code = parameters.get("code", "")
            language = parameters.get("language", "python")
            analysis_type = parameters.get("analysis_type", "quality")
            
            # Simulate code analysis
            score = 85.0  # Simulated quality score
            issues = [
                {"type": "warning", "message": "Consider adding type hints", "line": 10},
                {"type": "info", "message": "Function is well documented", "line": 15}
            ]
            recommendations = [
                "Add type hints to improve code quality",
                "Consider breaking down large functions"
            ]
            
            return MCPResponse(
                request_id=f"code_analysis_{datetime.utcnow().timestamp()}",
                success=True,
                data={
                    "score": score,
                    "issues": issues,
                    "recommendations": recommendations,
                    "language": language,
                    "analysis_type": analysis_type
                },
                metadata={"tool": "code_analysis", "context": context.agent_id}
            )
            
        except Exception as e:
            return MCPResponse(
                request_id=f"code_analysis_{datetime.utcnow().timestamp()}",
                success=False,
                error=str(e)
            )
    
    async def _execute_test_generation(self, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
        """Execute test generation tool."""
        try:
            code = parameters.get("code", "")
            language = parameters.get("language", "python")
            framework = parameters.get("framework", "pytest")
            test_type = parameters.get("test_type", "unit")
            
            # Simulate test generation
            tests = [
                f"def test_function_{i}():\n    # Generated test for {language}\n    assert True" 
                for i in range(3)
            ]
            coverage = 75.0
            
            return MCPResponse(
                request_id=f"test_generation_{datetime.utcnow().timestamp()}",
                success=True,
                data={
                    "tests": tests,
                    "coverage": coverage,
                    "language": language,
                    "framework": framework,
                    "test_type": test_type
                },
                metadata={"tool": "test_generation", "context": context.agent_id}
            )
            
        except Exception as e:
            return MCPResponse(
                request_id=f"test_generation_{datetime.utcnow().timestamp()}",
                success=False,
                error=str(e)
            )
    
    async def _execute_quality_gate(self, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
        """Execute quality gate tool."""
        try:
            code_changes = parameters.get("code_changes", [])
            quality_threshold = parameters.get("quality_threshold", 80.0)
            checks = parameters.get("checks", ["linting", "testing", "security"])
            
            # Simulate quality gate check
            score = 87.5
            passed = score >= quality_threshold
            violations = [] if passed else [
                {"type": "quality", "message": "Code quality below threshold", "severity": "medium"}
            ]
            
            return MCPResponse(
                request_id=f"quality_gate_{datetime.utcnow().timestamp()}",
                success=True,
                data={
                    "passed": passed,
                    "score": score,
                    "violations": violations,
                    "threshold": quality_threshold,
                    "checks": checks
                },
                metadata={"tool": "quality_gate", "context": context.agent_id}
            )
            
        except Exception as e:
            return MCPResponse(
                request_id=f"quality_gate_{datetime.utcnow().timestamp()}",
                success=False,
                error=str(e)
            )
    
    async def _execute_deployment_check(self, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
        """Execute deployment check tool."""
        try:
            application = parameters.get("application", "")
            environment = parameters.get("environment", "production")
            checks = parameters.get("checks", ["tests", "security", "performance"])
            
            # Simulate deployment check
            ready = True
            issues = []
            recommendations = [
                "All tests passing",
                "Security scan completed",
                "Performance benchmarks met"
            ]
            
            return MCPResponse(
                request_id=f"deployment_check_{datetime.utcnow().timestamp()}",
                success=True,
                data={
                    "ready": ready,
                    "issues": issues,
                    "recommendations": recommendations,
                    "application": application,
                    "environment": environment
                },
                metadata={"tool": "deployment_check", "context": context.agent_id}
            )
            
        except Exception as e:
            return MCPResponse(
                request_id=f"deployment_check_{datetime.utcnow().timestamp()}",
                success=False,
                error=str(e)
            )
    
    async def _execute_documentation_generator(self, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
        """Execute documentation generator tool."""
        try:
            code = parameters.get("code", "")
            language = parameters.get("language", "python")
            doc_type = parameters.get("doc_type", "api")
            
            # Simulate documentation generation
            documentation = f"""
# Generated Documentation for {language}

## Overview
This documentation was automatically generated from the provided code.

## API Reference
- Function: `example_function`
- Parameters: `param1`, `param2`
- Returns: `result`

## Usage Examples
```{language}
result = example_function(param1, param2)
```
            """.strip()
            
            return MCPResponse(
                request_id=f"doc_generation_{datetime.utcnow().timestamp()}",
                success=True,
                data={
                    "documentation": documentation,
                    "format": "markdown",
                    "language": language,
                    "doc_type": doc_type
                },
                metadata={"tool": "documentation_generator", "context": context.agent_id}
            )
            
        except Exception as e:
            return MCPResponse(
                request_id=f"doc_generation_{datetime.utcnow().timestamp()}",
                success=False,
                error=str(e)
            )
    
    async def _execute_default_tool(self, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
        """Default tool executor."""
        return MCPResponse(
            request_id=f"default_{datetime.utcnow().timestamp()}",
            success=True,
            data={"message": "Default tool executed successfully"},
            metadata={"tool": "default", "context": context.agent_id}
        )
    
    async def call_framework_tool(self, 
                                 tool_name: str,
                                 parameters: Dict[str, Any],
                                 context: MCPContext) -> MCPResponse:
        """Call a framework-specific tool."""
        if not self.integration_enabled:
            return MCPResponse(
                request_id=f"disabled_{datetime.utcnow().timestamp()}",
                success=False,
                error="MCP Integration not enabled"
            )
        
        if tool_name not in self.framework_tools:
            return MCPResponse(
                request_id=f"not_found_{datetime.utcnow().timestamp()}",
                success=False,
                error=f"Framework tool {tool_name} not found"
            )
        
        return await execute_tool(tool_name, parameters, context)
    
    def get_available_framework_tools(self) -> List[MCPTool]:
        """Get all available framework tools."""
        return list(self.framework_tools.values())
    
    def get_framework_tools_by_category(self, category: str) -> List[MCPTool]:
        """Get framework tools by category."""
        return [tool for tool in self.framework_tools.values() if tool.category == category]
    
    async def shutdown(self) -> bool:
        """Shutdown MCP integration."""
        try:
            if self.mcp_client:
                await self.mcp_client.disconnect()
            
            self.integration_enabled = False
            logger.info("Framework MCP Integration shutdown successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down Framework MCP Integration: {e}")
            return False

# Global framework MCP integration instance
_framework_mcp_integration: Optional[FrameworkMCPIntegration] = None

def get_framework_mcp_integration() -> FrameworkMCPIntegration:
    """Get global framework MCP integration instance."""
    global _framework_mcp_integration
    if _framework_mcp_integration is None:
        _framework_mcp_integration = FrameworkMCPIntegration()
    return _framework_mcp_integration

async def initialize_framework_mcp_integration(config: Optional[Dict[str, Any]] = None) -> FrameworkMCPIntegration:
    """Initialize framework MCP integration."""
    integration = get_framework_mcp_integration()
    await integration.initialize(config)
    return integration

async def call_framework_tool(tool_name: str, parameters: Dict[str, Any], context: MCPContext) -> MCPResponse:
    """Call a framework tool."""
    integration = get_framework_mcp_integration()
    return await integration.call_framework_tool(tool_name, parameters, context) 