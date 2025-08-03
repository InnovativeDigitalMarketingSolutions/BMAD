import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, List

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from integrations.prefect.prefect_workflow import PrefectWorkflowOrchestrator
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

# Enhanced MCP Integration for Phase 2
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)


# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ScrumError(Exception):
    """Custom exception for scrum-related errors."""
    pass

class ScrumValidationError(ScrumError):
    """Exception for scrum validation failures."""
    pass

class ScrummasterAgent:
    """
    Scrummaster Agent voor BMAD.
    Gespecialiseerd in agile project management, sprint planning, en team facilitation.
    """
    
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        try:
            self.scrummaster_template = self.framework_manager.get_framework_template('scrummaster')
        except:
            self.scrummaster_template = None
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "Scrummaster"
        
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "ScrummasterAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        self.workflow = PrefectWorkflowOrchestrator()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "sprint-planning": self.resource_base / "templates/scrummaster/sprint-planning.md",
            "daily-standup": self.resource_base / "templates/scrummaster/daily-standup.md",
            "sprint-review": self.resource_base / "templates/scrummaster/sprint-review.md",
            "retrospective": self.resource_base / "templates/scrummaster/retrospective.md",
            "team-health": self.resource_base / "templates/scrummaster/team-health.md",
            "impediment-tracking": self.resource_base / "templates/scrummaster/impediment-tracking.md",
            "velocity-tracking": self.resource_base / "templates/scrummaster/velocity-tracking.md",
            "scrum-guide": self.resource_base / "templates/scrummaster/scrum-guide.md"
        }
        self.data_paths = {
            "sprint-history": self.resource_base / "data/scrummaster/sprint-history.md",
            "team-metrics": self.resource_base / "data/scrummaster/team-metrics.md",
            "impediment-log": self.resource_base / "data/scrummaster/impediment-log.md",
            "velocity-data": self.resource_base / "data/scrummaster/velocity-data.md"
        }

        # Initialize histories
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        
        # Tracing Integration
        self.tracing_enabled = False
        self.sprint_history = []
        self.team_metrics = []
        self.impediment_log = []
        self.velocity_data = []
        self._load_sprint_history()
        self._load_team_metrics()
        self._load_impediment_log()
        self._load_velocity_data()

        # Scrum-specific attributes
        self.current_sprint = None
        self.team_members = ["Developer1", "Developer2", "Tester", "Designer"]
        self.sprint_duration = 14  # days
        self.velocity_target = 20
        self.impediments = []
        
        # Performance metrics
        self.performance_metrics = {
            "sprints_completed": 0,
            "team_velocity": 0.0,
            "impediments_resolved": 0,
            "sprint_success_rate": 0.0
        }

        # Initialize MCP integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False

        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

    async def initialize_mcp(self):
        """Initialize MCP client and integration."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False
    
    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration()
            await self.enhanced_mcp.initialize()
            self.enhanced_mcp_enabled = True
            logger.info("Enhanced MCP initialized successfully")
        except Exception as e:
            logger.warning(f"Enhanced MCP initialization failed: {e}")
            self.enhanced_mcp_enabled = False
    
    async def initialize_tracing(self):
        """Initialize tracing capabilities."""
        try:
            if self.tracer:
                await self.tracer.initialize()
                self.tracing_enabled = True
                logger.info("Tracing initialized successfully")
            else:
                logger.warning("Tracer not available")
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

    async def use_scrum_specific_mcp_tools(self, scrum_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use scrum-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # Sprint planning
        sprint_plan_result = await self.use_mcp_tool("sprint_planning", {
            "sprint_number": scrum_data.get("sprint_number", 1),
            "team_capacity": scrum_data.get("team_capacity", 100),
            "backlog_items": scrum_data.get("backlog_items", []),
            "planning_type": "comprehensive"
        })
        if sprint_plan_result:
            enhanced_data["sprint_planning"] = sprint_plan_result
        
        # Team facilitation
        team_facilitation_result = await self.use_mcp_tool("team_facilitation", {
            "team_size": scrum_data.get("team_size", 5),
            "team_health": scrum_data.get("team_health", "good"),
            "facilitation_type": scrum_data.get("facilitation_type", "daily_standup"),
            "impediments": scrum_data.get("impediments", [])
        })
        if team_facilitation_result:
            enhanced_data["team_facilitation"] = team_facilitation_result
        
        # Velocity tracking
        velocity_result = await self.use_mcp_tool("velocity_tracking", {
            "sprint_data": scrum_data.get("sprint_data", {}),
            "team_metrics": scrum_data.get("team_metrics", {}),
            "tracking_type": "comprehensive",
            "analysis_type": "trend_analysis"
        })
        if velocity_result:
            enhanced_data["velocity_tracking"] = velocity_result
        
        # Impediment management
        impediment_result = await self.use_mcp_tool("impediment_management", {
            "impediments": scrum_data.get("impediments", []),
            "resolution_priority": scrum_data.get("resolution_priority", "high"),
            "management_type": "proactive",
            "escalation_level": scrum_data.get("escalation_level", "team")
        })
        if impediment_result:
            enhanced_data["impediment_management"] = impediment_result
        
        return enhanced_data
    
    async def use_enhanced_mcp_tools(self, scrum_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_scrum_specific_mcp_tools(scrum_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": scrum_data.get("capabilities", []),
                "performance_metrics": scrum_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Scrum-specific enhanced tools
            scrum_enhanced_result = await self.use_scrum_specific_enhanced_tools(scrum_data)
            enhanced_data.update(scrum_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_scrum_operation(scrum_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_scrum_specific_enhanced_tools(self, scrum_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use scrum-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced sprint planning
            if "sprint_planning" in scrum_data:
                sprint_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_sprint_planning", {
                    "sprint_data": scrum_data["sprint_planning"],
                    "team_capacity": scrum_data.get("team_capacity", {}),
                    "velocity_history": scrum_data.get("velocity_history", [])
                })
                enhanced_tools["enhanced_sprint_planning"] = sprint_result
            
            # Enhanced team collaboration
            if "team_collaboration" in scrum_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "TestEngineer", "BackendDeveloper", "FrontendDeveloper"],
                    {
                        "type": "sprint_coordination",
                        "content": scrum_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced impediment resolution
            if "impediment_resolution" in scrum_data:
                impediment_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_impediment_resolution", {
                    "impediment_data": scrum_data["impediment_resolution"],
                    "resolution_strategies": scrum_data.get("resolution_strategies", [])
                })
                enhanced_tools["enhanced_impediment_resolution"] = impediment_result
            
            logger.info(f"Scrum-specific enhanced tools used: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Scrum-specific enhanced tools failed: {e}")
            enhanced_tools["error"] = str(e)
        
        return enhanced_tools
    
    async def trace_scrum_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace scrum operations for monitoring and debugging."""
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
            logger.info(f"Scrum operation traced: {operation_data.get('operation_type', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"status": "tracing_error", "error": str(e)}

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise ScrumValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_sprint_data(self, sprint_data: Dict[str, Any]) -> None:
        """Validate sprint data structure."""
        self._validate_input(sprint_data, dict, "sprint_data")
        required_fields = ["sprint_number", "start_date", "end_date", "team"]
        for field in required_fields:
            if field not in sprint_data:
                raise ScrumValidationError(f"Missing required field: {field}")

    def _validate_team_data(self, team_data: Dict[str, Any]) -> None:
        """Validate team data structure."""
        self._validate_input(team_data, dict, "team_data")
        required_fields = ["team_name", "members", "capacity"]
        for field in required_fields:
            if field not in team_data:
                raise ScrumValidationError(f"Missing required field: {field}")

    def _load_sprint_history(self):
        """Load sprint history with comprehensive error handling."""
        try:
            if self.data_paths["sprint-history"].exists():
                with open(self.data_paths["sprint-history"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.sprint_history.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading sprint history: {e}")
            raise ScrumError(f"Cannot access sprint history file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading sprint history: {e}")
            raise ScrumError(f"Invalid encoding in sprint history file: {e}")
        except OSError as e:
            logger.error(f"OS error loading sprint history: {e}")
            raise ScrumError(f"System error loading sprint history: {e}")
        except Exception as e:
            logger.warning(f"Could not load sprint history: {e}")

    def _save_sprint_history(self):
        """Save sprint history with comprehensive error handling."""
        try:
            self.data_paths["sprint-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["sprint-history"], "w", encoding="utf-8") as f:
                f.write("# Sprint History\n\n")
                f.writelines(f"- {sprint}\n" for sprint in self.sprint_history[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving sprint history: {e}")
            raise ScrumError(f"Cannot write to sprint history file: {e}")
        except OSError as e:
            logger.error(f"OS error saving sprint history: {e}")
            raise ScrumError(f"System error saving sprint history: {e}")
        except Exception as e:
            logger.error(f"Could not save sprint history: {e}")

    def _load_team_metrics(self):
        """Load team metrics with comprehensive error handling."""
        try:
            if self.data_paths["team-metrics"].exists():
                with open(self.data_paths["team-metrics"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.team_metrics.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading team metrics: {e}")
            raise ScrumError(f"Cannot access team metrics file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading team metrics: {e}")
            raise ScrumError(f"Invalid encoding in team metrics file: {e}")
        except OSError as e:
            logger.error(f"OS error loading team metrics: {e}")
            raise ScrumError(f"System error loading team metrics: {e}")
        except Exception as e:
            logger.warning(f"Could not load team metrics: {e}")

    def _save_team_metrics(self):
        """Save team metrics with comprehensive error handling."""
        try:
            self.data_paths["team-metrics"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["team-metrics"], "w", encoding="utf-8") as f:
                f.write("# Team Metrics\n\n")
                f.writelines(f"- {metric}\n" for metric in self.team_metrics[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving team metrics: {e}")
            raise ScrumError(f"Cannot write to team metrics file: {e}")
        except OSError as e:
            logger.error(f"OS error saving team metrics: {e}")
            raise ScrumError(f"System error saving team metrics: {e}")
        except Exception as e:
            logger.error(f"Could not save team metrics: {e}")

    def _load_impediment_log(self):
        """Load impediment log with comprehensive error handling."""
        try:
            if self.data_paths["impediment-log"].exists():
                with open(self.data_paths["impediment-log"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.impediment_log.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading impediment log: {e}")
            raise ScrumError(f"Cannot access impediment log file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading impediment log: {e}")
            raise ScrumError(f"Invalid encoding in impediment log file: {e}")
        except OSError as e:
            logger.error(f"OS error loading impediment log: {e}")
            raise ScrumError(f"System error loading impediment log: {e}")
        except Exception as e:
            logger.warning(f"Could not load impediment log: {e}")

    def _save_impediment_log(self):
        """Save impediment log with comprehensive error handling."""
        try:
            self.data_paths["impediment-log"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["impediment-log"], "w", encoding="utf-8") as f:
                f.write("# Impediment Log\n\n")
                f.writelines(f"- {impediment}\n" for impediment in self.impediment_log[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving impediment log: {e}")
            raise ScrumError(f"Cannot write to impediment log file: {e}")
        except OSError as e:
            logger.error(f"OS error saving impediment log: {e}")
            raise ScrumError(f"System error saving impediment log: {e}")
        except Exception as e:
            logger.error(f"Could not save impediment log: {e}")

    def _load_velocity_data(self):
        """Load velocity data with comprehensive error handling."""
        try:
            if self.data_paths["velocity-data"].exists():
                with open(self.data_paths["velocity-data"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.velocity_data.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading velocity data: {e}")
            raise ScrumError(f"Cannot access velocity data file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading velocity data: {e}")
            raise ScrumError(f"Invalid encoding in velocity data file: {e}")
        except OSError as e:
            logger.error(f"OS error loading velocity data: {e}")
            raise ScrumError(f"System error loading velocity data: {e}")
        except Exception as e:
            logger.warning(f"Could not load velocity data: {e}")

    def _save_velocity_data(self):
        """Save velocity data with comprehensive error handling."""
        try:
            self.data_paths["velocity-data"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["velocity-data"], "w", encoding="utf-8") as f:
                f.write("# Velocity Data\n\n")
                f.writelines(f"- {velocity}\n" for velocity in self.velocity_data[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving velocity data: {e}")
            raise ScrumError(f"Cannot write to velocity data file: {e}")
        except OSError as e:
            logger.error(f"OS error saving velocity data: {e}")
            raise ScrumError(f"System error saving velocity data: {e}")
        except Exception as e:
            logger.error(f"Could not save velocity data: {e}")

    def _record_scrum_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record scrum-specific metrics."""
        try:
            self.monitor._record_metric(self.agent_name, MetricType.SUCCESS_RATE, value, unit)
        except Exception as e:
            logger.warning(f"Could not record metric {metric_name}: {e}")

    def show_help(self):
        """Display help information."""
        help_text = """
Scrummaster Agent Commands:
  help                    - Show this help message
  plan-sprint [sprint_number] - Plan a new sprint
  start-sprint [sprint_number] - Start a sprint
  end-sprint [sprint_number] - End a sprint
  daily-standup          - Conduct daily standup
  track-impediment [description] - Track an impediment
  resolve-impediment [id] - Resolve an impediment
  show-sprint-history    - Show sprint history
  show-team-metrics      - Show team metrics
  show-impediments       - Show current impediments
  show-velocity          - Show velocity data
  calculate-velocity     - Calculate team velocity
  team-health-check      - Conduct team health check
  show-scrum-guide       - Show Scrum guide
  test                   - Test resource completeness
  collaborate            - Demonstrate collaboration with other agents
  run                    - Start the agent in event listening mode
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content with comprehensive error handling."""
        try:
            self._validate_input(resource_type, str, "resource_type")
            
            if not resource_type.strip():
                raise ScrumValidationError("Resource type cannot be empty")
            
            resource_mapping = {
                "sprint-planning": self.template_paths["sprint-planning"],
                "daily-standup": self.template_paths["daily-standup"],
                "sprint-review": self.template_paths["sprint-review"],
                "retrospective": self.template_paths["retrospective"],
                "team-health": self.template_paths["team-health"],
                "impediment-tracking": self.template_paths["impediment-tracking"],
                "velocity-tracking": self.template_paths["velocity-tracking"],
                "scrum-guide": self.template_paths["scrum-guide"]
            }
            
            if resource_type not in resource_mapping:
                print(f"Unknown resource type: {resource_type}")
                print(f"Available resources: {list(resource_mapping.keys())}")
                return
                
            path = resource_mapping[resource_type]
            
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except PermissionError as e:
            logger.error(f"Permission denied reading resource {resource_type}: {e}")
            print(f"Permission denied accessing resource: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error reading resource {resource_type}: {e}")
            print(f"Invalid encoding in resource file: {e}")
        except OSError as e:
            logger.error(f"OS error reading resource {resource_type}: {e}")
            print(f"System error reading resource: {e}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")
            print(f"Error reading resource: {e}")

    async def plan_sprint(self, sprint_number: int = 1) -> Dict[str, Any]:
        """Plan a sprint with comprehensive validation and MCP enhancement."""
        try:
            self._validate_input(sprint_number, int, "sprint_number")
            
            if sprint_number <= 0:
                raise ScrumValidationError("Sprint number must be positive")
            
            logger.info(f"Planning sprint {sprint_number}")

            # Simulate sprint planning process
            time.sleep(1)
            
            # Create base sprint data
            start_date = datetime.now()
            end_date = start_date + timedelta(days=14)  # Default 2-week sprint
            
            result = {
                "sprint_number": sprint_number,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": 14,
                "status": "planned",
                "team": ["Developer1", "Developer2", "Tester", "Designer"],  # Default team
                "velocity_target": 20,  # Default velocity
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Use MCP tools for enhanced sprint planning
            scrum_data = {
                "sprint_number": sprint_number,
                "team_capacity": 100,
                "backlog_items": ["Feature A", "Feature B", "Bug Fix C"],
                "team_size": 4,
                "team_health": "good",
                "facilitation_type": "sprint_planning",
                "sprint_data": result,
                "team_metrics": self.team_metrics,
                "impediments": [],
                "resolution_priority": "high",
                "escalation_level": "team"
            }
            
            enhanced_data = await self.use_scrum_specific_mcp_tools(scrum_data)
            
            # Add MCP enhanced data if available
            if enhanced_data:
                result["mcp_enhanced_data"] = enhanced_data
                result["mcp_enhanced"] = True

            # Add to history
            sprint_entry = f"{result['timestamp']}: Sprint {sprint_number} planned - Duration: 14 days"
            self.sprint_history.append(sprint_entry)
            self._save_sprint_history()

            # Record performance metric
            self._record_scrum_metric("sprint_planning_success", 95, "%")

            logger.info(f"Sprint planning result: {result}")
            return result
            
        except ScrumValidationError as e:
            logger.error(f"Validation error planning sprint: {e}")
            raise
        except Exception as e:
            logger.error(f"Error planning sprint: {e}")
            self._record_scrum_metric("sprint_planning_error", 5, "%")
            raise ScrumError(f"Failed to plan sprint: {e}")

    def start_sprint(self, sprint_number: int = 1) -> Dict[str, Any]:
        """Start a sprint with comprehensive validation and error handling."""
        try:
            self._validate_input(sprint_number, int, "sprint_number")
            
            if sprint_number <= 0:
                raise ScrumValidationError("Sprint number must be positive")
            
            logger.info(f"Starting sprint {sprint_number}")

            # Simulate sprint start process
            time.sleep(1)
            
            result = {
                "sprint_number": sprint_number,
                "start_date": datetime.now().isoformat(),
                "status": "active",
                "team": self.team_members,
                "velocity_target": self.velocity_target,
                "impediments": len(self.impediments),
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Update current sprint
            self.current_sprint = sprint_number

            # Add to history
            sprint_entry = f"{result['timestamp']}: Sprint {sprint_number} started - Status: active"
            self.sprint_history.append(sprint_entry)
            self._save_sprint_history()

            # Update metrics
            self._record_scrum_metric("sprint_start_success", 98, "%")

            logger.info(f"Sprint start result: {result}")
            return result
            
        except ScrumValidationError as e:
            logger.error(f"Validation error starting sprint: {e}")
            raise
        except Exception as e:
            logger.error(f"Error starting sprint: {e}")
            self._record_scrum_metric("sprint_start_error", 2, "%")
            raise ScrumError(f"Failed to start sprint: {e}")

    def end_sprint(self, sprint_number: int = 1) -> Dict[str, Any]:
        """End a sprint with comprehensive validation and error handling."""
        try:
            self._validate_input(sprint_number, int, "sprint_number")
            
            if sprint_number <= 0:
                raise ScrumValidationError("Sprint number must be positive")
            
            logger.info(f"Ending sprint {sprint_number}")

            # Simulate sprint end process
            time.sleep(1)
            
            result = {
                "sprint_number": sprint_number,
                "end_date": datetime.now().isoformat(),
                "status": "completed",
                "team": self.team_members,
                "velocity_achieved": self.performance_metrics["team_velocity"],
                "impediments_resolved": self.performance_metrics["impediments_resolved"],
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Update current sprint
            if self.current_sprint == sprint_number:
                self.current_sprint = None

            # Add to history
            sprint_entry = f"{result['timestamp']}: Sprint {sprint_number} completed - Velocity: {self.performance_metrics['team_velocity']}"
            self.sprint_history.append(sprint_entry)
            self._save_sprint_history()

            # Update metrics
            self.performance_metrics["sprint_success_rate"] = 95.5
            self._record_scrum_metric("sprint_end_success", 95.5, "%")

            logger.info(f"Sprint end result: {result}")
            return result
            
        except ScrumValidationError as e:
            logger.error(f"Validation error ending sprint: {e}")
            raise
        except Exception as e:
            logger.error(f"Error ending sprint: {e}")
            self._record_scrum_metric("sprint_end_error", 4.5, "%")
            raise ScrumError(f"Failed to end sprint: {e}")

    def daily_standup(self) -> Dict[str, Any]:
        """Conduct daily standup with comprehensive error handling."""
        try:
            logger.info("Conducting daily standup")

            # Simulate daily standup process
            time.sleep(1)
            
            result = {
                "date": datetime.now().isoformat(),
                "type": "daily_standup",
                "participants": self.team_members,
                "impediments_identified": len(self.impediments),
                "sprint_progress": "on_track",
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Add to team metrics
            metric_entry = f"{result['timestamp']}: Daily standup completed - Impediments: {len(self.impediments)}"
            self.team_metrics.append(metric_entry)
            self._save_team_metrics()

            # Update metrics
            self._record_scrum_metric("daily_standup_success", 97, "%")

            logger.info(f"Daily standup result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error conducting daily standup: {e}")
            self._record_scrum_metric("daily_standup_error", 3, "%")
            raise ScrumError(f"Failed to conduct daily standup: {e}")

    def track_impediment(self, description: str = "General impediment") -> Dict[str, Any]:
        """Track an impediment with comprehensive validation and error handling."""
        try:
            self._validate_input(description, str, "description")
            
            if not description.strip():
                raise ScrumValidationError("Impediment description cannot be empty")
            
            logger.info(f"Tracking impediment: {description}")

            # Generate impediment ID
            impediment_id = len(self.impediments) + 1
            
            result = {
                "impediment_id": impediment_id,
                "description": description,
                "status": "open",
                "created_date": datetime.now().isoformat(),
                "assigned_to": "team",
                "priority": "medium",
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Add to impediment log
            impediment_entry = f"{result['timestamp']}: Impediment {impediment_id} - {description}"
            self.impediment_log.append(impediment_entry)
            self._save_impediment_log()

            # Add to impediments list
            self.impediments.append(result)

            # Update metrics
            self._record_scrum_metric("impediment_tracking_success", 96, "%")

            logger.info(f"Impediment tracking result: {result}")
            return result
            
        except ScrumValidationError as e:
            logger.error(f"Validation error tracking impediment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error tracking impediment: {e}")
            self._record_scrum_metric("impediment_tracking_error", 4, "%")
            raise ScrumError(f"Failed to track impediment: {e}")

    def resolve_impediment(self, impediment_id: int) -> Dict[str, Any]:
        """Resolve an impediment with comprehensive validation and error handling."""
        try:
            self._validate_input(impediment_id, int, "impediment_id")
            
            if impediment_id <= 0:
                raise ScrumValidationError("Impediment ID must be positive")
            
            logger.info(f"Resolving impediment {impediment_id}")

            # Find impediment
            impediment = None
            for imp in self.impediments:
                if imp.get("impediment_id") == impediment_id:
                    impediment = imp
                    break
            
            if not impediment:
                raise ScrumValidationError(f"Impediment {impediment_id} not found")
            
            # Update impediment status
            impediment["status"] = "resolved"
            impediment["resolved_date"] = datetime.now().isoformat()
            
            result = {
                "impediment_id": impediment_id,
                "status": "resolved",
                "resolved_date": datetime.now().isoformat(),
                "resolution_time_hours": 24,  # Simulated
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Add to impediment log
            impediment_entry = f"{result['timestamp']}: Impediment {impediment_id} resolved"
            self.impediment_log.append(impediment_entry)
            self._save_impediment_log()

            # Update metrics
            self.performance_metrics["impediments_resolved"] += 1
            self._record_scrum_metric("impediment_resolution_success", 94, "%")

            logger.info(f"Impediment resolution result: {result}")
            return result
            
        except ScrumValidationError as e:
            logger.error(f"Validation error resolving impediment: {e}")
            raise
        except Exception as e:
            logger.error(f"Error resolving impediment: {e}")
            self._record_scrum_metric("impediment_resolution_error", 6, "%")
            raise ScrumError(f"Failed to resolve impediment: {e}")

    def calculate_velocity(self) -> Dict[str, Any]:
        """Calculate team velocity with comprehensive error handling."""
        try:
            logger.info("Calculating team velocity")

            # Simulate velocity calculation
            time.sleep(1)
            
            # Calculate average velocity from last 3 sprints
            recent_velocities = [15, 18, 16]  # Simulated data
            average_velocity = sum(recent_velocities) / len(recent_velocities)
            
            result = {
                "average_velocity": average_velocity,
                "sprints_analyzed": len(recent_velocities),
                "velocity_trend": "stable",
                "recommendation": "Maintain current sprint capacity",
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Update performance metrics
            self.performance_metrics["team_velocity"] = average_velocity

            # Add to velocity data
            velocity_entry = f"{result['timestamp']}: Velocity calculated - Average: {average_velocity}"
            self.velocity_data.append(velocity_entry)
            self._save_velocity_data()

            # Update metrics
            self._record_scrum_metric("velocity_calculation_success", 93, "%")

            logger.info(f"Velocity calculation result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating velocity: {e}")
            self._record_scrum_metric("velocity_calculation_error", 7, "%")
            raise ScrumError(f"Failed to calculate velocity: {e}")

    def team_health_check(self) -> Dict[str, Any]:
        """Conduct team health check with comprehensive error handling."""
        try:
            logger.info("Conducting team health check")

            # Simulate team health check
            time.sleep(1)
            
            result = {
                "date": datetime.now().isoformat(),
                "team_health_score": 8.5,
                "areas_of_concern": ["Communication", "Technical debt"],
                "positive_aspects": ["Collaboration", "Innovation"],
                "recommendations": ["Improve communication channels", "Address technical debt"],
                "timestamp": datetime.now().isoformat(),
                "agent": "ScrummasterAgent"
            }

            # Add to team metrics
            metric_entry = f"{result['timestamp']}: Team health check - Score: {result['team_health_score']}"
            self.team_metrics.append(metric_entry)
            self._save_team_metrics()

            # Update metrics
            self._record_scrum_metric("team_health_check_success", 92, "%")

            logger.info(f"Team health check result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error conducting team health check: {e}")
            self._record_scrum_metric("team_health_check_error", 8, "%")
            raise ScrumError(f"Failed to conduct team health check: {e}")

    def show_sprint_history(self):
        """Show sprint history."""
        if not self.sprint_history:
            print("No sprint history available.")
            return
        print("Sprint History:")
        print("=" * 50)
        for i, sprint in enumerate(self.sprint_history[-10:], 1):
            print(f"{i}. {sprint}")

    def show_team_metrics(self):
        """Show team metrics."""
        if not self.team_metrics:
            print("No team metrics available.")
            return
        print("Team Metrics:")
        print("=" * 50)
        for i, metric in enumerate(self.team_metrics[-10:], 1):
            print(f"{i}. {metric}")

    def show_impediments(self):
        """Show current impediments."""
        if not self.impediments:
            print("No current impediments.")
            return
        print("Current Impediments:")
        print("=" * 50)
        for i, impediment in enumerate(self.impediments, 1):
            print(f"{i}. ID: {impediment.get('impediment_id')} - {impediment.get('description')} - Status: {impediment.get('status')}")

    def show_velocity(self):
        """Show velocity data."""
        if not self.velocity_data:
            print("No velocity data available.")
            return
        print("Velocity Data:")
        print("=" * 50)
        for i, velocity in enumerate(self.velocity_data[-10:], 1):
            print(f"{i}. {velocity}")

    def test_resource_completeness(self):
        """Test resource completeness with detailed reporting."""
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
            return False
        else:
            print("All resources are available!")
            return True

    def collaborate_example(self):
        """Demonstrate collaboration with other agents."""
        logger.info("Starting collaboration example...")

        try:
            # Plan a sprint
            sprint_result = self.plan_sprint(1)
            
            # Start the sprint
            start_result = self.start_sprint(1)
            
            # Track an impediment
            impediment_result = self.track_impediment("Technical debt affecting development speed")
            
            # Conduct daily standup
            standup_result = self.daily_standup()
            
            # Resolve impediment
            resolve_result = self.resolve_impediment(1)
            
            # End sprint
            end_result = self.end_sprint(1)
            
            # Calculate velocity
            velocity_result = self.calculate_velocity()
            
            # Publish events
            publish("sprint_planning_completed", sprint_result)
            publish("sprint_started", start_result)
            publish("impediment_tracked", impediment_result)
            publish("daily_standup_completed", standup_result)
            publish("impediment_resolved", resolve_result)
            publish("sprint_completed", end_result)
            publish("velocity_calculated", velocity_result)

            # Notify via Slack
            try:
                send_slack_message(f"Sprint {sprint_result['sprint_number']} completed successfully with velocity {velocity_result['average_velocity']}")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")

            logger.info("Collaboration example completed successfully")
            
        except Exception as e:
            logger.error(f"Error in collaboration example: {e}")
            raise ScrumError(f"Collaboration example failed: {e}")

    def handle_sprint_review_completed(self, event):
        """Handle sprint review completed event."""
        try:
            logger.info(f"Sprint review completed: {event}")
            self.monitor.log_metric("sprint_review", event)
            allowed = self.policy_engine.evaluate_policy("sprint_review", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Error handling sprint review completed: {e}")

    def handle_sprint_planning_requested(self, event):
        """Handle sprint planning requested event."""
        try:
            logger.info(f"Sprint planning requested: {event}")
            sprint_number = event.get("sprint_number", 1)
            self.plan_sprint(sprint_number)
        except Exception as e:
            logger.error(f"Error handling sprint planning requested: {e}")

    async def run(self):
        """Start the agent in event listening mode met complete integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        subscribe("sprint_review_completed", self.handle_sprint_review_completed)
        subscribe("sprint_planning_requested", self.handle_sprint_planning_requested)

        logger.info("ScrummasterAgent ready and listening for events...")
        print("🎯 Scrummaster Agent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        self.collaborate_example()
        
        try:
            # Keep the agent running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scrummaster agent stopped.")
            print("\n🛑 Scrummaster Agent stopped.")
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the Scrummaster agent met MCP integration."""
        agent = cls()
        await agent.initialize_mcp()
        print("Scrummaster agent started with MCP integration")

def main():
    """Main CLI function with comprehensive error handling."""
    parser = argparse.ArgumentParser(description="Scrummaster Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "plan-sprint", "start-sprint", "end-sprint", "daily-standup",
                               "track-impediment", "resolve-impediment", "show-sprint-history",
                               "show-team-metrics", "show-impediments", "show-velocity",
                               "calculate-velocity", "team-health-check", "show-scrum-guide",
                               "test", "collaborate", "run", "initialize-mcp", "use-mcp-tool", 
                               "get-mcp-status", "use-scrum-mcp-tools", "check-dependencies",
                               "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary"])
    parser.add_argument("--sprint-number", type=int, default=1, help="Sprint number")
    parser.add_argument("--impediment-id", type=int, default=1, help="Impediment ID")
    parser.add_argument("--description", default="General impediment", help="Impediment description")

    args = parser.parse_args()

    try:
        agent = ScrummasterAgent()

        if args.command == "help":
            agent.show_help()
        elif args.command == "plan-sprint":
            result = asyncio.run(agent.plan_sprint(args.sprint_number))
            print(f"Sprint planned successfully: {result}")
        elif args.command == "start-sprint":
            result = agent.start_sprint(args.sprint_number)
            print(f"Sprint started successfully: {result}")
        elif args.command == "end-sprint":
            result = agent.end_sprint(args.sprint_number)
            print(f"Sprint ended successfully: {result}")
        elif args.command == "daily-standup":
            result = agent.daily_standup()
            print(f"Daily standup completed: {result}")
        elif args.command == "track-impediment":
            result = agent.track_impediment(args.description)
            print(f"Impediment tracked successfully: {result}")
        elif args.command == "resolve-impediment":
            result = agent.resolve_impediment(args.impediment_id)
            print(f"Impediment resolved successfully: {result}")
        elif args.command == "show-sprint-history":
            agent.show_sprint_history()
        elif args.command == "show-team-metrics":
            agent.show_team_metrics()
        elif args.command == "show-impediments":
            agent.show_impediments()
        elif args.command == "show-velocity":
            agent.show_velocity()
        elif args.command == "calculate-velocity":
            result = agent.calculate_velocity()
            print(f"Velocity calculated: {result}")
        elif args.command == "team-health-check":
            result = agent.team_health_check()
            print(f"Team health check completed: {result}")
        elif args.command == "show-scrum-guide":
            agent.show_resource("scrum-guide")
        elif args.command == "test":
            success = agent.test_resource_completeness()
            if success:
                print("Resource completeness test passed!")
            else:
                print("Resource completeness test failed!")
        elif args.command == "collaborate":
            agent.collaborate_example()
        elif args.command == "run":
            asyncio.run(agent.run())
        # Enhanced MCP commands
        elif args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["ProductOwner", "TestEngineer", "BackendDeveloper", "FrontendDeveloper"], 
                {"type": "sprint_coordination", "content": {"sprint_phase": "planning"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "auth_method": "multi_factor",
                "security_level": "enterprise",
                "compliance": ["gdpr", "sox", "iso27001"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "optimization_target": "sprint_planning",
                "performance_metrics": {"response_time": 0.5, "throughput": 100}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_scrum_operation({
                "operation_type": "sprint_planning",
                "sprint_number": args.sprint_number,
                "team_size": 5
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_scrum_operation({
                "operation_type": "performance_metrics",
                "metrics": {"velocity": 15, "sprint_duration": 14}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_scrum_operation({
                "operation_type": "error_scenario",
                "error_type": "impediment_resolution_failed",
                "error_details": "Team member unavailable"
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print(f"Tracing Status: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Enhanced MCP Status: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"MCP Status: {'Enabled' if agent.mcp_enabled else 'Disabled'}")
            
    except ScrumValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except ScrumError as e:
        print(f"Scrum error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
