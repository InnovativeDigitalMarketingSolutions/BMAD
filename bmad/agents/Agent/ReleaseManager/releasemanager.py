import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
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

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ReleaseManagerAgent:
    def __init__(self):
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
            "deployment_strategy": {
                "type": "blue-green",
                "rollback_plan": "Automatic rollback on failure",
                "monitoring": "Enhanced monitoring during deployment",
                "approval_required": True
            },
            "risk_assessment": {
                "risk_level": "medium",
                "identified_risks": [
                    "Database migration complexity",
                    "Third-party service dependencies",
                    "User experience changes"
                ],
                "mitigation_strategies": [
                    "Comprehensive testing",
                    "Gradual rollout",
                    "Monitoring and alerting"
                ]
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManager", MetricType.SUCCESS_RATE, 95, "%")

        # Add to release history
        release_entry = f"{datetime.now().isoformat()}: Release {version} plan created successfully"
        self.release_history.append(release_entry)
        self._save_release_history()

        logger.info(f"Release plan created: {release_result}")
        return release_result

    def approve_release(self, version: str = "1.2.0") -> Dict[str, Any]:
        """Approve release for deployment."""
        logger.info(f"Approving release {version} for deployment")

        # Simulate release approval
        time.sleep(1)

        approval_result = {
            "version": version,
            "approval_type": "Release Approval",
            "status": "approved",
            "approval_details": {
                "approved_by": "Product Owner",
                "approval_date": datetime.now().isoformat(),
                "approval_criteria": [
                    "All tests passing",
                    "Security review completed",
                    "Performance benchmarks met",
                    "User acceptance testing passed"
                ],
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
            "stakeholder_notifications": [
                "Development team notified",
                "Operations team notified",
                "Product team notified",
                "Customer success team notified"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManager", MetricType.SUCCESS_RATE, 98, "%")

        logger.info(f"Release approved: {approval_result}")
        return approval_result

    def deploy_release(self, version: str = "1.2.0") -> Dict[str, Any]:
        """Deploy release to production."""
        logger.info(f"Deploying release {version} to production")

        # Simulate release deployment
        time.sleep(2)

        deployment_result = {
            "version": version,
            "deployment_type": "Production Deployment",
            "status": "success",
            "deployment_phases": {
                "pre_deployment": {
                    "status": "completed",
                    "checks": [
                        "Environment validation",
                        "Database backup",
                        "Service health check",
                        "Resource availability"
                    ]
                },
                "deployment": {
                    "status": "completed",
                    "steps": [
                        "Blue environment deployment",
                        "Health checks",
                        "Traffic switch",
                        "Green environment cleanup"
                    ]
                },
                "post_deployment": {
                    "status": "completed",
                    "verifications": [
                        "Service health verification",
                        "Performance monitoring",
                        "Error rate monitoring",
                        "User experience validation"
                    ]
                }
            },
            "deployment_metrics": {
                "deployment_time": "8 minutes",
                "downtime": "2 minutes",
                "success_rate": "100%",
                "error_rate": "0.1%",
                "performance_impact": "minimal"
            },
            "monitoring_results": {
                "response_time": "120ms (baseline: 125ms)",
                "throughput": "1500 req/s (baseline: 1450 req/s)",
                "error_rate": "0.1% (baseline: 0.2%)",
                "resource_usage": "65% (baseline: 60%)"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManager", MetricType.SUCCESS_RATE, 100, "%")

        # Add to release history
        release_entry = f"{datetime.now().isoformat()}: Release {version} deployed successfully to production"
        self.release_history.append(release_entry)
        self._save_release_history()

        logger.info(f"Release deployed: {deployment_result}")
        return deployment_result

    def rollback_release(self, version: str = "1.2.0", reason: str = "High error rate") -> Dict[str, Any]:
        """Rollback failed release."""
        logger.info(f"Rolling back release {version} due to: {reason}")

        # Simulate rollback
        time.sleep(2)

        rollback_result = {
            "version": version,
            "rollback_type": "Production Rollback",
            "status": "completed",
            "reason": reason,
            "rollback_phases": {
                "trigger": {
                    "status": "completed",
                    "trigger_type": "automatic",
                    "threshold_exceeded": "Error rate > 5%"
                },
                "rollback": {
                    "status": "completed",
                    "steps": [
                        "Traffic switch to previous version",
                        "Health checks",
                        "Service validation",
                        "Monitoring verification"
                    ]
                },
                "verification": {
                    "status": "completed",
                    "checks": [
                        "Service health restored",
                        "Error rate normalized",
                        "Performance restored",
                        "User experience validated"
                    ]
                }
            },
            "rollback_metrics": {
                "rollback_time": "3 minutes",
                "downtime": "1 minute",
                "success_rate": "100%",
                "error_rate": "0.1% (restored)",
                "data_loss": "none"
            },
            "post_rollback_actions": [
                "Incident investigation initiated",
                "Root cause analysis scheduled",
                "Stakeholders notified",
                "Next release planning updated"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "ReleaseManagerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("ReleaseManager", MetricType.SUCCESS_RATE, 95, "%")

        # Add to rollback history
        rollback_entry = f"{datetime.now().isoformat()}: Release {version} rolled back due to {reason}"
        self.rollback_history.append(rollback_entry)
        self._save_rollback_history()

        logger.info(f"Release rolled back: {rollback_result}")
        return rollback_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export release report in specified format."""
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

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
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

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"release_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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
        logger.info(f"Tests passed event received: {event}")
        logger.info("[ReleaseManager] Tests geslaagd, release flow gestart.")
        try:
            send_slack_message("[ReleaseManager] Tests geslaagd, release flow gestart.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Start release flow (stub)

    def on_release_approved(self, event):
        """Handle release approved event from other agents."""
        logger.info(f"Release approved event received: {event}")
        logger.info("[ReleaseManager] Release goedgekeurd door PO, release wordt live gezet.")
        try:
            send_slack_message("[ReleaseManager] Release goedgekeurd door PO, release wordt live gezet.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Zet release live (stub)

    def on_deployment_failed(self, event):
        """Handle deployment failed event from other agents."""
        logger.error(f"Deployment failed event received: {event}")
        logger.error("[ReleaseManager] Deployment failed! Rollback gestart.")
        try:
            send_slack_message("[ReleaseManager] Deployment failed! Rollback gestart.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Start rollback (stub)

    def run(self):
        """Run the agent and listen for events."""
        subscribe("tests_passed", self.on_tests_passed)
        subscribe("release_approved", self.on_release_approved)
        subscribe("deployment_failed", self.on_deployment_failed)

        logger.info("ReleaseManagerAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="Release Manager Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "create-release", "approve-release", "deploy-release",
                               "rollback-release", "show-release-history", "show-rollback-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run"])
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
        result = agent.deploy_release(args.version)
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
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()

if __name__ == "__main__":
    main()
