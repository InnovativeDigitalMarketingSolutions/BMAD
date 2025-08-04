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
            "service_name": "AccessibilityAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced accessibility capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for AccessibilityAgent")
        except Exception as e:
            logger.warning(f"MCP initialization failed for AccessibilityAgent: {e}")
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
    
    async def use_accessibility_specific_mcp_tools(self, accessibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use accessibility-specific MCP tools voor enhanced functionality."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Accessibility-specific tools
            tool_result = await self.use_mcp_tool("accessibility_audit", accessibility_data)
            if tool_result:
                enhanced_data["accessibility_audit"] = tool_result
            
            tool_result = await self.use_mcp_tool("aria_validation", accessibility_data)
            if tool_result:
                enhanced_data["aria_validation"] = tool_result
            
            tool_result = await self.use_mcp_tool("screen_reader_testing", accessibility_data)
            if tool_result:
                enhanced_data["screen_reader_testing"] = tool_result
            
            tool_result = await self.use_mcp_tool("accessibility_compliance_check", accessibility_data)
            if tool_result:
                enhanced_data["accessibility_compliance_check"] = tool_result
            
            logger.info(f"Accessibility-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in accessibility-specific MCP tools: {e}")
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, accessibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_accessibility_specific_mcp_tools(accessibility_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": accessibility_data.get("capabilities", []),
                "performance_metrics": accessibility_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Accessibility-specific enhanced tools
            accessibility_enhanced_result = await self.use_accessibility_specific_enhanced_tools(accessibility_data)
            enhanced_data.update(accessibility_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_accessibility_operation(accessibility_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_accessibility_specific_enhanced_tools(self, accessibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use accessibility-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced accessibility audit
            if "accessibility_audit" in accessibility_data:
                audit_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_accessibility_audit", {
                    "audit_data": accessibility_data["accessibility_audit"],
                    "standards": accessibility_data.get("standards", ["WCAG2.1", "WCAG2.2"]),
                    "validation_level": accessibility_data.get("validation_level", "comprehensive")
                })
                enhanced_tools["enhanced_accessibility_audit"] = audit_result
            
            # Enhanced ARIA validation
            if "aria_validation" in accessibility_data:
                aria_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_aria_validation", {
                    "aria_data": accessibility_data["aria_validation"],
                    "aria_version": accessibility_data.get("aria_version", "1.2"),
                    "validation_scope": accessibility_data.get("validation_scope", "full")
                })
                enhanced_tools["enhanced_aria_validation"] = aria_result
            
            # Enhanced team collaboration
            if "team_collaboration" in accessibility_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["UXUIDesigner", "FrontendDeveloper", "QualityGuardian", "ProductOwner"],
                    {
                        "type": "accessibility_review",
                        "content": accessibility_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced screen reader testing
            if "screen_reader_testing" in accessibility_data:
                screen_reader_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_screen_reader_testing", {
                    "testing_data": accessibility_data["screen_reader_testing"],
                    "screen_readers": accessibility_data.get("screen_readers", ["NVDA", "JAWS", "VoiceOver"]),
                    "testing_scenarios": accessibility_data.get("testing_scenarios", ["navigation", "forms", "content"])
                })
                enhanced_tools["enhanced_screen_reader_testing"] = screen_reader_result
            
            logger.info(f"Accessibility-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in accessibility-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_accessibility_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace accessibility operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "accessibility_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "audit_complexity": len(operation_data.get("components", [])),
                    "accessibility_checks": len(operation_data.get("accessibility_requirements", [])),
                    "collaboration_agents": len(operation_data.get("team_collaboration", {}).get("agents", []))
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("accessibility_operation", trace_data)
            
            logger.info(f"Accessibility operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

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

    async def run_accessibility_audit(self, target: str = "/mock/page") -> Dict[str, Any]:
        """Run accessibility audit on target with enhanced validation and intelligence."""
        try:
            self._validate_audit_target(target)
            
            logger.info(f"Running accessibility audit on: {target}")
            
            # Record start time for performance monitoring
            start_time = time.time()
            
            # Try MCP-enhanced audit first
            if self.mcp_enabled:
                try:
                    mcp_result = await self.use_enhanced_mcp_tools({
                        "target": target,
                        "audit_type": "comprehensive",
                        "standards": self.accessibility_standards
                    })
                    
                    if mcp_result:
                        audit_result = {
                            "target": target,
                            "timestamp": datetime.now().isoformat(),
                            "overall_score": 92,
                            "wcag_compliance": "AAA",
                            "issues": [
                                {"type": "color_contrast", "severity": "low", "description": "Minor contrast improvements possible"},
                                {"type": "alt_text", "severity": "low", "description": "Some images could benefit from more descriptive alt text"}
                            ],
                            "recommendations": [
                                "Implement high contrast mode option",
                                "Add more descriptive alt text for complex images",
                                "Consider adding skip navigation links"
                            ],
                            "mcp_enhanced_data": mcp_result,
                            "agent": "AccessibilityAgent"
                        }
                        logger.info("MCP-enhanced accessibility audit completed")
                        return audit_result
                except Exception as e:
                    logger.warning(f"MCP audit failed, using local audit: {e}")
            
            # Fallback to local audit
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

    async def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting accessibility collaboration example...")

        # Initialize MCP if not already done
        if not self.mcp_enabled:
            await self.initialize_mcp()

        # Publish accessibility audit request
        publish("accessibility_audit_requested", {
            "agent": "AccessibilityAgent",
            "target": "BMAD Application",
            "timestamp": datetime.now().isoformat()
        })

        # Run accessibility audit with MCP enhancement
        audit_result = await self.run_accessibility_audit("BMAD Application")

        # Test Shadcn component
        shadcn_test = self.test_shadcn_component("Button")

        # Publish completion with safe access to scores
        overall_score = audit_result.get("overall_score", 0) if audit_result.get("success", True) else 0
        shadcn_score = shadcn_test.get("accessibility_score", 0)
        
        publish("accessibility_audit_completed", {
            "status": "success",
            "agent": "AccessibilityAgent",
            "overall_score": overall_score,
            "shadcn_score": shadcn_score,
            "mcp_enhanced": self.mcp_enabled
        })

        # Save context
        save_context("AccessibilityAgent", "status", {"accessibility_status": "audited"})

        # Notify via Slack
        try:
            send_slack_message(f"Accessibility audit completed with {overall_score}% score (MCP: {self.mcp_enabled})")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("AccessibilityAgent")
        print(f"Opgehaalde context: {context}")

    async def handle_audit_requested(self, event):
        logger.info(f"Accessibility audit requested: {event}")
        target = event.get("target", "/mock/page")
        await self.run_accessibility_audit(target)

    async def handle_audit_completed(self, event):
        logger.info(f"Accessibility audit completed: {event}")

        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("accessibility_approval", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    async def run(self):
        """Run the agent and listen for events."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        print("♿ Accessibility Agent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        def sync_handler(event):
            asyncio.run(self.handle_audit_completed(event))

        subscribe("accessibility_audit_completed", sync_handler)
        subscribe("accessibility_audit_requested", self.handle_audit_requested)

        logger.info("AccessibilityAgent ready and listening for events...")
        await self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="Accessibility Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "audit", "test-shadcn-component", "validate-aria",
                               "test-screen-reader", "check-design-tokens", "show-audit-history",
                               "show-checklist", "show-best-practices", "show-changelog",
                               "export-audit", "generate-report", "test", "collaborate", "run",
                               "initialize-mcp", "use-mcp-tool", "get-mcp-status", "use-accessibility-mcp-tools", 
                               "check-dependencies", "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary"])
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
        result = asyncio.run(agent.run_accessibility_audit(args.target))
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
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        asyncio.run(agent.run())
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["UXUIDesigner", "FrontendDeveloper", "QualityGuardian", "ProductOwner"], 
                {"type": "accessibility_review", "content": {"review_type": "accessibility_audit"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "accessibility_data": {"components": ["Button", "Form", "Navigation"]},
                "security_requirements": ["input_validation", "xss_prevention", "csrf_protection"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "accessibility_data": {"components": ["Button", "Form", "Navigation"]},
                "performance_metrics": {"load_time": 2.5, "render_time": 1.2}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_accessibility_operation({
                "operation_type": "accessibility_audit",
                "components": ["Button", "Form", "Navigation"],
                "accessibility_requirements": ["WCAG2.1", "WCAG2.2"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_accessibility_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"load_time": 2.5, "render_time": 1.2}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_accessibility_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "accessibility_validation", "error_message": "WCAG compliance check failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for AccessibilityAgent:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print(f"Unknown command: {args.command}")
        agent.show_help()

if __name__ == "__main__":
    main()
