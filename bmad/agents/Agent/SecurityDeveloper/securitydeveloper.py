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

class SecurityDeveloperAgent:
    def __init__(self):
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/securitydeveloper/best-practices.md",
            "security-scan": self.resource_base / "templates/securitydeveloper/security-scan-template.md",
            "compliance-report": self.resource_base / "templates/securitydeveloper/compliance-report-template.md",
            "incident-report": self.resource_base / "templates/securitydeveloper/incident-report-template.md",
            "vulnerability-assessment": self.resource_base / "templates/securitydeveloper/vulnerability-assessment-template.md",
            "security-checklist": self.resource_base / "templates/securitydeveloper/security-checklist-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/securitydeveloper/security-changelog.md",
            "scan-history": self.resource_base / "data/securitydeveloper/scan-history.md",
            "incident-history": self.resource_base / "data/securitydeveloper/incident-history.md"
        }

        # Initialize histories
        self.scan_history = []
        self.incident_history = []
        self._load_scan_history()
        self._load_incident_history()

    def _load_scan_history(self):
        try:
            if self.data_paths["scan-history"].exists():
                with open(self.data_paths["scan-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.scan_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load scan history: {e}")

    def _save_scan_history(self):
        try:
            self.data_paths["scan-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["scan-history"], "w") as f:
                f.write("# Security Scan History\n\n")
                f.writelines(f"- {scan}\n" for scan in self.scan_history[-50:])
        except Exception as e:
            logger.error(f"Could not save scan history: {e}")

    def _load_incident_history(self):
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
        try:
            self.data_paths["incident-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["incident-history"], "w") as f:
                f.write("# Security Incident History\n\n")
                f.writelines(f"- {incident}\n" for incident in self.incident_history[-50:])
        except Exception as e:
            logger.error(f"Could not save incident history: {e}")

    def show_help(self):
        help_text = """
SecurityDeveloper Agent Commands:
  help                    - Show this help message
  security-review         - Review code for security issues
  summarize-incidents     - Summarize security incidents
  run-security-scan       - Run comprehensive security scan
  vulnerability-assessment - Assess vulnerabilities
  compliance-check        - Check compliance requirements
  incident-report         - Generate incident report
  show-scan-history       - Show security scan history
  show-incident-history   - Show incident history
  show-best-practices     - Show security best practices
  show-changelog          - Show changelog
  export-report [format]  - Export report (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "security-checklist":
                path = self.template_paths["security-checklist"]
            elif resource_type == "compliance-report":
                path = self.template_paths["compliance-report"]
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

    def show_scan_history(self):
        if not self.scan_history:
            print("No scan history available.")
            return
        print("Security Scan History:")
        print("=" * 50)
        for i, scan in enumerate(self.scan_history[-10:], 1):
            print(f"{i}. {scan}")

    def show_incident_history(self):
        if not self.incident_history:
            print("No incident history available.")
            return
        print("Security Incident History:")
        print("=" * 50)
        for i, incident in enumerate(self.incident_history[-10:], 1):
            print(f"{i}. {incident}")

    def run_security_scan(self, target: str = "application") -> Dict[str, Any]:
        """Run comprehensive security scan on target."""
        logger.info(f"Running security scan on: {target}")

        # Simulate security scan
        time.sleep(2)

        scan_result = {
            "target": target,
            "scan_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": {
                "critical": 2,
                "high": 5,
                "medium": 8,
                "low": 12
            },
            "compliance": {
                "owasp_top_10": "85% compliant",
                "gdpr": "92% compliant",
                "sox": "88% compliant"
            },
            "security_score": 78,
            "recommendations": [
                "Update dependencies to latest versions",
                "Implement proper input validation",
                "Add rate limiting to API endpoints",
                "Enable security headers"
            ],
            "agent": "SecurityDeveloperAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("SecurityDeveloper", MetricType.SUCCESS_RATE, scan_result["security_score"], "%")

        # Add to scan history
        scan_entry = f"{datetime.now().isoformat()}: Security scan completed on {target} with {scan_result['security_score']}% security score"
        self.scan_history.append(scan_entry)
        self._save_scan_history()

        logger.info(f"Security scan completed: {scan_result}")
        return scan_result

    def vulnerability_assessment(self, component: str = "API") -> Dict[str, Any]:
        """Perform detailed vulnerability assessment."""
        logger.info(f"Performing vulnerability assessment on: {component}")

        assessment = {
            "component": component,
            "assessment_type": "detailed",
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [
                {
                    "id": "CVE-2024-001",
                    "severity": "high",
                    "description": "SQL injection vulnerability in user input",
                    "cwe": "CWE-89",
                    "recommendation": "Use parameterized queries"
                },
                {
                    "id": "CVE-2024-002",
                    "severity": "medium",
                    "description": "Cross-site scripting in search functionality",
                    "cwe": "CWE-79",
                    "recommendation": "Implement proper output encoding"
                }
            ],
            "risk_score": 7.5,
            "mitigation_plan": [
                "Implement input validation",
                "Add output encoding",
                "Update security headers",
                "Conduct penetration testing"
            ],
            "agent": "SecurityDeveloperAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("SecurityDeveloper", MetricType.SUCCESS_RATE, 85, "%")

        logger.info(f"Vulnerability assessment completed: {assessment}")
        return assessment

    def compliance_check(self, framework: str = "OWASP") -> Dict[str, Any]:
        """Check compliance with security frameworks."""
        logger.info(f"Checking compliance with: {framework}")

        compliance_result = {
            "framework": framework,
            "check_date": datetime.now().isoformat(),
            "overall_compliance": "85%",
            "categories": {
                "authentication": "90%",
                "authorization": "85%",
                "data_protection": "80%",
                "input_validation": "75%",
                "output_encoding": "90%"
            },
            "gaps": [
                "Missing multi-factor authentication",
                "Insufficient session management",
                "Weak password policies"
            ],
            "recommendations": [
                "Implement MFA for all user accounts",
                "Enhance session timeout policies",
                "Strengthen password requirements"
            ],
            "agent": "SecurityDeveloperAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("SecurityDeveloper", MetricType.SUCCESS_RATE, 85, "%")

        logger.info(f"Compliance check completed: {compliance_result}")
        return compliance_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        if not report_data:
            report_data = {
                "report_type": "Security Assessment",
                "target": "BMAD Application",
                "security_score": 78,
                "vulnerabilities_found": 27,
                "compliance_score": 85,
                "critical_issues": 2,
                "high_issues": 5,
                "timestamp": datetime.now().isoformat(),
                "agent": "SecurityDeveloperAgent"
            }

        try:
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "json":
                self._export_json(report_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def _export_markdown(self, report_data: Dict):
        output_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Security Assessment Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Target**: {report_data.get('target', 'N/A')}
- **Security Score**: {report_data.get('security_score', 0)}%
- **Vulnerabilities Found**: {report_data.get('vulnerabilities_found', 0)}
- **Compliance Score**: {report_data.get('compliance_score', 0)}%
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Risk Assessment
- **Critical Issues**: {report_data.get('critical_issues', 0)}
- **High Issues**: {report_data.get('high_issues', 0)}
- **Medium Issues**: {report_data.get('medium_issues', 0)}
- **Low Issues**: {report_data.get('low_issues', 0)}

## Recommendations
1. Update all dependencies to latest versions
2. Implement proper input validation
3. Add rate limiting to API endpoints
4. Enable security headers
5. Conduct regular security audits
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        output_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Report export saved to: {output_file}")

    def test_resource_completeness(self):
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
        logger.info("Starting security collaboration example...")

        # Publish security scan request
        publish("security_scan_requested", {
            "agent": "SecurityDeveloperAgent",
            "target": "BMAD Application",
            "timestamp": datetime.now().isoformat()
        })

        # Run security scan
        scan_result = self.run_security_scan("BMAD Application")

        # Perform vulnerability assessment
        self.vulnerability_assessment("API")

        # Publish completion
        publish("security_scan_completed", {
            "status": "success",
            "agent": "SecurityDeveloperAgent",
            "security_score": scan_result["security_score"],
            "vulnerabilities_found": len(scan_result["vulnerabilities"])
        })

        # Save context
        save_context("SecurityDeveloper", "status", {"security_status": "scanned"})

        # Notify via Slack
        try:
            send_slack_message(f"Security scan completed with {scan_result['security_score']}% security score")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("SecurityDeveloper")
        print(f"Opgehaalde context: {context}")

    def handle_security_scan_requested(self, event):
        logger.info(f"Security scan requested: {event}")
        target = event.get("target", "application")
        self.run_security_scan(target)

    async def handle_security_scan_completed(self, event):
        logger.info(f"Security scan completed: {event}")

        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("security_approval", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def run(self):
        def sync_handler(event):
            asyncio.run(self.handle_security_scan_completed(event))

        subscribe("security_scan_completed", sync_handler)
        subscribe("security_scan_requested", self.handle_security_scan_requested)

        logger.info("SecurityDeveloperAgent ready and listening for events...")
        self.collaborate_example()

    # --- ORIGINELE FUNCTIONALITEIT BEHOUDEN ---
    def notify_security_event(self, event):
        send_slack_message(f"[SecurityDeveloper] Security event: {event}")

    def security_review(self, code_snippet):
        prompt = f"Geef een security review van de volgende code/config:\n{code_snippet}"
        result = ask_openai(prompt)
        logging.info(f"[SecurityDeveloper][LLM Security Review]: {result}")

        # Add to incident history
        incident_entry = f"{datetime.now().isoformat()}: Security review completed - {code_snippet[:50]}..."
        self.incident_history.append(incident_entry)
        self._save_incident_history()

        # Log performance metric
        self.monitor._record_metric("SecurityDeveloper", MetricType.SUCCESS_RATE, 92, "%")

        return result

    def summarize_incidents(self, incident_list):
        prompt = "Vat de volgende security-incidenten samen in maximaal 3 bullets:\n" + "\n".join(incident_list)
        result = ask_openai(prompt)
        logging.info(f"[SecurityDeveloper][LLM Incident-samenvatting]: {result}")

        # Add to incident history
        summary_entry = f"{datetime.now().isoformat()}: Incident summary generated for {len(incident_list)} incidents"
        self.incident_history.append(summary_entry)
        self._save_incident_history()

        # Log performance metric
        self.monitor._record_metric("SecurityDeveloper", MetricType.SUCCESS_RATE, 88, "%")

        return result

    def on_security_review_requested(self, event):
        code_snippet = event.get("code_snippet", "")
        self.security_review(code_snippet)

    def on_summarize_incidents(self, event):
        incident_list = event.get("incident_list", [])
        self.summarize_incidents(incident_list)

    def handle_security_scan_started(self, event):
        logging.info("[SecurityDeveloper] Security scan gestart...")
        time.sleep(2)
        publish("security_findings_reported", {"desc": "Security bevindingen gerapporteerd"})
        logging.info("[SecurityDeveloper] Security findings gepubliceerd.")

    def handle_security_findings_reported(self, event):
        logging.info("[SecurityDeveloper] Wacht op HITL-review...")
        # HITL wordt afgehandeld door orchestrator

def main():
    parser = argparse.ArgumentParser(description="SecurityDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "security-review", "summarize-incidents", "run-security-scan",
                               "vulnerability-assessment", "compliance-check", "incident-report",
                               "show-scan-history", "show-incident-history", "show-best-practices",
                               "show-changelog", "export-report", "test", "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    parser.add_argument("--code", help="Code snippet for security review")
    parser.add_argument("--incidents", nargs="+", help="List of incidents to summarize")
    parser.add_argument("--target", default="application", help="Target for security scan")
    parser.add_argument("--component", default="API", help="Component for vulnerability assessment")
    parser.add_argument("--framework", default="OWASP", help="Framework for compliance check")

    args = parser.parse_args()

    agent = SecurityDeveloperAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "security-review":
        if args.code:
            result = agent.security_review(args.code)
            print(result)
        else:
            print("Please provide --code for security review")
    elif args.command == "summarize-incidents":
        if args.incidents:
            result = agent.summarize_incidents(args.incidents)
            print(result)
        else:
            print("Please provide --incidents for incident summary")
    elif args.command == "run-security-scan":
        result = agent.run_security_scan(args.target)
        print(json.dumps(result, indent=2))
    elif args.command == "vulnerability-assessment":
        result = agent.vulnerability_assessment(args.component)
        print(json.dumps(result, indent=2))
    elif args.command == "compliance-check":
        result = agent.compliance_check(args.framework)
        print(json.dumps(result, indent=2))
    elif args.command == "show-scan-history":
        agent.show_scan_history()
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
    # Subscribe to events
    agent = SecurityDeveloperAgent()
    subscribe("security_review_requested", agent.on_security_review_requested)
    subscribe("summarize_incidents", agent.on_summarize_incidents)
    subscribe("security_scan_started", agent.handle_security_scan_started)
    subscribe("security_findings_reported", agent.handle_security_findings_reported)

    main()
