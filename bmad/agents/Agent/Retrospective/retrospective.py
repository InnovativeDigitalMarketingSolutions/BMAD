import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
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

class RetrospectiveAgent:
    def __init__(self):
        # Set agent name
        self.agent_name = "Retrospective"
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

        # Initialize MCP integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2 attributes
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        self.enhanced_mcp_client = None
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False
        
        # Initialize tracer
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "Retrospective",
            "service_version": "1.0.0",
            "environment": "development",
            "sample_rate": 1.0,
            "exporters": []
        })())
        
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
                logger.info("Tracing initialized successfully")
            else:
                logger.warning("Tracer not available or missing initialize method")
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

    async def use_retrospective_specific_mcp_tools(self, retro_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use retrospective-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # Retrospective analysis
        retro_analysis_result = await self.use_mcp_tool("retrospective_analysis", {
            "sprint_name": retro_data.get("sprint_name", ""),
            "team_size": retro_data.get("team_size", 8),
            "feedback_list": retro_data.get("feedback_list", []),
            "analysis_type": "comprehensive"
        })
        if retro_analysis_result:
            enhanced_data["retrospective_analysis"] = retro_analysis_result
        
        # Action plan generation
        action_plan_result = await self.use_mcp_tool("action_plan_generation", {
            "retrospective_data": retro_data.get("retrospective_data", {}),
            "team_capacity": retro_data.get("team_capacity", 100),
            "priority_level": retro_data.get("priority_level", "medium"),
            "timeframe": retro_data.get("timeframe", "next_sprint")
        })
        if action_plan_result:
            enhanced_data["action_plan_generation"] = action_plan_result
        
        # Improvement tracking
        improvement_result = await self.use_mcp_tool("improvement_tracking", {
            "sprint_name": retro_data.get("sprint_name", ""),
            "action_items": retro_data.get("action_items", []),
            "tracking_type": "comprehensive",
            "metrics": retro_data.get("metrics", {})
        })
        if improvement_result:
            enhanced_data["improvement_tracking"] = improvement_result
        
        # Feedback analysis
        feedback_result = await self.use_mcp_tool("feedback_analysis", {
            "feedback_list": retro_data.get("feedback_list", []),
            "analysis_type": "sentiment_and_theme",
            "team_context": retro_data.get("team_context", {}),
            "historical_data": retro_data.get("historical_data", {})
        })
        if feedback_result:
            enhanced_data["feedback_analysis"] = feedback_result
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, retro_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_retrospective_specific_mcp_tools(retro_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": retro_data.get("capabilities", []),
                "performance_metrics": retro_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Retrospective-specific enhanced tools
            retro_enhanced_result = await self.use_retrospective_specific_enhanced_tools(retro_data)
            enhanced_data.update(retro_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_retrospective_operation(retro_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_retrospective_specific_enhanced_tools(self, retro_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use retrospective-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced retrospective analysis
            if "retrospective_analysis" in retro_data:
                analysis_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_retrospective_analysis", {
                    "analysis_data": retro_data["retrospective_analysis"],
                    "analysis_depth": retro_data.get("analysis_depth", "comprehensive"),
                    "include_sentiment": retro_data.get("include_sentiment", True)
                })
                enhanced_tools["enhanced_retrospective_analysis"] = analysis_result
            
            # Enhanced action plan generation
            if "action_plan_generation" in retro_data:
                action_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_action_plan_generation", {
                    "action_data": retro_data["action_plan_generation"],
                    "planning_comprehensive": retro_data.get("planning_comprehensive", "advanced"),
                    "include_tracking": retro_data.get("include_tracking", True)
                })
                enhanced_tools["enhanced_action_plan_generation"] = action_result
            
            # Enhanced team collaboration
            if "team_collaboration" in retro_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["Scrummaster", "ProductOwner", "QualityGuardian", "FeedbackAgent"],
                    {
                        "type": "retrospective_review",
                        "content": retro_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced feedback analysis
            if "feedback_analysis" in retro_data:
                feedback_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_feedback_analysis", {
                    "feedback_data": retro_data["feedback_analysis"],
                    "analysis_comprehensive": retro_data.get("analysis_comprehensive", "advanced"),
                    "include_insights": retro_data.get("include_insights", True)
                })
                enhanced_tools["enhanced_feedback_analysis"] = feedback_result
            
            logger.info(f"Retrospective-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in retrospective-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_retrospective_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace retrospective operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "retrospective_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "retrospective_count": len(operation_data.get("retrospectives", [])),
                    "action_count": len(operation_data.get("actions", [])),
                    "feedback_score": operation_data.get("feedback_score", 0.0)
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("retrospective_operation", trace_data)
            
            logger.info(f"Retrospective operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

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
        except FileNotFoundError:
            logger.info("Retrospective history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing retrospective history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in retrospective history: {e}")
        except OSError as e:
            logger.error(f"OS error loading retrospective history: {e}")
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
        except PermissionError as e:
            logger.error(f"Permission denied saving retrospective history: {e}")
        except OSError as e:
            logger.error(f"OS error saving retrospective history: {e}")
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
        except FileNotFoundError:
            logger.info("Action history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing action history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in action history: {e}")
        except OSError as e:
            logger.error(f"OS error loading action history: {e}")
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
        except PermissionError as e:
            logger.error(f"Permission denied saving action history: {e}")
        except OSError as e:
            logger.error(f"OS error saving action history: {e}")
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
        except FileNotFoundError:
            print(f"Resource file not found: {resource_type}")
        except PermissionError as e:
            print(f"Permission denied accessing resource {resource_type}: {e}")
        except UnicodeDecodeError as e:
            print(f"Unicode decode error in resource {resource_type}: {e}")
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

    async def conduct_retrospective(self, sprint_name: str = "Sprint 15", team_size: int = 8) -> Dict[str, Any]:
        """Conduct retrospective with enhanced functionality met MCP enhancement."""
        # Input validation
        if not isinstance(sprint_name, str):
            raise TypeError("sprint_name must be a string")
        if not isinstance(team_size, int):
            raise TypeError("team_size must be an integer")
        if not sprint_name.strip():
            raise ValueError("sprint_name cannot be empty")
        if team_size <= 0:
            raise ValueError("team_size must be positive")
        if team_size > 50:
            raise ValueError("team_size cannot exceed 50")
            
        logger.info(f"Conducting retrospective for {sprint_name}")

        # Use MCP tools for enhanced retrospective
        retro_data = {
            "sprint_name": sprint_name,
            "team_size": team_size,
            "feedback_list": [
                "Daily standups are working well",
                "Need better documentation",
                "Automation would help",
                "Team collaboration is good"
            ],
            "team_capacity": 100,
            "priority_level": "medium",
            "timeframe": "next_sprint",
            "action_items": [],
            "metrics": {},
            "team_context": {"team_size": team_size, "sprint_name": sprint_name},
            "historical_data": {"previous_retros": len(self.retro_history)}
        }
        
        enhanced_data = await self.use_enhanced_mcp_tools(retro_data)

        # Simulate retrospective process
        time.sleep(2)

        retrospective_result = {
            "sprint_name": sprint_name,
            "team_size": team_size,
            "retrospective_type": "Sprint Retrospective",
            "status": "completed",
            "retrospective_data": {
                "sprint_duration": "2 weeks",
                "participants": team_size,
                "retrospective_format": "Start/Stop/Continue",
                "facilitator": "Scrum Master",
                "duration": "1 hour"
            },
            "feedback_summary": {
                "total_feedback_items": 15,
                "positive_feedback": 8,
                "improvement_suggestions": 5,
                "concerns": 2
            },
            "action_items": [
                {
                    "action": "Implement automated testing",
                    "deadline": "Next sprint",
                    "owner": "DevOps Team",
                    "priority": "high",
                    "success_criteria": "All tests automated and passing"
                },
                {
                    "action": "Create documentation guidelines",
                    "deadline": "2 weeks",
                    "owner": "Documentation Team",
                    "priority": "medium",
                    "success_criteria": "Guidelines published and team trained"
                },
                {
                    "action": "Optimize meeting structure",
                    "deadline": "1 week",
                    "owner": "Scrum Master",
                    "priority": "medium",
                    "success_criteria": "Meetings are shorter and more focused"
                }
            ],
            "improvement_areas": {
                "process_improvements": ["Automation", "Documentation", "Communication"],
                "team_dynamics": ["Knowledge sharing", "Collaboration", "Feedback culture"],
                "technical_debt": ["Test coverage", "Code quality", "Performance"]
            },
            "team_sentiment": {
                "overall_satisfaction": "7.5/10",
                "morale": "Good",
                "engagement": "High",
                "stress_level": "Medium"
            },
            "key_insights": [
                "Team communication has improved significantly",
                "Need for better documentation practices",
                "Automation opportunities identified",
                "Knowledge sharing is working well"
            ],
            "feedback_categories": {
                "continue": [
                    "Daily standups",
                    "Pair programming sessions",
                    "Regular code reviews"
                ],
                "start": [
                    "Implement automated testing in CI/CD pipeline",
                    "Create comprehensive documentation",
                    "Regular knowledge sharing sessions"
                ],
                "stop": [
                    "Long meetings without clear agenda",
                    "Manual testing processes",
                    "Delayed code reviews"
                ]
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Add MCP enhanced data if available
        if enhanced_data:
            retrospective_result["mcp_enhanced_data"] = enhanced_data
            retrospective_result["mcp_enhanced"] = True

        # Add to history
        retro_entry = f"{retrospective_result['timestamp']}: {sprint_name} retrospective completed - Team size: {team_size}"
        self.retro_history.append(retro_entry)
        self._save_retro_history()

        # Record performance metric
        self.monitor._record_metric("RetrospectiveAgent", MetricType.RESPONSE_TIME, 2.0, {"sprint_name": sprint_name, "team_size": team_size})

        logger.info(f"Retrospective completed for {sprint_name}")
        return retrospective_result

    def analyze_feedback(self, feedback_list: List[str] = None) -> Dict[str, Any]:
        """Analyze feedback with enhanced functionality."""
        # Input validation
        if feedback_list is not None and not isinstance(feedback_list, list):
            raise TypeError("feedback_list must be a list")
        if feedback_list is not None:
            for i, feedback in enumerate(feedback_list):
                if not isinstance(feedback, str):
                    raise TypeError(f"feedback_list[{i}] must be a string")
                if not feedback.strip():
                    raise ValueError(f"feedback_list[{i}] cannot be empty")
            
        if feedback_list is None:
            feedback_list = [
                "Great communication during the sprint",
                "Need better documentation practices",
                "Process improvements needed",
                "Team collaboration is excellent",
                "Automation opportunities identified"
            ]

        logger.info("Analyzing feedback data")

        # Simulate feedback analysis
        time.sleep(1)

        analysis_result = {
            "feedback_analysis_type": "Retrospective Feedback Analysis",
            "status": "analyzed",
            "feedback_analysis": {
                "total_feedback_items": len(feedback_list),
                "feedback_categories": {
                    "positive": 3,
                    "improvement": 2,
                    "neutral": 0
                },
                "common_themes": [
                    "Communication",
                    "Documentation",
                    "Process improvement",
                    "Automation"
                ]
            },
            "sentiment_analysis": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.7,
                "positive_sentiments": ["excellent", "great", "improved"],
                "negative_sentiments": ["need", "improvements"],
                "neutral_sentiments": ["identified", "opportunities"]
            },
            "key_themes": {
                "communication": {
                    "frequency": 2,
                    "sentiment": "positive",
                    "priority": "medium"
                },
                "documentation": {
                    "frequency": 1,
                    "sentiment": "negative",
                    "priority": "high"
                },
                "process_improvement": {
                    "frequency": 1,
                    "sentiment": "neutral",
                    "priority": "high"
                },
                "automation": {
                    "frequency": 1,
                    "sentiment": "positive",
                    "priority": "medium"
                }
            },
            "priority_areas": [
                {
                    "area": "Documentation practices",
                    "priority": "high",
                    "impact": "High",
                    "effort": "Medium"
                },
                {
                    "area": "Process improvements",
                    "priority": "high",
                    "impact": "High",
                    "effort": "High"
                },
                {
                    "area": "Automation opportunities",
                    "priority": "medium",
                    "impact": "Medium",
                    "effort": "High"
                }
            ],
            "recommendations": [
                "Implement comprehensive documentation guidelines",
                "Establish process improvement framework",
                "Create automation roadmap",
                "Maintain current communication practices"
            ],
            "actionable_insights": [
                "Documentation is a critical pain point",
                "Process improvements are highly valued",
                "Automation opportunities should be prioritized",
                "Communication practices are working well"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RetrospectiveAgent", MetricType.SUCCESS_RATE, 88, "%")

        logger.info(f"Feedback analysis completed: {analysis_result}")
        return analysis_result

    def create_action_plan(self, retrospective_data: Dict = None) -> Dict[str, Any]:
        """Create action plan from retrospective data with enhanced functionality."""
        # Input validation
        if retrospective_data is not None and not isinstance(retrospective_data, dict):
            raise TypeError("retrospective_data must be a dictionary")
            
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
            "action_items": [
                {
                    "action": "Implement automated testing",
                    "priority": "high",
                    "owner": "DevOps Team",
                    "deadline": "Next sprint"
                },
                {
                    "action": "Create documentation guidelines",
                    "priority": "medium",
                    "owner": "Documentation Team",
                    "deadline": "2 weeks"
                },
                {
                    "action": "Optimize meeting structure",
                    "priority": "medium",
                    "owner": "Scrum Master",
                    "deadline": "1 week"
                }
            ],
            "timeline": {
                "week_1": ["Optimize meeting structure"],
                "week_2": ["Create documentation guidelines"],
                "week_3": ["Enhance knowledge sharing"],
                "week_4": ["Implement automated testing"]
            },
            "responsibilities": {
                "DevOps Team": ["Automated testing implementation"],
                "Documentation Team": ["Guidelines creation"],
                "Scrum Master": ["Meeting optimization"],
                "Team Lead": ["Knowledge sharing enhancement"]
            },
            "success_metrics": {
                "action_completion_rate": "target: 90%",
                "team_satisfaction": "target: 8.0/10",
                "process_efficiency": "target: 20% improvement",
                "quality_metrics": "target: 95% pass rate"
            },
            "follow_up_plan": {
                "review_schedule": "Weekly progress reviews",
                "checkpoints": ["Week 1", "Week 2", "Week 3", "Week 4"],
                "escalation_process": "Contact team lead if actions are blocked",
                "success_celebration": "Team recognition for completed actions"
            },
            "implementation_timeline": {
                "week_1": ["Optimize meeting structure"],
                "week_2": ["Create documentation guidelines"],
                "week_3": ["Enhance knowledge sharing"],
                "week_4": ["Implement automated testing"]
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
        self.monitor._record_metric("RetrospectiveAgent", MetricType.SUCCESS_RATE, 90, "%")

        logger.info(f"Action plan created: {action_plan_result}")
        return action_plan_result

    def track_improvements(self, sprint_name: str = "Sprint 15") -> Dict[str, Any]:
        """Track improvements with enhanced functionality."""
        # Input validation
        if not isinstance(sprint_name, str):
            raise TypeError("sprint_name must be a string")
        if not sprint_name.strip():
            raise ValueError("sprint_name cannot be empty")
            
        logger.info(f"Tracking improvements for {sprint_name}")

        # Simulate improvement tracking
        time.sleep(1)

        tracking_result = {
            "sprint_name": sprint_name,
            "tracking_type": "Sprint Improvement Tracking",
            "status": "tracked",
            "improvement_metrics": {
                "action_completion_rate": "85%",
                "team_satisfaction": "8.2/10",
                "process_efficiency": "15% improvement",
                "quality_metrics": "92% pass rate"
            },
            "progress_tracking": {
                "completed_actions": 3,
                "in_progress_actions": 2,
                "blocked_actions": 1,
                "total_actions": 6
            },
            "success_stories": [
                {
                    "action": "Optimize meeting structure",
                    "impact": "Meetings reduced by 30%",
                    "team_feedback": "Very positive",
                    "lessons_learned": "Clear agenda is crucial"
                },
                {
                    "action": "Improve documentation",
                    "impact": "Knowledge sharing improved",
                    "team_feedback": "Helpful for onboarding",
                    "lessons_learned": "Regular updates are important"
                }
            ],
            "challenges": [
                {
                    "challenge": "Resource constraints for automation",
                    "impact": "Delayed implementation",
                    "mitigation": "Secured additional budget",
                    "status": "Resolved"
                },
                {
                    "challenge": "Team resistance to changes",
                    "impact": "Slower adoption",
                    "mitigation": "Training and support provided",
                    "status": "In progress"
                }
            ],
            "next_steps": [
                "Continue monitoring action completion",
                "Address remaining blocked actions",
                "Plan next sprint improvements",
                "Share success stories with team"
            ],
            "trends_analysis": {
                "improvement_trend": "Positive",
                "team_engagement": "Increasing",
                "process_maturity": "Improving",
                "quality_metrics": "Stable"
            },
            "recommendations": [
                "Maintain current improvement momentum",
                "Focus on resolving blocked actions",
                "Celebrate team successes",
                "Plan for next sprint improvements"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "RetrospectiveAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("RetrospectiveAgent", MetricType.SUCCESS_RATE, 85, "%")

        logger.info(f"Improvement tracking completed: {tracking_result}")
        return tracking_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export retrospective report in specified format."""
        # Input validation
        if not isinstance(format_type, str):
            raise TypeError("format_type must be a string")
        if format_type not in ["md", "csv", "json"]:
            raise ValueError("format_type must be one of: md, csv, json")
        if report_data is not None and not isinstance(report_data, dict):
            raise TypeError("report_data must be a dictionary")
            
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
        except PermissionError as e:
            logger.error(f"Permission denied exporting report: {e}")
        except OSError as e:
            logger.error(f"OS error exporting report: {e}")
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

        try:
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
        output_file = f"retrospective_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Sprint Name", report_data.get("sprint_name", "N/A")])
                writer.writerow(["Status", report_data.get("status", "N/A")])
                writer.writerow(["Total Actions", report_data.get("total_actions", 0)])
                writer.writerow(["Completion Rate", report_data.get("completion_rate", "N/A")])
                writer.writerow(["Team Satisfaction", report_data.get("team_satisfaction", "N/A")])

            print(f"Report export saved to: {output_file}")
        except PermissionError as e:
            logger.error(f"Permission denied saving CSV report: {e}")
        except OSError as e:
            logger.error(f"OS error saving CSV report: {e}")
        except Exception as e:
            logger.error(f"Error saving CSV report: {e}")

    def _export_json(self, report_data: Dict):
        """Export report data as JSON."""
        output_file = f"retrospective_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
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
        save_context("Retrospective", "status", {"retrospective_status": "completed"})

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
        try:
            if not isinstance(event, dict):
                logger.error("Invalid event format: event must be a dictionary")
                return
            logger.info(f"Retro feedback event received: {event}")
            feedback_list = event.get("feedback_list", [])
            if not isinstance(feedback_list, list):
                logger.error("Invalid feedback_list format: must be a list")
                return
            self.summarize_retro(feedback_list)
        except Exception as e:
            logger.error(f"Error handling retro feedback event: {e}")

    def on_generate_actions(self, event):
        """Handle generate actions event from other agents."""
        try:
            if not isinstance(event, dict):
                logger.error("Invalid event format: event must be a dictionary")
                return
            logger.info(f"Generate actions event received: {event}")
            feedback_list = event.get("feedback_list", [])
            if not isinstance(feedback_list, list):
                logger.error("Invalid feedback_list format: must be a list")
                return
            self.generate_retro_actions(feedback_list)
        except Exception as e:
            logger.error(f"Error handling generate actions event: {e}")

    def on_feedback_sentiment_analyzed(self, event):
        """Handle feedback sentiment analysis from other agents."""
        try:
            if not isinstance(event, dict):
                logger.error("Invalid event format: event must be a dictionary")
                return
            sentiment = event.get("sentiment", "")
            motivatie = event.get("motivatie", "")
            feedback = event.get("feedback", "")
            if sentiment == "negatief":
                prompt = f"Bedenk 2 concrete verbeteracties op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen de acties als JSON."
                structured_output = '{"verbeteracties": ["actie 1", "actie 2"]}'
                result = ask_openai(prompt, structured_output=structured_output)
                logger.info(f"[Retrospective][LLM Verbeteracties]: {result}")
        except Exception as e:
            logger.error(f"Error handling feedback sentiment analyzed event: {e}")

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        await self.initialize_enhanced_mcp()
        await self.initialize_tracing()
        
        print("🔄 Retrospective is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        subscribe("retro_feedback", self.on_retro_feedback)
        subscribe("generate_actions", self.on_generate_actions)
        subscribe("feedback_sentiment_analyzed", self.on_feedback_sentiment_analyzed)

        logger.info("RetrospectiveAgent ready and listening for events...")
        print("Listening for events: retro_feedback, generate_actions, feedback_sentiment_analyzed")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Retrospective Agent stopped.")
    
    async def run_async(self):
        """Run the agent with enhanced MCP and tracing initialization."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        print("🔄 Retrospective is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        
        logger.info("RetrospectiveAgent ready and listening for events...")
        await self.collaborate_example()
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the Retrospective agent met MCP integration."""
        agent = cls()
        await agent.run()
    
    @classmethod
    async def run_agent_async(cls):
        """Class method to run the Retrospective agent with enhanced MCP."""
        agent = cls()
        await agent.run_async()

def main():
    parser = argparse.ArgumentParser(description="Retrospective Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "conduct-retrospective", "analyze-feedback", "create-action-plan",
                               "track-improvements", "show-retro-history", "show-action-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run", "enhanced-collaborate", "enhanced-security", 
                               "enhanced-performance", "trace-operation", "trace-performance", 
                               "trace-error", "tracing-summary"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--sprint-name", default="Sprint 15", help="Sprint name for retrospective")
    parser.add_argument("--team-size", type=int, default=8, help="Team size for retrospective")
    parser.add_argument("--feedback-list", nargs="+", help="List of feedback items to analyze")

    args = parser.parse_args()

    agent = RetrospectiveAgent()

    if args.command == "help":
        agent.show_help()
    elif args.command == "conduct-retrospective":
        result = asyncio.run(agent.conduct_retrospective(args.sprint_name, args.team_size))
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
        asyncio.run(agent.run())
    # Enhanced MCP Phase 2 Commands
    elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                         "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
        # Enhanced MCP commands
        if args.command == "enhanced-collaborate":
            result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                ["Scrummaster", "ProductOwner", "QualityGuardian", "FeedbackAgent"], 
                {"type": "retrospective_review", "content": {"review_type": "retrospective_analysis"}}
            ))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-security":
            result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                "retrospective_data": {"retrospectives": [], "actions": [], "feedback": []},
                "security_requirements": ["feedback_validation", "action_tracking", "improvement_safety"]
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "enhanced-performance":
            result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                "retrospective_data": {"retrospectives": [], "actions": [], "feedback": []},
                "performance_metrics": {"feedback_analysis_speed": 85.5, "action_generation_accuracy": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-operation":
            result = asyncio.run(agent.trace_retrospective_operation({
                "operation_type": "retrospective_analysis",
                "sprint_name": args.sprint_name,
                "retrospectives": list(agent.retro_history)
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-performance":
            result = asyncio.run(agent.trace_retrospective_operation({
                "operation_type": "performance_analysis",
                "performance_metrics": {"feedback_analysis_speed": 85.5, "action_generation_accuracy": 92.3}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "trace-error":
            result = asyncio.run(agent.trace_retrospective_operation({
                "operation_type": "error_analysis",
                "error_data": {"error_type": "retrospective_failure", "error_message": "Retrospective analysis failed"}
            }))
            print(json.dumps(result, indent=2))
        elif args.command == "tracing-summary":
            print("Tracing Summary for Retrospective:")
            print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
            print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
            print(f"Agent: {agent.agent_name}")
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)

if __name__ == "__main__":
    main()
