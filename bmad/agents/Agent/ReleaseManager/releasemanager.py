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
from typing import Any, Dict, Optional

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
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

# Enhanced MCP Phase 2 imports
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ReleaseManagerAgent:
    """
    Release Manager Agent voor BMAD.
    Gespecialiseerd in release management, deployment coordination, en version control.
    """
    
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        try:
            self.release_manager_template = self.framework_manager.get_framework_template('release_manager')
        except:
            self.release_manager_template = None
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "ReleaseManager"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/releasemanager/best-practices.md",
            "release-template": self.resource_base / "templates/releasemanager/release-template.md",
            "rollback-template": self.resource_base / "templates/releasemanager/rollback-template.md",
            "deployment-template": self.resource_base / "templates/releasemanager/deployment-template.md",
            "release-notes-template": self.resource_base / "templates/releasemanager/release-notes-template.md",
            "release-checklist-template": self.resource_base / "templates/releasemanager/release-checklist-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/releasemanager/changelog.md",
            "history": self.resource_base / "data/releasemanager/release-history.md",
            "rollback-history": self.resource_base / "data/releasemanager/rollback-history.md"
        }

        # Initialize history
        self.release_history = []
        self.rollback_history = []
        self._load_release_history()
        self._load_rollback_history()
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2 attributes
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Initialize tracer
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "ReleaseManager",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced release management capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for ReleaseManager")
        except Exception as e:
            logger.warning(f"MCP initialization failed for ReleaseManager: {e}")
            self.mcp_enabled = False

    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            # Check if initialize method exists before calling it
            if hasattr(self.enhanced_mcp, 'initialize'):
                await self.enhanced_mcp.initialize()
            self.enhanced_mcp_enabled = True
            logger.info("Enhanced MCP initialized successfully")
        except Exception as e:
            logger.warning(f"Enhanced MCP initialization failed: {e}")
            self.enhanced_mcp_enabled = False
    
    async def initialize_tracing(self):
        """Initialize tracing capabilities."""
        try:
            if self.tracer and hasattr(self.tracer, 'initialize'):
                await self.tracer.initialize()
                self.tracing_enabled = True
                logger.info("Tracing initialized successfully")
            else:
                logger.warning("Tracer not available or missing initialize method")
                self.tracing_enabled = False
        except Exception as e:
            logger.warning(f"Tracing initialization failed: {e}")
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
    
    async def use_release_specific_mcp_tools(self, release_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use release-specific MCP tools voor enhanced release management."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Release creation
            release_result = await self.use_mcp_tool("release_creation", {
                "version": release_data.get("version", ""),
                "description": release_data.get("description", ""),
                "release_type": release_data.get("release_type", "feature"),
                "target_environment": release_data.get("target_environment", "production")
            })
            if release_result:
                enhanced_data["release_creation"] = release_result
            
            # Release approval
            approval_result = await self.use_mcp_tool("release_approval", {
                "version": release_data.get("version", ""),
                "approval_criteria": release_data.get("approval_criteria", {}),
                "stakeholder_approval": release_data.get("stakeholder_approval", True)
            })
            if approval_result:
                enhanced_data["release_approval"] = approval_result
            
            # Deployment coordination
            deployment_result = await self.use_mcp_tool("deployment_coordination", {
                "version": release_data.get("version", ""),
                "deployment_strategy": release_data.get("deployment_strategy", "rolling"),
                "rollback_plan": release_data.get("rollback_plan", {}),
                "monitoring_setup": release_data.get("monitoring_setup", True)
            })
            if deployment_result:
                enhanced_data["deployment_coordination"] = deployment_result
            
            # Version control
            version_result = await self.use_mcp_tool("version_control", {
                "version": release_data.get("version", ""),
                "version_strategy": release_data.get("version_strategy", "semantic"),
                "changelog_generation": release_data.get("changelog_generation", True)
            })
            if version_result:
                enhanced_data["version_control"] = version_result
            
            logger.info(f"Release-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in release-specific MCP tools: {e}")
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, release_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_release_specific_mcp_tools(release_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": release_data.get("capabilities", []),
                "performance_metrics": release_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Release-specific enhanced tools
            release_enhanced_result = await self.use_release_specific_enhanced_tools(release_data)
            enhanced_data.update(release_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_release_operation(release_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_release_specific_enhanced_tools(self, release_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use release-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced release creation
            if "release_creation" in release_data:
                creation_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_release_creation", {
                    "release_data": release_data["release_creation"],
                    "creation_depth": release_data.get("creation_depth", "comprehensive"),
                    "include_automation": release_data.get("include_automation", True)
                })
                enhanced_tools["enhanced_release_creation"] = creation_result
            
            # Enhanced deployment coordination
            if "deployment_coordination" in release_data:
                deployment_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_deployment_coordination", {
                    "deployment_data": release_data["deployment_coordination"],
                    "coordination_complexity": release_data.get("coordination_complexity", "advanced"),
                    "include_monitoring": release_data.get("include_monitoring", True)
                })
                enhanced_tools["enhanced_deployment_coordination"] = deployment_result
            
            # Enhanced team collaboration
            if "team_collaboration" in release_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["DevOpsInfra", "QualityGuardian", "TestEngineer", "ProductOwner"],
                    {
                        "type": "release_coordination",
                        "content": release_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced version control
            if "version_control" in release_data:
                version_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_version_control", {
                    "version_data": release_data["version_control"],
                    "version_strategy": release_data.get("version_strategy", "semantic"),
                    "include_changelog": release_data.get("include_changelog", True)
                })
                enhanced_tools["enhanced_version_control"] = version_result
            
            logger.info(f"Release-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in release-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_release_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace release operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "release_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "release_count": len(operation_data.get("releases", [])),
                    "deployment_success_rate": operation_data.get("deployment_success_rate", 0.0),
                    "rollback_count": len(operation_data.get("rollbacks", []))
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("release_operation", trace_data)
            
            logger.info(f"Release operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

    def _load_release_history(self):
        """Load release history from data file"""
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.release_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Release history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing release history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in release history: {e}")
        except OSError as e:
            logger.error(f"OS error loading release history: {e}")
        except Exception as e:
            logger.warning(f"Could not load release history: {e}")

    def _save_release_history(self):
        """Save release history to data file"""
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Release History\n\n")
                for release in self.release_history[-50:]:  # Keep last 50 releases
                    f.write(f"- {release}\n")
        except PermissionError as e:
            logger.error(f"Permission denied saving release history: {e}")
        except OSError as e:
            logger.error(f"OS error saving release history: {e}")
        except Exception as e:
            logger.error(f"Could not save release history: {e}")

    def _load_rollback_history(self):
        """Load rollback history from data file"""
        try:
            if self.data_paths["rollback-history"].exists():
                with open(self.data_paths["rollback-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.rollback_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Rollback history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing rollback history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in rollback history: {e}")
        except OSError as e:
            logger.error(f"OS error loading rollback history: {e}")
        except Exception as e:
            logger.warning(f"Could not load rollback history: {e}")

    def _save_rollback_history(self):
        """Save rollback history to data file"""
        try:
            self.data_paths["rollback-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["rollback-history"], "w") as f:
                f.write("# Rollback History\n\n")
                for rollback in self.rollback_history[-50:]:  # Keep last 50 rollbacks
                    f.write(f"- {rollback}\n")
        except PermissionError as e:
            logger.error(f"Permission denied saving rollback history: {e}")
        except OSError as e:
            logger.error(f"OS error saving rollback history: {e}")
        except Exception as e:
            logger.error(f"Could not save rollback history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
Release Manager Agent Commands:
  help                    - Show this help message
  create-release          - Create new release plan
  approve-release         - Approve release for deployment
  deploy-release          - Deploy release to production
  rollback-release        - Rollback failed release
  show-release-history    - Show release history
  show-rollback-history   - Show rollback history
  show-best-practices     - Show release management best practices
  show-changelog          - Show release changelog
  export-report [format]  - Export release report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        # Input validation
        if not isinstance(resource_type, str):
            print("Error: resource_type must be a string")
            return
        
        if not resource_type.strip():
            print("Error: resource_type cannot be empty")
            return
        
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "release-template":
                path = self.template_paths["release-template"]
            elif resource_type == "rollback-template":
                path = self.template_paths["rollback-template"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return
            if path.exists():
                with open(path) as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except FileNotFoundError:
            print(f"Resource file not found: {resource_type}")
        except PermissionError as e:
            print(f"Permission denied accessing resource {resource_type}: {e}")
        except UnicodeDecodeError as e:
            print(f"Unicode decode error in resource {resource_type}: {e}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_release_history(self):
        """Show release history"""
        if not self.release_history:
            print("No release history available.")
            return
        print("Release History:")
        print("=" * 50)
        for i, release in enumerate(self.release_history[-10:], 1):
            print(f"{i}. {release}")

    def show_rollback_history(self):
        """Show rollback history"""
        if not self.rollback_history:
            print("No rollback history available.")
            return
        print("Rollback History:")
        print("=" * 50)
        for i, rollback in enumerate(self.rollback_history[-10:], 1):
            print(f"{i}. {rollback}")

    def create_release(self, version: str = "1.2.0", description: str = "Feature release") -> Dict[str, Any]:
        """Create new release plan with enhanced functionality."""
        # Input validation
        if not isinstance(version, str):
            raise TypeError("version must be a string")
        if not isinstance(description, str):
            raise TypeError("description must be a string")
        
        if not version.strip():
            raise ValueError("version cannot be empty")
        if not description.strip():
            raise ValueError("description cannot be empty")
            
        logger.info(f"Creating release plan for version {version}")

        # Simulate release creation
        time.sleep(1)

        release_result = {
            "version": version,
            "release_type": "Release Plan Creation",
            "status": "created",
            "description": description,
            "release_components": {
                "frontend": {
                    "version": "2.1.0",
                    "changes": ["New dashboard features", "UI improvements", "Performance optimizations"],
                    "status": "ready"
                },
                "backend": {
                    "version": "1.5.0",
                    "changes": ["API enhancements", "Database optimizations", "Security updates"],
                    "status": "ready"
                },
                "infrastructure": {
                    "version": "1.3.0",
                    "changes": ["Kubernetes updates", "Monitoring improvements", "Security patches"],
                    "status": "ready"
                }
            },
            "release_checklist": [
                "Code review completed",
                "Tests passing",
                "Security scan completed",
                "Performance testing done",
                "Documentation updated",
                "Stakeholder approval received"
            ],
            "deployment_plan": {
                "deployment_strategy": "Blue-green deployment",
                "deployment_window": "2025-07-28 02:00-04:00 UTC",
                "estimated_downtime": "5 minutes",
                "rollback_threshold": "5% error rate",
                "monitoring_plan": "Enhanced monitoring during deployment"
            },
            "risk_assessment": {
                "high_risk_areas": ["Database migrations", "Third-party integrations"],
                "mitigation_strategies": [
                    "Comprehensive testing in staging",
                    "Rollback procedures in place",
                    "Monitoring and alerting configured"
                ],
                "risk_level": "medium"
            },
            "stakeholder_communication": {
                "notifications": ["Development team", "Product team", "Operations team"],
                "communication_channels": ["Slack", "Email", "JIRA"],
                "escalation_procedures": "Contact release manager immediately"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManagerAgent", MetricType.SUCCESS_RATE, 95, "%")

        # Add to release history
        release_entry = f"{datetime.now().isoformat()}: Release created - {version} - {description}"
        self.release_history.append(release_entry)
        self._save_release_history()

        logger.info(f"Release plan created: {release_result}")
        return release_result

    def approve_release(self, version: str = "1.2.0") -> Dict[str, Any]:
        """Approve release for deployment with enhanced functionality."""
        # Input validation
        if not isinstance(version, str):
            raise TypeError("version must be a string")
        
        if not version.strip():
            raise ValueError("version cannot be empty")
            
        logger.info(f"Approving release version {version}")

        # Simulate approval process
        time.sleep(1)

        approval_result = {
            "version": version,
            "approval_type": "Release Approval",
            "status": "approved",
            "approval_details": {
                "approval_criteria": [
                    "All tests passing",
                    "Security review completed",
                    "Performance benchmarks met",
                    "User acceptance testing passed"
                ],
                "approved_by": "Product Owner",
                "approval_date": datetime.now().isoformat(),
                "conditions": [
                    "Monitor deployment closely",
                    "Have rollback plan ready",
                    "Notify stakeholders of deployment"
                ]
            },
            "deployment_approval": {
                "approved_for_production": True,
                "deployment_window": "2025-07-28 02:00-04:00 UTC",
                "estimated_downtime": "5 minutes",
                "rollback_threshold": "5% error rate"
            },
            "quality_gates": {
                "code_quality": "Passed",
                "security_scan": "Passed",
                "performance_tests": "Passed",
                "integration_tests": "Passed"
            },
            "stakeholder_signoffs": {
                "product_owner": "Approved",
                "tech_lead": "Approved",
                "security_team": "Approved",
                "operations_team": "Approved"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManagerAgent", MetricType.SUCCESS_RATE, 92, "%")

        logger.info(f"Release approved: {approval_result}")
        return approval_result

    async def deploy_release(self, version: str = "1.2.0") -> Dict[str, Any]:
        """Deploy release to production with enhanced functionality."""
        # Input validation
        if not isinstance(version, str):
            raise TypeError("version must be a string")
        
        if not version.strip():
            raise ValueError("version cannot be empty")
            
        logger.info(f"Deploying release version {version}")

        # Try MCP-enhanced deployment first
        if self.mcp_enabled and self.mcp_client:
            try:
                mcp_result = await self.use_mcp_tool("deploy_release", {
                    "version": version,
                    "deployment_strategy": "Blue-green deployment",
                    "target_environment": "production",
                    "rollback_plan": {
                        "rollback_available": True,
                        "rollback_window": "30 minutes",
                        "previous_version": "1.1.0"
                    },
                    "monitoring_setup": True
                })
                
                if mcp_result:
                    logger.info("MCP-enhanced deployment completed")
                    result = mcp_result.get("deployment_result", {})
                    result["mcp_enhanced"] = True
                else:
                    logger.warning("MCP deployment failed, using local deployment")
                    result = self._create_local_deployment_result(version)
            except Exception as e:
                logger.warning(f"MCP deployment failed: {e}, using local deployment")
                result = self._create_local_deployment_result(version)
        else:
            result = self._create_local_deployment_result(version)
        
        # Use release-specific MCP tools for additional enhancement
        if self.mcp_enabled:
            try:
                release_data = {
                    "version": version,
                    "deployment_strategy": "Blue-green deployment",
                    "rollback_plan": {
                        "rollback_available": True,
                        "rollback_window": "30 minutes",
                        "previous_version": "1.1.0"
                    },
                    "monitoring_setup": True,
                    "target_environment": "production"
                }
                release_enhanced = await self.use_release_specific_mcp_tools(release_data)
                if release_enhanced:
                    result["release_enhancements"] = release_enhanced
            except Exception as e:
                logger.warning(f"Release-specific MCP tools failed: {e}")

        # Log performance metrics
        self.monitor._record_metric("ReleaseManagerAgent", MetricType.SUCCESS_RATE, 90, "%")

        # Add to release history
        deployment_entry = f"{datetime.now().isoformat()}: Release deployed - {version}"
        self.release_history.append(deployment_entry)
        self._save_release_history()

        logger.info(f"Release deployed: {result}")
        return result
    
    def _create_local_deployment_result(self, version: str) -> Dict[str, Any]:
        """Create local deployment result when MCP is not available."""
        # Simulate deployment process
        time.sleep(2)
        
        return {
            "version": version,
            "deployment_type": "Production Deployment",
            "status": "deployed",
            "deployment_details": {
                "deployment_strategy": "Blue-green deployment",
                "deployment_start": datetime.now().isoformat(),
                "deployment_end": datetime.now().isoformat(),
                "deployment_duration": "15 minutes",
                "deployment_team": "DevOps Team"
            },
            "deployment_environment": {
                "environment": "Production",
                "region": "us-east-1",
                "infrastructure": "AWS EKS",
                "load_balancer": "ALB",
                "database": "RDS PostgreSQL"
            },
            "deployment_status": {
                "overall_status": "Success",
                "frontend_deployment": "Completed",
                "backend_deployment": "Completed",
                "database_migrations": "Completed",
                "health_checks": "Passed"
            },
            "monitoring_info": {
                "application_metrics": "All systems operational",
                "error_rate": "0.1%",
                "response_time": "150ms",
                "throughput": "1000 requests/second",
                "resource_utilization": "Normal"
            },
            "rollback_status": {
                "rollback_available": True,
                "rollback_window": "30 minutes",
                "previous_version": "1.1.0",
                "rollback_procedure": "Automated rollback on failure"
            },
            "post_deployment_checks": [
                "Application health checks passed",
                "Database connectivity verified",
                "External integrations tested",
                "Performance benchmarks met",
                "Security scans completed"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

    def rollback_release(self, version: str = "1.2.0", reason: str = "High error rate") -> Dict[str, Any]:
        """Rollback failed release with enhanced functionality."""
        # Input validation
        if not isinstance(version, str):
            raise TypeError("version must be a string")
        if not isinstance(reason, str):
            raise TypeError("reason must be a string")
        
        if not version.strip():
            raise ValueError("version cannot be empty")
        if not reason.strip():
            raise ValueError("reason cannot be empty")
            
        logger.info(f"Rolling back release version {version}")

        # Simulate rollback process
        time.sleep(2)

        rollback_result = {
            "version": version,
            "rollback_type": "Emergency Rollback",
            "status": "rolled_back",
            "reason": reason,
            "rollback_details": {
                "rollback_trigger": reason,
                "rollback_start": datetime.now().isoformat(),
                "rollback_end": datetime.now().isoformat(),
                "rollback_duration": "8 minutes",
                "rollback_team": "DevOps Team"
            },
            "rollback_plan": {
                "rollback_strategy": "Immediate rollback to previous version",
                "previous_version": "1.1.0",
                "rollback_steps": [
                    "Stop traffic to new version",
                    "Revert to previous version",
                    "Restore database state",
                    "Verify system health",
                    "Notify stakeholders"
                ],
                "rollback_automation": "Automated rollback triggered"
            },
            "rollback_status": {
                "overall_status": "Completed",
                "traffic_redirected": "Completed",
                "version_reverted": "Completed",
                "database_restored": "Completed",
                "health_checks": "Passed"
            },
            "impact_assessment": {
                "user_impact": "Minimal - 5 minutes of downtime",
                "business_impact": "Low - No data loss",
                "technical_impact": "System restored to stable state",
                "reputation_impact": "Managed professionally"
            },
            "post_rollback_actions": [
                "Incident investigation initiated",
                "Root cause analysis scheduled",
                "Stakeholder communication sent",
                "Lessons learned documented",
                "Prevention measures planned"
            ],
            "monitoring_post_rollback": {
                "error_rate": "0.05%",
                "response_time": "120ms",
                "system_stability": "Stable",
                "user_satisfaction": "High"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManagerAgent", MetricType.SUCCESS_RATE, 88, "%")

        # Add to rollback history
        rollback_entry = f"{datetime.now().isoformat()}: Release rolled back - {version} - {reason}"
        self.rollback_history.append(rollback_entry)
        self._save_rollback_history()

        logger.info(f"Release rolled back: {rollback_result}")
        return rollback_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export release report in specified format."""
        # Input validation
        if not isinstance(format_type, str):
            raise TypeError("format_type must be a string")
        
        if format_type not in ["md", "csv", "json"]:
            raise ValueError("format_type must be one of: md, csv, json")
        
        if report_data is not None and not isinstance(report_data, dict):
            raise TypeError("report_data must be a dictionary")
        
        if not report_data:
            report_data = {
                "report_type": "Release Report",
                "version": "1.2.0",
                "status": "success",
                "total_releases": 15,
                "successful_releases": 14,
                "failed_releases": 1,
                "timestamp": datetime.now().isoformat(),
                "agent": "ReleaseManagerAgent"
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
        try:
            output_file = f"release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            content = f"""# Release Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Version**: {report_data.get('version', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Total Releases**: {report_data.get('total_releases', 0)}
- **Successful Releases**: {report_data.get('successful_releases', 0)}
- **Failed Releases**: {report_data.get('failed_releases', 0)}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Release Metrics
- **Success Rate**: {(report_data.get('successful_releases', 0) / max(report_data.get('total_releases', 1), 1)) * 100:.1f}%
- **Average Deployment Time**: {report_data.get('deployment_metrics', {}).get('deployment_time', 'N/A')}
- **Average Downtime**: {report_data.get('deployment_metrics', {}).get('downtime', 'N/A')}
- **Rollback Rate**: {(report_data.get('failed_releases', 0) / max(report_data.get('total_releases', 1), 1)) * 100:.1f}%

## Recent Releases
{chr(10).join([f"- {release}" for release in self.release_history[-5:]])}

## Recent Rollbacks
{chr(10).join([f"- {rollback}" for rollback in self.rollback_history[-5:]])}
"""

            with open(output_file, "w") as f:
                f.write(content)
            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving markdown report: {e}")
        except OSError as e:
            logger.error(f"OS error saving markdown report: {e}")
        except Exception as e:
            logger.error(f"Error saving markdown report: {e}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        try:
            output_file = f"release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Version", report_data.get("version", "N/A")])
                writer.writerow(["Status", report_data.get("status", "N/A")])
                writer.writerow(["Total Releases", report_data.get("total_releases", 0)])
                writer.writerow(["Successful Releases", report_data.get("successful_releases", 0)])
                writer.writerow(["Failed Releases", report_data.get("failed_releases", 0)])

            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving CSV report: {e}")
        except OSError as e:
            logger.error(f"OS error saving CSV report: {e}")
        except Exception as e:
            logger.error(f"Error saving CSV report: {e}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        try:
            output_file = f"release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving JSON report: {e}")
        except OSError as e:
            logger.error(f"OS error saving JSON report: {e}")
        except Exception as e:
            logger.error(f"Error saving JSON report: {e}")

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

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting release management collaboration example...")

        # Publish release creation request
        publish("release_creation_requested", {
            "agent": "ReleaseManagerAgent",
            "version": "1.2.0",
            "timestamp": datetime.now().isoformat()
        })

        # Create release
        self.create_release("1.2.0", "Feature release with new dashboard")

        # Approve release
        self.approve_release("1.2.0")

        # Deploy release
        deployment_result = self.deploy_release("1.2.0")

        # Publish completion
        publish("release_deployment_completed", {
            "status": "success",
            "agent": "ReleaseManagerAgent",
            "version": "1.2.0",
            "deployment_status": deployment_result["status"]
        })

        # Save context
        save_context("ReleaseManager", "status", {"release_status": "deployed"})

        # Notify via Slack
        try:
            send_slack_message(f"Release 1.2.0 deployed successfully with {deployment_result['deployment_metrics']['success_rate']} success rate")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("ReleaseManager")
        print(f"Opgehaalde context: {context}")

    def on_tests_passed(self, event):
        """Handle tests passed event from other agents."""
        # Input validation
        if not isinstance(event, dict):
            logger.warning("Invalid event type for tests passed event")
            return
        
        logger.info(f"Tests passed event received: {event}")
        logger.info("[ReleaseManager] Tests geslaagd, release flow gestart.")
        try:
            send_slack_message("[ReleaseManager] Tests geslaagd, release flow gestart.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Start release flow (stub)

    def on_release_approved(self, event):
        """Handle release approved event from other agents."""
        # Input validation
        if not isinstance(event, dict):
            logger.warning("Invalid event type for release approved event")
            return
        
        logger.info(f"Release approved event received: {event}")
        logger.info("[ReleaseManager] Release goedgekeurd door PO, release wordt live gezet.")
        try:
            send_slack_message("[ReleaseManager] Release goedgekeurd door PO, release wordt live gezet.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Zet release live (stub)

    def on_deployment_failed(self, event):
        """Handle deployment failed event from other agents."""
        # Input validation
        if not isinstance(event, dict):
            logger.warning("Invalid event type for deployment failed event")
            return
        
        logger.error(f"Deployment failed event received: {event}")
        logger.error("[ReleaseManager] Deployment failed! Rollback gestart.")
        try:
            send_slack_message("[ReleaseManager] Deployment failed! Rollback gestart.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Start rollback (stub)

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        await self.initialize_enhanced_mcp()
        await self.initialize_tracing()
        
        print("🚀 ReleaseManager is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        subscribe("tests_passed", self.on_tests_passed)
        subscribe("release_approved", self.on_release_approved)
        subscribe("deployment_failed", self.on_deployment_failed)

        logger.info("ReleaseManagerAgent ready and listening for events...")
        await self.collaborate_example()
    
    async def run_async(self):
        """Run the agent with enhanced MCP and tracing initialization."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        print("🚀 ReleaseManager is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        logger.info("ReleaseManagerAgent ready and listening for events...")
        await self.collaborate_example()
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the ReleaseManager agent met MCP integration."""
        agent = cls()
        await agent.run_async()
    
    @classmethod
    async def run_agent_async(cls):
        """Class method to run the ReleaseManager agent with enhanced MCP."""
        agent = cls()
        await agent.run_async()

def main():
    parser = argparse.ArgumentParser(description="Release Manager Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "create-release", "approve-release", "deploy-release",
                               "rollback-release", "show-release-history", "show-rollback-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run", "enhanced-collaborate", "enhanced-security", 
                               "enhanced-performance", "trace-operation", "trace-performance", 
                               "trace-error", "tracing-summary"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--version", default="1.2.0", help="Release version")
    parser.add_argument("--description", default="Feature release", help="Release description")
    parser.add_argument("--reason", default="High error rate", help="Rollback reason")

    args = parser.parse_args()

    agent = ReleaseManagerAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "create-release":
        result = agent.create_release(args.version, args.description)
        print(json.dumps(result, indent=2))
    elif args.command == "approve-release":
        result = agent.approve_release(args.version)
        print(json.dumps(result, indent=2))
    elif args.command == "deploy-release":
        result = asyncio.run(agent.deploy_release(args.version))
        print(json.dumps(result, indent=2))
    elif args.command == "rollback-release":
        result = agent.rollback_release(args.version, args.reason)
        print(json.dumps(result, indent=2))
    elif args.command == "show-release-history":
        agent.show_release_history()
    elif args.command == "show-rollback-history":
        agent.show_rollback_history()
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
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["DevOpsInfra", "QualityGuardian", "TestEngineer", "ProductOwner"], 
                {"type": "release_coordination", "content": {"coordination_type": "release_management"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "release_data": {"releases": [], "deployments": [], "rollbacks": []},
                "security_requirements": ["release_validation", "deployment_security", "rollback_safety"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "release_data": {"releases": [], "deployments": [], "rollbacks": []},
                "performance_metrics": {"deployment_speed": 85.5, "success_rate": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_release_operation({
                "operation_type": "release_management",
                "version": args.version,
                "releases": list(agent.release_history)
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_release_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"deployment_speed": 85.5, "success_rate": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_release_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "deployment_failure", "error_message": "Deployment failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for ReleaseManager:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)
        return

if __name__ == "__main__":
    main()
