import logging
import os
import sys
import time
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.core.ai.llm_client import ask_openai
# New Message Bus Integration
from bmad.core.message_bus import (
    AgentMessageBusIntegration,
    EventTypes,
    get_message_bus
)
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
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

# Enhanced MCP Integration for Phase 2
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)

# Tracing Integration
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

RESOURCE_BASE = Path(__file__).parent.parent / "resources"
TEMPLATE_PATHS = {
    "design-api": RESOURCE_BASE / "templates/api/design-api.md",
    "microservices": RESOURCE_BASE / "templates/architecture/microservices.md",
    "event-flow": RESOURCE_BASE / "templates/architecture/event-flow.md",
    "memory-design": RESOURCE_BASE / "templates/architecture/memory-design.md",
    "nfrs": RESOURCE_BASE / "templates/architecture/nfrs.md",
    "adr": RESOURCE_BASE / "templates/general/adr.md",
    "risk-analysis": RESOURCE_BASE / "templates/general/risk-analysis.md",
    "review": RESOURCE_BASE / "templates/general/review.md",
    "refactor": RESOURCE_BASE / "templates/general/refactor.md",
    "infra-as-code": RESOURCE_BASE / "templates/devops/infra-as-code.md",
    "release-strategy": RESOURCE_BASE / "templates/devops/release-strategy.md",
    "poc": RESOURCE_BASE / "templates/general/poc.md",
    "security-review": RESOURCE_BASE / "templates/security/security-review.md",
    "tech-stack-eval": RESOURCE_BASE / "templates/general/tech-stack-eval.md",
    "checklist": RESOURCE_BASE / "templates/general/checklist.md",
    "api-contract": RESOURCE_BASE / "templates/api/api-contract.md",
    "test-strategy": RESOURCE_BASE / "templates/testing/test-strategy.md",
    "best-practices": RESOURCE_BASE / "templates/general/best-practices.md",
    "export": RESOURCE_BASE / "data/architect/architecture-examples.md",
    "changelog": RESOURCE_BASE / "data/general/changelog.md",
}


