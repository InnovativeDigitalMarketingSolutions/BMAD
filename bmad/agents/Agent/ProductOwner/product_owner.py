#!/usr/bin/env python3
"""
Product Owner Agent voor BMAD
"""
import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from dotenv import load_dotenv

from bmad.agents.core.ai.confidence_scoring import (
    confidence_scoring,
    create_review_request,
    format_confidence_message,
)
from bmad.agents.core.ai.llm_client import ask_openai_with_confidence
from bmad.core.message_bus import AgentMessageBusIntegration, EventTypes, get_message_bus
from bmad.agents.core.data.supabase_context import get_context, save_context
from bmad.projects.project_manager import project_manager
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


load_dotenv()


class ProductOwnerAgent(AgentMessageBusIntegration):
    """
    Product Owner Agent voor BMAD.
    Gespecialiseerd in product management, user stories, en product vision.
    """
    
    def __init__(self):
        super().__init__("ProductOwner")
        self.framework_manager = get_framework_templates_manager()
        try:
            self.product_owner_template = self.framework_manager.get_framework_template('product_owner')
        except:
            self.product_owner_template = None
        self.lessons_learned = []

        """Initialize ProductOwner agent met MCP integration."""
        self.agent_name = "ProductOwnerAgent"
        self.story_history = []
        self.vision_history = []
        
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
        
        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/productowner/best-practices.md",
            "user-story-template": self.resource_base / "templates/productowner/user-story-template.md",
            "vision-template": self.resource_base / "templates/productowner/vision-template.md",
            "backlog-template": self.resource_base / "templates/productowner/backlog-template.md",
            "roadmap-template": self.resource_base / "templates/productowner/roadmap-template.md",
            "acceptance-criteria": self.resource_base / "templates/productowner/acceptance-criteria.md",
            "stakeholder-analysis": self.resource_base / "templates/productowner/stakeholder-analysis.md"
        }
        self.data_paths = {
            "story-history": self.resource_base / "data/productowner/story-history.md",
            "vision-history": self.resource_base / "data/productowner/vision-history.md",
            "backlog": self.resource_base / "data/productowner/backlog.md"
        }
        
        self._load_story_history()
        self._load_vision_history()
        
        logging.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")

    async def initialize_message_bus(self):
        """Initialize message bus integration for ProductOwner agent."""
        try:
            # Subscribe to relevant event categories
            await self.subscribe_to_event_category("product_management")
            await self.subscribe_to_event_category("user_stories")
            await self.subscribe_to_event_category("backlog")
            await self.subscribe_to_event_category("feedback")
            await self.subscribe_to_event_category("collaboration")
            
            # Register specific event handlers
            await self.register_event_handler(EventTypes.USER_STORY_REQUESTED, self._handle_user_story_requested)
            await self.register_event_handler(EventTypes.BACKLOG_UPDATE_REQUESTED, self._handle_backlog_update_requested)
            await self.register_event_handler(EventTypes.PRODUCT_VISION_REQUESTED, self._handle_product_vision_requested)
            await self.register_event_handler(EventTypes.STAKEHOLDER_ANALYSIS_REQUESTED, self._handle_stakeholder_analysis_requested)
            await self.register_event_handler(EventTypes.FEEDBACK_RECEIVED, self._handle_feedback_received)
            await self.register_event_handler(EventTypes.TASK_DELEGATED, self._handle_task_delegated)
            
            logging.info("ProductOwner agent message bus integration initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize message bus integration: {e}")
            return False

    async def _handle_user_story_requested(self, event_data: Dict[str, Any]):
        """Handle user story requested event."""
        try:
            requirement = event_data.get('requirement', 'Default requirement')
            user_type = event_data.get('user_type', 'end_user')
            priority = event_data.get('priority', 'medium')
            
            logging.info(f"Processing user story request: {requirement}")
            
            # Create user story
            story_result = await self.create_user_story({
                "title": f"User Story for {requirement}",
                "description": requirement,
                "priority": priority,
                "user_type": user_type
            })
            
            if story_result.get("success"):
                await self.publish_agent_event(EventTypes.USER_STORY_CREATED, {
                    "requirement": requirement,
                    "story": story_result.get("story"),
                    "status": "success"
                })
            else:
                await self.publish_agent_event(EventTypes.USER_STORY_CREATION_FAILED, {
                    "requirement": requirement,
                    "error": story_result.get("error"),
                    "status": "failed"
                })
                
        except Exception as e:
            logging.error(f"Error handling user story requested event: {e}")
            await self.publish_agent_event(EventTypes.USER_STORY_CREATION_FAILED, {
                "error": str(e),
                "status": "failed"
            })

    async def _handle_backlog_update_requested(self, event_data: Dict[str, Any]):
        """Handle backlog update requested event."""
        try:
            backlog_items = event_data.get('backlog_items', [])
            prioritization_method = event_data.get('prioritization_method', 'value_effort')
            
            logging.info(f"Processing backlog update request with {len(backlog_items)} items")
            
            # Process backlog update
            # This would typically involve reordering, reprioritizing, or adding new items
            updated_backlog = await self._process_backlog_update(backlog_items, prioritization_method)
            
            await self.publish_agent_event(EventTypes.BACKLOG_UPDATED, {
                "backlog_items": updated_backlog,
                "prioritization_method": prioritization_method,
                "status": "success"
            })
            
        except Exception as e:
            logging.error(f"Error handling backlog update requested event: {e}")
            await self.publish_agent_event(EventTypes.BACKLOG_UPDATE_FAILED, {
                "error": str(e),
                "status": "failed"
            })

    async def _handle_product_vision_requested(self, event_data: Dict[str, Any]):
        """Handle product vision requested event."""
        try:
            product_name = event_data.get('product_name', 'Unknown Product')
            vision_type = event_data.get('vision_type', 'strategic')
            timeframe = event_data.get('timeframe', 'long_term')
            
            logging.info(f"Processing product vision request for {product_name}")
            
            # Generate product vision
            vision_result = await self._generate_product_vision(product_name, vision_type, timeframe)
            
            await self.publish_agent_event(EventTypes.PRODUCT_VISION_CREATED, {
                "product_name": product_name,
                "vision": vision_result,
                "vision_type": vision_type,
                "timeframe": timeframe,
                "status": "success"
            })
            
        except Exception as e:
            logging.error(f"Error handling product vision requested event: {e}")
            await self.publish_agent_event(EventTypes.PRODUCT_VISION_CREATION_FAILED, {
                "error": str(e),
                "status": "failed"
            })

    async def _handle_stakeholder_analysis_requested(self, event_data: Dict[str, Any]):
        """Handle stakeholder analysis requested event."""
        try:
            stakeholders = event_data.get('stakeholders', [])
            analysis_type = event_data.get('analysis_type', 'comprehensive')
            
            logging.info(f"Processing stakeholder analysis request for {len(stakeholders)} stakeholders")
            
            # Perform stakeholder analysis
            analysis_result = await self._perform_stakeholder_analysis(stakeholders, analysis_type)
            
            await self.publish_agent_event(EventTypes.STAKEHOLDER_ANALYSIS_COMPLETED, {
                "stakeholders": stakeholders,
                "analysis": analysis_result,
                "analysis_type": analysis_type,
                "status": "success"
            })
            
        except Exception as e:
            logging.error(f"Error handling stakeholder analysis requested event: {e}")
            await self.publish_agent_event(EventTypes.STAKEHOLDER_ANALYSIS_FAILED, {
                "error": str(e),
                "status": "failed"
            })

    async def _handle_feedback_received(self, event_data: Dict[str, Any]):
        """Handle feedback received event."""
        try:
            feedback = event_data.get('feedback', '')
            source = event_data.get('source', 'unknown')
            sentiment = event_data.get('sentiment', 'neutral')
            
            logging.info(f"Processing feedback from {source} with sentiment: {sentiment}")
            
            # Process feedback and determine actions
            actions = await self._process_feedback(feedback, source, sentiment)
            
            await self.publish_agent_event(EventTypes.FEEDBACK_PROCESSED, {
                "feedback": feedback,
                "source": source,
                "sentiment": sentiment,
                "actions": actions,
                "status": "success"
            })
            
        except Exception as e:
            logging.error(f"Error handling feedback received event: {e}")
            await self.publish_agent_event(EventTypes.FEEDBACK_PROCESSING_FAILED, {
                "error": str(e),
                "status": "failed"
            })

    async def _handle_task_delegated(self, event_data: Dict[str, Any]):
        """Handle task delegated event."""
        try:
            task = event_data.get('task', {})
            task_id = task.get('id', 'unknown')
            task_type = task.get('type', 'unknown')
            
            logging.info(f"Processing delegated task {task_id} of type {task_type}")
            
            # Accept and process the delegated task
            result = await self._process_delegated_task(task)
            
            await self.publish_agent_event(EventTypes.TASK_COMPLETED, {
                "task_id": task_id,
                "task_type": task_type,
                "result": result,
                "status": "completed"
            })
            
        except Exception as e:
            logging.error(f"Error handling task delegated event: {e}")
            await self.publish_agent_event(EventTypes.TASK_FAILED, {
                "task_id": task.get('id', 'unknown'),
                "error": str(e),
                "status": "failed"
            })

    async def _process_backlog_update(self, backlog_items: list, prioritization_method: str) -> list:
        """Process backlog update with prioritization."""
        # This is a placeholder implementation
        # In a real scenario, this would involve complex prioritization logic
        return sorted(backlog_items, key=lambda x: x.get('priority', 'medium'))

    async def _generate_product_vision(self, product_name: str, vision_type: str, timeframe: str) -> Dict[str, Any]:
        """Generate product vision."""
        # This is a placeholder implementation
        return {
            "product_name": product_name,
            "vision_type": vision_type,
            "timeframe": timeframe,
            "vision_statement": f"To create the best {product_name} experience for our users",
            "key_objectives": ["User satisfaction", "Market leadership", "Innovation"],
            "success_metrics": ["User adoption", "Customer satisfaction", "Revenue growth"]
        }

    async def _perform_stakeholder_analysis(self, stakeholders: list, analysis_type: str) -> Dict[str, Any]:
        """Perform stakeholder analysis."""
        # This is a placeholder implementation
        return {
            "stakeholders": stakeholders,
            "analysis_type": analysis_type,
            "engagement_levels": {s: "high" for s in stakeholders},
            "communication_preferences": {s: "email" for s in stakeholders},
            "influence_levels": {s: "medium" for s in stakeholders}
        }

    async def _process_feedback(self, feedback: str, source: str, sentiment: str) -> list:
        """Process feedback and determine actions."""
        actions = []
        
        if sentiment == "negative":
            actions.append("Prioritize improvements")
            actions.append("Schedule stakeholder meeting")
        elif sentiment == "positive":
            actions.append("Continue current direction")
            actions.append("Share success with team")
        else:
            actions.append("Monitor for trends")
        
        return actions

    async def _process_delegated_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a delegated task."""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'create_user_story':
            return await self.create_user_story(task.get('data', {}))
        elif task_type == 'update_backlog':
            return await self._process_backlog_update(task.get('data', {}).get('items', []), 'value_effort')
        elif task_type == 'generate_vision':
            data = task.get('data', {})
            return await self._generate_product_vision(data.get('product_name', ''), data.get('vision_type', 'strategic'), data.get('timeframe', 'long_term'))
        else:
            return {"status": "unknown_task_type", "error": f"Unknown task type: {task_type}"}

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
            self.enhanced_mcp_client = self.enhanced_mcp.mcp_client if self.enhanced_mcp else None
            self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            if self.enhanced_mcp_enabled:
                logging.info("Enhanced MCP capabilities initialized successfully")
            else:
                logging.warning("Enhanced MCP initialization failed, falling back to standard MCP")
        except Exception as e:
            logging.warning(f"Enhanced MCP initialization failed: {e}")
            self.enhanced_mcp_enabled = False
    
    async def initialize_tracing(self):
        """Initialize tracing capabilities."""
        try:
            self.tracer = BMADTracer(config=type("Config", (), {
                "service_name": f"{self.agent_name}",
                "environment": "development",
                "tracing_level": "detailed"
            })())
            self.tracing_enabled = await self.tracer.initialize()
            
            if self.tracing_enabled:
                logging.info("Tracing capabilities initialized successfully")
                await self.tracer.setup_agent_specific_tracing({
                    "agent_name": self.agent_name,
                    "tracing_level": "detailed",
                    "performance_tracking": True,
                    "error_tracking": True
                })
        except Exception as e:
            logging.warning(f"Tracing initialization failed: {e}")
            self.tracing_enabled = False

    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use MCP tool voor enhanced functionality."""
        if not self.mcp_enabled or not self.mcp_client:
            logging.warning("MCP not available, using local tools")
            return None
        
        try:
            # Create a context for the tool call
            context = await self.mcp_client.create_context(agent_id=self.agent_name)
            response = await self.mcp_client.call_tool(tool_name, parameters, context)
            
            if response.success:
                result = response.data
            else:
                logger.error(f"MCP tool {tool_name} failed: {response.error}")
                result = None
            logging.info(f"MCP tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logging.error(f"MCP tool {tool_name} execution failed: {e}")
            return None

    async def use_product_specific_mcp_tools(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use product-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # User story creation
        story_result = await self.use_mcp_tool("user_story_creation", {
            "requirement": product_data.get("requirement", ""),
            "user_type": product_data.get("user_type", "end_user"),
            "story_type": product_data.get("story_type", "feature"),
            "priority": product_data.get("priority", "medium"),
            "acceptance_criteria": product_data.get("acceptance_criteria", True)
        })
        if story_result:
            enhanced_data["user_story_creation"] = story_result
        
        # Product vision
        vision_result = await self.use_mcp_tool("product_vision", {
            "product_name": product_data.get("product_name", ""),
            "vision_type": product_data.get("vision_type", "strategic"),
            "timeframe": product_data.get("timeframe", "long_term"),
            "stakeholders": product_data.get("stakeholders", [])
        })
        if vision_result:
            enhanced_data["product_vision"] = vision_result
        
        # Backlog management
        backlog_result = await self.use_mcp_tool("backlog_management", {
            "backlog_items": product_data.get("backlog_items", []),
            "prioritization_method": product_data.get("prioritization_method", "value_effort"),
            "sprint_planning": product_data.get("sprint_planning", True),
            "refinement": product_data.get("refinement", True)
        })
        if backlog_result:
            enhanced_data["backlog_management"] = backlog_result
        
        # Stakeholder analysis
        stakeholder_result = await self.use_mcp_tool("stakeholder_analysis", {
            "stakeholders": product_data.get("stakeholders", []),
            "analysis_type": product_data.get("analysis_type", "comprehensive"),
            "engagement_strategy": product_data.get("engagement_strategy", True),
            "communication_plan": product_data.get("communication_plan", True)
        })
        if stakeholder_result:
            enhanced_data["stakeholder_analysis"] = stakeholder_result
        
        return enhanced_data
    
    async def use_enhanced_mcp_tools(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logging.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_product_specific_mcp_tools(product_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": product_data.get("capabilities", []),
                "performance_metrics": product_data.get("performance_metrics", {})
            })
            if core_result:
                enhanced_data["core_enhancement"] = core_result
            
            # Product-specific enhancement tools
            specific_result = await self.use_product_specific_enhanced_tools(product_data)
            if specific_result:
                enhanced_data.update(specific_result)
            
        except Exception as e:
            logging.error(f"Error in enhanced MCP tools: {e}")
        
        return enhanced_data
    
    async def use_product_specific_enhanced_tools(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use product-specific enhanced MCP tools."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {}
        
        enhanced_data = {}
        
        try:
            # Enhanced user story creation
            enhanced_story_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_user_story_creation", {
                "requirement": product_data.get("requirement", ""),
                "enhancement_level": "advanced",
                "stakeholder_analysis": product_data.get("stakeholder_analysis", True),
                "market_research": product_data.get("market_research", True)
            })
            if enhanced_story_result:
                enhanced_data["enhanced_user_story_creation"] = enhanced_story_result
            
            # Enhanced product vision
            enhanced_vision_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_product_vision", {
                "product_name": product_data.get("product_name", ""),
                "enhancement_level": "advanced",
                "competitive_analysis": product_data.get("competitive_analysis", True),
                "trend_analysis": product_data.get("trend_analysis", True)
            })
            if enhanced_vision_result:
                enhanced_data["enhanced_product_vision"] = enhanced_vision_result
            
            # Enhanced performance optimization
            enhanced_performance_result = await self.enhanced_mcp.enhanced_performance_optimization({
                "agent_type": "product_owner",
                "product_data": product_data,
                "optimization_targets": ["story_quality", "vision_clarity", "stakeholder_satisfaction"]
            })
            if enhanced_performance_result:
                enhanced_data["enhanced_performance_optimization"] = enhanced_performance_result
            
        except Exception as e:
            logging.error(f"Error in product-specific enhanced tools: {e}")
        
        return enhanced_data
    
    async def trace_product_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace product-specific operations."""
        if not self.tracing_enabled or not self.tracer:
            return {}
        
        try:
            trace_result = await self.tracer.trace_agent_operation({
                "operation_type": operation_data.get("type", "story_creation"),
                "agent_name": self.agent_name,
                "performance_metrics": operation_data.get("performance_metrics", {}),
                "timestamp": datetime.now().isoformat()
            })
            return trace_result
        except Exception as e:
            logging.error(f"Product operation tracing failed: {e}")
            return {}

    def show_help(self):
        print("""
