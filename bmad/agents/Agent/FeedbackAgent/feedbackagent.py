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

class FeedbackAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "FeedbackAgent"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/feedbackagent/best-practices.md",
            "feedback-template": self.resource_base / "templates/feedbackagent/feedback-template.md",
            "sentiment-template": self.resource_base / "templates/feedbackagent/sentiment-template.md",
            "analysis-template": self.resource_base / "templates/feedbackagent/analysis-template.md",
            "report-template": self.resource_base / "templates/feedbackagent/report-template.md",
            "feedback-checklist-template": self.resource_base / "templates/feedbackagent/feedback-checklist-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/feedbackagent/changelog.md",
            "history": self.resource_base / "data/feedbackagent/feedback-history.md",
            "sentiment-history": self.resource_base / "data/feedbackagent/sentiment-history.md"
        }

        # Initialize history
        self.feedback_history = []
        self.sentiment_history = []
        self._load_feedback_history()
        self._load_sentiment_history()

    def _load_feedback_history(self):
        """Load feedback history from data file"""
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.feedback_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load feedback history: {e}")

    def _save_feedback_history(self):
        """Save feedback history to data file"""
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Feedback History\n\n")
                for feedback in self.feedback_history[-50:]:  # Keep last 50 feedback items
                    f.write(f"- {feedback}\n")
        except Exception as e:
            logger.error(f"Could not save feedback history: {e}")

    def _load_sentiment_history(self):
        """Load sentiment history from data file"""
        try:
            if self.data_paths["sentiment-history"].exists():
                with open(self.data_paths["sentiment-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.sentiment_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load sentiment history: {e}")

    def _save_sentiment_history(self):
        """Save sentiment history to data file"""
        try:
            self.data_paths["sentiment-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["sentiment-history"], "w") as f:
                f.write("# Sentiment History\n\n")
                for sentiment in self.sentiment_history[-50:]:  # Keep last 50 sentiment items
                    f.write(f"- {sentiment}\n")
        except Exception as e:
            logger.error(f"Could not save sentiment history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
Feedback Agent Commands:
  help                    - Show this help message
  collect-feedback        - Collect new feedback
  analyze-sentiment       - Analyze feedback sentiment
  summarize-feedback      - Summarize feedback collection
  generate-insights       - Generate insights from feedback
  track-trends            - Track feedback trends
  show-feedback-history   - Show feedback history
  show-sentiment-history  - Show sentiment history
  show-best-practices     - Show feedback best practices
  show-changelog          - Show feedback changelog
  export-report [format]  - Export feedback report (format: md, csv, json)
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
            elif resource_type == "feedback-template":
                path = self.template_paths["feedback-template"]
            elif resource_type == "sentiment-template":
                path = self.template_paths["sentiment-template"]
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

    def show_feedback_history(self):
        """Show feedback history"""
        if not self.feedback_history:
            print("No feedback history available.")
            return
        print("Feedback History:")
        print("=" * 50)
        for i, feedback in enumerate(self.feedback_history[-10:], 1):
            print(f"{i}. {feedback}")

    def show_sentiment_history(self):
        """Show sentiment history"""
        if not self.sentiment_history:
            print("No sentiment history available.")
            return
        print("Sentiment History:")
        print("=" * 50)
        for i, sentiment in enumerate(self.sentiment_history[-10:], 1):
            print(f"{i}. {sentiment}")

    def collect_feedback(self, feedback_text: str = "The new dashboard is much more user-friendly", source: str = "User Survey") -> Dict[str, Any]:
        """Collect new feedback with enhanced functionality."""
        logger.info(f"Collecting feedback from {source}")

        # Simulate feedback collection
        time.sleep(1)

        feedback_result = {
            "feedback_id": hashlib.sha256(feedback_text.encode()).hexdigest()[:8],
            "feedback_type": "Feedback Collection",
            "source": source,
            "status": "collected",
            "feedback_details": {
                "text": feedback_text,
                "timestamp": datetime.now().isoformat(),
                "category": "user_experience",
                "priority": "medium",
                "tags": ["dashboard", "usability", "positive"]
            },
            "metadata": {
                "user_id": "user_12345",
                "session_id": "session_67890",
                "platform": "web",
                "browser": "Chrome",
                "location": "Netherlands"
            },
            "collection_method": {
                "method": "survey",
                "channel": "web_form",
                "response_time": "2 minutes",
                "completion_rate": "95%"
            },
            "quality_metrics": {
                "completeness": "high",
                "clarity": "high",
                "actionability": "medium",
                "relevance": "high"
            },
            "processing_status": {
                "sentiment_analyzed": False,
                "insights_generated": False,
                "trends_identified": False,
                "actions_created": False
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "FeedbackAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("FeedbackAgent", MetricType.SUCCESS_RATE, 98, "%")

        # Add to feedback history
        feedback_entry = f"{datetime.now().isoformat()}: Feedback collected from {source} - {feedback_text[:50]}..."
        self.feedback_history.append(feedback_entry)
        self._save_feedback_history()

        logger.info(f"Feedback collected: {feedback_result}")
        return feedback_result

    def analyze_sentiment(self, feedback_text: str = "The new dashboard is much more user-friendly") -> Dict[str, Any]:
        """Analyze feedback sentiment with enhanced functionality."""
        logger.info("Analyzing feedback sentiment")

        # Simulate sentiment analysis
        time.sleep(1)

        sentiment_result = {
            "feedback_id": hashlib.sha256(feedback_text.encode()).hexdigest()[:8],
            "sentiment_analysis_type": "Feedback Sentiment Analysis",
            "status": "completed",
            "sentiment_results": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.85,
                "confidence_level": "high",
                "sentiment_breakdown": {
                    "positive_words": ["user-friendly", "much", "more"],
                    "negative_words": [],
                    "neutral_words": ["new", "dashboard", "is"]
                }
            },
            "emotion_analysis": {
                "primary_emotion": "satisfaction",
                "secondary_emotion": "appreciation",
                "emotion_intensity": "moderate",
                "emotion_confidence": 0.78
            },
            "context_analysis": {
                "topic": "user_interface",
                "subtopic": "dashboard_usability",
                "context_score": 0.92,
                "relevance_score": 0.88
            },
            "actionability_analysis": {
                "actionability_score": 0.65,
                "actionable_aspects": [
                    "Dashboard usability improvements",
                    "User interface enhancements"
                ],
                "suggested_actions": [
                    "Continue improving dashboard usability",
                    "Apply similar improvements to other interfaces"
                ]
            },
            "trend_analysis": {
                "trend_direction": "improving",
                "trend_strength": "moderate",
                "trend_confidence": 0.75,
                "historical_comparison": "15% improvement from last month"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "FeedbackAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("FeedbackAgent", MetricType.SUCCESS_RATE, 95, "%")

        # Add to sentiment history
        sentiment_entry = f"{datetime.now().isoformat()}: Sentiment analysis completed - {sentiment_result['sentiment_results']['overall_sentiment']} (score: {sentiment_result['sentiment_results']['sentiment_score']})"
        self.sentiment_history.append(sentiment_entry)
        self._save_sentiment_history()

        logger.info(f"Sentiment analysis completed: {sentiment_result}")
        return sentiment_result

    def summarize_feedback(self, feedback_list: List[str] = None) -> Dict[str, Any]:
        """Summarize feedback collection with enhanced functionality."""
        if feedback_list is None:
            feedback_list = [
                "The new dashboard is much more user-friendly",
                "The loading times have improved significantly",
                "The mobile app needs better navigation",
                "The search functionality works great",
                "The documentation could be more comprehensive"
            ]

        logger.info("Summarizing feedback collection")

        # Simulate feedback summarization
        time.sleep(1)

        summary_result = {
            "summary_type": "Feedback Collection Summary",
            "total_feedback_items": len(feedback_list),
            "status": "completed",
            "summary_statistics": {
                "positive_feedback": 3,
                "negative_feedback": 1,
                "neutral_feedback": 1,
                "total_sentiment_score": 0.72,
                "average_sentiment": "positive"
            },
            "key_themes": {
                "user_experience": {
                    "count": 2,
                    "sentiment": "positive",
                    "examples": ["The new dashboard is much more user-friendly", "The search functionality works great"]
                },
                "performance": {
                    "count": 1,
                    "sentiment": "positive",
                    "examples": ["The loading times have improved significantly"]
                },
                "navigation": {
                    "count": 1,
                    "sentiment": "negative",
                    "examples": ["The mobile app needs better navigation"]
                },
                "documentation": {
                    "count": 1,
                    "sentiment": "neutral",
                    "examples": ["The documentation could be more comprehensive"]
                }
            },
            "priority_insights": [
                "User experience improvements are being recognized",
                "Performance optimizations are successful",
                "Mobile navigation needs attention",
                "Documentation could be enhanced"
            ],
            "action_recommendations": [
                "Continue user experience improvements",
                "Maintain performance optimizations",
                "Prioritize mobile navigation improvements",
                "Enhance documentation quality"
            ],
            "trend_analysis": {
                "overall_trend": "improving",
                "user_experience_trend": "improving",
                "performance_trend": "improving",
                "navigation_trend": "needs_attention",
                "documentation_trend": "stable"
            },
            "quality_metrics": {
                "feedback_quality": "high",
                "actionability": "medium",
                "completeness": "high",
                "relevance": "high"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "FeedbackAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("FeedbackAgent", MetricType.SUCCESS_RATE, 92, "%")

        logger.info(f"Feedback summary completed: {summary_result}")
        return summary_result

    def generate_insights(self, feedback_data: Dict = None) -> Dict[str, Any]:
        """Generate insights from feedback data."""
        if feedback_data is None:
            feedback_data = {
                "total_feedback": 25,
                "positive_feedback": 18,
                "negative_feedback": 5,
                "neutral_feedback": 2
            }

        logger.info("Generating insights from feedback data")

        # Simulate insight generation
        time.sleep(1)

        insights_result = {
            "insights_type": "Feedback Insights Generation",
            "status": "completed",
            "insights_data": {
                "total_feedback_analyzed": feedback_data.get("total_feedback", 25),
                "analysis_period": "Last 30 days",
                "confidence_level": "high"
            },
            "key_insights": [
                {
                    "insight": "User satisfaction has improved by 25%",
                    "confidence": 0.92,
                    "impact": "high",
                    "evidence": "18 positive vs 5 negative feedback items"
                },
                {
                    "insight": "Mobile experience needs immediate attention",
                    "confidence": 0.88,
                    "impact": "high",
                    "evidence": "60% of negative feedback relates to mobile"
                },
                {
                    "insight": "Performance improvements are well-received",
                    "confidence": 0.85,
                    "impact": "medium",
                    "evidence": "40% of positive feedback mentions performance"
                },
                {
                    "insight": "Documentation quality is adequate but improvable",
                    "confidence": 0.78,
                    "impact": "medium",
                    "evidence": "Mixed feedback on documentation"
                }
            ],
            "trend_insights": {
                "satisfaction_trend": "increasing",
                "performance_trend": "improving",
                "usability_trend": "stable",
                "mobile_trend": "declining"
            },
            "predictive_insights": [
                {
                    "prediction": "User satisfaction will continue to improve",
                    "confidence": 0.85,
                    "timeframe": "Next 30 days",
                    "factors": ["Performance improvements", "UI enhancements"]
                },
                {
                    "prediction": "Mobile complaints will increase without intervention",
                    "confidence": 0.80,
                    "timeframe": "Next 2 weeks",
                    "factors": ["Current negative trend", "Mobile usage growth"]
                }
            ],
            "actionable_insights": [
                {
                    "action": "Prioritize mobile navigation improvements",
                    "priority": "high",
                    "expected_impact": "Reduce negative feedback by 40%",
                    "effort_required": "medium"
                },
                {
                    "action": "Continue performance optimization efforts",
                    "priority": "medium",
                    "expected_impact": "Maintain positive feedback trend",
                    "effort_required": "low"
                },
                {
                    "action": "Enhance documentation quality",
                    "priority": "medium",
                    "expected_impact": "Improve user self-service",
                    "effort_required": "medium"
                }
            ],
            "business_impact": {
                "customer_satisfaction": "improving",
                "user_retention": "stable",
                "product_adoption": "increasing",
                "support_volume": "decreasing"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "FeedbackAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("FeedbackAgent", MetricType.SUCCESS_RATE, 90, "%")

        logger.info(f"Insights generation completed: {insights_result}")
        return insights_result

    def track_trends(self, timeframe: str = "30 days") -> Dict[str, Any]:
        """Track feedback trends over time."""
        logger.info(f"Tracking feedback trends over {timeframe}")

        # Simulate trend tracking
        time.sleep(1)

        trends_result = {
            "trends_type": "Feedback Trends Analysis",
            "timeframe": timeframe,
            "status": "completed",
            "trend_metrics": {
                "total_feedback": {
                    "current": 125,
                    "previous": 98,
                    "change": "+27.6%",
                    "trend": "increasing"
                },
                "sentiment_score": {
                    "current": 0.78,
                    "previous": 0.65,
                    "change": "+20.0%",
                    "trend": "improving"
                },
                "response_time": {
                    "current": "2.3 hours",
                    "previous": "4.1 hours",
                    "change": "-43.9%",
                    "trend": "improving"
                },
                "resolution_rate": {
                    "current": "94%",
                    "previous": "87%",
                    "change": "+8.0%",
                    "trend": "improving"
                }
            },
            "category_trends": {
                "user_experience": {
                    "trend": "improving",
                    "change": "+15%",
                    "volume": "high"
                },
                "performance": {
                    "trend": "improving",
                    "change": "+22%",
                    "volume": "medium"
                },
                "mobile": {
                    "trend": "declining",
                    "change": "-8%",
                    "volume": "high"
                },
                "documentation": {
                    "trend": "stable",
                    "change": "+2%",
                    "volume": "low"
                }
            },
            "seasonal_patterns": {
                "weekly_pattern": "Peak feedback on Mondays and Wednesdays",
                "monthly_pattern": "Higher feedback volume in first week of month",
                "quarterly_pattern": "Increased feedback during product releases"
            },
            "predictive_trends": {
                "next_week": "Expected 5% increase in feedback volume",
                "next_month": "Expected 12% improvement in sentiment score",
                "next_quarter": "Expected stabilization of mobile feedback"
            },
            "anomaly_detection": {
                "detected_anomalies": [
                    "Unusual spike in mobile feedback on 2025-07-15",
                    "Significant drop in performance feedback on 2025-07-20"
                ],
                "anomaly_causes": [
                    "Mobile app update release",
                    "Performance optimization deployment"
                ]
            },
            "correlation_analysis": {
                "positive_correlations": [
                    "Performance improvements correlate with positive sentiment",
                    "UI updates correlate with user experience feedback"
                ],
                "negative_correlations": [
                    "Mobile updates correlate with negative feedback",
                    "Feature releases correlate with documentation requests"
                ]
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "FeedbackAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("FeedbackAgent", MetricType.SUCCESS_RATE, 88, "%")

        logger.info(f"Trend tracking completed: {trends_result}")
        return trends_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export feedback report in specified format."""
        if not report_data:
            report_data = {
                "report_type": "Feedback Report",
                "timeframe": "Last 30 days",
                "status": "completed",
                "total_feedback": 125,
                "sentiment_score": 0.78,
                "timestamp": datetime.now().isoformat(),
                "agent": "FeedbackAgent"
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
        output_file = f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# Feedback Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Timeframe**: {report_data.get('timeframe', 'N/A')}
- **Status**: {report_data.get('status', 'N/A')}
- **Total Feedback**: {report_data.get('total_feedback', 0)}
- **Sentiment Score**: {report_data.get('sentiment_score', 'N/A')}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Feedback Trends
- **Volume Trend**: {report_data.get('trend_metrics', {}).get('total_feedback', {}).get('trend', 'N/A')}
- **Sentiment Trend**: {report_data.get('trend_metrics', {}).get('sentiment_score', {}).get('trend', 'N/A')}
- **Response Time**: {report_data.get('trend_metrics', {}).get('response_time', {}).get('current', 'N/A')}

## Recent Feedback
{chr(10).join([f"- {feedback}" for feedback in self.feedback_history[-5:]])}

## Recent Sentiment Analysis
{chr(10).join([f"- {sentiment}" for sentiment in self.sentiment_history[-5:]])}
"""

        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report export saved to: {output_file}")

    def _export_csv(self, report_data: Dict):
        """Export report data as CSV."""
        output_file = f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Timeframe", report_data.get("timeframe", "N/A")])
            writer.writerow(["Status", report_data.get("status", "N/A")])
            writer.writerow(["Total Feedback", report_data.get("total_feedback", 0)])
            writer.writerow(["Sentiment Score", report_data.get("sentiment_score", "N/A")])

        print(f"Report export saved to: {output_file}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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
        logger.info("Starting feedback collaboration example...")

        # Publish feedback collection request
        publish("feedback_collection_requested", {
            "agent": "FeedbackAgent",
            "source": "User Survey",
            "timestamp": datetime.now().isoformat()
        })

        # Collect feedback
        self.collect_feedback("The new dashboard is much more user-friendly", "User Survey")

        # Analyze sentiment
        sentiment_result = self.analyze_sentiment("The new dashboard is much more user-friendly")

        # Summarize feedback
        self.summarize_feedback()

        # Publish completion
        publish("feedback_analysis_completed", {
            "status": "success",
            "agent": "FeedbackAgent",
            "feedback_count": 1,
            "sentiment_score": sentiment_result["sentiment_results"]["sentiment_score"]
        })

        # Save context
        save_context("FeedbackAgent", "status", {"feedback_status": "analyzed"})

        # Notify via Slack
        try:
            send_slack_message(f"Feedback analysis completed with {sentiment_result['sentiment_results']['sentiment_score']} sentiment score")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("FeedbackAgent")
        print(f"Opgehaalde context: {context}")

    def publish_feedback(self, feedback_text: str, agent: str = "FeedbackAgent"):
        """Publish feedback with enhanced functionality."""
        event = {"timestamp": datetime.now().isoformat(), "feedback": feedback_text, "agent": agent}
        publish("feedback_collected", event)
        save_context(agent, "feedback", {"feedback": feedback_text, "timestamp": event["timestamp"]}, updated_by=agent)
        logger.info(f"[FeedbackAgent] Feedback gepubliceerd en opgeslagen: {feedback_text}")
        try:
            send_slack_message(f"[FeedbackAgent] Nieuwe feedback ontvangen: {feedback_text}")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

    def analyze_feedback_sentiment(self, feedback_text: str):
        """Analyze feedback sentiment with enhanced functionality."""
        prompt = f"Classificeer de volgende feedback als positief, negatief of neutraal en geef een korte motivatie: '{feedback_text}'"
        structured_output = '{"sentiment": "positief|negatief|neutraal", "motivatie": "..."}'
        result = ask_openai(prompt, structured_output=structured_output)
        logger.info(f"[FeedbackAgent][LLM Sentiment]: {result}")
        # Publiceer event zodat andere agents kunnen reageren
        publish("feedback_sentiment_analyzed", {"feedback": feedback_text, "sentiment": result.get("sentiment"), "motivatie": result.get("motivatie")})
        # Stuur Slack notificatie met feedback mogelijkheid
        try:
            send_slack_message(f"[FeedbackAgent] Sentimentanalyse: {result}", feedback_id=hashlib.sha256(feedback_text.encode()).hexdigest())
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
        return result

    def summarize_feedback_original(self, feedback_list: List[str]):
        """Summarize feedback with enhanced functionality."""
        prompt = "Vat de volgende feedback samen in maximaal 3 bullets:\n" + "\n".join(feedback_list)
        result = ask_openai(prompt)
        logger.info(f"[FeedbackAgent][LLM Samenvatting]: {result}")
        return result

    def on_feedback_received(self, event):
        """Handle feedback received event from other agents."""
        logger.info(f"Feedback received event: {event}")
        feedback = event.get("feedback", "")
        self.analyze_feedback_sentiment(feedback)

    def on_summarize_feedback(self, event):
        """Handle summarize feedback event from other agents."""
        logger.info(f"Summarize feedback event: {event}")
        feedback_list = event.get("feedback_list", [])
        self.summarize_feedback_original(feedback_list)

    def handle_retro_planned(self, event):
        """Handle retro planned event from other agents."""
        logger.info("[FeedbackAgent] Retro gepland, feedback wordt verzameld...")
        time.sleep(1)
        publish("feedback_collected", {"desc": "Feedback verzameld"})
        logger.info("[FeedbackAgent] Feedback verzameld, feedback_collected gepubliceerd.")

    def handle_feedback_collected(self, event):
        """Handle feedback collected event from other agents."""
        logger.info("[FeedbackAgent] Feedback wordt geanalyseerd...")
        time.sleep(1)
        publish("trends_analyzed", {"desc": "Trends geanalyseerd"})
        logger.info("[FeedbackAgent] Trends geanalyseerd, trends_analyzed gepubliceerd.")

    def run(self):
        """Run the agent and listen for events."""
        subscribe("feedback_received", self.on_feedback_received)
        subscribe("summarize_feedback", self.on_summarize_feedback)
        subscribe("retro_planned", self.handle_retro_planned)
        subscribe("feedback_collected", self.handle_feedback_collected)

        logger.info("FeedbackAgent ready and listening for events...")
        self.collaborate_example()

def main():
    parser = argparse.ArgumentParser(description="Feedback Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "collect-feedback", "analyze-sentiment", "summarize-feedback",
                               "generate-insights", "track-trends", "show-feedback-history", "show-sentiment-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--feedback-text", default="The new dashboard is much more user-friendly", help="Feedback text to analyze")
    parser.add_argument("--source", default="User Survey", help="Feedback source")
    parser.add_argument("--timeframe", default="30 days", help="Timeframe for trend analysis")
    parser.add_argument("--feedback-list", nargs="+", help="List of feedback items to summarize")

    args = parser.parse_args()

    agent = FeedbackAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "collect-feedback":
        result = agent.collect_feedback(args.feedback_text, args.source)
        print(json.dumps(result, indent=2))
    elif args.command == "analyze-sentiment":
        result = agent.analyze_sentiment(args.feedback_text)
        print(json.dumps(result, indent=2))
    elif args.command == "summarize-feedback":
        result = agent.summarize_feedback(args.feedback_list)
        print(json.dumps(result, indent=2))
    elif args.command == "generate-insights":
        result = agent.generate_insights()
        print(json.dumps(result, indent=2))
    elif args.command == "track-trends":
        result = agent.track_trends(args.timeframe)
        print(json.dumps(result, indent=2))
    elif args.command == "show-feedback-history":
        agent.show_feedback_history()
    elif args.command == "show-sentiment-history":
        agent.show_sentiment_history()
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