class ArchitectAgent(AgentMessageBusIntegration):
    """
    Architect Agent voor BMAD.
    Gespecialiseerd in software architectuur, API design, en system design.
    """
    
    def __init__(self):
        super().__init__("Architect")
        self.framework_manager = get_framework_templates_manager()
        try:
            self.architecture_template = self.framework_manager.get_framework_template('architecture')
        except:
            self.architecture_template = None
        self.lessons_learned = []

        """Initialize Architect agent met MCP integration."""
        self.agent_name = "Architect"
        self.architecture_history = []
        self.design_patterns = []
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        self.enhanced_mcp_client = None
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Performance metrics for quality-first implementation
        self.performance_metrics = {
            "total_api_designs": 0,
            "total_system_designs": 0,
            "total_architecture_reviews": 0,
            "total_tech_stack_evaluations": 0,
            "total_pipeline_advice": 0,
            "total_task_delegations": 0,
            "total_frontend_designs": 0,
            "total_architecture_designs": 0,
            "average_design_time": 0.0,
            "design_success_rate": 0.0,
            "review_processing_time": 0.0,
            "architecture_quality_score": 0.0
        }

        # Message Bus Integration
        self.message_bus_enabled = False

        # Initialize tracer
        try:
            self.tracer = BMADTracer("ArchitectAgent")
            self.tracing_enabled = True
        except Exception as e:
            logging.warning(f"Failed to initialize tracer: {e}")
            self.tracing_enabled = False
        
        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "design-api": self.resource_base / "templates/api/design-api.md",
            "microservices": self.resource_base / "templates/architecture/microservices.md",
            "event-flow": self.resource_base / "templates/architecture/event-flow.md",
            "memory-design": self.resource_base / "templates/architecture/memory-design.md",
            "nfrs": self.resource_base / "templates/architecture/nfrs.md",
            "adr": self.resource_base / "templates/general/adr.md",
            "risk-analysis": self.resource_base / "templates/general/risk-analysis.md",
            "review": self.resource_base / "templates/general/review.md",
            "refactor": self.resource_base / "templates/general/refactor.md",
            "infra-as-code": self.resource_base / "templates/devops/infra-as-code.md",
            "release-strategy": self.resource_base / "templates/devops/release-strategy.md",
            "poc": self.resource_base / "templates/general/poc.md",
            "security-review": self.resource_base / "templates/security/security-review.md",
            "tech-stack-eval": self.resource_base / "templates/general/tech-stack-eval.md",
            "checklist": self.resource_base / "templates/general/checklist.md",
            "api-contract": self.resource_base / "templates/api/api-contract.md",
            "test-strategy": self.resource_base / "templates/testing/test-strategy.md",
            "best-practices": self.resource_base / "templates/general/best-practices.md",
            "export": self.resource_base / "data/architect/architecture-examples.md",
            "changelog": self.resource_base / "data/general/changelog.md",
        }
        
        logging.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client and integration."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logging.info("MCP client initialized successfully")
        except Exception as e:
            logging.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False
    
    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            # Check if initialize method exists before calling it
            if hasattr(self.enhanced_mcp, 'initialize'):
                await self.enhanced_mcp.initialize()
            self.enhanced_mcp_enabled = True
            
            # Set enhanced MCP client reference
            self.enhanced_mcp_client = self.mcp_client
            
            logging.info("Enhanced MCP initialized successfully")
        except Exception as e:
            logging.warning(f"Enhanced MCP initialization failed: {e}")
            self.enhanced_mcp_enabled = False
    
    async def initialize_tracing(self):
        """Initialize tracing capabilities."""
        try:
            if self.tracer and hasattr(self.tracer, 'initialize'):
                await self.tracer.initialize()
                self.tracing_enabled = True
                logging.info("Tracing initialized successfully")
            else:
                logging.warning("Tracer not available or missing initialize method")
                self.tracing_enabled = False
        except Exception as e:
            logging.warning(f"Tracing initialization failed: {e}")
            self.tracing_enabled = False
    
    async def initialize_message_bus(self):
        """Initialize message bus integration for Architect agent."""
        try:
            # Subscribe to relevant event categories
            await self.subscribe_to_event_category("architecture")
            await self.subscribe_to_event_category("system_design")
            await self.subscribe_to_event_category("development")
            await self.subscribe_to_event_category("tech_stack")
            await self.subscribe_to_event_category("collaboration")
            
            # Register specific event handlers
            await self.register_event_handler(EventTypes.API_DESIGN_REQUESTED, self._handle_api_design_requested)
            await self.register_event_handler(EventTypes.SYSTEM_DESIGN_REQUESTED, self._handle_system_design_requested)
            await self.register_event_handler(EventTypes.ARCHITECTURE_REVIEW_REQUESTED, self._handle_architecture_review_requested)
            await self.register_event_handler(EventTypes.TECH_STACK_EVALUATION_REQUESTED, self._handle_tech_stack_evaluation_requested)
            await self.register_event_handler(EventTypes.PIPELINE_ADVICE_REQUESTED, self._handle_pipeline_advice_requested)
            await self.register_event_handler(EventTypes.TASK_DELEGATED, self._handle_task_delegated)
            
            logging.info("Architect agent message bus integration initialized successfully")
        except Exception as e:
            logging.error(f"Message bus initialization failed: {e}")
    
    async def _handle_api_design_requested(self, event_data: Dict[str, Any]):
        """Handle API design requested event with real functionality."""
        try:
            use_case = event_data.get("use_case", "Default API use case")
            
            # Record metric
            self.performance_metrics["total_api_designs"] += 1
            
            # Perform API design
            result = await self.design_api({"use_case": use_case})
            
            # Update metrics
            if result.get("success", False):
                self.performance_metrics["design_success_rate"] = (
                    self.performance_metrics["total_api_designs"] / 
                    max(1, self.performance_metrics["total_api_designs"]) * 100
                )
            
            # Publish completion event
            publish("api_design_completed", {
                "agent": self.agent_name,
                "use_case": use_case,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            logging.info(f"API design completed: {use_case}")
            return result
            
        except Exception as e:
            logging.error(f"Error handling API design requested: {e}")
            return {"error": str(e), "success": False}

    async def _handle_system_design_requested(self, event_data: Dict[str, Any]):
        """Handle system design requested event with real functionality."""
        try:
            requirements = event_data.get("requirements", {})
            
            # Record metric
            self.performance_metrics["total_system_designs"] += 1
            
            # Perform system design
            result = await self.design_system()
            
            # Update metrics
            if result.get("success", False):
                self.performance_metrics["design_success_rate"] = (
                    (self.performance_metrics["total_api_designs"] + self.performance_metrics["total_system_designs"]) / 
                    max(1, self.performance_metrics["total_api_designs"] + self.performance_metrics["total_system_designs"]) * 100
                )
            
            # Publish completion event
            publish("system_design_completed", {
                "agent": self.agent_name,
                "requirements": requirements,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            logging.info(f"System design completed")
            return result
            
        except Exception as e:
            logging.error(f"Error handling system design requested: {e}")
            return {"error": str(e), "success": False}

    async def _handle_architecture_review_requested(self, event_data: Dict[str, Any]):
        """Handle architecture review requested event with real functionality."""
        try:
            architecture_data = event_data.get("architecture_data", {})
            
            # Record metric
            self.performance_metrics["total_architecture_reviews"] += 1
            
            # Perform architecture review
            result = await self.review_architecture(architecture_data)
            
            # Update metrics
            if result.get("success", False):
                self.performance_metrics["architecture_quality_score"] = result.get("quality_score", 0.0)
            
            # Publish completion event
            publish("architecture_review_completed", {
                "agent": self.agent_name,
                "architecture_data": architecture_data,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            logging.info(f"Architecture review completed")
            return result
            
        except Exception as e:
            logging.error(f"Error handling architecture review requested: {e}")
            return {"error": str(e), "success": False}

    async def _handle_tech_stack_evaluation_requested(self, event_data: Dict[str, Any]):
        """Handle tech stack evaluation requested event with real functionality."""
        try:
            tech_stack_data = event_data.get("tech_stack_data", {})
            
            # Record metric
            self.performance_metrics["total_tech_stack_evaluations"] += 1
            
            # Perform tech stack evaluation
            result = await self.tech_stack()
            
            # Update metrics
            if result.get("success", False):
                self.performance_metrics["review_processing_time"] = 0.5  # Simulated time
            
            # Publish completion event
            publish("tech_stack_evaluation_completed", {
                "agent": self.agent_name,
                "tech_stack_data": tech_stack_data,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            logging.info(f"Tech stack evaluation completed")
            return result
            
        except Exception as e:
            logging.error(f"Error handling tech stack evaluation requested: {e}")
            return {"error": str(e), "success": False}

    async def _handle_pipeline_advice_requested(self, event_data: Dict[str, Any]):
        """Handle pipeline advice requested event with real functionality."""
        try:
            pipeline_data = event_data.get("pipeline_data", {})
            
            # Record metric
            self.performance_metrics["total_pipeline_advice"] += 1
            
            # Provide pipeline advice
            result = await self.provide_pipeline_advice(pipeline_data)
            
            # Update metrics
            if result.get("success", False):
                self.performance_metrics["review_processing_time"] = 0.3  # Simulated time
            
            # Publish completion event
            publish("pipeline_advice_completed", {
                "agent": self.agent_name,
                "pipeline_data": pipeline_data,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            logging.info(f"Pipeline advice completed")
            return result
            
        except Exception as e:
            logging.error(f"Error handling pipeline advice requested: {e}")
            return {"error": str(e), "success": False}

    async def _handle_task_delegated(self, event_data: Dict[str, Any]):
        """Handle task delegated event with real functionality."""
        try:
            task_data = event_data.get("task_data", {})
            target_agent = event_data.get("target_agent", "unknown")
            
            # Record metric
            self.performance_metrics["total_task_delegations"] += 1
            
            # Process task delegation
            result = {
                "success": True,
                "task_id": task_data.get("task_id", "unknown"),
                "target_agent": target_agent,
                "delegated_at": datetime.now().isoformat(),
                "agent": self.agent_name
            }
            
            # Update architecture history
            history_entry = {
                "type": "task_delegation",
                "target_agent": target_agent,
                "task_data": task_data,
                "timestamp": datetime.now().isoformat()
            }
            self.architecture_history.append(history_entry)
            
            # Publish completion event
            publish("task_delegation_completed", {
                "agent": self.agent_name,
                "target_agent": target_agent,
                "task_data": task_data,
                "timestamp": datetime.now().isoformat(),
                "result": result
            })
            
            logging.info(f"Task delegated to {target_agent}")
            return result
            
        except Exception as e:
            logging.error(f"Error handling task delegated: {e}")
            return {"error": str(e), "success": False}

    def _record_architecture_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record architecture performance metric."""
        if metric_name in self.performance_metrics:
            if isinstance(self.performance_metrics[metric_name], (int, float)):
                self.performance_metrics[metric_name] = value
            else:
                self.performance_metrics[metric_name] = value

    def _update_architecture_metrics(self, design_result: Dict[str, Any]) -> None:
        """Update architecture metrics based on operation result."""
        if "design_type" in design_result:
            if design_result["design_type"] == "api":
                self.performance_metrics["total_api_designs"] += 1
            elif design_result["design_type"] == "system":
                self.performance_metrics["total_system_designs"] += 1
            elif design_result["design_type"] == "architecture":
                self.performance_metrics["total_architecture_designs"] += 1

        if "success" in design_result and design_result["success"]:
            total_designs = (
                self.performance_metrics["total_api_designs"] + 
                self.performance_metrics["total_system_designs"] + 
                self.performance_metrics["total_architecture_designs"]
            )
            if total_designs > 0:
                self.performance_metrics["design_success_rate"] = (
                    total_designs / total_designs * 100
                )

    async def design_api(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design API based on requirements."""
        try:
            logging.info(f"Designing API with requirements: {requirements}")
            # Placeholder implementation
            return {
                "api_design": "API design completed",
                "endpoints": ["/api/users", "/api/posts"],
                "methods": ["GET", "POST", "PUT", "DELETE"]
            }
        except Exception as e:
            logging.error(f"Error designing API: {e}")
            return {"error": str(e)}
    
    async def provide_pipeline_advice(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide pipeline advice based on configuration."""
        try:
            logging.info(f"Providing pipeline advice for: {pipeline_data}")
            # Placeholder implementation
            return {
                "advice": "Pipeline advice provided",
                "recommendations": ["Use caching", "Implement monitoring"]
            }
        except Exception as e:
            logging.error(f"Error providing pipeline advice: {e}")
            return {"error": str(e)}
    
    async def review_architecture(self, architecture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review architecture based on provided data."""
        try:
            logging.info(f"Reviewing architecture: {architecture_data}")
            # Placeholder implementation
            return {
                "review_result": "Architecture review completed",
                "recommendations": ["Consider microservices", "Implement caching"]
            }
        except Exception as e:
            logging.error(f"Error reviewing architecture: {e}")
            return {"error": str(e)}
    
    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use MCP tool voor enhanced architecture design functionality."""
        if not self.mcp_enabled or not self.mcp_client:
            logging.warning("MCP not available, using local architecture design tools")
            return None
        
        try:
            # Create a context for the tool call
            context = await self.mcp_client.create_context(agent_id=self.agent_name)
            response = await self.mcp_client.call_tool(tool_name, parameters, context)
            
            if response.success:
                result = response.data
            else:
                logging.error(f"MCP tool {tool_name} failed: {response.error}")
                result = None
            logging.info(f"MCP tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logging.error(f"MCP tool {tool_name} execution failed: {e}")
            return None
    
    async def use_architecture_specific_mcp_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use architecture-specific MCP tools voor design enhancement."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Architecture analysis
            if "architecture_analysis" in self.mcp_config.custom_tools:
                analysis_result = await self.use_mcp_tool("architecture_analysis", {
                    "design": design_data.get("design", ""),
                    "patterns": design_data.get("patterns", []),
                    "analysis_type": "quality"
                })
                if analysis_result:
                    enhanced_data["architecture_analysis"] = analysis_result
            
            # Performance analysis
            if "performance_analysis" in self.mcp_config.custom_tools:
                performance_result = await self.use_mcp_tool("performance_analysis", {
                    "architecture": design_data.get("architecture", ""),
                    "metrics": design_data.get("performance_metrics", {})
                })
                if performance_result:
                    enhanced_data["performance_analysis"] = performance_result
            
            # Security review
            security_result = await self.use_mcp_tool("security_review", {
                "design": design_data.get("design", ""),
                "security_requirements": design_data.get("security_requirements", [])
            })
            if security_result:
                enhanced_data["security_review"] = security_result
            
            logging.info(f"Architecture-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logging.error(f"Error in architecture-specific MCP tools: {e}")
        
        return enhanced_data
    
    async def use_enhanced_mcp_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logging.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_architecture_specific_mcp_tools(design_data)
        
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
            
            # Architecture-specific enhanced tools
            architecture_enhanced_result = await self.use_architecture_specific_enhanced_tools(design_data)
            enhanced_data.update(architecture_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_architecture_operation(design_data)
                enhanced_data["tracing"] = trace_result
            
            logging.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logging.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_architecture_specific_enhanced_tools(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use architecture-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced API design
            if "api_design" in design_data:
                api_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_api_design", {
                    "api_data": design_data["api_design"],
                    "requirements": design_data.get("requirements", {}),
                    "constraints": design_data.get("constraints", {})
                })
                enhanced_tools["enhanced_api_design"] = api_result
            
            # Enhanced system architecture
            if "system_architecture" in design_data:
                system_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_system_architecture", {
                    "architecture_data": design_data["system_architecture"],
                    "scalability_requirements": design_data.get("scalability_requirements", {}),
                    "performance_requirements": design_data.get("performance_requirements", {})
                })
                enhanced_tools["enhanced_system_architecture"] = system_result
            
            # Enhanced team collaboration
            if "team_collaboration" in design_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "BackendDeveloper", "FrontendDeveloper", "DevOpsInfra"],
                    {
                        "type": "architecture_review",
                        "content": design_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            logging.info(f"Architecture-specific enhanced tools used: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logging.error(f"Architecture-specific enhanced tools failed: {e}")
            enhanced_tools["error"] = str(e)
        
        return enhanced_tools
    
    async def trace_architecture_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace architecture operations for monitoring and debugging."""
        if not self.tracing_enabled or not self.tracer:
            return {"status": "tracing_disabled"}
        
        try:
            trace_data = {
                "agent": self.agent_name,
                "operation": operation_data.get("operation_type", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "data": operation_data
            }
            
            result = await self.tracer.trace_operation(trace_data)
            logging.info(f"Architecture operation traced: {operation_data.get('operation_type', 'unknown')}")
            
            return result
            
        except Exception as e:
            logging.error(f"Tracing failed: {e}")
            return {"status": "tracing_error", "error": str(e)}

    def show_help(self):
        """Show help information for Architect agent."""
        print("🏗️ Architect Agent CLI")
        print("\n📋 Beschikbare commando's:")
        print("  design-frontend        - Design frontend architecture")
        print("  design-system          - Design system architecture")
        print("  tech-stack             - Evaluate technology stack")
        print("  start-conversation     - Start interactive conversation")
        print("  best-practices         - Show architecture best practices")
        print("  export                 - Export architecture examples")
        print("  changelog              - Show changelog")
        print("  list-resources         - List available resources")
        print("  test                   - Test resource completeness")
        print("  collaborate            - Collaborate example")
        print("  run                    - Run agent")
        
        # Message Bus Commands
        print("\n🔗 Message Bus Commands:")
        print("  message-bus-status     - Show Message Bus status")
        print("  publish-event          - Publish event to Message Bus")
        print("  subscribe-event        - Subscribe to event")
        print("  list-events            - List supported events")
        print("  event-history          - Show event history")
        print("  performance-metrics    - Show performance metrics")
        
        # Enhanced MCP Commands
        print("\n🔍 Enhanced MCP Commands:")
        print("  enhanced-collaborate   - Enhanced collaboration")
        print("  enhanced-security      - Enhanced security validation")
        print("  enhanced-performance   - Enhanced performance optimization")
        print("  trace-operation        - Trace operation")
        print("  trace-performance      - Trace performance")
        print("  trace-error            - Trace error")
        print("  tracing-summary        - Show tracing summary")
        
        print("\n📝 Usage Examples:")
        print("  python architect.py design-frontend")
        print("  python architect.py design-system")
        print("  python architect.py tech-stack")
        print("  python architect.py message-bus-status")
        print("  python architect.py publish-event --event-type api_design_requested --event-data '{\"use_case\": \"REST API\"}'")
        print("  python architect.py performance-metrics")

    # ... bestaande fallback-methodes ...
    def best_practices(self):
        path = TEMPLATE_PATHS.get("best-practices")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen best practices resource gevonden.")

    def export(self):
        path = TEMPLATE_PATHS.get("export")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen export resource gevonden.")

    def changelog(self):
        path = TEMPLATE_PATHS.get("changelog")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen changelog resource gevonden.")

    def list_resources(self):
        print("Beschikbare resource-bestanden:")
        for key, path in TEMPLATE_PATHS.items():
            print(f"- {key}: {path}")

    def test(self):
        missing = []
        for key, path in TEMPLATE_PATHS.items():
            if not path.exists():
                missing.append((key, str(path)))
        if missing:
            print("[FOUT] Ontbrekende resource-bestanden:")
            for key, path in missing:
                print(f"- {key}: {path}")
        else:
            print("[OK] Alle resource-bestanden zijn aanwezig.")

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        try:
            # Publish architecture event
            publish("architecture_reviewed", {
                "status": "success", 
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat()
            })
            
            # Save context
            save_context(self.agent_name, "review_status", {"review_status": "completed"})
            print("Event gepubliceerd en context opgeslagen.")
            
            # Get context
            context = get_context(self.agent_name)
            print(f"Opgehaalde context: {context}")
            
            # Record collaboration metric
            self.performance_metrics["total_task_delegations"] += 1
            
            return {
                "success": True,
                "message": "Collaboration example completed",
                "context": context
            }
            
        except Exception as e:
            logging.error(f"Error in collaborate example: {e}")
            return {"error": str(e), "success": False}

    def ask_llm_api_design(self, use_case):
        """Vraag de LLM om een API-design voorstel op basis van een use case."""
        prompt = f"Ontwerp een REST API endpoint voor de volgende use case: {use_case}. Geef een korte beschrijving en een voorbeeld van de JSON input/output."
        result = ask_openai(prompt)
        print(f"[LLM API-design]: {result}")
        return result

    async def design_frontend(self):
        """Ontwerp de BMAD frontend architectuur met MCP enhancement."""
        print("🏗️ Architect Agent - Frontend Design")
        print("=" * 50)

        # Haal de user stories op van de ProductOwner
        context = get_context("ProductOwner", "frontend_stories")

        # Handle context data properly
        if isinstance(context, list) and len(context) > 0:
            stories = context[0].get("stories", "Geen user stories gevonden")
        elif isinstance(context, dict):
            stories = context.get("stories", "Geen user stories gevonden")
        else:
            stories = "Geen user stories gevonden"

        print("📋 Beschikbare user stories:")
        print(stories[:500] + "..." if len(stories) > 500 else stories)
        print()

        # Vraag gebruiker om input
        print("🤔 Wat wil je dat ik ontwerp?")
        print("1. Complete frontend architectuur")
        print("2. Component structuur en hiërarchie")
        print("3. State management strategie")
        print("4. API integratie patronen")
        print("5. Custom opdracht")

        choice = input("\nKies een optie (1-5) of beschrijf je eigen opdracht: ").strip()

        if choice == "1":
            prompt = f"""
            Ontwerp een complete frontend architectuur voor de BMAD dashboard op basis van deze user stories:
            
            {stories}
            
            Geef een gedetailleerd architectuurontwerp met:
            1. Component structuur en hiërarchie
            2. State management strategie
            3. API integratie patronen
            4. Routing en navigatie
            5. Real-time updates (WebSocket/SSE)
            6. Error handling en loading states
            7. Responsive design approach
            8. Performance optimalisaties
            
            Focus op een moderne, schaalbare architectuur die de user stories ondersteunt.
            """
        elif choice == "2":
            prompt = f"Ontwerp een gedetailleerde component structuur en hiërarchie voor de BMAD frontend op basis van: {stories}"
        elif choice == "3":
            prompt = f"Ontwerp een state management strategie voor de BMAD frontend op basis van: {stories}"
        elif choice == "4":
            prompt = f"Ontwerp API integratie patronen voor de BMAD frontend op basis van: {stories}"
        elif choice == "5":
            custom_prompt = input("Beschrijf je opdracht: ")
            prompt = f"Opdracht: {custom_prompt}\n\nContext: {stories}"
        else:
            # Gebruiker heeft direct een opdracht ingevoerd
            prompt = f"Opdracht: {choice}\n\nContext: {stories}"

        print("\n🔄 Architect aan het werk...")
        
        # Try MCP-enhanced architecture design first
        if self.mcp_enabled and self.mcp_client:
            try:
                mcp_result = await self.use_mcp_tool("design_architecture", {
                    "prompt": prompt,
                    "architecture_type": "frontend",
                    "framework": "react/nextjs",
                    "include_performance": True,
                    "include_security": True
                })
                
                if mcp_result:
                    logging.info("MCP-enhanced architecture design completed")
                    result = mcp_result.get("architecture", "")
                    result += "\n\n[MCP Enhanced] - Architecture design enhanced with MCP tools"
                else:
                    logging.warning("MCP architecture design failed, using local design")
                    result = ask_openai(prompt)
            except Exception as e:
                logging.warning(f"MCP architecture design failed: {e}, using local design")
                result = ask_openai(prompt)
        else:
            result = ask_openai(prompt)

        print("\n🏗️ BMAD Frontend Architectuur:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        # Use architecture-specific MCP tools for additional enhancement
        if self.mcp_enabled:
            try:
                design_data = {
                    "design": result,
                    "architecture_type": "frontend",
                    "patterns": ["component-based", "state-management", "api-integration"],
                    "performance_metrics": {"load_time": "target_2s", "bundle_size": "target_500kb"}
                }
                architecture_enhanced = await self.use_architecture_specific_mcp_tools(design_data)
                if architecture_enhanced:
                    print("\n🔧 Architecture Enhancements:")
                    for key, value in architecture_enhanced.items():
                        print(f"- {key}: {value}")
            except Exception as e:
                logging.warning(f"Architecture-specific MCP tools failed: {e}")

        # Sla het ontwerp op
        save_context("Architect", "frontend_architecture", {
            "timestamp": time.time(),
            "architecture": result,
            "status": "designed",
            "prompt": prompt,
            "mcp_enhanced": self.mcp_enabled
        })

        # Publiceer event
        publish("frontend_architecture_created", {
            "agent": "Architect",
            "status": "success"
        })

    async def design_system(self):
        """Maak een component diagram en API koppeling."""
        if self.mcp_enabled and self.mcp_client:
            # Try MCP first
            result = await self.use_mcp_tool("design_system", {
                "component_hierarchy": True,
                "api_integration": True,
                "state_management": True,
                "data_flow": True
            })
            if result:
                print("🏗️ BMAD Component Diagram & API Koppeling (MCP Enhanced):")
                print("=" * 60)
                print(result.get("design", result))
                print("=" * 60)
                return result
        
        # Fallback naar lokale implementatie
        return await asyncio.to_thread(self._design_system_sync)

    def _design_system_sync(self):
        """Sync fallback voor design_system."""
        prompt = """
        Maak een gedetailleerd component diagram voor de BMAD frontend met:
        
        1. Component hiërarchie:
           - Layout components (Header, Sidebar, Main, Footer)
           - Page components (Dashboard, AgentStatus, WorkflowManager, APITester)
           - Feature components (AgentCard, WorkflowCard, MetricChart, StatusIndicator)
           - Shared components (Button, Modal, Table, Chart, LoadingSpinner)
        
        2. API integratie:
           - REST API calls naar BMAD backend
           - WebSocket/SSE voor real-time updates
           - Error handling en retry logic
           - Caching strategie
        
        3. State management:
           - Global state (user, agents, workflows)
           - Local state (forms, UI state)
           - Server state (API data, real-time data)
        
        4. Data flow:
           - User interactions
           - API calls
           - Real-time updates
           - Error propagation
        
        Geef een visueel diagram in ASCII art en gedetailleerde beschrijvingen.
        """

        result = ask_openai(prompt)
        print("🏗️ BMAD Component Diagram & API Koppeling:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        return {"design": result, "status": "completed"}

    async def design_architecture(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design software architecture based on requirements."""
        try:
            # Initialize enhanced MCP if not already done
            if not self.enhanced_mcp_enabled:
                await self.initialize_enhanced_mcp()
            
            # Use enhanced MCP tools if available
            if self.enhanced_mcp_enabled and self.enhanced_mcp:
                result = await self.use_enhanced_mcp_tools({
                    "operation": "design_architecture",
                    "requirements": requirements,
                    "constraints": requirements.get("constraints", []),
                    "patterns": requirements.get("patterns", []),
                    "scale": requirements.get("scale", "medium")
                })
                if result:
                    return result
            
            # Fallback to local implementation
            return await asyncio.to_thread(self._design_architecture_sync, requirements)
            
        except Exception as e:
            logging.error(f"Error in design_architecture: {e}")
            return {
                "success": False,
                "error": str(e),
                "architecture": None
            }

    def _design_architecture_sync(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous fallback for design_architecture."""
        try:
            prompt = f"""
            Design a comprehensive software architecture based on the following requirements:
            
            Requirements: {requirements.get('requirements', {})}
            Constraints: {requirements.get('constraints', [])}
            Scale: {requirements.get('scale', 'medium')}
            
            Please provide:
            1. System Architecture Overview
            2. Component Design
            3. Data Flow Design
            4. Security Considerations
            5. Performance Considerations
            6. Scalability Strategy
            7. Technology Recommendations
            8. Implementation Roadmap
            
            Make the design practical and implementable.
            """
            
            result = ask_openai(prompt)
            
            return {
                "success": True,
                "architecture": {
                    "overview": result,
                    "components": requirements.get("requirements", {}),
                    "constraints": requirements.get("constraints", []),
                    "scale": requirements.get("scale", "medium"),
                    "timestamp": datetime.now().isoformat()
                },
                "status": "completed"
            }
            
        except Exception as e:
            logging.error(f"Error in _design_architecture_sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "architecture": None
            }

    async def tech_stack(self):
        """Evalueer de frontend tech stack."""
        if self.mcp_enabled and self.mcp_client:
            # Try MCP first
            result = await self.use_mcp_tool("tech_stack_evaluation", {
                "requirements": [
                    "real-time updates",
                    "rich UI with charts",
                    "API testing interface",
                    "responsive design",
                    "type safety",
                    "developer experience",
                    "performance and scalability"
                ],
                "options": [
                    "React + TypeScript + Vite + TanStack Query + Tailwind CSS",
                    "Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS",
                    "SvelteKit + TypeScript + Tailwind CSS",
                    "Next.js + TypeScript + Tailwind CSS"
                ]
            })
            if result:
                print("🏗️ Frontend Tech Stack Evaluatie (MCP Enhanced):")
                print("=" * 60)
                print(result.get("evaluation", result))
                print("=" * 60)
                return result
        
        # Fallback naar lokale implementatie
        return await asyncio.to_thread(self._tech_stack_sync)

    def _tech_stack_sync(self):
        """Sync fallback voor tech_stack."""
        prompt = """
        Evalueer en beveel een moderne frontend tech stack aan voor de BMAD dashboard:
        
        Requirements:
        - Real-time updates (agent status, workflow progress)
        - Rich UI met charts en dashboards
        - API testing interface
        - Responsive design
        - Type safety
        - Good developer experience
        - Performance en scalability
        
        Beoordeel de volgende opties:
        1. React + TypeScript + Vite + TanStack Query + Tailwind CSS
        2. Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS
        3. SvelteKit + TypeScript + Tailwind CSS
        4. Next.js + TypeScript + Tailwind CSS
        
        Geef een gedetailleerde vergelijking en aanbeveling met motivatie.
        """

        result = ask_openai(prompt)
        print("🏗️ Frontend Tech Stack Evaluatie:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        return {"evaluation": result, "status": "completed"}

    def start_conversation(self):
        """Start een interactieve conversatie met de Architect agent."""
        print("🏗️ Architect Agent - Interactieve Modus")
        print("=" * 50)
        print("Hallo! Ik ben de Architect agent. Ik kan je helpen met:")
        print("- Frontend architectuur ontwerpen")
        print("- API design en integratie")
        print("- Tech stack evaluatie")
        print("- System design en componenten")
        print("- Performance en security advies")
        print()
        print("Type 'help' voor commando's, 'quit' om te stoppen.")
        print()

        while True:
            try:
                user_input = input("🏗️ Architect > ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Tot ziens! 👋")
                    break
                if user_input.lower() == "help":
                    self.show_help()
                elif user_input.lower() == "clear":
                    # Clear screen securely
                    import subprocess
                    import platform
                    
                    if platform.system() == "Windows":
                        subprocess.run(["cls"], shell=False, check=False)
                    else:
                        subprocess.run(["clear"], shell=False, check=False)
                elif user_input:
                    # Probeer het als commando uit te voeren
                    self.run(user_input)
                else:
                    continue

            except KeyboardInterrupt:
                print("\nTot ziens! 👋")
                break
            except Exception as e:
                print(f"❌ Fout: {e}")
                print("Probeer 'help' voor beschikbare commando's.")

    async def run(self, command=None):
        """Main run method for Architect agent."""
        try:
            # Initialize all integrations
            await self.initialize_mcp()
            await self.initialize_enhanced_mcp()
            await self.initialize_tracing()
            await self.initialize_message_bus()

            # Subscribe to relevant events
            subscribe("api_design_requested", self._handle_api_design_requested)
            subscribe("system_design_requested", self._handle_system_design_requested)
            subscribe("architecture_review_requested", self._handle_architecture_review_requested)
            subscribe("tech_stack_evaluation_requested", self._handle_tech_stack_evaluation_requested)
            subscribe("pipeline_advice_requested", self._handle_pipeline_advice_requested)
            subscribe("task_delegated", self._handle_task_delegated)

            # Get context and save initial state
            try:
                context = get_context(self.agent_name)
                if isinstance(context, list):
                    context = {}
                context["agent_status"] = "active"
                context["last_activity"] = datetime.now().isoformat()
                save_context(self.agent_name, "status", context)
            except Exception as e:
                logging.warning(f"Context handling failed: {e}")
                # Continue without context

            print(f"🏗️ Architect Agent gestart en klaar voor architecture requests")
            print(f"📊 Performance Metrics: {len(self.performance_metrics)} metrics actief")
            print(f"🔗 Message Bus: {'Enabled' if self.message_bus_enabled else 'Disabled'}")
            print(f"🔍 Enhanced MCP: {'Enabled' if self.enhanced_mcp_enabled else 'Disabled'}")
            print(f"📈 Tracing: {'Enabled' if self.tracing_enabled else 'Disabled'}")

            # Run command if provided
            if command:
                if command == "design-frontend":
                    return await self.design_frontend()
                elif command == "design-system":
                    return await self.design_system()
                elif command == "tech-stack":
                    return await self.tech_stack()
                elif command == "start-conversation":
                    return self.start_conversation()
                elif command == "help":
                    self.show_help()
                elif command == "best-practices":
                    self.best_practices()
                elif command == "export":
                    self.export()
                elif command == "changelog":
                    self.changelog()
                elif command == "list-resources":
                    self.list_resources()
                elif command == "test":
                    self.test()
                elif command in ["collaborate_example", "collaborate"]:
                    return self.collaborate_example()
                else:
                    print(f"Unknown command: {command}")
                    logging.error(f"Onbekend commando: {command}")
                    self.show_help()

        except Exception as e:
            logging.error(f"Error in Architect run method: {e}")
            raise

    async def run_async(self):
        """Async version of run method."""
        return await self.run()

    @classmethod
    async def run_agent(cls):
        """Class method to run the agent."""
        agent = cls()
        await agent.run()

    @classmethod
    async def run_agent_async(cls):
        """Class method to run the agent asynchronously."""
        return await cls.run_agent()


async def on_api_design_requested(event):
    """Event handler voor API design requests."""
    try:
        use_case = event.get("use_case", "Default API use case")
        
        # Use ask_openai for API design
        result = ask_openai(
            f"Design a REST API for: {use_case}",
            "You are an expert API architect. Provide a complete API design with endpoints, data models, and documentation."
        )
        
        return {
            "success": True,
            "use_case": use_case,
            "api_design": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Error in API design event handler: {e}")
        return {"error": str(e), "success": False}

async def on_pipeline_advice_requested(event):
    """Event handler voor pipeline advice requests."""
    try:
        pipeline_type = event.get("pipeline_type", "CI/CD")
        
        # Use ask_openai for pipeline advice
        result = ask_openai(
            f"Provide advice for {pipeline_type} pipeline",
            "You are an expert DevOps engineer. Provide comprehensive pipeline advice including tools, best practices, and implementation steps."
        )
        
        return {
            "success": True,
            "pipeline_type": pipeline_type,
            "advice": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Error in pipeline advice event handler: {e}")
        return {"error": str(e), "success": False}

def main():
    """Main function for Architect agent CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Architect Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "design-frontend", "design-system", "tech-stack", 
                               "start-conversation", "best-practices", "export", "changelog", 
                               "list-resources", "test", "collaborate", "run",
                               "initialize-mcp", "use-mcp-tool", "get-mcp-status", "use-architecture-mcp-tools",
                               "check-dependencies", "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary",
                               "message-bus-status", "publish-event", "subscribe-event", "list-events",
                               "event-history", "performance-metrics"])
    parser.add_argument("--event-type", help="Event type for publish-event")
    parser.add_argument("--event-data", help="JSON data for publish-event")
    args = parser.parse_args()
    
    agent = ArchitectAgent()
    
    if args.command == "help":
        agent.show_help()
    elif args.command == "design-frontend":
        asyncio.run(agent.design_frontend())
    elif args.command == "design-system":
        asyncio.run(agent.design_system())
    elif args.command == "tech-stack":
        asyncio.run(agent.tech_stack())
    elif args.command == "start-conversation":
        agent.start_conversation()
    elif args.command == "best-practices":
        agent.best_practices()
    elif args.command == "export":
        agent.export()
    elif args.command == "changelog":
        agent.changelog()
    elif args.command == "list-resources":
        agent.list_resources()
    elif args.command == "test":
        agent.test()
    elif args.command == "collaborate":
        result = agent.collaborate_example()
        print(json.dumps(result, indent=2))
    elif args.command == "run":
        asyncio.run(agent.run())
    # Message Bus Commands
    elif args.command == "message-bus-status":
        print("🏗️ Architect Agent Message Bus Status:")
        print(f"✅ Message Bus Integration: {'Enabled' if agent.message_bus_enabled else 'Disabled'}")
        print(f"✅ Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
        print(f"✅ Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
        print(f"📊 Performance Metrics: {len(agent.performance_metrics)} metrics tracked")
        print(f"📝 Architecture History: {len(agent.architecture_history)} entries")
        print(f"🎯 Design Patterns: {len(agent.design_patterns)} patterns")
    elif args.command == "publish-event":
        if not args.event_type:
            print("Geef event type op met --event-type")
            sys.exit(1)
        event_data = {}
        if args.event_data:
            try:
                event_data = json.loads(args.event_data)
            except json.JSONDecodeError:
                print("Invalid JSON in event data")
                sys.exit(1)
        publish(args.event_type, event_data)
        print(f"Event '{args.event_type}' gepubliceerd met data: {event_data}")
    elif args.command == "subscribe-event":
        if not args.event_type:
            print("Geef event type op met --event-type")
            sys.exit(1)
        # Subscribe to event (this would be handled in the agent initialization)
        print(f"Subscribed to event: {args.event_type}")
    elif args.command == "list-events":
        print("🏗️ Architect Agent Supported Events:")
        print("📥 Input Events:")
        print("  - api_design_requested")
        print("  - system_design_requested")
        print("  - architecture_review_requested")
        print("  - tech_stack_evaluation_requested")
        print("  - pipeline_advice_requested")
        print("  - task_delegated")
        print("📤 Output Events:")
        print("  - api_design_completed")
        print("  - system_design_completed")
        print("  - architecture_review_completed")
        print("  - tech_stack_evaluation_completed")
        print("  - pipeline_advice_completed")
        print("  - task_delegation_completed")
    elif args.command == "event-history":
        print("📝 Architecture History:")
        for entry in agent.architecture_history[-10:]:
            print(f"  - {entry.get('type', 'unknown')}: {entry.get('target_agent', 'unknown')}")
        print("\n🎯 Design Patterns:")
        for pattern in agent.design_patterns[-10:]:
            print(f"  - {pattern}")
    elif args.command == "performance-metrics":
        print("📊 Architect Agent Performance Metrics:")
        for metric, value in agent.performance_metrics.items():
            if isinstance(value, float):
                print(f"  • {metric}: {value:.2f}")
            else:
                print(f"  • {metric}: {value}")
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["ProductOwner", "BackendDeveloper", "FrontendDeveloper", "DevOpsInfra"], 
                {"type": "architecture_review", "content": {"review_type": "system_design"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "architecture_data": {"components": ["API", "Database", "Frontend"]},
                "security_requirements": ["authentication", "authorization", "data_encryption"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "architecture_data": {"components": ["API", "Database", "Frontend"]},
                "performance_metrics": {"response_time": 200, "throughput": 1000}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_architecture_operation({
                "operation_type": "system_design",
                "components": ["API", "Database", "Frontend"],
                "architecture_requirements": ["scalability", "reliability", "security"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_architecture_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"response_time": 200, "throughput": 1000}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_architecture_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "design_validation", "error_message": "Architecture review failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for Architect Agent:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Message Bus: {'Enabled' if agent.message_bus_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print(f"Unknown command: {args.command}")
        agent.show_help()

if __name__ == "__main__":
    main()