🎯 ProductOwner Agent - Beschikbare commando's:

  create-story [--input "requirement"]  - Maak een user story
  show-vision                           - Toon BMAD visie
  help                                  - Toon deze help

Voorbeelden:
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story --input "Dashboard voor agent monitoring"
""")

    async def create_user_story(self, story_data: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """Create a user story based on story data with MCP enhancement."""
        try:
            # Initialize enhanced MCP if not already done
            if not self.enhanced_mcp_enabled:
                await self.initialize_enhanced_mcp()
            
            # Handle both string and dictionary input
            if isinstance(story_data, str):
                # Convert string to dictionary format
                story_data = {
                    "title": "User Story",
                    "description": story_data,
                    "priority": "medium"
                }
            
            # Extract story data
            title = story_data.get("title", "Untitled Story")
            description = story_data.get("description", "")
            priority = story_data.get("priority", "medium")
            
            # Use enhanced MCP tools if available
            if self.enhanced_mcp_enabled and self.enhanced_mcp:
                result = await self.use_enhanced_mcp_tools({
                    "operation": "create_user_story",
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "acceptance_criteria": True,
                    "story_type": "feature",
                    "capabilities": ["story_creation", "acceptance_criteria", "story_prioritization"]
                })
                if result:
                    return result
            
            # Fallback to local implementation
            return await asyncio.to_thread(self._create_user_story_sync, story_data)
            
        except Exception as e:
            logging.error(f"Error in create_user_story: {e}")
            return {
                "success": False,
                "error": str(e),
                "story": None
            }

    def _create_user_story_sync(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous fallback for create_user_story."""
        try:
            title = story_data.get("title", "Untitled Story")
            description = story_data.get("description", "")
            priority = story_data.get("priority", "medium")
            
            # Create user story using existing function
            story_content = create_user_story(description)
            
            return {
                "success": True,
                "story": {
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "content": story_content,
                    "acceptance_criteria": [
                        f"User can {description.lower()}",
                        f"System responds appropriately",
                        f"Error handling is in place"
                    ],
                    "story_points": 3,
                    "timestamp": datetime.now().isoformat()
                },
                "status": "completed"
            }
            
        except Exception as e:
            logging.error(f"Error in _create_user_story_sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "story": None
            }

    def show_vision(self):
        """Show the BMAD vision."""
        return show_bmad_vision()

    def _load_story_history(self):
        """Load story history from file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "story-history.md")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse stories from markdown
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('- ') and 'Story:' in line:
                            self.story_history.append(line.strip())
        except FileNotFoundError:
            logging.info("Story history file not found, starting with empty history")
        except PermissionError as e:
            logging.error(f"Permission denied accessing story history: {e}")
        except UnicodeDecodeError as e:
            logging.error(f"Unicode decode error in story history: {e}")
        except OSError as e:
            logging.error(f"OS error loading story history: {e}")
        except Exception as e:
            logging.warning(f"Could not load story history: {e}")

    def _save_story_history(self):
        """Save story history to file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "story-history.md")
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("# Story History\n\n")
                for story in self.story_history:
                    f.write(f"{story}\n")
        except PermissionError as e:
            logging.error(f"Permission denied saving story history: {e}")
        except OSError as e:
            logging.error(f"OS error saving story history: {e}")
        except Exception as e:
            logging.error(f"Could not save story history: {e}")

    def _load_vision_history(self):
        """Load vision history from file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "vision-history.md")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse vision entries from markdown
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('- ') and 'Vision:' in line:
                            self.vision_history.append(line.strip())
        except FileNotFoundError:
            logging.info("Vision history file not found, starting with empty history")
        except PermissionError as e:
            logging.error(f"Permission denied accessing vision history: {e}")
        except UnicodeDecodeError as e:
            logging.error(f"Unicode decode error in vision history: {e}")
        except OSError as e:
            logging.error(f"OS error loading vision history: {e}")
        except Exception as e:
            logging.warning(f"Could not load vision history: {e}")

    def _save_vision_history(self):
        """Save vision history to file."""
        try:
            history_file = os.path.join(os.path.dirname(__file__), "vision-history.md")
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                f.write("# Vision History\n\n")
                for vision in self.vision_history:
                    f.write(f"{vision}\n")
        except PermissionError as e:
            logging.error(f"Permission denied saving vision history: {e}")
        except OSError as e:
            logging.error(f"OS error saving vision history: {e}")
        except Exception as e:
            logging.error(f"Could not save vision history: {e}")

    def show_resource(self, resource_type="best_practices"):
        """Display available resources."""
        # Input validation
        if not isinstance(resource_type, str):
            print("Error: resource_type must be a string")
            return
        
        if not resource_type.strip():
            print("Error: resource_type cannot be empty")
            return
        
        try:
            resource_file = os.path.join(os.path.dirname(__file__), f"{resource_type}.md")
            if os.path.exists(resource_file):
                with open(resource_file, 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print(f"Resource '{resource_type}' not found. Available: best_practices, templates")
        except FileNotFoundError:
            print(f"Resource file not found: {resource_type}")
        except PermissionError as e:
            print(f"Permission denied accessing resource {resource_type}: {e}")
        except UnicodeDecodeError as e:
            print(f"Unicode decode error in resource {resource_type}: {e}")
        except Exception as e:
            logging.error(f"Error reading resource {resource_type}: {e}")

    def show_story_history(self):
        """Display story history."""
        if self.story_history:
            print("📚 Story History:")
            for i, story in enumerate(self.story_history, 1):
                print(f"{i}. {story}")
        else:
            print("No story history available.")

    def show_vision_history(self):
        """Display vision history."""
        if self.vision_history:
            print("👁️ Vision History:")
            for i, vision in enumerate(self.vision_history, 1):
                print(f"{i}. {vision}")
        else:
            print("No vision history available.")

    def export_report(self, format_type, data):
        """Export reports in various formats."""
        # Input validation
        if not isinstance(format_type, str):
            raise TypeError("format_type must be a string")
        
        if format_type not in ["md", "json"]:
            raise ValueError("format_type must be one of: md, json")
        
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"productowner_report_{timestamp}"
        
        try:
            if format_type == "md":
                filename += ".md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("# Product Owner Report\n\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Data: {data}\n")
            elif format_type == "json":
                filename += ".json"
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                print(f"Unsupported format: {format_type}")
                return
            
            print(f"Report export saved to: {filename}")
        except PermissionError as e:
            logging.error(f"Permission denied saving report: {e}")
        except OSError as e:
            logging.error(f"OS error saving report: {e}")
        except Exception as e:
            logging.error(f"Error saving report: {e}")

    async def run(self):
        """Main event loop for the agent met complete integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize message bus integration
        await self.initialize_message_bus()
        
        print("🎯 ProductOwner Agent is running...")
        print("Listening for events: user_story_requested, backlog_update_requested, product_vision_requested")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 ProductOwner Agent stopped.")

    async def run_async(self):
        """Async version of run method."""
        await self.run()

    async def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        try:
            await self.publish_agent_event(EventTypes.BACKLOG_UPDATED, {"status": "success", "agent": "ProductOwner"})
            save_context("ProductOwner", "status", {"backlog_status": "updated"})
            print("Event gepubliceerd en context opgeslagen.")
            context = get_context("ProductOwner")
            print(f"Opgehaalde context: {context}")
        except Exception as e:
            logging.error(f"Collaboration example failed: {e}")
            print(f"❌ Error in collaboration: {e}")
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the ProductOwner agent met MCP integration."""
        agent = cls()
        await agent.initialize_mcp()
        print("ProductOwner agent started with MCP integration")


def main():
    parser = argparse.ArgumentParser(description="Product Owner Agent")
    parser.add_argument(
        "command", nargs="?", default="help", help="Commando voor de agent"
    )
    parser.add_argument("--input", "-i", help="Input voor het commando")
    args = parser.parse_args()

    if args.command == "help":
        show_help()
    elif args.command == "create-story":
        if args.input:
            asyncio.run(create_user_story(args.input))
        else:
            asyncio.run(create_bmad_frontend_story())
    elif args.command == "show-vision":
        show_bmad_vision()
    elif args.command == "collaborate":
        asyncio.run(collaborate_example())
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)
        return

def show_help():
    print("""
