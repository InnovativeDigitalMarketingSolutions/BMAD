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
from typing import Any, Dict, List, Optional

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.figma.figma_client import FigmaClient
from integrations.slack.slack_notify import send_slack_message

# Voeg MCP imports toe na de bestaande imports
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

class UXUIDesignerAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "UXUIDesigner"
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/uxuidesigner/best-practices.md",
            "design-system": self.resource_base / "templates/uxuidesigner/design-system-template.md",
            "component-spec": self.resource_base / "templates/uxuidesigner/component-spec-template.md",
            "shadcn-tokens": self.resource_base / "templates/uxuidesigner/shadcn-design-tokens.md",
            "accessibility-checklist": self.resource_base / "templates/uxuidesigner/accessibility-checklist.md",
            "design-review": self.resource_base / "templates/uxuidesigner/design-review-template.md",
            "figma-analysis": self.resource_base / "templates/uxuidesigner/figma-analysis-template.md",
            "user-research": self.resource_base / "templates/uxuidesigner/user-research-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/uxuidesigner/design-changelog.md",
            "design-history": self.resource_base / "data/uxuidesigner/design-history.md",
            "feedback-history": self.resource_base / "data/uxuidesigner/feedback-history.md"
        }

        # Initialize histories
        self.design_history = []
        self.feedback_history = []
        self._load_design_history()
        self._load_feedback_history()

        # MCP integratie attributen
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
            "service_name": "UXUIDesignerAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced UX/UI design capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for UXUIDesigner")
        except Exception as e:
            logger.warning(f"MCP initialization failed for UXUIDesigner: {e}")
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

    async def use_uxui_specific_mcp_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use UX/UI-specific MCP tools voor enhanced design analysis."""
        if not self.mcp_enabled:
            return {}
        enhanced_data = {}
        try:
            # Design analysis
            analysis_result = await self.use_mcp_tool("design_analysis", {
                "design_id": design_data.get("design_id", ""),
                "platform": design_data.get("platform", ""),
                "app_type": design_data.get("app_type", ""),
                "design_data": design_data,
                "analysis_type": "uxui"
            })
            if analysis_result:
                enhanced_data["design_analysis"] = analysis_result
            # Accessibility check
            accessibility_result = await self.use_mcp_tool("accessibility_check", {
                "design_id": design_data.get("design_id", ""),
                "platform": design_data.get("platform", ""),
                "design_data": design_data
            })
            if accessibility_result:
                enhanced_data["accessibility_check"] = accessibility_result
            # Component spec generation
            component_spec_result = await self.use_mcp_tool("component_spec_generation", {
                "component_name": design_data.get("component_name", ""),
                "platform": design_data.get("platform", ""),
                "design_data": design_data
            })
            if component_spec_result:
                enhanced_data["component_spec_generation"] = component_spec_result
            # Figma analysis
            figma_result = await self.use_mcp_tool("figma_analysis", {
                "figma_file_id": design_data.get("figma_file_id", ""),
                "design_data": design_data
            })
            if figma_result:
                enhanced_data["figma_analysis"] = figma_result
            logger.info(f"UX/UI-specific MCP tools executed: {list(enhanced_data.keys())}")
        except Exception as e:
            logger.error(f"Error in UX/UI-specific MCP tools: {e}")
        return enhanced_data

    async def use_enhanced_mcp_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_uxui_specific_mcp_tools(design_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": design_data.get("capabilities", []),
                "performance_metrics": design_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # UX/UI-specific enhanced tools
            uxui_enhanced_result = await self.use_uxui_specific_enhanced_tools(design_data)
            enhanced_data.update(uxui_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_uxui_operation(design_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_uxui_specific_enhanced_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use UX/UI-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced design system
            if "design_system" in design_data:
                design_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_design_system", {
                    "design_data": design_data["design_system"],
                    "requirements": design_data.get("requirements", {}),
                    "constraints": design_data.get("constraints", {})
                })
                enhanced_tools["enhanced_design_system"] = design_result
            
            # Enhanced component design
            if "component_design" in design_data:
                component_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_component_design", {
                    "component_data": design_data["component_design"],
                    "accessibility_requirements": design_data.get("accessibility_requirements", {}),
                    "performance_requirements": design_data.get("performance_requirements", {})
                })
                enhanced_tools["enhanced_component_design"] = component_result
            
            # Enhanced team collaboration
            if "team_collaboration" in design_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "FrontendDeveloper", "AccessibilityAgent", "QualityGuardian"],
                    {
                        "type": "design_review",
                        "content": design_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced accessibility validation
            if "accessibility_validation" in design_data:
                accessibility_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_accessibility_validation", {
                    "design_data": design_data["accessibility_validation"],
                    "standards": design_data.get("accessibility_standards", ["WCAG2.1", "WCAG2.2"]),
                    "validation_level": design_data.get("validation_level", "comprehensive")
                })
                enhanced_tools["enhanced_accessibility_validation"] = accessibility_result
            
            logger.info(f"UX/UI-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in UX/UI-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_uxui_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace UX/UI design operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "uxui_design",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "design_complexity": len(operation_data.get("components", [])),
                    "accessibility_checks": len(operation_data.get("accessibility_requirements", [])),
                    "collaboration_agents": len(operation_data.get("team_collaboration", {}).get("agents", []))
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("uxui_design_operation", trace_data)
            
            logger.info(f"UX/UI operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

    async def create_mobile_ux_design(self, platform: str = "iOS", app_type: str = "native") -> Dict[str, Any]:
        """Create comprehensive mobile UX design for specified platform with input validation."""
        # Input validation
        if not platform or not isinstance(platform, str):
            raise ValueError("Platform must be a non-empty string")
        if not app_type or not isinstance(app_type, str):
            raise ValueError("App type must be a non-empty string")
            
        valid_platforms = ["iOS", "Android", "React Native", "Flutter"]
        if platform not in valid_platforms:
            raise ValueError(f"Platform must be one of: {', '.join(valid_platforms)}")
            
        valid_app_types = ["native", "hybrid", "pwa"]
        if app_type not in valid_app_types:
            raise ValueError(f"App type must be one of: {', '.join(valid_app_types)}")
        
        logger.info(f"Creating mobile UX design for {platform} - {app_type}")

        # Simulate mobile UX design creation
        time.sleep(1)

        mobile_ux_result = {
            "design_id": f"mobile_ux_{platform}_{app_type}_{int(time.time())}",
            "platform": platform,
            "app_type": app_type,
            "status": "completed",
            "design_system": {
                "platform_guidelines": f"{platform} Human Interface Guidelines",
                "design_tokens": {
                    "colors": f"{platform} color palette",
                    "typography": f"{platform} typography system",
                    "spacing": f"{platform} spacing system",
                    "icons": f"{platform} icon system"
                },
                "components": {
                    "navigation": f"{platform} navigation patterns",
                    "forms": f"{platform} form components",
                    "buttons": f"{platform} button styles",
                    "cards": f"{platform} card components",
                    "modals": f"{platform} modal patterns"
                }
            },
            "user_flows": {
                "onboarding": f"{platform} onboarding flow",
                "authentication": f"{platform} authentication flow",
                "main_navigation": f"{platform} main navigation flow",
                "feature_interaction": f"{platform} feature interaction flows"
            },
            "accessibility": {
                "screen_reader": f"{platform} screen reader support",
                "voice_control": f"{platform} voice control support",
                "gesture_navigation": f"{platform} gesture navigation",
                "accessibility_labels": f"{platform} accessibility labels"
            },
            "performance_considerations": {
                "loading_states": f"{platform} loading state design",
                "offline_states": f"{platform} offline state design",
                "error_states": f"{platform} error state design",
                "success_states": f"{platform} success state design"
            },
            "platform_specific": {
                "ios": {
                    "safe_areas": "Safe area considerations",
                    "gestures": "iOS gesture patterns",
                    "haptic_feedback": "Haptic feedback design",
                    "dark_mode": "Dark mode support"
                },
                "android": {
                    "material_design": "Material Design 3 guidelines",
                    "gesture_navigation": "Gesture navigation support",
                    "adaptive_icons": "Adaptive icon design",
                    "theming": "Dynamic theming support"
                },
                "cross_platform": {
                    "responsive_design": "Responsive design patterns",
                    "adaptive_layouts": "Adaptive layout strategies",
                    "platform_detection": "Platform detection logic",
                    "unified_experience": "Unified cross-platform experience"
                }
            },
            "quality_metrics": {
                "usability": "95%",
                "accessibility": "92%",
                "performance": "90%",
                "platform_compliance": "98%"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "UXUIDesigner"
        }

        # MCP integratie
        design_data = {
            "design_id": mobile_ux_result["design_id"],
            "platform": platform,
            "app_type": app_type,
            "design_data": mobile_ux_result
        }
        mcp_enhanced_data = await self.use_uxui_specific_mcp_tools(design_data)
        if mcp_enhanced_data:
            mobile_ux_result["mcp_enhanced_data"] = mcp_enhanced_data
            logger.info("MCP enhanced data integrated into mobile UX design")

        # Log performance metrics
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 95, "%")

        # Add to design history
        design_entry = f"{datetime.now().isoformat()}: Mobile UX design created - {platform} {app_type}"
        self.design_history.append(design_entry)
        self._save_design_history()

        logger.info(f"Mobile UX design created: {mobile_ux_result}")
        return mobile_ux_result

    def design_mobile_component(self, component_name: str = "Button", platform: str = "iOS") -> Dict[str, Any]:
        """Design mobile-specific component for specified platform."""
        logger.info(f"Designing mobile component: {component_name} for {platform}")

        # Simulate mobile component design
        time.sleep(1)

        mobile_component_result = {
            "component_id": f"mobile_{component_name}_{platform}_{int(time.time())}",
            "component_name": component_name,
            "platform": platform,
            "status": "completed",
            "design_specs": {
                "visual_design": {
                    "colors": f"{platform} color palette for {component_name}",
                    "typography": f"{platform} typography for {component_name}",
                    "spacing": f"{platform} spacing for {component_name}",
                    "shadows": f"{platform} shadow system for {component_name}",
                    "borders": f"{platform} border radius for {component_name}"
                },
                "interactions": {
                    "touch_targets": f"{platform} touch target size for {component_name}",
                    "gestures": f"{platform} gesture support for {component_name}",
                    "feedback": f"{platform} haptic feedback for {component_name}",
                    "animations": f"{platform} animation patterns for {component_name}"
                },
                "states": {
                    "default": f"{platform} default state for {component_name}",
                    "pressed": f"{platform} pressed state for {component_name}",
                    "disabled": f"{platform} disabled state for {component_name}",
                    "loading": f"{platform} loading state for {component_name}",
                    "error": f"{platform} error state for {component_name}"
                }
            },
            "accessibility": {
                "accessibility_label": f"Accessibility label for {component_name}",
                "accessibility_hint": f"Accessibility hint for {component_name}",
                "accessibility_traits": f"Accessibility traits for {component_name}",
                "voice_control": f"Voice control support for {component_name}"
            },
            "platform_specific": {
                "ios": {
                    "swift_ui": f"SwiftUI implementation for {component_name}",
                    "uikit": f"UIKit implementation for {component_name}",
                    "auto_layout": f"Auto Layout constraints for {component_name}"
                },
                "android": {
                    "compose": f"Jetpack Compose implementation for {component_name}",
                    "xml": f"XML layout for {component_name}",
                    "constraint_layout": f"Constraint Layout for {component_name}"
                },
                "react_native": {
                    "jsx": f"React Native JSX for {component_name}",
                    "styling": f"React Native styling for {component_name}",
                    "props": f"React Native props for {component_name}"
                },
                "flutter": {
                    "dart": f"Flutter Dart implementation for {component_name}",
                    "widget": f"Flutter widget for {component_name}",
                    "theme": f"Flutter theme for {component_name}"
                }
            },
            "quality_metrics": {
                "usability": "94%",
                "accessibility": "93%",
                "performance": "91%",
                "platform_compliance": "96%"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "UXUIDesigner"
        }

        # Log performance metrics
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 94, "%")

        # Add to design history
        design_entry = f"{datetime.now().isoformat()}: Mobile component designed - {component_name} for {platform}"
        self.design_history.append(design_entry)
        self._save_design_history()

        logger.info(f"Mobile component designed: {mobile_component_result}")
        return mobile_component_result

    def create_mobile_user_flow(self, flow_name: str = "Onboarding", platform: str = "iOS") -> Dict[str, Any]:
        """Create mobile user flow design for specified platform."""
        logger.info(f"Creating mobile user flow: {flow_name} for {platform}")

        # Simulate mobile user flow creation
        time.sleep(1)

        mobile_flow_result = {
            "flow_id": f"mobile_flow_{flow_name}_{platform}_{int(time.time())}",
            "flow_name": flow_name,
            "platform": platform,
            "status": "completed",
            "flow_steps": {
                "step_1": {
                    "screen": f"{flow_name} - Welcome Screen",
                    "actions": ["Tap to start", "Swipe to continue"],
                    "transitions": ["Slide right", "Fade in"]
                },
                "step_2": {
                    "screen": f"{flow_name} - Information Screen",
                    "actions": ["Scroll content", "Tap next"],
                    "transitions": ["Slide up", "Scale in"]
                },
                "step_3": {
                    "screen": f"{flow_name} - Action Screen",
                    "actions": ["Complete action", "Submit"],
                    "transitions": ["Slide left", "Fade out"]
                }
            },
            "interaction_patterns": {
                "gestures": f"{platform} gesture patterns for {flow_name}",
                "navigation": f"{platform} navigation patterns for {flow_name}",
                "feedback": f"{platform} feedback patterns for {flow_name}",
                "accessibility": f"{platform} accessibility patterns for {flow_name}"
            },
            "user_experience": {
                "progressive_disclosure": "Progressive disclosure strategy",
                "cognitive_load": "Minimal cognitive load design",
                "error_prevention": "Error prevention strategies",
                "recovery_mechanisms": "Error recovery mechanisms"
            },
            "platform_optimization": {
                "ios": {
                    "safe_areas": "Safe area considerations",
                    "gesture_navigation": "Gesture navigation support",
                    "haptic_feedback": "Haptic feedback integration"
                },
                "android": {
                    "material_design": "Material Design principles",
                    "gesture_navigation": "Gesture navigation support",
                    "adaptive_icons": "Adaptive icon integration"
                }
            },
            "quality_metrics": {
                "usability": "93%",
                "accessibility": "91%",
                "performance": "89%",
                "user_satisfaction": "92%"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "UXUIDesigner"
        }

        # Log performance metrics
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 93, "%")

        # Add to design history
        design_entry = f"{datetime.now().isoformat()}: Mobile user flow created - {flow_name} for {platform}"
        self.design_history.append(design_entry)
        self._save_design_history()

        logger.info(f"Mobile user flow created: {mobile_flow_result}")
        return mobile_flow_result

    def _load_design_history(self):
        """Load design history from file with improved error handling."""
        try:
            if self.data_paths["design-history"].exists():
                with open(self.data_paths["design-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.design_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Design history file not found, starting with empty history")
            self.design_history = []
        except PermissionError:
            logger.warning("Permission denied accessing design history file")
            self.design_history = []
        except UnicodeDecodeError:
            logger.error("Design history file contains invalid characters, starting with empty history")
            self.design_history = []
        except Exception as e:
            logger.warning(f"Could not load design history: {e}")
            self.design_history = []

    def _save_design_history(self):
        """Save design history to file with improved error handling."""
        try:
            self.data_paths["design-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["design-history"], "w") as f:
                f.write("# Design History\n\n")
                f.writelines(f"- {design}\n" for design in self.design_history[-50:])
        except PermissionError:
            logger.error("Permission denied saving design history file")
        except OSError as e:
            logger.error(f"OS error saving design history: {e}")
        except Exception as e:
            logger.error(f"Could not save design history: {e}")

    def _load_feedback_history(self):
        """Load feedback history from file with improved error handling."""
        try:
            if self.data_paths["feedback-history"].exists():
                with open(self.data_paths["feedback-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.feedback_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Feedback history file not found, starting with empty history")
            self.feedback_history = []
        except PermissionError:
            logger.warning("Permission denied accessing feedback history file")
            self.feedback_history = []
        except UnicodeDecodeError:
            logger.error("Feedback history file contains invalid characters, starting with empty history")
            self.feedback_history = []
        except Exception as e:
            logger.warning(f"Could not load feedback history: {e}")
            self.feedback_history = []

    def _save_feedback_history(self):
        """Save feedback history to file with improved error handling."""
        try:
            self.data_paths["feedback-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["feedback-history"], "w") as f:
                f.write("# Feedback History\n\n")
                f.writelines(f"- {feedback}\n" for feedback in self.feedback_history[-50:])
        except PermissionError:
            logger.error("Permission denied saving feedback history file")
        except OSError as e:
            logger.error(f"OS error saving feedback history: {e}")
        except Exception as e:
            logger.error(f"Could not save feedback history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
UXUIDesigner Agent Commands:
  help                    - Show this help message
  build-shadcn-component  - Build Shadcn/ui component
  create-component-spec   - Create component specification
  create-mobile-ux        - Create mobile UX design
  design-mobile-component - Design mobile component
  create-mobile-flow      - Create mobile user flow
  design-feedback         - Provide design feedback
  document-component      - Document component
  analyze-figma           - Analyze Figma design
  show-design-history     - Show design history
  show-feedback-history   - Show feedback history
  show-best-practices     - Show UX/UI best practices
  show-changelog          - Show UX/UI designer changelog
  export-report [format]  - Export design report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Run the agent and listen for events
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content with improved error handling and validation."""
        if not resource_type or not isinstance(resource_type, str):
            print("Error: Invalid resource type provided")
            return
            
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "design-system":
                path = self.template_paths["design-system"]
            elif resource_type == "shadcn-tokens":
                path = self.template_paths["shadcn-tokens"]
            elif resource_type == "accessibility-checklist":
                path = self.template_paths["accessibility-checklist"]
            else:
                print(f"Error: Unknown resource type: {resource_type}")
                print("Available resource types: best-practices, changelog, design-system, shadcn-tokens, accessibility-checklist")
                return
                
            if path.exists():
                with open(path) as f:
                    content = f.read()
                    if content.strip():
                        print(content)
                    else:
                        print(f"Resource file is empty: {path}")
            else:
                print(f"Error: Resource file not found: {path}")
        except PermissionError:
            logger.error(f"Permission denied reading resource {resource_type}")
            print(f"Error: Permission denied accessing resource: {resource_type}")
        except UnicodeDecodeError:
            logger.error(f"Resource file {resource_type} contains invalid characters")
            print(f"Error: Resource file contains invalid characters: {resource_type}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")
            print(f"Error: Could not read resource {resource_type}: {e}")

    def show_design_history(self):
        if not self.design_history:
            print("No design history available.")
            return
        print("Design History:")
        print("=" * 50)
        for i, design in enumerate(self.design_history[-10:], 1):
            print(f"{i}. {design}")

    def show_feedback_history(self):
        if not self.feedback_history:
            print("No feedback history available.")
            return
        print("Feedback History:")
        print("=" * 50)
        for i, feedback in enumerate(self.feedback_history[-10:], 1):
            print(f"{i}. {feedback}")

    def build_shadcn_component(self, component_name: str = "Button") -> Dict[str, Any]:
        """Build a Shadcn/ui component with design tokens and accessibility focus."""
        # Input validation
        if not component_name or not isinstance(component_name, str):
            raise ValueError("Component name must be a non-empty string")
        if len(component_name.strip()) == 0:
            raise ValueError("Component name cannot be empty or whitespace")
            
        # Validate component name format
        if not component_name[0].isupper():
            raise ValueError("Component name should start with uppercase letter")
        
        logger.info(f"Building Shadcn component: {component_name}")

        # Simulate Shadcn component build with design tokens
        time.sleep(1)
        result = {
            "component": component_name,
            "type": "Shadcn/ui",
            "design_tokens": {
                "colors": {
                    "primary": "hsl(var(--primary))",
                    "secondary": "hsl(var(--secondary))",
                    "accent": "hsl(var(--accent))",
                    "destructive": "hsl(var(--destructive))"
                },
                "spacing": {
                    "xs": "0.25rem",
                    "sm": "0.5rem",
                    "md": "1rem",
                    "lg": "1.5rem",
                    "xl": "2rem"
                },
                "typography": {
                    "font-family": "Inter, system-ui, sans-serif",
                    "font-size": {
                        "sm": "0.875rem",
                        "base": "1rem",
                        "lg": "1.125rem",
                        "xl": "1.25rem"
                    }
                }
            },
            "variants": ["default", "secondary", "outline", "destructive", "ghost", "link"],
            "sizes": ["sm", "default", "lg", "icon"],
            "accessibility_features": [
                "ARIA labels",
                "Keyboard navigation",
                "Focus management",
                "Screen reader support",
                "High contrast support"
            ],
            "status": "created",
            "accessibility_score": 98,
            "design_score": 95,
            "timestamp": datetime.now().isoformat(),
            "agent": "UXUIDesignerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, result["accessibility_score"], "%")
        self.monitor._record_metric("UXUIDesigner", MetricType.RESPONSE_TIME, result["design_score"], "ms")

        # Add to design history
        design_entry = f"{datetime.now().isoformat()}: Shadcn {component_name} component built with {result['accessibility_score']}% accessibility score"
        self.design_history.append(design_entry)
        self._save_design_history()

        logger.info(f"Shadcn component build result: {result}")
        return result

    def create_component_spec(self, component_name: str = "Button") -> Dict[str, Any]:
        """Create a detailed component specification with Shadcn design tokens."""
        logger.info(f"Creating component spec for: {component_name}")

        spec = {
            "component_name": component_name,
            "version": "1.0.0",
            "description": f"Shadcn/ui {component_name} component with design tokens",
            "design_tokens": {
                "colors": {
                    "primary": "hsl(var(--primary))",
                    "secondary": "hsl(var(--secondary))",
                    "accent": "hsl(var(--accent))",
                    "destructive": "hsl(var(--destructive))",
                    "muted": "hsl(var(--muted))",
                    "popover": "hsl(var(--popover))",
                    "card": "hsl(var(--card))"
                },
                "spacing": {
                    "xs": "0.25rem",
                    "sm": "0.5rem",
                    "md": "1rem",
                    "lg": "1.5rem",
                    "xl": "2rem",
                    "2xl": "3rem"
                },
                "border_radius": {
                    "sm": "calc(var(--radius) - 4px)",
                    "md": "calc(var(--radius) - 2px)",
                    "lg": "var(--radius)"
                }
            },
            "props": {
                "variant": {
                    "type": "string",
                    "default": "default",
                    "options": ["default", "secondary", "outline", "destructive", "ghost", "link"]
                },
                "size": {
                    "type": "string",
                    "default": "default",
                    "options": ["sm", "default", "lg", "icon"]
                },
                "disabled": {
                    "type": "boolean",
                    "default": False
                }
            },
            "accessibility": {
                "aria_label": "Required for icon buttons",
                "keyboard_navigation": "Tab and Enter/Space support",
                "focus_management": "Visible focus indicators",
                "screen_reader": "Proper ARIA attributes"
            },
            "usage_examples": [
                f'<{component_name} variant="default">Click me</{component_name}>',
                f'<{component_name} variant="outline" size="sm">Small Outline</{component_name}>',
                f'<{component_name} variant="destructive">Delete</{component_name}>'
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "UXUIDesignerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 95, "%")

        # Add to design history
        spec_entry = f"{datetime.now().isoformat()}: Component spec created for {component_name} with design tokens"
        self.design_history.append(spec_entry)
        self._save_design_history()

        logger.info(f"Component spec created: {spec}")
        return spec

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        if not report_data:
            report_data = {
                "design_system": "BMAD Design System v1.0",
                "components_created": 15,
                "shadcn_components": 8,
                "accessibility_score": 96,
                "design_score": 94,
                "user_research_sessions": 5,
                "timestamp": datetime.now().isoformat(),
                "agent": "UXUIDesignerAgent"
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
        output_file = f"uxui_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# UX/UI Designer Report

## Summary
- **Design System**: {report_data.get('design_system', 'N/A')}
- **Components Created**: {report_data.get('components_created', 0)}
- **Shadcn Components**: {report_data.get('shadcn_components', 0)}
- **Accessibility Score**: {report_data.get('accessibility_score', 0)}%
- **Design Score**: {report_data.get('design_score', 0)}%
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Activity
- User Research Sessions: {report_data.get('user_research_sessions', 0)}
- Design Reviews: {report_data.get('design_reviews', 0)}
- Component Specs: {report_data.get('component_specs', 0)}

## Performance Metrics
- Design Quality: {report_data.get('design_score', 0)}%
- Accessibility Compliance: {report_data.get('accessibility_score', 0)}%
- User Satisfaction: {report_data.get('user_satisfaction', 'N/A')}
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        output_file = f"uxui_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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

    async def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting UX/UI collaboration example...")

        # Publish design request
        publish("design_requested", {
            "agent": "UXUIDesignerAgent",
            "task": "Create Shadcn Button Component",
            "timestamp": datetime.now().isoformat()
        })

        # Build Shadcn component
        self.build_shadcn_component("Button")

        # Create component spec
        self.create_component_spec("Button")

        # Publish completion
        publish("design_completed", {
            "status": "success",
            "agent": "UXUIDesignerAgent",
            "component": "Button",
            "accessibility_score": 98
        })

        # Save context
        save_context("UXUIDesigner", "status", {"design_status": "completed"})

        # Notify via Slack
        try:
            send_slack_message("UX/UI design completed with 98% accessibility score")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("UXUIDesigner")
        print(f"Opgehaalde context: {context}")

    def handle_design_requested(self, event):
        logger.info(f"Design requested: {event}")
        event.get("task", "Create UI Component")
        self.build_shadcn_component("Button")

    async def handle_design_completed(self, event):
        logger.info(f"Design completed: {event}")

        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("design_approval", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    async def run(self):
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        print("🎨 UX/UI Designer Agent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        def sync_handler(event):
            asyncio.run(self.handle_design_completed(event))

        subscribe("design_completed", sync_handler)
        subscribe("design_requested", self.handle_design_requested)

        logger.info("UXUIDesignerAgent ready and listening for events...")
        await self.collaborate_example()

    # --- ORIGINELE FUNCTIONALITEIT BEHOUDEN ---
    def collaborate_example_original(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("design_finalized", {"status": "success", "agent": "UXUIDesigner"})
        save_context("UXUIDesigner", "status", {"design_status": "finalized"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("UXUIDesigner")
        print(f"Opgehaalde context: {context}")

    def design_feedback(self, feedback_text):
        if not feedback_text:
            return {"error": "Feedback text cannot be empty"}
        
        prompt = f"Analyseer de volgende design feedback en doe 2 concrete verbetervoorstellen:\n{feedback_text}"
        result = ask_openai(prompt)
        logging.info(f"[UXUIDesigner][LLM Design Feedback]: {result}")

        # Add to feedback history
        feedback_entry = f"{datetime.now().isoformat()}: Design feedback analyzed - {feedback_text[:50]}..."
        self.feedback_history.append(feedback_entry)
        self._save_feedback_history()

        # Log performance metric
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 92, "%")

        return result

    def document_component(self, component_desc):
        if not component_desc:
            return {"error": "Component description cannot be empty"}
        
        prompt = f"Genereer een korte documentatie voor deze UI-component:\n{component_desc}"
        result = ask_openai(prompt)
        logging.info(f"[UXUIDesigner][LLM Component Doc]: {result}")

        # Add to design history
        doc_entry = f"{datetime.now().isoformat()}: Component documented - {component_desc[:50]}..."
        self.design_history.append(doc_entry)
        self._save_design_history()

        # Log performance metric
        self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 88, "%")

        return result

    def analyze_figma_design(self, figma_file_id: str) -> Dict:
        """
        Analyseer een Figma design op layout, kleurgebruik, en accessibility-signalen.
        """
        if not figma_file_id:
            return {"error": "Figma file ID cannot be empty"}
        
        try:
            client = FigmaClient()

            # Haal file data op
            file_data = client.get_file(figma_file_id)

            logging.info(f"[UXUIDesigner][Figma Analysis] Analyzing file: {file_data.get('name', 'Unknown')}")

            # Analyseer document structuur
            document = file_data.get("document", {})
            pages = document.get("children", [])

            analysis_result = {
                "file_name": file_data.get("name", ""),
                "file_id": figma_file_id,
                "total_pages": len(pages),
                "pages": [],
                "design_insights": {},
                "accessibility_issues": [],
                "color_analysis": {},
                "layout_analysis": {}
            }

            # Analyseer elke pagina
            for page in pages:
                page_analysis = self.analyze_page(page)
                analysis_result["pages"].append(page_analysis)

            # Genereer algemene design insights met LLM
            design_insights = self.generate_design_insights(analysis_result)
            analysis_result["design_insights"] = design_insights

            # Analyseer kleurgebruik
            color_analysis = self.analyze_colors(file_data)
            analysis_result["color_analysis"] = color_analysis

            # Analyseer layout
            layout_analysis = self.analyze_layout(file_data)
            analysis_result["layout_analysis"] = layout_analysis

            # Check accessibility
            accessibility_issues = self.check_accessibility(file_data)
            analysis_result["accessibility_issues"] = accessibility_issues

            # Add to design history
            analysis_entry = f"{datetime.now().isoformat()}: Figma design analyzed - {file_data.get('name', 'Unknown')}"
            self.design_history.append(analysis_entry)
            self._save_design_history()

            # Log performance metric
            self.monitor._record_metric("UXUIDesigner", MetricType.SUCCESS_RATE, 95, "%")

            logging.info(f"[UXUIDesigner][Figma Analysis] Completed analysis for {len(pages)} pages")
            return analysis_result

        except Exception as e:
            logging.exception(f"[UXUIDesigner][Figma Analysis Error]: {e!s}")
            return {"error": str(e)}

    def analyze_page(self, page_data: Dict) -> Dict:
        """Analyseer een individuele Figma pagina."""
        return {
            "name": page_data.get("name", ""),
            "id": page_data.get("id", ""),
            "type": page_data.get("type", ""),
            "children_count": len(page_data.get("children", [])),
            "has_components": self.has_components(page_data),
            "has_text": self.has_text_elements(page_data),
            "has_images": self.has_image_elements(page_data)
        }

    def has_components(self, node: Dict) -> bool:
        """Check of een node componenten bevat."""
        if node.get("type") == "COMPONENT":
            return True
        for child in node.get("children", []):
            if self.has_components(child):
                return True
        return False

    def has_text_elements(self, node: Dict) -> bool:
        """Check of een node tekst elementen bevat."""
        if node.get("type") == "TEXT":
            return True
        for child in node.get("children", []):
            if self.has_text_elements(child):
                return True
        return False

    def has_image_elements(self, node: Dict) -> bool:
        """Check of een node afbeeldingen bevat."""
        if node.get("type") in ["RECTANGLE", "ELLIPSE", "VECTOR"]:
            return True
        for child in node.get("children", []):
            if self.has_image_elements(child):
                return True
        return False

    def generate_design_insights(self, analysis_data: Dict) -> Dict:
        """Genereer design insights met LLM."""
        prompt = f"""
        Analyseer deze Figma design data en geef design insights:
        - Aantal pagina's: {analysis_data.get('total_pages', 0)}
        - Pagina's met componenten: {sum(1 for p in analysis_data.get('pages', []) if p.get('has_components'))}
        - Pagina's met tekst: {sum(1 for p in analysis_data.get('pages', []) if p.get('has_text'))}
        - Pagina's met afbeeldingen: {sum(1 for p in analysis_data.get('pages', []) if p.get('has_images'))}
        
        Geef 3 concrete design aanbevelingen.
        """

        result = ask_openai(prompt)
        return {
            "llm_insights": result,
            "summary": f"Design met {analysis_data.get('total_pages', 0)} pagina's geanalyseerd"
        }

    def analyze_colors(self, file_data: Dict) -> Dict:
        """Analyseer kleurgebruik in Figma design."""
        colors = set()

        def extract_colors(node):
            if "fills" in node:
                for fill in node["fills"]:
                    if fill.get("type") == "SOLID":
                        color = fill.get("color", {})
                        if color:
                            colors.add(f"rgb({color.get('r', 0)}, {color.get('g', 0)}, {color.get('b', 0)})")
            for child in node.get("children", []):
                extract_colors(child)

        extract_colors(file_data.get("document", {}))

        return {
            "unique_colors": len(colors),
            "color_palette": list(colors)[:10]  # Eerste 10 kleuren
        }

    def analyze_layout(self, file_data: Dict) -> Dict:
        """Analyseer layout structuur."""
        layout_info = {"total_elements": 0, "max_depth": 0}

        def analyze_node(node, depth=0):
            layout_info["total_elements"] += 1
            layout_info["max_depth"] = max(layout_info["max_depth"], depth)

            for child in node.get("children", []):
                analyze_node(child, depth + 1)

        analyze_node(file_data.get("document", {}))

        return layout_info

    def check_accessibility(self, file_data: Dict) -> List[Dict]:
        """Check accessibility issues in design."""
        issues = []

        def check_node(node):
            # Check voor tekst contrast
            if node.get("type") == "TEXT":
                # Simuleer contrast check
                if "fills" in node and node.get("fills"):
                    issues.append({
                        "type": "contrast_warning",
                        "element": node.get("name", "Text element"),
                        "message": "Contrast ratio should be checked"
                    })

            # Check voor interactieve elementen
            if node.get("type") in ["FRAME", "GROUP"]:
                if node.get("name", "").lower() in ["button", "link", "input"]:
                    issues.append({
                        "type": "interactive_element",
                        "element": node.get("name", "Interactive element"),
                        "message": "Ensure proper ARIA labels and keyboard navigation"
                    })

            for child in node.get("children", []):
                check_node(child)

        check_node(file_data.get("document", {}))

        return issues

def on_figma_analysis_requested(event):
    """Event handler voor Figma analysis requests."""
    agent = UXUIDesignerAgent()
    file_id = event.get("file_id", "")
    if file_id:
        result = agent.analyze_figma_design(file_id)
        publish("figma_analysis_completed", {
            "file_id": file_id,
            "result": result,
            "agent": "UXUIDesignerAgent"
        })

def on_design_feedback_requested(event):
    """Event handler voor design feedback requests."""
    agent = UXUIDesignerAgent()
    feedback = event.get("feedback", "")
    if feedback:
        result = agent.design_feedback(feedback)
        publish("design_feedback_completed", {
            "feedback": feedback,
            "result": result,
            "agent": "UXUIDesignerAgent"
        })

def on_document_component(event):
    """Event handler voor component documentation requests."""
    agent = UXUIDesignerAgent()
    component = event.get("component", "")
    if component:
        result = agent.document_component(component)
        publish("component_documented", {
            "component": component,
            "result": result,
            "agent": "UXUIDesignerAgent"
        })

def main():
    parser = argparse.ArgumentParser(description="UXUIDesigner Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "build-shadcn-component", "create-component-spec",
                               "create-mobile-ux", "design-mobile-component", "create-mobile-flow",
                               "design-feedback", "document-component", "analyze-figma",
                               "show-design-history", "show-feedback-history", "show-best-practices",
                               "show-changelog", "export-report", "test", "collaborate", "run",
                               "initialize-mcp", "use-mcp-tool", "get-mcp-status", "use-uxui-mcp-tools", 
                               "check-dependencies", "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary"])
    parser.add_argument("--component-name", default="Button", help="Component name")
    parser.add_argument("--platform", choices=["iOS", "Android", "React Native", "Flutter"], default="iOS", help="Mobile platform")
    parser.add_argument("--app-type", choices=["native", "hybrid", "pwa"], default="native", help="App type")
    parser.add_argument("--flow-name", default="Onboarding", help="User flow name")
    parser.add_argument("--feedback-text", help="Design feedback text")
    parser.add_argument("--component-desc", help="Component description")
    parser.add_argument("--figma-file-id", help="Figma file ID")
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    args = parser.parse_args()
    agent = UXUIDesignerAgent()
    
    if args.command == "help":
        agent.show_help()
    elif args.command == "build-shadcn-component":
        result = agent.build_shadcn_component(args.component_name)
        print(json.dumps(result, indent=2))
    elif args.command == "create-component-spec":
        result = agent.create_component_spec(args.component_name)
        print(json.dumps(result, indent=2))
    elif args.command == "create-mobile-ux":
        result = asyncio.run(agent.create_mobile_ux_design(args.platform, args.app_type))
        print(json.dumps(result, indent=2))
    elif args.command == "design-mobile-component":
        result = agent.design_mobile_component(args.component_name, args.platform)
        print(json.dumps(result, indent=2))
    elif args.command == "create-mobile-flow":
        result = agent.create_mobile_user_flow(args.flow_name, args.platform)
        print(json.dumps(result, indent=2))
    elif args.command == "design-feedback":
        if not args.feedback_text:
            print("Geef feedback tekst op met --feedback-text")
            sys.exit(1)
        result = agent.design_feedback(args.feedback_text)
        if isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(json.dumps(result, indent=2))
    elif args.command == "document-component":
        if not args.component_desc:
            print("Geef component beschrijving op met --component-desc")
            sys.exit(1)
        result = agent.document_component(args.component_desc)
        if isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(json.dumps(result, indent=2))
    elif args.command == "analyze-figma":
        if not args.figma_file_id:
            print("Geef Figma file ID op met --figma-file-id")
            sys.exit(1)
        result = agent.analyze_figma_design(args.figma_file_id)
        if isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(json.dumps(result, indent=2))
    elif args.command == "show-design-history":
        agent.show_design_history()
    elif args.command == "show-feedback-history":
        agent.show_feedback_history()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-report":
        agent.export_report(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        result = asyncio.run(agent.collaborate_example())
        print(json.dumps(result, indent=2))
    elif args.command == "run":
        asyncio.run(agent.run())
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["ProductOwner", "FrontendDeveloper", "AccessibilityAgent", "QualityGuardian"], 
                {"type": "design_review", "content": {"review_type": "uxui_design"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "design_data": {"components": ["Button", "Form", "Navigation"]},
                "security_requirements": ["input_validation", "xss_prevention", "csrf_protection"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "design_data": {"components": ["Button", "Form", "Navigation"]},
                "performance_metrics": {"load_time": 2.5, "render_time": 1.2}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_uxui_operation({
                "operation_type": "component_design",
                "components": ["Button", "Form", "Navigation"],
                "accessibility_requirements": ["WCAG2.1", "WCAG2.2"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_uxui_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"load_time": 2.5, "render_time": 1.2}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_uxui_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "design_validation", "error_message": "Accessibility check failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for UXUIDesigner Agent:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print(f"Unknown command: {args.command}")
        agent.show_help()

if __name__ == "__main__":
    main()
