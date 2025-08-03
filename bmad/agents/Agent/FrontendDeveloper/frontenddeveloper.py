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
    AgentPerformanceProfile,
    AlertLevel,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.communication.message_bus import publish, subscribe
from integrations.figma.figma_client import FigmaClient
from integrations.slack.slack_notify import send_slack_message
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager

# MCP Integration
from bmad.core.mcp import (
    MCPClient,
    MCPContext,
    FrameworkMCPIntegration,
    get_mcp_client,
    get_framework_mcp_integration,
    initialize_framework_mcp_integration
)


# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class FrontendDeveloperAgent:
    """
    Frontend Developer Agent voor BMAD.
    Gespecialiseerd in React/Next.js, Shadcn/ui, en moderne frontend development.
    """
    
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        self.frontend_development_template = self.framework_manager.get_framework_template('frontend_development')
        self.lessons_learned = []

        """Initialize FrontendDeveloper agent met lazy loading."""
        self.agent_name = "FrontendDeveloper"
        self.component_history = []
        self.performance_history = []
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/frontenddeveloper/best-practices.md",
            "component-template": self.resource_base / "templates/frontenddeveloper/component-template.md",
            "component-export-md": self.resource_base / "templates/frontenddeveloper/component-export-template.md",
            "component-export-json": self.resource_base / "templates/frontenddeveloper/component-export-template.json",
            "performance-report": self.resource_base / "templates/frontenddeveloper/performance-report-template.md",
            "storybook-template": self.resource_base / "templates/frontenddeveloper/storybook-template.mdx",
            "accessibility-checklist": self.resource_base / "templates/frontenddeveloper/accessibility-checklist.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/frontenddeveloper/component-changelog.md",
            "component-history": self.resource_base / "data/frontenddeveloper/component-history.md",
            "performance-history": self.resource_base / "data/frontenddeveloper/performance-history.md"
        }
        
        # Lazy loading flags
        self._services_initialized = False
        self._resources_loaded = False
        self._policy_engine_initialized = False
        self._message_bus_initialized = False
        
        # Basic initialization only
        logger.info(f"{self.agent_name} Agent geïnitialiseerd (lazy loading)")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced frontend development capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for FrontendDeveloper")
        except Exception as e:
            logger.warning(f"MCP initialization failed for FrontendDeveloper: {e}")
            self.mcp_enabled = False
    
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
    
    async def use_frontend_specific_mcp_tools(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use frontend-specific MCP tools for component enhancement."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Component analysis
            if "component_analysis" in self.mcp_config.custom_tools:
                analysis_result = await self.use_mcp_tool("code_analysis", {
                    "code": component_data.get("code", ""),
                    "language": "typescript",
                    "analysis_type": "quality"
                })
                if analysis_result:
                    enhanced_data["component_analysis"] = analysis_result
            
            # Accessibility check
            if "accessibility_check" in self.mcp_config.custom_tools:
                accessibility_result = await self.use_mcp_tool("quality_gate", {
                    "metrics": {
                        "accessibility_score": component_data.get("accessibility_score", 0),
                        "wcag_compliance": component_data.get("wcag_compliance", False)
                    },
                    "thresholds": {
                        "accessibility_score": 90,
                        "wcag_compliance": True
                    }
                })
                if accessibility_result:
                    enhanced_data["accessibility_check"] = accessibility_result
            
            # Documentation generation
            doc_result = await self.use_mcp_tool("documentation_generator", {
                "source": component_data.get("code", ""),
                "output_format": "markdown",
                "include_examples": True
            })
            if doc_result:
                enhanced_data["documentation"] = doc_result
            
            logger.info(f"Frontend-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in frontend-specific MCP tools: {e}")
        
        return enhanced_data
    
    def _ensure_message_bus_initialized(self):
        """Lazy initialize MessageBus only when needed."""
        if not hasattr(self, '_message_bus_initialized'):
            try:
                # Use dependency manager for safe import
                psutil = self.dependency_manager.safe_import('psutil')
                if psutil:
                    # Import MessageBus only when needed
                    from bmad.agents.core.message_bus import MessageBus
                    self.message_bus = MessageBus()
                    self._message_bus_initialized = True
                    logger.debug("MessageBus initialized with psutil support")
                else:
                    # Fallback without psutil
                    self.message_bus = None
                    self._message_bus_initialized = True
                    logger.debug("MessageBus initialized without psutil support")
            except Exception as e:
                logger.warning(f"MessageBus initialization failed: {e}")
                self.message_bus = None
                self._message_bus_initialized = True
    
    def _ensure_services_initialized(self):
        """Lazy initialize core services only when needed."""
        if not self._services_initialized:
            # Initialize core services
            self.performance_monitor = get_performance_monitor()
            self.policy_engine = get_advanced_policy_engine()
            self.sprite_library = get_sprite_library()
            
            # Register performance profile
            profile = AgentPerformanceProfile(
                agent_name=self.agent_name,
                thresholds={
                    MetricType.RESPONSE_TIME: {AlertLevel.WARNING: 2.0, AlertLevel.CRITICAL: 5.0},
                    MetricType.SUCCESS_RATE: {AlertLevel.WARNING: 95.0, AlertLevel.CRITICAL: 90.0},
                    MetricType.MEMORY_USAGE: {AlertLevel.WARNING: 512, AlertLevel.CRITICAL: 1024},
                    MetricType.CPU_USAGE: {AlertLevel.WARNING: 80, AlertLevel.CRITICAL: 95}
                }
            )
            self.performance_monitor.register_agent_profile(profile)
            
            self._services_initialized = True
            logger.debug(f"{self.agent_name} services geïnitialiseerd")
    
    def _ensure_resources_loaded(self):
        """Lazy load resources only when needed."""
        if not self._resources_loaded:
            self._load_component_history()
            self._load_performance_history()
            self._resources_loaded = True
            logger.debug(f"{self.agent_name} resources geladen")
    
    def _ensure_policy_engine_initialized(self):
        """Lazy initialize policy engine only when needed."""
        if not self._policy_engine_initialized:
            self._ensure_services_initialized()
            # Policy engine is already initialized in services
            self._policy_engine_initialized = True

    def validate_input(self, component_name: str, format_type: str = None):
        """Validate input parameters for component operations."""
        if not component_name or not isinstance(component_name, str):
            raise ValueError("Component name must be a non-empty string")
        if format_type and format_type not in ["md", "json"]:
            raise ValueError("Format type must be 'md' or 'json'")

    def _load_component_history(self):
        try:
            if self.data_paths["component-history"].exists():
                with open(self.data_paths["component-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.component_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load component history: {e}")

    def _save_component_history(self):
        try:
            self.data_paths["component-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["component-history"], "w") as f:
                f.write("# Component History\n\n")
                f.writelines(f"- {comp}\n" for comp in self.component_history[-50:])
        except Exception as e:
            logger.error(f"Could not save component history: {e}")

    def _load_performance_history(self):
        try:
            if self.data_paths["performance-history"].exists():
                with open(self.data_paths["performance-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.performance_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        try:
            self.data_paths["performance-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["performance-history"], "w") as f:
                f.write("# Performance History\n\n")
                f.writelines(f"- {perf}\n" for perf in self.performance_history[-50:])
        except Exception as e:
            logger.error(f"Could not save performance history: {e}")

    def show_help(self):
        help_text = """
FrontendDeveloper Agent Commands:
  help                    - Show this help message
  build-component [name]  - Build or update component
  build-shadcn-component  - Build Shadcn/ui component
  run-accessibility-check - Run accessibility check
  show-component-history  - Show component history
  show-performance        - Show performance metrics
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-component [format] - Export component (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "accessibility-checklist":
                path = self.template_paths["accessibility-checklist"]
            elif resource_type == "performance-report":
                path = self.template_paths["performance-report"]
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

    def show_component_history(self):
        if not self.component_history:
            print("No component history available.")
            return
        print("Component History:")
        print("=" * 50)
        for i, comp in enumerate(self.component_history[-10:], 1):
            print(f"{i}. {comp}")

    def show_performance(self):
        if not self.performance_history:
            print("No performance history available.")
            return
        print("Performance History:")
        print("=" * 50)
        for i, perf in enumerate(self.performance_history[-10:], 1):
            print(f"{i}. {perf}")

    async def build_shadcn_component(self, component_name: str = "Button") -> Dict[str, Any]:
        """Build a Shadcn/ui component with enhanced features and MCP integration."""
        # Validate input
        self.validate_input(component_name)
        
        logger.info(f"Building Shadcn component: {component_name}")

        # Ensure services are initialized
        self._ensure_services_initialized()
        
        start_time = time.time()

        # Simulate Shadcn component build with accessibility focus
        time.sleep(1)
        result = {
            "component": component_name,
            "type": "Shadcn/ui",
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
            "performance_score": 95,
            "timestamp": datetime.now().isoformat(),
            "agent": "FrontendDeveloperAgent"
        }

        # Try MCP-enhanced component building first
        if self.mcp_enabled and self.mcp_client:
            try:
                mcp_result = await self.use_mcp_tool("build_component", {
                    "component_name": component_name,
                    "framework": "shadcn/ui",
                    "include_accessibility": True,
                    "include_performance": True
                })
                
                if mcp_result:
                    logger.info("MCP-enhanced component building completed")
                    result.update(mcp_result)
                    result["mcp_enhanced"] = True
                else:
                    logger.warning("MCP component building failed, using local building")
            except Exception as e:
                logger.warning(f"MCP component building failed: {e}, using local building")
        
        # Use frontend-specific MCP tools for additional enhancement
        if self.mcp_enabled:
            try:
                frontend_enhanced = await self.use_frontend_specific_mcp_tools(result)
                if frontend_enhanced:
                    result["frontend_enhancements"] = frontend_enhanced
            except Exception as e:
                logger.warning(f"Frontend-specific MCP tools failed: {e}")

        # Add to component history
        comp_entry = f"{datetime.now().isoformat()}: Shadcn {component_name} component built with {result['accessibility_score']}% accessibility score"
        self.component_history.append(comp_entry)
        self._save_component_history()

        logger.info(f"Shadcn component build result: {result}")
        return result

    def build_component(self, component_name: str = "Button") -> Dict[str, Any]:
        # Validate input
        self.validate_input(component_name)
        
        logger.info(f"Building component: {component_name}")

        # Simuleer component bouw
        time.sleep(1)
        result = {
            "name": component_name,
            "type": "React/Next.js",
            "status": "created",
            "accessibility_score": 95,
            "performance_score": 88,
            "timestamp": datetime.now().isoformat(),
            "agent": "FrontendDeveloperAgent"
        }

        # Voeg aan historie toe
        comp_entry = f"{result['timestamp']}: {component_name} - Status: {result['status']}, Accessibility: {result['accessibility_score']}%"
        self.component_history.append(comp_entry)
        self._save_component_history()

        # Log performance metric
        self.performance_monitor._record_metric("FrontendDeveloper", MetricType.SUCCESS_RATE, result["accessibility_score"], "%")

        logger.info(f"Component build result: {result}")
        return result

    def run_accessibility_check(self, component_name: str = "Button") -> Dict[str, Any]:
        # Validate input
        self.validate_input(component_name)
        
        logger.info(f"Running accessibility check for: {component_name}")

        # Simuleer accessibility check
        time.sleep(1)
        result = {
            "component": component_name,
            "score": 95,
            "issues": [
                {"type": "contrast", "severity": "low", "description": "Button text contrast could be improved"},
                {"type": "alt-text", "severity": "medium", "description": "Missing alt text on image"}
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "FrontendDeveloperAgent"
        }

        # Log performance metric
        self.performance_monitor._record_metric("FrontendDeveloper", MetricType.SUCCESS_RATE, result["score"], "%")

        logger.info(f"Accessibility check result: {result}")
        return result

    def export_component(self, format_type: str = "md", component_data: Optional[Dict] = None):
        if not component_data:
            if self.component_history:
                component_name = self.component_history[-1].split(": ")[1].split(" - ")[0]
                component_data = self.build_component(component_name)
            else:
                component_data = self.build_component()

        # Validate format type
        if format_type not in ["md", "json"]:
            raise ValueError("Format type must be 'md' or 'json'")

        try:
            if format_type == "md":
                self._export_markdown(component_data)
            elif format_type == "json":
                self._export_json(component_data)
        except Exception as e:
            logger.error(f"Error exporting component: {e}")
            raise

    def _export_markdown(self, component_data: Dict):
        template_path = self.template_paths["component-export-md"]
        if template_path.exists():
            with open(template_path) as f:
                template = f.read()

            # Vul template
            content = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            content = content.replace("{{component_name}}", component_data["name"])
            content = content.replace("{{component_type}}", component_data["type"])
            content = content.replace("{{accessibility_score}}", str(component_data["accessibility_score"]))

            # Save to file
            output_file = f"component_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, "w") as f:
                f.write(content)
            print(f"Component export saved to: {output_file}")

    def _export_json(self, component_data: Dict):
        output_file = f"component_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(component_data, f, indent=2)

        print(f"Component export saved to: {output_file}")

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

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the FrontendDeveloper agent."""
        base_status = {
            "agent_name": self.agent_name,
            "component_history_count": len(self.component_history),
            "performance_history_count": len(self.performance_history),
            "last_component": self.component_history[-1] if self.component_history else None,
            "last_performance": self.performance_history[-1] if self.performance_history else None,
            "services_initialized": self._services_initialized,
            "resources_loaded": self._resources_loaded,
            "status": "active"
        }
        
        # Add dependency status if using MCP mixin
        if hasattr(self, 'get_dependency_status'):
            base_status["dependency_status"] = self.get_dependency_status()
        
        return base_status
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check dependency status and provide recommendations."""
        if hasattr(self, 'get_dependency_status'):
            return self.get_dependency_status()
        else:
            # Fallback for agents without MCP mixin
            return {
                "agent_name": self.agent_name,
                "missing_dependencies": [],
                "degraded_features": [],
                "dependency_warnings": [],
                "recommendations": [],
                "dependency_health": True,
                "note": "Dependency checking not available for this agent"
            }

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        try:
            logger.info("Starting collaboration example...")

            # Publish component build request
            publish("component_build_requested", {
                "agent": "FrontendDeveloperAgent",
                "component_name": "Button",
                "timestamp": datetime.now().isoformat()
            })

            # Build component
            component_result = self.build_component("Button")

            # Run accessibility check
            accessibility_result = self.run_accessibility_check("Button")

            # Publish completion
            publish("component_build_completed", component_result)
            publish("accessibility_check_completed", accessibility_result)

            # Notify via Slack
            try:
                send_slack_message(f"Component {component_result['name']} built successfully with {accessibility_result['score']}% accessibility score")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")
            
            print("Collaboration example completed successfully.")
        except Exception as e:
            logger.error(f"Collaboration example failed: {e}")
            print(f"❌ Error in collaboration: {e}")

    def handle_component_build_requested(self, event):
        logger.info(f"Component build requested: {event}")
        component_name = event.get("component_name", "Button")
        self.build_component(component_name)

    async def handle_component_build_completed(self, event):
        logger.info(f"Component build completed: {event}")

        # Evaluate policy
        try:
            allowed = await self.policy_engine.evaluate_policy("component_build", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Policy evaluation failed: {e}")

    def code_review(self, code_snippet: str) -> str:
        if not code_snippet or not isinstance(code_snippet, str):
            raise ValueError("Code snippet must be a non-empty string")
        
        try:
            prompt = f"Geef een korte code review van de volgende code:\n{code_snippet}"
            result = ask_openai(prompt)
            logger.info(f"[FrontendDeveloper][LLM Code Review]: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to perform code review: {e}")
            error_result = f"Error performing code review: {e}"
            logger.info(f"[FrontendDeveloper][LLM Code Review Error]: {error_result}")
            return error_result

    def bug_root_cause(self, error_log: str) -> str:
        if not error_log or not isinstance(error_log, str):
            raise ValueError("Error log must be a non-empty string")
        
        try:
            prompt = f"Analyseer deze foutmelding/log en geef een mogelijke oorzaak en oplossing:\n{error_log}"
            result = ask_openai(prompt)
            logger.info(f"[FrontendDeveloper][LLM Bug Analyse]: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to analyze bug root cause: {e}")
            error_result = f"Error analyzing bug root cause: {e}"
            logger.info(f"[FrontendDeveloper][LLM Bug Analyse Error]: {error_result}")
            return error_result

    def parse_figma_components(self, figma_file_id: str) -> Dict:
        try:
            client = FigmaClient()

            # Haal file info op
            file_data = client.get_file(figma_file_id)
            components_data = client.get_components(figma_file_id)

            logger.info(f"[FrontendDeveloper][Figma Parse] File: {file_data.get('name', 'Unknown')}")

            # Parse components naar abstract model
            components = []
            for component_id, component_info in components_data.get("meta", {}).get("components", {}).items():
                component = {
                    "id": component_id,
                    "name": component_info.get("name", ""),
                    "description": component_info.get("description", ""),
                    "key": component_info.get("key", ""),
                    "created_at": component_info.get("created_at", ""),
                    "updated_at": component_info.get("updated_at", "")
                }
                components.append(component)

            return {
                "file_name": file_data.get("name", ""),
                "file_id": figma_file_id,
                "components": components,
                "total_components": len(components)
            }

        except Exception as e:
            logger.error(f"[FrontendDeveloper][Figma Parse Error]: {e!s}")
            return {"error": str(e)}

    def generate_nextjs_component(self, component_data: Dict, component_name: str) -> str:
        try:
            prompt = f"""
            Genereer een Next.js component met Tailwind CSS voor het volgende Figma component:
            
            Component Naam: {component_name}
            Component Data: {json.dumps(component_data, indent=2)}
            
            Vereisten:
            - Gebruik Next.js functional component syntax
            - Gebruik Tailwind CSS voor styling
            - Maak het component responsive
            - Voeg TypeScript types toe
            - Zorg voor goede accessibility
            - Gebruik moderne React patterns (hooks, etc.)
            
            Genereer alleen de component code, geen uitleg.
            """

            result = ask_openai(prompt)
            logger.info(f"[FrontendDeveloper][Component Generation] Generated component: {component_name}")
            return result

        except Exception as e:
            logger.error(f"[FrontendDeveloper][Component Generation Error]: {e!s}")
            return f"// Error generating component: {e!s}"

    def generate_components_from_figma(self, figma_file_id: str, output_dir: str = "components") -> Dict:
        try:
            # Parse Figma components
            figma_data = self.parse_figma_components(figma_file_id)

            if "error" in figma_data:
                return figma_data

            generated_components = []

            # Genereer component voor elke Figma component
            for component in figma_data["components"]:
                component_name = component["name"].replace(" ", "").replace("-", "")
                component_code = self.generate_nextjs_component(component, component_name)

                generated_components.append({
                    "name": component_name,
                    "figma_id": component["id"],
                    "code": component_code,
                    "file_path": f"{output_dir}/{component_name}.tsx"
                })

            result = {
                "file_name": figma_data["file_name"],
                "file_id": figma_file_id,
                "generated_components": generated_components,
                "total_generated": len(generated_components)
            }

            logger.info(f"[FrontendDeveloper][Figma Codegen] Generated {len(generated_components)} components")
            return result

        except Exception as e:
            logger.error(f"[FrontendDeveloper][Figma Codegen Error]: {e!s}")
            return {"error": str(e)}

    async def run(self):
        """Run the FrontendDeveloper agent met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        def sync_handler(event):
            asyncio.run(self.handle_component_build_completed(event))

        subscribe("component_build_completed", sync_handler)
        subscribe("component_build_requested", self.handle_component_build_requested)

        logger.info("FrontendDeveloperAgent ready and listening for events...")
        self.collaborate_example()
        
        try:
            # Keep the agent running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("FrontendDeveloper agent stopped.")
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the FrontendDeveloper agent met MCP integration."""
        agent = cls()
        await agent.run()

def main():
    parser = argparse.ArgumentParser(description="FrontendDeveloper Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "build-component", "build-shadcn-component", "run-accessibility-check", "show-component-history",
                               "show-performance", "show-best-practices", "show-changelog", "export-component",
                               "test", "collaborate", "run", "initialize-mcp", "use-mcp-tool", "get-mcp-status", "use-frontend-mcp-tools", "check-dependencies"])
    parser.add_argument("--name", default="Button", help="Component name")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    parser.add_argument("--tool-name", help="MCP tool name")
    parser.add_argument("--parameters", help="MCP tool parameters (JSON string)")
    parser.add_argument("--component-data", help="Component data for frontend MCP tools (JSON string)")

    args = parser.parse_args()

    agent = FrontendDeveloperAgent()
    
    # Show dependency warnings on startup
    if hasattr(agent, 'get_dependency_status'):
        dep_status = agent.get_dependency_status()
        if dep_status.get('missing_dependencies'):
            print(f"[DEPENDENCY WARNING] {len(dep_status['missing_dependencies'])} dependencies missing")
            for dep in dep_status['missing_dependencies']:
                print(f"  - {dep}: {dep_status['degraded_features'][dep_status['missing_dependencies'].index(dep)]}")
            print("Use 'check-dependencies' command for detailed information and recommendations.")

    if args.command == "help":
        agent.show_help()
    elif args.command == "build-component":
        agent.build_component(args.name)
    elif args.command == "build-shadcn-component":
        asyncio.run(agent.build_shadcn_component(args.name))
    elif args.command == "run-accessibility-check":
        agent.run_accessibility_check(args.name)
    elif args.command == "show-component-history":
        agent.show_component_history()
    elif args.command == "show-performance":
        agent.show_performance()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-component":
        agent.export_component(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        agent.collaborate_example()
    elif args.command == "run":
        asyncio.run(agent.run())
    elif args.command == "initialize-mcp":
        success = asyncio.run(agent.initialize_mcp())
        print(f"MCP initialization: {'Success' if success else 'Failed'}")
    elif args.command == "use-mcp-tool":
        if not args.tool_name:
            print("Error: --tool-name is required for use-mcp-tool command")
            return
        parameters = json.loads(args.parameters) if args.parameters else {}
        result = asyncio.run(agent.use_mcp_tool(args.tool_name, parameters))
        print(f"MCP tool result: {result}")
    elif args.command == "get-mcp-status":
        status = agent.get_status()
        print(json.dumps(status, indent=2, default=str))
    elif args.command == "use-frontend-mcp-tools":
        if not args.component_data:
            print("Error: --component-data is required for use-frontend-mcp-tools command")
            return
        component_data = json.loads(args.component_data)
        result = asyncio.run(agent.use_frontend_specific_mcp_tools(component_data))
        print(f"Frontend MCP tools result: {result}")
    elif args.command == "check-dependencies":
        status = agent.check_dependencies()
        print(json.dumps(status, indent=2, default=str))

if __name__ == "__main__":
    main()
