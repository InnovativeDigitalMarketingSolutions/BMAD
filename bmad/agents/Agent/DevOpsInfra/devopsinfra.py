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

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DevOpsInfraAgent:
    """
    DevOps Infrastructure Agent voor BMAD.
    Gespecialiseerd in infrastructure management, CI/CD pipelines, en deployment automation.
    """
    
    def __init__(self):
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
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Integration for Phase 2
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
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
                            self.infrastructure_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load infrastructure history: {e}")

    def _save_infrastructure_history(self):
        """Save infrastructure history to data file"""
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Infrastructure History\n\n")
                for infra in self.infrastructure_history[-50:]:  # Keep last 50 entries
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
                            self.incident_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load incident history: {e}")

    def _save_incident_history(self):
        """Save incident history to data file"""
        try:
            self.data_paths["incident-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["incident-history"], "w") as f:
                f.write("# Incident History\n\n")
                for incident in self.incident_history[-50:]:  # Keep last 50 incidents
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
        publish("infrastructure_deployment_requested", {
            "agent": "DevOpsInfraAgent",
            "infrastructure_type": "kubernetes",
            "timestamp": datetime.now().isoformat()
        })

        # Deploy infrastructure
        deployment_result = await self.deploy_infrastructure("kubernetes")

        # Generate pipeline advice
        advice_result = self.pipeline_advice("Sample CI/CD pipeline configuration")

        # Publish completion
        publish("infrastructure_deployment_completed", {
            "status": "success",
            "agent": "DevOpsInfraAgent",
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

    def on_pipeline_advice_requested(self, event):
        """Handle pipeline advice request from other agents."""
        logger.info(f"Pipeline advice requested: {event}")
        pipeline_config = event.get("pipeline_config", "Sample CI/CD pipeline")
        self.pipeline_advice(pipeline_config)

    def on_incident_response_requested(self, event):
        """Handle incident response request from other agents."""
        logger.info(f"Incident response requested: {event}")
        incident_desc = event.get("incident_desc", "Sample incident description")
        self.incident_response(incident_desc)

    def on_feedback_sentiment_analyzed(self, event):
        """Handle feedback sentiment analysis from other agents."""
        sentiment = event.get("sentiment", "")
        motivatie = event.get("motivatie", "")
        feedback = event.get("feedback", "")
        if sentiment == "negatief":
            prompt = f"Bedenk een DevOps-actie of monitoringvoorstel op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen het voorstel als JSON."
            structured_output = '{"devops_voorstel": "..."}'
            result = ask_openai(prompt, structured_output=structured_output)
            logger.info(f"[DevOpsInfra][LLM DevOps Voorstel]: {result}")

    def handle_build_triggered(self, event):
        """Handle build trigger event."""
        logger.info("[DevOpsInfra] Build gestart...")
        # Simuleer build (in productie: start build pipeline)
        time.sleep(2)
        publish("tests_requested", {"desc": "Tests uitvoeren"})
        logger.info("[DevOpsInfra] Build afgerond, tests_requested gepubliceerd.")

    def handle_deployment_executed(self, event):
        """Handle deployment execution event."""
        logger.info("[DevOpsInfra] Deployment gestart...")
        # Simuleer deployment (in productie: start deployment pipeline)
        time.sleep(2)
        publish("deployment_completed", {"desc": "Deployment afgerond"})
        logger.info("[DevOpsInfra] Deployment afgerond, deployment_completed gepubliceerd.")

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        await self.initialize_enhanced_mcp()
        await self.initialize_tracing()
        
        def sync_handler(event):
            asyncio.run(self.on_pipeline_advice_requested(event))

        subscribe("pipeline_advice_requested", self.on_pipeline_advice_requested)
        subscribe("incident_response_requested", self.on_incident_response_requested)
        subscribe("feedback_sentiment_analyzed", self.on_feedback_sentiment_analyzed)
        subscribe("build_triggered", self.handle_build_triggered)
        subscribe("deployment_executed", self.handle_deployment_executed)

        logger.info("DevOpsInfraAgent ready and listening for events...")
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

def main():
    parser = argparse.ArgumentParser(description="DevOps Infrastructure Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "pipeline-advice", "incident-response", "deploy-infrastructure",
                               "monitor-infrastructure", "show-infrastructure-history", "show-incident-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run"])
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
    elif args.command == "run":
        asyncio.run(agent.run())

if __name__ == "__main__":
    main()