🎯 ProductOwner Agent - Beschikbare commando's:

  create-story [--input "requirement"]  - Maak een user story
  show-vision                           - Toon BMAD visie
  help                                  - Toon deze help

Voorbeelden:
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story
  python -m bmad.agents.Agent.ProductOwner.product_owner create-story --input "Dashboard voor agent monitoring"
""")

async def create_bmad_frontend_story():
    """Maak user stories voor het huidige project."""
    # Haal project context op
    project_context = project_manager.get_project_context()

    if not project_context:
        print("❌ Geen project geladen! Laad eerst een project met:")
        print("   python -m bmad.projects.cli load <project_name>")
        return

    project_name = project_context["project_name"]
    project_type = project_context["config"]["project_type"]
    requirements = project_context["requirements"]

    print(f"🎯 ProductOwner - User Stories voor '{project_name}' ({project_type})")
    print("=" * 60)

    # Toon huidige requirements
    if requirements:
        print("📋 Huidige Requirements:")
        for category, reqs in requirements.items():
            if reqs:
                print(f"  {category}:")
                for req in reqs:
                    print(f"    - {req['description']}")
        print()

    # Vraag gebruiker om input
    print("🤔 Wat wil je dat ik doe?")
    print("1. Genereer user stories voor alle requirements")
    print("2. Genereer user stories voor specifieke categorie")
    print("3. Genereer user stories voor nieuwe feature")
    print("4. Review en verbeter bestaande user stories")

    choice = input("\nKies een optie (1-4) of beschrijf je eigen opdracht: ").strip()

    if choice == "1":
        # Genereer user stories voor alle requirements
        all_requirements = []
        for category, reqs in requirements.items():
            for req in reqs:
                all_requirements.append(f"{category}: {req['description']}")

        requirements_text = "\n".join(all_requirements) if all_requirements else "Geen requirements gedefinieerd"

        prompt = f"""
        Schrijf gedetailleerde user stories in Gherkin-formaat voor het project '{project_name}' ({project_type}).
        
        Requirements:
        {requirements_text}
        
        Geef voor elke requirement een user story met acceptatiecriteria.
        Focus op functionaliteit die de gebruiker nodig heeft.
        """

    elif choice == "2":
        category = input("Welke categorie? (functional/non_functional/technical): ").strip()
        reqs = requirements.get(category, [])
        if reqs:
            requirements_text = "\n".join([req["description"] for req in reqs])
            prompt = f"""
            Schrijf user stories voor de {category} requirements van project '{project_name}':
            
            {requirements_text}
            
            Geef voor elke requirement een user story met acceptatiecriteria.
            """
        else:
            print(f"❌ Geen requirements gevonden in categorie '{category}'")
            return

    elif choice == "3":
        feature = input("Beschrijf de nieuwe feature: ").strip()
        prompt = f"""
        Schrijf user stories voor de nieuwe feature van project '{project_name}':
        
        Feature: {feature}
        
        Geef 3-5 user stories met acceptatiecriteria voor deze feature.
        """

    elif choice == "4":
        # Review bestaande user stories
        existing_stories = project_context.get("user_stories", [])
        if existing_stories:
            stories_text = "\n".join([f"{s['id']}. {s['story']}" for s in existing_stories])
            prompt = f"""
            Review en verbeter de bestaande user stories voor project '{project_name}':
            
            {stories_text}
            
            Geef verbeterde versies van deze user stories met betere acceptatiecriteria.
            """
        else:
            print("❌ Geen bestaande user stories gevonden")
            return

    else:
        # Custom opdracht
        prompt = f"""
        Opdracht: {choice}
        
        Project: {project_name} ({project_type})
        Requirements: {requirements}
        
        Schrijf user stories op basis van deze opdracht.
        """

    print("\n🔄 ProductOwner aan het werk...")
    result = ask_openai_with_confidence(prompt)

    print("\n🎯 User Stories:")
    print("=" * 50)
    print(result["answer"])
    print("=" * 50)

    # Sla de user stories op in project context
    project_manager.add_user_story(result["answer"], "high")

    # Publiceer event voor andere agents
    message_bus = get_message_bus()
    await message_bus.publish(EventTypes.USER_STORIES_CREATED, {
        "agent": "ProductOwner",
        "project": project_name,
        "status": "success"
    })

def create_user_story(requirement):
    """Maak een user story op basis van een specifieke requirement."""
    # Input validation
    if not isinstance(requirement, str):
        raise TypeError("Requirement must be a string")
    
    if not requirement or not requirement.strip():
        raise ValueError("Requirement must be a non-empty string")
    
    prompt = f"""
    Schrijf een user story in Gherkin-formaat voor de volgende requirement:
    
    {requirement}
    
    Geef een duidelijke user story met acceptatiecriteria.
    """

    # Context voor de LLM
    context = {
        "task": "create_user_story",
        "agent": "ProductOwner",
        "requirement": requirement
    }

    try:
        result = ask_openai_with_confidence(prompt, context=context)
        print(f"🎯 User Story voor: {requirement}")
        print("=" * 50)
        print(result["answer"])
        print("=" * 50)
        return result
    except Exception as e:
        logging.error(f"Failed to create user story: {e}")
        error_result = {"answer": f"Error creating user story: {e}", "confidence": 0.0}
        print(f"❌ Error: {e}")
        return error_result

def show_bmad_vision():
    """Toon de BMAD visie en strategie."""
    vision = """
    🚀 BMAD (Business Multi-Agent DevOps) Visie
    
    BMAD is een innovatief systeem dat AI-agents inzet voor DevOps en software development.
    
    Kernprincipes:
    - Multi-agent samenwerking
    - Human-in-the-loop workflows
    - Event-driven architectuur
    - Continuous feedback loops
    
    Doelstellingen:
    - Automatisering van repetitieve taken
    - Verbeterde code kwaliteit
    - Snellere development cycles
    - Betere team samenwerking
    
    Frontend Doel:
    - Centraal dashboard voor agent monitoring
    - Intuïtieve workflow management
    - Real-time insights en metrics
    - Eenvoudige API testing en debugging
    """

    print(vision)


async def collaborate_example():
    """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
    message_bus = get_message_bus()
    await message_bus.publish(EventTypes.BACKLOG_UPDATED, {"status": "success", "agent": "ProductOwner"})
    save_context("ProductOwner", "status", {"backlog_status": "updated"})
    print("Event gepubliceerd en context opgeslagen.")
    context = get_context("ProductOwner")
    print(f"Opgehaalde context: {context}")


