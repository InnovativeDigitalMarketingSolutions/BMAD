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
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "StrategiePartnerAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())

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
  show-strategy-history   - Show strategy history
  show-market-data        - Show market data
  show-competitive-data   - Show competitive data
  show-risk-register      - Show risk register
  calculate-roi [strategy] - Calculate ROI for strategy
  business-model-canvas   - Generate business model canvas
  show-strategy-guide     - Show strategy guide
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Start the agent in event listening mode
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

    def develop_strategy(self, strategy_name: str = "Digital Transformation Strategy") -> Dict[str, Any]:
        """Develop a new strategy with comprehensive validation and error handling."""
        try:
            self._validate_input(strategy_name, str, "strategy_name")
            
            if not strategy_name.strip():
                raise StrategyValidationError("Strategy name cannot be empty")
            
            logger.info(f"Developing strategy: {strategy_name}")

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

    def collaborate_example(self):
        """Demonstrate collaboration with other agents."""
        logger.info("Starting collaboration example...")

        try:
            # Develop strategy
            strategy_result = self.develop_strategy("Digital Transformation Strategy")
            
            # Analyze market
            market_result = self.analyze_market("Technology")
            
            # Competitive analysis
            competitive_result = self.competitive_analysis("Main Competitor")
            
            # Risk assessment
            risk_result = self.assess_risks("Digital Transformation")
            
            # Stakeholder analysis
            stakeholder_result = self.stakeholder_analysis("Digital Transformation Project")
            
            # Create roadmap
            roadmap_result = self.create_roadmap("Digital Transformation Strategy")
            
            # Calculate ROI
            roi_result = self.calculate_roi("Digital Transformation Strategy")
            
            # Generate business model canvas
            canvas_result = self.business_model_canvas()
            
            # Publish events
            publish("strategy_developed", strategy_result)
            publish("market_analyzed", market_result)
            publish("competitive_analysis_completed", competitive_result)
            publish("risk_assessment_completed", risk_result)
            publish("stakeholder_analysis_completed", stakeholder_result)
            publish("roadmap_created", roadmap_result)
            publish("roi_calculated", roi_result)
            publish("business_model_canvas_generated", canvas_result)

            # Notify via Slack
            try:
                send_slack_message(f"Strategy '{strategy_result['strategy_name']}' developed with {roi_result['roi_percentage']} ROI")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")

            logger.info("Collaboration example completed successfully")
            
        except Exception as e:
            logger.error(f"Error in collaboration example: {e}")
            raise StrategyError(f"Collaboration example failed: {e}")

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

    def run(self):
        """Start the agent in event listening mode."""
        subscribe("alignment_check_completed", self.handle_alignment_check_completed)
        subscribe("strategy_development_requested", self.handle_strategy_development_requested)

        logger.info("StrategiePartnerAgent ready and listening for events...")
        self.collaborate_example()

def main():
    """Main CLI function with comprehensive error handling."""
    parser = argparse.ArgumentParser(description="StrategiePartner Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "develop-strategy", "analyze-market", "competitive-analysis",
                               "assess-risks", "stakeholder-analysis", "create-roadmap", "calculate-roi",
                               "business-model-canvas", "show-strategy-history", "show-market-data",
                               "show-competitive-data", "show-risk-register", "show-strategy-guide",
                               "test", "collaborate", "run"])
    parser.add_argument("--strategy-name", default="Digital Transformation Strategy", help="Strategy name")
    parser.add_argument("--sector", default="Technology", help="Market sector")
    parser.add_argument("--competitor", default="Main Competitor", help="Competitor name")
    parser.add_argument("--project", default="Digital Transformation Project", help="Project name")

    args = parser.parse_args()

    try:
        agent = StrategiePartnerAgent()

        if args.command == "help":
            agent.show_help()
        elif args.command == "develop-strategy":
            result = agent.develop_strategy(args.strategy_name)
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
            agent.collaborate_example()
        elif args.command == "run":
            agent.run()
            
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
