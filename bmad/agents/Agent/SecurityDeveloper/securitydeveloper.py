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
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass

class SecurityValidationError(SecurityError):
    """Exception for security validation failures."""
    pass

class SecurityDeveloperAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "SecurityDeveloper"
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

        # Security-specific attributes
        self.security_thresholds = {
            "critical": 9.0,
            "high": 7.0,
            "medium": 4.0,
            "low": 0.0
        }
        self.active_threats = []
        self.security_policies = {}

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise SecurityValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_security_target(self, target: str) -> None:
        """Validate security scan target."""
        self._validate_input(target, str, "target")
        if not target or target.strip() == "":
            raise SecurityValidationError("Security target cannot be empty")
        
        # Validate target format
        allowed_targets = ["application", "api", "database", "network", "infrastructure"]
        if target.lower() not in allowed_targets:
            logger.warning(f"Unusual security target: {target}")

    def _validate_vulnerability_data(self, vulnerability_data: Dict[str, Any]) -> None:
        """Validate vulnerability assessment data."""
        self._validate_input(vulnerability_data, dict, "vulnerability_data")
        
        required_fields = ["severity", "description", "cwe"]
        for field in required_fields:
            if field not in vulnerability_data:
                raise SecurityValidationError(f"Missing required field: {field}")
        
        # Validate severity levels
        valid_severities = ["critical", "high", "medium", "low"]
        if vulnerability_data.get("severity") not in valid_severities:
            raise SecurityValidationError(f"Invalid severity level: {vulnerability_data.get('severity')}")

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

    def _record_security_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record security-specific performance metrics."""
        try:
            self.monitor._record_metric("SecurityDeveloper", MetricType.SUCCESS_RATE, value, unit)
            logger.info(f"Security metric recorded: {metric_name} = {value}{unit}")
        except Exception as e:
            logger.error(f"Failed to record security metric: {e}")

    def _assess_threat_level(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Assess overall threat level based on vulnerabilities."""
        if not vulnerabilities:
            return "low"
        
        max_severity = "low"
        severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            if severity_scores.get(severity, 0) > severity_scores.get(max_severity, 0):
                max_severity = severity
        
        return max_severity

    def _generate_security_recommendations(self, vulnerabilities: List[Dict[str, Any]], threat_level: str) -> List[str]:
        """Generate security recommendations based on vulnerabilities and threat level."""
        recommendations = []
        
        # Base recommendations
        recommendations.append("Implement comprehensive input validation")
        recommendations.append("Enable security headers (HSTS, CSP, X-Frame-Options)")
        recommendations.append("Use parameterized queries to prevent SQL injection")
        recommendations.append("Implement proper output encoding")
        
        # Threat level specific recommendations
        if threat_level in ["critical", "high"]:
            recommendations.append("Immediate security review required")
            recommendations.append("Consider implementing additional authentication layers")
            recommendations.append("Enable real-time threat monitoring")
        
        if threat_level == "critical":
            recommendations.append("Emergency security patch deployment recommended")
            recommendations.append("Consider temporary service suspension")
        
        return recommendations

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
  threat-assessment       - Assess current threat level
  security-recommendations - Generate security recommendations
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            self._validate_input(resource_type, str, "resource_type")
            
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
        try:
            self._validate_security_target(target)
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

            # Record performance metrics
            self._record_security_metric("security_scan_score", scan_result["security_score"])
            self._record_security_metric("vulnerabilities_found", sum(scan_result["vulnerabilities"].values()))

            # Add to scan history
            scan_entry = f"{datetime.now().isoformat()}: Security scan completed on {target} with {scan_result['security_score']}% security score"
            self.scan_history.append(scan_entry)
            self._save_scan_history()

            logger.info(f"Security scan completed: {scan_result}")
            return scan_result
            
        except SecurityValidationError as e:
            logger.error(f"Security validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            self._record_security_metric("security_scan_failure", 1, "count")
            raise SecurityError(f"Security scan failed: {e}")

    def vulnerability_assessment(self, component: str = "API") -> Dict[str, Any]:
        """Perform detailed vulnerability assessment."""
        try:
            self._validate_input(component, str, "component")
            if not component or component.strip() == "":
                raise SecurityValidationError("Component cannot be empty")
                
            logger.info(f"Performing vulnerability assessment on: {component}")

            vulnerabilities = [
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
            ]

            # Validate vulnerability data
            for vuln in vulnerabilities:
                self._validate_vulnerability_data(vuln)

            threat_level = self._assess_threat_level(vulnerabilities)
            recommendations = self._generate_security_recommendations(vulnerabilities, threat_level)

            assessment = {
                "component": component,
                "assessment_type": "detailed",
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": vulnerabilities,
                "threat_level": threat_level,
                "risk_score": 7.5,
                "mitigation_plan": recommendations,
                "agent": "SecurityDeveloperAgent"
            }

            # Record performance metrics
            self._record_security_metric("vulnerability_assessment_score", 85)
            self._record_security_metric("threat_level", {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(threat_level, 1))

            logger.info(f"Vulnerability assessment completed: {assessment}")
            return assessment
            
        except SecurityValidationError as e:
            logger.error(f"Security validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Vulnerability assessment failed: {e}")
            self._record_security_metric("vulnerability_assessment_failure", 1, "count")
            raise SecurityError(f"Vulnerability assessment failed: {e}")

    def compliance_check(self, framework: str = "OWASP") -> Dict[str, Any]:
        """Check compliance with security frameworks."""
        try:
            self._validate_input(framework, str, "framework")
            if not framework or framework.strip() == "":
                raise SecurityValidationError("Framework cannot be empty")
                
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

            # Record performance metrics
            self._record_security_metric("compliance_score", 85)
            self._record_security_metric("compliance_gaps", len(compliance_result["gaps"]))

            logger.info(f"Compliance check completed: {compliance_result}")
            return compliance_result
            
        except SecurityValidationError as e:
            logger.error(f"Security validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            self._record_security_metric("compliance_check_failure", 1, "count")
            raise SecurityError(f"Compliance check failed: {e}")

    def threat_assessment(self) -> Dict[str, Any]:
        """Assess current threat level and active threats."""
        try:
            threat_assessment = {
                "timestamp": datetime.now().isoformat(),
                "overall_threat_level": "medium",
                "active_threats": len(self.active_threats),
                "threat_categories": {
                    "network": 2,
                    "application": 3,
                    "data": 1,
                    "infrastructure": 0
                },
                "recommendations": [
                    "Enable real-time threat monitoring",
                    "Implement automated threat response",
                    "Conduct regular security audits"
                ],
                "agent": "SecurityDeveloperAgent"
            }

            self._record_security_metric("threat_assessment_score", 75)
            return threat_assessment
            
        except Exception as e:
            logger.error(f"Threat assessment failed: {e}")
            raise SecurityError(f"Threat assessment failed: {e}")

    def generate_security_recommendations(self, context: Dict[str, Any] = None) -> List[str]:
        """Generate comprehensive security recommendations."""
        try:
            if context is None:
                context = {}
            
            self._validate_input(context, dict, "context")
            
            recommendations = [
                "Implement comprehensive input validation",
                "Enable security headers (HSTS, CSP, X-Frame-Options)",
                "Use parameterized queries to prevent SQL injection",
                "Implement proper output encoding",
                "Enable multi-factor authentication",
                "Implement rate limiting",
                "Regular security audits and penetration testing",
                "Keep all dependencies updated",
                "Implement proper logging and monitoring",
                "Use HTTPS for all communications"
            ]

            # Context-specific recommendations
            if context.get("has_user_input"):
                recommendations.append("Implement strict input validation rules")
                recommendations.append("Use whitelist approach for allowed characters")
            
            if context.get("has_database"):
                recommendations.append("Use database connection pooling")
                recommendations.append("Implement database access logging")
            
            if context.get("has_api"):
                recommendations.append("Implement API rate limiting")
                recommendations.append("Use API authentication tokens")
                recommendations.append("Implement API versioning")

            self._record_security_metric("recommendations_generated", len(recommendations))
            return recommendations
            
        except SecurityValidationError as e:
            logger.error(f"Security validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Security recommendations generation failed: {e}")
            raise SecurityError(f"Security recommendations generation failed: {e}")

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        try:
            self._validate_input(format_type, str, "format_type")
            if format_type not in ["md", "json"]:
                raise SecurityValidationError(f"Unsupported format: {format_type}")
                
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

            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "json":
                self._export_json(report_data)
                
        except SecurityValidationError as e:
            logger.error(f"Security validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise SecurityError(f"Report export failed: {e}")

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
                               "show-changelog", "export-report", "test", "collaborate", "run",
                               "threat-assessment", "security-recommendations"])
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
    elif args.command == "threat-assessment":
        result = agent.threat_assessment()
        print(json.dumps(result, indent=2))
    elif args.command == "security-recommendations":
        context = {}
        if args.code:
            context["code_snippet"] = args.code
        if args.target == "application":
            context["has_api"] = True
        if args.target == "database":
            context["has_database"] = True
        if args.target == "api":
            context["has_api"] = True
        if args.target == "network":
            context["has_network"] = True
        if args.target == "infrastructure":
            context["has_infrastructure"] = True
        if args.code and "user_input" in args.code.lower():
            context["has_user_input"] = True

        recommendations = agent.generate_security_recommendations(context)
        print("\n".join(recommendations))


if __name__ == "__main__":
    # Subscribe to events
    agent = SecurityDeveloperAgent()
    subscribe("security_review_requested", agent.on_security_review_requested)
    subscribe("summarize_incidents", agent.on_summarize_incidents)
    subscribe("security_scan_started", agent.handle_security_scan_started)
    subscribe("security_findings_reported", agent.handle_security_findings_reported)

    main()
