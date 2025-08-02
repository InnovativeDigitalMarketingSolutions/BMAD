import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Union

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from integrations.prefect.prefect_workflow import PrefectWorkflowOrchestrator
from integrations.slack.slack_notify import send_slack_message
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager

# MCP Integration
from bmad.core.mcp import (
    MCPClient,
    MCPContext,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class BackendError(Exception):
    """Custom exception for backend-related errors."""
    pass

class BackendValidationError(BackendError):
    """Exception for backend validation failures."""
    pass

class BackendDeveloperAgent:
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        self.backend_development_template = self.framework_manager.get_template('backend_development')
        self.lessons_learned = []
        
        # Set agent name
        self.agent_name = "BackendDeveloper"
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "BackendDeveloperAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        self.workflow = PrefectWorkflowOrchestrator()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/backenddeveloper/best-practices.md",
            "api-template": self.resource_base / "templates/backenddeveloper/api-template.md",
            "api-export-md": self.resource_base / "templates/backenddeveloper/api-export-template.md",
            "api-export-json": self.resource_base / "templates/backenddeveloper/api-export-template.json",
            "performance-report": self.resource_base / "templates/backenddeveloper/performance-report-template.md",
            "database-template": self.resource_base / "templates/backenddeveloper/database-template.md",
            "security-template": self.resource_base / "templates/backenddeveloper/security-template.md",
            "deployment-template": self.resource_base / "templates/backenddeveloper/deployment-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/backenddeveloper/backend-changelog.md",
            "api-history": self.resource_base / "data/backenddeveloper/api-history.md",
            "performance-history": self.resource_base / "data/backenddeveloper/performance-history.md",
            "deployment-history": self.resource_base / "data/backenddeveloper/deployment-history.md"
        }

        # Initialize histories
        self.api_history = []
        self.performance_history = []
        self.deployment_history = []
        self._load_api_history()
        self._load_performance_history()
        self._load_deployment_history()

        # Backend-specific attributes
        self.api_endpoints = {}
        self.database_connections = {}
        self.security_configs = {}
        self.deployment_configs = {}
        
        # Performance metrics
        self.performance_metrics = {
            "total_apis": 0,
            "deployment_success_rate": 0.0,
            "api_build_success_rate": 0.0,
            "average_response_time": 0.0
        }
        
        # Initialize MCP integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False

        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

    async def initialize_mcp(self):
        """Initialize MCP client and integration."""
        try:
            self.mcp_client = await get_mcp_client()
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False

    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use MCP tool voor enhanced functionality."""
        if not self.mcp_enabled or not self.mcp_client:
            logger.warning("MCP not available, using local tools")
            return None
        
        try:
            result = await self.mcp_client.execute_tool(tool_name, parameters)
            logger.info(f"MCP tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"MCP tool {tool_name} execution failed: {e}")
            return None

    async def use_backend_specific_mcp_tools(self, backend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use backend-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # API development
        api_dev_result = await self.use_mcp_tool("api_development", {
            "endpoint": backend_data.get("endpoint", ""),
            "method": backend_data.get("method", "GET"),
            "framework": backend_data.get("framework", "fastapi"),
            "development_type": "comprehensive"
        })
        if api_dev_result:
            enhanced_data["api_development"] = api_dev_result
        
        # Database design
        db_result = await self.use_mcp_tool("database_design", {
            "database_type": backend_data.get("database_type", "postgresql"),
            "schema_requirements": backend_data.get("schema_requirements", {}),
            "design_type": "optimized",
            "scalability": backend_data.get("scalability", "medium")
        })
        if db_result:
            enhanced_data["database_design"] = db_result
        
        # Security implementation
        security_result = await self.use_mcp_tool("security_implementation", {
            "security_level": backend_data.get("security_level", "standard"),
            "authentication": backend_data.get("authentication", "jwt"),
            "authorization": backend_data.get("authorization", "rbac"),
            "compliance": backend_data.get("compliance", ["gdpr", "sox"])
        })
        if security_result:
            enhanced_data["security_implementation"] = security_result
        
        # Performance optimization
        performance_result = await self.use_mcp_tool("performance_optimization", {
            "performance_metrics": backend_data.get("performance_metrics", {}),
            "optimization_type": "comprehensive",
            "target_latency": backend_data.get("target_latency", 100),
            "scaling_strategy": backend_data.get("scaling_strategy", "horizontal")
        })
        if performance_result:
            enhanced_data["performance_optimization"] = performance_result
        
        return enhanced_data
    
    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise BackendValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_endpoint(self, endpoint: str) -> None:
        """Validate API endpoint format."""
        self._validate_input(endpoint, str, "endpoint")
        if not endpoint.strip():
            raise BackendValidationError("Endpoint cannot be empty")
        if not endpoint.startswith("/"):
            raise BackendValidationError("Endpoint must start with '/'")
        if len(endpoint) > 200:
            raise BackendValidationError("Endpoint too long (max 200 characters)")

    def _validate_api_data(self, api_data: Dict[str, Any]) -> None:
        """Validate API data structure."""
        self._validate_input(api_data, dict, "api_data")
        required_fields = ["endpoint", "method", "status"]
        for field in required_fields:
            if field not in api_data:
                raise BackendValidationError(f"Missing required field: {field}")

    def _validate_export_format(self, format_type: str) -> None:
        """Validate export format."""
        self._validate_input(format_type, str, "format_type")
        valid_formats = ["md", "json", "yaml", "html"]
        if format_type.lower() not in valid_formats:
            raise BackendValidationError(f"Invalid export format. Valid formats: {valid_formats}")

    def _load_api_history(self):
        """Load API history with comprehensive error handling."""
        try:
            if self.data_paths["api-history"].exists():
                with open(self.data_paths["api-history"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.api_history.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading API history: {e}")
            raise BackendError(f"Cannot access API history file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading API history: {e}")
            raise BackendError(f"Invalid encoding in API history file: {e}")
        except OSError as e:
            logger.error(f"OS error loading API history: {e}")
            raise BackendError(f"System error loading API history: {e}")
        except Exception as e:
            logger.warning(f"Could not load API history: {e}")

    def _save_api_history(self):
        """Save API history with comprehensive error handling."""
        try:
            self.data_paths["api-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["api-history"], "w", encoding="utf-8") as f:
                f.write("# API History\n\n")
                f.writelines(f"- {api}\n" for api in self.api_history[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving API history: {e}")
            raise BackendError(f"Cannot write to API history file: {e}")
        except OSError as e:
            logger.error(f"OS error saving API history: {e}")
            raise BackendError(f"System error saving API history: {e}")
        except Exception as e:
            logger.error(f"Could not save API history: {e}")

    def _load_performance_history(self):
        """Load performance history with comprehensive error handling."""
        try:
            if self.data_paths["performance-history"].exists():
                with open(self.data_paths["performance-history"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.performance_history.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading performance history: {e}")
            raise BackendError(f"Cannot access performance history file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading performance history: {e}")
            raise BackendError(f"Invalid encoding in performance history file: {e}")
        except OSError as e:
            logger.error(f"OS error loading performance history: {e}")
            raise BackendError(f"System error loading performance history: {e}")
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        """Save performance history with comprehensive error handling."""
        try:
            self.data_paths["performance-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["performance-history"], "w", encoding="utf-8") as f:
                f.write("# Performance History\n\n")
                f.writelines(f"- {perf}\n" for perf in self.performance_history[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving performance history: {e}")
            raise BackendError(f"Cannot write to performance history file: {e}")
        except OSError as e:
            logger.error(f"OS error saving performance history: {e}")
            raise BackendError(f"System error saving performance history: {e}")
        except Exception as e:
            logger.error(f"Could not save performance history: {e}")

    def _load_deployment_history(self):
        """Load deployment history with comprehensive error handling."""
        try:
            if self.data_paths["deployment-history"].exists():
                with open(self.data_paths["deployment-history"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.deployment_history.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading deployment history: {e}")
            raise BackendError(f"Cannot access deployment history file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading deployment history: {e}")
            raise BackendError(f"Invalid encoding in deployment history file: {e}")
        except OSError as e:
            logger.error(f"OS error loading deployment history: {e}")
            raise BackendError(f"System error loading deployment history: {e}")
        except Exception as e:
            logger.warning(f"Could not load deployment history: {e}")

    def _save_deployment_history(self):
        """Save deployment history with comprehensive error handling."""
        try:
            self.data_paths["deployment-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["deployment-history"], "w", encoding="utf-8") as f:
                f.write("# Deployment History\n\n")
                f.writelines(f"- {deploy}\n" for deploy in self.deployment_history[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving deployment history: {e}")
            raise BackendError(f"Cannot write to deployment history file: {e}")
        except OSError as e:
            logger.error(f"OS error saving deployment history: {e}")
            raise BackendError(f"System error saving deployment history: {e}")
        except Exception as e:
            logger.error(f"Could not save deployment history: {e}")

    def _record_backend_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record backend-specific metrics."""
        try:
            self.monitor._record_metric(self.agent_name, MetricType.SUCCESS_RATE, value, unit)
        except Exception as e:
            logger.warning(f"Could not record metric {metric_name}: {e}")

    def show_help(self):
        """Display help information."""
        help_text = """
BackendDeveloper Agent Commands:
  help                    - Show this help message
  build-api [endpoint]    - Build or update API endpoint
  deploy-api [endpoint]   - Deploy API endpoint
  show-api-history        - Show API history
  show-performance        - Show performance metrics
  show-deployment-history - Show deployment history
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-api [format]     - Export API documentation (md, json, yaml, html)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Start the agent in event listening mode
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content with comprehensive error handling."""
        try:
            self._validate_input(resource_type, str, "resource_type")
            
            if not resource_type.strip():
                raise BackendValidationError("Resource type cannot be empty")
            
            resource_mapping = {
                "best-practices": self.template_paths["best-practices"],
                "changelog": self.data_paths["changelog"],
                "performance-report": self.template_paths["performance-report"],
                "security-template": self.template_paths["security-template"],
                "deployment-template": self.template_paths["deployment-template"]
            }
            
            if resource_type not in resource_mapping:
                print(f"Unknown resource type: {resource_type}")
                print(f"Available resources: {list(resource_mapping.keys())}")
                return
                
            path = resource_mapping[resource_type]
            
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except PermissionError as e:
            logger.error(f"Permission denied reading resource {resource_type}: {e}")
            print(f"Permission denied accessing resource: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error reading resource {resource_type}: {e}")
            print(f"Invalid encoding in resource file: {e}")
        except OSError as e:
            logger.error(f"OS error reading resource {resource_type}: {e}")
            print(f"System error reading resource: {e}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")
            print(f"Error reading resource: {e}")

    def show_api_history(self):
        """Show API history."""
        if not self.api_history:
            print("No API history available.")
            return
        print("API History:")
        print("=" * 50)
        for i, api in enumerate(self.api_history[-10:], 1):
            print(f"{i}. {api}")

    def show_performance(self):
        """Show performance history."""
        if not self.performance_history:
            print("No performance history available.")
            return
        print("Performance History:")
        print("=" * 50)
        for i, perf in enumerate(self.performance_history[-10:], 1):
            print(f"{i}. {perf}")

    def show_deployment_history(self):
        """Show deployment history."""
        if not self.deployment_history:
            print("No deployment history available.")
            return
        print("Deployment History:")
        print("=" * 50)
        for i, deploy in enumerate(self.deployment_history[-10:], 1):
            print(f"{i}. {deploy}")

    async def build_api(self, endpoint: str = "/api/v1/users") -> Dict[str, Any]:
        """Build API endpoint with comprehensive validation and MCP enhancement."""
        try:
            self._validate_endpoint(endpoint)
            
            logger.info(f"Building API endpoint: {endpoint}")

            # Use MCP tools for enhanced API development
            backend_data = {
                "endpoint": endpoint,
                "method": "GET",
                "framework": "fastapi",
                "development_type": "comprehensive",
                "database_type": "postgresql",
                "schema_requirements": {"users": ["id", "name", "email"]},
                "scalability": "medium",
                "security_level": "standard",
                "authentication": "jwt",
                "authorization": "rbac",
                "compliance": ["gdpr", "sox"],
                "performance_metrics": {"response_time": 100, "throughput": 1000},
                "target_latency": 100,
                "scaling_strategy": "horizontal"
            }
            
            enhanced_data = await self.use_backend_specific_mcp_tools(backend_data)

            # Simulate API building process
            time.sleep(2)
            
            result = {
                "endpoint": endpoint,
                "method": "GET",
                "status": "built",
                "framework": "FastAPI",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "agent": "BackendDeveloperAgent",
                "api_spec": {
                    "openapi": "3.0.0",
                    "info": {
                        "title": f"API for {endpoint}",
                        "version": "1.0.0",
                        "description": "Auto-generated API endpoint"
                    },
                    "paths": {
                        endpoint: {
                            "get": {
                                "summary": f"Get data from {endpoint}",
                                "responses": {
                                    "200": {
                                        "description": "Successful response",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "data": {"type": "array"},
                                                        "status": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "database_schema": {
                    "tables": ["users", "sessions", "logs"],
                    "relationships": ["one_to_many", "many_to_many"],
                    "indexes": ["primary_key", "foreign_key", "unique_constraints"]
                },
                "security_config": {
                    "authentication": "JWT",
                    "authorization": "RBAC",
                    "rate_limiting": "enabled",
                    "cors": "configured",
                    "ssl": "enabled"
                },
                "performance_config": {
                    "caching": "redis",
                    "load_balancing": "nginx",
                    "monitoring": "prometheus",
                    "logging": "structured"
                }
            }

            # Add MCP enhanced data if available
            if enhanced_data:
                result["mcp_enhanced_data"] = enhanced_data
                result["mcp_enhanced"] = True

            # Add to history
            api_entry = f"{result['timestamp']}: {result['method']} {endpoint} - Status: {result['status']}"
            self.api_history.append(api_entry)
            self._save_api_history()

            # Update metrics
            self.performance_metrics["total_apis"] += 1
            self._record_backend_metric("api_build_success", 95, "%")

            logger.info(f"API build result: {result}")
            return result
            
        except BackendValidationError as e:
            logger.error(f"Validation error building API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error building API: {e}")
            self._record_backend_metric("api_build_error", 5, "%")
            raise BackendError(f"Failed to build API: {e}")

    def deploy_api(self, endpoint: str = "/api/v1/users") -> Dict[str, Any]:
        """Deploy API endpoint with comprehensive validation and error handling."""
        try:
            self._validate_endpoint(endpoint)
            
            logger.info(f"Deploying API endpoint: {endpoint}")

            # Simulate deployment process
            time.sleep(2)
            
            result = {
                "endpoint": endpoint,
                "status": "deployed",
                "environment": "production",
                "deployment_time": datetime.now().isoformat(),
                "agent": "BackendDeveloperAgent",
                "health_check": "passed",
                "load_balancer": "configured",
                "monitoring": "enabled"
            }

            # Add to deployment history
            deploy_entry = f"{result['deployment_time']}: {endpoint} - Status: {result['status']} - Environment: {result['environment']}"
            self.deployment_history.append(deploy_entry)
            self._save_deployment_history()

            # Update metrics
            self.performance_metrics["deployment_success_rate"] = 98.5
            self._record_backend_metric("deployment_success", 98.5, "%")

            logger.info(f"API deployment result: {result}")
            return result
            
        except BackendValidationError as e:
            logger.error(f"Validation error deploying API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deploying API: {e}")
            self._record_backend_metric("deployment_error", 1.5, "%")
            raise BackendError(f"Failed to deploy API: {e}")

    def export_api(self, format_type: str = "md", api_data: Optional[Dict] = None):
        """Export API documentation with comprehensive validation and error handling."""
        try:
            self._validate_export_format(format_type)
            
            if not api_data:
                if self.api_history:
                    endpoint = self.api_history[-1].split(": ")[1].split(" - ")[0]
                    api_data = self.build_api(endpoint)
                else:
                    api_data = self.build_api()

            self._validate_api_data(api_data)

            if format_type.lower() == "md":
                self._export_markdown(api_data)
            elif format_type.lower() == "json":
                self._export_json(api_data)
            elif format_type.lower() == "yaml":
                self._export_yaml(api_data)
            elif format_type.lower() == "html":
                self._export_html(api_data)
            else:
                print(f"Unsupported format: {format_type}")
                
        except BackendValidationError as e:
            logger.error(f"Validation error exporting API: {e}")
            print(f"Validation error: {e}")
        except Exception as e:
            logger.error(f"Error exporting API: {e}")
            print(f"Export error: {e}")

    def _export_markdown(self, api_data: Dict):
        """Export API documentation to Markdown format."""
        try:
            template_path = self.template_paths["api-export-md"]
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    template = f.read()

                # Fill template
                content = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
                content = content.replace("{{endpoints}}", f"- {api_data['method']} {api_data['endpoint']}")
                content = content.replace("{{performance_metrics}}", f"- Response time: {api_data['response_time']}\n- Throughput: {api_data['throughput']}")
                content = content.replace("{{security_status}}", "- Authentication: enabled\n- Rate limiting: enabled")
                content = content.replace("{{database_status}}", "- Connection pool: healthy\n- Query performance: optimal")

                # Save to file
                output_file = f"api_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"API export saved to: {output_file}")
            else:
                print("Markdown template not found")
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            raise BackendError(f"Failed to export to Markdown: {e}")

    def _export_json(self, api_data: Dict):
        """Export API documentation to JSON format."""
        try:
            output_file = f"api_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(api_data, f, indent=2, ensure_ascii=False)

            print(f"API export saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise BackendError(f"Failed to export to JSON: {e}")

    def _export_yaml(self, api_data: Dict):
        """Export API documentation to YAML format."""
        try:
            import yaml
            output_file = f"api_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(api_data, f, default_flow_style=False, allow_unicode=True)

            print(f"API export saved to: {output_file}")
        except ImportError:
            print("YAML export requires PyYAML package")
        except Exception as e:
            logger.error(f"Error exporting to YAML: {e}")
            raise BackendError(f"Failed to export to YAML: {e}")

    def _export_html(self, api_data: Dict):
        """Export API documentation to HTML format."""
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .endpoint {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .metric {{ color: #666; }}
    </style>
</head>
<body>
    <h1>API Documentation</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="endpoint">
        <h2>{api_data['method']} {api_data['endpoint']}</h2>
        <p><strong>Status:</strong> {api_data['status']}</p>
        <p class="metric"><strong>Response Time:</strong> {api_data['response_time']}</p>
        <p class="metric"><strong>Throughput:</strong> {api_data['throughput']}</p>
    </div>
</body>
</html>
            """
            
            output_file = f"api_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"API export saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error exporting to HTML: {e}")
            raise BackendError(f"Failed to export to HTML: {e}")

    def test_resource_completeness(self):
        """Test resource completeness with detailed reporting."""
        print("Testing resource completeness...")
        missing_resources = []

        for name, path in self.template_paths.items():
            if not path.exists():
                missing_resources.append(f"Template: {name} ({path})")

        for name, path in self.data_paths.items():
            if not path.exists():
                missing_resources.append(f"Data: {name} ({path})")

        if missing_resources:
            print("Missing resources:")
            for resource in missing_resources:
                print(f"  - {resource}")
            return False
        else:
            print("All resources are available!")
            return True

    def collaborate_example(self):
        """Demonstrate collaboration with other agents."""
        logger.info("Starting collaboration example...")

        try:
            # Publish API change request
            publish("api_change_requested", {
                "agent": "BackendDeveloperAgent",
                "endpoint": "/api/v1/users",
                "timestamp": datetime.now().isoformat()
            })

            # Build API
            api_result = self.build_api("/api/v1/users")

            # Deploy API
            deploy_result = self.deploy_api("/api/v1/users")

            # Publish completion
            publish("api_change_completed", api_result)
            publish("api_deployment_completed", deploy_result)

            # Notify via Slack
            try:
                send_slack_message(f"API endpoint {api_result['endpoint']} created and deployed successfully")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")

            logger.info("Collaboration example completed successfully")
            
        except Exception as e:
            logger.error(f"Error in collaboration example: {e}")
            raise BackendError(f"Collaboration example failed: {e}")

    def handle_api_change_requested(self, event):
        """Handle API change requested event."""
        try:
            logger.info(f"API change requested: {event}")
            endpoint = event.get("endpoint", "/api/v1/users")
            self.build_api(endpoint)
        except Exception as e:
            logger.error(f"Error handling API change request: {e}")

    async def handle_api_change_completed(self, event):
        """Handle API change completed event."""
        try:
            logger.info(f"API change completed: {event}")

            # Record event in tracing
            self.tracer.record_event("api_change_completed", event)

            # Evaluate policy
            try:
                allowed = await self.policy_engine.evaluate_policy("api_change", event)
                logger.info(f"Policy evaluation result: {allowed}")
            except Exception as e:
                logger.error(f"Policy evaluation failed: {e}")
                
        except Exception as e:
            logger.error(f"Error handling API change completed: {e}")

    def handle_api_deployment_requested(self, event):
        """Handle API deployment requested event."""
        try:
            logger.info(f"API deployment requested: {event}")
            endpoint = event.get("endpoint", "/api/v1/users")
            self.deploy_api(endpoint)
        except Exception as e:
            logger.error(f"Error handling API deployment request: {e}")

    async def handle_api_deployment_completed(self, event):
        """Handle API deployment completed event."""
        try:
            logger.info(f"API deployment completed: {event}")

            # Record event in tracing
            self.tracer.record_event("api_deployment_completed", event)

            # Evaluate policy
            try:
                allowed = await self.policy_engine.evaluate_policy("api_deployment", event)
                logger.info(f"Policy evaluation result: {allowed}")
            except Exception as e:
                logger.error(f"Policy evaluation failed: {e}")
                
        except Exception as e:
            logger.error(f"Error handling API deployment completed: {e}")

    async def run(self):
        """Start the agent in event listening mode met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        def sync_handler(event):
            asyncio.run(self.handle_api_change_completed(event))

        def sync_deployment_handler(event):
            asyncio.run(self.handle_api_deployment_completed(event))

        subscribe("api_change_completed", sync_handler)
        subscribe("api_change_requested", self.handle_api_change_requested)
        subscribe("api_deployment_completed", sync_deployment_handler)
        subscribe("api_deployment_requested", self.handle_api_deployment_requested)

        logger.info("BackendDeveloperAgent ready and listening for events...")
        print("🔧 BackendDeveloper Agent is running...")
        print("Listening for events: api_change_completed, api_change_requested, api_deployment_completed, api_deployment_requested")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 BackendDeveloper Agent stopped.")

    @classmethod
    async def run_agent(cls):
        """Class method to run the BackendDeveloper agent met MCP integration."""
        agent = cls()
        await agent.run()

def main():
    """Main CLI function with comprehensive error handling."""
    parser = argparse.ArgumentParser(description="BackendDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "build-api", "deploy-api", "show-api-history", "show-performance",
                               "show-deployment-history", "show-best-practices", "show-changelog", "export-api",
                               "test", "collaborate", "run"])
    parser.add_argument("--endpoint", default="/api/v1/users", help="API endpoint")
    parser.add_argument("--format", choices=["md", "json", "yaml", "html"], default="md", help="Export format")

    args = parser.parse_args()

    try:
        agent = BackendDeveloperAgent()

        if args.command == "help":
            agent.show_help()
        elif args.command == "build-api":
            result = asyncio.run(agent.build_api(args.endpoint))
            print(f"API built successfully: {result}")
        elif args.command == "deploy-api":
            result = agent.deploy_api(args.endpoint)
            print(f"API deployed successfully: {result}")
        elif args.command == "show-api-history":
            agent.show_api_history()
        elif args.command == "show-performance":
            agent.show_performance()
        elif args.command == "show-deployment-history":
            agent.show_deployment_history()
        elif args.command == "show-best-practices":
            agent.show_resource("best-practices")
        elif args.command == "show-changelog":
            agent.show_resource("changelog")
        elif args.command == "export-api":
            agent.export_api(args.format)
        elif args.command == "test":
            success = agent.test_resource_completeness()
            if success:
                print("Resource completeness test passed!")
            else:
                print("Resource completeness test failed!")
        elif args.command == "collaborate":
            agent.collaborate_example()
        elif args.command == "run":
            asyncio.run(agent.run())
        else:
            print("Unknown command. Use 'help' to see available commands.")
            sys.exit(1)

    except BackendError as e:
        logger.error(f"Backend error: {e}")
        print(f"❌ Backend error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