def ask_llm_user_story(requirement):
    """Vraag de LLM om een user story te genereren met confidence scoring."""
    # Input validation
    if not isinstance(requirement, str):
        raise TypeError("Requirement must be a string")
    
    if not requirement or not requirement.strip():
        raise ValueError("Requirement must be a non-empty string")
    
    prompt = f"""
    Schrijf een user story in Gherkin-formaat voor de volgende requirement:
    
    Requirement: {requirement}
    
    Geef een user story met:
    - Feature beschrijving
    - Scenario's met Given/When/Then
    - Acceptatiecriteria
    - Prioriteit (High/Medium/Low)
    """

    # Context voor confidence scoring
    context = {
        "task": "create_user_story",
        "agent": "ProductOwner",
        "requirement": requirement
    }

    try:
        # Gebruik confidence scoring
        result = ask_openai_with_confidence(prompt, context)

        # Enhance output met confidence scoring
        enhanced_output = confidence_scoring.enhance_agent_output(
            output=result["answer"],
            agent_name="ProductOwner",
            task_type="create_user_story",
            context=context
        )

        # Log confidence info
        print(f"🎯 Confidence Score: {enhanced_output['confidence']:.2f} ({enhanced_output['review_level']})")

        # Als review vereist is, maak review request
        if enhanced_output["review_required"]:
            create_review_request(enhanced_output)
            print("🔍 Review vereist - User story wordt ter goedkeuring voorgelegd")
            print(format_confidence_message(enhanced_output))

            # TODO: Stuur review request naar Slack of andere kanalen
            # publish("review_requested", review_request)

        return enhanced_output["output"]
    except Exception as e:
        logging.error(f"Failed to generate user story with LLM: {e}")
        error_output = f"Error generating user story: {e}"
        print(f"❌ Error: {e}")
        return error_output





if __name__ == "__main__":
    main()
