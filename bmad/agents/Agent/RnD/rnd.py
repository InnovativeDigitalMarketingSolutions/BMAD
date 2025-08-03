import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import csv
import hashlib
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

class RnDAgent:
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        try:
            self.rnd_template = self.framework_manager.get_framework_template('rnd')
        except:
            self.rnd_template = None
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "RnD"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/rnd/best-practices.md",
            "experiment-template": self.resource_base / "templates/rnd/experiment-template.md",
            "research-template": self.resource_base / "templates/rnd/research-template.md",
            "innovation-template": self.resource_base / "templates/rnd/innovation-template.md",
            "prototype-template": self.resource_base / "templates/rnd/prototype-template.md",
            "evaluation-template": self.resource_base / "templates/rnd/evaluation-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/rnd/changelog.md",
            "experiment-history": self.resource_base / "data/rnd/experiment-history.md",
            "research-history": self.resource_base / "data/rnd/research-history.md"
        }

        # Initialize history
        self.experiment_history = []
        self.research_history = []
        self._load_experiment_history()
        self._load_research_history()
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced research and development capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for RnD")
        except Exception as e:
            logger.warning(f"MCP initialization failed for RnD: {e}")
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
    
    async def use_rnd_specific_mcp_tools(self, rnd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use R&D-specific MCP tools voor enhanced research and development."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Research analysis
            research_result = await self.use_mcp_tool("research_analysis", {
                "research_topic": rnd_data.get("research_topic", ""),
                "research_type": rnd_data.get("research_type", ""),
                "research_data": rnd_data.get("research_data", {}),
                "analysis_type": "rnd"
            })
            if research_result:
                enhanced_data["research_analysis"] = research_result
            
            # Experiment design
            experiment_result = await self.use_mcp_tool("experiment_design", {
                "experiment_name": rnd_data.get("experiment_name", ""),
                "hypothesis": rnd_data.get("hypothesis", ""),
                "experiment_type": rnd_data.get("experiment_type", "pilot"),
                "success_criteria": rnd_data.get("success_criteria", [])
            })
            if experiment_result:
                enhanced_data["experiment_design"] = experiment_result
            
            # Innovation generation
            innovation_result = await self.use_mcp_tool("innovation_generation", {
                "innovation_area": rnd_data.get("innovation_area", ""),
                "focus_area": rnd_data.get("focus_area", ""),
                "constraints": rnd_data.get("constraints", []),
                "opportunities": rnd_data.get("opportunities", [])
            })
            if innovation_result:
                enhanced_data["innovation_generation"] = innovation_result
            
            # Prototype development
            prototype_result = await self.use_mcp_tool("prototype_development", {
                "prototype_name": rnd_data.get("prototype_name", ""),
                "solution_type": rnd_data.get("solution_type", ""),
                "requirements": rnd_data.get("requirements", []),
                "technology_stack": rnd_data.get("technology_stack", [])
            })
            if prototype_result:
                enhanced_data["prototype_development"] = prototype_result
            
            # Results evaluation
            evaluation_result = await self.use_mcp_tool("results_evaluation", {
                "experiment_results": rnd_data.get("experiment_results", {}),
                "success_metrics": rnd_data.get("success_metrics", []),
                "evaluation_criteria": rnd_data.get("evaluation_criteria", [])
            })
            if evaluation_result:
                enhanced_data["results_evaluation"] = evaluation_result
            
            logger.info(f"R&D-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in R&D-specific MCP tools: {e}")
        
        return enhanced_data

    def _load_experiment_history(self):
        """Load experiment history from data file"""
        try:
            if self.data_paths["experiment-history"].exists():
                with open(self.data_paths["experiment-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.experiment_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Experiment history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing experiment history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in experiment history: {e}")
        except OSError as e:
            logger.error(f"OS error loading experiment history: {e}")
        except Exception as e:
            logger.warning(f"Could not load experiment history: {e}")

    def _save_experiment_history(self):
        """Save experiment history to data file"""
        try:
            self.data_paths["experiment-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["experiment-history"], "w") as f:
                f.write("# Experiment History\n\n")
                for experiment in self.experiment_history[-50:]:  # Keep last 50 experiments
                    f.write(f"- {experiment}\n")
        except PermissionError as e:
            logger.error(f"Permission denied saving experiment history: {e}")
        except OSError as e:
            logger.error(f"OS error saving experiment history: {e}")
        except Exception as e:
            logger.error(f"Could not save experiment history: {e}")

    def _load_research_history(self):
        """Load research history from data file"""
        try:
            if self.data_paths["research-history"].exists():
                with open(self.data_paths["research-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.research_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Research history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing research history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in research history: {e}")
        except OSError as e:
            logger.error(f"OS error loading research history: {e}")
        except Exception as e:
            logger.warning(f"Could not load research history: {e}")

    def _save_research_history(self):
        """Save research history to data file"""
        try:
            self.data_paths["research-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["research-history"], "w") as f:
                f.write("# Research History\n\n")
                for research in self.research_history[-50:]:  # Keep last 50 research items
                    f.write(f"- {research}\n")
        except PermissionError as e:
            logger.error(f"Permission denied saving research history: {e}")
        except OSError as e:
            logger.error(f"OS error saving research history: {e}")
        except Exception as e:
            logger.error(f"Could not save research history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
RnD Agent Commands:
  help                    - Show this help message
  conduct-research        - Conduct new research
  design-experiment       - Design new experiment
  run-experiment          - Run experiment
  evaluate-results        - Evaluate experiment results
  generate-innovation     - Generate innovation ideas
  prototype-solution      - Create prototype solution
  show-experiment-history - Show experiment history
  show-research-history   - Show research history
  show-best-practices     - Show RnD best practices
  show-changelog          - Show RnD changelog
  export-report [format]  - Export RnD report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
  run                     - Run the agent and listen for events
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        # Input validation
        if not isinstance(resource_type, str):
            print("Error: resource_type must be a string")
            return
        
        if not resource_type.strip():
            print("Error: resource_type cannot be empty")
            return
        
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "experiment-template":
                path = self.template_paths["experiment-template"]
            elif resource_type == "research-template":
                path = self.template_paths["research-template"]
            else:
                print(f"Unknown resource type: {resource_type}")
                return
            if path.exists():
                with open(path) as f:
                    print(f.read())
            else:
                print(f"Resource file not found: {path}")
        except FileNotFoundError:
            print(f"Resource file not found: {resource_type}")
        except PermissionError as e:
            print(f"Permission denied accessing resource {resource_type}: {e}")
        except UnicodeDecodeError as e:
            print(f"Unicode decode error in resource {resource_type}: {e}")
        except Exception as e:
            logger.error(f"Error reading resource {resource_type}: {e}")

    def show_experiment_history(self):
        """Show experiment history"""
        if not self.experiment_history:
            print("No experiment history available.")
            return
        print("Experiment History:")
        print("=" * 50)
        for i, experiment in enumerate(self.experiment_history[-10:], 1):
            print(f"{i}. {experiment}")

    def show_research_history(self):
        """Show research history"""
        if not self.research_history:
            print("No research history available.")
            return
        print("Research History:")
        print("=" * 50)
        for i, research in enumerate(self.research_history[-10:], 1):
            print(f"{i}. {research}")

    async def conduct_research(self, research_topic: str = "AI-powered automation", research_type: str = "Technology Research") -> Dict[str, Any]:
        """Conduct new research with enhanced functionality."""
        # Input validation
        if not isinstance(research_topic, str):
            raise TypeError("research_topic must be a string")
        if not isinstance(research_type, str):
            raise TypeError("research_type must be a string")
        
        if not research_topic.strip():
            raise ValueError("research_topic cannot be empty")
        if not research_type.strip():
            raise ValueError("research_type cannot be empty")
            
        logger.info(f"Conducting research on {research_topic}")

        # Simulate research process
        time.sleep(1)

        research_result = {
            "research_id": hashlib.sha256(research_topic.encode()).hexdigest()[:8],
            "research_type": research_type,
            "topic": research_topic,
            "status": "completed",
            "research_details": {
                "objective": f"Investigate {research_topic} for potential implementation",
                "methodology": "Literature review, market analysis, expert interviews",
                "findings": [
                    "Technology shows promising results in similar applications",
                    "Market adoption is growing at 25% annually",
                    "Implementation complexity is moderate",
                    "ROI potential is high"
                ],
                "recommendations": [
                    "Proceed with pilot implementation",
                    "Conduct feasibility study",
                    "Evaluate vendor options",
                    "Plan integration strategy"
                ]
            },
            "metadata": {
                "researcher": "RnDAgent",
                "duration": "2 weeks",
                "sources": 15,
                "confidence_level": "high"
            },
            "impact_assessment": {
                "business_impact": "high",
                "technical_impact": "medium",
                "resource_requirements": "moderate",
                "timeline": "6-12 months"
            },
            "next_steps": [
                "Design pilot experiment",
                "Identify key stakeholders",
                "Develop implementation plan",
                "Set up monitoring framework"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Use MCP tools for enhanced research analysis
        rnd_data = {
            "research_topic": research_topic,
            "research_type": research_type,
            "research_data": research_result,
            "analysis_type": "rnd"
        }
        
        mcp_enhanced_data = await self.use_rnd_specific_mcp_tools(rnd_data)
        
        # Integrate MCP enhanced data
        if mcp_enhanced_data:
            research_result["mcp_enhanced_data"] = mcp_enhanced_data
            logger.info("MCP enhanced data integrated into research")

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 95, "%")

        # Add to research history
        research_entry = f"{datetime.now().isoformat()}: Research completed on {research_topic} - {research_type}"
        self.research_history.append(research_entry)
        self._save_research_history()

        logger.info(f"Research completed: {research_result}")
        return research_result

    def design_experiment(self, experiment_name: str = "AI Automation Pilot", hypothesis: str = "AI automation will improve efficiency by 30%") -> Dict[str, Any]:
        """Design new experiment with enhanced functionality."""
        # Input validation
        if not isinstance(experiment_name, str):
            raise TypeError("experiment_name must be a string")
        if not isinstance(hypothesis, str):
            raise TypeError("hypothesis must be a string")
        
        if not experiment_name.strip():
            raise ValueError("experiment_name cannot be empty")
        if not hypothesis.strip():
            raise ValueError("hypothesis cannot be empty")
            
        logger.info(f"Designing experiment: {experiment_name}")

        # Simulate experiment design
        time.sleep(1)

        experiment_design = {
            "experiment_id": hashlib.sha256(experiment_name.encode()).hexdigest()[:8],
            "experiment_name": experiment_name,
            "hypothesis": hypothesis,
            "status": "designed",
            "experiment_design": {
                "objective": "Test the effectiveness of AI automation in improving operational efficiency",
                "hypothesis": hypothesis,
                "variables": {
                    "independent": "AI automation implementation",
                    "dependent": "Operational efficiency metrics",
                    "control": "Traditional manual processes"
                },
                "methodology": "A/B testing with control group",
                "sample_size": "100 processes",
                "duration": "4 weeks",
                "success_criteria": [
                    "30% improvement in efficiency",
                    "Reduced error rate by 50%",
                    "Cost savings of 25%",
                    "User satisfaction > 80%"
                ]
            },
            "implementation_plan": {
                "phase_1": "Setup and configuration (1 week)",
                "phase_2": "Pilot testing (2 weeks)",
                "phase_3": "Full implementation (1 week)",
                "phase_4": "Evaluation and analysis (1 week)"
            },
            "risk_assessment": {
                "technical_risks": ["System integration issues", "Performance bottlenecks"],
                "business_risks": ["User resistance", "Training requirements"],
                "mitigation_strategies": [
                    "Thorough testing and validation",
                    "Comprehensive user training",
                    "Gradual rollout approach"
                ]
            },
            "resource_requirements": {
                "team_size": "5 members",
                "budget": "$50,000",
                "tools": ["AI platform", "Analytics tools", "Testing framework"],
                "timeline": "5 weeks"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 92, "%")

        logger.info(f"Experiment designed: {experiment_design}")
        return experiment_design

    def run_experiment(self, experiment_id: str = "exp_12345", experiment_name: str = "AI Automation Pilot") -> Dict[str, Any]:
        """Run experiment with enhanced functionality."""
        # Input validation
        if not isinstance(experiment_id, str):
            raise TypeError("experiment_id must be a string")
        if not isinstance(experiment_name, str):
            raise TypeError("experiment_name must be a string")
        
        if not experiment_id.strip():
            raise ValueError("experiment_id cannot be empty")
        if not experiment_name.strip():
            raise ValueError("experiment_name cannot be empty")
            
        logger.info(f"Running experiment: {experiment_name}")

        # Simulate experiment execution
        time.sleep(2)

        experiment_results = {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "status": "completed",
            "execution_details": {
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": "4 weeks",
                "participants": "100 processes",
                "completion_rate": "95%"
            },
            "results": {
                "efficiency_improvement": "35%",
                "error_rate_reduction": "55%",
                "cost_savings": "28%",
                "user_satisfaction": "85%",
                "processing_time_reduction": "40%",
                "accuracy_improvement": "45%"
            },
            "analysis": {
                "statistical_significance": "p < 0.01",
                "confidence_interval": "95%",
                "effect_size": "Large",
                "data_quality": "High",
                "outliers_detected": "None"
            },
            "conclusions": [
                "AI automation significantly improves operational efficiency",
                "Error rates are substantially reduced",
                "Cost savings exceed initial projections",
                "User satisfaction is high",
                "Implementation is feasible and scalable"
            ],
            "recommendations": [
                "Proceed with full implementation",
                "Expand to additional processes",
                "Develop comprehensive training program",
                "Establish monitoring and feedback systems",
                "Plan for continuous improvement"
            ],
            "challenges_encountered": [
                "Initial setup complexity",
                "User training requirements",
                "System integration issues"
            ],
            "lessons_learned": [
                "Early stakeholder engagement is crucial",
                "Gradual rollout reduces resistance",
                "Continuous monitoring is essential",
                "User feedback drives improvements"
            ],
            "next_steps": [
                "Scale implementation across organization",
                "Develop advanced analytics dashboard",
                "Create knowledge sharing platform",
                "Establish best practices documentation"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 90, "%")

        # Add to experiment history
        experiment_entry = f"{datetime.now().isoformat()}: Experiment completed - {experiment_name} ({experiment_id})"
        self.experiment_history.append(experiment_entry)
        self._save_experiment_history()

        logger.info(f"Experiment completed: {experiment_results}")
        return experiment_results

    def evaluate_results(self, experiment_results: Dict = None) -> Dict[str, Any]:
        """Evaluate experiment results with enhanced functionality."""
        # Input validation
        if experiment_results is not None and not isinstance(experiment_results, dict):
            raise TypeError("experiment_results must be a dictionary")
            
        logger.info("Evaluating experiment results")

        # Simulate evaluation process
        time.sleep(1)

        if experiment_results is None:
            experiment_results = {
                "status": "completed",
                "results": {"efficiency_improvement": "30%"}
            }

        evaluation_result = {
            "evaluation_id": hashlib.sha256(str(experiment_results).encode()).hexdigest()[:8],
            "status": "evaluated",
            "evaluation_summary": "Comprehensive analysis of experiment outcomes and impact assessment",
            "key_findings": [
                "Significant improvement in operational efficiency",
                "Reduced error rates across all processes",
                "Positive user feedback and adoption",
                "Cost savings exceed initial projections",
                "Scalability potential confirmed"
            ],
            "statistical_analysis": {
                "sample_size": "100 processes",
                "confidence_level": "95%",
                "p_value": "< 0.001",
                "effect_size": "Large (Cohen's d = 0.8)",
                "power_analysis": "Sufficient power (0.95)"
            },
            "impact_assessment": {
                "business_impact": "High - 35% efficiency improvement",
                "operational_impact": "Significant process optimization",
                "financial_impact": "28% cost reduction",
                "user_impact": "85% satisfaction rate",
                "strategic_impact": "Competitive advantage achieved"
            },
            "quality_assessment": {
                "data_quality": "Excellent - No missing data",
                "methodology_quality": "Robust - A/B testing design",
                "analysis_quality": "Comprehensive - Multiple metrics",
                "reporting_quality": "Clear - Well-documented results"
            },
            "recommendations": [
                "Proceed with full-scale implementation",
                "Expand to additional business units",
                "Develop comprehensive training program",
                "Establish continuous monitoring system",
                "Create knowledge sharing platform"
            ],
            "risk_assessment": {
                "implementation_risks": "Low - Proven technology",
                "adoption_risks": "Medium - Training required",
                "scaling_risks": "Low - Architecture supports growth",
                "maintenance_risks": "Low - Automated systems"
            },
            "next_steps": [
                "Develop implementation roadmap",
                "Secure stakeholder approval",
                "Allocate resources and budget",
                "Establish project timeline",
                "Create success metrics dashboard"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 94, "%")

        logger.info(f"Results evaluation completed: {evaluation_result}")
        return evaluation_result

    def generate_innovation(self, innovation_area: str = "AI and Automation", focus_area: str = "Process Optimization") -> Dict[str, Any]:
        """Generate innovation ideas with enhanced functionality."""
        # Input validation
        if not isinstance(innovation_area, str):
            raise TypeError("innovation_area must be a string")
        if not isinstance(focus_area, str):
            raise TypeError("focus_area must be a string")
        
        if not innovation_area.strip():
            raise ValueError("innovation_area cannot be empty")
        if not focus_area.strip():
            raise ValueError("focus_area cannot be empty")
            
        logger.info(f"Generating innovation ideas for {innovation_area}")

        # Simulate innovation generation
        time.sleep(1)

        innovation_result = {
            "innovation_id": hashlib.sha256(f"{innovation_area}_{focus_area}".encode()).hexdigest()[:8],
            "innovation_area": innovation_area,
            "focus_area": focus_area,
            "status": "generated",
            "innovation_concept": {
                "title": f"Advanced {innovation_area} for {focus_area}",
                "description": f"Revolutionary approach to {focus_area} using cutting-edge {innovation_area} technologies",
                "value_proposition": f"Transform {focus_area} through intelligent automation and data-driven insights",
                "unique_features": [
                    "AI-powered decision making",
                    "Real-time optimization",
                    "Predictive analytics",
                    "Adaptive learning systems",
                    "Seamless integration"
                ]
            },
            "potential_impact": {
                "efficiency_gains": "40-60% improvement",
                "cost_reduction": "30-50% savings",
                "quality_improvement": "25-35% enhancement",
                "speed_increase": "3-5x faster processing",
                "scalability": "Unlimited growth potential"
            },
            "implementation_plan": {
                "phase_1": "Research and validation (3 months)",
                "phase_2": "Prototype development (6 months)",
                "phase_3": "Pilot testing (3 months)",
                "phase_4": "Full implementation (6 months)"
            },
            "risk_assessment": {
                "technical_risks": ["Emerging technology uncertainty", "Integration complexity"],
                "business_risks": ["Market adoption", "Competitive response"],
                "operational_risks": ["Change management", "Resource allocation"],
                "mitigation_strategies": [
                    "Phased implementation approach",
                    "Comprehensive stakeholder engagement",
                    "Robust testing and validation",
                    "Continuous monitoring and adaptation"
                ]
            },
            "success_metrics": {
                "efficiency_improvement": "Target: 50%",
                "cost_reduction": "Target: 40%",
                "user_adoption": "Target: 90%",
                "time_to_value": "Target: 6 months",
                "roi_achievement": "Target: 300%"
            },
            "business_case": {
                "total_investment": "$1.4 million",
                "annual_revenue_potential": "$2 million",
                "expected_roi": "300%",
                "payback_period": "18 months",
                "risk_adjusted_return": "250%"
            },
            "next_steps": [
                "Conduct feasibility study",
                "Develop detailed business case",
                "Secure stakeholder approval",
                "Assemble implementation team",
                "Create project timeline"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 88, "%")

        logger.info(f"Innovation generated: {innovation_result}")
        return innovation_result

    def prototype_solution(self, prototype_name: str = "AI Automation Prototype", solution_type: str = "Process Automation") -> Dict[str, Any]:
        """Create prototype solution with enhanced functionality."""
        # Input validation
        if not isinstance(prototype_name, str):
            raise TypeError("prototype_name must be a string")
        if not isinstance(solution_type, str):
            raise TypeError("solution_type must be a string")
        
        if not prototype_name.strip():
            raise ValueError("prototype_name cannot be empty")
        if not solution_type.strip():
            raise ValueError("solution_type cannot be empty")
            
        logger.info(f"Creating prototype: {prototype_name}")

        # Simulate prototype creation
        time.sleep(2)

        prototype_result = {
            "prototype_id": hashlib.sha256(prototype_name.encode()).hexdigest()[:8],
            "prototype_name": prototype_name,
            "solution_type": solution_type,
            "status": "prototyped",
            "prototype_specifications": {
                "objective": "Demonstrate AI automation capabilities for process optimization",
                "scope": "Document processing and workflow automation",
                "features": [
                    "Intelligent document classification",
                    "Automated data extraction",
                    "Workflow orchestration",
                    "Real-time monitoring",
                    "Performance analytics"
                ],
                "technology_stack": [
                    "Python 3.9+",
                    "TensorFlow 2.x",
                    "FastAPI",
                    "PostgreSQL",
                    "Redis",
                    "Docker"
                ],
                "architecture": "Microservices-based architecture with API-first design"
            },
            "implementation_details": {
                "development_approach": "Agile methodology with rapid prototyping",
                "code_quality": "High - 90% test coverage",
                "documentation": "Comprehensive - API docs, user guides",
                "security": "Enterprise-grade - OAuth2, encryption",
                "performance": "Optimized - < 2s response time"
            },
            "testing_plan": {
                "unit_tests": "150 tests covering all components",
                "integration_tests": "25 tests for system interactions",
                "performance_tests": "Load testing with 1000 concurrent users",
                "security_tests": "Penetration testing and vulnerability assessment",
                "user_acceptance_tests": "End-to-end workflow validation"
            },
            "deployment_strategy": {
                "environment": "Cloud-native deployment on AWS/GCP",
                "containerization": "Docker containers with Kubernetes orchestration",
                "monitoring": "Prometheus/Grafana for metrics and alerting",
                "logging": "Centralized logging with ELK stack",
                "backup": "Automated backup and disaster recovery"
            },
            "success_criteria": {
                "functional_requirements": "All core features working",
                "performance_requirements": "Sub-2 second response time",
                "scalability_requirements": "Support 1000+ concurrent users",
                "security_requirements": "Zero critical vulnerabilities",
                "usability_requirements": "90% user satisfaction"
            },
            "development_metrics": {
                "development_time": "6 weeks",
                "team_size": "4 developers",
                "code_lines": "15,000",
                "test_coverage": "85%",
                "documentation_completeness": "90%"
            },
            "performance_metrics": {
                "processing_speed": "100 documents/minute",
                "accuracy_rate": "95%",
                "response_time": "< 2 seconds",
                "uptime": "99.9%",
                "scalability": "Horizontal scaling supported"
            },
            "user_experience": {
                "interface_type": "Web-based dashboard",
                "ease_of_use": "Intuitive and user-friendly",
                "learning_curve": "Minimal training required",
                "accessibility": "WCAG 2.1 compliant",
                "mobile_support": "Responsive design"
            },
            "testing_results": {
                "unit_tests": "150 tests passed",
                "integration_tests": "25 tests passed",
                "performance_tests": "All benchmarks met",
                "security_tests": "No vulnerabilities found",
                "user_acceptance_tests": "90% satisfaction rate"
            },
            "deployment_ready": {
                "containerization": "Docker containers ready",
                "orchestration": "Kubernetes manifests provided",
                "monitoring": "Prometheus/Grafana setup",
                "logging": "Centralized logging configured",
                "backup": "Automated backup procedures"
            },
            "next_steps": [
                "Deploy to staging environment",
                "Conduct user acceptance testing",
                "Gather feedback and iterate",
                "Plan production deployment",
                "Develop training materials"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 92, "%")

        logger.info(f"Prototype created: {prototype_result}")
        return prototype_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export RnD report in specified format."""
        # Input validation
        if not isinstance(format_type, str):
            raise TypeError("format_type must be a string")
        
        if format_type not in ["md", "csv", "json"]:
            raise ValueError("format_type must be one of: md, csv, json")
        
        if report_data is not None and not isinstance(report_data, dict):
            raise TypeError("report_data must be a dictionary")
        
        if not report_data:
            report_data = {
                "report_type": "RnD Report",
                "version": "1.2.0",
                "status": "success",
                "total_experiments": 15,
                "successful_experiments": 14,
                "failed_experiments": 1,
                "timestamp": datetime.now().isoformat(),
                "agent": "RnDAgent"
            }

        try:
            if format_type == "md":
                self._export_markdown(report_data)
            elif format_type == "csv":
                self._export_csv(report_data)
            elif format_type == "json":
                self._export_json(report_data)
            else:
                print(f"Unsupported format: {format_type}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")

    def _export_markdown(self, report_data: Dict):
        """Export report data as markdown."""
        try:
            output_file = f"rnd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            content = f"""# RnD Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Version**: {report_data.get('version', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Total Experiments**: {report_data.get('total_experiments', 0)}
- **Successful Experiments**: {report_data.get('successful_experiments', 0)}
- **Failed Experiments**: {report_data.get('failed_experiments', 0)}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Experiment Metrics
- **Success Rate**: {(report_data.get('successful_experiments', 0) / max(report_data.get('total_experiments', 1), 1)) * 100:.1f}%
- **Average Experiment Duration**: {report_data.get('experiment_metrics', {}).get('duration', 'N/A')}
- **Innovation Rate**: {report_data.get('experiment_metrics', {}).get('innovation_rate', 'N/A')}
- **Failure Rate**: {(report_data.get('failed_experiments', 0) / max(report_data.get('total_experiments', 1), 1)) * 100:.1f}%

## Recent Experiments
{chr(10).join([f"- {experiment}" for experiment in self.experiment_history[-5:]])}

## Recent Research
{chr(10).join([f"- {research}" for research in self.research_history[-5:]])}
"""

            with open(output_file, "w") as f:
                f.write(content)
            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving markdown report: {e}")
        except OSError as e:
            logger.error(f"OS error saving markdown report: {e}")
        except Exception as e:
            logger.error(f"Error saving markdown report: {e}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        try:
            output_file = f"rnd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Version", report_data.get("version", "N/A")])
                writer.writerow(["Status", report_data.get("status", "N/A")])
                writer.writerow(["Total Experiments", report_data.get("total_experiments", 0)])
                writer.writerow(["Successful Experiments", report_data.get("successful_experiments", 0)])
                writer.writerow(["Failed Experiments", report_data.get("failed_experiments", 0)])

            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving CSV report: {e}")
        except OSError as e:
            logger.error(f"OS error saving CSV report: {e}")
        except Exception as e:
            logger.error(f"Error saving CSV report: {e}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        try:
            output_file = f"rnd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving JSON report: {e}")
        except OSError as e:
            logger.error(f"OS error saving JSON report: {e}")
        except Exception as e:
            logger.error(f"Error saving JSON report: {e}")

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
        logger.info("Starting RnD collaboration example...")

        # Publish experiment request
        publish("experiment_requested", {
            "agent": "RnDAgent",
            "experiment_type": "AI Automation",
            "timestamp": datetime.now().isoformat()
        })

        # Conduct research
        await self.conduct_research("AI-powered automation", "Technology Research")

        # Design experiment
        self.design_experiment("AI Automation Pilot", "AI automation will improve efficiency by 30%")

        # Run experiment
        experiment_results = self.run_experiment("exp_12345", "AI Automation Pilot")

        # Publish completion
        publish("experiment_completed", {
            "status": "success",
            "agent": "RnDAgent",
            "experiment_id": "exp_12345",
            "results": experiment_results["results"]
        })

        # Save context
        save_context("RnDAgent", "status", {"experiment_status": "completed"})

        # Notify via Slack
        try:
            send_slack_message(f"RnD experiment completed with {experiment_results['results']['efficiency_improvement']} efficiency improvement")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("RnDAgent")
        print(f"Opgehaalde context: {context}")

    # Original functionality preserved
    def handle_experiment_completed(self, event):
        """Handle experiment completed event from other agents."""
        # Input validation
        if not isinstance(event, dict):
            logger.warning("Invalid event type for experiment completed event")
            return
        
        logger.info(f"Experiment completed event received: {event}")
        logger.info("[RnD] Experiment voltooid, resultaten worden geëvalueerd.")
        try:
            send_slack_message("[RnD] Experiment voltooid, resultaten worden geëvalueerd.")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        # Evaluate results (stub)

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        subscribe("experiment_completed", self.handle_experiment_completed)
        logger.info("RnDAgent ready and listening for events...")
        print("[RnDAgent] Ready and listening for events...")
        await self.collaborate_example()

def main():
    import asyncio
    
    parser = argparse.ArgumentParser(description="RnD Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "conduct-research", "design-experiment", "run-experiment",
                               "evaluate-results", "generate-innovation", "prototype-solution",
                               "show-experiment-history", "show-research-history", "show-best-practices",
                               "show-changelog", "export-report", "test", "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--research-topic", default="AI-powered automation", help="Research topic")
    parser.add_argument("--research-type", default="Technology Research", help="Research type")
    parser.add_argument("--experiment-name", default="AI Automation Pilot", help="Experiment name")
    parser.add_argument("--hypothesis", default="AI automation will improve efficiency by 30%", help="Experiment hypothesis")
    parser.add_argument("--experiment-id", default="exp_12345", help="Experiment ID")
    parser.add_argument("--innovation-area", default="AI and Automation", help="Innovation area")
    parser.add_argument("--focus-area", default="Process Optimization", help="Focus area")
    parser.add_argument("--prototype-name", default="AI Automation Prototype", help="Prototype name")
    parser.add_argument("--solution-type", default="Process Automation", help="Solution type")

    args = parser.parse_args()

    agent = RnDAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "conduct-research":
        result = asyncio.run(agent.conduct_research(args.research_topic, args.research_type))
        print(json.dumps(result, indent=2))
    elif args.command == "design-experiment":
        result = agent.design_experiment(args.experiment_name, args.hypothesis)
        print(json.dumps(result, indent=2))
    elif args.command == "run-experiment":
        result = agent.run_experiment(args.experiment_id, args.experiment_name)
        print(json.dumps(result, indent=2))
    elif args.command == "evaluate-results":
        result = agent.evaluate_results()
        print(json.dumps(result, indent=2))
    elif args.command == "generate-innovation":
        result = agent.generate_innovation(args.innovation_area, args.focus_area)
        print(json.dumps(result, indent=2))
    elif args.command == "prototype-solution":
        result = agent.prototype_solution(args.prototype_name, args.solution_type)
        print(json.dumps(result, indent=2))
    elif args.command == "show-experiment-history":
        agent.show_experiment_history()
    elif args.command == "show-research-history":
        agent.show_research_history()
    elif args.command == "show-best-practices":
        agent.show_resource("best-practices")
    elif args.command == "show-changelog":
        agent.show_resource("changelog")
    elif args.command == "export-report":
        agent.export_report(args.format)
    elif args.command == "test":
        agent.test_resource_completeness()
    elif args.command == "collaborate":
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        asyncio.run(agent.run())
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)
        return

if __name__ == "__main__":
    main()
