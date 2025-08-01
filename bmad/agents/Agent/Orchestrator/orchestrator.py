import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
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
from bmad.agents.core.communication.message_bus import get_events, publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.slack.slack_notify import send_human_in_loop_alert, send_slack_message

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

class OrchestratorAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "Orchestrator"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

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

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        try:
            logger.info("Starting orchestrator collaboration example...")

            # Publish workflow start
            publish("workflow_started", {
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
            
            # Quality gate check via QualityGuardian
            self.manage_escalations("quality_gate_failed", "feature_development")

            # Idea validation via StrategiePartner
            publish("idea_validation_requested", {
                "idea_description": "A mobile app for task management",
                "agent": "OrchestratorAgent",
                "timestamp": datetime.now().isoformat()
            })

            # Publish completion
            publish("orchestration_completed", {
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

    def route_event(self, event):
        event_type = event.get("event_type")
        self.log_event(event)
        if event_type == "feedback":
            publish("feedback_received", event)
        elif event_type == "pipeline_advice":
            publish("pipeline_advice_requested", event)
        logging.info(f"[Orchestrator] Event gerouteerd: {event_type}")

    def intelligent_task_assignment(self, task_desc):
        if not task_desc or not isinstance(task_desc, str):
            raise ValueError("Task description must be a non-empty string")
        
        try:
            prompt = f"Welke agent is het meest geschikt voor deze taak: '{task_desc}'? Kies uit: ProductOwner, Architect, TestEngineer, QualityGuardian, StrategiePartner, FeedbackAgent, DevOpsInfra, Retrospective. Geef alleen de agentnaam als JSON."
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
                    publish(event_type, event)
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

    def replay_history(self):
        print("Replaying event history...")
        for event in self.event_log:
            publish(event.get("event_type"), event)
            print(f"Event gereplayed: {event}")

    def wait_for_hitl_decision(self, alert_id, timeout=3600):
        """
        Wacht op een hitl_decision event met het juiste alert_id.
        :param alert_id: Unieke alert_id van de HITL stap (str)
        :param timeout: Timeout in seconden (int)
        :return: True als goedgekeurd, False als afgewezen of timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            events = get_events("hitl_decision")
            for e in events:
                if e["data"].get("alert_id") == alert_id:
                    approved = e["data"].get("approved")
                    logging.info(f"[Orchestrator] HITL-beslissing ontvangen: {'goedgekeurd' if approved else 'afgewezen'} (alert_id={alert_id})")
                    return approved
            time.sleep(5)
        logging.warning(f"[Orchestrator] Timeout bij wachten op HITL-beslissing (alert_id={alert_id})")
        return False

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
        self.collaborate_example()
    
    @classmethod
    def run_agent(cls):
        """Class method to run the Orchestrator agent."""
        agent = cls()
        agent.run()

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

subscribe("slack_command", handle_slack_command)
subscribe("hitl_decision", handle_hitl_decision)

# --- Productieklare agent-handler voorbeeld ---
# Plaats dit in de relevante agent (bijv. DevOpsInfra, TestEngineer, etc.)

def handle_build_triggered(event):
    logging.info("[DevOpsInfra] Build gestart...")
    # Simuleer build (in productie: start build pipeline)
    time.sleep(2)
    publish("tests_requested", {"desc": "Tests uitvoeren"})
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

subscribe("tests_completed", handle_tests_completed)

def handle_quality_gate_check_requested(event):
    """Handle quality gate check requested event."""
    logger.info(f"Quality gate check requested: {event}")
    # Trigger QualityGuardian agent
    publish("qualityguardian_quality_gate_check", event)

def handle_idea_validation_requested(event):
    """Handle idea validation requested event."""
    logger.info(f"Idea validation requested: {event}")
    # Trigger StrategiePartner agent
    publish("strategiepartner_validate_idea", event)

def handle_idea_refinement_requested(event):
    """Handle idea refinement requested event."""
    logger.info(f"Idea refinement requested: {event}")
    # Trigger StrategiePartner agent
    publish("strategiepartner_refine_idea", event)

def handle_epic_creation_requested(event):
    """Handle epic creation requested event."""
    logger.info(f"Epic creation requested: {event}")
    # Trigger StrategiePartner agent
    publish("strategiepartner_create_epic", event)

subscribe("quality_gate_check_requested", handle_quality_gate_check_requested)
subscribe("idea_validation_requested", handle_idea_validation_requested)
subscribe("idea_refinement_requested", handle_idea_refinement_requested)
subscribe("epic_creation_requested", handle_epic_creation_requested)

def main():
    parser = argparse.ArgumentParser(description="Orchestrator Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "start-workflow", "monitor-workflows", "orchestrate-agents",
                               "manage-escalations", "analyze-metrics", "show-workflow-history",
                               "show-orchestration-history", "show-best-practices", "show-changelog",
                               "export-report", "test", "collaborate", "run", "show-status",
                               "list-workflows", "show-history", "replay-history", "show-workflow-status",
                               "show-metrics"])
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
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()
    elif args.command == "show-status":
        agent.show_status()
    elif args.command == "list-workflows":
        agent.list_workflows()
    elif args.command == "show-history":
        agent.show_history()
    elif args.command == "replay-history":
        agent.replay_history()
    elif args.command == "show-workflow-status":
        if not args.workflow:
            print("Geef een workflow op met --workflow")
            sys.exit(1)
            return
        status = agent.get_workflow_status(args.workflow)
        print(f"Status van workflow '{args.workflow}': {status}")
    elif args.command == "show-metrics":
        print("\n[Orchestrator Metrics]")
        for k, v in METRICS.items():
            print(f"- {k}: {v}")

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
