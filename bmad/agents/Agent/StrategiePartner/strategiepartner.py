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
from bmad.core.mcp import (
    MCPClient, MCPContext, FrameworkMCPIntegration,
    get_mcp_client, get_framework_mcp_integration, initialize_framework_mcp_integration
)

# Enhanced MCP Phase 2 imports
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)

# Message Bus Integration
from bmad.agents.core.communication.agent_message_bus_integration import (
    AgentMessageBusIntegration,
    create_agent_message_bus_integration
)

from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class StrategyError(Exception):
    """Custom exception for strategy-related errors."""
    pass

class StrategyValidationError(StrategyError):
    """Exception for strategy validation failures."""
    pass

class StrategiePartnerAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "StrategiePartner"
        
        # Initialize core services
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2 attributes
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        self.enhanced_mcp_client = None
        
        # Tracing Integration
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "StrategiePartnerAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        self.tracing_enabled = False
        
        # Message Bus Integration
        self.message_bus_integration: Optional[AgentMessageBusIntegration] = None
        self.message_bus_enabled = False

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "strategy-planning": self.resource_base / "templates/strategiepartner/strategy-planning.md",
            "market-analysis": self.resource_base / "templates/strategiepartner/market-analysis.md",
            "competitive-analysis": self.resource_base / "templates/strategiepartner/competitive-analysis.md",
            "business-model": self.resource_base / "templates/strategiepartner/business-model.md",
            "risk-assessment": self.resource_base / "templates/strategiepartner/risk-assessment.md",
            "stakeholder-analysis": self.resource_base / "templates/strategiepartner/stakeholder-analysis.md",
            "strategic-roadmap": self.resource_base / "templates/strategiepartner/strategic-roadmap.md",
            "strategy-guide": self.resource_base / "templates/strategiepartner/strategy-guide.md"
        }
        self.data_paths = {
            "strategy-history": self.resource_base / "data/strategiepartner/strategy-history.md",
            "market-data": self.resource_base / "data/strategiepartner/market-data.md",
            "competitive-data": self.resource_base / "data/strategiepartner/competitive-data.md",
            "risk-register": self.resource_base / "data/strategiepartner/risk-register.md"
        }

        # Initialize histories
        self.strategy_history = []
        self.market_data = []
        self.competitive_data = []
        self.risk_register = []
        self._load_strategy_history()
        self._load_market_data()
        self._load_competitive_data()
        self._load_risk_register()

        # Strategy-specific attributes
        self.current_strategy = None
        self.strategic_goals = []
        self.market_position = "unknown"
        self.competitive_advantage = []
        self.risk_factors = []
        
        # Performance metrics
        self.performance_metrics = {
            "strategies_developed": 0,
            "market_analyses_completed": 0,
            "competitive_analyses_completed": 0,
            "risk_assessments_completed": 0,
            "strategy_success_rate": 0.0
        }

        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced strategy capabilities."""
        try:
            self.mcp_client = get_mcp_client()
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for StrategiePartner")
        except Exception as e:
            logger.warning(f"MCP initialization failed for StrategiePartner: {e}")
            self.mcp_enabled = False

    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            self.enhanced_mcp_client = self.enhanced_mcp.mcp_client if self.enhanced_mcp else None
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
                logger.info("Tracing initialized successfully for StrategiePartner")
                # Set up strategy-specific tracing spans
                await self.tracer.setup_strategy_tracing({
                    "agent_name": self.agent_name,
                    "tracing_level": "detailed",
                    "strategy_tracking": True,
                    "market_tracking": True,
                    "competitive_tracking": True,
                    "risk_tracking": True
                })
            else:
                logger.warning("Tracing initialization failed, continuing without tracing")
                
        except Exception as e:
            logger.warning(f"Tracing initialization failed for StrategiePartner: {e}")
            self.tracing_enabled = False

    async def initialize_message_bus_integration(self):
        """Initialize Message Bus Integration for the agent."""
        try:
            self.message_bus_integration = create_agent_message_bus_integration(
                agent_name=self.agent_name,
                agent_instance=self
            )
            
            # Register event handlers for strategy-specific events
            await self.message_bus_integration.register_event_handler(
                "strategy_development_requested", 
                self.handle_strategy_development_requested
            )
            await self.message_bus_integration.register_event_handler(
                "idea_validation_requested", 
                self.handle_idea_validation_requested
            )
            await self.message_bus_integration.register_event_handler(
                "idea_refinement_requested",
                self.handle_idea_refinement_requested
            )
            await self.message_bus_integration.register_event_handler(
                "epic_creation_requested",
                self.handle_epic_creation_requested
            )
            
            self.message_bus_enabled = True
            logger.info(f"✅ Message Bus Integration geïnitialiseerd voor {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Fout bij initialiseren van Message Bus Integration voor {self.agent_name}: {e}")
            return False

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

    async def use_strategy_specific_mcp_tools(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use strategy-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # Strategy development
        strategy_result = await self.use_mcp_tool("strategy_development", {
            "strategy_name": strategy_data.get("strategy_name", ""),
            "business_context": strategy_data.get("business_context", ""),
            "market_conditions": strategy_data.get("market_conditions", ""),
            "analysis_type": "comprehensive"
        })
        if strategy_result:
            enhanced_data["strategy_development"] = strategy_result
        
        # Market analysis
        market_result = await self.use_mcp_tool("market_analysis", {
            "sector": strategy_data.get("sector", ""),
            "market_size": strategy_data.get("market_size", ""),
            "growth_rate": strategy_data.get("growth_rate", ""),
            "analysis_depth": "detailed"
        })
        if market_result:
            enhanced_data["market_analysis"] = market_result
        
        # Competitive analysis
        competitive_result = await self.use_mcp_tool("competitive_analysis", {
            "competitors": strategy_data.get("competitors", []),
            "market_position": strategy_data.get("market_position", ""),
            "competitive_advantage": strategy_data.get("competitive_advantage", ""),
            "analysis_scope": "comprehensive"
        })
        if competitive_result:
            enhanced_data["competitive_analysis"] = competitive_result
        
        # Risk assessment
        risk_result = await self.use_mcp_tool("risk_assessment", {
            "strategy": strategy_data.get("strategy", ""),
            "risk_factors": strategy_data.get("risk_factors", []),
            "mitigation_strategies": strategy_data.get("mitigation_strategies", []),
            "assessment_type": "comprehensive"
        })
        if risk_result:
            enhanced_data["risk_assessment"] = risk_result
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_strategy_specific_mcp_tools(strategy_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": strategy_data.get("capabilities", []),
                "performance_metrics": strategy_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Strategy-specific enhanced tools
            strategy_enhanced_result = await self.use_strategy_specific_enhanced_tools(strategy_data)
            enhanced_data.update(strategy_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_strategy_operation(strategy_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_strategy_specific_enhanced_tools(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use strategy-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced strategy development
            if "strategy_development" in strategy_data:
                strategy_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_strategy_development", {
                    "strategy_data": strategy_data["strategy_development"],
                    "market_analysis": strategy_data.get("market_analysis", {}),
                    "competitive_analysis": strategy_data.get("competitive_analysis", {})
                })
                enhanced_tools["enhanced_strategy_development"] = strategy_result
            
            # Enhanced market analysis
            if "market_analysis" in strategy_data:
                market_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_market_analysis", {
                    "market_data": strategy_data["market_analysis"],
                    "sector": strategy_data.get("sector", "Technology"),
                    "analysis_depth": strategy_data.get("analysis_depth", "comprehensive")
                })
                enhanced_tools["enhanced_market_analysis"] = market_result
            
            # Enhanced team collaboration
            if "team_collaboration" in strategy_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "Architect", "QualityGuardian", "Scrummaster"],
                    {
                        "type": "strategy_review",
                        "content": strategy_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced risk assessment
            if "risk_assessment" in strategy_data:
                risk_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_risk_assessment", {
                    "risk_data": strategy_data["risk_assessment"],
                    "risk_factors": strategy_data.get("risk_factors", []),
                    "assessment_methodology": strategy_data.get("assessment_methodology", "comprehensive")
                })
                enhanced_tools["enhanced_risk_assessment"] = risk_result
            
            logger.info(f"Strategy-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in strategy-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_strategy_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace strategy operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "strategy_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "strategy_complexity": len(operation_data.get("strategies", [])),
                    "market_analysis_depth": len(operation_data.get("market_analysis", [])),
                    "collaboration_agents": len(operation_data.get("team_collaboration", {}).get("agents", []))
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("strategy_operation", trace_data)
            
            logger.info(f"Strategy operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

    def _validate_input(self, value: Any, expected_type: type, param_name: str) -> None:
        """Validate input parameters with type checking."""
        if not isinstance(value, expected_type):
            raise StrategyValidationError(
                f"Invalid type for {param_name}: expected {expected_type.__name__}, got {type(value).__name__}"
            )

    def _validate_strategy_data(self, strategy_data: Dict[str, Any]) -> None:
        """Validate strategy data structure."""
        self._validate_input(strategy_data, dict, "strategy_data")
        required_fields = ["strategy_name", "objectives", "timeline", "stakeholders"]
        for field in required_fields:
            if field not in strategy_data:
                raise StrategyValidationError(f"Missing required field: {field}")

    def _validate_market_data(self, market_data: Dict[str, Any]) -> None:
        """Validate market data structure."""
        self._validate_input(market_data, dict, "market_data")
        required_fields = ["market_size", "growth_rate", "key_players", "trends"]
        for field in required_fields:
            if field not in market_data:
                raise StrategyValidationError(f"Missing required field: {field}")

    def _load_strategy_history(self):
        """Load strategy history with comprehensive error handling."""
        try:
            if self.data_paths["strategy-history"].exists():
                with open(self.data_paths["strategy-history"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.strategy_history.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading strategy history: {e}")
            raise StrategyError(f"Cannot access strategy history file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading strategy history: {e}")
            raise StrategyError(f"Invalid encoding in strategy history file: {e}")
        except OSError as e:
            logger.error(f"OS error loading strategy history: {e}")
            raise StrategyError(f"System error loading strategy history: {e}")
        except Exception as e:
            logger.warning(f"Could not load strategy history: {e}")

    def _save_strategy_history(self):
        """Save strategy history with comprehensive error handling."""
        try:
            self.data_paths["strategy-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["strategy-history"], "w", encoding="utf-8") as f:
                f.write("# Strategy History\n\n")
                f.writelines(f"- {strategy}\n" for strategy in self.strategy_history[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving strategy history: {e}")
            raise StrategyError(f"Cannot write to strategy history file: {e}")
        except OSError as e:
            logger.error(f"OS error saving strategy history: {e}")
            raise StrategyError(f"System error saving strategy history: {e}")
        except Exception as e:
            logger.error(f"Could not save strategy history: {e}")

    def _load_market_data(self):
        """Load market data with comprehensive error handling."""
        try:
            if self.data_paths["market-data"].exists():
                with open(self.data_paths["market-data"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.market_data.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading market data: {e}")
            raise StrategyError(f"Cannot access market data file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading market data: {e}")
            raise StrategyError(f"Invalid encoding in market data file: {e}")
        except OSError as e:
            logger.error(f"OS error loading market data: {e}")
            raise StrategyError(f"System error loading market data: {e}")
        except Exception as e:
            logger.warning(f"Could not load market data: {e}")

    def _save_market_data(self):
        """Save market data with comprehensive error handling."""
        try:
            self.data_paths["market-data"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["market-data"], "w", encoding="utf-8") as f:
                f.write("# Market Data\n\n")
                f.writelines(f"- {data}\n" for data in self.market_data[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving market data: {e}")
            raise StrategyError(f"Cannot write to market data file: {e}")
        except OSError as e:
            logger.error(f"OS error saving market data: {e}")
            raise StrategyError(f"System error saving market data: {e}")
        except Exception as e:
            logger.error(f"Could not save market data: {e}")

    def _load_competitive_data(self):
        """Load competitive data with comprehensive error handling."""
        try:
            if self.data_paths["competitive-data"].exists():
                with open(self.data_paths["competitive-data"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.competitive_data.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading competitive data: {e}")
            raise StrategyError(f"Cannot access competitive data file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading competitive data: {e}")
            raise StrategyError(f"Invalid encoding in competitive data file: {e}")
        except OSError as e:
            logger.error(f"OS error loading competitive data: {e}")
            raise StrategyError(f"System error loading competitive data: {e}")
        except Exception as e:
            logger.warning(f"Could not load competitive data: {e}")

    def _save_competitive_data(self):
        """Save competitive data with comprehensive error handling."""
        try:
            self.data_paths["competitive-data"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["competitive-data"], "w", encoding="utf-8") as f:
                f.write("# Competitive Data\n\n")
                f.writelines(f"- {data}\n" for data in self.competitive_data[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving competitive data: {e}")
            raise StrategyError(f"Cannot write to competitive data file: {e}")
        except OSError as e:
            logger.error(f"OS error saving competitive data: {e}")
            raise StrategyError(f"System error saving competitive data: {e}")
        except Exception as e:
            logger.error(f"Could not save competitive data: {e}")

    def _load_risk_register(self):
        """Load risk register with comprehensive error handling."""
        try:
            if self.data_paths["risk-register"].exists():
                with open(self.data_paths["risk-register"], "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.risk_register.append(line.strip()[2:])
        except PermissionError as e:
            logger.error(f"Permission denied loading risk register: {e}")
            raise StrategyError(f"Cannot access risk register file: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode error loading risk register: {e}")
            raise StrategyError(f"Invalid encoding in risk register file: {e}")
        except OSError as e:
            logger.error(f"OS error loading risk register: {e}")
            raise StrategyError(f"System error loading risk register: {e}")
        except Exception as e:
            logger.warning(f"Could not load risk register: {e}")

    def _save_risk_register(self):
        """Save risk register with comprehensive error handling."""
        try:
            self.data_paths["risk-register"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["risk-register"], "w", encoding="utf-8") as f:
                f.write("# Risk Register\n\n")
                f.writelines(f"- {risk}\n" for risk in self.risk_register[-50:])
        except PermissionError as e:
            logger.error(f"Permission denied saving risk register: {e}")
            raise StrategyError(f"Cannot write to risk register file: {e}")
        except OSError as e:
            logger.error(f"OS error saving risk register: {e}")
            raise StrategyError(f"System error saving risk register: {e}")
        except Exception as e:
            logger.error(f"Could not save risk register: {e}")

    def _record_strategy_metric(self, metric_name: str, value: float, unit: str = "%") -> None:
        """Record strategy-specific metrics."""
        try:
            self.monitor._record_metric(self.agent_name, MetricType.SUCCESS_RATE, value, unit)
        except Exception as e:
            logger.warning(f"Could not record metric {metric_name}: {e}")

    def show_help(self):
        """Display help information."""
        help_text = """
