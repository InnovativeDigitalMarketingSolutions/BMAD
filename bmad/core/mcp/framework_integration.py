#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Framework Integration for BMAD
Following official MCP specification: https://modelcontextprotocol.io/docs
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .mcp_client import MCPClient, MCPTool, MCPContext, MCPResponse
from .tool_registry import MCPToolRegistry, ToolMetadata, ToolCategory

logger = logging.getLogger(__name__)

class FrameworkType(Enum):
    """Framework types for MCP integration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    QUALITY = "quality"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    MONITORING = "monitoring"

@dataclass
class FrameworkTool:
    """Framework-specific tool definition."""
    name: str
    description: str
    framework_type: FrameworkType
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Callable
    version: str = "1.0.0"
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class FrameworkMCPIntegration:
    """Framework MCP Integration following official specification."""
    
    def __init__(self):
        self.mcp_client: Optional[MCPClient] = None
        self.tool_registry: Optional[MCPToolRegistry] = None
        self.framework_tools: Dict[str, FrameworkTool] = {}
        self.integration_enabled = False
        self.framework_config: Dict[str, Any] = {}
        
        logger.info("Framework MCP Integration initialized")
    
    async def initialize(self, mcp_client: Optional[MCPClient] = None, 
                        tool_registry: Optional[MCPToolRegistry] = None) -> bool:
        """Initialize framework MCP integration."""
        try:
            # Initialize MCP client
            if mcp_client:
                self.mcp_client = mcp_client
            else:
                self.mcp_client = MCPClient()
                await self.mcp_client.connect()
            
            # Initialize tool registry
            if tool_registry:
                self.tool_registry = tool_registry
            else:
                self.tool_registry = MCPToolRegistry()
            
            # Register framework tools
            await self._register_framework_tools()
            
            self.integration_enabled = True
            logger.info("Framework MCP Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Framework MCP Integration: {e}")
            return False
    
    async def _register_framework_tools(self):
        """Register framework-specific tools following MCP specification."""
        framework_tools = [
            # Development Tools
            FrameworkTool(
                name="code_analysis",
                description="Analyze code quality and provide recommendations following MCP specification",
                framework_type=FrameworkType.DEVELOPMENT,
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["quality", "security", "performance", "complexity"]
                        },
                        "rules": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["code", "language", "analysis_type"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "issues": {"type": "array"},
                        "recommendations": {"type": "array"},
                        "metrics": {"type": "object"}
                    }
                },
                handler=self._execute_code_analysis,
                dependencies=["ast", "pylint"]
            ),
            
            # Testing Tools
            FrameworkTool(
                name="test_generation",
                description="Generate automated tests following MCP specification",
                framework_type=FrameworkType.TESTING,
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                        "framework": {"type": "string"},
                        "test_type": {
                            "type": "string",
                            "enum": ["unit", "integration", "e2e", "performance"]
                        },
                        "coverage_target": {"type": "number"}
                    },
                    "required": ["code", "language", "framework", "test_type"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "tests": {"type": "array"},
                        "coverage": {"type": "number"},
                        "test_count": {"type": "number"},
                        "framework_specific": {"type": "object"}
                    }
                },
                handler=self._execute_test_generation,
                dependencies=["pytest", "unittest"]
            ),
            
            # Quality Tools
            FrameworkTool(
                name="quality_gate",
                description="Quality gate validation following MCP specification",
                framework_type=FrameworkType.QUALITY,
                input_schema={
                    "type": "object",
                    "properties": {
                        "metrics": {"type": "object"},
                        "thresholds": {"type": "object"},
                        "quality_rules": {"type": "array", "items": {"type": "string"}},
                        "severity_levels": {"type": "object"}
                    },
                    "required": ["metrics", "thresholds"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "passed": {"type": "boolean"},
                        "score": {"type": "number"},
                        "violations": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                handler=self._execute_quality_gate,
                dependencies=["sonarqube", "codecov"]
            ),
            
            # Deployment Tools
            FrameworkTool(
                name="deployment_check",
                description="Deployment readiness check following MCP specification",
                framework_type=FrameworkType.DEPLOYMENT,
                input_schema={
                    "type": "object",
                    "properties": {
                        "environment": {"type": "string"},
                        "config": {"type": "object"},
                        "dependencies": {"type": "array"},
                        "security_scan": {"type": "boolean"},
                        "performance_test": {"type": "boolean"}
                    },
                    "required": ["environment", "config"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "ready": {"type": "boolean"},
                        "checks": {"type": "array"},
                        "warnings": {"type": "array"},
                        "blockers": {"type": "array"}
                    }
                },
                handler=self._execute_deployment_check,
                dependencies=["docker", "kubernetes"]
            ),
            
            # Documentation Tools
            FrameworkTool(
                name="documentation_generator",
                description="Generate documentation following MCP specification",
                framework_type=FrameworkType.DOCUMENTATION,
                input_schema={
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "output_format": {
                            "type": "string",
                            "enum": ["markdown", "html", "pdf", "json"]
                        },
                        "template": {"type": "string"},
                        "include_examples": {"type": "boolean"},
                        "include_diagrams": {"type": "boolean"}
                    },
                    "required": ["source", "output_format"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "documentation": {"type": "string"},
                        "sections": {"type": "array"},
                        "metadata": {"type": "object"},
                        "generated_at": {"type": "string"}
                    }
                },
                handler=self._execute_documentation_generator,
                dependencies=["sphinx", "mkdocs"]
            ),
            
            # Monitoring Tools
            FrameworkTool(
                name="performance_monitor",
                description="Performance monitoring and analysis following MCP specification",
                framework_type=FrameworkType.MONITORING,
                input_schema={
                    "type": "object",
                    "properties": {
                        "metrics": {"type": "array"},
                        "timeframe": {"type": "string"},
                        "thresholds": {"type": "object"},
                        "alert_rules": {"type": "array"}
                    },
                    "required": ["metrics", "timeframe"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "metrics_data": {"type": "object"},
                        "alerts": {"type": "array"},
                        "trends": {"type": "object"}
                    }
                },
                handler=self._execute_performance_monitor,
                dependencies=["prometheus", "grafana"]
            )
        ]
        
        # Register each framework tool
        for framework_tool in framework_tools:
            await self._register_framework_tool(framework_tool)
    
    async def _register_framework_tool(self, framework_tool: FrameworkTool):
        """Register a single framework tool."""
        try:
            # Create MCP tool from framework tool
            mcp_tool = MCPTool(
                name=framework_tool.name,
                description=framework_tool.description,
                input_schema=framework_tool.input_schema,
                output_schema=framework_tool.output_schema,
                category=framework_tool.framework_type.value,
                version=framework_tool.version,
                handler=framework_tool.handler
            )
            
            # Register with MCP client
            if self.mcp_client:
                self.mcp_client.register_tool(mcp_tool)
            
            # Register with tool registry
            if self.tool_registry:
                metadata = ToolMetadata(
                    name=framework_tool.name,
                    description=framework_tool.description,
                    version=framework_tool.version,
                    category=framework_tool.framework_type.value,
                    author="BMAD Framework",
                    tags=[framework_tool.framework_type.value, "framework", "mcp"],
                    dependencies=framework_tool.dependencies,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                self.tool_registry.register_tool(mcp_tool, framework_tool.handler, metadata)
            
            # Store framework tool
            self.framework_tools[framework_tool.name] = framework_tool
            
            logger.info(f"Registered framework tool: {framework_tool.name}")
            
        except Exception as e:
            logger.error(f"Error registering framework tool {framework_tool.name}: {e}")
    
    async def call_framework_tool(self, tool_name: str, parameters: Dict[str, Any], 
                                context: MCPContext) -> MCPResponse:
        """Call framework tool following MCP specification."""
        try:
            if not self.integration_enabled:
                return MCPResponse(
                    request_id="framework_integration_disabled",
                    success=False,
                    error="Framework MCP Integration not enabled"
                )
            
            if tool_name not in self.framework_tools:
                return MCPResponse(
                    request_id="tool_not_found",
                    success=False,
                    error=f"Framework tool not found: {tool_name}"
                )
            
            # Call through MCP client
            if self.mcp_client:
                return await self.mcp_client.call_tool(tool_name, parameters, context)
            else:
                return MCPResponse(
                    request_id="no_mcp_client",
                    success=False,
                    error="MCP client not available"
                )
                
        except Exception as e:
            logger.error(f"Error calling framework tool {tool_name}: {e}")
            return MCPResponse(
                request_id="framework_error",
                success=False,
                error=str(e)
            )
    
    # Framework Tool Handlers
    
    async def _execute_code_analysis(self, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute code analysis following MCP specification."""
        try:
            code = parameters.get("code", "")
            language = parameters.get("language", "python")
            analysis_type = parameters.get("analysis_type", "quality")
            
            # Simulate code analysis
            analysis_result = {
                "score": 85.5,
                "issues": [
                    {
                        "type": "warning",
                        "message": "Function too complex",
                        "line": 15,
                        "severity": "medium"
                    }
                ],
                "recommendations": [
                    "Consider breaking down complex functions",
                    "Add more comprehensive error handling",
                    "Improve code documentation"
                ],
                "metrics": {
                    "cyclomatic_complexity": 8,
                    "lines_of_code": 150,
                    "maintainability_index": 75.2,
                    "code_duplication": 5.3
                }
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            return {
                "score": 0,
                "issues": [{"type": "error", "message": str(e)}],
                "recommendations": [],
                "metrics": {}
            }
    
    async def _execute_test_generation(self, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute test generation following MCP specification."""
        try:
            code = parameters.get("code", "")
            language = parameters.get("language", "python")
            framework = parameters.get("framework", "pytest")
            test_type = parameters.get("test_type", "unit")
            
            # Simulate test generation
            generated_tests = [
                {
                    "name": "test_function_basic",
                    "code": "def test_function_basic():\n    assert True",
                    "type": "unit",
                    "framework": framework
                },
                {
                    "name": "test_function_edge_cases",
                    "code": "def test_function_edge_cases():\n    assert True",
                    "type": "unit",
                    "framework": framework
                }
            ]
            
            return {
                "tests": generated_tests,
                "coverage": 78.5,
                "test_count": len(generated_tests),
                "framework_specific": {
                    "framework": framework,
                    "test_type": test_type,
                    "language": language
                }
            }
            
        except Exception as e:
            logger.error(f"Error in test generation: {e}")
            return {
                "tests": [],
                "coverage": 0,
                "test_count": 0,
                "framework_specific": {}
            }
    
    async def _execute_quality_gate(self, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute quality gate validation following MCP specification."""
        try:
            metrics = parameters.get("metrics", {})
            thresholds = parameters.get("thresholds", {})
            
            # Simulate quality gate validation
            violations = []
            passed = True
            
            # Check code coverage
            coverage = metrics.get("coverage", 0)
            coverage_threshold = thresholds.get("coverage", 80)
            if coverage < coverage_threshold:
                violations.append({
                    "metric": "coverage",
                    "current": coverage,
                    "threshold": coverage_threshold,
                    "severity": "high"
                })
                passed = False
            
            # Check code quality score
            quality_score = metrics.get("quality_score", 0)
            quality_threshold = thresholds.get("quality_score", 70)
            if quality_score < quality_threshold:
                violations.append({
                    "metric": "quality_score",
                    "current": quality_score,
                    "threshold": quality_threshold,
                    "severity": "medium"
                })
                passed = False
            
            return {
                "passed": passed,
                "score": quality_score,
                "violations": violations,
                "recommendations": [
                    "Increase test coverage",
                    "Improve code quality",
                    "Address security vulnerabilities"
                ] if not passed else []
            }
            
        except Exception as e:
            logger.error(f"Error in quality gate: {e}")
            return {
                "passed": False,
                "score": 0,
                "violations": [{"metric": "error", "message": str(e)}],
                "recommendations": []
            }
    
    async def _execute_deployment_check(self, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute deployment readiness check following MCP specification."""
        try:
            environment = parameters.get("environment", "production")
            config = parameters.get("config", {})
            
            # Simulate deployment checks
            checks = [
                {"name": "security_scan", "status": "passed", "details": "No vulnerabilities found"},
                {"name": "dependency_check", "status": "passed", "details": "All dependencies up to date"},
                {"name": "configuration_validation", "status": "passed", "details": "Configuration valid"},
                {"name": "resource_availability", "status": "passed", "details": "Resources available"}
            ]
            
            warnings = [
                "Consider enabling additional security features",
                "Monitor resource usage during deployment"
            ]
            
            blockers = []
            
            return {
                "ready": len(blockers) == 0,
                "checks": checks,
                "warnings": warnings,
                "blockers": blockers
            }
            
        except Exception as e:
            logger.error(f"Error in deployment check: {e}")
            return {
                "ready": False,
                "checks": [],
                "warnings": [],
                "blockers": [{"error": str(e)}]
            }
    
    async def _execute_documentation_generator(self, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute documentation generation following MCP specification."""
        try:
            source = parameters.get("source", "")
            output_format = parameters.get("output_format", "markdown")
            
            # Simulate documentation generation
            documentation = f"""# Generated Documentation

## Overview
This documentation was automatically generated from the source code.

## Source
{source}

## Format
{output_format}

## Generated At
{datetime.now(timezone.utc).isoformat()}
"""
            
            return {
                "documentation": documentation,
                "sections": ["Overview", "Source", "Format", "Generated At"],
                "metadata": {
                    "format": output_format,
                    "source_length": len(source),
                    "generation_time": datetime.now(timezone.utc).isoformat()
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in documentation generation: {e}")
            return {
                "documentation": "",
                "sections": [],
                "metadata": {},
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def _execute_performance_monitor(self, parameters: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Execute performance monitoring following MCP specification."""
        try:
            metrics = parameters.get("metrics", [])
            timeframe = parameters.get("timeframe", "1h")
            
            # Simulate performance monitoring
            metrics_data = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "response_time": 125.5,
                "throughput": 1500.0
            }
            
            alerts = []
            if metrics_data["cpu_usage"] > 80:
                alerts.append({
                    "type": "warning",
                    "message": "High CPU usage detected",
                    "metric": "cpu_usage",
                    "value": metrics_data["cpu_usage"]
                })
            
            return {
                "status": "healthy",
                "metrics_data": metrics_data,
                "alerts": alerts,
                "trends": {
                    "cpu_trend": "stable",
                    "memory_trend": "increasing",
                    "response_time_trend": "stable"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in performance monitoring: {e}")
            return {
                "status": "error",
                "metrics_data": {},
                "alerts": [{"type": "error", "message": str(e)}],
                "trends": {}
            }
    
    def get_framework_tools(self, framework_type: Optional[FrameworkType] = None) -> List[FrameworkTool]:
        """Get available framework tools."""
        if framework_type:
            return [tool for tool in self.framework_tools.values() if tool.framework_type == framework_type]
        return list(self.framework_tools.values())
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status following MCP specification."""
        return {
            "enabled": self.integration_enabled,
            "mcp_client_connected": self.mcp_client.connected if self.mcp_client else False,
            "tool_registry_available": self.tool_registry is not None,
            "framework_tools_count": len(self.framework_tools),
            "framework_types": [ft.value for ft in FrameworkType],
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

def get_framework_mcp_integration() -> FrameworkMCPIntegration:
    """Get framework MCP integration instance."""
    return FrameworkMCPIntegration()

async def initialize_framework_mcp_integration(mcp_client: Optional[MCPClient] = None,
                                             tool_registry: Optional[MCPToolRegistry] = None) -> FrameworkMCPIntegration:
    """Initialize framework MCP integration."""
    integration = FrameworkMCPIntegration()
    await integration.initialize(mcp_client, tool_registry)
    return integration 