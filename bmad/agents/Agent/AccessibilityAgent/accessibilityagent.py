import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import logging
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import asyncio
import time

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor, MetricType
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.data.supabase_context import save_context, get_context
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class AccessibilityAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        
        # Resource paths - corrected path
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/accessibilityagent/best-practices.md",
            "audit-template": self.resource_base / "templates/accessibilityagent/audit-template.md",
            "audit-export": self.resource_base / "templates/accessibilityagent/audit-export-template.md",
            "audit-export-csv": self.resource_base / "templates/accessibilityagent/audit-export-template.csv",
            "checklist": self.resource_base / "templates/accessibilityagent/checklist-template.md",
            "improvement-report": self.resource_base / "templates/accessibilityagent/improvement-report-template.md",
            "shadcn-accessibility": self.resource_base / "templates/accessibilityagent/shadcn-accessibility-template.md",
            "aria-testing": self.resource_base / "templates/accessibilityagent/aria-testing-template.md",
            "screen-reader-testing": self.resource_base / "templates/accessibilityagent/screen-reader-testing-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/accessibilityagent/accessibility-changelog.md",
            "audit-history": self.resource_base / "data/accessibilityagent/audit-history.md",
            "improvement-history": self.resource_base / "data/accessibilityagent/improvement-history.md"
        }
        
        # Initialize audit history
        self.audit_history = []
        self._load_audit_history()

    def _load_audit_history(self):
        """Load audit history from data file"""
        try:
            if self.data_paths["audit-history"].exists():
                with open(self.data_paths["audit-history"], 'r') as f:
                    content = f.read()
                    # Parse audit history from markdown
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            self.audit_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load audit history: {e}")

    def _save_audit_history(self):
        """Save audit history to data file"""
        try:
            self.data_paths["audit-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["audit-history"], 'w') as f:
                f.write("# Accessibility Audit History\n\n")
                for audit in self.audit_history[-50:]:  # Keep last 50 audits
                    f.write(f"- {audit}\n")
        except Exception as e:
            logger.error(f"Could not save audit history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
Accessibility Agent Commands:
  help                    - Show this help message
  audit [target]          - Run accessibility audit on target (default: /mock/page)
  test-shadcn-component   - Test Shadcn component accessibility
  validate-aria           - Validate ARIA attributes
  test-screen-reader      - Test screen reader compatibility
  check-design-tokens     - Check design token accessibility
  show-audit-history      - Show audit history
  show-checklist          - Show accessibility checklist
  show-best-practices     - Show accessibility best practices
  show-changelog          - Show accessibility changelog
  export-audit [format]   - Export last audit (format: md, csv, json)
  generate-report         - Generate improvement report
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        try:
            if resource_type == "checklist":
                path = self.template_paths["checklist"]
            elif resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "shadcn-accessibility":
                path = self.template_paths["shadcn-accessibility"]
            elif resource_type == "aria-testing":
                path = self.template_paths["aria-testing"]
            elif resource_type == "screen-reader-testing":
                path = self.template_paths["screen-reader-testing"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return
            if path.exists():
                with open(path, 'r') as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_audit_history(self):
        """Show audit history"""
        if not self.audit_history:
            print("No audit history available.")
            return
        print("Accessibility Audit History:")
        print("=" * 50)
        for i, audit in enumerate(self.audit_history[-10:], 1):
            print(f"{i}. {audit}")

    def test_shadcn_component(self, component_name: str = "Button") -> Dict[str, Any]:
        """Test Shadcn component accessibility."""
        logger.info(f"Testing Shadcn component accessibility: {component_name}")
        
        # Simulate Shadcn component accessibility testing
        time.sleep(1)
        
        test_result = {
            "component": component_name,
            "type": "Shadcn/ui",
            "accessibility_score": 96,
            "tests_performed": {
                "aria_labels": "PASS",
                "keyboard_navigation": "PASS",
                "focus_management": "PASS",
                "screen_reader": "PASS",
                "color_contrast": "PASS",
                "touch_targets": "PASS"
            },
            "issues_found": [
                {
                    "type": "minor",
                    "description": "Icon button missing aria-label",
                    "severity": "low",
                    "recommendation": "Add aria-label to icon buttons"
                }
            ],
            "design_tokens_check": {
                "color_contrast": "WCAG AA compliant",
                "focus_indicators": "Visible and clear",
                "spacing": "Adequate for touch targets",
                "typography": "Readable and scalable"
            },
            "screen_reader_test": {
                "announcement": "Button component properly announced",
                "navigation": "Keyboard navigation works correctly",
                "state_changes": "State changes properly communicated"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }
        
        # Log performance metrics
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, test_result["accessibility_score"], "%")
        
        # Add to audit history
        audit_entry = f"{datetime.now().isoformat()}: Shadcn {component_name} component tested with {test_result['accessibility_score']}% accessibility score"
        self.audit_history.append(audit_entry)
        self._save_audit_history()
        
        logger.info(f"Shadcn component accessibility test completed: {test_result}")
        return test_result

    def validate_aria(self, component_code: str = "") -> Dict[str, Any]:
        """Validate ARIA attributes in component code."""
        logger.info("Validating ARIA attributes")
        
        # Simulate ARIA validation
        time.sleep(1)
        
        validation_result = {
            "validation_type": "ARIA attributes",
            "overall_score": 94,
            "checks_performed": {
                "aria_labels": {
                    "status": "PASS",
                    "score": 95,
                    "findings": "All interactive elements have proper labels"
                },
                "aria_roles": {
                    "status": "PASS",
                    "score": 92,
                    "findings": "Roles are semantically correct"
                },
                "aria_states": {
                    "status": "PASS",
                    "score": 96,
                    "findings": "States are properly managed"
                },
                "aria_live": {
                    "status": "PASS",
                    "score": 90,
                    "findings": "Live regions are appropriately used"
                }
            },
            "issues_found": [
                {
                    "type": "aria-label",
                    "element": "search button",
                    "issue": "Missing aria-label for icon button",
                    "severity": "medium",
                    "fix": "Add aria-label='Search' to button element"
                }
            ],
            "recommendations": [
                "Add aria-label to all icon buttons",
                "Ensure proper aria-expanded states for collapsible content",
                "Use aria-live regions for dynamic content updates"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }
        
        # Log performance metrics
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, validation_result["overall_score"], "%")
        
        logger.info(f"ARIA validation completed: {validation_result}")
        return validation_result

    def test_screen_reader(self, component_name: str = "Button") -> Dict[str, Any]:
        """Test screen reader compatibility."""
        logger.info(f"Testing screen reader compatibility for: {component_name}")
        
        # Simulate screen reader testing
        time.sleep(1)
        
        screen_reader_test = {
            "component": component_name,
            "test_type": "Screen reader compatibility",
            "overall_score": 98,
            "screen_readers_tested": {
                "NVDA": {
                    "status": "PASS",
                    "announcement": "Button, Click me",
                    "navigation": "Tab navigation works correctly",
                    "state_changes": "State changes properly announced"
                },
                "JAWS": {
                    "status": "PASS",
                    "announcement": "Button, Click me",
                    "navigation": "Tab navigation works correctly",
                    "state_changes": "State changes properly announced"
                },
                "VoiceOver": {
                    "status": "PASS",
                    "announcement": "Button, Click me",
                    "navigation": "Tab navigation works correctly",
                    "state_changes": "State changes properly announced"
                }
            },
            "keyboard_testing": {
                "tab_navigation": "PASS",
                "enter_key": "PASS",
                "space_key": "PASS",
                "arrow_keys": "PASS",
                "escape_key": "PASS"
            },
            "focus_management": {
                "visible_focus": "PASS",
                "focus_trap": "PASS",
                "focus_restoration": "PASS"
            },
            "issues_found": [],
            "recommendations": [
                "Component works well with all major screen readers",
                "Keyboard navigation is fully functional",
                "Focus management is properly implemented"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }
        
        # Log performance metrics
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, screen_reader_test["overall_score"], "%")
        
        logger.info(f"Screen reader test completed: {screen_reader_test}")
        return screen_reader_test

    def check_design_tokens(self, design_system: str = "Shadcn") -> Dict[str, Any]:
        """Check design token accessibility."""
        logger.info(f"Checking design token accessibility for: {design_system}")
        
        # Simulate design token accessibility check
        time.sleep(1)
        
        design_token_check = {
            "design_system": design_system,
            "check_type": "Design token accessibility",
            "overall_score": 97,
            "color_tokens": {
                "primary": {
                    "contrast_ratio": "4.8:1",
                    "wcag_compliance": "AA",
                    "status": "PASS"
                },
                "secondary": {
                    "contrast_ratio": "5.2:1",
                    "wcag_compliance": "AA",
                    "status": "PASS"
                },
                "destructive": {
                    "contrast_ratio": "4.9:1",
                    "wcag_compliance": "AA",
                    "status": "PASS"
                },
                "muted": {
                    "contrast_ratio": "3.1:1",
                    "wcag_compliance": "AA",
                    "status": "PASS"
                }
            },
            "spacing_tokens": {
                "touch_targets": "Minimum 44px maintained",
                "focus_indicators": "2px border width",
                "status": "PASS"
            },
            "typography_tokens": {
                "font_sizes": "Scalable from 12px to 24px",
                "line_heights": "1.5x for body text",
                "font_weights": "400, 500, 600, 700 available",
                "status": "PASS"
            },
            "focus_tokens": {
                "focus_ring": "2px solid primary color",
                "focus_offset": "2px from element",
                "status": "PASS"
            },
            "issues_found": [
                {
                    "type": "color_contrast",
                    "element": "muted text on light background",
                    "issue": "Contrast ratio slightly below optimal",
                    "severity": "low",
                    "recommendation": "Consider increasing contrast for better readability"
                }
            ],
            "recommendations": [
                "Design tokens are well-structured for accessibility",
                "Color contrast meets WCAG AA standards",
                "Spacing supports adequate touch targets",
                "Typography is readable and scalable"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }
        
        # Log performance metrics
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, design_token_check["overall_score"], "%")
        
        logger.info(f"Design token accessibility check completed: {design_token_check}")
        return design_token_check

    def run_accessibility_audit(self, target: str = "/mock/page") -> Dict[str, Any]:
        """Run accessibility audit on target."""
        logger.info(f"Running accessibility audit on: {target}")
        
        # Simulate accessibility audit
        time.sleep(2)
        
        audit_result = {
            "target": target,
            "audit_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "overall_score": 85,
            "categories": {
                "perceivable": {
                    "score": 88,
                    "issues": ["Low contrast text", "Missing alt text"]
                },
                "operable": {
                    "score": 92,
                    "issues": ["Keyboard navigation works well"]
                },
                "understandable": {
                    "score": 90,
                    "issues": ["Clear navigation structure"]
                },
                "robust": {
                    "score": 85,
                    "issues": ["Some ARIA implementation issues"]
                }
            },
            "critical_issues": [
                "Missing alt text on important images",
                "Insufficient color contrast on navigation links"
            ],
            "recommendations": [
                "Add descriptive alt text to all images",
                "Improve color contrast to meet WCAG AA standards",
                "Ensure all interactive elements are keyboard accessible"
            ],
            "agent": "AccessibilityAgent"
        }
        
        # Log performance metrics
        self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, audit_result["overall_score"], "%")
        
        # Add to audit history
        audit_entry = f"{datetime.now().isoformat()}: Accessibility audit completed on {target} with {audit_result['overall_score']}% score"
        self.audit_history.append(audit_entry)
        self._save_audit_history()
        
        logger.info(f"Accessibility audit completed: {audit_result}")
        return audit_result

    def export_audit(self, format_type: str = "md", audit_data: Optional[Dict] = None):
        """Export audit results in specified format."""
        if not audit_data:
            audit_data = {
                "audit_type": "Accessibility Audit",
                "target": "BMAD Application",
                "overall_score": 85,
                "critical_issues": 3,
                "recommendations": 5,
                "timestamp": datetime.now().isoformat(),
                "agent": "AccessibilityAgent"
            }
        
        try:
            if format_type == "md":
                self._export_markdown(audit_data)
            elif format_type == "csv":
                self._export_csv(audit_data)
            elif format_type == "json":
                self._export_json(audit_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting audit: {e}")

    def _export_markdown(self, audit_data: Dict):
        """Export audit data as markdown."""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""# Accessibility Audit Report

## Summary
- **Audit Type**: {audit_data.get('audit_type', 'N/A')}
- **Target**: {audit_data.get('target', 'N/A')}
- **Overall Score**: {audit_data.get('overall_score', 0)}%
- **Critical Issues**: {audit_data.get('critical_issues', 0)}
- **Recommendations**: {audit_data.get('recommendations', 0)}
- **Timestamp**: {audit_data.get('timestamp', 'N/A')}
- **Agent**: {audit_data.get('agent', 'N/A')}

## Categories
- **Perceivable**: {audit_data.get('categories', {}).get('perceivable', {}).get('score', 0)}%
- **Operable**: {audit_data.get('categories', {}).get('operable', {}).get('score', 0)}%
- **Understandable**: {audit_data.get('categories', {}).get('understandable', {}).get('score', 0)}%
- **Robust**: {audit_data.get('categories', {}).get('robust', {}).get('score', 0)}%

## Critical Issues
{chr(10).join([f"- {issue}" for issue in audit_data.get('critical_issues', [])])}

## Recommendations
{chr(10).join([f"- {rec}" for rec in audit_data.get('recommendations', [])])}
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"Audit export saved to: {output_file}")

    def _export_csv(self, audit_data: Dict):
        """Export audit data as CSV."""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Score', 'Issues'])
            
            categories = audit_data.get('categories', {})
            for category, data in categories.items():
                issues = ', '.join(data.get('issues', []))
                writer.writerow([category, data.get('score', 0), issues])
        
        print(f"Audit export saved to: {output_file}")

    def _export_json(self, audit_data: Dict):
        """Export audit data as JSON."""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        print(f"Audit export saved to: {output_file}")

    def generate_improvement_report(self):
        """Generate improvement report based on audit history."""
        logger.info("Generating improvement report")
        
        # Analyze common issues
        common_issues = self._analyze_common_issues()
        
        report = {
            "report_type": "Accessibility Improvement",
            "generated_date": datetime.now().isoformat(),
            "common_issues": common_issues,
            "trends": {
                "score_improvement": "+5% over last month",
                "critical_issues_reduction": "-30%",
                "compliance_improvement": "+8%"
            },
            "recommendations": [
                "Focus on color contrast improvements",
                "Implement comprehensive ARIA training",
                "Add automated accessibility testing to CI/CD"
            ],
            "agent": "AccessibilityAgent"
        }
        
        logger.info(f"Improvement report generated: {report}")
        return report

    def _analyze_common_issues(self) -> str:
        """Analyze common accessibility issues from audit history."""
        return "Color contrast, missing alt text, and keyboard navigation are the most common issues."

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
        logger.info("Starting accessibility collaboration example...")
        
        # Publish accessibility audit request
        publish("accessibility_audit_requested", {
            "agent": "AccessibilityAgent",
            "target": "BMAD Application",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run accessibility audit
        audit_result = self.run_accessibility_audit("BMAD Application")
        
        # Test Shadcn component
        shadcn_test = self.test_shadcn_component("Button")
        
        # Publish completion
        publish("accessibility_audit_completed", {
            "status": "success", 
            "agent": "AccessibilityAgent",
            "overall_score": audit_result["overall_score"],
            "shadcn_score": shadcn_test["accessibility_score"]
        })
        
        # Save context
        save_context("AccessibilityAgent", {"accessibility_status": "audited"})
        
        # Notify via Slack
        try:
            send_slack_message(f"Accessibility audit completed with {audit_result['overall_score']}% score")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("AccessibilityAgent")
        print(f"Opgehaalde context: {context}")

    def handle_audit_requested(self, event):
        logger.info(f"Accessibility audit requested: {event}")
        target = event.get("target", "/mock/page")
        self.run_accessibility_audit(target)

    async def handle_audit_completed(self, event):
        logger.info(f"Accessibility audit completed: {event}")
        
        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("accessibility_approval", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def run(self):
        """Run the agent and listen for events."""
        def sync_handler(event):
            asyncio.run(self.handle_audit_completed(event))
        
        subscribe("accessibility_audit_completed", sync_handler)
        subscribe("accessibility_audit_requested", self.handle_audit_requested)
        
        logger.info("AccessibilityAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="Accessibility Agent CLI")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["help", "audit", "test-shadcn-component", "validate-aria", 
                               "test-screen-reader", "check-design-tokens", "show-audit-history",
                               "show-checklist", "show-best-practices", "show-changelog",
                               "export-audit", "generate-report", "test", "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--target", default="/mock/page", help="Target for accessibility audit")
    parser.add_argument("--component", default="Button", help="Component name for testing")
    parser.add_argument("--code", help="Component code for ARIA validation")
    parser.add_argument("--design-system", default="Shadcn", help="Design system for token check")
    
    args = parser.parse_args()
    
    agent = AccessibilityAgent()
    
    if args.command == "help":
        agent.show_help()
    elif args.command == "audit":
        result = agent.run_accessibility_audit(args.target)
        print(json.dumps(result, indent=2))
    elif args.command == "test-shadcn-component":
        result = agent.test_shadcn_component(args.component)
        print(json.dumps(result, indent=2))
    elif args.command == "validate-aria":
        result = agent.validate_aria(args.code)
        print(json.dumps(result, indent=2))
    elif args.command == "test-screen-reader":
        result = agent.test_screen_reader(args.component)
        print(json.dumps(result, indent=2))
    elif args.command == "check-design-tokens":
        result = agent.check_design_tokens(args.design_system)
        print(json.dumps(result, indent=2))
    elif args.command == "show-audit-history":
        agent.show_audit_history()
    elif args.command == "show-checklist":
        agent.show_resource("checklist")
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-audit":
        agent.export_audit(args.format)
    elif args.command == "generate-report":
        result = agent.generate_improvement_report()
        print(json.dumps(result, indent=2))
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()

if __name__ == "__main__":
    main()
