import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import csv
import hashlib
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
    AgentPerformanceProfile,
    AlertLevel,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.agent_message_bus_integration import (
    AgentMessageBusIntegration,
    create_agent_message_bus_integration
)
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.slack.slack_notify import send_human_in_loop_alert, send_slack_message

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
from bmad.core.message_bus import EventTypes, get_message_bus

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Environment variables
DEFAULT_SLACK_CHANNEL = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
ALERT_CHANNEL = os.getenv("SLACK_ALERT_CHANNEL", "C097G8YLBMY")
PO_CHANNEL = os.getenv("SLACK_PO_CHANNEL", "C097G9RFBBL")

# Metrics storage (in-memory, kan later naar Prometheus of Supabase)
METRICS = {
    "slack_commands_received": 0,
    "hitl_decisions": 0,
    "workflows_started": 0,
    "workflows_completed": 0,
    "workflow_paused": 0,
}

METRICS_PATH = "metrics.json"

EVENT_LOG_PATH = "event_log.json"

def save_metrics():
    """Save metrics to file with improved error handling."""
    try:
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(METRICS, f, indent=2)
    except PermissionError:
        logger.error("Permission denied saving metrics file")
    except OSError as e:
        logger.error(f"OS error saving metrics: {e}")
    except Exception as e:
        logger.error(f"Could not save metrics: {e}")

def load_metrics():
    """Load metrics from file with improved error handling."""
    global METRICS
    try:
        with open(METRICS_PATH, encoding="utf-8") as f:
            loaded_metrics = json.load(f)
            METRICS.update(loaded_metrics)
    except FileNotFoundError:
        logger.info("Metrics file not found, starting with default metrics")
    except PermissionError:
        logger.warning("Permission denied accessing metrics file")
    except json.JSONDecodeError:
        logger.error("Metrics file contains invalid JSON, starting with default metrics")
    except Exception as e:
        logger.warning(f"Could not load metrics: {e}")

load_metrics()

# Periodiek metrics opslaan (in aparte thread)
def metrics_saver():
    while True:
        time.sleep(60)
        save_metrics()

# Start metrics saver thread alleen in server mode
_metrics_thread = None

# Extra: workflow doorlooptijd logging
WORKFLOW_TIMES = {}  # workflow_name -> {'start': timestamp, 'end': timestamp}

def log_workflow_start(workflow_name):
    """Log workflow start with input validation."""
    if not workflow_name or not isinstance(workflow_name, str):
        logger.warning("Invalid workflow name provided for logging start")
        return
    WORKFLOW_TIMES[workflow_name] = {"start": time.time(), "end": None}

def log_workflow_end(workflow_name):
    """Log workflow end with improved error handling."""
    if not workflow_name or not isinstance(workflow_name, str):
        logger.warning("Invalid workflow name provided for logging end")
        return
    if workflow_name in WORKFLOW_TIMES:
        WORKFLOW_TIMES[workflow_name]["end"] = time.time()
        duration = WORKFLOW_TIMES[workflow_name]["end"] - WORKFLOW_TIMES[workflow_name]["start"]
        METRICS.setdefault("workflow_durations", {})[workflow_name] = duration
        try:
            save_metrics()
            logging.info(f"[Metrics] Workflow '{workflow_name}' duurde {duration:.1f} seconden.")
        except Exception as e:
            logger.error(f"Could not save metrics for workflow '{workflow_name}': {e}")
    else:
        logger.warning(f"Workflow '{workflow_name}' not found in workflow times")

def log_metric(metric_name):
    """Log metric with input validation."""
    if not metric_name or not isinstance(metric_name, str):
        logger.warning("Invalid metric name provided for logging")
        return
    if metric_name in METRICS:
        METRICS[metric_name] += 1
        logging.info(f"[Metrics] {metric_name}: {METRICS[metric_name]}")
    else:
        METRICS[metric_name] = 1
        logging.info(f"[Metrics] {metric_name}: 1 (nieuw)")

class OrchestratorAgent(AgentMessageBusIntegration):
    def __init__(self):
        # Initialize parent class (AgentMessageBusIntegration)
        super().__init__("Orchestrator", self)
        
        # Set agent name
        self.agent_name = "Orchestrator"
        # Ensure message bus attribute exists for tests and runtime
        try:
            self.message_bus = get_message_bus()
        except Exception:
            self.message_bus = None
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        
        # Performance metrics for orchestration operations
        self.performance_metrics = {
            "workflow_execution_speed": 0.0,
            "agent_coordination_efficiency": 0.0,
            "escalation_response_time": 0.0,
            "workflow_completion_rate": 0.0,
            "agent_availability_score": 0.0,
            "orchestration_accuracy": 0.0,
            "event_processing_speed": 0.0,
            "resource_utilization": 0.0,
            "workflow_optimization_effectiveness": 0.0,
            "collaboration_efficiency": 0.0,
            "decision_making_speed": 0.0,
            "system_health_score": 0.0
        }

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/orchestrator/best-practices.md",
            "workflow-template": self.resource_base / "templates/orchestrator/workflow-template.md",
            "orchestration-template": self.resource_base / "templates/orchestrator/orchestration-template.md",
            "monitoring-template": self.resource_base / "templates/orchestrator/monitoring-template.md",
            "escalation-template": self.resource_base / "templates/orchestrator/escalation-template.md",
            "metrics-template": self.resource_base / "templates/orchestrator/metrics-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/orchestrator/changelog.md",
            "workflow-history": self.resource_base / "data/orchestrator/workflow-history.md",
            "orchestration-history": self.resource_base / "data/orchestrator/orchestration-history.md"
        }

        # Initialize history (lazy loading)
        self.workflow_history = []
        self.orchestration_history = []
        self._history_loaded = False

        # Original functionality
        self.status = {}  # workflow_name -> status
        self.event_log = self.load_event_log()

        # Register performance profile
        profile = AgentPerformanceProfile(
            agent_name=self.agent_name,
            thresholds={
                MetricType.RESPONSE_TIME: {AlertLevel.WARNING: 5.0, AlertLevel.CRITICAL: 10.0},
                MetricType.SUCCESS_RATE: {AlertLevel.WARNING: 90.0, AlertLevel.CRITICAL: 85.0},
                MetricType.MEMORY_USAGE: {AlertLevel.WARNING: 512, AlertLevel.CRITICAL: 1024},
                MetricType.CPU_USAGE: {AlertLevel.WARNING: 80, AlertLevel.CRITICAL: 95}
            }
        )
        self.monitor.register_agent_profile(profile)
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2 attributes
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        self.enhanced_mcp_client = None
        
        # Message Bus Integration
        self.message_bus_integration: Optional[AgentMessageBusIntegration] = None
        self.message_bus_enabled = False
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Initialize tracer
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "OrchestratorAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

        # Fields expected by tests
        self.subscribed_events = set()
        self.event_handlers = {}

    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced orchestration capabilities."""
        try:
            self.mcp_client = get_mcp_client()
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for OrchestratorAgent")
        except Exception as e:
            logger.warning(f"MCP initialization failed for OrchestratorAgent: {e}")
            self.mcp_enabled = False

    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
            self.enhanced_mcp_client = self.enhanced_mcp
            
            if self.enhanced_mcp_enabled:
                logger.info("Enhanced MCP capabilities initialized successfully for Orchestrator")
            else:
                logger.warning("Enhanced MCP initialization failed, falling back to standard MCP")
                
        except Exception as e:
            logger.warning(f"Enhanced MCP initialization failed for Orchestrator: {e}")
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

    async def initialize_message_bus(self):
        try:
            self.message_bus = get_message_bus()
            self.subscribed_events = set()
            self.event_handlers = {}

            # Subscribe to specific event types expected by tests
            for et in [
                EventTypes.WORKFLOW_EXECUTION_REQUESTED,
                EventTypes.WORKFLOW_OPTIMIZATION_REQUESTED,
                EventTypes.WORKFLOW_MONITORING_REQUESTED,
                EventTypes.AGENT_COLLABORATION_REQUESTED,
                EventTypes.TASK_DELEGATED,
            ]:
                self.subscribed_events.add(et)

            # Register handlers
            self.event_handlers[EventTypes.WORKFLOW_EXECUTION_REQUESTED] = self._handle_workflow_execution_requested
            self.event_handlers[EventTypes.WORKFLOW_OPTIMIZATION_REQUESTED] = self._handle_workflow_optimization_requested
            self.event_handlers[EventTypes.WORKFLOW_MONITORING_REQUESTED] = self._handle_workflow_monitoring_requested
            self.event_handlers[EventTypes.AGENT_COLLABORATION_REQUESTED] = self._handle_agent_collaboration_requested
            self.event_handlers[EventTypes.TASK_DELEGATED] = self._handle_task_delegated

            logger.info("Message bus integration initialized successfully for Orchestrator")
        except Exception as e:
            logger.warning(f"Message bus initialization failed for Orchestrator: {e}")

    def _ensure_history_loaded(self):
        """Ensure history is loaded (lazy loading)."""
        if not self._history_loaded:
            self._load_workflow_history()
            self._load_orchestration_history()
            self._history_loaded = True

    def validate_input(self, workflow_name: str, orchestration_type: str = None, format_type: str = None):
        """Validate input parameters for orchestration operations."""
        if not workflow_name or not isinstance(workflow_name, str):
            raise ValueError("Workflow name must be a non-empty string")
        if orchestration_type and orchestration_type not in ["task_assignment", "workflow_coordination", "resource_allocation"]:
            raise ValueError("Orchestration type must be task_assignment, workflow_coordination, or resource_allocation")
        if format_type and format_type not in ["md", "csv", "json"]:
            raise ValueError("Format type must be 'md', 'csv', or 'json'")

    def _load_workflow_history(self):
        """Load workflow history from data file"""
        try:
            # Clear existing history to prevent duplicates
            self.workflow_history.clear()
            
            if self.data_paths["workflow-history"].exists():
                with open(self.data_paths["workflow-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.workflow_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load workflow history: {e}")

    def _save_workflow_history(self):
        """Save workflow history to data file"""
        try:
            # Ensure directory exists (only if it doesn't already exist)
            if not self.data_paths["workflow-history"].parent.exists():
                self.data_paths["workflow-history"].parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_paths["workflow-history"], "w") as f:
                f.write("# Workflow History\n\n")
                for workflow in self.workflow_history[-50:]:  # Keep last 50 workflows
                    f.write(f"- {workflow}\n")
        except Exception as e:
            logger.error(f"Could not save workflow history: {e}")
            raise  # Re-raise to allow proper error handling

    def _load_orchestration_history(self):
        """Load orchestration history from data file"""
        try:
            # Clear existing history to prevent duplicates
            self.orchestration_history.clear()
            
            if self.data_paths["orchestration-history"].exists():
                with open(self.data_paths["orchestration-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.orchestration_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load orchestration history: {e}")

    def _save_orchestration_history(self):
        """Save orchestration history to data file"""
        try:
            # Ensure directory exists (only if it doesn't already exist)
            if not self.data_paths["orchestration-history"].parent.exists():
                self.data_paths["orchestration-history"].parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_paths["orchestration-history"], "w") as f:
                f.write("# Orchestration History\n\n")
                for orchestration in self.orchestration_history[-50:]:  # Keep last 50 orchestrations
                    f.write(f"- {orchestration}\n")
        except Exception as e:
            logger.error(f"Could not save orchestration history: {e}")
            raise  # Re-raise to allow proper error handling

    def show_help(self):
        """Show available commands"""
        help_text = """
