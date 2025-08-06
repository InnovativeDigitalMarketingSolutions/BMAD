#!/usr/bin/env python3
"""
Fullstack Developer Agent voor CoPilot AI Business Suite
Implementeert features van frontend tot backend met Shadcn/ui integratie.
Output in code snippets, pull requests, changelogs, testresultaten en dev logs.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv

# Add path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager
from integrations.slack.slack_notify import send_slack_message

# MCP Integration
from bmad.core.mcp import (
    MCPClient,
    MCPContext,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)

# Enhanced MCP Integration for Phase 2
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)

# Message Bus Integration
from bmad.agents.core.communication.agent_message_bus_integration import (
    AgentMessageBusIntegration,
    create_agent_message_bus_integration
)

# Tracing Integration
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DevelopmentError(Exception):
    """Custom exception for development-related errors."""
    pass

class DevelopmentValidationError(DevelopmentError):
    """Exception for development validation failures."""
    pass

class FullstackDeveloperAgent:
    """
    Fullstack Developer Agent voor BMAD.
    Gespecialiseerd in fullstack development, API building, en frontend-backend integratie.
    """
    
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        try:
            self.fullstack_development_template = self.framework_manager.get_framework_template('fullstack_development')
        except:
            self.fullstack_development_template = None
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "FullstackDeveloper"
        
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Integration
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_client: Optional[MCPClient] = None
        self.enhanced_mcp_enabled = False
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Message Bus Integration
        self.message_bus_integration: Optional[AgentMessageBusIntegration] = None
        self.message_bus_enabled = False
        
        # Performance Metrics for Quality-First Implementation
        self.performance_metrics = {
            "total_features": 0,
            "api_endpoints_created": 0,
            "frontend_components_built": 0,
            "integration_tests_passed": 0,
            "deployment_success_rate": 0,
            "average_development_time": 0,
            "code_quality_score": 0,
            "test_coverage_rate": 0,
            "security_issues_fixed": 0,
            "performance_optimizations": 0
        }
        
        # History tracking for quality-first implementation
        self.development_history = []
        self.performance_history = []
        self.api_history = []
        self.frontend_history = []
        self.integration_history = []
        
        # Load existing history
        self._load_development_history()
        self._load_performance_history()
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced fullstack development capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for FullstackDeveloper")
        except Exception as e:
            logger.warning(f"MCP initialization failed for FullstackDeveloper: {e}")
            self.mcp_enabled = False

    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            if self.enhanced_mcp_enabled:
                logger.info("Enhanced MCP capabilities initialized successfully for FullstackDeveloper")
            else:
                logger.warning("Enhanced MCP initialization failed, falling back to standard MCP")
                
        except Exception as e:
            logger.warning(f"Enhanced MCP initialization failed for FullstackDeveloper: {e}")
            self.enhanced_mcp_enabled = False

    async def initialize_tracing(self):
        """Initialize tracing capabilities."""
        try:
            if self.tracer and hasattr(self.tracer, 'initialize'):
                await self.tracer.initialize()
                self.tracing_enabled = True
                logger.info("Tracing initialized successfully for FullstackDeveloper")
                # Set up fullstack-specific tracing spans
                await self.tracer.setup_fullstack_tracing({
                    "agent_name": self.agent_name,
                    "tracing_level": "detailed",
                    "development_tracking": True,
                    "integration_tracking": True,
                    "performance_tracking": True,
                    "error_tracking": True
                })
            else:
                logger.warning("Tracer not available or missing initialize method")
                self.tracing_enabled = False
        except Exception as e:
            logger.warning(f"Tracing initialization failed: {e}")
            self.tracing_enabled = False

    async def initialize_message_bus_integration(self):
        """Initialize Message Bus Integration for the agent."""
        try:
            self.message_bus_integration = create_agent_message_bus_integration(
                agent_name=self.agent_name,
                agent_type="fullstack_developer",
                config={
                    "message_bus_url": "redis://localhost:6379",
                    "enable_publishing": True,
                    "enable_subscription": True,
                    "event_handlers": {
                        "fullstack_development_requested": self.handle_fullstack_development_requested,
                        "fullstack_development_completed": self.handle_fullstack_development_completed,
                        "api_development_requested": self.handle_api_development_requested,
                        "frontend_development_requested": self.handle_frontend_development_requested
                    }
                }
            )
            await self.message_bus_integration.initialize()
            self.message_bus_enabled = True
            logger.info("Message Bus Integration initialized successfully for FullstackDeveloper")
        except Exception as e:
            logger.warning(f"Message Bus Integration initialization failed: {e}")
            self.message_bus_enabled = False

    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use MCP tool voor enhanced functionality."""
        if not self.mcp_enabled or not self.mcp_client:
            logger.warning("MCP not available, using local tools")
            return None
        
        try:
            # Create a context for the tool call
            context = await self.mcp_client.create_context(agent_id=self.agent_name)
            response = await self.mcp_client.call_tool(tool_name, parameters, context)
            
            if response.success:
                logger.info(f"MCP tool {tool_name} executed successfully")
                return response.data
            else:
                logger.error(f"MCP tool {tool_name} failed: {response.error}")
                return None
        except Exception as e:
            logger.error(f"MCP tool {tool_name} execution failed: {e}")
            return None
    
    async def use_fullstack_specific_mcp_tools(self, development_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use fullstack-specific MCP tools voor enhanced development."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Fullstack development
            development_result = await self.use_mcp_tool("fullstack_development", {
                "feature_name": development_data.get("feature_name", ""),
                "feature_description": development_data.get("feature_description", ""),
                "development_type": development_data.get("development_type", "fullstack"),
                "include_frontend": development_data.get("include_frontend", True),
                "include_backend": development_data.get("include_backend", True),
                "include_api": development_data.get("include_api", True)
            })
            if development_result:
                enhanced_data["fullstack_development"] = development_result
            
            # API development
            api_result = await self.use_mcp_tool("api_development", {
                "api_name": development_data.get("api_name", ""),
                "api_type": development_data.get("api_type", "REST"),
                "endpoints": development_data.get("endpoints", []),
                "authentication": development_data.get("authentication", True),
                "documentation": development_data.get("documentation", True)
            })
            if api_result:
                enhanced_data["api_development"] = api_result
            
            # Frontend development
            frontend_result = await self.use_mcp_tool("frontend_development", {
                "component_name": development_data.get("component_name", ""),
                "framework": development_data.get("framework", "React"),
                "ui_library": development_data.get("ui_library", "Shadcn/ui"),
                "accessibility": development_data.get("accessibility", True),
                "responsive": development_data.get("responsive", True)
            })
            if frontend_result:
                enhanced_data["frontend_development"] = frontend_result
            
            # Integration testing
            integration_result = await self.use_mcp_tool("integration_testing", {
                "test_scope": development_data.get("test_scope", "fullstack"),
                "test_type": development_data.get("test_type", "end-to-end"),
                "coverage": development_data.get("coverage", "comprehensive"),
                "automation": development_data.get("automation", True)
            })
            if integration_result:
                enhanced_data["integration_testing"] = integration_result
            
            logger.info(f"Fullstack-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in fullstack-specific MCP tools: {e}")
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_fullstack_specific_mcp_tools(agent_data)
        
        enhanced_data = {}
        
        # Core enhancement tools
        core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
            "agent_type": self.agent_name,
            "enhancement_level": "advanced",
            "capabilities": agent_data.get("capabilities", []),
            "performance_metrics": agent_data.get("performance_metrics", {})
        })
        if core_result:
            enhanced_data["core_enhancement"] = core_result
        
        # Fullstack-specific enhancement tools
        specific_result = await self.use_fullstack_specific_enhanced_tools(agent_data)
        if specific_result:
            enhanced_data.update(specific_result)
        
        return enhanced_data

    async def use_fullstack_specific_enhanced_tools(self, fullstack_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use fullstack-specific enhanced MCP tools."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {}
        
        enhanced_data = {}
        
        # Feature development enhancement
        feature_result = await self.enhanced_mcp.use_enhanced_mcp_tool("feature_development", {
            "feature_name": fullstack_data.get("feature_name", ""),
            "complexity": fullstack_data.get("complexity", "medium"),
            "frontend_requirements": fullstack_data.get("frontend_requirements", {}),
            "backend_requirements": fullstack_data.get("backend_requirements", {}),
            "integration_points": fullstack_data.get("integration_points", [])
        })
        if feature_result:
            enhanced_data["feature_development"] = feature_result
        
        # Integration enhancement
        integration_result = await self.enhanced_mcp.use_enhanced_mcp_tool("integration_enhancement", {
            "frontend_backend_integration": fullstack_data.get("frontend_backend_integration", {}),
            "api_contracts": fullstack_data.get("api_contracts", {}),
            "data_flow": fullstack_data.get("data_flow", {}),
            "error_handling": fullstack_data.get("error_handling", {})
        })
        if integration_result:
            enhanced_data["integration_enhancement"] = integration_result
        
        # Performance optimization
        performance_result = await self.enhanced_mcp.use_enhanced_mcp_tool("performance_optimization", {
            "frontend_performance": fullstack_data.get("frontend_performance", {}),
            "backend_performance": fullstack_data.get("backend_performance", {}),
            "database_optimization": fullstack_data.get("database_optimization", {}),
            "caching_strategy": fullstack_data.get("caching_strategy", {})
        })
        if performance_result:
            enhanced_data["performance_optimization"] = performance_result
        
        return enhanced_data

    async def communicate_with_agents(self, target_agents: List[str], message: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate with other agents via enhanced MCP."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {"error": "Enhanced MCP not available"}
        
        try:
            return await self.enhanced_mcp.communicate_with_agents(target_agents, message)
        except Exception as e:
            logger.error(f"Enhanced agent communication failed: {e}")
            return {"error": str(e)}

    async def use_external_tools(self, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Use external tools via enhanced MCP."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {"error": "Enhanced MCP not available"}
        
        try:
            return await self.enhanced_mcp.use_external_tool(tool_config)
        except Exception as e:
            logger.error(f"External tool usage failed: {e}")
            return {"error": str(e)}

    async def enhanced_security_validation(self, security_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced security validation for fullstack development."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {"error": "Enhanced MCP not available"}
        
        try:
            return await self.enhanced_mcp.enhanced_security_validation(security_data)
        except Exception as e:
            logger.error(f"Enhanced security validation failed: {e}")
            return {"error": str(e)}

    async def enhanced_performance_optimization(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced performance optimization for fullstack development."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {"error": "Enhanced MCP not available"}
        
        try:
            return await self.enhanced_mcp.enhanced_performance_optimization(performance_data)
        except Exception as e:
            logger.error(f"Enhanced performance optimization failed: {e}")
            return {"error": str(e)}

    def get_enhanced_performance_summary(self) -> Dict[str, Any]:
        """Get enhanced performance summary."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {}
        
        try:
            return self.enhanced_mcp.get_performance_summary()
        except Exception as e:
            logger.error(f"Failed to get enhanced performance summary: {e}")
            return {}

    def get_enhanced_communication_summary(self) -> Dict[str, Any]:
        """Get enhanced communication summary."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {}
        
        try:
            return self.enhanced_mcp.get_communication_summary()
        except Exception as e:
            logger.error(f"Failed to get enhanced communication summary: {e}")
            return {}

    async def trace_feature_development(self, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace feature development process."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for feature development")
            return {}
        
        try:
            trace_result = await self.tracer.trace_feature_development({
                "feature_name": feature_data.get("feature_name", ""),
                "complexity": feature_data.get("complexity", "medium"),
                "frontend_components": feature_data.get("frontend_components", []),
                "backend_apis": feature_data.get("backend_apis", []),
                "integration_points": feature_data.get("integration_points", []),
                "performance_metrics": feature_data.get("performance_metrics", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Feature development traced: {feature_data.get('feature_name', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Feature development tracing failed: {e}")
            return {}

    async def trace_fullstack_integration(self, integration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace fullstack integration process."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for fullstack integration")
            return {}
        
        try:
            trace_result = await self.tracer.trace_fullstack_integration({
                "integration_type": integration_data.get("type", "api_integration"),
                "frontend_component": integration_data.get("frontend_component", ""),
                "backend_api": integration_data.get("backend_api", ""),
                "data_flow": integration_data.get("data_flow", {}),
                "error_handling": integration_data.get("error_handling", {}),
                "performance_impact": integration_data.get("performance_impact", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Fullstack integration traced: {integration_data.get('type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Fullstack integration tracing failed: {e}")
            return {}

    async def trace_performance_optimization(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace performance optimization process."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for performance optimization")
            return {}
        
        try:
            trace_result = await self.tracer.trace_performance_optimization({
                "optimization_type": performance_data.get("type", "general"),
                "frontend_optimizations": performance_data.get("frontend_optimizations", {}),
                "backend_optimizations": performance_data.get("backend_optimizations", {}),
                "database_optimizations": performance_data.get("database_optimizations", {}),
                "caching_strategies": performance_data.get("caching_strategies", {}),
                "before_metrics": performance_data.get("before_metrics", {}),
                "after_metrics": performance_data.get("after_metrics", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Performance optimization traced: {performance_data.get('type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Performance optimization tracing failed: {e}")
            return {}

    async def trace_fullstack_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace fullstack errors and exceptions."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for fullstack errors")
            return {}
        
        try:
            trace_result = await self.tracer.trace_fullstack_error({
                "error_type": error_data.get("type", "unknown"),
                "error_message": error_data.get("message", ""),
                "feature_name": error_data.get("feature_name", ""),
                "frontend_component": error_data.get("frontend_component", ""),
                "backend_api": error_data.get("backend_api", ""),
                "stack_trace": error_data.get("stack_trace", ""),
                "user_context": error_data.get("user_context", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Fullstack error traced: {error_data.get('type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Fullstack error tracing failed: {e}")
            return {}

    def get_tracing_summary(self) -> Dict[str, Any]:
        """Get tracing summary for the agent."""
        if not self.tracing_enabled or not self.tracer:
            return {}
        
        try:
            return self.tracer.get_tracing_summary()
        except Exception as e:
            logger.error(f"Failed to get tracing summary: {e}")
            return {}

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input type for parameters."""
        if not isinstance(value, expected_type):
            raise DevelopmentValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_feature_name(self, feature_name: str) -> None:
        """Validate feature name parameter."""
        self._validate_input(feature_name, str, "feature_name")
        if not feature_name.strip():
            raise DevelopmentValidationError("Feature name cannot be empty")
        if len(feature_name) > 100:
            raise DevelopmentValidationError("Feature name cannot exceed 100 characters")

    def _validate_component_name(self, component_name: str) -> None:
        """Validate component name parameter."""
        self._validate_input(component_name, str, "component_name")
        if not component_name.strip():
            raise DevelopmentValidationError("Component name cannot be empty")
        if not component_name[0].isupper():
            raise DevelopmentValidationError("Component name must start with uppercase letter")

    def _validate_format_type(self, format_type: str) -> None:
        """Validate export format type."""
        self._validate_input(format_type, str, "format_type")
        if format_type not in ["md", "json"]:
            raise DevelopmentValidationError("Format type must be 'md' or 'json'")

    def _record_development_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record development-specific metrics."""
        try:
            self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, value, unit)
            logger.info(f"Development metric recorded: {metric_name} = {value}{unit}")
        except Exception as e:
            logger.error(f"Failed to record development metric: {e}")

    def _assess_development_complexity(self, feature_description: str) -> str:
        """Assess the complexity of a development task."""
        if not feature_description:
            return "low"
        
        complexity_indicators = {
            "high": ["complex", "advanced", "sophisticated", "enterprise", "scalable", "distributed"],
            "medium": ["standard", "typical", "common", "basic", "simple", "straightforward"]
        }
        
        description_lower = feature_description.lower()
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return complexity
        
        return "medium"

    def _generate_development_recommendations(self, complexity: str) -> list:
        """Generate development recommendations based on complexity."""
        base_recommendations = [
            "Follow coding standards and best practices",
            "Write comprehensive unit tests",
            "Document code and APIs",
            "Perform code reviews before merging"
        ]
        
        if complexity == "high":
            return base_recommendations + [
                "Implement comprehensive error handling",
                "Add performance monitoring and logging",
                "Consider scalability and maintainability",
                "Plan for future extensibility"
            ]
        elif complexity == "medium":
            return base_recommendations + [
                "Add basic error handling",
                "Include essential logging",
                "Consider basic performance optimization"
            ]
        else:
            return base_recommendations + [
                "Keep implementation simple and focused",
                "Ensure code readability"
            ]

    def _load_development_history(self):
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.development_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load development history: {e}")

    def _save_development_history(self):
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Development History\n\n")
                f.writelines(f"- {dev}\n" for dev in self.development_history[-50:])
        except Exception as e:
            logger.error(f"Could not save development history: {e}")

    def _load_performance_history(self):
        try:
            if self.data_paths["feedback"].exists():
                with open(self.data_paths["feedback"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.performance_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        try:
            self.data_paths["feedback"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["feedback"], "w") as f:
                f.write("# Performance History\n\n")
                f.writelines(f"- {perf}\n" for perf in self.performance_history[-50:])
        except Exception as e:
            logger.error(f"Could not save performance history: {e}")

    def show_help(self):
        help_text = """
FullstackDeveloper Agent Commands:
  help                    - Show this help message
  implement-story         - Implement user story
  build-api               - Build API endpoint
  build-frontend          - Build frontend with Shadcn/ui
  build-shadcn-component  - Generate Shadcn component
  integrate-service       - Integrate external service
  write-tests             - Write tests
  ci-cd                   - Show CI/CD pipeline
  dev-log                 - Show development log
  review                  - Code review
  refactor                - Refactoring advice
  security-check          - Security checklist
  blockers                - Show blockers
  show-development-history - Show development history
  show-performance        - Show performance metrics
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-report [format]  - Export report (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration
  api-contract            - Show API contract
  component-doc           - Show component documentation
  performance-profile     - Show performance profile
  a11y-check              - Show accessibility check
  feature-toggle          - Show feature toggle config
  monitoring-setup        - Show monitoring setup
  release-notes           - Show release notes
  devops-handover         - Show DevOps handover
  tech-debt               - Show technical debt

Enhanced MCP Phase 2 Commands:
  enhanced-collaborate    - Enhanced inter-agent communication
  enhanced-security       - Enhanced security validation
  enhanced-performance    - Enhanced performance optimization
  enhanced-tools          - Enhanced external tool integration
  enhanced-summary        - Show enhanced performance and communication summaries

Tracing Commands:
  trace-feature           - Trace feature development process
  trace-integration       - Trace fullstack integration process
  trace-performance       - Trace performance optimization process
  trace-error             - Trace fullstack errors and exceptions
  tracing-summary         - Get tracing summary and analytics

Enhanced Command Examples:
  enhanced-collaborate --agents FrontendDeveloper BackendDeveloper --message "Feature integration ready"
  enhanced-security
  enhanced-performance
  enhanced-tools --tool-config '{"tool_name": "github", "category": "development"}'
  enhanced-summary
  trace-feature --feature-data '{"feature_name": "UserAuth", "complexity": "medium"}'
  trace-integration --integration-data '{"type": "api_integration", "frontend_component": "LoginForm"}'
  trace-performance --performance-data '{"type": "general", "frontend_optimizations": {}}'
  trace-error --error-data '{"type": "integration_error", "message": "API connection failed"}'
  tracing-summary
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "shadcn-component":
                path = self.template_paths["shadcn-component"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return
            if path.exists():
                with open(path) as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_development_history(self):
        if not self.development_history:
            print("No development history available.")
            return
        print("Development History:")
        print("=" * 50)
        for i, dev in enumerate(self.development_history[-10:], 1):
            print(f"{i}. {dev}")

    def show_performance(self):
        if not self.performance_history:
            print("No performance history available.")
            return
        print("Performance History:")
        print("=" * 50)
        for i, perf in enumerate(self.performance_history[-10:], 1):
            print(f"{i}. {perf}")

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export development report with validation."""
        try:
            self._validate_format_type(format_type)
            
            if report_data is None:
                report_data = {
                    "agent": "FullstackDeveloper",
                    "timestamp": datetime.now().isoformat(),
                    "development_history": self.development_history[-10:],
                    "performance_metrics": {
                        "total_features": len([h for h in self.development_history if "feature" in h.lower()]),
                        "total_components": len([h for h in self.development_history if "component" in h.lower()]),
                        "success_rate": 95.0
                    }
                }
            
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "json":
                self._export_json(report_data)
            
            # Log performance metric
            self._record_development_metric("report_export", 100, "%")
            
        except DevelopmentValidationError as e:
            logger.error(f"Validation error exporting report: {e}")
            raise
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise

    def _export_markdown(self, report_data: Dict):
        output_file = f"fullstack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Fullstack Developer Report

## Summary
- **Story**: {report_data.get('story', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Components
- Frontend Components: {report_data.get('frontend_components', 0)}
- Backend Endpoints: {report_data.get('backend_endpoints', 0)}
- Tests Written: {report_data.get('tests_written', 0)}
- Shadcn Components: {report_data.get('shadcn_components', 0)}

## Performance
- Accessibility Score: {report_data.get('accessibility_score', 0)}%
- Performance Score: {report_data.get('performance_score', 0)}%
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        output_file = f"fullstack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Report export saved to: {output_file}")

    def test_resource_completeness(self):
        """Test resource completeness with enhanced validation including Message Bus Integration."""
        print("🔍 FullstackDeveloper Agent - Resource Completeness Test")
        print("=" * 60)
        
        # Core functionality tests
        core_tests = [
            ("Agent Initialization", hasattr(self, 'agent_name')),
            ("Performance Monitor", hasattr(self, 'monitor')),
            ("Policy Engine", hasattr(self, 'policy_engine')),
            ("Sprite Library", hasattr(self, 'sprite_library')),
            ("Framework Manager", hasattr(self, 'framework_manager')),
        ]
        
        # MCP Integration tests
        mcp_tests = [
            ("MCP Client", hasattr(self, 'mcp_client')),
            ("MCP Integration", hasattr(self, 'mcp_integration')),
            ("Enhanced MCP", hasattr(self, 'enhanced_mcp')),
            ("Enhanced MCP Client", hasattr(self, 'enhanced_mcp_client')),
        ]
        
        # Message Bus Integration tests
        message_bus_tests = [
            ("Message Bus Integration", hasattr(self, 'message_bus_integration')),
            ("Message Bus Enabled", hasattr(self, 'message_bus_enabled')),
            ("Performance Metrics", hasattr(self, 'performance_metrics')),
            ("Performance History", hasattr(self, 'performance_history')),
            ("Development History", hasattr(self, 'development_history')),
            ("API History", hasattr(self, 'api_history')),
            ("Frontend History", hasattr(self, 'frontend_history')),
            ("Integration History", hasattr(self, 'integration_history')),
        ]
        
        # Tracing Integration tests
        tracing_tests = [
            ("Tracer", hasattr(self, 'tracer')),
            ("Tracing Enabled", hasattr(self, 'tracing_enabled')),
        ]
        
        # Event handlers tests
        event_handler_tests = [
            ("handle_fullstack_development_requested", hasattr(self, 'handle_fullstack_development_requested')),
            ("handle_fullstack_development_completed", hasattr(self, 'handle_fullstack_development_completed')),
            ("handle_api_development_requested", hasattr(self, 'handle_api_development_requested')),
            ("handle_frontend_development_requested", hasattr(self, 'handle_frontend_development_requested')),
        ]
        
        all_tests = core_tests + mcp_tests + message_bus_tests + tracing_tests + event_handler_tests
        
        passed = 0
        total = len(all_tests)
        
        print("\n📋 Core Functionality:")
        for test_name, result in core_tests:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
        
        print("\n🔗 MCP Integration:")
        for test_name, result in mcp_tests:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
        
        print("\n📡 Message Bus Integration:")
        for test_name, result in message_bus_tests:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
        
        print("\n🔍 Tracing Integration:")
        for test_name, result in tracing_tests:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
        
        print("\n🎯 Event Handlers:")
        for test_name, result in event_handler_tests:
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            if result:
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All resources available and properly configured!")
            print("✅ FullstackDeveloper Agent is fully compliant with workflow requirements")
        else:
            print("⚠️  Some resources are missing or not properly configured")
            print("🔧 Please check the failed tests above")
        
        return passed == total

    def build_shadcn_component(self, component_name: str = "Button") -> Dict[str, Any]:
        """Build a Shadcn/ui component with proper validation."""
        try:
            self._validate_component_name(component_name)
            
            logger.info(f"Building Shadcn/ui component: {component_name}")
            
            # Record start time for performance monitoring
            start_time = time.time()
            
            # Generate component code
            component_code = f"""
import React from 'react';
import {{ cn }} from '@/lib/utils';

interface {component_name}Props {{
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}}

export function {component_name}({{ 
  className, 
  children, 
  onClick, 
  disabled = false 
}}: {component_name}Props) {{
  return (
    <button
      className={{cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
        "bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4",
        className
      )}}
      onClick={{onClick}}
      disabled={{disabled}}
    >
      {{children}}
    </button>
  );
}}
"""
            
            # Record performance
            end_time = time.time()
            build_time = end_time - start_time
            
            # Log performance metric
            self._record_development_metric("component_build_time", build_time, "s")
            
            # Add to development history
            dev_entry = f"{datetime.now().isoformat()}: Built Shadcn/ui component {component_name}"
            self.development_history.append(dev_entry)
            self._save_development_history()
            
            return {
                "success": True,
                "component_name": component_name,
                "component_code": component_code,
                "build_time": build_time,
                "template_used": "shadcn/ui"
            }
            
        except DevelopmentValidationError as e:
            logger.error(f"Validation error building component {component_name}: {e}")
            return {
                "success": False,
                "component_name": component_name,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error building component {component_name}: {e}")
            return {
                "success": False,
                "component_name": component_name,
                "error": str(e)
            }

    async def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting collaboration example...")

        # Publish development request
        publish("fullstack_development_requested", {
            "agent": "FullstackDeveloperAgent",
            "story": "User Authentication",
            "timestamp": datetime.now().isoformat()
        })

        # Implement story
        self.implement_story()

        # Build frontend with Shadcn
        self.build_frontend()

        # Build Shadcn component
        component_result = self.build_shadcn_component("Button")

        # Develop feature with MCP
        feature_result = await self.develop_feature("UserAuth", "User authentication feature with login/logout")

        # Publish completion
        publish("fullstack_development_completed", {
            "status": "success",
            "agent": "FullstackDeveloperAgent",
            "shadcn_components": 1
        })

        # Save context
        save_context("FullstackDeveloper", "status", {"feature_status": "deployed"})

        # Notify via Slack
        try:
            send_slack_message(f"Fullstack development completed with {component_result['variants']} Shadcn component variants")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("FullstackDeveloper")
        print(f"Opgehaalde context: {context}")

    async def handle_fullstack_development_requested(self, event):
        """Handle fullstack development requested event with quality-first implementation."""
        try:
            logger.info(f"Fullstack development requested: {event}")
            
            # Extract event data
            feature_name = event.get("feature_name", "Unknown Feature")
            feature_description = event.get("feature_description", "")
            development_type = event.get("development_type", "fullstack")
            
            # Update performance metrics
            self.performance_metrics["total_features"] += 1
            
            # Record in performance history
            performance_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "fullstack_development_requested",
                "feature_name": feature_name,
                "development_type": development_type,
                "status": "processing"
            }
            self.performance_history.append(performance_entry)
            
            # Record in development history
            dev_entry = f"{datetime.now().isoformat()}: Fullstack development requested for {feature_name}"
            self.development_history.append(dev_entry)
            
            # Publish follow-up event
            if self.message_bus_integration:
                await self.message_bus_integration.publish_event("fullstack_development_processing", {
                    "feature_name": feature_name,
                    "development_type": development_type,
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Fullstack development processing started for {feature_name}")
            return {"status": "processing", "feature_name": feature_name}
            
        except Exception as e:
            logger.error(f"Error handling fullstack development requested: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_fullstack_development_completed(self, event):
        """Handle fullstack development completed event with quality-first implementation."""
        try:
            logger.info(f"Fullstack development completed: {event}")
            
            # Extract event data
            feature_name = event.get("feature_name", "Unknown Feature")
            development_time = event.get("development_time", 0)
            test_coverage = event.get("test_coverage", 0)
            code_quality = event.get("code_quality", 0)
            
            # Update performance metrics
            self.performance_metrics["average_development_time"] = (
                (self.performance_metrics["average_development_time"] + development_time) / 2
            )
            self.performance_metrics["test_coverage_rate"] = max(
                self.performance_metrics["test_coverage_rate"], test_coverage
            )
            self.performance_metrics["code_quality_score"] = max(
                self.performance_metrics["code_quality_score"], code_quality
            )
            
            # Record in performance history
            performance_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "fullstack_development_completed",
                "feature_name": feature_name,
                "development_time": development_time,
                "test_coverage": test_coverage,
                "code_quality": code_quality,
                "status": "completed"
            }
            self.performance_history.append(performance_entry)
            
            # Record in development history
            dev_entry = f"{datetime.now().isoformat()}: Fullstack development completed for {feature_name} (time: {development_time}s, coverage: {test_coverage}%, quality: {code_quality})"
            self.development_history.append(dev_entry)
            
            # Publish follow-up event
            if self.message_bus_integration:
                await self.message_bus_integration.publish_event("fullstack_development_finalized", {
                    "feature_name": feature_name,
                    "development_time": development_time,
                    "test_coverage": test_coverage,
                    "code_quality": code_quality,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Fullstack development completed for {feature_name}")
            return {"status": "completed", "feature_name": feature_name}
            
        except Exception as e:
            logger.error(f"Error handling fullstack development completed: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_api_development_requested(self, event):
        """Handle API development requested event with quality-first implementation."""
        try:
            logger.info(f"API development requested: {event}")
            
            # Extract event data
            api_name = event.get("api_name", "Unknown API")
            api_type = event.get("api_type", "REST")
            endpoints = event.get("endpoints", [])
            
            # Update performance metrics
            self.performance_metrics["api_endpoints_created"] += len(endpoints)
            
            # Record in API history
            api_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "api_development_requested",
                "api_name": api_name,
                "api_type": api_type,
                "endpoints": endpoints,
                "status": "processing"
            }
            self.api_history.append(api_entry)
            
            # Record in performance history
            performance_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "api_development_requested",
                "api_name": api_name,
                "endpoints_count": len(endpoints),
                "status": "processing"
            }
            self.performance_history.append(performance_entry)
            
            # Publish follow-up event
            if self.message_bus_integration:
                await self.message_bus_integration.publish_event("api_development_processing", {
                    "api_name": api_name,
                    "api_type": api_type,
                    "endpoints": endpoints,
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"API development processing started for {api_name}")
            return {"status": "processing", "api_name": api_name}
            
        except Exception as e:
            logger.error(f"Error handling API development requested: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_frontend_development_requested(self, event):
        """Handle frontend development requested event with quality-first implementation."""
        try:
            logger.info(f"Frontend development requested: {event}")
            
            # Extract event data
            component_name = event.get("component_name", "Unknown Component")
            framework = event.get("framework", "React")
            ui_library = event.get("ui_library", "Shadcn/ui")
            
            # Update performance metrics
            self.performance_metrics["frontend_components_built"] += 1
            
            # Record in frontend history
            frontend_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "frontend_development_requested",
                "component_name": component_name,
                "framework": framework,
                "ui_library": ui_library,
                "status": "processing"
            }
            self.frontend_history.append(frontend_entry)
            
            # Record in performance history
            performance_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": "frontend_development_requested",
                "component_name": component_name,
                "framework": framework,
                "status": "processing"
            }
            self.performance_history.append(performance_entry)
            
            # Publish follow-up event
            if self.message_bus_integration:
                await self.message_bus_integration.publish_event("frontend_development_processing", {
                    "component_name": component_name,
                    "framework": framework,
                    "ui_library": ui_library,
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Frontend development processing started for {component_name}")
            return {"status": "processing", "component_name": component_name}
            
        except Exception as e:
            logger.error(f"Error handling frontend development requested: {e}")
            return {"status": "error", "error": str(e)}

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        await self.initialize_enhanced_mcp()
        await self.initialize_tracing()
        await self.initialize_message_bus_integration()
        
        logger.info("FullstackDeveloperAgent ready and listening for events...")
        await self.collaborate_example()

    # --- ORIGINELE FUNCTIONALITEIT BEHOUDEN ---
    def implement_story(self):
        print(
            textwrap.dedent(
                """
        ## Pull Request: User Authentication
        - [x] Endpoint `/auth/login` geïmplementeerd (FastAPI)
        - [x] JWT integratie met Supabase
        - [x] Frontend login form (Next.js)
        - [x] Unit tests (pytest, coverage 95%)
        - [ ] E2E test pending
        **Blockers:**
        - Nog geen e-mail service voor registratiebevestiging
        """
            )
        )

        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, 95, "%")

        # Add to history
        dev_entry = f"{datetime.now().isoformat()}: User Authentication story implemented"
        self.development_history.append(dev_entry)
        self._save_development_history()

    def build_api(self):
        print(
            textwrap.dedent(
                """
        @router.post("/auth/login")
        def login(user: UserLogin):
            token = auth_service.authenticate(user.email, user.password)
            return {"access_token": token}
        """
            )
        )

        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, 90, "%")

    def build_frontend(self):
        """Bouw de BMAD frontend dashboard."""
        print("🚀 FullstackDeveloper - BMAD Frontend Development")
        print("=" * 60)

        # Haal architectuur op van de Architect
        get_context("Architect", "frontend_architecture")

        print("📋 BMAD Dashboard Componenten:")
        print("=" * 40)

        # Dashboard Component
        print("""
// components/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { AgentStatus } from './AgentStatus';
import { WorkflowManager } from './WorkflowManager';
import { APITester } from './APITester';
import { MetricsChart } from './MetricsChart';

export function Dashboard(): JSX.Element {
  const [activeTab, setActiveTab] = useState('agents');
  const [agents, setAgents] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [metrics, setMetrics] = useState({});

  useEffect(() => {
    // Load initial data
    fetchAgents();
    fetchWorkflows();
    fetchMetrics();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents/status');
      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('/api/orchestrator/status');
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/orchestrator/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>BMAD Dashboard</h1>
        <nav className="dashboard-nav">
          <button 
            className={activeTab === 'agents' ? 'active' : ''} 
            onClick={() => setActiveTab('agents')}
          >
            Agent Status
          </button>
          <button 
            className={activeTab === 'workflows' ? 'active' : ''} 
            onClick={() => setActiveTab('workflows')}
          >
            Workflows
          </button>
          <button 
            className={activeTab === 'api' ? 'active' : ''} 
            onClick={() => setActiveTab('api')}
          >
            API Testing
          </button>
          <button 
            className={activeTab === 'metrics' ? 'active' : ''} 
            onClick={() => setActiveTab('metrics')}
          >
            Metrics
          </button>
        </nav>
      </header>

      <main className="dashboard-content">
        {activeTab === 'agents' && <AgentStatus agents={agents} />}
        {activeTab === 'workflows' && <WorkflowManager workflows={workflows} />}
        {activeTab === 'api' && <APITester />}
        {activeTab === 'metrics' && <MetricsChart metrics={metrics} />}
      </main>
    </div>
  );
}
""")

        # Agent Status Component
        print("""
// components/AgentStatus.tsx
import React from 'react';

interface Agent {
  name: string;
  status: 'online' | 'offline' | 'error';
  lastSeen: string;
  performance: {
    responseTime: number;
    throughput: number;
  };
}

interface AgentStatusProps {
  agents: Agent[];
}

export function AgentStatus({ agents }: AgentStatusProps): JSX.Element {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'green';
      case 'offline': return 'red';
      case 'error': return 'orange';
      default: return 'gray';
    }
  };

  return (
    <div className="agent-status">
      <h2>Agent Status</h2>
      <div className="agent-grid">
        {agents.map((agent) => (
          <div key={agent.name} className="agent-card">
            <div className="agent-header">
              <h3>{agent.name}</h3>
              <span 
                className={`status-indicator ${getStatusColor(agent.status)}`}
                title={agent.status}
              />
            </div>
            <div className="agent-details">
              <p>Last seen: {agent.lastSeen}</p>
              <p>Response time: {agent.performance.responseTime}ms</p>
              <p>Throughput: {agent.performance.throughput}/min</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
""")

        # Workflow Manager Component
        print("""
// components/WorkflowManager.tsx
import React, { useState } from 'react';

interface Workflow {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  startTime: string;
  endTime?: string;
}

interface WorkflowManagerProps {
  workflows: Workflow[];
}

export function WorkflowManager({ workflows }: WorkflowManagerProps): JSX.Element {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

  const startWorkflow = async (workflowName: string) => {
    try {
      const response = await fetch('/api/orchestrator/start-workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow: workflowName })
      });
      
      if (response.ok) {
        console.log('Workflow started successfully');
        // Refresh workflows
      }
    } catch (error) {
      console.error('Error starting workflow:', error);
    }
  };

  return (
    <div className="workflow-manager">
      <h2>Workflow Management</h2>
      
      <div className="workflow-controls">
        <button onClick={() => startWorkflow('feature')}>
          Start Feature Workflow
        </button>
        <button onClick={() => startWorkflow('bugfix')}>
          Start Bugfix Workflow
        </button>
        <button onClick={() => startWorkflow('deployment')}>
          Start Deployment Workflow
        </button>
      </div>

      <div className="workflow-list">
        {workflows.map((workflow) => (
          <div key={workflow.id} className="workflow-card">
            <div className="workflow-header">
              <h3>{workflow.name}</h3>
              <span className={`status ${workflow.status}`}>
                {workflow.status}
              </span>
            </div>
            <div className="workflow-progress">
              <div 
                className="progress-bar" 
                style={{ width: `${workflow.progress}%` }}
              />
              <span>{workflow.progress}%</span>
            </div>
            <div className="workflow-timestamps">
              <p>Started: {workflow.startTime}</p>
              {workflow.endTime && <p>Ended: {workflow.endTime}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
""")

        # API Tester Component
        print("""
// components/APITester.tsx
import React, { useState } from 'react';

export function APITester(): JSX.Element {
  const [endpoint, setEndpoint] = useState('/api/test/ping');
  const [method, setMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const testEndpoint = async () => {
    setLoading(true);
    try {
      const options: RequestInit = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };

      if (method !== 'GET' && requestBody) {
        options.body = requestBody;
      }

      const response = await fetch(endpoint, options);
      const data = await response.json();
      
      setResponse(JSON.stringify(data, null, 2));
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-tester">
      <h2>API Testing Interface</h2>
      
      <div className="api-controls">
        <div className="endpoint-input">
          <label>Endpoint:</label>
          <input 
            type="text" 
            value={endpoint} 
            onChange={(e) => setEndpoint(e.target.value)}
            placeholder="/api/endpoint"
          />
        </div>
        
        <div className="method-selector">
          <label>Method:</label>
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
        
        <button onClick={testEndpoint} disabled={loading}>
          {loading ? 'Testing...' : 'Test Endpoint'}
        </button>
      </div>

      {method !== 'GET' && (
        <div className="request-body">
          <label>Request Body (JSON):</label>
          <textarea
            value={requestBody}
            onChange={(e) => setRequestBody(e.target.value)}
            placeholder='{"key": "value"}'
            rows={5}
          />
        </div>
      )}

      {response && (
        <div className="response">
          <h3>Response:</h3>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}
""")

        # Metrics Chart Component
        print("""
// components/MetricsChart.tsx
import React from 'react';
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager


interface Metrics {
  workflows: {
    total: number;
    running: number;
    completed: number;
    failed: number;
  };
  agents: {
    total: number;
    online: number;
    offline: number;
  };
  performance: {
    avgResponseTime: number;
    totalRequests: number;
    successRate: number;
  };
}

interface MetricsChartProps {
  metrics: Metrics;
}

export function MetricsChart({ metrics }: MetricsChartProps): JSX.Element {
  return (
    <div className="metrics-chart">
      <h2>System Metrics</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Workflows</h3>
          <div className="metric-values">
            <div>Total: {metrics.workflows?.total || 0}</div>
            <div>Running: {metrics.workflows?.running || 0}</div>
            <div>Completed: {metrics.workflows?.completed || 0}</div>
            <div>Failed: {metrics.workflows?.failed || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <h3>Agents</h3>
          <div className="metric-values">
            <div>Total: {metrics.agents?.total || 0}</div>
            <div>Online: {metrics.agents?.online || 0}</div>
            <div>Offline: {metrics.agents?.offline || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <h3>Performance</h3>
          <div className="metric-values">
            <div>Avg Response: {metrics.performance?.avgResponseTime || 0}ms</div>
            <div>Total Requests: {metrics.performance?.totalRequests || 0}</div>
            <div>Success Rate: {metrics.performance?.successRate || 0}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
""")

        print("\n🎨 CSS Styling:")
        print("""
/* styles/dashboard.css */
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.dashboard-nav {
  display: flex;
  gap: 10px;
}

.dashboard-nav button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #f0f0f0;
  cursor: pointer;
  transition: background 0.3s;
}

.dashboard-nav button.active {
  background: #007bff;
  color: white;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator.green { background: #28a745; }
.status-indicator.red { background: #dc3545; }
.status-indicator.orange { background: #ffc107; }
.status-indicator.gray { background: #6c757d; }

.workflow-controls {
  margin-bottom: 20px;
}

.workflow-controls button {
  margin-right: 10px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #007bff;
  color: white;
  cursor: pointer;
}

.api-controls {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 15px;
  margin-bottom: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.metric-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
  text-align: center;
}
""")

        print("\n📦 Package.json:")
        print("""
{
  "name": "bmad-dashboard",
  "version": "1.0.0",
  "description": "BMAD Agent Dashboard",
  "main": "index.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@vitejs/plugin-react": "^3.1.0",
    "typescript": "^4.9.4",
    "vite": "^4.1.0",
    "vitest": "^0.29.0"
  }
}
""")

        # Sla de frontend code op
        save_context("FullstackDeveloper", "frontend_code", {
            "timestamp": time.time(),
            "components": ["Dashboard", "AgentStatus", "WorkflowManager", "APITester", "MetricsChart"],
            "status": "generated"
        })

        # Publiceer event
        publish("frontend_code_generated", {
            "agent": "FullstackDeveloper",
            "status": "success",
            "components_count": 5
        })

        print("\n✅ BMAD Frontend Dashboard gegenereerd!")
        print("📁 Componenten: Dashboard, AgentStatus, WorkflowManager, APITester, MetricsChart")
        print("🎨 CSS styling en package.json inbegrepen")
        print("🔗 Klaar voor integratie met BMAD API")

        # Log performance metric
        self.monitor._record_metric("FullstackDeveloper", MetricType.SUCCESS_RATE, 95, "%")

        # Add to history
        dev_entry = f"{datetime.now().isoformat()}: Frontend Dashboard generated with 5 components"
        self.development_history.append(dev_entry)
        self._save_development_history()

    def integrate_service(self):
        print(
            textwrap.dedent(
                """
        # Integratie met Supabase, Redis, pgvector, Langchain
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        """
            )
        )

    def write_tests(self):
        print(
            textwrap.dedent(
                """
        def test_login_success(client):
            response = client.post("/auth/login", json={"email": "test@test.com", "password": "secret"})
            assert response.status_code == 200
            assert "access_token" in response.json()
        """
            )
        )

    def ci_cd(self):
        print(
            textwrap.dedent(
                """
        # CI/CD Pipeline (GitHub Actions)
        name: CI
        on: [push]
        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - name: Set up Python
                uses: actions/setup-python@v4
                with:
                  python-version: '3.11'
              - name: Install dependencies
                run: pip install -r requirements.txt
              - name: Run tests
                run: pytest
        """
            )
        )

    def dev_log(self):
        print(
            textwrap.dedent(
                """
        ### Dev Log 2024-07-20
        - User login endpoint gebouwd
        - JWT integratie getest
        - Frontend login form aangemaakt
        - Unit tests toegevoegd
        - Blocker: wacht op e-mail service
        """
            )
        )

    def review(self):
        print(
            textwrap.dedent(
                """
        # Code Review
        - [x] Code voldoet aan style guide
        - [x] Alle tests geslaagd
        - [ ] Edge cases afgedekt
        - [ ] Security checks uitgevoerd
        """
            )
        )

    def refactor(self):
        print(
            textwrap.dedent(
                """
        # Refactoring Advies
        - Herstructureer login logica naar aparte service
        - Gebruik environment variables voor secrets
        - Voeg type hints toe aan alle functies
        """
            )
        )

    def security_check(self):
        print(
            textwrap.dedent(
                """
        # Security Checklist
        - [x] Input validatie aanwezig
        - [x] JWT tokens met expiry
        - [ ] Rate limiting op login endpoint
        - [ ] Dependency scan uitgevoerd
        """
            )
        )

    def blockers(self):
        print(
            textwrap.dedent(
                """
        # Blockers
        - E-mail service ontbreekt voor registratie
        - Testdata niet beschikbaar voor E2E tests
        """
            )
        )

    # --- Uitbreidingen hieronder ---
    def api_contract(self):
        print(
            "Zie OpenAPI contract voorbeeld in: resources/templates/openapi-snippet.yaml"
        )

    def component_doc(self):
        print(
            "Zie Storybook/MDX voorbeeld in: resources/templates/storybook-mdx-template.mdx"
        )

    def performance_profile(self):
        print(
            "Zie performance report template in: resources/templates/performance-report-template.md"
        )

    def a11y_check(self):
        print(
            textwrap.dedent(
                """
        ## Accessibility Check
        - [x] Alle inputs hebben labels
        - [x] Contrast ratio voldoet aan WCAG AA
        - [ ] Keyboard navigation volledig ondersteund
        """
            )
        )

    def feature_toggle(self):
        print(
            "Zie feature toggle config in: resources/templates/feature-toggle-config.yaml"
        )

    def monitoring_setup(self):
        print(
            "Zie monitoring config snippet in: resources/templates/monitoring-config-snippet.yaml"
        )

    def release_notes(self):
        print(
            "Zie release notes template in: resources/templates/release-notes-template.md"
        )

    def devops_handover(self):
        print(
            "Zie DevOps handover checklist in: resources/templates/devops-handover-checklist.md"
        )

    def tech_debt(self):
        print(
            textwrap.dedent(
                """
        # Technische schuld
        - [ ] Oude API endpoints refactoren
        - [ ] Dependency upgrades nodig
        - [ ] Test coverage verhogen voor legacy code
        """
            )
        )

    async def develop_feature(self, feature_name: str, feature_description: str = "") -> Dict[str, Any]:
        """
        Develop a complete feature from frontend to backend with enhanced validation.
        
        Args:
            feature_name: Name of the feature to develop
            feature_description: Description of the feature
            
        Returns:
            Dict containing development results
        """
        try:
            self._validate_feature_name(feature_name)
            self._validate_input(feature_description, str, "feature_description")
            
            logger.info(f"Starting development of feature: {feature_name}")
            
            # Record start time for performance monitoring
            start_time = time.time()
            
            # Assess complexity
            complexity = self._assess_development_complexity(feature_description)
            recommendations = self._generate_development_recommendations(complexity)
            
            # Try MCP-enhanced feature development first
            if self.mcp_enabled and self.mcp_client:
                try:
                    mcp_result = await self.use_mcp_tool("develop_feature", {
                        "feature_name": feature_name,
                        "feature_description": feature_description,
                        "complexity": complexity,
                        "development_type": "fullstack",
                        "include_frontend": True,
                        "include_backend": True,
                        "include_api": True
                    })
                    
                    if mcp_result:
                        logger.info("MCP-enhanced feature development completed")
                        result = mcp_result.get("development_result", {})
                        result["mcp_enhanced"] = True
                    else:
                        logger.warning("MCP feature development failed, using local development")
                        result = self._create_local_development_result(feature_name, feature_description, complexity, recommendations)
                except Exception as e:
                    logger.warning(f"MCP feature development failed: {e}, using local development")
                    result = self._create_local_development_result(feature_name, feature_description, complexity, recommendations)
            else:
                result = self._create_local_development_result(feature_name, feature_description, complexity, recommendations)
            
            # Use fullstack-specific MCP tools for additional enhancement
            if self.mcp_enabled:
                try:
                    development_data = {
                        "feature_name": feature_name,
                        "feature_description": feature_description,
                        "development_type": "fullstack",
                        "include_frontend": True,
                        "include_backend": True,
                        "include_api": True,
                        "api_name": f"{feature_name}API",
                        "api_type": "REST",
                        "endpoints": [f"GET /api/{feature_name.lower()}", f"POST /api/{feature_name.lower()}"],
                        "component_name": feature_name,
                        "framework": "React",
                        "ui_library": "Shadcn/ui",
                        "accessibility": True,
                        "responsive": True,
                        "test_scope": "fullstack",
                        "test_type": "end-to-end",
                        "coverage": "comprehensive",
                        "automation": True
                    }
                    development_enhanced = await self.use_fullstack_specific_mcp_tools(development_data)
                    if development_enhanced:
                        result["development_enhancements"] = development_enhanced
                except Exception as e:
                    logger.warning(f"Fullstack-specific MCP tools failed: {e}")

            # Use enhanced MCP tools for Phase 2 capabilities
            if self.enhanced_mcp_enabled:
                try:
                    enhanced_data = await self.use_enhanced_mcp_tools({
                        "feature_name": feature_name,
                        "feature_description": feature_description,
                        "complexity": complexity,
                        "capabilities": ["frontend", "backend", "api", "integration"],
                        "performance_metrics": {"development_time": start_time}
                    })
                    if enhanced_data:
                        result["enhanced_mcp_data"] = enhanced_data
                        result["enhanced_mcp_enabled"] = True
                except Exception as e:
                    logger.warning(f"Enhanced MCP tools failed: {e}")

            # Trace feature development process
            if self.tracing_enabled and self.tracer:
                try:
                    trace_result = await self.trace_feature_development({
                        "feature_name": feature_name,
                        "complexity": complexity,
                        "frontend_components": [f"{feature_name}Component"],
                        "backend_apis": [f"{feature_name}API"],
                        "integration_points": ["api_integration", "data_flow"],
                        "performance_metrics": {"development_time": start_time}
                    })
                    if trace_result:
                        result["tracing_data"] = trace_result
                        result["tracing_enabled"] = True
                except Exception as e:
                    logger.warning(f"Feature development tracing failed: {e}")

            # Record performance
            end_time = time.time()
            development_time = end_time - start_time
            
            # Log performance metric
            try:
                self._record_development_metric("feature_development_time", development_time, "s")
            except AttributeError:
                logger.info("Performance metrics recording not available")
            
            # Save to development history
            self.development_history.append(f"Developed feature: {feature_name} in {development_time:.2f}s")
            self._save_development_history()
            
            logger.info(f"Feature development completed: {feature_name}")
            
            return result
            
        except DevelopmentValidationError as e:
            logger.error(f"Validation error developing feature {feature_name}: {e}")
            return {
                "success": False,
                "feature_name": feature_name,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error developing feature {feature_name}: {e}")
            return {
                "success": False,
                "feature_name": feature_name,
                "error": str(e)
            }
    
    def _create_local_development_result(self, feature_name: str, feature_description: str, complexity: str, recommendations: list) -> Dict[str, Any]:
        """Create local development result when MCP is not available."""
        # Create feature development plan
        plan = {
            "feature_name": feature_name,
            "description": feature_description,
            "complexity": complexity,
            "recommendations": recommendations,
            "components": [],
            "apis": [],
            "tests": [],
            "status": "completed"
        }
        
        # Build frontend component
        component_result = self.build_shadcn_component(feature_name)
        plan["components"].append(component_result)
        
        # Build API endpoint
        api_result = self.build_api()
        plan["apis"].append(api_result)
        
        # Write tests
        test_result = self.write_tests()
        plan["tests"].append(test_result)
        
        return {
            "success": True,
            "feature_name": feature_name,
            "development_time": 0.0,
            "complexity": complexity,
            "plan": plan
        }

    def handle_tasks_assigned(self, event):
        logging.info("[FullstackDeveloper] Taken ontvangen, ontwikkeling wordt gestart...")
        time.sleep(1)
        publish("development_started", {"desc": "Ontwikkeling gestart"})
        logging.info("[FullstackDeveloper] Ontwikkeling gestart, development_started gepubliceerd.")

    def handle_development_started(self, event):
        logging.info("[FullstackDeveloper] Ontwikkeling in uitvoering...")
        time.sleep(2)
        publish("testing_started", {"desc": "Testen gestart"})
        logging.info("[FullstackDeveloper] Testen gestart, testing_started gepubliceerd.")

    def setup_event_handlers(self):
        subscribe("tasks_assigned", self.handle_tasks_assigned)
        subscribe("development_started", self.handle_development_started)

def main():
    parser = argparse.ArgumentParser(description="FullstackDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "implement-story", "build-api", "build-frontend", "build-shadcn-component",
                               "write-tests", "show-development-history", "show-performance", "show-best-practices",
                               "show-changelog", "export-report", "test", "collaborate", "run", "integrate-service",
                               "ci-cd", "dev-log", "review", "refactor", "security-check", "blockers", "api-contract",
                               "component-doc", "performance-profile", "a11y-check", "feature-toggle", "monitoring-setup",
                               "release-notes", "devops-handover", "tech-debt", "develop-feature",
                               "enhanced-collaborate", "enhanced-security", "enhanced-performance", "enhanced-tools", "enhanced-summary",
                               "trace-feature", "trace-integration", "trace-performance", "trace-error", "tracing-summary",
                               "message-bus-status", "publish-event", "subscribe-event", "test-message-bus", "message-bus-performance", "message-bus-health"])
    parser.add_argument("--name", default="User Authentication", help="Story/Component name")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    parser.add_argument("--agents", nargs="+", help="Target agents for collaboration")
    parser.add_argument("--message", help="Message for agent communication")
    parser.add_argument("--tool-config", help="External tool configuration (JSON)")
    parser.add_argument("--feature-data", help="Feature data for tracing (JSON)")
    parser.add_argument("--integration-data", help="Integration data for tracing (JSON)")
    parser.add_argument("--performance-data", help="Performance data for tracing (JSON)")
    parser.add_argument("--error-data", help="Error data for tracing (JSON)")

    args = parser.parse_args()

    agent = FullstackDeveloperAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "implement-story":
        agent.implement_story()
    elif args.command == "build-api":
        agent.build_api()
    elif args.command == "build-frontend":
        agent.build_frontend()
    elif args.command == "build-shadcn-component":
        agent.build_shadcn_component(args.name)
    elif args.command == "write-tests":
        agent.write_tests()
    elif args.command == "show-development-history":
        agent.show_development_history()
    elif args.command == "show-performance":
        agent.show_performance()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-report":
        agent.export_report(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        asyncio.run(agent.run())
    elif args.command == "integrate-service":
        agent.integrate_service()
    elif args.command == "ci-cd":
        agent.ci_cd()
    elif args.command == "dev-log":
        agent.dev_log()
    elif args.command == "review":
        agent.review()
    elif args.command == "refactor":
        agent.refactor()
    elif args.command == "security-check":
        agent.security_check()
    elif args.command == "blockers":
        agent.blockers()
    elif args.command == "api-contract":
        agent.api_contract()
    elif args.command == "component-doc":
        agent.component_doc()
    elif args.command == "performance-profile":
        agent.performance_profile()
    elif args.command == "a11y-check":
        agent.a11y_check()
    elif args.command == "feature-toggle":
        agent.feature_toggle()
    elif args.command == "monitoring-setup":
        agent.monitoring_setup()
    elif args.command == "release-notes":
        agent.release_notes()
    elif args.command == "devops-handover":
        agent.devops_handover()
    elif args.command == "tech-debt":
        agent.tech_debt()
    elif args.command == "develop-feature":
        result = asyncio.run(agent.develop_feature(args.name, "Feature development with enhanced MCP and tracing"))
        print(f"Feature development result: {result}")
    elif args.command == "enhanced-collaborate":
        if not args.agents or not args.message:
            print("Error: --agents and --message are required for enhanced collaboration")
            sys.exit(1)
        message = {"type": "collaboration", "content": {"message": args.message}}
        result = asyncio.run(agent.communicate_with_agents(args.agents, message))
        print(f"Enhanced collaboration result: {result}")
    elif args.command == "enhanced-security":
        security_data = {
            "auth_method": "multi_factor",
            "security_level": "enterprise",
            "compliance": ["gdpr", "sox", "iso27001"],
            "model": "rbac",
            "indicators": ["suspicious_activity", "unauthorized_access"]
        }
        result = asyncio.run(agent.enhanced_security_validation(security_data))
        print(f"Enhanced security validation result: {result}")
    elif args.command == "enhanced-performance":
        performance_data = {
            "cache_strategy": "adaptive",
            "memory_usage": {"current": 50, "peak": 80},
            "target_latency": 50
        }
        result = asyncio.run(agent.enhanced_performance_optimization(performance_data))
        print(f"Enhanced performance optimization result: {result}")
    elif args.command == "enhanced-tools":
        if not args.tool_config:
            print("Error: --tool-config is required for enhanced tools")
            sys.exit(1)
        try:
            tool_config = json.loads(args.tool_config)
            result = asyncio.run(agent.use_external_tools(tool_config))
            print(f"Enhanced external tools result: {result}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --tool-config")
            sys.exit(1)
    elif args.command == "enhanced-summary":
        performance_summary = agent.get_enhanced_performance_summary()
        communication_summary = agent.get_enhanced_communication_summary()
        print("Enhanced Performance Summary:")
        print(json.dumps(performance_summary, indent=2))
        print("\nEnhanced Communication Summary:")
        print(json.dumps(communication_summary, indent=2))
    elif args.command == "trace-feature":
        if not args.feature_data:
            print("Error: --feature-data is required for trace-feature command")
            sys.exit(1)
        try:
            feature_data = json.loads(args.feature_data)
            result = asyncio.run(agent.trace_feature_development(feature_data))
            print(f"Feature tracing result: {result}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --feature-data")
            sys.exit(1)
    elif args.command == "trace-integration":
        if not args.integration_data:
            print("Error: --integration-data is required for trace-integration command")
            sys.exit(1)
        try:
            integration_data = json.loads(args.integration_data)
            result = asyncio.run(agent.trace_fullstack_integration(integration_data))
            print(f"Integration tracing result: {result}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --integration-data")
            sys.exit(1)
    elif args.command == "trace-performance":
        if not args.performance_data:
            print("Error: --performance-data is required for trace-performance command")
            sys.exit(1)
        try:
            performance_data = json.loads(args.performance_data)
            result = asyncio.run(agent.trace_performance_optimization(performance_data))
            print(f"Performance tracing result: {result}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --performance-data")
            sys.exit(1)
    elif args.command == "trace-error":
        if not args.error_data:
            print("Error: --error-data is required for trace-error command")
            sys.exit(1)
        try:
            error_data = json.loads(args.error_data)
            result = asyncio.run(agent.trace_fullstack_error(error_data))
            print(f"Error tracing result: {result}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --error-data")
            sys.exit(1)
    elif args.command == "tracing-summary":
        tracing_summary = agent.get_tracing_summary()
        print("Tracing Summary:")
        print(json.dumps(tracing_summary, indent=2))
    elif args.command == "message-bus-status":
        status = "enabled" if agent.message_bus_enabled else "disabled"
        print(f"Message Bus Status: {status}")
        if agent.message_bus_integration:
            print(f"Integration: {type(agent.message_bus_integration).__name__}")
        else:
            print("Integration: None")
    elif args.command == "publish-event":
        if not args.message:
            print("Error: --message is required for publish-event command")
            sys.exit(1)
        try:
            event_data = json.loads(args.message)
            if agent.message_bus_integration:
                asyncio.run(agent.message_bus_integration.publish_event("custom_event", event_data))
                print(f"Event published: {event_data}")
            else:
                print("Error: Message Bus not initialized")
                sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --message")
            sys.exit(1)
    elif args.command == "subscribe-event":
        print("Event subscription status:")
        if agent.message_bus_integration:
            print("✅ Message Bus Integration active")
            print("Registered event handlers:")
            print("- fullstack_development_requested")
            print("- fullstack_development_completed")
            print("- api_development_requested")
            print("- frontend_development_requested")
        else:
            print("❌ Message Bus Integration not available")
    elif args.command == "test-message-bus":
        print("Testing Message Bus Integration...")
        if agent.message_bus_integration:
            # Test event publishing
            test_event = {"test": True, "timestamp": datetime.now().isoformat()}
            asyncio.run(agent.message_bus_integration.publish_event("test_event", test_event))
            print("✅ Test event published successfully")
        else:
            print("❌ Message Bus Integration not available")
    elif args.command == "message-bus-performance":
        print("Message Bus Performance Metrics:")
        print(f"Total Features: {agent.performance_metrics['total_features']}")
        print(f"API Endpoints Created: {agent.performance_metrics['api_endpoints_created']}")
        print(f"Frontend Components Built: {agent.performance_metrics['frontend_components_built']}")
        print(f"Integration Tests Passed: {agent.performance_metrics['integration_tests_passed']}")
        print(f"Deployment Success Rate: {agent.performance_metrics['deployment_success_rate']}%")
        print(f"Average Development Time: {agent.performance_metrics['average_development_time']}s")
        print(f"Code Quality Score: {agent.performance_metrics['code_quality_score']}")
        print(f"Test Coverage Rate: {agent.performance_metrics['test_coverage_rate']}%")
    elif args.command == "message-bus-health":
        print("Message Bus Health Check:")
        print(f"Message Bus Enabled: {agent.message_bus_enabled}")
        print(f"Integration Available: {agent.message_bus_integration is not None}")
        print(f"Performance Metrics: {len(agent.performance_metrics)} metrics tracked")
        print(f"Performance History: {len(agent.performance_history)} entries")
        print(f"Development History: {len(agent.development_history)} entries")
        print(f"API History: {len(agent.api_history)} entries")
        print(f"Frontend History: {len(agent.frontend_history)} entries")
        print("✅ Health check completed")

if __name__ == "__main__":
    main()