StrategiePartner Agent Commands:
  help                    - Show this help message
  develop-strategy [name] - Develop a new strategy
  analyze-market [sector] - Analyze market conditions
  competitive-analysis [competitor] - Analyze competitors
  assess-risks [strategy] - Assess risks for a strategy
  stakeholder-analysis [project] - Analyze stakeholders
  create-roadmap [strategy] - Create strategic roadmap
  calculate-roi [strategy] - Calculate ROI for strategy
  business-model-canvas   - Generate business model canvas
  validate-idea [description] - Valideer en verfijn vage ideeën tot concrete plannen
  refine-idea [description] [data] - Verfijn idee op basis van aanvullende informatie
  create-epic-from-idea [idea] - Maak epic van gevalideerd idee voor ProductOwner en Scrummaster
  show-strategy-history   - Show strategy history
  show-market-data        - Show market data
  show-competitive-data   - Show competitive data
  show-risk-register      - Show risk register
  show-strategy-guide     - Show strategy guide
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Start the agent in event listening mode
  initialize-mcp           - Initialize MCP integration
  use-mcp-tool [tool_name] [parameters] - Use MCP tool for enhanced functionality
  get-mcp-status           - Get MCP status
  use-strategy-mcp-tools [strategy_data] - Use strategy-specific MCP tools
  check-dependencies       - Check dependencies for enhanced collaboration
  enhanced-collaborate     - Enhanced collaboration with other agents
  enhanced-security        - Enhanced security validation
  enhanced-performance     - Enhanced performance optimization
  trace-operation [operation_data] - Trace strategy operation
  trace-performance [performance_metrics] - Trace performance analysis
  trace-error [error_data] - Trace error analysis
  tracing-summary          - Show tracing summary
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content with comprehensive error handling."""
        try:
            self._validate_input(resource_type, str, "resource_type")
            
            if not resource_type.strip():
                raise StrategyValidationError("Resource type cannot be empty")
            
            resource_mapping = {
                "strategy-planning": self.template_paths["strategy-planning"],
                "market-analysis": self.template_paths["market-analysis"],
                "competitive-analysis": self.template_paths["competitive-analysis"],
                "business-model": self.template_paths["business-model"],
                "risk-assessment": self.template_paths["risk-assessment"],
                "stakeholder-analysis": self.template_paths["stakeholder-analysis"],
                "strategic-roadmap": self.template_paths["strategic-roadmap"],
                "strategy-guide": self.template_paths["strategy-guide"]
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

    async def develop_strategy(self, strategy_name: str = "Digital Transformation Strategy") -> Dict[str, Any]:
        """Develop a new strategy with comprehensive validation and error handling."""
        try:
            self._validate_input(strategy_name, str, "strategy_name")
            
            if not strategy_name.strip():
                raise StrategyValidationError("Strategy name cannot be empty")
            
            logger.info(f"Developing strategy: {strategy_name}")

            # Use MCP tools for enhanced strategy development
            strategy_data = {
                "strategy_name": strategy_name,
                "business_context": "Digital transformation initiative",
                "market_conditions": "Evolving technology landscape",
                "sector": "Technology",
                "market_size": "$500B",
                "growth_rate": "8.5%",
                "competitors": ["Company A", "Company B", "Company C"],
                "market_position": "Emerging",
                "competitive_advantage": "Innovation focus",
                "strategy": strategy_name,
                "risk_factors": ["Market volatility", "Technology changes"],
                "mitigation_strategies": ["Agile approach", "Continuous monitoring"]
            }
            
            enhanced_data = await self.use_enhanced_mcp_tools(strategy_data)

            # Simulate strategy development process
            time.sleep(1)
            
            result = {
                "strategy_name": strategy_name,
                "objectives": ["Increase market share", "Improve customer satisfaction", "Reduce costs"],
                "timeline": "12 months",
                "stakeholders": ["Management", "Employees", "Customers", "Investors"],
                "success_metrics": ["Revenue growth", "Customer retention", "Cost reduction"],
                "status": "developed",
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add MCP enhanced data if available
            if enhanced_data:
                result["mcp_enhanced_data"] = enhanced_data

            # Add to history
            strategy_entry = f"{result['timestamp']}: Strategy '{strategy_name}' developed - Timeline: {result['timeline']}"
            self.strategy_history.append(strategy_entry)
            self._save_strategy_history()

            # Update metrics
            self.performance_metrics["strategies_developed"] += 1
            self._record_strategy_metric("strategy_development_success", 95, "%")

            logger.info(f"Strategy development result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error developing strategy: {e}")
            raise
        except Exception as e:
            logger.error(f"Error developing strategy: {e}")
            self._record_strategy_metric("strategy_development_error", 5, "%")
            raise StrategyError(f"Failed to develop strategy: {e}")

    def analyze_market(self, sector: str = "Technology") -> Dict[str, Any]:
        """Analyze market conditions with comprehensive validation and error handling."""
        try:
            self._validate_input(sector, str, "sector")
            
            if not sector.strip():
                raise StrategyValidationError("Sector cannot be empty")
            
            logger.info(f"Analyzing market in sector: {sector}")

            # Simulate market analysis process
            time.sleep(1)
            
            result = {
                "sector": sector,
                "market_size": "$500B",
                "growth_rate": "8.5%",
                "key_players": ["Company A", "Company B", "Company C"],
                "trends": ["AI/ML", "Cloud Computing", "Cybersecurity"],
                "opportunities": ["Digital transformation", "Remote work solutions"],
                "threats": ["Economic uncertainty", "Regulatory changes"],
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to market data
            market_entry = f"{result['timestamp']}: Market analysis for {sector} - Size: {result['market_size']}, Growth: {result['growth_rate']}"
            self.market_data.append(market_entry)
            self._save_market_data()

            # Update metrics
            self.performance_metrics["market_analyses_completed"] += 1
            self._record_strategy_metric("market_analysis_success", 92, "%")

            logger.info(f"Market analysis result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error analyzing market: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
            self._record_strategy_metric("market_analysis_error", 8, "%")
            raise StrategyError(f"Failed to analyze market: {e}")

    def competitive_analysis(self, competitor: str = "Main Competitor") -> Dict[str, Any]:
        """Analyze competitors with comprehensive validation and error handling."""
        try:
            self._validate_input(competitor, str, "competitor")
            
            if not competitor.strip():
                raise StrategyValidationError("Competitor name cannot be empty")
            
            logger.info(f"Analyzing competitor: {competitor}")

            # Simulate competitive analysis process
            time.sleep(1)
            
            result = {
                "competitor": competitor,
                "market_share": "25%",
                "strengths": ["Strong brand", "Large customer base", "Innovation"],
                "weaknesses": ["High costs", "Slow decision making", "Legacy systems"],
                "opportunities": ["Market expansion", "Digital transformation"],
                "threats": ["New entrants", "Technology disruption"],
                "competitive_position": "strong",
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to competitive data
            competitive_entry = f"{result['timestamp']}: Competitive analysis for {competitor} - Market share: {result['market_share']}"
            self.competitive_data.append(competitive_entry)
            self._save_competitive_data()

            # Update metrics
            self.performance_metrics["competitive_analyses_completed"] += 1
            self._record_strategy_metric("competitive_analysis_success", 90, "%")

            logger.info(f"Competitive analysis result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error analyzing competitor: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing competitor: {e}")
            self._record_strategy_metric("competitive_analysis_error", 10, "%")
            raise StrategyError(f"Failed to analyze competitor: {e}")

    def assess_risks(self, strategy: str = "Digital Transformation") -> Dict[str, Any]:
        """Assess risks for a strategy with comprehensive validation and error handling."""
        try:
            self._validate_input(strategy, str, "strategy")
            
            if not strategy.strip():
                raise StrategyValidationError("Strategy name cannot be empty")
            
            logger.info(f"Assessing risks for strategy: {strategy}")

            # Simulate risk assessment process
            time.sleep(1)
            
            result = {
                "strategy": strategy,
                "high_risks": ["Technology failure", "Budget overruns", "Resistance to change"],
                "medium_risks": ["Timeline delays", "Resource constraints", "Market changes"],
                "low_risks": ["Minor technical issues", "Documentation delays"],
                "mitigation_strategies": ["Phased implementation", "Regular monitoring", "Stakeholder engagement"],
                "risk_score": "Medium",
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to risk register
            risk_entry = f"{result['timestamp']}: Risk assessment for {strategy} - Risk score: {result['risk_score']}"
            self.risk_register.append(risk_entry)
            self._save_risk_register()

            # Update metrics
            self.performance_metrics["risk_assessments_completed"] += 1
            self._record_strategy_metric("risk_assessment_success", 88, "%")

            logger.info(f"Risk assessment result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error assessing risks: {e}")
            raise
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            self._record_strategy_metric("risk_assessment_error", 12, "%")
            raise StrategyError(f"Failed to assess risks: {e}")

    def stakeholder_analysis(self, project: str = "Digital Transformation Project") -> Dict[str, Any]:
        """Analyze stakeholders with comprehensive validation and error handling."""
        try:
            self._validate_input(project, str, "project")
            
            if not project.strip():
                raise StrategyValidationError("Project name cannot be empty")
            
            logger.info(f"Analyzing stakeholders for project: {project}")

            # Simulate stakeholder analysis process
            time.sleep(1)
            
            result = {
                "project": project,
                "stakeholders": {
                    "internal": ["Management", "Employees", "IT Team"],
                    "external": ["Customers", "Suppliers", "Regulators"]
                },
                "influence_levels": {
                    "high": ["Management", "Customers"],
                    "medium": ["Employees", "Suppliers"],
                    "low": ["Regulators"]
                },
                "engagement_strategies": {
                    "Management": "Regular updates and involvement in decisions",
                    "Employees": "Training and communication",
                    "Customers": "Feedback sessions and surveys"
                },
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to strategy history
            stakeholder_entry = f"{result['timestamp']}: Stakeholder analysis for {project} - {len(result['stakeholders']['internal'])} internal, {len(result['stakeholders']['external'])} external stakeholders"
            self.strategy_history.append(stakeholder_entry)
            self._save_strategy_history()

            # Update metrics
            self._record_strategy_metric("stakeholder_analysis_success", 94, "%")

            logger.info(f"Stakeholder analysis result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error analyzing stakeholders: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing stakeholders: {e}")
            self._record_strategy_metric("stakeholder_analysis_error", 6, "%")
            raise StrategyError(f"Failed to analyze stakeholders: {e}")

    def create_roadmap(self, strategy: str = "Digital Transformation Strategy") -> Dict[str, Any]:
        """Create strategic roadmap with comprehensive validation and error handling."""
        try:
            self._validate_input(strategy, str, "strategy")
            
            if not strategy.strip():
                raise StrategyValidationError("Strategy name cannot be empty")
            
            logger.info(f"Creating roadmap for strategy: {strategy}")

            # Simulate roadmap creation process
            time.sleep(1)
            
            result = {
                "strategy": strategy,
                "phases": [
                    {
                        "phase": "Phase 1",
                        "duration": "3 months",
                        "objectives": ["Assessment", "Planning", "Stakeholder alignment"],
                        "deliverables": ["Current state analysis", "Strategy document", "Stakeholder buy-in"]
                    },
                    {
                        "phase": "Phase 2",
                        "duration": "6 months",
                        "objectives": ["Implementation", "Training", "Change management"],
                        "deliverables": ["Pilot implementation", "Training programs", "Change management plan"]
                    },
                    {
                        "phase": "Phase 3",
                        "duration": "3 months",
                        "objectives": ["Optimization", "Scaling", "Continuous improvement"],
                        "deliverables": ["Full implementation", "Performance metrics", "Improvement plan"]
                    }
                ],
                "total_duration": "12 months",
                "key_milestones": ["Strategy approval", "Pilot launch", "Full deployment"],
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to strategy history
            roadmap_entry = f"{result['timestamp']}: Roadmap created for {strategy} - Duration: {result['total_duration']}"
            self.strategy_history.append(roadmap_entry)
            self._save_strategy_history()

            # Update metrics
            self._record_strategy_metric("roadmap_creation_success", 96, "%")

            logger.info(f"Roadmap creation result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error creating roadmap: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating roadmap: {e}")
            self._record_strategy_metric("roadmap_creation_error", 4, "%")
            raise StrategyError(f"Failed to create roadmap: {e}")

    def calculate_roi(self, strategy: str = "Digital Transformation Strategy") -> Dict[str, Any]:
        """Calculate ROI for strategy with comprehensive validation and error handling."""
        try:
            self._validate_input(strategy, str, "strategy")
            
            if not strategy.strip():
                raise StrategyValidationError("Strategy name cannot be empty")
            
            logger.info(f"Calculating ROI for strategy: {strategy}")

            # Simulate ROI calculation process
            time.sleep(1)
            
            result = {
                "strategy": strategy,
                "investment": "$2,000,000",
                "expected_returns": "$3,500,000",
                "roi_percentage": "75%",
                "payback_period": "18 months",
                "npv": "$1,200,000",
                "irr": "25%",
                "risk_adjusted_roi": "60%",
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to strategy history
            roi_entry = f"{result['timestamp']}: ROI calculated for {strategy} - ROI: {result['roi_percentage']}, Payback: {result['payback_period']}"
            self.strategy_history.append(roi_entry)
            self._save_strategy_history()

            # Update metrics
            self._record_strategy_metric("roi_calculation_success", 93, "%")

            logger.info(f"ROI calculation result: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error calculating ROI: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calculating ROI: {e}")
            self._record_strategy_metric("roi_calculation_error", 7, "%")
            raise StrategyError(f"Failed to calculate ROI: {e}")

    def business_model_canvas(self) -> Dict[str, Any]:
        """Generate business model canvas with comprehensive error handling."""
        try:
            logger.info("Generating business model canvas")

            # Simulate business model canvas generation
            time.sleep(1)
            
            result = {
                "key_partners": ["Technology providers", "Consulting firms", "Training partners"],
                "key_activities": ["Software development", "Consulting services", "Training delivery"],
                "key_resources": ["Technical expertise", "Customer relationships", "Intellectual property"],
                "value_propositions": ["Cost reduction", "Efficiency improvement", "Innovation"],
                "customer_relationships": ["Long-term partnerships", "Consultative approach", "Ongoing support"],
                "channels": ["Direct sales", "Online platform", "Partner network"],
                "customer_segments": ["Enterprise clients", "Mid-market companies", "Startups"],
                "cost_structure": ["Personnel costs", "Technology infrastructure", "Marketing"],
                "revenue_streams": ["Software licenses", "Consulting fees", "Training services"],
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }

            # Add to strategy history
            canvas_entry = f"{result['timestamp']}: Business model canvas generated - {len(result['customer_segments'])} customer segments identified"
            self.strategy_history.append(canvas_entry)
            self._save_strategy_history()

            # Update metrics
            self._record_strategy_metric("business_model_canvas_success", 91, "%")

            logger.info(f"Business model canvas result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating business model canvas: {e}")
            self._record_strategy_metric("business_model_canvas_error", 9, "%")
            raise StrategyError(f"Failed to generate business model canvas: {e}")

    def validate_idea(self, idea_description: str) -> Dict[str, Any]:
        """Validate and refine vague ideas into concrete plans."""
        try:
            self._validate_input(idea_description, str, "idea_description")
            
            if not idea_description.strip():
                raise StrategyValidationError("Idea description cannot be empty")
            
            logger.info(f"Validating idea: {idea_description}")
            
            # Simulate idea validation process
            time.sleep(1)
            
            # Analyze idea completeness
            completeness_score = self._analyze_idea_completeness(idea_description)
            
            # Generate refinement questions
            refinement_questions = self._generate_refinement_questions(idea_description)
            
            # Create validation report
            result = {
                "idea_description": idea_description,
                "completeness_score": completeness_score,
                "validation_status": "needs_refinement" if completeness_score < 80 else "ready_for_development",
                "missing_elements": self._identify_missing_elements(idea_description),
                "refinement_questions": refinement_questions,
                "next_steps": self._suggest_next_steps(completeness_score),
                "estimated_effort": self._estimate_effort(idea_description),
                "risk_assessment": self._assess_idea_risks(idea_description),
                "stakeholder_impact": self._analyze_stakeholder_impact(idea_description),
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }
            
            self._record_strategy_metric("ideas_validated", 92, "%")
            
            logger.info(f"Idea validation completed: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error validating idea: {e}")
            raise
        except Exception as e:
            logger.error(f"Error validating idea: {e}")
            self._record_strategy_metric("idea_validation_error", 8, "%")
            raise StrategyError(f"Failed to validate idea: {e}")

    def refine_idea(self, idea_description: str, refinement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refine idea based on additional information and feedback."""
        try:
            self._validate_input(idea_description, str, "idea_description")
            self._validate_input(refinement_data, dict, "refinement_data")
            
            if not idea_description.strip():
                raise StrategyValidationError("Idea description cannot be empty")
            
            logger.info(f"Refining idea: {idea_description}")
            
            # Simulate idea refinement process
            time.sleep(1)
            
            # Combine original idea with refinement data
            refined_idea = self._combine_idea_with_refinement(idea_description, refinement_data)
            
            # Re-validate refined idea
            refined_validation = self.validate_idea(refined_idea)
            # Add original idea description to refined validation for epic creation
            refined_validation["idea_description"] = refined_idea
            
            # Create refinement report
            result = {
                "original_idea": idea_description,
                "refinement_data": refinement_data,
                "refined_idea": refined_idea,
                "refined_validation": refined_validation,
                "improvement_score": refined_validation["completeness_score"] - self._analyze_idea_completeness(idea_description),
                "refinement_actions": self._document_refinement_actions(refinement_data),
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }
            
            self._record_strategy_metric("ideas_refined", 88, "%")
            
            logger.info(f"Idea refinement completed: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error refining idea: {e}")
            raise
        except Exception as e:
            logger.error(f"Error refining idea: {e}")
            self._record_strategy_metric("idea_refinement_error", 12, "%")
            raise StrategyError(f"Failed to refine idea: {e}")

    def create_epic_from_idea(self, validated_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Create epic from validated idea for ProductOwner and Scrummaster."""
        try:
            self._validate_input(validated_idea, dict, "validated_idea")
            
            if validated_idea.get("validation_status") != "ready_for_development":
                raise StrategyValidationError("Idea must be validated before creating epic")
            
            logger.info("Creating epic from validated idea...")
            
            # Simulate epic creation process
            time.sleep(1)
            
            # Generate epic structure
            epic = self._generate_epic_structure(validated_idea)
            
            # Create PBIs (Product Backlog Items)
            pbis = self._generate_pbis(validated_idea)
            
            # Estimate story points
            story_points = self._estimate_story_points(pbis)
            
            # Create epic result
            result = {
                "epic": epic,
                "product_backlog_items": pbis,
                "total_story_points": story_points,
                "estimated_sprints": self._estimate_sprints(story_points),
                "priority": self._determine_priority(validated_idea),
                "dependencies": self._identify_dependencies(pbis),
                "acceptance_criteria": self._generate_acceptance_criteria(epic),
                "success_metrics": self._define_success_metrics(validated_idea),
                "timestamp": datetime.now().isoformat(),
                "agent": "StrategiePartnerAgent"
            }
            
            self._record_strategy_metric("epics_created", 90, "%")
            
            logger.info(f"Epic created from idea: {result}")
            return result
            
        except StrategyValidationError as e:
            logger.error(f"Validation error creating epic: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating epic: {e}")
            self._record_strategy_metric("epic_creation_error", 10, "%")
            raise StrategyError(f"Failed to create epic: {e}")

    def _analyze_idea_completeness(self, idea_description: str) -> float:
        """Analyze idea completeness and return score (0-100)."""
        # Simple completeness analysis based on key elements
        completeness_factors = {
            "problem_statement": 25,
            "solution_approach": 25,
            "target_audience": 20,
            "value_proposition": 20,
            "implementation_plan": 10
        }
        
        score = 0
        idea_lower = idea_description.lower()
        
        if any(word in idea_lower for word in ["problem", "issue", "challenge", "need"]):
            score += completeness_factors["problem_statement"]
        if any(word in idea_lower for word in ["solution", "approach", "method", "strategy"]):
            score += completeness_factors["solution_approach"]
        if any(word in idea_lower for word in ["user", "customer", "audience", "target"]):
            score += completeness_factors["target_audience"]
        if any(word in idea_lower for word in ["value", "benefit", "advantage", "improvement"]):
            score += completeness_factors["value_proposition"]
        if any(word in idea_lower for word in ["implement", "plan", "timeline", "steps"]):
            score += completeness_factors["implementation_plan"]
        
        return min(score, 100)

    def _generate_refinement_questions(self, idea_description: str) -> List[str]:
        """Generate questions to refine the idea."""
        questions = []
        idea_lower = idea_description.lower()
        
        if "problem" not in idea_lower and "issue" not in idea_lower:
            questions.append("What specific problem or challenge does this idea address?")
        
        if "user" not in idea_lower and "customer" not in idea_lower:
            questions.append("Who is the target audience or user for this idea?")
        
        if "value" not in idea_lower and "benefit" not in idea_lower:
            questions.append("What value or benefit does this idea provide?")
        
        if "implement" not in idea_lower and "plan" not in idea_lower:
            questions.append("What are the key implementation steps or timeline?")
        
        if "cost" not in idea_lower and "budget" not in idea_lower:
            questions.append("What are the estimated costs and resource requirements?")
        
        if "risk" not in idea_lower and "challenge" not in idea_lower:
            questions.append("What are the potential risks or challenges?")
        
        return questions

    def _identify_missing_elements(self, idea_description: str) -> List[str]:
        """Identify missing elements in the idea."""
        missing = []
        idea_lower = idea_description.lower()
        
        if "problem" not in idea_lower and "issue" not in idea_lower:
            missing.append("Problem statement")
        if "user" not in idea_lower and "customer" not in idea_lower:
            missing.append("Target audience definition")
        if "value" not in idea_lower and "benefit" not in idea_lower:
            missing.append("Value proposition")
        if "implement" not in idea_lower and "plan" not in idea_lower:
            missing.append("Implementation plan")
        if "cost" not in idea_lower and "budget" not in idea_lower:
            missing.append("Cost estimation")
        
        return missing

    def _suggest_next_steps(self, completeness_score: float) -> List[str]:
        """Suggest next steps based on completeness score."""
        if completeness_score >= 80:
            return [
                "Create epic and PBIs",
                "Present to ProductOwner for approval",
                "Schedule sprint planning with Scrummaster"
            ]
        elif completeness_score >= 60:
            return [
                "Gather additional requirements",
                "Conduct stakeholder interviews",
                "Refine idea based on feedback"
            ]
        else:
            return [
                "Define problem statement clearly",
                "Identify target audience",
                "Research similar solutions",
                "Gather more information"
            ]

    def _estimate_effort(self, idea_description: str) -> Dict[str, Any]:
        """Estimate effort for idea implementation."""
        # Simple effort estimation based on idea complexity
        word_count = len(idea_description.split())
        complexity_score = min(word_count / 10, 10)  # Scale complexity
        
        return {
            "complexity": complexity_score,
            "estimated_story_points": int(complexity_score * 3),
            "estimated_sprints": max(1, int(complexity_score / 2)),
            "confidence_level": "medium"
        }

    def _assess_idea_risks(self, idea_description: str) -> List[Dict[str, Any]]:
        """Assess risks associated with the idea."""
        risks = []
        idea_lower = idea_description.lower()
        
        if "new" in idea_lower or "innovative" in idea_lower:
            risks.append({
                "risk": "Technology uncertainty",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Proof of concept development"
            })
        
        if "user" in idea_lower or "customer" in idea_lower:
            risks.append({
                "risk": "User adoption",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "User research and testing"
            })
        
        if "cost" in idea_lower or "budget" in idea_lower:
            risks.append({
                "risk": "Budget overrun",
                "probability": "low",
                "impact": "high",
                "mitigation": "Detailed cost analysis"
            })
        
        return risks

    def _analyze_stakeholder_impact(self, idea_description: str) -> Dict[str, Any]:
        """Analyze stakeholder impact of the idea."""
        return {
            "primary_stakeholders": ["End Users", "Development Team", "Business Stakeholders"],
            "impact_level": "medium",
            "change_management_required": True,
            "communication_needs": ["Regular updates", "Training sessions", "Feedback collection"]
        }

    def _combine_idea_with_refinement(self, original_idea: str, refinement_data: Dict[str, Any]) -> str:
        """Combine original idea with refinement data."""
        refined_idea = original_idea
        
        # Add missing elements from refinement data
        if "problem_statement" in refinement_data:
            refined_idea += f"\n\nProblem Statement: {refinement_data['problem_statement']}"
        if "target_audience" in refinement_data:
            refined_idea += f"\n\nTarget Audience: {refinement_data['target_audience']}"
        if "value_proposition" in refinement_data:
            refined_idea += f"\n\nValue Proposition: {refinement_data['value_proposition']}"
        if "implementation_plan" in refinement_data:
            refined_idea += f"\n\nImplementation Plan: {refinement_data['implementation_plan']}"
        
        return refined_idea

    def _document_refinement_actions(self, refinement_data: Dict[str, Any]) -> List[str]:
        """Document refinement actions taken."""
        actions = []
        for key, value in refinement_data.items():
            actions.append(f"Added {key}: {value}")
        return actions

    def _generate_epic_structure(self, validated_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Generate epic structure from validated idea."""
        # Get idea description from validated idea or use default
        idea_description = validated_idea.get("idea_description", "A validated idea ready for development")
        
        return {
            "epic_name": f"Epic: {idea_description[:50]}...",
            "epic_description": idea_description,
            "epic_goals": [
                "Implement the proposed solution",
                "Deliver value to target audience",
                "Achieve success metrics"
            ],
            "epic_acceptance_criteria": [
                "Solution is implemented and functional",
                "Target audience can use the solution",
                "Success metrics are achieved"
            ]
        }

    def _generate_pbis(self, validated_idea: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Product Backlog Items from validated idea."""
        return [
            {
                "pbi_id": "PBI-001",
                "title": "Research and Analysis",
                "description": "Conduct research and analysis for the idea",
                "story_points": 3,
                "priority": "high"
            },
            {
                "pbi_id": "PBI-002",
                "title": "Design and Architecture",
                "description": "Design the solution architecture",
                "story_points": 5,
                "priority": "high"
            },
            {
                "pbi_id": "PBI-003",
                "title": "Implementation",
                "description": "Implement the core solution",
                "story_points": 8,
                "priority": "medium"
            },
            {
                "pbi_id": "PBI-004",
                "title": "Testing and Validation",
                "description": "Test and validate the solution",
                "story_points": 3,
                "priority": "medium"
            }
        ]

    def _estimate_story_points(self, pbis: List[Dict[str, Any]]) -> int:
        """Estimate total story points for PBIs."""
        return sum(pbi.get("story_points", 0) for pbi in pbis)

    def _estimate_sprints(self, story_points: int) -> int:
        """Estimate number of sprints needed."""
        velocity_per_sprint = 13  # Average story points per sprint
        return max(1, int(story_points / velocity_per_sprint))

    def _determine_priority(self, validated_idea: Dict[str, Any]) -> str:
        """Determine priority based on idea characteristics."""
        if validated_idea.get("completeness_score", 0) >= 90:
            return "high"
        elif validated_idea.get("completeness_score", 0) >= 70:
            return "medium"
        else:
            return "low"

    def _identify_dependencies(self, pbis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify dependencies between PBIs."""
        return [
            {
                "from_pbi": "PBI-001",
                "to_pbi": "PBI-002",
                "dependency_type": "finish-to-start"
            },
            {
                "from_pbi": "PBI-002",
                "to_pbi": "PBI-003",
                "dependency_type": "finish-to-start"
            }
        ]

    def _generate_acceptance_criteria(self, epic: Dict[str, Any]) -> List[str]:
        """Generate acceptance criteria for epic."""
        return [
            "Solution meets all functional requirements",
            "Solution is user-friendly and accessible",
            "Solution performs within acceptable parameters",
            "Solution is properly tested and validated"
        ]

    def _define_success_metrics(self, validated_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Define success metrics for the idea."""
        return {
            "user_adoption_rate": "Target: 80%",
            "performance_improvement": "Target: 25%",
            "user_satisfaction": "Target: 4.5/5",
            "time_to_market": "Target: 3 sprints"
        }

    def show_strategy_history(self):
        """Show strategy history."""
        if not self.strategy_history:
            print("No strategy history available.")
            return
        print("Strategy History:")
        print("=" * 50)
        for i, strategy in enumerate(self.strategy_history[-10:], 1):
            print(f"{i}. {strategy}")

    def show_market_data(self):
        """Show market data."""
        if not self.market_data:
            print("No market data available.")
            return
        print("Market Data:")
        print("=" * 50)
        for i, data in enumerate(self.market_data[-10:], 1):
            print(f"{i}. {data}")

    def show_competitive_data(self):
        """Show competitive data."""
        if not self.competitive_data:
            print("No competitive data available.")
            return
        print("Competitive Data:")
        print("=" * 50)
        for i, data in enumerate(self.competitive_data[-10:], 1):
            print(f"{i}. {data}")

    def show_risk_register(self):
        """Show risk register."""
        if not self.risk_register:
            print("No risk register available.")
            return
        print("Risk Register:")
        print("=" * 50)
        for i, risk in enumerate(self.risk_register[-10:], 1):
            print(f"{i}. {risk}")

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

    async def collaborate_example(self):
        """Demonstrate collaboration with other agents with async optimization."""
        logger.info("Starting async collaboration example...")

        try:
            # Use asyncio.gather for parallel execution of all operations
            tasks = [
                self._async_develop_strategy("Digital Transformation Strategy"),
                self._async_analyze_market("Technology"),
                self._async_competitive_analysis("Main Competitor"),
                self._async_assess_risks("Digital Transformation"),
                self._async_stakeholder_analysis("Digital Transformation Project"),
                self._async_create_roadmap("Digital Transformation Strategy"),
                self._async_calculate_roi("Digital Transformation Strategy"),
                self._async_business_model_canvas()
            ]
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Unpack results
            strategy_result, market_result, competitive_result, risk_result, \
            stakeholder_result, roadmap_result, roi_result, canvas_result = results
            
            # Check for errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Task {i} failed: {result}")
                    raise result
            
            # Publish events (can be done in parallel too)
            publish_tasks = [
                self._async_publish_event("strategy_developed", strategy_result),
                self._async_publish_event("market_analyzed", market_result),
                self._async_publish_event("competitive_analysis_completed", competitive_result),
                self._async_publish_event("risk_assessment_completed", risk_result),
                self._async_publish_event("stakeholder_analysis_completed", stakeholder_result),
                self._async_publish_event("roadmap_created", roadmap_result),
                self._async_publish_event("roi_calculated", roi_result),
                self._async_publish_event("business_model_canvas_generated", canvas_result)
            ]
            
            await asyncio.gather(*publish_tasks, return_exceptions=True)

            # Notify via Slack (async)
            try:
                await self._async_send_slack_message(
                    f"Strategy '{strategy_result['strategy_name']}' developed with {roi_result['roi_percentage']} ROI"
                )
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")

            logger.info("Async collaboration example completed successfully")
            
        except Exception as e:
            logger.error(f"Error in async collaboration example: {e}")
            raise StrategyError(f"Async collaboration example failed: {e}")
    
    # Async wrapper methods for parallel execution
    async def _async_develop_strategy(self, strategy_name: str):
        """Async wrapper for develop_strategy."""
        return await self.develop_strategy(strategy_name)
    
    async def _async_analyze_market(self, sector: str):
        """Async wrapper for analyze_market."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_market, sector)
    
    async def _async_competitive_analysis(self, competitor: str):
        """Async wrapper for competitive_analysis."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.competitive_analysis, competitor)
    
    async def _async_assess_risks(self, strategy: str):
        """Async wrapper for assess_risks."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.assess_risks, strategy)
    
    async def _async_stakeholder_analysis(self, project: str):
        """Async wrapper for stakeholder_analysis."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.stakeholder_analysis, project)
    
    async def _async_create_roadmap(self, strategy: str):
        """Async wrapper for create_roadmap."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.create_roadmap, strategy)
    
    async def _async_calculate_roi(self, strategy: str):
        """Async wrapper for calculate_roi."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.calculate_roi, strategy)
    
    async def _async_business_model_canvas(self):
        """Async wrapper for business_model_canvas."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.business_model_canvas)
    
    async def _async_publish_event(self, event_type: str, data: Dict[str, Any]):
        """Async wrapper for publish."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, publish, event_type, data)
    
    async def _async_send_slack_message(self, message: str):
        """Async wrapper for send_slack_message."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, send_slack_message, message)

    def handle_alignment_check_completed(self, event):
        """Handle alignment check completed event."""
        try:
            logger.info(f"Alignment check completed: {event}")
            self.monitor.log_metric("alignment_check", event)
            allowed = self.policy_engine.evaluate_policy("alignment", event)
            logger.info(f"Policy evaluation result: {allowed}")
        except Exception as e:
            logger.error(f"Error handling alignment check completed: {e}")

    def handle_strategy_development_requested(self, event):
        """Handle strategy development requested event."""
        try:
            logger.info(f"Strategy development requested: {event}")
            strategy_name = event.get("strategy_name", "Default Strategy")
            self.develop_strategy(strategy_name)
        except Exception as e:
            logger.error(f"Error handling strategy development requested: {e}")

    def handle_idea_validation_requested(self, event):
        """Handle idea validation requested event."""
        try:
            logger.info(f"Idea validation requested: {event}")
            idea_description = event.get("idea_description", "A new mobile app for task management")
            result = self.validate_idea(idea_description)
            
            # Publish validation result
            publish("idea_validation_completed", {
                "agent": "StrategiePartnerAgent",
                "idea_description": idea_description,
                "validation_result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Idea validation completed: {result}")
        except Exception as e:
            logger.error(f"Error handling idea validation requested: {e}")

    def handle_idea_refinement_requested(self, event):
        """Handle idea refinement requested event."""
        try:
            logger.info(f"Idea refinement requested: {event}")
            idea_description = event.get("idea_description", "A mobile app")
            refinement_data = event.get("refinement_data", {})
            result = self.refine_idea(idea_description, refinement_data)
            
            # Publish refinement result
            publish("idea_refinement_completed", {
                "agent": "StrategiePartnerAgent",
                "idea_description": idea_description,
                "refinement_result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Idea refinement completed: {result}")
        except Exception as e:
            logger.error(f"Error handling idea refinement requested: {e}")

    def handle_epic_creation_requested(self, event):
        """Handle epic creation requested event."""
        try:
            logger.info(f"Epic creation requested: {event}")
            validated_idea = event.get("validated_idea", {})
            result = self.create_epic_from_idea(validated_idea)
            
            # Publish epic creation result
            publish("epic_creation_completed", {
                "agent": "StrategiePartnerAgent",
                "validated_idea": validated_idea,
                "epic_result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Epic creation completed: {result}")
        except Exception as e:
            logger.error(f"Error handling epic creation requested: {e}")

    async def run(self):
        """Start the agent in event listening mode."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize Message Bus Integration
        await self.initialize_message_bus_integration()
        
        print("🎯 StrategiePartner Agent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        subscribe("alignment_check_completed", self.handle_alignment_check_completed)
        subscribe("strategy_development_requested", self.handle_strategy_development_requested)
        subscribe("strategiepartner_validate_idea", self.handle_idea_validation_requested)
        subscribe("strategiepartner_refine_idea", self.handle_idea_refinement_requested)
        subscribe("strategiepartner_create_epic", self.handle_epic_creation_requested)

        logger.info("StrategiePartnerAgent ready and listening for events...")
        await self.collaborate_example()

    @classmethod
    async def run_agent(cls):
        """Class method to run the agent with proper async setup."""
        agent = cls()
        await agent.run()
        return agent

def main():
    """Main CLI function with comprehensive error handling."""
    parser = argparse.ArgumentParser(description="StrategiePartner Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "develop-strategy", "analyze-market", "competitive-analysis",
                               "assess-risks", "stakeholder-analysis", "create-roadmap", "calculate-roi",
                               "business-model-canvas", "validate-idea", "refine-idea", "create-epic-from-idea",
                               "show-strategy-history", "show-market-data", "show-competitive-data", 
                               "show-risk-register", "show-strategy-guide", "test", "collaborate", "run",
                               "initialize-mcp", "use-mcp-tool", "get-mcp-status", "use-strategy-mcp-tools", 
                               "check-dependencies", "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary"])
    parser.add_argument("--strategy-name", default="Digital Transformation Strategy", help="Strategy name")
    parser.add_argument("--sector", default="Technology", help="Market sector")
    parser.add_argument("--competitor", default="Main Competitor", help="Competitor name")
    parser.add_argument("--project", default="Digital Transformation Project", help="Project name")
    parser.add_argument("--idea-description", default="A new mobile app for task management", help="Idea description")
    parser.add_argument("--refinement-data", default='{"problem_statement": "Users need better task organization"}', help="Refinement data as JSON")
    parser.add_argument("--validated-idea", default='{"validation_status": "ready_for_development"}', help="Validated idea as JSON")

    args = parser.parse_args()

    try:
        agent = StrategiePartnerAgent()

        if args.command == "help":
            agent.show_help()
        elif args.command == "develop-strategy":
            result = asyncio.run(agent.develop_strategy(args.strategy_name))
            print(f"Strategy developed successfully: {result}")
        elif args.command == "analyze-market":
            result = agent.analyze_market(args.sector)
            print(f"Market analysis completed: {result}")
        elif args.command == "competitive-analysis":
            result = agent.competitive_analysis(args.competitor)
            print(f"Competitive analysis completed: {result}")
        elif args.command == "assess-risks":
            result = agent.assess_risks(args.strategy_name)
            print(f"Risk assessment completed: {result}")
        elif args.command == "stakeholder-analysis":
            result = agent.stakeholder_analysis(args.project)
            print(f"Stakeholder analysis completed: {result}")
        elif args.command == "create-roadmap":
            result = agent.create_roadmap(args.strategy_name)
            print(f"Roadmap created successfully: {result}")
        elif args.command == "calculate-roi":
            result = agent.calculate_roi(args.strategy_name)
            print(f"ROI calculated: {result}")
        elif args.command == "business-model-canvas":
            result = agent.business_model_canvas()
            print(f"Business model canvas generated: {result}")
        elif args.command == "validate-idea":
            result = agent.validate_idea(args.idea_description)
            print(f"Idea validation completed: {result}")
        elif args.command == "refine-idea":
            refinement_data = json.loads(args.refinement_data)
            result = agent.refine_idea(args.idea_description, refinement_data)
            print(f"Idea refinement completed: {result}")
        elif args.command == "create-epic-from-idea":
            validated_idea = json.loads(args.validated_idea)
            result = agent.create_epic_from_idea(validated_idea)
            print(f"Epic created from idea: {result}")
        elif args.command == "show-strategy-history":
            agent.show_strategy_history()
        elif args.command == "show-market-data":
            agent.show_market_data()
        elif args.command == "show-competitive-data":
            agent.show_competitive_data()
        elif args.command == "show-risk-register":
            agent.show_risk_register()
        elif args.command == "show-strategy-guide":
            agent.show_resource("strategy-guide")
        elif args.command == "test":
            success = agent.test_resource_completeness()
            if success:
                print("Resource completeness test passed!")
            else:
                print("Resource completeness test failed!")
        elif args.command == "collaborate":
            asyncio.run(agent.collaborate_example())
        elif args.command == "run":
            agent = asyncio.run(StrategiePartnerAgent.run_agent())
        # Enhanced MCP Phase 2 Commands
        elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                             "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
            # Enhanced MCP commands
            if args.command == "enhanced-collaborate":
                result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "Architect", "QualityGuardian", "Scrummaster"], 
                    {"type": "strategy_review", "content": {"review_type": "strategy_development"}}
                ))
                print(json.dumps(result, indent=2))
            elif args.command == "enhanced-security":
                result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                    "strategy_data": {"strategies": ["Digital Transformation", "Market Expansion"]},
                    "security_requirements": ["data_protection", "compliance", "risk_mitigation"]
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "enhanced-performance":
                result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                    "strategy_data": {"strategies": ["Digital Transformation", "Market Expansion"]},
                    "performance_metrics": {"roi": 25.5, "time_to_market": 6.2}
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "trace-operation":
                result = asyncio.run(agent.trace_strategy_operation({
                    "operation_type": "strategy_development",
                    "strategies": ["Digital Transformation", "Market Expansion"],
                    "market_analysis": ["Technology", "Healthcare"]
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "trace-performance":
                result = asyncio.run(agent.trace_strategy_operation({
                    "operation_type": "performance_analysis",
                    "performance_metrics": {"roi": 25.5, "time_to_market": 6.2}
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "trace-error":
                result = asyncio.run(agent.trace_strategy_operation({
                    "operation_type": "error_analysis",
                    "error_data": {"error_type": "strategy_validation", "error_message": "Market analysis incomplete"}
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "tracing-summary":
                print("Tracing Summary for StrategiePartner Agent:")
                print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
                print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
                print(f"Agent: {agent.agent_name}")
        else:
            print(f"Unknown command: {args.command}")
            agent.show_help()
    except StrategyValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except StrategyError as e:
        print(f"Strategy error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