Orchestrator Agent Commands:
  help                    - Show this help message
  start-workflow          - Start a workflow
  monitor-workflows       - Monitor active workflows
  orchestrate-agents      - Orchestrate agent activities
  manage-escalations      - Manage workflow escalations
  analyze-metrics         - Analyze orchestration metrics
  show-workflow-history   - Show workflow history
  show-orchestration-history - Show orchestration history
  show-best-practices     - Show orchestration best practices
  show-changelog          - Show orchestrator changelog
  export-report [format]  - Export orchestration report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Run the agent and listen for events
  show-status             - Show agent status
  list-workflows          - List available workflows
  show-history            - Show event history
  replay-history          - Replay event history
  show-workflow-status    - Show specific workflow status
  show-metrics            - Show metrics

Message Bus Integration Commands:
  initialize-message-bus  - Initialize Message Bus integration
  message-bus-status      - Show Message Bus status and metrics
  publish-event           - Publish event to Message Bus
  subscribe-event         - Subscribe to Message Bus events
  list-events             - List supported events
  event-history           - Show recent event history
  performance-metrics     - Show performance metrics

Enhanced MCP Phase 2 Commands:
  enhanced-collaborate    - Enhanced collaboration with other agents
  enhanced-security       - Security-aware operations
  enhanced-performance    - Performance-optimized operations
  trace-operation         - Trace specific operations
  trace-performance       - Performance tracing
  trace-error             - Error tracing and logging
  tracing-summary         - Overview of tracing data
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "workflow-template":
                path = self.template_paths["workflow-template"]
            elif resource_type == "orchestration-template":
                path = self.template_paths["orchestration-template"]
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

    def show_workflow_history(self):
        """Show workflow history"""
        self._ensure_history_loaded()
        if not self.workflow_history:
            print("No workflow history available.")
            return
        print("Workflow History:")
        print("=" * 50)
        for i, workflow in enumerate(self.workflow_history[-10:], 1):
            print(f"{i}. {workflow}")

    def show_orchestration_history(self):
        """Show orchestration history"""
        self._ensure_history_loaded()
        if not self.orchestration_history:
            print("No orchestration history available.")
            return
        print("Orchestration History:")
        print("=" * 50)
        for i, orchestration in enumerate(self.orchestration_history[-10:], 1):
            print(f"{i}. {orchestration}")

    def monitor_workflows(self) -> Dict[str, Any]:
        """Monitor active workflows with enhanced functionality."""
        # Validate input
        self.validate_input("workflow_monitoring")
        
        logger.info("Monitoring active workflows")

        # Simulate workflow monitoring
        time.sleep(1)

        monitoring_result = {
            "monitoring_type": "Workflow Monitoring",
            "status": "completed",
            "active_workflows": {
                "automated_deployment": {
                    "status": "running",
                    "progress": "75%",
                    "current_step": "deployment_executed",
                    "start_time": datetime.now().isoformat(),
                    "estimated_completion": "2 hours"
                },
                "feature_delivery": {
                    "status": "paused",
                    "progress": "60%",
                    "current_step": "acceptance_required",
                    "start_time": datetime.now().isoformat(),
                    "pause_reason": "Waiting for HITL approval"
                },
                "security_review": {
                    "status": "completed",
                    "progress": "100%",
                    "current_step": "security_review_completed",
                    "start_time": datetime.now().isoformat(),
                    "completion_time": datetime.now().isoformat()
                }
            },
            "workflow_metrics": {
                "total_workflows": 15,
                "active_workflows": 2,
                "completed_workflows": 12,
                "failed_workflows": 1,
                "average_completion_time": "4.2 hours",
                "success_rate": "92%"
            },
            "performance_indicators": {
                "workflow_efficiency": "85%",
                "resource_utilization": "78%",
                "agent_coordination": "92%",
                "escalation_rate": "8%",
                "hitl_approval_rate": "95%"
            },
            "alerts": [
                {
                    "type": "workflow_paused",
                    "workflow": "feature_delivery",
                    "message": "Workflow paused waiting for HITL approval",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "resource_high_usage",
                    "message": "High resource usage detected",
                    "severity": "low",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "recommendations": [
                "Consider automating HITL approval process for low-risk changes",
                "Optimize resource allocation for better efficiency",
                "Implement proactive monitoring for workflow bottlenecks"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "OrchestratorAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("OrchestratorAgent", MetricType.SUCCESS_RATE, 92, "%")

        logger.info(f"Workflow monitoring completed: {monitoring_result}")
        return monitoring_result

    def orchestrate_agents(self, orchestration_type: str = "task_assignment", task_description: str = "Feature development") -> Dict[str, Any]:
        """Orchestrate agents for task execution with input validation."""
        # Input validation
        if not orchestration_type or not isinstance(orchestration_type, str):
            raise ValueError("Orchestration type must be a non-empty string")
        if not task_description or not isinstance(task_description, str):
            raise ValueError("Task description must be a non-empty string")
            
        valid_orchestration_types = ["task_assignment", "workflow_coordination", "resource_allocation"]
        if orchestration_type not in valid_orchestration_types:
            raise ValueError(f"Orchestration type must be one of: {', '.join(valid_orchestration_types)}")
        
        logger.info(f"Orchestrating agents for {orchestration_type}: {task_description}")

        # Simulate agent orchestration
        time.sleep(1)

        orchestration_result = {
            "orchestration_id": hashlib.sha256(f"{orchestration_type}_{task_description}".encode()).hexdigest()[:8],
            "orchestration_type": orchestration_type,
            "task_description": task_description,
            "status": "completed",
            "agent_assignments": {
                "ProductOwner": {
                    "role": "Requirements definition",
                    "priority": "high",
                    "estimated_duration": "2 days",
                    "dependencies": []
                },
                "Architect": {
                    "role": "System design",
                    "priority": "high",
                    "estimated_duration": "3 days",
                    "dependencies": ["ProductOwner"]
                },
                "FrontendDeveloper": {
                    "role": "UI implementation",
                    "priority": "medium",
                    "estimated_duration": "5 days",
                    "dependencies": ["Architect"]
                },
                "BackendDeveloper": {
                    "role": "API development",
                    "priority": "medium",
                    "estimated_duration": "4 days",
                    "dependencies": ["Architect"]
                },
                "TestEngineer": {
                    "role": "Testing and validation",
                    "priority": "medium",
                    "estimated_duration": "3 days",
                    "dependencies": ["FrontendDeveloper", "BackendDeveloper"]
                }
            },
            "coordination_plan": {
                "kickoff_meeting": "Day 1 - Requirements alignment",
                "design_review": "Day 3 - Architecture review",
                "development_sync": "Day 5 - Development progress",
                "testing_coordination": "Day 8 - Testing coordination",
                "delivery_review": "Day 10 - Final delivery review"
            },
            "communication_channels": {
                "daily_standup": "Slack channel #feature-dev",
                "technical_discussions": "Slack channel #tech-discussions",
                "escalations": "Slack channel #escalations",
                "documentation": "Confluence space"
            },
            "success_criteria": [
                "All agents complete their tasks on time",
                "Quality standards are met",
                "Stakeholder approval is obtained",
                "Documentation is complete"
            ],
            "risk_mitigation": {
                "delays": "Buffer time included in schedule",
                "conflicts": "Clear escalation procedures",
                "quality_issues": "Regular review checkpoints",
                "communication_gaps": "Structured communication plan"
            },
            "performance_metrics": {
                "coordination_efficiency": "88%",
                "communication_effectiveness": "92%",
                "task_completion_rate": "95%",
                "stakeholder_satisfaction": "90%"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "OrchestratorAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("OrchestratorAgent", MetricType.SUCCESS_RATE, 88, "%")

        # Add to orchestration history
        orchestration_entry = f"{datetime.now().isoformat()}: Agent orchestration completed for {orchestration_type} - {task_description}"
        self.orchestration_history.append(orchestration_entry)
        self._save_orchestration_history()

        logger.info(f"Agent orchestration completed: {orchestration_result}")
        return orchestration_result

    async def use_enhanced_mcp_tools(self, orchestration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard orchestration tools")
            return {"orchestration_result": orchestration_data}
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": orchestration_data.get("capabilities", []),
                "performance_metrics": orchestration_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Orchestration-specific enhanced tools
            orchestration_enhanced_result = await self.use_orchestration_specific_enhanced_tools(orchestration_data)
            enhanced_data.update(orchestration_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_orchestration_operation(orchestration_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_orchestration_specific_enhanced_tools(self, orchestration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use orchestration-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced workflow orchestration
            if "workflow_orchestration" in orchestration_data:
                workflow_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_workflow_orchestration", {
                    "workflow_data": orchestration_data["workflow_orchestration"],
                    "orchestration_type": orchestration_data.get("orchestration_type", "task_assignment"),
                    "coordination_level": orchestration_data.get("coordination_level", "comprehensive")
                })
                enhanced_tools["enhanced_workflow_orchestration"] = workflow_result
            
            # Enhanced agent coordination
            if "agent_coordination" in orchestration_data:
                coordination_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_agent_coordination", {
                    "coordination_data": orchestration_data["agent_coordination"],
                    "agents": orchestration_data.get("agents", []),
                    "coordination_strategy": orchestration_data.get("coordination_strategy", "adaptive")
                })
                enhanced_tools["enhanced_agent_coordination"] = coordination_result
            
            # Enhanced team collaboration
            if "team_collaboration" in orchestration_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "Scrummaster", "Architect", "QualityGuardian"],
                    {
                        "type": "orchestration_review",
                        "content": orchestration_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced resource allocation
            if "resource_allocation" in orchestration_data:
                resource_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_resource_allocation", {
                    "resource_data": orchestration_data["resource_allocation"],
                    "allocation_strategy": orchestration_data.get("allocation_strategy", "optimized"),
                    "resource_constraints": orchestration_data.get("resource_constraints", [])
                })
                enhanced_tools["enhanced_resource_allocation"] = resource_result
            
            logger.info(f"Orchestration-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in orchestration-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_orchestration_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace orchestration operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "orchestration_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "workflow_complexity": len(operation_data.get("workflows", [])),
                    "agent_coordination": len(operation_data.get("agent_coordination", [])),
                    "collaboration_agents": len(operation_data.get("team_collaboration", {}).get("agents", []))
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("orchestration_operation", trace_data)
            
            logger.info(f"Orchestration operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

    async def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """Trace operations for monitoring and debugging."""
        try:
            if not self.tracing_enabled or not self.tracer:
                return False
            
            trace_data = {
                "agent": self.agent_name,
                "operation": operation_name,
                "timestamp": datetime.now().isoformat(),
                "attributes": attributes or {}
            }
            
            await self.tracer.trace_operation(trace_data)
            return True
            
        except Exception as e:
            logger.warning(f"Tracing operation failed: {e}")
            return False

    def manage_escalations(self, escalation_type: str = "workflow_blocked", workflow_name: str = "feature_delivery") -> Dict[str, Any]:
        """Manage escalations with input validation."""
        # Input validation
        if not escalation_type or not isinstance(escalation_type, str):
            raise ValueError("Escalation type must be a non-empty string")
        if not workflow_name or not isinstance(workflow_name, str):
            raise ValueError("Workflow name must be a non-empty string")
            
        valid_escalation_types = ["workflow_blocked", "agent_failure", "resource_shortage", "deadline_missed"]
        if escalation_type not in valid_escalation_types:
            raise ValueError(f"Escalation type must be one of: {', '.join(valid_escalation_types)}")
        
        logger.info(f"Managing escalation: {escalation_type} for workflow: {workflow_name}")

        # Simulate escalation management
        time.sleep(1)

        escalation_result = {
            "escalation_id": hashlib.sha256(f"{escalation_type}_{workflow_name}".encode()).hexdigest()[:8],
            "escalation_type": escalation_type,
            "workflow_name": workflow_name,
            "status": "resolved",
            "escalation_details": {
                "trigger": "HITL approval timeout",
                "severity": "medium",
                "impact": "Workflow delayed by 2 hours",
                "affected_agents": ["ProductOwner", "FrontendDeveloper"],
                "root_cause": "Stakeholder unavailability"
            },
            "escalation_process": {
                "detection": "Automated monitoring detected timeout",
                "notification": "Alert sent to Product Owner",
                "assessment": "Impact assessment completed",
                "resolution": "Manual approval granted",
                "follow_up": "Process improvement recommendations made"
            },
            "resolution_actions": [
                "Product Owner manually approved the change",
                "Workflow resumed normal operation",
                "Stakeholder availability improved",
                "Escalation procedures updated"
            ],
            "prevention_measures": [
                "Implement backup approvers",
                "Reduce HITL timeout threshold",
                "Improve stakeholder communication",
                "Add automated reminders"
            ],
            "escalation_metrics": {
                "time_to_detection": "5 minutes",
                "time_to_resolution": "2 hours",
                "escalation_frequency": "5% of workflows",
                "resolution_success_rate": "95%"
            },
            "lessons_learned": [
                "Backup approvers are essential for workflow continuity",
                "Clear escalation procedures improve resolution time",
                "Proactive communication reduces escalation frequency",
                "Automated monitoring enables quick detection"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "OrchestratorAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("OrchestratorAgent", MetricType.SUCCESS_RATE, 85, "%")

        logger.info(f"Escalation management completed: {escalation_result}")
        return escalation_result

    def analyze_metrics(self, metrics_type: str = "workflow_performance", timeframe: str = "30 days") -> Dict[str, Any]:
        """Analyze orchestration metrics with enhanced functionality."""
        logger.info(f"Analyzing {metrics_type} metrics")

        # Simulate metrics analysis
        time.sleep(1)

        analysis_result = {
            "analysis_type": f"{metrics_type} Analysis",
            "timeframe": timeframe,
            "status": "completed",
            "key_metrics": {
                "workflow_success_rate": "92%",
                "average_completion_time": "4.2 hours",
                "escalation_rate": "8%",
                "hitl_approval_rate": "95%",
                "agent_coordination_efficiency": "88%",
                "resource_utilization": "78%"
            },
            "trend_analysis": {
                "success_rate_trend": "improving",
                "completion_time_trend": "decreasing",
                "escalation_rate_trend": "stable",
                "coordination_efficiency_trend": "improving"
            },
            "performance_insights": [
                {
                    "insight": "Workflow success rate improved by 5%",
                    "cause": "Better agent coordination and communication",
                    "impact": "Increased productivity and reduced delays"
                },
                {
                    "insight": "Average completion time reduced by 15%",
                    "cause": "Streamlined processes and automation",
                    "impact": "Faster delivery and improved efficiency"
                },
                {
                    "insight": "Escalation rate remains stable at 8%",
                    "cause": "Consistent process quality and monitoring",
                    "impact": "Predictable workflow management"
                }
            ],
            "recommendations": [
                {
                    "recommendation": "Implement additional automation for routine tasks",
                    "expected_impact": "Reduce completion time by 10%",
                    "effort_required": "medium"
                },
                {
                    "recommendation": "Enhance agent training and communication",
                    "expected_impact": "Improve coordination efficiency by 5%",
                    "effort_required": "low"
                },
                {
                    "recommendation": "Optimize resource allocation",
                    "expected_impact": "Increase resource utilization by 8%",
                    "effort_required": "medium"
                }
            ],
            "benchmark_comparison": {
                "industry_average": {
                    "success_rate": "85%",
                    "completion_time": "6 hours",
                    "escalation_rate": "12%"
                },
                "our_performance": {
                    "success_rate": "92%",
                    "completion_time": "4.2 hours",
                    "escalation_rate": "8%"
                },
                "performance_gap": {
                    "success_rate": "+7%",
                    "completion_time": "-30%",
                    "escalation_rate": "-4%"
                }
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "OrchestratorAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("OrchestratorAgent", MetricType.SUCCESS_RATE, 90, "%")

        logger.info(f"Metrics analysis completed: {analysis_result}")
        return analysis_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export orchestration report in specified format."""
        # Validate format type
        if format_type not in ["md", "csv", "json"]:
            raise ValueError("Format type must be 'md', 'csv', or 'json'")

        if not report_data:
            report_data = {
                "report_type": "Orchestration Report",
                "timeframe": "Last 30 days",
                "status": "completed",
                "workflows_managed": 25,
                "escalations_handled": 3,
                "success_rate": "92%",
                "timestamp": datetime.now().isoformat(),
                "agent": "OrchestratorAgent"
            }

        try:
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "csv":
                self._export_csv(report_data)
            elif format_type == "json":
                self._export_json(report_data)
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise

    def _export_markdown(self, report_data: Dict):
        """Export report data as markdown."""
        output_file = f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Orchestration Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Timeframe**: {report_data.get('timeframe', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Workflows Managed**: {report_data.get('workflows_managed', 0)}
- **Escalations Handled**: {report_data.get('escalations_handled', 0)}
- **Success Rate**: {report_data.get('success_rate', 'N/A')}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Recent Workflows
{chr(10).join([f"- {workflow}" for workflow in self.workflow_history[-5:]])}

## Recent Orchestrations
{chr(10).join([f"- {orchestration}" for orchestration in self.orchestration_history[-5:]])}
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        output_file = f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Timeframe", report_data.get("timeframe", "N/A")])
            writer.writerow(["Status", report_data.get("status", "N/A")])
            writer.writerow(["Workflows Managed", report_data.get("workflows_managed", 0)])
            writer.writerow(["Escalations Handled", report_data.get("escalations_handled", 0)])
            writer.writerow(["Success Rate", report_data.get("success_rate", "N/A")])

        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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
        try:
            logger.info("Starting orchestrator collaboration example...")

            # Publish workflow start
            await self.publish_agent_event(EventTypes.WORKFLOW_STARTED, {
                "agent": "OrchestratorAgent",
                "workflow_type": "feature_delivery",
                "timestamp": datetime.now().isoformat()
            })

            # Monitor workflows
            monitoring_result = self.monitor_workflows()

            # Orchestrate agents
            self.orchestrate_agents("task_assignment", "Feature development")

            # Manage escalations
            self.manage_escalations("workflow_blocked", "feature_delivery")
            
            # Quality gate check via QualityGuardian (no publish here)
            self.manage_escalations("quality_gate_failed", "feature_development")

            # Idea validation via StrategiePartner
            await self.publish_agent_event(EventTypes.IDEA_VALIDATION_REQUESTED, {
                "idea_description": "A mobile app for task management",
                "agent": "OrchestratorAgent",
                "timestamp": datetime.now().isoformat()
            })

            # Publish completion
            await self.publish_agent_event(EventTypes.ORCHESTRATION_COMPLETED, {
                "status": "success",
                "agent": "OrchestratorAgent",
                "workflows_managed": 3,
                "escalations_handled": 1
            })

            # Save context
            save_context("OrchestratorAgent", "status", {"orchestration_status": "completed"})

            # Notify via Slack
            try:
                send_slack_message(f"Orchestration completed with {monitoring_result['workflow_metrics']['success_rate']} success rate")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")

            print("Collaboration example completed successfully.")
            context = get_context("OrchestratorAgent")
            print(f"Retrieved context: {context}")
        except Exception as e:
            logger.error(f"Collaboration example failed: {e}")
            print(f"❌ Error in collaboration: {e}")

    # Message Bus Event Handlers
    async def _handle_workflow_execution_requested(self, event):
        """Handle workflow execution requested events."""
        try:
            workflow_name = event.get("data", {}).get("workflow_name", "unknown")
            logger.info(f"Handling workflow execution requested: {workflow_name}")
            
            # Start the workflow
            result = self.start_workflow(workflow_name)
            
            # Publish workflow started event via wrapper
            await self.publish_agent_event(
                EventTypes.WORKFLOW_EXECUTION_STARTED,
                {
                    "workflow_name": workflow_name,
                    "status": "started",
                    "result": result
                }
            )

            logger.info(f"Workflow execution started: {workflow_name}")
        except Exception as e:
            logger.error(f"Error handling workflow execution requested: {e}")

    async def _handle_workflow_optimization_requested(self, event):
        """Handle workflow optimization requested events."""
        try:
            workflow_name = event.get("data", {}).get("workflow_name", "unknown")
            logger.info(f"Handling workflow optimization requested: {workflow_name}")
            
            # Optimize the workflow
            result = self.analyze_metrics("workflow_performance", "30 days")
            
            # Publish optimization completed event
            await self.publish_agent_event(
                EventTypes.WORKFLOW_OPTIMIZATION_COMPLETED,
                {
                    "workflow_name": workflow_name,
                    "optimization_result": result
                }
            )
            
            logger.info(f"Workflow optimization completed: {workflow_name}")
        except Exception as e:
            logger.error(f"Error handling workflow optimization requested: {e}")

    async def _handle_workflow_monitoring_requested(self, event):
        """Handle workflow monitoring requested events."""
        try:
            logger.info("Handling workflow monitoring requested")
            
            # Monitor workflows
            result = self.monitor_workflows()
            
            # Publish monitoring completed event
            await self.publish_agent_event(
                EventTypes.WORKFLOW_MONITORING_COMPLETED,
                {
                    "monitoring_result": result
                }
            )
            
            logger.info("Workflow monitoring completed")
        except Exception as e:
            logger.error(f"Error handling workflow monitoring requested: {e}")

    async def _handle_agent_collaboration_requested(self, event):
        """Handle agent collaboration requested events."""
        try:
            target_agent = event.get("data", {}).get("target_agent", "unknown")
            task = event.get("data", {}).get("task", "unknown")
            logger.info(f"Handling agent collaboration requested: {target_agent} - {task}")
            
            # Request collaboration
            result = await self.request_collaboration(target_agent, task)
            
            logger.info(f"Agent collaboration completed: {target_agent}")
        except Exception as e:
            logger.error(f"Error handling agent collaboration requested: {e}")

    async def _handle_task_delegated(self, event):
        """Handle task delegated events."""
        try:
            task = event.get("data", {}).get("task", "unknown")
            target_agent = event.get("data", {}).get("target_agent", "unknown")
            logger.info(f"Handling task delegated: {task} to {target_agent}")
            
            # Accept the delegated task
            result = await self.accept_task(task, target_agent)
            
            logger.info(f"Task delegation accepted: {task}")
        except Exception as e:
            logger.error(f"Error handling task delegated: {e}")

    # Original functionality preserved
    def load_event_log(self):
        try:
            with open(EVENT_LOG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_event_log(self):
        with open(EVENT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.event_log, f, indent=2)

    def log_event(self, event):
        event["timestamp"] = datetime.now().isoformat()
        self.event_log.append(event)
        self.save_event_log()

    async def route_event(self, event):
        event_type = event.get("event_type")
        self.log_event(event)
        if event_type == "feedback":
            await self.publish_agent_event(EventTypes.FEEDBACK_RECEIVED, event)
        elif event_type == "pipeline_advice":
            await self.publish_agent_event(EventTypes.PIPELINE_ADVICE_REQUESTED, event)
        logging.info(f"[Orchestrator] Event gerouteerd: {event_type}")

    def intelligent_task_assignment(self, task_desc):
        if not task_desc or not isinstance(task_desc, str):
            raise ValueError("Task description must be a non-empty string")
        
        try:
            prompt = f"Welke agent is het meest geschikt voor deze taak: '{task_desc}'? Kies uit: ProductOwner, Architect, TestEngineer, QualityGuardian, StrategiePartner, WorkflowAutomator, FeedbackAgent, DevOpsInfra, Retrospective. Geef alleen de agentnaam als JSON."
            structured_output = '{"agent": "..."}'
            result = ask_openai(prompt, structured_output=structured_output)
            agent = result.get("agent")
            logging.info(f"[Orchestrator] LLM adviseert agent: {agent} voor taak: {task_desc}")
            return agent
        except Exception as e:
            logger.error(f"Failed to get intelligent task assignment: {e}")
            error_result = f"Error getting task assignment: {e}"
            logging.info(f"[Orchestrator][LLM Task Assignment Error]: {error_result}")
            return "ProductOwner"  # Default fallback

    def set_workflow_status(self, workflow_name, status):
        self.status[workflow_name] = status
        self.log_event({"event_type": "workflow_status", "workflow": workflow_name, "status": status})
        logging.info(f"[Orchestrator] Workflow '{workflow_name}' status: {status}")

    def get_workflow_status(self, workflow_name):
        return self.status.get(workflow_name, "onbekend")

    def start_workflow(self, workflow_name, slack_channel=None):
        """
        Start een workflow en coördineer alle stappen, inclusief HITL-momenten.
        :param workflow_name: Naam van de workflow (str)
        :param slack_channel: Slack kanaal voor notificaties (str)
        """
        if slack_channel is None:
            slack_channel = DEFAULT_SLACK_CHANNEL
        if workflow_name not in WORKFLOW_TEMPLATES:
            logging.error(f"Workflow '{workflow_name}' niet gevonden.")
            send_slack_message(f":x: Workflow '{workflow_name}' niet gevonden.", channel=slack_channel, use_api=True)
            # In development mode, create a mock workflow response
            if os.getenv("DEV_MODE") == "true":
                return {"status": "mock_workflow", "message": f"Mock workflow '{workflow_name}' created for development"}
            return
        self.set_workflow_status(workflow_name, "lopend")
        log_workflow_start(workflow_name)
        logging.info(f"[Orchestrator] Start workflow: {workflow_name}")
        send_slack_message(f":rocket: Workflow *{workflow_name}* gestart door Orchestrator.", channel=slack_channel, use_api=True)

        # Add to workflow history
        workflow_entry = f"{datetime.now().isoformat()}: Workflow started - {workflow_name}"
        self.workflow_history.append(workflow_entry)
        self._save_workflow_history()

        for event in WORKFLOW_TEMPLATES[workflow_name]:
            event_type = event["event_type"]
            desc = event.get("desc", event_type)
            # HITL-moment: stuur alert en wacht op beslissing
            if event.get("hitl"):
                METRICS["hitl_moments"] = METRICS.get("hitl_moments", 0) + 1
                save_metrics()
                alert_id = f"{workflow_name}_{event_type}_{int(time.time())}"
                send_human_in_loop_alert(
                    reason=desc,
                    channel=slack_channel,
                    alert_id=alert_id
                )
                logging.info(f"[Orchestrator] HITL-alert verstuurd: {desc} (alert_id={alert_id})")
                send_slack_message(f":hourglass_flowing_sand: Wachten op goedkeuring voor stap: *{desc}*.", channel=slack_channel, use_api=True)
                # Wacht op HITL-beslissing
                approved = self.wait_for_hitl_decision(alert_id)
                if not approved:
                    METRICS["escalaties"] = METRICS.get("escalaties", 0) + 1
                    save_metrics()
                    self.set_workflow_status(workflow_name, "gepauzeerd")
                    send_slack_message(f":no_entry: Workflow *{workflow_name}* gepauzeerd of afgebroken door HITL. Escalatie naar Product Owner.", channel=slack_channel, use_api=True)
                    send_slack_message(f":rotating_light: Escalatie: Workflow *{workflow_name}* gepauzeerd door HITL. Product Owner wordt gevraagd om actie te ondernemen.", channel=PO_CHANNEL, use_api=True)
                    logging.warning(f"[Orchestrator] Workflow '{workflow_name}' gepauzeerd/afgebroken door HITL. Escalatie verstuurd.")
                    break
                send_slack_message(":white_check_mark: HITL-goedkeuring ontvangen, workflow vervolgt.", channel=slack_channel, use_api=True)
            else:
                try:
                    # Use Message Bus Integration instead of old publish function
                    if self.message_bus_integration:
                        asyncio.create_task(self.message_bus_integration.publish_event(event_type, event))
                    logging.info(f"[Orchestrator] Event gepubliceerd: {event_type} ({desc})")
                    send_slack_message(f":information_source: Stap *{desc}* gestart.", channel=slack_channel, use_api=True)
                except Exception as e:
                    METRICS["escalaties"] = METRICS.get("escalaties", 0) + 1
                    save_metrics()
                    self.set_workflow_status(workflow_name, "geblokkeerd")
                    logging.exception(f"[Orchestrator] Fout bij publiceren event {event_type}: {e}")
                    send_slack_message(f":x: Fout bij stap *{desc}*: {e}", channel=slack_channel, use_api=True)
                    send_slack_message(f":rotating_light: Escalatie: Workflow *{workflow_name}* geblokkeerd door fout. Product Owner wordt gevraagd om actie te ondernemen.", channel=PO_CHANNEL, use_api=True)
                    break
                # Optioneel: wacht op bevestiging van agent (kan uitgebreid worden)
        if self.get_workflow_status(workflow_name) == "lopend":
            self.set_workflow_status(workflow_name, "afgerond")
        log_workflow_end(workflow_name)
        send_slack_message(f":tada: Workflow *{workflow_name}* afgerond (of gepauzeerd).", channel=slack_channel, use_api=True)
        logging.info(f"[Orchestrator] Workflow '{workflow_name}' afgerond of gepauzeerd.")

    def list_workflows(self):
        print("Beschikbare workflows:")
        for wf in WORKFLOW_TEMPLATES:
            print(f"- {wf}")

    def show_status(self):
        self.monitor_agents()

    def show_history(self):
        print("Event history:")
        for event in self.event_log:
            print(event)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Orchestrator agent."""
        self._ensure_history_loaded()
        return {
            "agent_name": self.agent_name,
            "workflow_history_count": len(self.workflow_history),
            "orchestration_history_count": len(self.orchestration_history),
            "active_workflows": len([s for s in self.status.values() if s == "active"]),
            "last_workflow": self.workflow_history[-1] if self.workflow_history else None,
            "last_orchestration": self.orchestration_history[-1] if self.orchestration_history else None,
            "event_log_count": len(self.event_log) if self.event_log else 0,
            "status": "active"
        }

    async def replay_history(self):
        print("Replaying event history...")
        for event in self.event_log:
            try:
                await self.publish_agent_event(event.get("event_type"), event)
                print(f"Event gereplayed: {event}")
            except Exception as e:
                print(f"Error replaying event: {e}")

    async def wait_for_hitl_decision(self, alert_id, timeout=3600):
        """
        Wacht op een hitl_decision event met het juiste alert_id.
        :param alert_id: Unieke alert_id van de HITL stap (str)
        :param timeout: Timeout in seconden (int)
        :return: True als goedgekeurd, False als afgewezen of timeout
        """
        start = time.time()
        poll_interval = 0.05
        while time.time() - start < timeout:
            try:
                if self.message_bus:
                    events = await self.message_bus.get_events(EventTypes.HITL_DECISION)
                    for ev in events:
                        data = getattr(ev, "data", {}) if not isinstance(ev, dict) else ev.get("data", {})
                        if data.get("alert_id") == alert_id:
                            return bool(data.get("approved", False))
                await asyncio.sleep(poll_interval)
            except Exception as e:
                logging.warning(f"[Orchestrator] Error checking HITL decision: {e}")
                await asyncio.sleep(poll_interval)
        logging.warning(f"[Orchestrator] Timeout bij wachten op HITL-beslissing (alert_id={alert_id})")
        return False

    async def subscribe_to_event(self, event_type: str, callback):
        """Passthrough voor tests: abonneer op event via core message bus."""
        if not self.message_bus:
            self.message_bus = get_message_bus()
        return await self.message_bus.subscribe(event_type, callback)

    def monitor_agents(self):
        agents = ["ProductOwner", "Architect", "TestEngineer", "FeedbackAgent", "DevOpsInfra", "Retrospective", "MobileDeveloper"]
        for agent in agents:
            status = get_context(agent, context_type="status")
            self.status[agent] = status
        logging.info(f"[Orchestrator] Agent status: {self.status}")
        print("Agent status:", self.status)

    def run(self):
        """Run the agent and listen for events."""
        logger.info("OrchestratorAgent ready and listening for events...")
        print("[Orchestrator] Ready and listening for events...")
        asyncio.run(self.collaborate_example())
    
    async def run_async(self):
        """Run the agent with enhanced MCP, tracing, and message bus initialization."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize message bus integration
        await self.initialize_message_bus()
        
        print("🎯 Orchestrator Agent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled")
        
        logger.info("OrchestratorAgent ready and listening for events...")
        print("[Orchestrator] Ready and listening for events...")
        await self.collaborate_example()
    
    @classmethod
    def run_agent(cls):
        """Class method to run the Orchestrator agent."""
        agent = cls()
        agent.run()
    
    @classmethod
    async def run_agent_async(cls):
        """Class method to run the Orchestrator agent with enhanced MCP."""
        agent = cls()
        await agent.run_async()

    async def publish_agent_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Module-level helper to publish events with uniform contract when no self is available."""
        try:
            payload = dict(data) if isinstance(data, dict) else {"data": data}
            if "status" not in payload and str(event_type).endswith("_COMPLETED"):
                payload["status"] = "completed"
            message_bus = get_message_bus()
            return await message_bus.publish_event(event_type, payload)
        except Exception as e:
            logger.error(f"Failed to publish event from orchestrator helper: {e}")
            return False

    async def request_collaboration(self, payload: Dict[str, Any]) -> bool:
        return await self.publish_agent_event(EventTypes.AGENT_COLLABORATION_REQUESTED, payload)

    async def accept_task(self, payload: Dict[str, Any]) -> bool:
        return await self.publish_agent_event(EventTypes.TASK_ACCEPTED, payload)

# Workflow templates
WORKFLOW_TEMPLATES = {
    # --- Bestaande workflows ---
    "feature": [
        {"event_type": "new_task", "task_desc": "Nieuwe feature ontwikkelen"},
        {"event_type": "user_story_requested", "requirement": "Feature requirement"},
        {"event_type": "test_generation_requested", "function_description": "Feature test"},
    ],
    "incident_response": [
        {"event_type": "incident_reported", "incident_desc": "Incident details"},
        {"event_type": "incident_response_requested", "incident_desc": "Incident details"},
    ],
    # --- Geavanceerde workflows ---
    "automated_deployment": [
        {"event_type": "build_triggered", "desc": "Build gestart"},
        {"event_type": "tests_requested", "desc": "Tests uitvoeren"},
        {"event_type": "tests_completed", "desc": "Tests voltooid"},
        {"event_type": "hitl_required", "desc": "Goedkeuring voor deployment", "hitl": True},
        {"event_type": "deployment_executed", "desc": "Deployment uitgevoerd"},
        {"event_type": "deployment_completed", "desc": "Deployment afgerond"},
    ],
    "feature_delivery": [
        {"event_type": "feature_planned", "desc": "Feature gepland"},
        {"event_type": "tasks_assigned", "desc": "Taken toegewezen"},
        {"event_type": "development_started", "desc": "Ontwikkeling gestart"},
        {"event_type": "testing_started", "desc": "Testen gestart"},
        {"event_type": "acceptance_required", "desc": "Acceptatie vereist", "hitl": True},
        {"event_type": "feature_delivered", "desc": "Feature opgeleverd"},
    ],
    "security_review": [
        {"event_type": "security_scan_started", "desc": "Security scan gestart"},
        {"event_type": "security_findings_reported", "desc": "Security bevindingen gerapporteerd"},
        {"event_type": "hitl_required", "desc": "Security review goedkeuring", "hitl": True},
        {"event_type": "security_review_completed", "desc": "Security review afgerond"},
    ],
    "retrospective_feedback": [
        {"event_type": "retro_planned", "desc": "Retrospective gepland"},
        {"event_type": "feedback_collected", "desc": "Feedback verzameld"},
        {"event_type": "trends_analyzed", "desc": "Trends geanalyseerd"},
        {"event_type": "retro_results_shared", "desc": "Resultaten gedeeld in Slack"},
    ],
    # --- Mobile Development Workflows ---
    "mobile_app_development": [
        {"event_type": "mobile_app_planned", "desc": "Mobile app gepland"},
        {"event_type": "ux_design_requested", "desc": "UX design voor mobile"},
        {"event_type": "mobile_development_started", "desc": "Mobile development gestart"},
        {"event_type": "cross_platform_testing", "desc": "Cross-platform testing"},
        {"event_type": "app_store_submission", "desc": "App store submission"},
        {"event_type": "hitl_required", "desc": "App store goedkeuring", "hitl": True},
        {"event_type": "mobile_app_released", "desc": "Mobile app vrijgegeven"},
    ],
    "mobile_feature_delivery": [
        {"event_type": "mobile_feature_planned", "desc": "Mobile feature gepland"},
        {"event_type": "mobile_ux_design", "desc": "Mobile UX design"},
        {"event_type": "mobile_development", "desc": "Mobile development"},
        {"event_type": "mobile_testing", "desc": "Mobile testing"},
        {"event_type": "performance_optimization", "desc": "Performance optimalisatie"},
        {"event_type": "app_store_update", "desc": "App store update"},
    ],
    "mobile_performance_optimization": [
        {"event_type": "performance_analysis", "desc": "Performance analyse"},
        {"event_type": "optimization_planning", "desc": "Optimalisatie planning"},
        {"event_type": "optimization_implementation", "desc": "Optimalisatie implementatie"},
        {"event_type": "performance_testing", "desc": "Performance testing"},
        {"event_type": "optimization_validation", "desc": "Optimalisatie validatie"},
    ],
}

# Event handlers
def handle_slack_command(event):
    data = event["data"]
    command = data.get("command")
    agent = data.get("agent")
    channel = data.get("channel")
    user = data.get("user")
    log_metric("slack_commands_received")
    logging.info(f"[Orchestrator] Slack commando ontvangen: {command} voor agent {agent} door user {user}")
    orch = OrchestratorAgent()
    if command and command.startswith("workflow status"):
        parts = command.split()
        if len(parts) >= 3:
            workflow_name = parts[2]
            status = orch.get_workflow_status(workflow_name)
            send_slack_message(f"Status van workflow *{workflow_name}*: {status}", channel=channel, use_api=True)
        else:
            send_slack_message("Gebruik: workflow status <workflow_naam>", channel=channel, use_api=True)
        return
    if command and command.strip() == "metrics":
        metrics_str = "\n".join([f"- {k}: {v}" for k, v in METRICS.items()])
        send_slack_message(f"[Orchestrator Metrics]\n{metrics_str}", channel=channel, use_api=True)
        return
    if command == "start workflow":
        send_slack_message("Workflow 'feature' wordt gestart door Orchestrator.", channel=channel, use_api=True)
        orch.start_workflow("feature")
        log_metric("workflows_started")
    else:
        send_slack_message(f"Commando '{command}' voor agent '{agent}' wordt door Orchestrator gerouteerd.", channel=channel, use_api=True)
        # Eventueel publish naar specifieke agent event

def handle_hitl_decision(event):
    data = event["data"]
    alert_id = data.get("alert_id")
    approved = data.get("approved")
    user = data.get("user")
    channel = data.get("channel")
    log_metric("hitl_decisions")
    logging.info(f"[Orchestrator] HITL beslissing: {'goedgekeurd' if approved else 'afgewezen'} door {user} voor alert {alert_id}")
    if approved:
        send_slack_message(f"✅ Human-in-the-loop: Actie goedgekeurd door <@{user}>. Workflow wordt vervolgd.", channel=channel, use_api=True)
        log_metric("workflows_completed")
        # Hier vervolgactie, bijvoorbeeld deployment starten
    else:
        send_slack_message(f"❌ Human-in-the-loop: Actie afgewezen door <@{user}>. Workflow wordt gepauzeerd en geëscaleerd naar Product Owner.", channel=channel, use_api=True)
        send_slack_message(f":rotating_light: Escalatie: Workflow gepauzeerd na afwijzing door <@{user}>. Product Owner wordt gevraagd om actie te ondernemen.", channel=PO_CHANNEL, use_api=True)
        log_metric("workflow_paused")
        # Hier workflow pauzeren of annuleren

# Note: These subscriptions are now handled by the new message bus integration
# subscribe("slack_command", handle_slack_command)
# subscribe("hitl_decision", handle_hitl_decision)

# --- Productieklare agent-handler voorbeeld ---
# Plaats dit in de relevante agent (bijv. DevOpsInfra, TestEngineer, etc.)

async def handle_build_triggered(event):
    logging.info("[DevOpsInfra] Build gestart...")
    time.sleep(2)
    await publish_agent_event(EventTypes.TEST_EXECUTION_REQUESTED, {"desc": "Tests uitvoeren"})
    logging.info("[DevOpsInfra] Build afgerond, tests_requested gepubliceerd.")

# Herhaal dit patroon voor andere events en agents.

# Extra: feedback loop bij tests_completed met failure

def handle_tests_completed(event):
    data = event.get("data", event)
    if data.get("result") == "failure":
        logging.warning("[Orchestrator] Tests gefaald, workflow keert terug naar development.")
        send_slack_message(":x: Tests zijn gefaald! Workflow keert terug naar development.", channel=ALERT_CHANNEL, use_api=True)
        send_slack_message(":rotating_light: Escalatie: Tests gefaald, Product Owner wordt gevraagd om actie te ondernemen.", channel=PO_CHANNEL, use_api=True)
        # Hier kun je eventueel een event publiceren om de workflow terug te zetten

# Note: These subscriptions are now handled by the new message bus integration
# subscribe("tests_completed", handle_tests_completed)

async def handle_quality_gate_check_requested(event):
    """Handle quality gate check requested event."""
    logger.info(f"Quality gate check requested: {event}")
    await publish_agent_event(EventTypes.QUALITY_GATE_CHECK_REQUESTED, event)

async def handle_idea_validation_requested(event):
    """Handle idea validation requested event."""
    logger.info(f"Idea validation requested: {event}")
    await publish_agent_event(EventTypes.IDEA_VALIDATION_REQUESTED, event)

async def handle_idea_refinement_requested(event):
    """Handle idea refinement requested event."""
    logger.info(f"Idea refinement requested: {event}")
    await publish_agent_event(EventTypes.IDEA_REFINEMENT_REQUESTED, event)

async def handle_epic_creation_requested(event):
    """Handle epic creation requested event."""
    logger.info(f"Epic creation requested: {event}")
    await publish_agent_event(EventTypes.EPIC_CREATION_REQUESTED, event)

async def handle_workflow_execution_requested(event):
    """Handle workflow execution requested event."""
    workflow_id = event.get("workflow_id")
    logger.info(f"Workflow execution requested for workflow: {workflow_id}")
    await publish_agent_event(EventTypes.WORKFLOW_EXECUTION_REQUESTED, {
        "workflow_id": workflow_id,
        "timestamp": datetime.now().isoformat()
    })

async def handle_workflow_optimization_requested(event):
    """Handle workflow optimization requested event."""
    workflow_id = event.get("workflow_id")
    logger.info(f"Workflow optimization requested for workflow: {workflow_id}")
    await publish_agent_event(EventTypes.WORKFLOW_OPTIMIZATION_REQUESTED, {
        "workflow_id": workflow_id,
        "timestamp": datetime.now().isoformat()
    })

async def handle_workflow_monitoring_requested(event):
    """Handle workflow monitoring requested event."""
    workflow_id = event.get("workflow_id")
    logger.info(f"Workflow monitoring requested for workflow: {workflow_id}")
    await publish_agent_event(EventTypes.WORKFLOW_MONITORING_REQUESTED, {
        "workflow_id": workflow_id,
        "timestamp": datetime.now().isoformat()
    })

# Note: These subscriptions are now handled by the new message bus integration
# subscribe("quality_gate_check_requested", handle_quality_gate_check_requested)
# subscribe("idea_validation_requested", handle_idea_validation_requested)
# subscribe("idea_refinement_requested", handle_idea_refinement_requested)
# subscribe("epic_creation_requested", handle_epic_creation_requested)
# subscribe("workflow_execution_requested", handle_workflow_execution_requested)
# subscribe("workflow_optimization_requested", handle_workflow_optimization_requested)
# subscribe("workflow_monitoring_requested", handle_workflow_monitoring_requested)

def main():
    parser = argparse.ArgumentParser(description="Orchestrator Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "start-workflow", "monitor-workflows", "orchestrate-agents",
                               "manage-escalations", "analyze-metrics", "show-workflow-history",
                               "show-orchestration-history", "show-best-practices", "show-changelog",
                               "export-report", "test", "collaborate", "run", "show-status",
                               "list-workflows", "show-history", "replay-history", "show-workflow-status",
                               "show-metrics", "initialize-mcp", "use-mcp-tool", "get-mcp-status", 
                               "use-orchestration-mcp-tools", "check-dependencies", "enhanced-collaborate", 
                               "enhanced-security", "enhanced-performance", "trace-operation", 
                               "trace-performance", "trace-error", "tracing-summary",
                               "initialize-message-bus", "message-bus-status", "publish-event", 
                               "subscribe-event", "list-events", "event-history", "performance-metrics"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--workflow", help="Workflow naam voor start-workflow of show-workflow-status")
    parser.add_argument("--orchestration-type", default="task_assignment", help="Orchestration type")
    parser.add_argument("--task-description", default="Feature development", help="Task description")
    parser.add_argument("--escalation-type", default="workflow_blocked", help="Escalation type")
    parser.add_argument("--workflow-name", default="feature_delivery", help="Workflow name")
    parser.add_argument("--metrics-type", default="workflow_performance", help="Metrics type")
    parser.add_argument("--timeframe", default="30 days", help="Timeframe for analysis")

    args = parser.parse_args()

    agent = OrchestratorAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "start-workflow":
        if not args.workflow:
            print("Geef een workflow op met --workflow")
            sys.exit(1)
            return
        agent.start_workflow(args.workflow)
    elif args.command == "monitor-workflows":
        result = agent.monitor_workflows()
        print(json.dumps(result, indent=2))
    elif args.command == "orchestrate-agents":
        result = agent.orchestrate_agents(args.orchestration_type, args.task_description)
        print(json.dumps(result, indent=2))
    elif args.command == "manage-escalations":
        result = agent.manage_escalations(args.escalation_type, args.workflow_name)
        print(json.dumps(result, indent=2))
    elif args.command == "analyze-metrics":
        result = agent.analyze_metrics(args.metrics_type, args.timeframe)
        print(json.dumps(result, indent=2))
    elif args.command == "show-workflow-history":
        agent.show_workflow_history()
    elif args.command == "show-orchestration-history":
        agent.show_orchestration_history()
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
        agent.run()
    elif args.command == "show-status":
        agent.show_status()
    elif args.command == "list-workflows":
        agent.list_workflows()
    elif args.command == "show-history":
        agent.show_history()
    elif args.command == "replay-history":
        asyncio.run(agent.replay_history())
    elif args.command == "show-workflow-status":
        if not args.workflow:
            print("Geef een workflow op met --workflow")
            sys.exit(1)
            return
        status = agent.get_workflow_status(args.workflow)
        print(f"Status van workflow '{args.workflow}': {status}")
    elif args.command == "show-metrics":
        print("\n[Orchestrator Metrics]")
        for metric, value in METRICS.items():
            print(f"{metric}: {value}")
    
    # Message Bus Integration Commands
    elif args.command == "initialize-message-bus":
        asyncio.run(agent.initialize_message_bus())
        print("✅ Message Bus Integration geïnitialiseerd")
    elif args.command == "message-bus-status":
        print("🚀 Orchestrator Message Bus Status:")
        print(f"✅ Message Bus Integration: {'Enabled' if agent.message_bus_enabled else 'Disabled'}")
        print(f"✅ Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
        print(f"✅ Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
        print(f"📊 Performance Metrics: {len(agent.performance_metrics)} metrics tracked")
        print(f"📝 Workflow History: {len(agent.workflow_history)} entries")
        print(f"📊 Orchestration History: {len(agent.orchestration_history)} entries")
    elif args.command == "publish-event":
        event_type = input("Event type: ")
        event_data = input("Event data (JSON): ")
        try:
            data = json.loads(event_data) if event_data else {}
            asyncio.run(agent.message_bus_integration.publish_event(event_type, data))
            print(f"✅ Event '{event_type}' gepubliceerd")
        except Exception as e:
            print(f"❌ Fout bij publiceren: {e}")
    elif args.command == "subscribe-event":
        event_type = input("Event type: ")
        print(f"✅ Subscribed op event '{event_type}'")
    elif args.command == "list-events":
        print("🚀 Orchestrator Supported Events:")
        print("📥 Input Events:")
        print("  - workflow_execution_requested")
        print("  - workflow_optimization_requested")
        print("  - workflow_monitoring_requested")
        print("  - agent_collaboration_requested")
        print("  - task_delegated")
        print("📤 Output Events:")
        print("  - workflow_started")
        print("  - workflow_completed")
        print("  - workflow_optimized")
        print("  - escalation_triggered")
        print("  - task_assigned")
    elif args.command == "event-history":
        print("📝 Recent Event History:")
        for event in agent.event_log[-10:]:
            print(f"  - {event.get('timestamp', 'N/A')}: {event.get('type', 'Unknown')}")
    elif args.command == "performance-metrics":
        print("📊 Orchestrator Performance Metrics:")
        for metric, value in agent.performance_metrics.items():
            print(f"  • {metric}: {value}")
    
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["ProductOwner", "Scrummaster", "Architect", "QualityGuardian"], 
                {"type": "orchestration_review", "content": {"review_type": "workflow_orchestration"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "orchestration_data": {"workflows": ["feature_delivery", "security_review"]},
                "security_requirements": ["workflow_validation", "access_control", "audit_trail"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "orchestration_data": {"workflows": ["feature_delivery", "security_review"]},
                "performance_metrics": {"workflow_efficiency": 85.5, "agent_coordination": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_orchestration_operation({
                "operation_type": "workflow_orchestration",
                "workflows": ["feature_delivery", "security_review"],
                "agent_coordination": ["ProductOwner", "Scrummaster", "Architect"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_orchestration_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"workflow_efficiency": 85.5, "agent_coordination": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_orchestration_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "workflow_orchestration", "error_message": "Workflow coordination failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for Orchestrator Agent:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print(f"Unknown command: {args.command}")
        agent.show_help()

def run_server_mode():
    """Run orchestrator in server mode with metrics thread"""
    global _metrics_thread
    print("Orchestrator is actief en luistert naar Slack events...")
    # Start metrics saver thread in server mode
    _metrics_thread = threading.Thread(target=metrics_saver, daemon=True)
    _metrics_thread.start()
    main()
    # Metrics monitor loop (optioneel)
    while True:
        time.sleep(60)
        # print_metrics() # This line is removed as per the edit hint to remove print_metrics
        # The metrics_saver thread handles periodic saving, so we don't need a separate loop here
        # unless you want to print them periodically.

if __name__ == "__main__":
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        # CLI mode - just run the command and exit
        main()
    else:
        # Server mode - run the infinite loop for listening to events
        run_server_mode()
