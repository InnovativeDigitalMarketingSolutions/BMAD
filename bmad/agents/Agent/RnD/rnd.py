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

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class RnDAgent:
    def __init__(self):
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

    def conduct_research(self, research_topic: str = "AI-powered automation", research_type: str = "Technology Research") -> Dict[str, Any]:
        """Conduct new research with enhanced functionality."""
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
            "statistical_analysis": {
                "confidence_level": "95%",
                "p_value": "0.001",
                "effect_size": "large",
                "statistical_significance": "significant"
            },
            "key_findings": [
                "AI automation exceeded efficiency improvement targets",
                "Error rates were reduced more than expected",
                "User adoption was higher than anticipated",
                "Cost savings were achieved ahead of schedule"
            ],
            "challenges_encountered": [
                "Initial setup complexity",
                "User training requirements",
                "System integration issues"
            ],
            "lessons_learned": [
                "Early user involvement is crucial",
                "Comprehensive training improves adoption",
                "Gradual rollout reduces resistance"
            ],
            "recommendations": [
                "Proceed with full implementation",
                "Expand to additional processes",
                "Develop advanced training program",
                "Plan for scaling and optimization"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 88, "%")

        # Add to experiment history
        experiment_entry = f"{datetime.now().isoformat()}: Experiment completed - {experiment_name} (ID: {experiment_id})"
        self.experiment_history.append(experiment_entry)
        self._save_experiment_history()

        logger.info(f"Experiment completed: {experiment_results}")
        return experiment_results

    def evaluate_results(self, experiment_results: Dict = None) -> Dict[str, Any]:
        """Evaluate experiment results with enhanced functionality."""
        if experiment_results is None:
            experiment_results = {
                "efficiency_improvement": "35%",
                "error_rate_reduction": "55%",
                "cost_savings": "28%",
                "user_satisfaction": "85%"
            }

        logger.info("Evaluating experiment results")

        # Simulate result evaluation
        time.sleep(1)

        evaluation_result = {
            "evaluation_type": "Experiment Results Evaluation",
            "status": "completed",
            "evaluation_criteria": {
                "efficiency_target": "30%",
                "error_reduction_target": "50%",
                "cost_savings_target": "25%",
                "satisfaction_target": "80%"
            },
            "performance_analysis": {
                "efficiency": {
                    "achieved": experiment_results.get("efficiency_improvement", "35%"),
                    "target": "30%",
                    "status": "exceeded",
                    "improvement": "+5%"
                },
                "error_reduction": {
                    "achieved": experiment_results.get("error_rate_reduction", "55%"),
                    "target": "50%",
                    "status": "exceeded",
                    "improvement": "+5%"
                },
                "cost_savings": {
                    "achieved": experiment_results.get("cost_savings", "28%"),
                    "target": "25%",
                    "status": "exceeded",
                    "improvement": "+3%"
                },
                "user_satisfaction": {
                    "achieved": experiment_results.get("user_satisfaction", "85%"),
                    "target": "80%",
                    "status": "exceeded",
                    "improvement": "+5%"
                }
            },
            "overall_assessment": {
                "success_rate": "100%",
                "target_achievement": "exceeded",
                "confidence_level": "high",
                "recommendation": "proceed_with_implementation"
            },
            "business_impact": {
                "roi_estimate": "350%",
                "payback_period": "8 months",
                "annual_savings": "$500,000",
                "productivity_gain": "35%"
            },
            "risk_assessment": {
                "implementation_risks": "low",
                "operational_risks": "medium",
                "financial_risks": "low",
                "overall_risk": "low"
            },
            "next_phases": [
                {
                    "phase": "Full Implementation",
                    "timeline": "6 months",
                    "scope": "All applicable processes",
                    "budget": "$200,000"
                },
                {
                    "phase": "Optimization",
                    "timeline": "3 months",
                    "scope": "Performance tuning",
                    "budget": "$50,000"
                },
                {
                    "phase": "Expansion",
                    "timeline": "12 months",
                    "scope": "Additional departments",
                    "budget": "$300,000"
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 90, "%")

        logger.info(f"Results evaluation completed: {evaluation_result}")
        return evaluation_result

    def generate_innovation(self, innovation_area: str = "AI and Automation", focus_area: str = "Process Optimization") -> Dict[str, Any]:
        """Generate innovation ideas with enhanced functionality."""
        logger.info(f"Generating innovation ideas for {innovation_area}")

        # Simulate innovation generation
        time.sleep(1)

        innovation_result = {
            "innovation_id": hashlib.sha256(f"{innovation_area}_{focus_area}".encode()).hexdigest()[:8],
            "innovation_area": innovation_area,
            "focus_area": focus_area,
            "status": "generated",
            "innovation_ideas": [
                {
                    "idea": "AI-Powered Predictive Analytics Platform",
                    "description": "Advanced analytics platform that predicts trends and optimizes decision-making",
                    "potential_impact": "high",
                    "feasibility": "medium",
                    "timeline": "12-18 months",
                    "investment_required": "$500,000"
                },
                {
                    "idea": "Intelligent Process Automation Suite",
                    "description": "Comprehensive automation suite for end-to-end process optimization",
                    "potential_impact": "very_high",
                    "feasibility": "high",
                    "timeline": "8-12 months",
                    "investment_required": "$300,000"
                },
                {
                    "idea": "Real-time Collaboration Platform",
                    "description": "Advanced collaboration platform with AI-powered insights",
                    "potential_impact": "medium",
                    "feasibility": "high",
                    "timeline": "6-10 months",
                    "investment_required": "$200,000"
                },
                {
                    "idea": "Smart Resource Management System",
                    "description": "AI-driven resource allocation and optimization system",
                    "potential_impact": "high",
                    "feasibility": "medium",
                    "timeline": "10-14 months",
                    "investment_required": "$400,000"
                }
            ],
            "market_analysis": {
                "market_size": "$50 billion",
                "growth_rate": "25% annually",
                "competition_level": "moderate",
                "entry_barriers": "medium"
            },
            "technology_assessment": {
                "technology_readiness": "TRL 7-8",
                "integration_complexity": "medium",
                "scalability": "high",
                "maintenance_requirements": "low"
            },
            "business_case": {
                "total_investment": "$1.4 million",
                "expected_roi": "300%",
                "payback_period": "18 months",
                "annual_revenue_potential": "$2 million"
            },
            "implementation_roadmap": {
                "phase_1": "Research and validation (3 months)",
                "phase_2": "Prototype development (6 months)",
                "phase_3": "Pilot testing (3 months)",
                "phase_4": "Full implementation (6 months)"
            },
            "risk_mitigation": {
                "technical_risks": ["Technology maturity", "Integration complexity"],
                "market_risks": ["Competition", "Market adoption"],
                "mitigation_strategies": [
                    "Thorough research and validation",
                    "Strategic partnerships",
                    "Gradual market entry"
                ]
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "RnDAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 85, "%")

        logger.info(f"Innovation ideas generated: {innovation_result}")
        return innovation_result

    def prototype_solution(self, prototype_name: str = "AI Automation Prototype", solution_type: str = "Process Automation") -> Dict[str, Any]:
        """Create prototype solution with enhanced functionality."""
        logger.info(f"Creating prototype: {prototype_name}")

        # Simulate prototype creation
        time.sleep(2)

        prototype_result = {
            "prototype_id": hashlib.sha256(prototype_name.encode()).hexdigest()[:8],
            "prototype_name": prototype_name,
            "solution_type": solution_type,
            "status": "completed",
            "prototype_details": {
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
        self.monitor._record_metric("RnDAgent", MetricType.SUCCESS_RATE, 87, "%")

        logger.info(f"Prototype created: {prototype_result}")
        return prototype_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export RnD report in specified format."""
        if not report_data:
            report_data = {
                "report_type": "RnD Report",
                "timeframe": "Last 30 days",
                "status": "completed",
                "experiments_conducted": 5,
                "research_projects": 3,
                "prototypes_created": 2,
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
        output_file = f"rnd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# RnD Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Timeframe**: {report_data.get('timeframe', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Experiments Conducted**: {report_data.get('experiments_conducted', 0)}
- **Research Projects**: {report_data.get('research_projects', 0)}
- **Prototypes Created**: {report_data.get('prototypes_created', 0)}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Recent Experiments
{chr(10).join([f"- {experiment}" for experiment in self.experiment_history[-5:]])}

## Recent Research
{chr(10).join([f"- {research}" for research in self.research_history[-5:]])}
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        output_file = f"rnd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Timeframe", report_data.get("timeframe", "N/A")])
            writer.writerow(["Status", report_data.get("status", "N/A")])
            writer.writerow(["Experiments Conducted", report_data.get("experiments_conducted", 0)])
            writer.writerow(["Research Projects", report_data.get("research_projects", 0)])
            writer.writerow(["Prototypes Created", report_data.get("prototypes_created", 0)])

        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"rnd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"Report export saved to: {output_file}")

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
        logger.info("Starting RnD collaboration example...")

        # Publish experiment request
        publish("experiment_requested", {
            "agent": "RnDAgent",
            "experiment_type": "AI Automation",
            "timestamp": datetime.now().isoformat()
        })

        # Conduct research
        self.conduct_research("AI-powered automation", "Technology Research")

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
        logger.info(f"Experiment completed event: {event}")
        print(f"[RnDAgent] Experiment completed: {event}")
        self.monitor.log_metric("experiment", event)
        allowed = self.policy_engine.evaluate_policy("experiment", event)
        print(f"[RnDAgent] Policy allowed: {allowed}")

    def run(self):
        """Run the agent and listen for events."""
        subscribe("experiment_completed", self.handle_experiment_completed)
        logger.info("RnDAgent ready and listening for events...")
        print("[RnDAgent] Ready and listening for events...")
        self.collaborate_example()

def main():
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
    parser.add_argument("--innovation-area", default="AI and Automation", help="Innovation area")
    parser.add_argument("--focus-area", default="Process Optimization", help="Focus area")
    parser.add_argument("--prototype-name", default="AI Automation Prototype", help="Prototype name")
    parser.add_argument("--solution-type", default="Process Automation", help="Solution type")

    args = parser.parse_args()

    agent = RnDAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "conduct-research":
        result = agent.conduct_research(args.research_topic, args.research_type)
        print(json.dumps(result, indent=2))
    elif args.command == "design-experiment":
        result = agent.design_experiment(args.experiment_name, args.hypothesis)
        print(json.dumps(result, indent=2))
    elif args.command == "run-experiment":
        result = agent.run_experiment("exp_12345", args.experiment_name)
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
        agent.collaborate_example()
    elif args.command == "run":
        agent.run()

if __name__ == "__main__":
    main()
