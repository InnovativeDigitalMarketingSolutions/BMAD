import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
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

# Enhanced MCP Integration for Phase 2
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)

# Tracing Integration
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer

# Message Bus Integration
from bmad.agents.core.communication.agent_message_bus_integration import (
    AgentMessageBusIntegration,
    create_agent_message_bus_integration
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DevOpsInfraAgent(AgentMessageBusIntegration):
    """
    DevOps Infrastructure Agent voor BMAD.
    Gespecialiseerd in infrastructure management, CI/CD pipelines, en deployment automation.
    """
    
    def __init__(self):
        # Initialize parent class with agent name and instance
        super().__init__("DevOpsInfra", self)
        
        self.framework_manager = get_framework_templates_manager()
        try:
            self.devops_template = self.framework_manager.get_framework_template('devops')
        except:
            self.devops_template = None
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "DevOpsInfra"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/devopsinfra/best-practices.md",
            "pipeline-template": self.resource_base / "templates/devopsinfra/pipeline-template.yaml",
            "monitoring-template": self.resource_base / "templates/devopsinfra/monitoring-template.md",
            "incident-response": self.resource_base / "templates/devopsinfra/incident-response-template.md",
            "deployment-template": self.resource_base / "templates/devopsinfra/deployment-template.yaml",
            "infrastructure-template": self.resource_base / "templates/devopsinfra/infrastructure-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/devopsinfra/changelog.md",
            "history": self.resource_base / "data/devopsinfra/infrastructure-history.md",
            "incident-history": self.resource_base / "data/devopsinfra/incident-history.md"
        }

        # Initialize history
        self.infrastructure_history = []
        self.incident_history = []
        self._load_infrastructure_history()
        self._load_incident_history()
        
        # Performance metrics
        self.performance_metrics = {
            "pipeline_execution_time": 0.0,
            "deployment_success_rate": 0.0,
            "incident_response_time": 0.0,
            "infrastructure_uptime": 0.0,
            "monitoring_accuracy": 0.0,
            "automation_level": 0.0,
            "security_compliance_score": 0.0,
            "resource_utilization": 0.0,
            "deployment_frequency": 0.0,
            "mean_time_to_recovery": 0.0,
            "change_failure_rate": 0.0,
            "lead_time_for_changes": 0.0
        }
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Integration for Phase 2
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        self.enhanced_mcp_client = None
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Message Bus Integration
        self.message_bus_integration: Optional[AgentMessageBusIntegration] = None
        self.message_bus_enabled = False
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced DevOps capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for DevOpsInfra")
        except Exception as e:
            logger.warning(f"MCP initialization failed for DevOpsInfra: {e}")
            self.mcp_enabled = False

    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            if self.enhanced_mcp_enabled:
                logger.info("Enhanced MCP capabilities initialized successfully for DevOpsInfra")
            else:
                logger.warning("Enhanced MCP initialization failed, falling back to standard MCP")
                
        except Exception as e:
            logger.warning(f"Enhanced MCP initialization failed for DevOpsInfra: {e}")
            self.enhanced_mcp_enabled = False

    async def initialize_tracing(self):
        """Initialize tracing capabilities for DevOps infrastructure."""
        try:
            self.tracer = BMADTracer(config=type("Config", (), {
                "service_name": f"{self.agent_name}",
                "environment": "development",
                "tracing_level": "detailed"
            })())
            self.tracing_enabled = await self.tracer.initialize()
            
            if self.tracing_enabled:
                logger.info("Tracing capabilities initialized successfully for DevOpsInfra")
                # Set up DevOps-specific tracing spans
                await self.tracer.setup_devops_tracing({
                    "agent_name": self.agent_name,
                    "tracing_level": "detailed",
                    "infrastructure_tracking": True,
                    "pipeline_tracking": True,
                    "incident_tracking": True,
                    "deployment_tracking": True
                })
            else:
                logger.warning("Tracing initialization failed, continuing without tracing")
                
        except Exception as e:
            logger.warning(f"Tracing initialization failed for DevOpsInfra: {e}")
            self.tracing_enabled = False

    async def initialize_message_bus_integration(self):
        """Initialize Message Bus Integration for the agent."""
        try:
            self.message_bus_integration = create_agent_message_bus_integration(
                agent_name=self.agent_name,
                agent_instance=self
            )
            
            # Register event handlers for DevOps-specific events
            await self.message_bus_integration.register_event_handler(
                "pipeline_advice_requested", 
                self.on_pipeline_advice_requested
            )
            await self.message_bus_integration.register_event_handler(
                "incident_response_requested", 
                self.on_incident_response_requested
            )
            await self.message_bus_integration.register_event_handler(
                "infrastructure_deployment_requested",
                self.handle_infrastructure_deployment_requested
            )
            await self.message_bus_integration.register_event_handler(
                "infrastructure_monitoring_requested",
                self.handle_monitoring_requested
            )
            
            self.message_bus_enabled = True
            logger.info(f"✅ Message Bus Integration geïnitialiseerd voor {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Fout bij initialiseren van Message Bus Integration voor {self.agent_name}: {e}")
            return False
    
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
    
    async def use_devops_specific_mcp_tools(self, devops_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use DevOps-specific MCP tools voor infrastructure enhancement."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Infrastructure analysis
            if "infrastructure_analysis" in self.mcp_config.custom_tools:
                analysis_result = await self.use_mcp_tool("infrastructure_analysis", {
                    "infrastructure": devops_data.get("infrastructure", ""),
                    "pipeline": devops_data.get("pipeline", ""),
                    "analysis_type": "performance"
                })
                if analysis_result:
                    enhanced_data["infrastructure_analysis"] = analysis_result
            
            # Deployment optimization
            if "deployment_optimization" in self.mcp_config.custom_tools:
                optimization_result = await self.use_mcp_tool("deployment_optimization", {
                    "deployment_config": devops_data.get("deployment_config", {}),
                    "performance_metrics": devops_data.get("performance_metrics", {})
                })
                if optimization_result:
                    enhanced_data["deployment_optimization"] = optimization_result
            
            # Monitoring enhancement
            monitoring_result = await self.use_mcp_tool("monitoring_enhancement", {
                "monitoring_config": devops_data.get("monitoring_config", {}),
                "alert_rules": devops_data.get("alert_rules", [])
            })
            if monitoring_result:
                enhanced_data["monitoring_enhancement"] = monitoring_result
            
            logger.info(f"DevOps-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in DevOps-specific MCP tools: {e}")
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_devops_specific_mcp_tools(agent_data)
        
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
        
        # DevOps-specific enhancement tools
        specific_result = await self.use_devops_specific_enhanced_tools(agent_data)
        if specific_result:
            enhanced_data.update(specific_result)
        
        return enhanced_data

    async def use_devops_specific_enhanced_tools(self, devops_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use DevOps-specific enhanced MCP tools."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {}
        
        enhanced_data = {}
        
        # Infrastructure deployment enhancement
        infrastructure_result = await self.enhanced_mcp.use_enhanced_mcp_tool("infrastructure_deployment", {
            "infrastructure_type": devops_data.get("infrastructure_type", "kubernetes"),
            "deployment_strategy": devops_data.get("deployment_strategy", "blue-green"),
            "monitoring_config": devops_data.get("monitoring_config", {}),
            "security_config": devops_data.get("security_config", {})
        })
        if infrastructure_result:
            enhanced_data["infrastructure_deployment"] = infrastructure_result
        
        # Pipeline optimization enhancement
        pipeline_result = await self.enhanced_mcp.use_enhanced_mcp_tool("pipeline_optimization", {
            "pipeline_type": devops_data.get("pipeline_type", "ci-cd"),
            "optimization_focus": devops_data.get("optimization_focus", "performance"),
            "automation_level": devops_data.get("automation_level", "high"),
            "monitoring_integration": devops_data.get("monitoring_integration", {})
        })
        if pipeline_result:
            enhanced_data["pipeline_optimization"] = pipeline_result
        
        # Incident response enhancement
        incident_result = await self.enhanced_mcp.use_enhanced_mcp_tool("incident_response", {
            "incident_type": devops_data.get("incident_type", "infrastructure"),
            "severity_level": devops_data.get("severity_level", "medium"),
            "response_strategy": devops_data.get("response_strategy", "automated"),
            "communication_plan": devops_data.get("communication_plan", {})
        })
        if incident_result:
            enhanced_data["incident_response"] = incident_result
        
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
        """Enhanced security validation for DevOps infrastructure."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {"error": "Enhanced MCP not available"}
        
        try:
            return await self.enhanced_mcp.enhanced_security_validation(security_data)
        except Exception as e:
            logger.error(f"Enhanced security validation failed: {e}")
            return {"error": str(e)}

    async def enhanced_performance_optimization(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced performance optimization for DevOps infrastructure."""
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

    async def trace_infrastructure_deployment(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace infrastructure deployment process."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for infrastructure deployment")
            return {}
        
        try:
            trace_result = await self.tracer.trace_infrastructure_deployment({
                "infrastructure_type": deployment_data.get("infrastructure_type", "kubernetes"),
                "deployment_strategy": deployment_data.get("deployment_strategy", "blue-green"),
                "environment": deployment_data.get("environment", "production"),
                "resources": deployment_data.get("resources", {}),
                "monitoring_config": deployment_data.get("monitoring_config", {}),
                "security_config": deployment_data.get("security_config", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Infrastructure deployment traced: {deployment_data.get('infrastructure_type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Infrastructure deployment tracing failed: {e}")
            return {}

    async def trace_pipeline_optimization(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace pipeline optimization process."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for pipeline optimization")
            return {}
        
        try:
            trace_result = await self.tracer.trace_pipeline_optimization({
                "pipeline_type": pipeline_data.get("pipeline_type", "ci-cd"),
                "optimization_focus": pipeline_data.get("optimization_focus", "performance"),
                "automation_level": pipeline_data.get("automation_level", "high"),
                "before_metrics": pipeline_data.get("before_metrics", {}),
                "after_metrics": pipeline_data.get("after_metrics", {}),
                "monitoring_integration": pipeline_data.get("monitoring_integration", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Pipeline optimization traced: {pipeline_data.get('pipeline_type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Pipeline optimization tracing failed: {e}")
            return {}

    async def trace_incident_response(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace incident response process."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for incident response")
            return {}
        
        try:
            trace_result = await self.tracer.trace_incident_response({
                "incident_type": incident_data.get("incident_type", "infrastructure"),
                "severity_level": incident_data.get("severity_level", "medium"),
                "response_strategy": incident_data.get("response_strategy", "automated"),
                "detection_time": incident_data.get("detection_time", ""),
                "resolution_time": incident_data.get("resolution_time", ""),
                "communication_plan": incident_data.get("communication_plan", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Incident response traced: {incident_data.get('incident_type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"Incident response tracing failed: {e}")
            return {}

    async def trace_devops_error(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace DevOps errors and exceptions."""
        if not self.tracing_enabled or not self.tracer:
            logger.warning("Tracing not available for DevOps errors")
            return {}
        
        try:
            trace_result = await self.tracer.trace_devops_error({
                "error_type": error_data.get("type", "unknown"),
                "error_message": error_data.get("message", ""),
                "infrastructure_component": error_data.get("infrastructure_component", ""),
                "pipeline_stage": error_data.get("pipeline_stage", ""),
                "stack_trace": error_data.get("stack_trace", ""),
                "impact_assessment": error_data.get("impact_assessment", {}),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"DevOps error traced: {error_data.get('type', 'unknown')}")
            return trace_result
            
        except Exception as e:
            logger.error(f"DevOps error tracing failed: {e}")
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

    def _load_infrastructure_history(self):
        """Load infrastructure history from data file"""
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            # Support both string and dictionary formats
                            entry = line.strip()[2:]
                            try:
                                # Try to parse as JSON (dictionary)
                                import json
                                parsed_entry = json.loads(entry)
                                self.infrastructure_history.append(parsed_entry)
                            except (json.JSONDecodeError, ValueError):
                                # Fall back to string format
                                self.infrastructure_history.append(entry)
        except Exception as e:
            logger.warning(f"Could not load infrastructure history: {e}")

    def _save_infrastructure_history(self):
        """Save infrastructure history to data file"""
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Infrastructure History\n\n")
                for infra in self.infrastructure_history[-50:]:  # Keep last 50 entries
                    if isinstance(infra, dict):
                        import json
                        f.write(f"- {json.dumps(infra)}\n")
                    else:
                        f.write(f"- {infra}\n")
        except Exception as e:
            logger.error(f"Could not save infrastructure history: {e}")

    def _load_incident_history(self):
        """Load incident history from data file"""
        try:
            if self.data_paths["incident-history"].exists():
                with open(self.data_paths["incident-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            # Support both string and dictionary formats
                            entry = line.strip()[2:]
                            try:
                                # Try to parse as JSON (dictionary)
                                import json
                                parsed_entry = json.loads(entry)
                                self.incident_history.append(parsed_entry)
                            except (json.JSONDecodeError, ValueError):
                                # Fall back to string format
                                self.incident_history.append(entry)
        except Exception as e:
            logger.warning(f"Could not load incident history: {e}")

    def _save_incident_history(self):
        """Save incident history to data file"""
        try:
            self.data_paths["incident-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["incident-history"], "w") as f:
                f.write("# Incident History\n\n")
                for incident in self.incident_history[-50:]:  # Keep last 50 incidents
                    if isinstance(incident, dict):
                        import json
                        f.write(f"- {json.dumps(incident)}\n")
                    else:
                        f.write(f"- {incident}\n")
        except Exception as e:
            logger.error(f"Could not save incident history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
DevOps Infrastructure Agent Commands:
  help                    - Show this help message
  pipeline-advice         - Get CI/CD pipeline optimization advice
  incident-response       - Generate incident response plan
  deploy-infrastructure   - Deploy infrastructure components
  monitor-infrastructure  - Monitor infrastructure health
  show-infrastructure-history - Show infrastructure history
  show-incident-history   - Show incident history
  show-best-practices     - Show DevOps best practices
  show-changelog          - Show infrastructure changelog
  export-report [format]  - Export infrastructure report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Run the agent with full integration

Enhanced MCP Phase 2 Commands:
  enhanced-collaborate    - Enhanced collaboration with other agents
  enhanced-security       - Enhanced security validation
  enhanced-performance    - Enhanced performance optimization
  trace-operation         - Trace infrastructure operations
  trace-performance       - Trace performance metrics
  trace-error             - Trace error analysis
  tracing-summary         - Show tracing status

Message Bus Integration Commands:
  initialize-message-bus  - Initialize Message Bus integration
  message-bus-status      - Show Message Bus status
  publish-event           - Publish infrastructure event
  subscribe-event         - Show subscribed events
  list-events             - List supported events
  event-history           - Show event history
  performance-metrics     - Show performance metrics
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "pipeline-template":
                path = self.template_paths["pipeline-template"]
            elif resource_type == "monitoring-template":
                path = self.template_paths["monitoring-template"]
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

    def show_infrastructure_history(self):
        """Show infrastructure history"""
        if not self.infrastructure_history:
            print("No infrastructure history available.")
            return
        print("Infrastructure History:")
        print("=" * 50)
        for i, infra in enumerate(self.infrastructure_history[-10:], 1):
            print(f"{i}. {infra}")

    def show_incident_history(self):
        """Show incident history"""
        if not self.incident_history:
            print("No incident history available.")
            return
        print("Incident History:")
        print("=" * 50)
        for i, incident in enumerate(self.incident_history[-10:], 1):
            print(f"{i}. {incident}")

    def pipeline_advice(self, pipeline_config: str = "Sample CI/CD pipeline") -> Dict[str, Any]:
        """Get CI/CD pipeline optimization advice with enhanced functionality."""
        logger.info("Analyzing CI/CD pipeline configuration")

        # Simulate pipeline analysis
        time.sleep(1)

        advice_result = {
            "pipeline_config": pipeline_config,
            "analysis_type": "CI/CD Pipeline Optimization",
            "overall_score": 85,
            "analysis_results": {
                "build_optimization": {
                    "score": 88,
                    "status": "GOOD",
                    "findings": "Build process is well-structured"
                },
                "test_coverage": {
                    "score": 92,
                    "status": "EXCELLENT",
                    "findings": "Comprehensive test coverage"
                },
                "deployment_strategy": {
                    "score": 78,
                    "status": "NEEDS_IMPROVEMENT",
                    "findings": "Could benefit from blue-green deployment"
                },
                "security_scanning": {
                    "score": 82,
                    "status": "GOOD",
                    "findings": "Basic security scanning implemented"
                }
            },
            "optimization_suggestions": [
                {
                    "category": "deployment",
                    "suggestion": "Implement blue-green deployment strategy",
                    "impact": "high",
                    "effort": "medium",
                    "priority": "high"
                },
                {
                    "category": "security",
                    "suggestion": "Add automated security scanning in pipeline",
                    "impact": "high",
                    "effort": "low",
                    "priority": "high"
                },
                {
                    "category": "performance",
                    "suggestion": "Optimize build cache usage",
                    "impact": "medium",
                    "effort": "low",
                    "priority": "medium"
                }
            ],
            "estimated_improvements": {
                "deployment_time": "30% reduction",
                "failure_rate": "50% reduction",
                "security_vulnerabilities": "80% reduction"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "DevOpsInfraAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("DevOpsInfra", MetricType.SUCCESS_RATE, advice_result["overall_score"], "%")

        # Add to infrastructure history
        infra_entry = f"{datetime.now().isoformat()}: Pipeline analysis completed with {advice_result['overall_score']}% score"
        self.infrastructure_history.append(infra_entry)
        self._save_infrastructure_history()

        logger.info(f"Pipeline advice completed: {advice_result}")
        return advice_result

    def incident_response(self, incident_desc: str = "Sample incident description") -> Dict[str, Any]:
        """Generate incident response plan with enhanced functionality."""
        logger.info("Generating incident response plan")

        # Simulate incident response generation
        time.sleep(1)

        response_result = {
            "incident_description": incident_desc,
            "response_type": "Incident Response Plan",
            "severity_level": "medium",
            "response_plan": {
                "immediate_actions": [
                    "Isolate affected systems",
                    "Assess impact and scope",
                    "Notify stakeholders",
                    "Activate incident response team"
                ],
                "investigation_phase": [
                    "Gather system logs and metrics",
                    "Analyze root cause",
                    "Document incident timeline",
                    "Identify affected services"
                ],
                "remediation_phase": [
                    "Implement temporary fixes",
                    "Deploy permanent solutions",
                    "Verify system stability",
                    "Monitor for recurrence"
                ],
                "post_incident": [
                    "Conduct post-mortem analysis",
                    "Update runbooks and procedures",
                    "Implement preventive measures",
                    "Update monitoring and alerting"
                ]
            },
            "monitoring_recommendations": [
                "Add real-time alerting for similar issues",
                "Implement automated health checks",
                "Set up log aggregation and analysis",
                "Create incident response playbooks"
            ],
            "estimated_resolution_time": "2-4 hours",
            "required_resources": [
                "DevOps engineer",
                "System administrator",
                "Database administrator",
                "Security analyst"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "DevOpsInfraAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("DevOpsInfra", MetricType.SUCCESS_RATE, 90, "%")

        # Add to incident history
        incident_entry = f"{datetime.now().isoformat()}: Incident response plan generated for {incident_desc[:50]}..."
        self.incident_history.append(incident_entry)
        self._save_incident_history()

        logger.info(f"Incident response completed: {response_result}")
        return response_result

    async def deploy_infrastructure(self, infrastructure_type: str = "kubernetes") -> Dict[str, Any]:
        """Deploy infrastructure components with enhanced MCP and tracing capabilities."""
        
        # Initialize enhanced MCP and tracing if not already done
        if not self.enhanced_mcp_enabled:
            await self.initialize_enhanced_mcp()
        if not self.tracing_enabled:
            await self.initialize_tracing()

        # Policy evaluation for deployment approval
        event = {
            "action": "deploy_infrastructure",
            "infrastructure_type": infrastructure_type,
            "timestamp": datetime.now().isoformat(),
            "agent": "DevOpsInfra"
        }

        try:
            allowed = await self.policy_engine.evaluate_policy("deployment_approval", event)
            if not allowed:
                return {
                    "status": "denied",
                    "reason": "Deployment not approved by policy",
                    "infrastructure_type": infrastructure_type,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"Policy evaluation failed: {e}")
            # Continue without policy check if evaluation fails

        print(f"🚀 Deploying {infrastructure_type} infrastructure with enhanced MCP and tracing...")

        # Enhanced deployment configuration
        deployment_config = {
            "infrastructure_type": infrastructure_type,
            "deployment_strategy": "blue-green",
            "environment": "production",
            "monitoring_config": {
                "health_checks": True,
                "alerting": True,
                "metrics_collection": True,
                "log_aggregation": True
            },
            "security_config": {
                "network_policies": True,
                "rbac_enabled": True,
                "secrets_management": True,
                "vulnerability_scanning": True
            },
            "performance_config": {
                "auto_scaling": True,
                "load_balancing": True,
                "resource_optimization": True
            }
        }

        # Simulate deployment process with enhanced steps
        deployment_steps = [
            "Validating infrastructure configuration",
            "Running security compliance checks",
            "Checking resource availability",
            "Creating infrastructure components",
            "Configuring networking and security policies",
            "Setting up monitoring and alerting",
            "Configuring auto-scaling and load balancing",
            "Running comprehensive health checks",
            "Performing post-deployment validation"
        ]

        # Enhanced MCP deployment with tracing
        deployment_result = None
        trace_data = {}

        # Try enhanced MCP infrastructure deployment first
        if self.enhanced_mcp_enabled and self.enhanced_mcp:
            try:
                print("  🔧 Using enhanced MCP for infrastructure deployment...")
                
                # Use enhanced MCP tools for comprehensive deployment
                enhanced_result = await self.use_enhanced_mcp_tools({
                    "infrastructure_type": infrastructure_type,
                    "deployment_config": deployment_config,
                    "deployment_steps": deployment_steps,
                    "capabilities": ["infrastructure_deployment", "pipeline_optimization", "security_validation"],
                    "performance_metrics": {"target_deployment_time": "5s", "target_success_rate": "99%"}
                })
                
                if enhanced_result:
                    logger.info("Enhanced MCP infrastructure deployment completed")
                    deployment_result = enhanced_result.get("infrastructure_deployment", {})
                    deployment_result["enhanced_mcp_used"] = True
                    deployment_result["enhancements"] = enhanced_result
                else:
                    logger.warning("Enhanced MCP deployment failed, falling back to standard MCP")
                    deployment_result = None
                    
            except Exception as e:
                logger.warning(f"Enhanced MCP infrastructure deployment failed: {e}, falling back to standard MCP")
                deployment_result = None

        # Fallback to standard MCP if enhanced MCP failed
        if not deployment_result and self.mcp_enabled and self.mcp_client:
            try:
                print("  🔧 Using standard MCP for infrastructure deployment...")
                
                mcp_result = await self.use_mcp_tool("deploy_infrastructure", {
                    "infrastructure_type": infrastructure_type,
                    "deployment_steps": deployment_steps,
                    "include_monitoring": True,
                    "include_optimization": True,
                    "deployment_config": deployment_config
                })
                
                if mcp_result:
                    logger.info("Standard MCP-enhanced infrastructure deployment completed")
                    deployment_result = mcp_result.get("deployment_result", {})
                    deployment_result["mcp_enhanced"] = True
                else:
                    logger.warning("Standard MCP deployment failed, using local deployment")
                    deployment_result = None
                    
            except Exception as e:
                logger.warning(f"Standard MCP infrastructure deployment failed: {e}, using local deployment")
                deployment_result = None

        # Local deployment as final fallback
        if not deployment_result:
            print("  🔧 Using local deployment process...")
            
            for step in deployment_steps:
                print(f"    📋 {step}")
                time.sleep(0.3)  # Simulate processing time
            
            deployment_result = {
                "status": "success",
                "infrastructure_type": infrastructure_type,
                "deployment_steps": deployment_steps,
                "deployment_config": deployment_config,
                "timestamp": datetime.now().isoformat(),
                "agent": "DevOpsInfraAgent",
                "deployment_method": "local"
            }

        # Use DevOps-specific MCP tools for additional enhancement
        if self.mcp_enabled:
            try:
                devops_data = {
                    "infrastructure": infrastructure_type,
                    "pipeline": "deployment_pipeline",
                    "deployment_config": deployment_result,
                    "performance_metrics": {"deployment_time": "2.5s", "success_rate": "95%"},
                    "monitoring_config": deployment_config["monitoring_config"],
                    "security_config": deployment_config["security_config"],
                    "alert_rules": ["high_cpu", "high_memory", "service_down", "security_violation"]
                }
                devops_enhanced = await self.use_devops_specific_mcp_tools(devops_data)
                if devops_enhanced:
                    deployment_result["devops_enhancements"] = devops_enhanced
            except Exception as e:
                logger.warning(f"DevOps-specific MCP tools failed: {e}")

        # Enhanced tracing for deployment process
        if self.tracing_enabled:
            try:
                print("  📊 Tracing deployment process...")
                trace_data = await self.trace_infrastructure_deployment({
                    "infrastructure_type": infrastructure_type,
                    "deployment_strategy": deployment_config["deployment_strategy"],
                    "environment": deployment_config["environment"],
                    "resources": deployment_result.get("resources", {}),
                    "monitoring_config": deployment_config["monitoring_config"],
                    "security_config": deployment_config["security_config"],
                    "deployment_result": deployment_result
                })
                
                if trace_data:
                    deployment_result["tracing_data"] = trace_data
                    logger.info("Infrastructure deployment tracing completed")
                    
            except Exception as e:
                logger.warning(f"Deployment tracing failed: {e}")

        # Enhanced security validation
        if self.enhanced_mcp_enabled:
            try:
                print("  🔒 Running enhanced security validation...")
                security_result = await self.enhanced_security_validation({
                    "infrastructure_type": infrastructure_type,
                    "deployment_config": deployment_config,
                    "security_checks": ["network_policies", "rbac", "secrets", "vulnerabilities"]
                })
                
                if security_result and not security_result.get("error"):
                    deployment_result["security_validation"] = security_result
                    logger.info("Enhanced security validation completed")
                else:
                    logger.warning(f"Enhanced security validation failed: {security_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.warning(f"Enhanced security validation failed: {e}")

        # Enhanced performance optimization
        if self.enhanced_mcp_enabled:
            try:
                print("  ⚡ Running enhanced performance optimization...")
                performance_result = await self.enhanced_performance_optimization({
                    "infrastructure_type": infrastructure_type,
                    "deployment_config": deployment_config,
                    "optimization_targets": ["deployment_speed", "resource_efficiency", "scalability"]
                })
                
                if performance_result and not performance_result.get("error"):
                    deployment_result["performance_optimization"] = performance_result
                    logger.info("Enhanced performance optimization completed")
                else:
                    logger.warning(f"Enhanced performance optimization failed: {performance_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.warning(f"Enhanced performance optimization failed: {e}")

        # Record in history with enhanced information
        deployment_record = f"{infrastructure_type} infrastructure deployed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} with enhanced MCP and tracing"
        self.infrastructure_history.append(deployment_record)
        self._save_infrastructure_history()

        # Log performance metrics
        try:
            self.monitor._record_metric("DevOpsInfra", MetricType.SUCCESS_RATE, 95, "%")
            self.monitor._record_metric("DevOpsInfra", MetricType.DEPLOYMENT_TIME, 2.5, "seconds")
        except AttributeError:
            logger.info("Performance metrics recording not available")

        print(f"✅ {infrastructure_type} infrastructure deployed successfully with enhanced capabilities!")

        # Determine deployment method used
        deployment_method = "local"
        if deployment_result.get("enhanced_mcp_used"):
            deployment_method = "enhanced_mcp"
        elif deployment_result.get("mcp_enhanced"):
            deployment_method = "standard_mcp"

        # Prepare final result with all enhancements
        final_result = {
            "status": "success",
            "infrastructure_type": infrastructure_type,
            "deployment_steps": deployment_steps,
            "deployment_config": deployment_config,
            "timestamp": datetime.now().isoformat(),
            "history_record": deployment_record,
            "deployment_method": deployment_method,
            "enhanced_capabilities": {
                "enhanced_mcp_used": self.enhanced_mcp_enabled,
                "tracing_enabled": self.tracing_enabled,
                "security_validation": "security_validation" in deployment_result,
                "performance_optimization": "performance_optimization" in deployment_result
            }
        }

        # Add tracing data if available
        if "tracing_data" in deployment_result:
            final_result["tracing_data"] = deployment_result["tracing_data"]

        # Add security validation if available
        if "security_validation" in deployment_result:
            final_result["security_validation"] = deployment_result["security_validation"]

        # Add performance optimization if available
        if "performance_optimization" in deployment_result:
            final_result["performance_optimization"] = deployment_result["performance_optimization"]

        # Add DevOps enhancements if available
        if "devops_enhancements" in deployment_result:
            final_result["devops_enhancements"] = deployment_result["devops_enhancements"]

        return final_result

    async def setup_infrastructure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup infrastructure based on configuration."""
        try:
            # Initialize enhanced MCP if not already done
            if not self.enhanced_mcp_enabled:
                await self.initialize_enhanced_mcp()
            
            # Use enhanced MCP tools if available
            if self.enhanced_mcp_enabled and self.enhanced_mcp:
                result = await self.use_enhanced_mcp_tools({
                    "operation": "setup_infrastructure",
                    "config": config,
                    "environment": config.get("environment", "production"),
                    "services": config.get("services", []),
                    "capabilities": ["infrastructure_setup", "service_configuration", "monitoring_setup"]
                })
                if result:
                    return result
            
            # Fallback to local implementation
            return await asyncio.to_thread(self._setup_infrastructure_sync, config)
            
        except Exception as e:
            logging.error(f"Error in setup_infrastructure: {e}")
            return {
                "success": False,
                "error": str(e),
                "infrastructure": None
            }

    def _setup_infrastructure_sync(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous fallback for setup_infrastructure."""
        try:
            environment = config.get("environment", "production")
            services = config.get("services", [])
            
            # Simulate infrastructure setup
            setup_steps = [
                f"Setting up {environment} environment",
                "Configuring networking and security",
                "Setting up monitoring and logging",
                "Configuring load balancers",
                "Setting up databases and caches",
                "Configuring CI/CD pipelines",
                "Setting up backup and disaster recovery"
            ]
            
            # Add service-specific setup
            for service in services:
                setup_steps.append(f"Configuring {service} service")
            
            # Simulate setup process
            time.sleep(2)  # Simulate setup time
            
            return {
                "success": True,
                "infrastructure": {
                    "environment": environment,
                    "services": services,
                    "setup_steps": setup_steps,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                },
                "status": "completed"
            }
            
        except Exception as e:
            logging.error(f"Error in _setup_infrastructure_sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "infrastructure": None
            }

    def monitor_infrastructure(self, infrastructure_id: str = "infra_001") -> Dict[str, Any]:
        """Monitor infrastructure health."""
        logger.info(f"Monitoring infrastructure: {infrastructure_id}")

        # Simulate infrastructure monitoring
        time.sleep(1)

        monitoring_result = {
            "infrastructure_id": infrastructure_id,
            "monitoring_type": "Infrastructure Health Check",
            "overall_status": "healthy",
            "health_metrics": {
                "cpu_usage": {
                    "current": "45%",
                    "threshold": "80%",
                    "status": "healthy"
                },
                "memory_usage": {
                    "current": "62%",
                    "threshold": "85%",
                    "status": "healthy"
                },
                "disk_usage": {
                    "current": "38%",
                    "threshold": "90%",
                    "status": "healthy"
                },
                "network_usage": {
                    "current": "28%",
                    "threshold": "75%",
                    "status": "healthy"
                }
            },
            "service_status": {
                "kubernetes_api": "healthy",
                "etcd": "healthy",
                "kubelet": "healthy",
                "container_runtime": "healthy"
            },
            "alerts": [
                {
                    "type": "info",
                    "message": "High memory usage on node-2",
                    "severity": "low",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "recommendations": [
                "Consider scaling up memory on node-2",
                "Optimize application memory usage",
                "Review resource allocation policies"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "DevOpsInfraAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("DevOpsInfra", MetricType.SUCCESS_RATE, 95, "%")

        logger.info(f"Infrastructure monitoring completed: {monitoring_result}")
        return monitoring_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export infrastructure report in specified format."""
        if not report_data:
            report_data = {
                "report_type": "Infrastructure Report",
                "infrastructure_type": "Kubernetes",
                "overall_health": "healthy",
                "total_components": 12,
                "healthy_components": 11,
                "timestamp": datetime.now().isoformat(),
                "agent": "DevOpsInfraAgent"
            }

        try:
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "csv":
                self._export_csv(report_data)
            elif format_type == "json":
                self._export_json(report_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def _export_markdown(self, report_data: Dict):
        """Export report data as markdown."""
        output_file = f"infrastructure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Infrastructure Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Infrastructure Type**: {report_data.get('infrastructure_type', 'N/A')}
- **Overall Health**: {report_data.get('overall_health', 'N/A')}
- **Total Components**: {report_data.get('total_components', 0)}
- **Healthy Components**: {report_data.get('healthy_components', 0)}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Health Metrics
- **CPU Usage**: {report_data.get('health_metrics', {}).get('cpu_usage', {}).get('current', 'N/A')}
- **Memory Usage**: {report_data.get('health_metrics', {}).get('memory_usage', {}).get('current', 'N/A')}
- **Disk Usage**: {report_data.get('health_metrics', {}).get('disk_usage', {}).get('current', 'N/A')}
- **Network Usage**: {report_data.get('health_metrics', {}).get('network_usage', {}).get('current', 'N/A')}

## Service Status
{chr(10).join([f"- **{service}**: {status}" for service, status in report_data.get('service_status', {}).items()])}

## Alerts
{chr(10).join([f"- {alert.get('message', 'N/A')} ({alert.get('severity', 'N/A')})" for alert in report_data.get('alerts', [])])}
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        output_file = f"infrastructure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Overall Health", report_data.get("overall_health", "N/A")])
            writer.writerow(["Total Components", report_data.get("total_components", 0)])
            writer.writerow(["Healthy Components", report_data.get("healthy_components", 0)])

        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"infrastructure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Report export saved to: {output_file}")

    def test_resource_completeness(self):
        """Test if all required resources are available."""
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
        else:
            print("All resources are available!")

    async def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting DevOps infrastructure collaboration example...")

        # Publish infrastructure deployment request
        from bmad.core.message_bus.events import EventTypes
        await self.publish_agent_event(EventTypes.DEPLOYMENT_REQUESTED, {
            "agent": "DevOpsInfraAgent",
            "infrastructure_type": "kubernetes",
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
        })

        # Deploy infrastructure
        deployment_result = await self.deploy_infrastructure("kubernetes")

        # Generate pipeline advice
        advice_result = self.pipeline_advice("Sample CI/CD pipeline configuration")

        # Publish completion
        await self.publish_agent_event(EventTypes.DEPLOYMENT_COMPLETED, {
            "status": "completed",
            "agent": "DevOpsInfraAgent",
            "timestamp": datetime.now().isoformat(),
            "deployment_status": deployment_result["status"],
            "pipeline_score": advice_result["overall_score"]
        })

        # Save context
        save_context("DevOpsInfra", "status", {"infrastructure_status": "deployed"})

        # Notify via Slack
        try:
            send_slack_message(f"Infrastructure deployment completed with {advice_result['overall_score']}% pipeline score")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("DevOpsInfra")
        print(f"Opgehaalde context: {context}")

    async def on_pipeline_advice_requested(self, event):
        """Handle pipeline advice request from other agents."""
        try:
            logger.info(f"Pipeline advice requested: {event}")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for pipeline advice requested
            self.monitor.log_metric("pipeline_advice_requested", {
                "pipeline_config": event.get("pipeline_config", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update infrastructure history
            history_entry = {
                "action": "pipeline_advice_requested",
                "timestamp": datetime.now().isoformat(),
                "pipeline_config": event.get("pipeline_config", "Sample CI/CD pipeline"),
                "status": "processing"
            }
            self.infrastructure_history.append(history_entry)
            self._save_infrastructure_history()
            
            # Process pipeline advice request
            pipeline_config = event.get("pipeline_config", "Sample CI/CD pipeline")
            result = self.pipeline_advice(pipeline_config)
            
            # Publish follow-up event
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("pipeline_advice_completed", {
                        "pipeline_config": pipeline_config,
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    })
                except Exception as e:
                    logger.warning(f"Failed to publish pipeline_advice_completed event: {e}")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error in pipeline advice event handler: {e}")
            return None

    async def on_incident_response_requested(self, event):
        """Handle incident response request from other agents."""
        try:
            logger.info(f"Incident response requested: {event}")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for incident response requested
            self.monitor.log_metric("incident_response_requested", {
                "incident_desc": event.get("incident_desc", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update incident history
            incident_entry = {
                "action": "incident_response_requested",
                "timestamp": datetime.now().isoformat(),
                "incident_desc": event.get("incident_desc", "Sample incident description"),
                "status": "processing"
            }
            self.incident_history.append(incident_entry)
            self._save_incident_history()
            
            # Process incident response request
            incident_desc = event.get("incident_desc", "Sample incident description")
            result = self.incident_response(incident_desc)
            
            # Publish follow-up event
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("incident_response_completed", {
                        "incident_desc": incident_desc,
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    })
                except Exception as e:
                    logger.warning(f"Failed to publish incident_response_completed event: {e}")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error in incident response event handler: {e}")
            return None

    async def on_feedback_sentiment_analyzed(self, event):
        """Handle feedback sentiment analysis from other agents."""
        try:
            logger.info(f"Feedback sentiment analyzed: {event}")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for feedback sentiment analyzed
            self.monitor.log_metric("feedback_sentiment_analyzed", {
                "sentiment": event.get("sentiment", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update incident history for feedback processing
            feedback_entry = {
                "action": "feedback_sentiment_analyzed",
                "timestamp": datetime.now().isoformat(),
                "sentiment": event.get("sentiment", ""),
                "motivatie": event.get("motivatie", ""),
                "feedback": event.get("feedback", ""),
                "status": "processing"
            }
            self.incident_history.append(feedback_entry)
            self._save_incident_history()
            
            # Process feedback sentiment
            sentiment = event.get("sentiment", "")
            motivatie = event.get("motivatie", "")
            feedback = event.get("feedback", "")
            
            if sentiment == "negatief":
                prompt = f"Bedenk een DevOps-actie of monitoringvoorstel op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen het voorstel als JSON."
                structured_output = '{"devops_voorstel": "..."}'
                result = ask_openai(prompt, structured_output=structured_output)
                logger.info(f"[DevOpsInfra][LLM DevOps Voorstel]: {result}")
            
            # Publish follow-up event
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("feedback_processing_completed", {
                        "sentiment": sentiment,
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    })
                except Exception as e:
                    logger.warning(f"Failed to publish feedback_processing_completed event: {e}")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error in feedback sentiment event handler: {e}")
            return None

    async def handle_build_triggered(self, event):
        """Handle build trigger event."""
        try:
            logger.info("[DevOpsInfra] Build gestart...")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for build triggered
            self.monitor.log_metric("build_triggered", {
                "build_type": event.get("build_type", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update infrastructure history
            build_entry = {
                "action": "build_triggered",
                "timestamp": datetime.now().isoformat(),
                "build_type": event.get("build_type", "unknown"),
                "status": "processing"
            }
            self.infrastructure_history.append(build_entry)
            self._save_infrastructure_history()
            
            # Simuleer build (in productie: start build pipeline)
            await asyncio.sleep(2)
            
            # Publish follow-up events
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("tests_requested", {"desc": "Tests uitvoeren"})
                    await self.message_bus_integration.publish_event("build_completed", {
                        "build_type": event.get("build_type", "unknown"),
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    })
                except Exception as e:
                    logger.warning(f"Failed to publish build events: {e}")
            
            logger.info("[DevOpsInfra] Build afgerond, tests_requested gepubliceerd.")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error in build triggered event handler: {e}")
            return None

    async def handle_deployment_executed(self, event):
        """Handle deployment execution event."""
        try:
            logger.info("[DevOpsInfra] Deployment gestart...")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for deployment executed
            self.monitor.log_metric("deployment_executed", {
                "deployment_type": event.get("deployment_type", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update infrastructure history
            deployment_entry = {
                "action": "deployment_executed",
                "timestamp": datetime.now().isoformat(),
                "deployment_type": event.get("deployment_type", "unknown"),
                "status": "processing"
            }
            self.infrastructure_history.append(deployment_entry)
            self._save_infrastructure_history()
            
            # Simuleer deployment (in productie: start deployment pipeline)
            await asyncio.sleep(2)
            
            # Publish follow-up events
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("deployment_completed", {"desc": "Deployment afgerond"})
                except Exception as e:
                    logger.warning(f"Failed to publish deployment_completed event: {e}")
            
            logger.info("[DevOpsInfra] Deployment afgerond, deployment_completed gepubliceerd.")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error in deployment executed event handler: {e}")
            return None

    async def handle_infrastructure_deployment_requested(self, event):
        """Handle infrastructure deployment requested event."""
        try:
            logger.info(f"Infrastructure deployment requested: {event}")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for infrastructure deployment requested
            self.monitor.log_metric("infrastructure_deployment_requested", {
                "infrastructure_type": event.get("infrastructure_type", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update infrastructure history
            infra_entry = {
                "action": "infrastructure_deployment_requested",
                "timestamp": datetime.now().isoformat(),
                "infrastructure_type": event.get("infrastructure_type", "kubernetes"),
                "status": "processing"
            }
            self.infrastructure_history.append(infra_entry)
            self._save_infrastructure_history()
            
            # Perform infrastructure deployment based on event data
            infrastructure_type = event.get("infrastructure_type", "kubernetes")
            deployment_config = event.get("deployment_config", {})
            
            # Simulate infrastructure deployment
            deployment_result = await self.deploy_infrastructure(infrastructure_type)
            
            # Publish follow-up event
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("infrastructure_deployment_completed", {
                        "request_id": event.get("request_id"),
                        "infrastructure_type": infrastructure_type,
                        "result": deployment_result
                    })
                except Exception as e:
                    logger.warning(f"Failed to publish infrastructure_deployment_completed event: {e}")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error handling infrastructure deployment request: {e}")
            return None

    async def handle_monitoring_requested(self, event):
        """Handle infrastructure monitoring requested event."""
        try:
            logger.info(f"Infrastructure monitoring requested: {event}")
            
            # Validate event data
            if not isinstance(event, dict):
                logger.error("Invalid event data: event must be a dictionary")
                return None
            
            # Log metric for monitoring requested
            self.monitor.log_metric("monitoring_requested", {
                "infrastructure_id": event.get("infrastructure_id", "unknown"),
                "monitoring_type": event.get("monitoring_type", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update infrastructure history
            monitoring_entry = {
                "action": "monitoring_requested",
                "timestamp": datetime.now().isoformat(),
                "infrastructure_id": event.get("infrastructure_id", "infra_001"),
                "monitoring_type": event.get("monitoring_type", "performance"),
                "status": "processing"
            }
            self.infrastructure_history.append(monitoring_entry)
            self._save_infrastructure_history()
            
            # Perform infrastructure monitoring based on event data
            infrastructure_id = event.get("infrastructure_id", "infra_001")
            monitoring_type = event.get("monitoring_type", "performance")
            
            # Simulate monitoring
            monitoring_result = self.monitor_infrastructure(infrastructure_id)
            
            # Publish follow-up event
            if self.message_bus_integration:
                try:
                    await self.message_bus_integration.publish_event("infrastructure_monitoring_completed", {
                        "request_id": event.get("request_id"),
                        "infrastructure_id": infrastructure_id,
                        "result": monitoring_result
                    })
                except Exception as e:
                    logger.warning(f"Failed to publish infrastructure_monitoring_completed event: {e}")
            
            # Return None for consistency with other event handlers
            return None
            
        except Exception as e:
            logger.error(f"Error handling monitoring request: {e}")
            return None

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        await self.initialize_enhanced_mcp()
        await self.initialize_tracing()
        
        # Initialize Message Bus Integration
        await self.initialize_message_bus_integration()
        
        # Register event handlers
        subscribe("pipeline_advice_requested", self.on_pipeline_advice_requested)
        subscribe("incident_response_requested", self.on_incident_response_requested)
        subscribe("feedback_sentiment_analyzed", self.on_feedback_sentiment_analyzed)
        subscribe("build_triggered", self.handle_build_triggered)
        subscribe("deployment_executed", self.handle_deployment_executed)

        logger.info("DevOpsInfraAgent ready and listening for events...")
        print("🛠️ DevOpsInfra is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled" if self.message_bus_enabled else "Message Bus: Disabled")
        await self.collaborate_example()
        
        try:
            # Keep the agent running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("DevOpsInfra agent stopped.")
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the DevOpsInfra agent met MCP integration."""
        agent = cls()
        await agent.initialize_mcp()
        print("DevOpsInfra agent started with MCP integration")

    def get_enhanced_mcp_tools(self) -> List[str]:
        """Beschikbare Enhanced MCP tools voor DevOpsInfra."""
        if not getattr(self, 'enhanced_mcp_enabled', False):
            return []
        return [
            "devops.pipeline_advice",
            "devops.incident_response",
            "devops.deploy_infrastructure",
            "devops.monitor_infrastructure",
            "devops.security_validation",
            "devops.performance_optimization",
        ]

    def register_enhanced_mcp_tools(self) -> bool:
        """Registreer Enhanced MCP tools indien beschikbaar."""
        if not getattr(self, 'enhanced_mcp_enabled', False) or not getattr(self, 'enhanced_mcp', None):
            return False
        try:
            for tool in self.get_enhanced_mcp_tools():
                if hasattr(self.enhanced_mcp, 'register_tool'):
                    self.enhanced_mcp.register_tool(tool)
            return True
        except Exception as e:
            logger.warning(f"Failed to register enhanced MCP tools: {e}")
            return False

    async def trace_operation(self, operation_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generieke tracing haak voor DevOps operaties."""
        try:
            if getattr(self, 'tracing_enabled', False) and getattr(self, 'tracer', None):
                span_name = f"devops.{operation_name}"
                if hasattr(self.tracer, 'start_span'):
                    span = self.tracer.start_span(span_name)
                    try:
                        if hasattr(span, 'set_attribute'):
                            span.set_attribute("agent", self.agent_name)
                            for k, v in (data or {}).items():
                                try:
                                    span.set_attribute(f"data.{k}", v)
                                except Exception:
                                    pass
                    finally:
                        if hasattr(span, 'end'):
                            span.end()
            return {"operation": operation_name, "agent": self.agent_name, **(data or {})}
        except Exception as e:
            logger.warning(f"trace_operation failed: {e}")
            return {"operation": operation_name, "agent": self.agent_name, "trace": "failed"}

    async def publish_agent_event(self, event_type: str, data: Dict[str, Any], correlation_id: Optional[str] = None) -> bool:
        """Gestandaardiseerde wrapper naar core publish_event met uniform payload."""
        try:
            from bmad.core.message_bus import publish_event
            payload = {**data}
            if "agent" not in payload:
                payload["agent"] = self.agent_name
            if "status" not in payload:
                payload["status"] = "completed"
            return await publish_event(event_type, payload, source_agent=self.agent_name, correlation_id=correlation_id)
        except Exception as e:
            logger.warning(f"Failed to publish event {event_type}: {e}")
            return False

    async def subscribe_to_event(self, event_type: str, callback) -> bool:
        """Subscribe via integratie met core/legacy fallback."""
        try:
            integration = getattr(self, 'message_bus_integration', None)
            if integration and hasattr(integration, 'register_event_handler'):
                return await integration.register_event_handler(event_type, callback)
            try:
                from bmad.core.message_bus.message_bus import subscribe_to_event as core_subscribe_to_event
                return await core_subscribe_to_event(event_type, callback)
            except Exception:
                try:
                    from bmad.agents.core.communication.message_bus import subscribe as legacy_subscribe
                    legacy_subscribe(event_type, callback)
                    return True
                except Exception:
                    return False
        except Exception as e:
            logger.warning(f"subscribe_to_event failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="DevOps Infrastructure Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "pipeline-advice", "incident-response", "deploy-infrastructure",
                               "monitor-infrastructure", "show-infrastructure-history", "show-incident-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run",
                               "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary",
                               "initialize-message-bus", "message-bus-status", "publish-event", "subscribe-event",
                               "list-events", "event-history", "performance-metrics"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--pipeline-config", default="Sample CI/CD pipeline", help="Pipeline configuration for analysis")
    parser.add_argument("--incident-desc", default="Sample incident description", help="Incident description for response")
    parser.add_argument("--infrastructure-type", default="kubernetes", help="Infrastructure type for deployment")
    parser.add_argument("--infrastructure-id", default="infra_001", help="Infrastructure ID for monitoring")

    args = parser.parse_args()

    agent = DevOpsInfraAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "pipeline-advice":
        result = agent.pipeline_advice(args.pipeline_config)
        print(json.dumps(result, indent=2))
    elif args.command == "incident-response":
        result = agent.incident_response(args.incident_desc)
        print(json.dumps(result, indent=2))
    elif args.command == "deploy-infrastructure":
        result = asyncio.run(agent.deploy_infrastructure(args.infrastructure_type))
        print(json.dumps(result, indent=2))
    elif args.command == "monitor-infrastructure":
        result = agent.monitor_infrastructure(args.infrastructure_id)
        print(json.dumps(result, indent=2))
    elif args.command == "show-infrastructure-history":
        agent.show_infrastructure_history()
    elif args.command == "show-incident-history":
        agent.show_incident_history()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-report":
        agent.export_report(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    # Enhanced MCP Phase 2 Commands
    elif args.command == "enhanced-collaborate":
        result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
            ["ReleaseManager", "QualityGuardian", "TestEngineer", "DataEngineer"], 
            {"type": "infrastructure_coordination", "content": {"coordination_type": "devops_management"}}
        ))
        print(json.dumps(result, indent=2))
    elif args.command == "enhanced-security":
        result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
            "infrastructure_data": {"pipelines": [], "deployments": [], "incidents": []},
            "security_requirements": ["infrastructure_security", "deployment_security", "access_control"]
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "enhanced-performance":
        result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
            "infrastructure_data": {"pipelines": [], "deployments": [], "incidents": []},
            "performance_metrics": {"deployment_speed": 85.5, "uptime": 99.9}
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "trace-operation":
        result = asyncio.run(agent.trace_infrastructure_deployment({
            "operation_type": "infrastructure_deployment",
            "infrastructure_type": args.infrastructure_type,
            "deployments": list(agent.infrastructure_history)
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "trace-performance":
        result = asyncio.run(agent.trace_pipeline_optimization({
            "operation_type": "performance_analysis",
            "performance_metrics": {"deployment_speed": 85.5, "uptime": 99.9}
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "trace-error":
        result = asyncio.run(agent.trace_devops_error({
            "operation_type": "error_analysis",
            "error_data": {"error_type": "deployment_failure", "error_message": "Infrastructure deployment failed"}
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "tracing-summary":
        print("Tracing Summary for DevOpsInfra:")
        print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
        print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
        print(f"Agent: {agent.agent_name}")
    elif args.command == "initialize-message-bus":
        asyncio.run(agent.initialize_message_bus_integration())
        print("✅ Message Bus Integration initialized successfully")
    elif args.command == "message-bus-status":
        print("🚀 DevOpsInfra Agent Message Bus Status:")
        print(f"✅ Message Bus Integration: {'Enabled' if agent.message_bus_enabled else 'Disabled'}")
        print(f"✅ Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
        print(f"✅ Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
        print(f"📊 Performance Metrics: {len(agent.performance_metrics)} metrics tracked")
        print(f"📝 Infrastructure History: {len(agent.infrastructure_history)} entries")
        print(f"⚡ Incident History: {len(agent.incident_history)} entries")
    elif args.command == "publish-event":
        if len(sys.argv) < 4:
            print("❌ Usage: publish-event <event_type> <event_data_json>")
            return
        event_type = sys.argv[2]
        try:
            event_data = json.loads(sys.argv[3])
            asyncio.run(agent.message_bus_integration.publish_event(event_type, event_data))
            print(f"✅ Event '{event_type}' published successfully")
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for event_data")
    elif args.command == "subscribe-event":
        if len(sys.argv) < 3:
            print("❌ Usage: subscribe-event <event_type>")
            return
        event_type = sys.argv[2]
        print(f"📡 Subscribing to event: {event_type}")
        # Event handlers are already registered in initialize_message_bus_integration
    elif args.command == "list-events":
        print("🚀 DevOpsInfra Agent Supported Events:")
        print("📥 Input Events:")
        print("  - pipeline_advice_requested")
        print("  - incident_response_requested")
        print("  - infrastructure_deployment_requested")
        print("  - monitoring_requested")
        print("  - build_triggered")
        print("  - deployment_executed")
        print("  - feedback_sentiment_analyzed")
        print("📤 Output Events:")
        print("  - pipeline_advice_provided")
        print("  - incident_response_completed")
        print("  - infrastructure_deployed")
        print("  - monitoring_configured")
        print("  - build_completed")
        print("  - deployment_completed")
    elif args.command == "event-history":
        print("📝 Infrastructure History:")
        for entry in agent.infrastructure_history[-10:]:  # Show last 10 entries
            print(f"  - {entry}")
        print("\n⚡ Incident History:")
        for entry in agent.incident_history[-10:]:  # Show last 10 entries
            print(f"  - {entry}")
    elif args.command == "performance-metrics":
        print("📊 DevOpsInfra Agent Performance Metrics:")
        for metric, value in agent.performance_metrics.items():
            if isinstance(value, float):
                print(f"  • {metric}: {value:.2f}")
            else:
                print(f"  • {metric}: {value}")
    elif args.command == "run":
        asyncio.run(agent.run())

if __name__ == "__main__":
    main()
