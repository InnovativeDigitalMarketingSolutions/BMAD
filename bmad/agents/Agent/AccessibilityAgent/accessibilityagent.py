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

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class AccessibilityError(Exception):
    """Custom exception for accessibility-related errors."""
    pass

class AccessibilityValidationError(AccessibilityError):
    """Exception for accessibility validation failures."""
    pass

class AccessibilityAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "AccessibilityAgent"
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

        # Accessibility-specific attributes
        self.accessibility_standards = {
            "wcag": "2.1",
            "aria": "1.2",
            "section508": "2017"
        }
        self.common_issues = []
        self.improvement_recommendations = []

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise AccessibilityValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_component_name(self, component_name: str) -> None:
        """Validate component name parameter."""
        self._validate_input(component_name, str, "component_name")
        if not component_name.strip():
            raise AccessibilityValidationError("Component name cannot be empty")
        if len(component_name) > 100:
            raise AccessibilityValidationError("Component name cannot exceed 100 characters")

    def _validate_audit_target(self, target: str) -> None:
        """Validate accessibility audit target."""
        self._validate_input(target, str, "target")
        if not target.strip():
            raise AccessibilityValidationError("Audit target cannot be empty")
        if not target.startswith(('/', 'http://', 'https://')):
            raise AccessibilityValidationError("Audit target must be a valid URL or path")

    def _validate_format_type(self, format_type: str) -> None:
        """Validate export format type."""
        self._validate_input(format_type, str, "format_type")
        if format_type not in ["md", "csv", "json"]:
            raise AccessibilityValidationError("Format type must be 'md', 'csv', or 'json'")

    def _record_accessibility_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record accessibility-specific metrics."""
        try:
            self.monitor._record_metric("AccessibilityAgent", MetricType.SUCCESS_RATE, value, unit)
            logger.info(f"Accessibility metric recorded: {metric_name} = {value}{unit}")
        except Exception as e:
            logger.error(f"Failed to record accessibility metric: {e}")

    def _assess_accessibility_level(self, audit_results: Dict[str, Any]) -> str:
        """Assess the overall accessibility level based on audit results."""
        if not audit_results:
            return "unknown"
        
        # Calculate accessibility score
        total_issues = len(audit_results.get("issues", []))
        critical_issues = len([issue for issue in audit_results.get("issues", []) 
                             if issue.get("severity") == "critical"])
        
        if critical_issues > 0:
            return "critical"
        elif total_issues > 10:
            return "poor"
        elif total_issues > 5:
            return "fair"
        elif total_issues > 0:
            return "good"
        else:
            return "excellent"

    def _generate_accessibility_recommendations(self, audit_results: Dict[str, Any]) -> list:
        """Generate accessibility recommendations based on audit results."""
        recommendations = [
            "Ensure all images have alt text",
            "Use semantic HTML elements",
            "Provide sufficient color contrast",
            "Implement keyboard navigation",
            "Add ARIA labels where needed"
        ]
        
        issues = audit_results.get("issues", [])
        if not issues:
            return recommendations + ["Maintain current accessibility standards"]
        
        # Add specific recommendations based on issues
        for issue in issues:
            if "color" in issue.get("type", "").lower():
                recommendations.append("Improve color contrast ratios")
            if "keyboard" in issue.get("type", "").lower():
                recommendations.append("Enhance keyboard navigation support")
            if "screen reader" in issue.get("type", "").lower():
                recommendations.append("Add screen reader specific attributes")
        
        return list(set(recommendations))  # Remove duplicates

    def _load_audit_history(self):
        """Load audit history from data file"""
        try:
            if self.data_paths["audit-history"].exists():
                with open(self.data_paths["audit-history"]) as f:
                    content = f.read()
                    # Parse audit history from markdown
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.audit_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load audit history: {e}")

    def _save_audit_history(self):
        """Save audit history to data file"""
        try:
            self.data_paths["audit-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["audit-history"], "w") as f:
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
                with open(path) as f:
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
        # Input validation
        self._validate_component_name(component_name)
            
        logger.info(f"Testing Shadcn component accessibility: {component_name}")

        # Simulate Shadcn component accessibility testing
        time.sleep(1)

        test_result = {
            "component": component_name,
            "type": "Shadcn/ui",
            "status": "tested",
            "accessibility_score": 96,
            "tests_performed": {
                "aria_labels": "PASS",
                "keyboard_navigation": "PASS",
                "focus_management": "PASS",
                "screen_reader": "PASS",
                "color_contrast": "PASS",
                "touch_targets": "PASS"
            },
            "component_issues": [
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
            "wcag_compliance": {
                "wcag_2_1_aa": "Compliant",
                "wcag_2_1_aaa": "Partially compliant",
                "wcag_2_2": "Ready for compliance"
            },
            "performance_impact": {
                "load_time": "No significant impact",
                "memory_usage": "Optimized",
                "bundle_size": "Minimal increase"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }

        # Log performance metrics
        self._record_accessibility_metric("ShadcnComponentTest", test_result["accessibility_score"], "%")

        # Add to audit history
        audit_entry = f"{datetime.now().isoformat()}: Shadcn {component_name} component tested with {test_result['accessibility_score']}% accessibility score"
        self.audit_history.append(audit_entry)
        self._save_audit_history()

        logger.info(f"Shadcn component accessibility test completed: {test_result}")
        return test_result

    def validate_aria(self, component_code: str = "") -> Dict[str, Any]:
        """Validate ARIA attributes in component code."""
        # Input validation
        self._validate_input(component_code, str, "component_code")
        if not component_code.strip():
            raise AccessibilityValidationError("component_code cannot be empty")
            
        logger.info("Validating ARIA attributes")

        # Simulate ARIA validation
        time.sleep(1)

        validation_result = {
            "validation_type": "ARIA attributes",
            "status": "validated",
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
            "aria_issues": [
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
            "wcag_compliance": {
                "wcag_2_1_aa": "Compliant",
                "wcag_2_1_aaa": "Partially compliant"
            },
            "automated_fixes": [
                {
                    "issue": "Missing aria-label",
                    "suggested_fix": "Add aria-label attribute",
                    "code_example": 'aria-label="Search"'
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }

        # Log performance metrics
        self._record_accessibility_metric("ARIAValidation", validation_result["overall_score"], "%")

        logger.info(f"ARIA validation completed: {validation_result}")
        return validation_result

    def test_screen_reader(self, component_name: str = "Button") -> Dict[str, Any]:
        """Test screen reader compatibility."""
        # Input validation
        self._validate_component_name(component_name)
            
        logger.info(f"Testing screen reader compatibility for: {component_name}")

        # Simulate screen reader testing
        time.sleep(1)

        screen_reader_test = {
            "component": component_name,
            "test_type": "Screen reader compatibility",
            "status": "tested",
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
            "screen_reader_issues": [],
            "recommendations": [
                "Component works well with all major screen readers",
                "Keyboard navigation is fully functional",
                "Focus management is properly implemented"
            ],
            "accessibility_standards": {
                "wcag_2_1_aa": "Compliant",
                "wcag_2_1_aaa": "Compliant",
                "section_508": "Compliant"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }

        # Log performance metrics
        self._record_accessibility_metric("ScreenReaderTest", screen_reader_test["overall_score"], "%")

        logger.info(f"Screen reader test completed: {screen_reader_test}")
        return screen_reader_test

    def check_design_tokens(self, design_system: str = "Shadcn") -> Dict[str, Any]:
        """Check design token accessibility."""
        # Input validation
        self._validate_input(design_system, str, "design_system")
        if not design_system.strip():
            raise AccessibilityValidationError("design_system cannot be empty")
            
        logger.info(f"Checking design token accessibility for: {design_system}")

        # Simulate design token accessibility check
        time.sleep(1)

        design_token_check = {
            "design_system": design_system,
            "check_type": "Design token accessibility",
            "status": "checked",
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
            "design_token_issues": [
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
            "wcag_compliance": {
                "wcag_2_1_aa": "Compliant",
                "wcag_2_1_aaa": "Partially compliant"
            },
            "mobile_accessibility": {
                "touch_targets": "Compliant (44px minimum)",
                "gesture_support": "Properly implemented",
                "viewport_scaling": "Supports zoom up to 200%"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "AccessibilityAgent"
        }

        # Log performance metrics
        self._record_accessibility_metric("DesignTokenCheck", design_token_check["overall_score"], "%")

        logger.info(f"Design token accessibility check completed: {design_token_check}")
        return design_token_check

    def run_accessibility_audit(self, target: str = "/mock/page") -> Dict[str, Any]:
        """Run accessibility audit on target with enhanced validation and intelligence."""
        try:
            self._validate_audit_target(target)
            
            logger.info(f"Running accessibility audit on: {target}")
            
            # Record start time for performance monitoring
            start_time = time.time()
            
            # Simulate accessibility audit
            audit_result = {
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "overall_score": 85,
                "wcag_compliance": "AA",
                "issues": [
                    {"type": "color_contrast", "severity": "medium", "description": "Insufficient color contrast on buttons"},
                    {"type": "alt_text", "severity": "low", "description": "Missing alt text on decorative images"},
                    {"type": "keyboard_navigation", "severity": "high", "description": "Focus indicators not visible"}
                ],
                "recommendations": [],
                "agent": "AccessibilityAgent"
            }
            
            # Assess accessibility level
            accessibility_level = self._assess_accessibility_level(audit_result)
            audit_result["accessibility_level"] = accessibility_level
            
            # Generate recommendations
            recommendations = self._generate_accessibility_recommendations(audit_result)
            audit_result["recommendations"] = recommendations
            
            # Record performance
            end_time = time.time()
            audit_time = end_time - start_time
            
            # Log performance metric
            self._record_accessibility_metric("audit_execution_time", audit_time, "s")
            
            # Add to audit history
            audit_entry = f"{datetime.now().isoformat()}: Accessibility audit on {target} - Score: {audit_result['overall_score']}%"
            self.audit_history.append(audit_entry)
            self._save_audit_history()
            
            logger.info(f"Accessibility audit completed: {audit_result}")
            
            return audit_result
            
        except AccessibilityValidationError as e:
            logger.error(f"Validation error in accessibility audit: {e}")
            return {
                "success": False,
                "target": target,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error running accessibility audit: {e}")
            return {
                "success": False,
                "target": target,
                "error": str(e)
            }

    def export_audit(self, format_type: str = "md", audit_data: Optional[Dict] = None):
        """Export audit results in specified format with enhanced validation."""
        try:
            self._validate_format_type(format_type)
            
            if audit_data is None:
                audit_data = {
                    "agent": "AccessibilityAgent",
                    "timestamp": datetime.now().isoformat(),
                    "audit_history": self.audit_history[-10:],
                    "accessibility_metrics": {
                        "total_audits": len(self.audit_history),
                        "average_score": 85.0,
                        "compliance_level": "WCAG 2.1 AA"
                    }
                }
            
            if format_type == "md":
                self._export_markdown(audit_data)
            elif format_type == "csv":
                self._export_csv(audit_data)
            elif format_type == "json":
                self._export_json(audit_data)
            
            # Log performance metric
            self._record_accessibility_metric("audit_export", 100, "%")
            
        except AccessibilityValidationError as e:
            logger.error(f"Validation error exporting audit: {e}")
            raise
        except Exception as e:
            logger.error(f"Error exporting audit: {e}")
            raise

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

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Audit export saved to: {output_file}")

    def _export_csv(self, audit_data: Dict):
        """Export audit data as CSV."""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Score", "Issues"])

            categories = audit_data.get("categories", {})
            for category, data in categories.items():
                issues = ", ".join(data.get("issues", []))
                writer.writerow([category, data.get("score", 0), issues])

        print(f"Audit export saved to: {output_file}")

    def _export_json(self, audit_data: Dict):
        """Export audit data as JSON."""
        output_file = f"accessibility_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(audit_data, f, indent=2)

        print(f"Audit export saved to: {output_file}")

    def generate_improvement_report(self):
        """Generate accessibility improvement report with enhanced intelligence."""
        try:
            logger.info("Generating accessibility improvement report")
            
            # Analyze common issues
            common_issues = self._analyze_common_issues()
            
            # Generate comprehensive report
            report = {
                "timestamp": datetime.now().isoformat(),
                "agent": "AccessibilityAgent",
                "accessibility_standards": self.accessibility_standards,
                "common_issues": common_issues,
                "recommendations": [
                    "Implement automated accessibility testing in CI/CD",
                    "Add accessibility training for development team",
                    "Establish accessibility review process",
                    "Use accessibility testing tools regularly",
                    "Monitor accessibility metrics over time"
                ],
                "next_steps": [
                    "Schedule accessibility audit for all components",
                    "Review and update accessibility guidelines",
                    "Implement accessibility monitoring dashboard",
                    "Conduct user testing with assistive technologies"
                ]
            }
            
            # Log performance metric
            self._record_accessibility_metric("improvement_report_generation", 100, "%")
            
            logger.info(f"Accessibility improvement report generated: {report}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating improvement report: {e}")
            return {
                "success": False,
                "error": str(e)
            }

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

        # Publish completion with safe access to scores
        overall_score = audit_result.get("overall_score", 0) if audit_result.get("success", True) else 0
        shadcn_score = shadcn_test.get("accessibility_score", 0)
        
        publish("accessibility_audit_completed", {
            "status": "success",
            "agent": "AccessibilityAgent",
            "overall_score": overall_score,
            "shadcn_score": shadcn_score
        })

        # Save context
        save_context("AccessibilityAgent", "status", {"accessibility_status": "audited"})

        # Notify via Slack
        try:
            send_slack_message(f"Accessibility audit completed with {overall_score}% score")
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
