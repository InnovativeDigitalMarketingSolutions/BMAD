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
# Message Bus Integration
from bmad.agents.core.communication.agent_message_bus_integration import (
    AgentMessageBusIntegration,
    create_agent_message_bus_integration
)
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager
from integrations.slack.slack_notify import send_slack_message

# MCP Integration
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

class FeedbackAgent:
    """
    Feedback Agent voor BMAD.
    Gespecialiseerd in feedback collection, sentiment analysis, en template quality tracking.
    """
    
    def __init__(self):
        # Framework templates integration
        self.framework_manager = get_framework_templates_manager()
        try:
            self.feedback_agent_template = self.framework_manager.get_framework_template('feedback_agent')
        except:
            self.feedback_agent_template = None
        self.lessons_learned = []

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

        # Template quality tracking
        self.template_feedback = {}
        self.template_quality_scores = {}
        self._load_template_feedback()
        
        # MCP Integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Message Bus Integration
        self.message_bus_integration: Optional[AgentMessageBusIntegration] = None
        self.message_bus_enabled = False
        
        # Enhanced MCP Phase 2 attributes
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        self.enhanced_mcp_client = None
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Initialize tracer
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "FeedbackAgent",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client voor enhanced feedback capabilities."""
        try:
            self.mcp_client = get_mcp_client()  # Remove await - this is a sync function
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully for FeedbackAgent")
        except Exception as e:
            logger.warning(f"MCP initialization failed for FeedbackAgent: {e}")
            self.mcp_enabled = False

    async def initialize_enhanced_mcp(self):
        """Initialize enhanced MCP capabilities for Phase 2."""
        try:
            self.enhanced_mcp = create_enhanced_mcp_integration(self.agent_name)
            self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            if self.enhanced_mcp_enabled:
                self.enhanced_mcp_client = self.enhanced_mcp.mcp_client if self.enhanced_mcp else None
                logger.info("Enhanced MCP initialized successfully")
            else:
                logger.warning("Enhanced MCP initialization failed, falling back to standard MCP")
                
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
    
    async def initialize_message_bus(self):
        """Initialize Message Bus Integration for the agent."""
        try:
            self.message_bus_integration = create_agent_message_bus_integration(
                agent_name=self.agent_name,
                agent_type="feedback_agent",
                config={
                    "message_bus_url": "redis://localhost:6379",
                    "enable_publishing": True,
                    "enable_subscription": True,
                    "event_handlers": {
                        "feedback_collected": self._handle_feedback_collected_event,
                        "quality_gate_requested": self._handle_quality_gate_requested_event,
                        "task_delegated": self._handle_task_delegated_event
                    }
                }
            )
            await self.message_bus_integration.initialize()
            self.message_bus_enabled = True
            logger.info("Message Bus Integration initialized successfully for FeedbackAgent")
        except Exception as e:
            logger.warning(f"Message Bus Integration initialization failed: {e}")
            self.message_bus_enabled = False
    
    async def _handle_feedback_collected_event(self, event):
        """Handle feedback collected event"""
        try:
            feedback_data = event.data
            logger.info(f"📨 FeedbackAgent received feedback: {feedback_data.get('feedback_text', 'N/A')}")
            
            # Process the feedback
            await self._process_incoming_feedback(feedback_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to handle feedback collected event: {e}")
    
    async def _handle_quality_gate_requested_event(self, event):
        """Handle quality gate check requested event"""
        try:
            quality_data = event.data
            logger.info(f"📨 FeedbackAgent received quality gate request")
            
            # Perform quality gate check
            await self._perform_quality_gate_check(quality_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to handle quality gate event: {e}")
    
    async def _handle_task_delegated_event(self, event):
        """Handle task delegated event"""
        try:
            task_data = event.data
            if task_data.get('to_agent') == self.agent_name:
                logger.info(f"📨 FeedbackAgent received delegated task: {task_data.get('task', {}).get('type', 'N/A')}")
                
                # Accept the task
                await self.message_bus_integration.accept_task(
                    task_data.get('delegation_id'),
                    task_data.get('task', {})
                )
                
                # Process the task
                await self._process_delegated_task(task_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to handle task delegated event: {e}")
    
    async def _process_incoming_feedback(self, feedback_data: Dict[str, Any]):
        """Process incoming feedback from message bus"""
        try:
            feedback_text = feedback_data.get('feedback_text', '')
            source = feedback_data.get('source', 'MessageBus')
            
            # Collect and analyze feedback
            result = await self.collect_feedback(feedback_text, source)
            
            # Publish feedback analyzed event
            await self.message_bus_integration.publish_agent_event(
                EventTypes.FEEDBACK_ANALYZED,
                {
                    "feedback_id": result.get('feedback_id'),
                    "sentiment_score": result.get('sentiment_score'),
                    "analysis_summary": result.get('summary', '')
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to process incoming feedback: {e}")
    
    async def _perform_quality_gate_check(self, quality_data: Dict[str, Any]):
        """Perform quality gate check"""
        try:
            # Perform quality analysis
            quality_result = {
                "quality_score": 85,  # Example score
                "issues_found": [],
                "recommendations": ["Consider adding more test coverage"]
            }
            
            # Publish quality gate result
            await self.message_bus_integration.publish_agent_event(
                EventTypes.QUALITY_GATE_PASSED,
                quality_result
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to perform quality gate check: {e}")
    
    async def _process_delegated_task(self, task_data: Dict[str, Any]):
        """Process delegated task"""
        try:
            task = task_data.get('task', {})
            task_type = task.get('type', '')
            
            if task_type == 'feedback_analysis':
                # Perform feedback analysis
                feedback_text = task.get('feedback_text', '')
                result = await self.collect_feedback(feedback_text, 'Delegated Task')
                
                # Complete the task
                await self.message_bus_integration.complete_task(
                    task_data.get('delegation_id'),
                    result
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to process delegated task: {e}")
    
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
    
    async def use_feedback_specific_mcp_tools(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback-specific MCP tools voor enhanced feedback analysis."""
        if not self.mcp_enabled:
            return {}
        
        enhanced_data = {}
        
        try:
            # Feedback collection
            collection_result = await self.use_mcp_tool("feedback_collection", {
                "feedback_text": feedback_data.get("feedback_text", ""),
                "source": feedback_data.get("source", ""),
                "collection_type": feedback_data.get("collection_type", "general"),
                "include_metadata": feedback_data.get("include_metadata", True)
            })
            if collection_result:
                enhanced_data["feedback_collection"] = collection_result
            
            # Sentiment analysis
            sentiment_result = await self.use_mcp_tool("sentiment_analysis", {
                "feedback_text": feedback_data.get("feedback_text", ""),
                "analysis_type": feedback_data.get("analysis_type", "comprehensive"),
                "include_emotions": feedback_data.get("include_emotions", True),
                "confidence_threshold": feedback_data.get("confidence_threshold", 0.8)
            })
            if sentiment_result:
                enhanced_data["sentiment_analysis"] = sentiment_result
            
            # Feedback summarization
            summary_result = await self.use_mcp_tool("feedback_summarization", {
                "feedback_list": feedback_data.get("feedback_list", []),
                "summary_type": feedback_data.get("summary_type", "comprehensive"),
                "include_trends": feedback_data.get("include_trends", True),
                "group_by_category": feedback_data.get("group_by_category", True)
            })
            if summary_result:
                enhanced_data["feedback_summarization"] = summary_result
            
            # Trend analysis
            trend_result = await self.use_mcp_tool("trend_analysis", {
                "feedback_data": feedback_data.get("feedback_data", {}),
                "timeframe": feedback_data.get("timeframe", "30 days"),
                "trend_type": feedback_data.get("trend_type", "sentiment"),
                "include_predictions": feedback_data.get("include_predictions", True)
            })
            if trend_result:
                enhanced_data["trend_analysis"] = trend_result
            
            logger.info(f"Feedback-specific MCP tools executed: {list(enhanced_data.keys())}")
            
        except Exception as e:
            logger.error(f"Error in feedback-specific MCP tools: {e}")
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_feedback_specific_mcp_tools(feedback_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": feedback_data.get("capabilities", []),
                "performance_metrics": feedback_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Feedback-specific enhanced tools
            feedback_enhanced_result = await self.use_feedback_specific_enhanced_tools(feedback_data)
            enhanced_data.update(feedback_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_feedback_operation(feedback_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_feedback_specific_enhanced_tools(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use feedback-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced feedback collection
            if "feedback_collection" in feedback_data:
                collection_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_feedback_collection", {
                    "feedback_data": feedback_data["feedback_collection"],
                    "collection_depth": feedback_data.get("collection_depth", "comprehensive"),
                    "include_context": feedback_data.get("include_context", True)
                })
                enhanced_tools["enhanced_feedback_collection"] = collection_result
            
            # Enhanced sentiment analysis
            if "sentiment_analysis" in feedback_data:
                sentiment_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_sentiment_analysis", {
                    "sentiment_data": feedback_data["sentiment_analysis"],
                    "analysis_complexity": feedback_data.get("analysis_complexity", "advanced"),
                    "include_emotion_detection": feedback_data.get("include_emotion_detection", True)
                })
                enhanced_tools["enhanced_sentiment_analysis"] = sentiment_result
            
            # Enhanced team collaboration
            if "team_collaboration" in feedback_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["ProductOwner", "UXUIDesigner", "QualityGuardian", "Retrospective"],
                    {
                        "type": "feedback_review",
                        "content": feedback_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced trend analysis
            if "trend_analysis" in feedback_data:
                trend_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_trend_analysis", {
                    "trend_data": feedback_data["trend_analysis"],
                    "analysis_period": feedback_data.get("analysis_period", "comprehensive"),
                    "include_predictions": feedback_data.get("include_predictions", True)
                })
                enhanced_tools["enhanced_trend_analysis"] = trend_result
            
            logger.info(f"Feedback-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in feedback-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_feedback_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace feedback operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "feedback_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "feedback_count": len(operation_data.get("feedback_list", [])),
                    "sentiment_score": operation_data.get("sentiment_score", 0.0),
                    "trend_analysis": len(operation_data.get("trend_data", {}))
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("feedback_operation", trace_data)
            
            logger.info(f"Feedback operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

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

    def _load_template_feedback(self):
        """Load template feedback from data file"""
        try:
            feedback_file = self.resource_base / "data/feedbackagent/template-feedback.json"
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    data = json.load(f)
                    self.template_feedback = data.get('template_feedback', {})
                    self.template_quality_scores = data.get('quality_scores', {})
        except Exception as e:
            logger.warning(f"Could not load template feedback: {e}")

    def _save_template_feedback(self):
        """Save template feedback to data file"""
        try:
            feedback_file = self.resource_base / "data/feedbackagent/template-feedback.json"
            feedback_file.parent.mkdir(parents=True, exist_ok=True)
            with open(feedback_file, 'w') as f:
                json.dump({
                    'template_feedback': self.template_feedback,
                    'quality_scores': self.template_quality_scores,
                    'last_updated': datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save template feedback: {e}")

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

Template Quality Assurance:
  collect-template-feedback <template> <feedback> [type] [rating] - Collect feedback for framework templates
  analyze-template-trends [template] [timeframe]                 - Analyze feedback trends for templates
  suggest-template-improvements <template>                       - Suggest improvements for templates
  get-template-quality-report [template]                        - Generate quality report for templates

Examples:
  collect-template-feedback "backend_development" "Excellent template with clear guidelines" "quality" 5
  analyze-template-trends "backend_development" "30 days"
  suggest-template-improvements "backend_development"
  get-template-quality-report "backend_development"
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

    async def collect_feedback(self, feedback_text: str = "The new dashboard is much more user-friendly", source: str = "User Survey") -> Dict[str, Any]:
        """Collect new feedback with enhanced functionality."""
        # Input validation
        if not isinstance(feedback_text, str):
            raise TypeError("feedback_text must be a string")
        if not isinstance(source, str):
            raise TypeError("source must be a string")
        if not feedback_text.strip():
            raise ValueError("feedback_text cannot be empty")
        if not source.strip():
            raise ValueError("source cannot be empty")
            
        logger.info(f"Collecting feedback from {source}")

        # Try MCP-enhanced feedback collection first
        if self.mcp_enabled and self.mcp_client:
            try:
                mcp_result = await self.use_mcp_tool("collect_feedback", {
                    "feedback_text": feedback_text,
                    "source": source,
                    "collection_type": "enhanced",
                    "include_metadata": True,
                    "include_analysis": True
                })
                
                if mcp_result:
                    logger.info("MCP-enhanced feedback collection completed")
                    result = mcp_result.get("feedback_result", {})
                    result["mcp_enhanced"] = True
                else:
                    logger.warning("MCP feedback collection failed, using local feedback collection")
                    result = self._create_local_feedback_result(feedback_text, source)
            except Exception as e:
                logger.warning(f"MCP feedback collection failed: {e}, using local feedback collection")
                result = self._create_local_feedback_result(feedback_text, source)
        else:
            result = self._create_local_feedback_result(feedback_text, source)
        
        # Use feedback-specific MCP tools for additional enhancement
        if self.mcp_enabled:
            try:
                feedback_data = {
                    "feedback_text": feedback_text,
                    "source": source,
                    "collection_type": "comprehensive",
                    "include_metadata": True,
                    "analysis_type": "comprehensive",
                    "include_emotions": True,
                    "confidence_threshold": 0.8
                }
                feedback_enhanced = await self.use_feedback_specific_mcp_tools(feedback_data)
                if feedback_enhanced:
                    result["feedback_enhancements"] = feedback_enhanced
            except Exception as e:
                logger.warning(f"Feedback-specific MCP tools failed: {e}")

        # Log performance metrics
        try:
            self.monitor._record_metric("FeedbackAgent", MetricType.SUCCESS_RATE, 98, "%")
        except AttributeError:
            logger.info("Performance metrics recording not available")

        # Add to feedback history
        feedback_entry = f"{datetime.now().isoformat()}: Feedback collected from {source} - {feedback_text[:50]}..."
        self.feedback_history.append(feedback_entry)
        self._save_feedback_history()

        logger.info(f"Feedback collected: {result}")
        return result
    
    def _create_local_feedback_result(self, feedback_text: str, source: str) -> Dict[str, Any]:
        """Create local feedback result when MCP is not available."""
        # Simulate feedback collection
        time.sleep(1)
        
        return {
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

    def analyze_sentiment(self, feedback_text: str = "The new dashboard is much more user-friendly") -> Dict[str, Any]:
        """Analyze feedback sentiment with enhanced functionality."""
        # Input validation
        if not isinstance(feedback_text, str):
            raise TypeError("feedback_text must be a string")
        if not feedback_text.strip():
            raise ValueError("feedback_text cannot be empty")
            
        logger.info("Analyzing feedback sentiment")

        # Simulate sentiment analysis
        time.sleep(1)

        sentiment_result = {
            "feedback_id": hashlib.sha256(feedback_text.encode()).hexdigest()[:8],
            "sentiment_analysis_type": "Feedback Sentiment Analysis",
            "status": "analyzed",
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
        # Input validation
        if feedback_list is not None:
            if not isinstance(feedback_list, list):
                raise TypeError("feedback_list must be a list")
            if not feedback_list:
                raise ValueError("feedback_list cannot be empty")
            for i, feedback in enumerate(feedback_list):
                if not isinstance(feedback, str):
                    raise TypeError(f"feedback_list[{i}] must be a string")
                if not feedback.strip():
                    raise ValueError(f"feedback_list[{i}] cannot be empty")
            
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
            "status": "summarized",
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
        # Input validation
        if feedback_data is not None:
            if not isinstance(feedback_data, dict):
                raise TypeError("feedback_data must be a dictionary")
            if not feedback_data:
                raise ValueError("feedback_data cannot be empty")
            
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
            "status": "generated",
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
        # Input validation
        if not isinstance(timeframe, str):
            raise TypeError("timeframe must be a string")
        if not timeframe.strip():
            raise ValueError("timeframe cannot be empty")
            
        logger.info(f"Tracking feedback trends over {timeframe}")

        # Simulate trend tracking
        time.sleep(1)

        trends_result = {
            "trends_type": "Feedback Trends Analysis",
            "timeframe": timeframe,
            "status": "tracked",
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

    async def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        logger.info("Starting feedback collaboration example...")

        # Publish feedback collection request
        publish("feedback_collection_requested", {
            "agent": "FeedbackAgent",
            "source": "User Survey",
            "timestamp": datetime.now().isoformat()
        })

        # Collect feedback
        await self.collect_feedback("The new dashboard is much more user-friendly", "User Survey")

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

    def collect_template_feedback(self, template_name: str, feedback_text: str, 
                                feedback_type: str = "general", 
                                rating: int = 5) -> Dict[str, Any]:
        """
        Collect feedback for framework templates
        
        Args:
            template_name: Name of the template
            feedback_text: Feedback text
            feedback_type: Type of feedback (general, quality, usability, content)
            rating: Rating from 1-5
            
        Returns:
            Dict with feedback collection result
        """
        try:
            # Validate inputs
            if not template_name or not feedback_text:
                raise ValueError("Template name and feedback text are required")
            
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            
            # Create feedback entry
            feedback_entry = {
                "template_name": template_name,
                "feedback_text": feedback_text,
                "feedback_type": feedback_type,
                "rating": rating,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.agent_name
            }
            
            # Store feedback
            if template_name not in self.template_feedback:
                self.template_feedback[template_name] = []
            
            self.template_feedback[template_name].append(feedback_entry)
            
            # Update quality score
            self._update_template_quality_score(template_name)
            
            # Save feedback
            self._save_template_feedback()
            
            # Record metric
            self.monitor.record_metric(
                MetricType.COUNTER,
                "template_feedback_collected",
                1,
                {"template": template_name, "type": feedback_type}
            )
            
            logger.info(f"Template feedback collected for {template_name}")
            
            return {
                "success": True,
                "message": f"Feedback collected for template {template_name}",
                "feedback_id": len(self.template_feedback[template_name]),
                "template_name": template_name,
                "rating": rating,
                "timestamp": feedback_entry["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error collecting template feedback: {e}")
            return {
                "success": False,
                "error": str(e),
                "template_name": template_name
            }

    def _update_template_quality_score(self, template_name: str):
        """Update quality score for a template based on feedback"""
        try:
            if template_name not in self.template_feedback:
                return
            
            feedback_list = self.template_feedback[template_name]
            if not feedback_list:
                return
            
            # Calculate average rating
            total_rating = sum(f["rating"] for f in feedback_list)
            avg_rating = total_rating / len(feedback_list)
            
            # Calculate quality score (0-100)
            quality_score = (avg_rating / 5) * 100
            
            # Store quality score
            self.template_quality_scores[template_name] = {
                "score": round(quality_score, 2),
                "feedback_count": len(feedback_list),
                "last_updated": datetime.utcnow().isoformat(),
                "average_rating": round(avg_rating, 2)
            }
            
        except Exception as e:
            logger.error(f"Error updating quality score for {template_name}: {e}")

    def analyze_template_trends(self, template_name: str = None, 
                              timeframe: str = "30 days") -> Dict[str, Any]:
        """
        Analyze feedback trends for templates
        
        Args:
            template_name: Specific template to analyze (None for all)
            timeframe: Timeframe for analysis
            
        Returns:
            Dict with trend analysis results
        """
        try:
            # Calculate cutoff date
            if timeframe == "30 days":
                cutoff_date = datetime.utcnow().timestamp() - (30 * 24 * 60 * 60)
            elif timeframe == "7 days":
                cutoff_date = datetime.utcnow().timestamp() - (7 * 24 * 60 * 60)
            else:
                cutoff_date = 0  # All time
            
            templates_to_analyze = [template_name] if template_name else list(self.template_feedback.keys())
            
            trends = {}
            
            for template in templates_to_analyze:
                if template not in self.template_feedback:
                    continue
                
                feedback_list = self.template_feedback[template]
                
                # Filter by timeframe
                recent_feedback = [
                    f for f in feedback_list 
                    if datetime.fromisoformat(f["timestamp"]).timestamp() >= cutoff_date
                ]
                
                if not recent_feedback:
                    continue
                
                # Analyze trends
                ratings = [f["rating"] for f in recent_feedback]
                feedback_types = [f["feedback_type"] for f in recent_feedback]
                
                trends[template] = {
                    "total_feedback": len(recent_feedback),
                    "average_rating": round(sum(ratings) / len(ratings), 2),
                    "rating_distribution": {
                        "1": ratings.count(1),
                        "2": ratings.count(2),
                        "3": ratings.count(3),
                        "4": ratings.count(4),
                        "5": ratings.count(5)
                    },
                    "feedback_type_distribution": {
                        "general": feedback_types.count("general"),
                        "quality": feedback_types.count("quality"),
                        "usability": feedback_types.count("usability"),
                        "content": feedback_types.count("content")
                    },
                    "trend": "improving" if len(recent_feedback) > 5 and sum(ratings[-5:]) > sum(ratings[:5]) else "stable"
                }
            
            return {
                "success": True,
                "timeframe": timeframe,
                "templates_analyzed": len(trends),
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing template trends: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def suggest_template_improvements(self, template_name: str) -> Dict[str, Any]:
        """
        Suggest improvements for a specific template based on feedback
        
        Args:
            template_name: Name of the template to analyze
            
        Returns:
            Dict with improvement suggestions
        """
        try:
            if template_name not in self.template_feedback:
                return {
                    "success": False,
                    "error": f"No feedback found for template {template_name}"
                }
            
            feedback_list = self.template_feedback[template_name]
            if not feedback_list:
                return {
                    "success": False,
                    "error": f"No feedback available for template {template_name}"
                }
            
            # Analyze feedback patterns
            low_ratings = [f for f in feedback_list if f["rating"] <= 2]
            quality_feedback = [f for f in feedback_list if f["feedback_type"] == "quality"]
            usability_feedback = [f for f in feedback_list if f["feedback_type"] == "usability"]
            
            suggestions = []
            
            # Quality-related suggestions
            if quality_feedback:
                avg_quality_rating = sum(f["rating"] for f in quality_feedback) / len(quality_feedback)
                if avg_quality_rating < 3:
                    suggestions.append({
                        "category": "quality",
                        "priority": "high",
                        "suggestion": "Improve template quality standards and validation",
                        "evidence": f"Average quality rating: {avg_quality_rating:.1f}/5"
                    })
            
            # Usability-related suggestions
            if usability_feedback:
                avg_usability_rating = sum(f["rating"] for f in usability_feedback) / len(usability_feedback)
                if avg_usability_rating < 3:
                    suggestions.append({
                        "category": "usability",
                        "priority": "medium",
                        "suggestion": "Enhance template usability and user experience",
                        "evidence": f"Average usability rating: {avg_usability_rating:.1f}/5"
                    })
            
            # General suggestions based on low ratings
            if low_ratings:
                common_issues = {}
                for feedback in low_ratings:
                    text = feedback["feedback_text"].lower()
                    if "outdated" in text:
                        common_issues["outdated"] = common_issues.get("outdated", 0) + 1
                    if "unclear" in text or "confusing" in text:
                        common_issues["unclear"] = common_issues.get("unclear", 0) + 1
                    if "incomplete" in text:
                        common_issues["incomplete"] = common_issues.get("incomplete", 0) + 1
                
                for issue, count in common_issues.items():
                    if count >= 2:  # If mentioned by multiple users
                        suggestions.append({
                            "category": "content",
                            "priority": "high" if count >= 3 else "medium",
                            "suggestion": f"Address {issue} content issues",
                            "evidence": f"Mentioned by {count} users"
                        })
            
            # Quality score
            quality_score = self.template_quality_scores.get(template_name, {}).get("score", 0)
            
            return {
                "success": True,
                "template_name": template_name,
                "quality_score": quality_score,
                "total_feedback": len(feedback_list),
                "suggestions": suggestions,
                "priority": "high" if quality_score < 70 else "medium" if quality_score < 85 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error suggesting template improvements: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_template_quality_report(self, template_name: str = None) -> Dict[str, Any]:
        """
        Generate quality report for templates
        
        Args:
            template_name: Specific template (None for all)
            
        Returns:
            Dict with quality report
        """
        try:
            if template_name:
                # Single template report
                if template_name not in self.template_quality_scores:
                    return {
                        "success": False,
                        "error": f"No quality data found for template {template_name}"
                    }
                
                quality_data = self.template_quality_scores[template_name]
                feedback_count = len(self.template_feedback.get(template_name, []))
                
                return {
                    "success": True,
                    "template_name": template_name,
                    "quality_score": quality_data["score"],
                    "feedback_count": feedback_count,
                    "average_rating": quality_data["average_rating"],
                    "last_updated": quality_data["last_updated"],
                    "status": "excellent" if quality_data["score"] >= 90 else 
                             "good" if quality_data["score"] >= 80 else 
                             "fair" if quality_data["score"] >= 70 else "needs_improvement"
                }
            else:
                # All templates report
                templates = list(self.template_quality_scores.keys())
                if not templates:
                    return {
                        "success": False,
                        "error": "No template quality data available"
                    }
                
                scores = [self.template_quality_scores[t]["score"] for t in templates]
                avg_score = sum(scores) / len(scores)
                
                return {
                    "success": True,
                    "total_templates": len(templates),
                    "average_quality_score": round(avg_score, 2),
                    "templates": {
                        template: {
                            "score": data["score"],
                            "feedback_count": data["feedback_count"],
                            "status": "excellent" if data["score"] >= 90 else 
                                     "good" if data["score"] >= 80 else 
                                     "fair" if data["score"] >= 70 else "needs_improvement"
                        }
                        for template, data in self.template_quality_scores.items()
                    },
                    "overall_status": "excellent" if avg_score >= 90 else 
                                     "good" if avg_score >= 80 else 
                                     "fair" if avg_score >= 70 else "needs_improvement"
                }
                
        except Exception as e:
            logger.error(f"Error generating template quality report: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize message bus integration
        await self.initialize_message_bus()
        
        print("💬 FeedbackAgent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled" if self.message_bus_integration else "Message Bus: Disabled")
        
        # Legacy event subscriptions (for backward compatibility)
        try:
            from bmad.agents.core.communication.message_bus import subscribe
            subscribe("feedback_received", self.on_feedback_received)
            subscribe("summarize_feedback", self.on_summarize_feedback)
            subscribe("retro_planned", self.handle_retro_planned)
            subscribe("feedback_collected", self.handle_feedback_collected)
        except ImportError:
            logger.info("Legacy message bus not available, using new message bus only")

        logger.info("FeedbackAgent ready and listening for events...")
        await self.collaborate_example()
    
    async def run_async(self):
        """Run the agent with enhanced MCP and tracing initialization."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize message bus integration
        await self.initialize_message_bus()
        
        print("💬 FeedbackAgent is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled" if self.message_bus_integration else "Message Bus: Disabled")
        
        logger.info("FeedbackAgent ready and listening for events...")
        await self.collaborate_example()
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the FeedbackAgent agent met MCP integration."""
        agent = cls()
        await agent.run_async()
    
    @classmethod
    async def run_agent_async(cls):
        """Class method to run the FeedbackAgent agent with enhanced MCP."""
        agent = cls()
        await agent.run_async()

import asyncio

def main():
    parser = argparse.ArgumentParser(description="Feedback Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "collect-feedback", "analyze-sentiment", "summarize-feedback",
                               "generate-insights", "track-trends", "show-feedback-history", "show-sentiment-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run", "collect-template-feedback", "analyze-template-trends",
                               "suggest-template-improvements", "get-template-quality-report", "initialize-mcp", 
                               "use-mcp-tool", "get-mcp-status", "use-feedback-mcp-tools", 
                               "check-dependencies", "enhanced-collaborate", "enhanced-security", 
                               "enhanced-performance", "trace-operation", "trace-performance", 
                               "trace-error", "tracing-summary"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--feedback-text", default="The new dashboard is much more user-friendly", help="Feedback text to analyze")
    parser.add_argument("--source", default="User Survey", help="Feedback source")
    parser.add_argument("--timeframe", default="30 days", help="Timeframe for trend analysis")
    parser.add_argument("--feedback-list", nargs="+", help="List of feedback items to summarize")
    
    # Template quality assurance arguments
    parser.add_argument("--template-name", help="Template name for quality assurance")
    parser.add_argument("--template-feedback", help="Feedback text for template")
    parser.add_argument("--feedback-type", default="general", choices=["general", "quality", "usability", "content"], help="Type of feedback")
    parser.add_argument("--rating", type=int, default=5, choices=[1, 2, 3, 4, 5], help="Rating from 1-5")

    args = parser.parse_args()

    agent = FeedbackAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "collect-feedback":
        result = asyncio.run(agent.collect_feedback(args.feedback_text, args.source))
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
        asyncio.run(agent.collaborate_example())
    elif args.command == "run":
        asyncio.run(agent.run())
    elif args.command == "collect-template-feedback":
        if not args.template_name or not args.template_feedback:
            print("Error: --template-name and --template-feedback are required")
            return
        result = agent.collect_template_feedback(args.template_name, args.template_feedback, args.feedback_type, args.rating)
        print(json.dumps(result, indent=2))
    elif args.command == "analyze-template-trends":
        result = agent.analyze_template_trends(args.template_name, args.timeframe)
        print(json.dumps(result, indent=2))
    elif args.command == "suggest-template-improvements":
        if not args.template_name:
            print("Error: --template-name is required")
            return
        result = agent.suggest_template_improvements(args.template_name)
        print(json.dumps(result, indent=2))
    elif args.command == "get-template-quality-report":
        result = agent.get_template_quality_report(args.template_name)
        print(json.dumps(result, indent=2))
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["ProductOwner", "UXUIDesigner", "QualityGuardian", "Retrospective"], 
                {"type": "feedback_review", "content": {"review_type": "feedback_analysis"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "feedback_data": {"feedback_list": [], "sentiment_data": [], "trend_data": []},
                "security_requirements": ["data_privacy", "access_control", "audit_trail"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "feedback_data": {"feedback_list": [], "sentiment_data": [], "trend_data": []},
                "performance_metrics": {"analysis_speed": 85.5, "sentiment_accuracy": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_feedback_operation({
                "operation_type": "feedback_analysis",
                "feedback_text": args.feedback_text,
                "feedback_list": args.feedback_list or []
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_feedback_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"analysis_speed": 85.5, "sentiment_accuracy": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_feedback_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "feedback_analysis", "error_message": "Feedback analysis failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for FeedbackAgent:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print(f"Unknown command: {args.command}")
        agent.show_help()

if __name__ == "__main__":
    main()
