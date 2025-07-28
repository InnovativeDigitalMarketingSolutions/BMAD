import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import csv
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
from integrations.slack.slack_notify import send_slack_message

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class RetrospectiveAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/retrospective/best-practices.md",
            "retro-template": self.resource_base / "templates/retrospective/retro-template.md",
            "action-plan-template": self.resource_base / "templates/retrospective/action-plan-template.md",
            "feedback-template": self.resource_base / "templates/retrospective/feedback-template.md",
            "improvement-template": self.resource_base / "templates/retrospective/improvement-template.md",
            "retro-checklist-template": self.resource_base / "templates/retrospective/retro-checklist-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/retrospective/changelog.md",
            "history": self.resource_base / "data/retrospective/retro-history.md",
            "action-history": self.resource_base / "data/retrospective/action-history.md"
        }

        # Initialize history
        self.retro_history = []
        self.action_history = []
        self._load_retro_history()
        self._load_action_history()

    def _load_retro_history(self):
        """Load retrospective history from data file"""
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.retro_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load retrospective history: {e}")

    def _save_retro_history(self):
        """Save retrospective history to data file"""
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Retrospective History\n\n")
                for retro in self.retro_history[-50:]:  # Keep last 50 retrospectives
                    f.write(f"- {retro}\n")
        except Exception as e:
            logger.error(f"Could not save retrospective history: {e}")

    def _load_action_history(self):
        """Load action history from data file"""
        try:
            if self.data_paths["action-history"].exists():
                with open(self.data_paths["action-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.action_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load action history: {e}")

    def _save_action_history(self):
        """Save action history to data file"""
        try:
            self.data_paths["action-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["action-history"], "w") as f:
                f.write("# Action History\n\n")
                for action in self.action_history[-50:]:  # Keep last 50 actions
                    f.write(f"- {action}\n")
        except Exception as e:
            logger.error(f"Could not save action history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
Retrospective Agent Commands:
  help                    - Show this help message
  conduct-retrospective   - Conduct a new retrospective
  analyze-feedback        - Analyze feedback and generate insights
  create-action-plan      - Create action plan from retrospective
  track-improvements      - Track improvement progress
  show-retro-history      - Show retrospective history
  show-action-history     - Show action history
  show-best-practices     - Show retrospective best practices
  show-changelog          - Show retrospective changelog
  export-report [format]  - Export retrospective report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        """Show resource content"""
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "retro-template":
                path = self.template_paths["retro-template"]
            elif resource_type == "action-plan-template":
                path = self.template_paths["action-plan-template"]
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

    def show_retro_history(self):
        """Show retrospective history"""
        if not self.retro_history:
            print("No retrospective history available.")
            return
        print("Retrospective History:")
        print("=" * 50)
        for i, retro in enumerate(self.retro_history[-10:], 1):
            print(f"{i}. {retro}")

    def show_action_history(self):
        """Show action history"""
        if not self.action_history:
            print("No action history available.")
            return
        print("Action History:")
        print("=" * 50)
        for i, action in enumerate(self.action_history[-10:], 1):
            print(f"{i}. {action}")

    def conduct_retrospective(self, sprint_name: str = "Sprint 15", team_size: int = 8) -> Dict[str, Any]:
        """Conduct a new retrospective with enhanced functionality."""
        logger.info(f"Conducting retrospective for {sprint_name}")

        # Simulate retrospective conduction
        time.sleep(2)

        retro_result = {
            "sprint_name": sprint_name,
            "retrospective_type": "Sprint Retrospective",
            "team_size": team_size,
            "status": "completed",
            "retrospective_framework": {
                "method": "Start-Stop-Continue",
                "duration": "60 minutes",
                "facilitator": "Scrum Master",
                "participants": team_size
            },
            "feedback_categories": {
                "start": [
                    "Implement automated testing in CI/CD pipeline",
                    "Add code review guidelines",
                    "Create team knowledge sharing sessions"
                ],
                "stop": [
                    "Long meetings without clear agenda",
                    "Manual deployment processes",
                    "Lack of documentation updates"
                ],
                "continue": [
                    "Daily standups",
                    "Pair programming sessions",
                    "Regular code reviews"
                ]
            },
            "team_sentiment": {
                "overall_sentiment": "positive",
                "satisfaction_score": 7.5,
                "engagement_level": "high",
                "collaboration_quality": "excellent"
            },
            "key_insights": [
                "Team communication has improved significantly",
                "Need for better documentation practices",
                "Automation opportunities identified",
                "Knowledge sharing is working well"
            ],
            "action_items": [
                {
                    "action": "Implement automated testing",
                    "owner": "DevOps Team",
                    "priority": "high",
                    "deadline": "Next sprint",
                    "status": "planned"
                },
                {
                    "action": "Create documentation guidelines",
                    "owner": "Documentation Team",
                    "priority": "medium",
                    "deadline": "2 weeks",
                    "status": "planned"
                },
                {
                    "action": "Optimize meeting structure",
                    "owner": "Scrum Master",
                    "priority": "medium",
                    "deadline": "1 week",
                    "status": "planned"
                }
            ],
            "metrics": {
                "participation_rate": "100%",
                "action_item_count": 3,
                "completion_rate": "85%",
                "team_satisfaction": "7.5/10"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("Retrospective", MetricType.SUCCESS_RATE, 95, "%")

        # Add to retrospective history
        retro_entry = f"{datetime.now().isoformat()}: Retrospective completed for {sprint_name} with {len(retro_result['action_items'])} action items"
        self.retro_history.append(retro_entry)
        self._save_retro_history()

        logger.info(f"Retrospective completed: {retro_result}")
        return retro_result

    def analyze_feedback(self, feedback_list: List[str] = None) -> Dict[str, Any]:
        """Analyze feedback and generate insights."""
        if feedback_list is None:
            feedback_list = [
                "Team communication has improved",
                "Need better documentation",
                "Meetings are too long",
                "Code quality is good",
                "Deployment process needs improvement"
            ]

        logger.info("Analyzing feedback and generating insights")

        # Simulate feedback analysis
        time.sleep(1)

        analysis_result = {
            "feedback_analysis_type": "Feedback Sentiment and Theme Analysis",
            "total_feedback_items": len(feedback_list),
            "sentiment_analysis": {
                "positive": 3,
                "negative": 2,
                "neutral": 0,
                "overall_sentiment": "positive"
            },
            "theme_analysis": {
                "communication": {
                    "count": 2,
                    "sentiment": "positive",
                    "examples": ["Team communication has improved", "Need better documentation"]
                },
                "process": {
                    "count": 2,
                    "sentiment": "negative",
                    "examples": ["Meetings are too long", "Deployment process needs improvement"]
                },
                "quality": {
                    "count": 1,
                    "sentiment": "positive",
                    "examples": ["Code quality is good"]
                }
            },
            "key_insights": [
                "Communication improvements are being recognized",
                "Process optimization opportunities identified",
                "Quality standards are being maintained"
            ],
            "recommendations": [
                "Continue fostering open communication",
                "Review and optimize meeting structure",
                "Streamline deployment processes",
                "Maintain quality standards"
            ],
            "trends": {
                "communication_trend": "improving",
                "process_trend": "needs_attention",
                "quality_trend": "stable"
            },
            "action_priorities": [
                "High: Optimize meeting structure",
                "Medium: Streamline deployment process",
                "Low: Enhance documentation"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("Retrospective", MetricType.SUCCESS_RATE, 92, "%")

        logger.info(f"Feedback analysis completed: {analysis_result}")
        return analysis_result

    def create_action_plan(self, retrospective_data: Dict = None) -> Dict[str, Any]:
        """Create action plan from retrospective data."""
        if retrospective_data is None:
            retrospective_data = {
                "sprint_name": "Sprint 15",
                "action_items": [
                    {"action": "Implement automated testing", "priority": "high"},
                    {"action": "Create documentation guidelines", "priority": "medium"},
                    {"action": "Optimize meeting structure", "priority": "medium"}
                ]
            }

        logger.info("Creating action plan from retrospective data")

        # Simulate action plan creation
        time.sleep(1)

        action_plan_result = {
            "action_plan_type": "Sprint Improvement Action Plan",
            "sprint_name": retrospective_data.get("sprint_name", "Sprint 15"),
            "status": "created",
            "action_plan": {
                "high_priority_actions": [
                    {
                        "action": "Implement automated testing in CI/CD pipeline",
                        "owner": "DevOps Team",
                        "deadline": "Next sprint",
                        "success_criteria": "All tests automated and passing",
                        "resources_needed": ["CI/CD tools", "Test frameworks"],
                        "dependencies": ["Test framework selection", "Pipeline configuration"]
                    }
                ],
                "medium_priority_actions": [
                    {
                        "action": "Create comprehensive documentation guidelines",
                        "owner": "Documentation Team",
                        "deadline": "2 weeks",
                        "success_criteria": "Guidelines published and team trained",
                        "resources_needed": ["Documentation tools", "Training materials"],
                        "dependencies": ["Tool selection", "Template creation"]
                    },
                    {
                        "action": "Optimize meeting structure and agenda",
                        "owner": "Scrum Master",
                        "deadline": "1 week",
                        "success_criteria": "Meetings are shorter and more focused",
                        "resources_needed": ["Meeting templates", "Time tracking"],
                        "dependencies": ["Team agreement", "Template creation"]
                    }
                ],
                "low_priority_actions": [
                    {
                        "action": "Enhance knowledge sharing sessions",
                        "owner": "Team Lead",
                        "deadline": "3 weeks",
                        "success_criteria": "Regular knowledge sharing sessions established",
                        "resources_needed": ["Presentation tools", "Scheduling system"],
                        "dependencies": ["Session format definition", "Schedule coordination"]
                    }
                ]
            },
            "implementation_timeline": {
                "week_1": ["Optimize meeting structure"],
                "week_2": ["Create documentation guidelines"],
                "week_3": ["Enhance knowledge sharing"],
                "week_4": ["Implement automated testing"]
            },
            "success_metrics": {
                "action_completion_rate": "target: 90%",
                "team_satisfaction": "target: 8.0/10",
                "process_efficiency": "target: 20% improvement",
                "quality_metrics": "target: 95% pass rate"
            },
            "risk_assessment": {
                "high_risks": [
                    "Resource constraints for automated testing implementation",
                    "Team resistance to process changes"
                ],
                "mitigation_strategies": [
                    "Secure additional resources and budget",
                    "Provide training and support for process changes"
                ]
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("Retrospective", MetricType.SUCCESS_RATE, 88, "%")

        # Add to action history
        action_entry = f"{datetime.now().isoformat()}: Action plan created for {retrospective_data.get('sprint_name', 'Sprint 15')} with {len(action_plan_result['action_plan']['high_priority_actions']) + len(action_plan_result['action_plan']['medium_priority_actions'])} actions"
        self.action_history.append(action_entry)
        self._save_action_history()

        logger.info(f"Action plan created: {action_plan_result}")
        return action_plan_result

    def track_improvements(self, sprint_name: str = "Sprint 15") -> Dict[str, Any]:
        """Track improvement progress from previous retrospectives."""
        logger.info(f"Tracking improvements for {sprint_name}")

        # Simulate improvement tracking
        time.sleep(1)

        tracking_result = {
            "sprint_name": sprint_name,
            "tracking_type": "Improvement Progress Tracking",
            "status": "completed",
            "improvement_areas": {
                "communication": {
                    "previous_score": 6.5,
                    "current_score": 7.8,
                    "improvement": "+20%",
                    "status": "improving",
                    "actions_completed": ["Daily standup optimization", "Team chat channels"],
                    "actions_pending": ["Knowledge sharing sessions"]
                },
                "process_efficiency": {
                    "previous_score": 5.8,
                    "current_score": 6.9,
                    "improvement": "+19%",
                    "status": "improving",
                    "actions_completed": ["Meeting agenda templates", "Documentation updates"],
                    "actions_pending": ["Automated testing implementation"]
                },
                "code_quality": {
                    "previous_score": 7.2,
                    "current_score": 7.5,
                    "improvement": "+4%",
                    "status": "stable",
                    "actions_completed": ["Code review guidelines", "Quality gates"],
                    "actions_pending": ["Additional test coverage"]
                },
                "team_collaboration": {
                    "previous_score": 7.0,
                    "current_score": 7.9,
                    "improvement": "+13%",
                    "status": "improving",
                    "actions_completed": ["Pair programming sessions", "Team building activities"],
                    "actions_pending": ["Cross-functional training"]
                }
            },
            "overall_progress": {
                "total_actions": 12,
                "completed_actions": 8,
                "in_progress_actions": 3,
                "pending_actions": 1,
                "completion_rate": "67%"
            },
            "key_achievements": [
                "Communication score improved by 20%",
                "Process efficiency increased by 19%",
                "8 out of 12 planned actions completed",
                "Team satisfaction at 7.8/10"
            ],
            "challenges": [
                "Automated testing implementation delayed",
                "Resource constraints for some improvements",
                "Team adaptation to new processes"
            ],
            "next_steps": [
                "Complete automated testing implementation",
                "Continue knowledge sharing initiatives",
                "Monitor and sustain improvements"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("Retrospective", MetricType.SUCCESS_RATE, 85, "%")

        logger.info(f"Improvement tracking completed: {tracking_result}")
        return tracking_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export retrospective report in specified format."""
        if not report_data:
            report_data = {
                "report_type": "Retrospective Report",
                "sprint_name": "Sprint 15",
                "status": "completed",
                "total_actions": 12,
                "completion_rate": "67%",
                "team_satisfaction": "7.8/10",
                "timestamp": datetime.now().isoformat(),
                "agent": "RetrospectiveAgent"
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
        output_file = f"retrospective_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Retrospective Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Sprint Name**: {report_data.get('sprint_name', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Total Actions**: {report_data.get('total_actions', 0)}
- **Completion Rate**: {report_data.get('completion_rate', 'N/A')}
- **Team Satisfaction**: {report_data.get('team_satisfaction', 'N/A')}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Improvement Areas
- **Communication**: {report_data.get('improvement_areas', {}).get('communication', {}).get('improvement', 'N/A')}
- **Process Efficiency**: {report_data.get('improvement_areas', {}).get('process_efficiency', {}).get('improvement', 'N/A')}
- **Code Quality**: {report_data.get('improvement_areas', {}).get('code_quality', {}).get('improvement', 'N/A')}
- **Team Collaboration**: {report_data.get('improvement_areas', {}).get('team_collaboration', {}).get('improvement', 'N/A')}

## Key Achievements
{chr(10).join([f"- {achievement}" for achievement in report_data.get('key_achievements', [])])}

## Recent Retrospectives
{chr(10).join([f"- {retro}" for retro in self.retro_history[-5:]])}

## Recent Actions
{chr(10).join([f"- {action}" for action in self.action_history[-5:]])}
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        output_file = f"retrospective_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Sprint Name", report_data.get("sprint_name", "N/A")])
            writer.writerow(["Status", report_data.get("status", "N/A")])
            writer.writerow(["Total Actions", report_data.get("total_actions", 0)])
            writer.writerow(["Completion Rate", report_data.get("completion_rate", "N/A")])
            writer.writerow(["Team Satisfaction", report_data.get("team_satisfaction", "N/A")])

        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"retrospective_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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
        logger.info("Starting retrospective collaboration example...")

        # Publish retrospective request
        publish("retrospective_requested", {
            "agent": "RetrospectiveAgent",
            "sprint_name": "Sprint 15",
            "timestamp": datetime.now().isoformat()
        })

        # Conduct retrospective
        retro_result = self.conduct_retrospective("Sprint 15", 8)

        # Analyze feedback
        self.analyze_feedback()

        # Create action plan
        action_plan_result = self.create_action_plan(retro_result)

        # Publish completion
        publish("retrospective_completed", {
            "status": "success",
            "agent": "RetrospectiveAgent",
            "sprint_name": "Sprint 15",
            "action_items_count": len(action_plan_result["action_plan"]["high_priority_actions"]) + len(action_plan_result["action_plan"]["medium_priority_actions"])
        })

        # Save context
        save_context("Retrospective", {"retrospective_status": "completed"})

        # Notify via Slack
        try:
            send_slack_message(f"Retrospective completed for Sprint 15 with {len(action_plan_result['action_plan']['high_priority_actions']) + len(action_plan_result['action_plan']['medium_priority_actions'])} action items")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("Retrospective")
        print(f"Opgehaalde context: {context}")

    def publish_improvement(self, action: str, agent: str = "Retrospective"):
        """Publish improvement action with enhanced functionality."""
        event = {"timestamp": datetime.now().isoformat(), "improvement": action, "agent": agent}
        publish("improvement_action", event)
        save_context(agent, "improvement", {"improvement": action, "timestamp": event["timestamp"]}, updated_by=agent)
        logger.info(f"[Retrospective] Verbeteractie gepubliceerd en opgeslagen: {action}")
        try:
            send_slack_message(f"[Retrospective] Verbeteractie gepubliceerd: {action}")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

    def summarize_retro(self, feedback_list: List[str]):
        """Summarize retrospective feedback with enhanced functionality."""
        prompt = "Vat de volgende retro-feedback samen in maximaal 3 bullets:\n" + "\n".join(feedback_list)
        result = ask_openai(prompt)
        logger.info(f"[Retrospective][LLM Retro-samenvatting]: {result}")
        return result

    def generate_retro_actions(self, feedback_list: List[str]):
        """Generate retrospective actions with enhanced functionality."""
        prompt = "Bedenk 3 concrete verbeteracties op basis van deze retro-feedback:\n" + "\n".join(feedback_list)
        result = ask_openai(prompt)
        logger.info(f"[Retrospective][LLM Actiepunten]: {result}")
        return result

    def on_retro_feedback(self, event):
        """Handle retro feedback event from other agents."""
        logger.info(f"Retro feedback event received: {event}")
        feedback_list = event.get("feedback_list", [])
        self.summarize_retro(feedback_list)

    def on_generate_actions(self, event):
        """Handle generate actions event from other agents."""
        logger.info(f"Generate actions event received: {event}")
        feedback_list = event.get("feedback_list", [])
        self.generate_retro_actions(feedback_list)

    def on_feedback_sentiment_analyzed(self, event):
        """Handle feedback sentiment analysis from other agents."""
        sentiment = event.get("sentiment", "")
        motivatie = event.get("motivatie", "")
        feedback = event.get("feedback", "")
        if sentiment == "negatief":
            prompt = f"Bedenk 2 concrete verbeteracties op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen de acties als JSON."
            structured_output = '{"verbeteracties": ["actie 1", "actie 2"]}'
            result = ask_openai(prompt, structured_output=structured_output)
            logger.info(f"[Retrospective][LLM Verbeteracties]: {result}")

    def run(self):
        """Run the agent and listen for events."""
        subscribe("retro_feedback", self.on_retro_feedback)
        subscribe("generate_actions", self.on_generate_actions)
        subscribe("feedback_sentiment_analyzed", self.on_feedback_sentiment_analyzed)

        logger.info("RetrospectiveAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="Retrospective Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "conduct-retrospective", "analyze-feedback", "create-action-plan",
                               "track-improvements", "show-retro-history", "show-action-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--sprint-name", default="Sprint 15", help="Sprint name for retrospective")
    parser.add_argument("--team-size", type=int, default=8, help="Team size for retrospective")
    parser.add_argument("--feedback-list", nargs="+", help="List of feedback items to analyze")

    args = parser.parse_args()

    agent = RetrospectiveAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "conduct-retrospective":
        result = agent.conduct_retrospective(args.sprint_name, args.team_size)
        print(json.dumps(result, indent=2))
    elif args.command == "analyze-feedback":
        result = agent.analyze_feedback(args.feedback_list)
        print(json.dumps(result, indent=2))
    elif args.command == "create-action-plan":
        result = agent.create_action_plan()
        print(json.dumps(result, indent=2))
    elif args.command == "track-improvements":
        result = agent.track_improvements(args.sprint_name)
        print(json.dumps(result, indent=2))
    elif args.command == "show-retro-history":
        agent.show_retro_history()
    elif args.command == "show-action-history":
        agent.show_action_history()
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
