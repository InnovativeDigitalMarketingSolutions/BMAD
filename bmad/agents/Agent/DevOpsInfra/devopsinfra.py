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
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DevOpsInfraAgent:
    def __init__(self):
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
        """Deploy infrastructure components with policy approval."""

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

        print(f"🚀 Deploying {infrastructure_type} infrastructure...")

        # Simulate deployment process
        deployment_steps = [
            "Validating infrastructure configuration",
            "Checking resource availability",
            "Creating infrastructure components",
            "Configuring networking",
            "Setting up monitoring",
            "Running health checks"
        ]

        for step in deployment_steps:
            print(f"  📋 {step}")
            time.sleep(0.5)  # Simulate processing time

        # Record in history
        deployment_record = f"{infrastructure_type} infrastructure deployed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.infrastructure_history.append(deployment_record)
        self._save_infrastructure_history()

        print(f"✅ {infrastructure_type} infrastructure deployed successfully!")

        return {
            "status": "success",
            "infrastructure_type": infrastructure_type,
            "deployment_steps": deployment_steps,
            "timestamp": datetime.now().isoformat(),
            "history_record": deployment_record
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

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting DevOps infrastructure collaboration example...")

        # Publish infrastructure deployment request
        publish("infrastructure_deployment_requested", {
            "agent": "DevOpsInfraAgent",
            "infrastructure_type": "kubernetes",
            "timestamp": datetime.now().isoformat()
        })

        # Deploy infrastructure
        deployment_result = self.deploy_infrastructure("kubernetes")

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
        save_context("DevOpsInfra", {"infrastructure_status": "deployed"})

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

    def run(self):
        """Run the agent and listen for events."""
        def sync_handler(event):
            asyncio.run(self.on_pipeline_advice_requested(event))

        subscribe("pipeline_advice_requested", self.on_pipeline_advice_requested)
        subscribe("incident_response_requested", self.on_incident_response_requested)
        subscribe("feedback_sentiment_analyzed", self.on_feedback_sentiment_analyzed)
        subscribe("build_triggered", self.handle_build_triggered)
        subscribe("deployment_executed", self.handle_deployment_executed)

        logger.info("DevOpsInfraAgent ready and listening for events...")
        self.collaborate_example()

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
        result = agent.deploy_infrastructure(args.infrastructure_type)
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
        agent.run()

if __name__ == "__main__":
    main()
