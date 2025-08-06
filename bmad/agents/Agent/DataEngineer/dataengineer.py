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

# Enhanced MCP Phase 2 imports
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer

# Message Bus Integration
from bmad.agents.core.communication.agent_message_bus_integration import (
    AgentMessageBusIntegration,
    create_agent_message_bus_integration
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DataEngineerAgent:
    """
    Data Engineer Agent voor BMAD.
    Gespecialiseerd in data pipeline development, ETL processes, en data architecture.
    """
    
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        try:
            self.data_engineer_template = self.framework_manager.get_framework_template('data_engineer')
        except:
            self.data_engineer_template = None
        self.lessons_learned = []

        # Set agent name
        self.agent_name = "DataEngineer"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/dataengineer/best-practices.md",
            "pipeline-template": self.resource_base / "templates/dataengineer/pipeline-template.py",
            "data-quality-template": self.resource_base / "templates/dataengineer/data-quality-template.md",
            "etl-template": self.resource_base / "templates/dataengineer/etl-template.py",
            "monitoring-template": self.resource_base / "templates/dataengineer/monitoring-template.md",
            "performance-report": self.resource_base / "templates/dataengineer/performance-report-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/dataengineer/pipeline-changelog.md",
            "history": self.resource_base / "data/dataengineer/pipeline-history.md",
            "quality-history": self.resource_base / "data/dataengineer/quality-history.md"
        }

        # Initialize history
        self.pipeline_history = []
        self.quality_history = []
        self._load_pipeline_history()
        self._load_quality_history()
        
        # MCP Integration
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
        
        # Message Bus Integration
        self.message_bus_integration: Optional[AgentMessageBusIntegration] = None
        self.message_bus_enabled = False
        
        # Initialize tracer
        self.tracer = BMADTracer(config=type("Config", (), {
            "service_name": "DataEngineer",
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

    async def initialize_message_bus_integration(self):
        """Initialize Message Bus Integration for the agent."""
        try:
            self.message_bus_integration = create_agent_message_bus_integration(
                agent_name=self.agent_name,
                agent_instance=self
            )
            
            # Register event handlers for data-specific events
            await self.message_bus_integration.register_event_handler(
                "data_quality_check_requested", 
                self.handle_data_quality_check_requested
            )
            await self.message_bus_integration.register_event_handler(
                "explain_pipeline_requested", 
                self.handle_explain_pipeline
            )
            await self.message_bus_integration.register_event_handler(
                "data_pipeline_build_requested",
                self.handle_pipeline_build_requested
            )
            await self.message_bus_integration.register_event_handler(
                "data_monitoring_requested",
                self.handle_monitoring_requested
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

    async def use_data_specific_mcp_tools(self, data_engineering_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use data-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # Data pipeline development
        pipeline_result = await self.use_mcp_tool("data_pipeline_development", {
            "pipeline_name": data_engineering_data.get("pipeline_name", ""),
            "pipeline_type": data_engineering_data.get("pipeline_type", "etl"),
            "data_sources": data_engineering_data.get("data_sources", []),
            "development_type": "comprehensive"
        })
        if pipeline_result:
            enhanced_data["data_pipeline_development"] = pipeline_result
        
        # Data quality assessment
        quality_result = await self.use_mcp_tool("data_quality_assessment", {
            "data_summary": data_engineering_data.get("data_summary", ""),
            "quality_metrics": data_engineering_data.get("quality_metrics", {}),
            "assessment_type": "comprehensive",
            "validation_rules": data_engineering_data.get("validation_rules", [])
        })
        if quality_result:
            enhanced_data["data_quality_assessment"] = quality_result
        
        # ETL process optimization
        etl_result = await self.use_mcp_tool("etl_process_optimization", {
            "pipeline_code": data_engineering_data.get("pipeline_code", ""),
            "performance_metrics": data_engineering_data.get("performance_metrics", {}),
            "optimization_type": "comprehensive",
            "scaling_strategy": data_engineering_data.get("scaling_strategy", "horizontal")
        })
        if etl_result:
            enhanced_data["etl_process_optimization"] = etl_result
        
        # Data monitoring and alerting
        monitoring_result = await self.use_mcp_tool("data_monitoring_alerting", {
            "pipeline_id": data_engineering_data.get("pipeline_id", ""),
            "monitoring_metrics": data_engineering_data.get("monitoring_metrics", {}),
            "alert_thresholds": data_engineering_data.get("alert_thresholds", {}),
            "notification_channels": data_engineering_data.get("notification_channels", ["slack", "email"])
        })
        if monitoring_result:
            enhanced_data["data_monitoring_alerting"] = monitoring_result
        
        return enhanced_data

    async def use_enhanced_mcp_tools(self, data_engineering_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_data_specific_mcp_tools(data_engineering_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": data_engineering_data.get("capabilities", []),
                "performance_metrics": data_engineering_data.get("performance_metrics", {})
            })
            enhanced_data["core_enhancement"] = core_result
            
            # Data-specific enhanced tools
            data_enhanced_result = await self.use_data_specific_enhanced_tools(data_engineering_data)
            enhanced_data.update(data_enhanced_result)
            
            # Tracing integration
            if self.tracing_enabled:
                trace_result = await self.trace_data_operation(data_engineering_data)
                enhanced_data["tracing"] = trace_result
            
            logger.info(f"Enhanced MCP tools used successfully: {len(enhanced_data)} tools")
            
        except Exception as e:
            logger.error(f"Enhanced MCP tools failed: {e}")
            enhanced_data["error"] = str(e)
        
        return enhanced_data
    
    async def use_data_specific_enhanced_tools(self, data_engineering_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use data-specific enhanced MCP tools."""
        enhanced_tools = {}
        
        try:
            # Enhanced data pipeline development
            if "data_pipeline_development" in data_engineering_data:
                pipeline_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_data_pipeline_development", {
                    "pipeline_data": data_engineering_data["data_pipeline_development"],
                    "development_depth": data_engineering_data.get("development_depth", "comprehensive"),
                    "include_monitoring": data_engineering_data.get("include_monitoring", True)
                })
                enhanced_tools["enhanced_data_pipeline_development"] = pipeline_result
            
            # Enhanced data quality assessment
            if "data_quality_assessment" in data_engineering_data:
                quality_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_data_quality_assessment", {
                    "quality_data": data_engineering_data["data_quality_assessment"],
                    "assessment_comprehensive": data_engineering_data.get("assessment_comprehensive", "advanced"),
                    "include_validation": data_engineering_data.get("include_validation", True)
                })
                enhanced_tools["enhanced_data_quality_assessment"] = quality_result
            
            # Enhanced team collaboration
            if "team_collaboration" in data_engineering_data:
                collaboration_result = await self.enhanced_mcp.communicate_with_agents(
                    ["AiDeveloper", "BackendDeveloper", "DevOpsInfra", "QualityGuardian"],
                    {
                        "type": "data_engineering_review",
                        "content": data_engineering_data["team_collaboration"]
                    }
                )
                enhanced_tools["enhanced_team_collaboration"] = collaboration_result
            
            # Enhanced ETL process optimization
            if "etl_process_optimization" in data_engineering_data:
                etl_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_etl_process_optimization", {
                    "etl_data": data_engineering_data["etl_process_optimization"],
                    "optimization_comprehensive": data_engineering_data.get("optimization_comprehensive", "advanced"),
                    "include_scaling": data_engineering_data.get("include_scaling", True)
                })
                enhanced_tools["enhanced_etl_process_optimization"] = etl_result
            
            logger.info(f"Data-specific enhanced tools executed: {list(enhanced_tools.keys())}")
            
        except Exception as e:
            logger.error(f"Error in data-specific enhanced tools: {e}")
        
        return enhanced_tools
    
    async def trace_data_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace data operations."""
        if not self.tracing_enabled or not self.tracer:
            return {"tracing": "disabled"}
        
        try:
            trace_data = {
                "operation_type": "data_operation",
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "operation_data": operation_data,
                "performance_metrics": {
                    "pipeline_count": len(operation_data.get("pipelines", [])),
                    "data_quality_score": operation_data.get("data_quality_score", 0.0),
                    "etl_performance": operation_data.get("etl_performance", {})
                }
            }
            
            # Add trace to tracer
            if hasattr(self.tracer, 'add_trace'):
                await self.tracer.add_trace("data_operation", trace_data)
            
            logger.info(f"Data operation traced: {trace_data['operation_type']}")
            return trace_data
            
        except Exception as e:
            logger.error(f"Tracing failed: {e}")
            return {"tracing": "error", "error": str(e)}

    def _load_pipeline_history(self):
        """Load pipeline history from data file"""
        try:
            if self.data_paths["history"].exists():
                with open(self.data_paths["history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.pipeline_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Pipeline history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing pipeline history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in pipeline history: {e}")
        except OSError as e:
            logger.error(f"OS error loading pipeline history: {e}")
        except Exception as e:
            logger.warning(f"Could not load pipeline history: {e}")

    def _save_pipeline_history(self):
        """Save pipeline history to data file"""
        try:
            self.data_paths["history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["history"], "w") as f:
                f.write("# Data Pipeline History\n\n")
                for pipeline in self.pipeline_history[-50:]:  # Keep last 50 pipelines
                    f.write(f"- {pipeline}\n")
        except PermissionError as e:
            logger.error(f"Permission denied saving pipeline history: {e}")
        except OSError as e:
            logger.error(f"OS error saving pipeline history: {e}")
        except Exception as e:
            logger.error(f"Could not save pipeline history: {e}")

    def _load_quality_history(self):
        """Load quality history from data file"""
        try:
            if self.data_paths["quality-history"].exists():
                with open(self.data_paths["quality-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.quality_history.append(line.strip()[2:])
        except FileNotFoundError:
            logger.info("Quality history file not found, starting with empty history")
        except PermissionError as e:
            logger.error(f"Permission denied accessing quality history: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error in quality history: {e}")
        except OSError as e:
            logger.error(f"OS error loading quality history: {e}")
        except Exception as e:
            logger.warning(f"Could not load quality history: {e}")

    def _save_quality_history(self):
        """Save quality history to data file"""
        try:
            self.data_paths["quality-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["quality-history"], "w") as f:
                f.write("# Data Quality History\n\n")
                for quality in self.quality_history[-50:]:  # Keep last 50 quality checks
                    f.write(f"- {quality}\n")
        except PermissionError as e:
            logger.error(f"Permission denied saving quality history: {e}")
        except OSError as e:
            logger.error(f"OS error saving quality history: {e}")
        except Exception as e:
            logger.error(f"Could not save quality history: {e}")

    def show_help(self):
        """Show available commands"""
        help_text = """
Data Engineer Agent Commands:
  help                    - Show this help message
  data-quality-check      - Run data quality check
  explain-pipeline        - Explain ETL pipeline
  build-pipeline          - Build new data pipeline
  monitor-pipeline        - Monitor pipeline performance
  show-pipeline-history   - Show pipeline history
  show-quality-history    - Show quality check history
  show-best-practices     - Show data engineering best practices
  show-changelog          - Show pipeline changelog
  export-report [format]  - Export pipeline report (format: md, csv, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents

Enhanced MCP Phase 2 Commands:
  enhanced-collaborate    - Enhanced collaboration with other agents
  enhanced-security       - Enhanced security features
  enhanced-performance    - Enhanced performance monitoring
  trace-operation         - Trace data operation
  trace-performance       - Trace performance metrics
  trace-error             - Trace error handling
  tracing-summary         - Show tracing summary

Message Bus Integration Commands:
  initialize-message-bus  - Initialize Message Bus Integration
  message-bus-status      - Show Message Bus Integration status
  publish-event           - Publish data event
  subscribe-event         - Subscribe to data events
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
            elif resource_type == "pipeline-template":
                path = self.template_paths["pipeline-template"]
            elif resource_type == "data-quality-template":
                path = self.template_paths["data-quality-template"]
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

    def show_pipeline_history(self):
        """Show pipeline history"""
        if not self.pipeline_history:
            print("No pipeline history available.")
            return
        print("Data Pipeline History:")
        print("=" * 50)
        for i, pipeline in enumerate(self.pipeline_history[-10:], 1):
            print(f"{i}. {pipeline}")

    def show_quality_history(self):
        """Show quality check history"""
        if not self.quality_history:
            print("No quality check history available.")
            return
        print("Data Quality Check History:")
        print("=" * 50)
        for i, quality in enumerate(self.quality_history[-10:], 1):
            print(f"{i}. {quality}")

    def data_quality_check(self, data_summary: str = "Sample data summary") -> Dict[str, Any]:
        """Run data quality check with enhanced functionality."""
        # Input validation
        if not isinstance(data_summary, str):
            raise TypeError("data_summary must be a string")
        
        if not data_summary.strip():
            raise ValueError("data_summary cannot be empty")
        
        logger.info("Running data quality check")

        # Simulate data quality check
        time.sleep(1)

        quality_result = {
            "check_type": "Data Quality Assessment",
            "data_summary": data_summary,
            "overall_score": 92,
            "checks_performed": {
                "completeness": {
                    "score": 95,
                    "status": "PASS",
                    "findings": "Data completeness is excellent"
                },
                "accuracy": {
                    "score": 88,
                    "status": "PASS",
                    "findings": "Data accuracy is good with minor issues"
                },
                "consistency": {
                    "score": 94,
                    "status": "PASS",
                    "findings": "Data consistency is very good"
                },
                "timeliness": {
                    "score": 90,
                    "status": "PASS",
                    "findings": "Data is up to date"
                }
            },
            "issues_found": [
                {
                    "type": "accuracy",
                    "description": "Some duplicate records detected",
                    "severity": "medium",
                    "recommendation": "Implement deduplication logic"
                }
            ],
            "recommendations": [
                "Implement automated data validation",
                "Add data lineage tracking",
                "Set up data quality monitoring alerts"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "DataEngineerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("DataEngineer", MetricType.SUCCESS_RATE, quality_result["overall_score"], "%")

        # Add to quality history
        quality_entry = f"{datetime.now().isoformat()}: Data quality check completed with {quality_result['overall_score']}% score"
        self.quality_history.append(quality_entry)
        self._save_quality_history()

        logger.info(f"Data quality check completed: {quality_result}")
        return quality_result

    def explain_pipeline(self, pipeline_code: str = "Sample ETL pipeline") -> Dict[str, Any]:
        """Explain ETL pipeline with enhanced functionality."""
        # Input validation
        if not isinstance(pipeline_code, str):
            raise TypeError("pipeline_code must be a string")
        
        if not pipeline_code.strip():
            raise ValueError("pipeline_code cannot be empty")
        
        logger.info("Explaining ETL pipeline")

        # Simulate pipeline explanation
        time.sleep(1)

        explanation_result = {
            "pipeline_code": pipeline_code,
            "explanation_type": "ETL Pipeline Analysis",
            "overall_complexity": "Medium",
            "components": {
                "extract": {
                    "description": "Data extraction from multiple sources",
                    "complexity": "Low",
                    "performance": "Good"
                },
                "transform": {
                    "description": "Data transformation and cleaning",
                    "complexity": "Medium",
                    "performance": "Good"
                },
                "load": {
                    "description": "Data loading into target system",
                    "complexity": "Low",
                    "performance": "Excellent"
                }
            },
            "performance_metrics": {
                "execution_time": "2.5 minutes",
                "data_volume": "1.2 GB",
                "success_rate": "98%",
                "error_rate": "2%"
            },
            "optimization_suggestions": [
                "Add parallel processing for large datasets",
                "Implement incremental loading",
                "Add data validation checkpoints"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "DataEngineerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("DataEngineer", MetricType.SUCCESS_RATE, 95, "%")

        logger.info(f"Pipeline explanation completed: {explanation_result}")
        return explanation_result

    async def build_pipeline(self, pipeline_name: str = "ETL Pipeline") -> Dict[str, Any]:
        """Build new data pipeline met MCP enhancement."""
        # Input validation
        if not isinstance(pipeline_name, str):
            raise TypeError("pipeline_name must be a string")
        
        if not pipeline_name.strip():
            raise ValueError("pipeline_name cannot be empty")
        
        logger.info(f"Building data pipeline: {pipeline_name}")

        # Use MCP tools for enhanced pipeline development
        data_engineering_data = {
            "pipeline_name": pipeline_name,
            "pipeline_type": "etl",
            "data_sources": ["database", "api", "files"],
            "development_type": "comprehensive",
            "data_summary": "Sample data summary for pipeline development",
            "quality_metrics": {"completeness": 95, "accuracy": 98, "consistency": 92},
            "validation_rules": ["not_null", "data_type", "range_check"],
            "pipeline_code": "Sample ETL pipeline code",
            "performance_metrics": {"processing_time": 120, "throughput": 1000},
            "scaling_strategy": "horizontal",
            "pipeline_id": "pipeline_001",
            "monitoring_metrics": {"success_rate": 99.5, "error_rate": 0.5},
            "alert_thresholds": {"error_rate": 1.0, "processing_time": 300},
            "notification_channels": ["slack", "email"]
        }
        
        enhanced_data = await self.use_enhanced_mcp_tools(data_engineering_data)

        # Simulate pipeline building
        time.sleep(2)

        pipeline_result = {
            "pipeline_name": pipeline_name,
            "build_type": "ETL Pipeline",
            "status": "success",
            "components_created": {
                "extractors": ["database_extractor", "api_extractor", "file_extractor"],
                "transformers": ["data_cleaner", "data_validator", "data_enricher"],
                "loaders": ["database_loader", "warehouse_loader"]
            },
            "configuration": {
                "parallel_processing": True,
                "error_handling": "comprehensive",
                "monitoring": "enabled",
                "logging": "detailed"
            },
            "performance_optimization": {
                "caching": "enabled",
                "batch_processing": "optimized",
                "memory_usage": "efficient"
            },
            "quality_checks": [
                "data_completeness_check",
                "data_accuracy_check",
                "data_consistency_check"
            ],
            "data_architecture": {
                "data_lake": "configured",
                "data_warehouse": "optimized",
                "data_marts": "designed"
            },
            "etl_processes": {
                "extract_processes": ["incremental", "full_load", "change_data_capture"],
                "transform_processes": ["cleansing", "enrichment", "aggregation"],
                "load_processes": ["append", "upsert", "replace"]
            },
            "monitoring_setup": {
                "metrics_collection": "enabled",
                "alerting": "configured",
                "dashboard": "created"
            },
            "timestamp": datetime.now().isoformat(),
            "agent": "DataEngineerAgent"
        }

        # Add MCP enhanced data if available
        if enhanced_data:
            pipeline_result["mcp_enhanced_data"] = enhanced_data
            pipeline_result["mcp_enhanced"] = True

        # Add to history
        pipeline_entry = f"{pipeline_result['timestamp']}: {pipeline_name} - Status: {pipeline_result['status']}"
        self.pipeline_history.append(pipeline_entry)
        self._save_pipeline_history()

        logger.info(f"Pipeline build result: {pipeline_result}")
        return pipeline_result

    def monitor_pipeline(self, pipeline_id: str = "pipeline_001") -> Dict[str, Any]:
        """Monitor pipeline performance."""
        # Input validation
        if not isinstance(pipeline_id, str):
            raise TypeError("pipeline_id must be a string")
        
        if not pipeline_id.strip():
            raise ValueError("pipeline_id cannot be empty")
        
        logger.info(f"Monitoring pipeline: {pipeline_id}")

        # Simulate pipeline monitoring
        time.sleep(1)

        monitoring_result = {
            "pipeline_id": pipeline_id,
            "monitoring_type": "Real-time Performance",
            "current_status": "running",
            "performance_metrics": {
                "execution_time": "1.8 minutes",
                "data_processed": "850 MB",
                "records_processed": "125000",
                "success_rate": "99.5%",
                "error_count": 5,
                "warning_count": 12
            },
            "resource_usage": {
                "cpu_usage": "45%",
                "memory_usage": "2.1 GB",
                "disk_io": "150 MB/s",
                "network_io": "50 MB/s"
            },
            "alerts": [
                {
                    "type": "warning",
                    "message": "High memory usage detected",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "recommendations": [
                "Consider increasing memory allocation",
                "Optimize data processing algorithms",
                "Implement better error handling"
            ],
            "timestamp": datetime.now().isoformat(),
            "agent": "DataEngineerAgent"
        }

        # Log performance metrics
        self.monitor._record_metric("DataEngineer", MetricType.SUCCESS_RATE, 99, "%")

        logger.info(f"Pipeline monitoring completed: {monitoring_result}")
        return monitoring_result

    def export_report(self, format_type: str = "md", report_data: Optional[Dict] = None):
        """Export pipeline report in specified format."""
        # Input validation
        if not isinstance(format_type, str):
            raise TypeError("format_type must be a string")
        
        if format_type not in ["md", "csv", "json"]:
            raise ValueError("format_type must be one of: md, csv, json")
        
        if report_data is not None and not isinstance(report_data, dict):
            raise TypeError("report_data must be a dictionary")
        
        if not report_data:
            report_data = {
                "report_type": "Data Pipeline Report",
                "pipeline_name": "ETL Pipeline",
                "overall_score": 92,
                "total_pipelines": 15,
                "success_rate": "98%",
                "timestamp": datetime.now().isoformat(),
                "agent": "DataEngineerAgent"
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
            output_file = f"data_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            content = f"""# Data Pipeline Report

## Summary
- **Report Type**: {report_data.get('report_type', 'N/A')}
- **Pipeline Name**: {report_data.get('pipeline_name', 'N/A')}
- **Overall Score**: {report_data.get('overall_score', 0)}%
- **Total Pipelines**: {report_data.get('total_pipelines', 0)}
- **Success Rate**: {report_data.get('success_rate', 'N/A')}
- **Timestamp**: {report_data.get('timestamp', 'N/A')}
- **Agent**: {report_data.get('agent', 'N/A')}

## Performance Metrics
- **Execution Time**: {report_data.get('performance_metrics', {}).get('execution_time', 'N/A')}
- **Data Processed**: {report_data.get('performance_metrics', {}).get('data_processed', 'N/A')}
- **Records Processed**: {report_data.get('performance_metrics', {}).get('records_processed', 'N/A')}

## Quality Metrics
- **Completeness**: {report_data.get('quality_metrics', {}).get('completeness', 'N/A')}
- **Accuracy**: {report_data.get('quality_metrics', {}).get('accuracy', 'N/A')}
- **Consistency**: {report_data.get('quality_metrics', {}).get('consistency', 'N/A')}
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
            output_file = f"data_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Overall Score", report_data.get("overall_score", 0)])
                writer.writerow(["Success Rate", report_data.get("success_rate", "N/A")])
                writer.writerow(["Total Pipelines", report_data.get("total_pipelines", 0)])

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
            output_file = f"data_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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
        logger.info("Starting data engineering collaboration example...")

        # Publish pipeline validation event
        publish("pipeline_validated", {
            "status": "success",
            "agent": "DataEngineerAgent",
            "timestamp": datetime.now().isoformat()
        })

        # Run data quality check
        quality_result = self.data_quality_check("Sample data for quality assessment")

        # Build pipeline
        pipeline_result = await self.build_pipeline("Sample ETL Pipeline")

        # Publish completion
        publish("data_engineering_completed", {
            "status": "success",
            "agent": "DataEngineerAgent",
            "quality_score": quality_result["overall_score"],
            "pipeline_status": pipeline_result["status"]
        })

        # Save context
        save_context("DataEngineer", "status", {"pipeline_status": "validated"})

        # Notify via Slack
        try:
            send_slack_message(f"Data engineering completed with {quality_result['overall_score']}% quality score")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")

        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("DataEngineer")
        print(f"Opgehaalde context: {context}")

    def handle_data_quality_check_requested(self, event):
        """Handle data quality check request from other agents."""
        # Input validation
        if not isinstance(event, dict):
            logger.warning("Invalid event type for data quality check request")
            return
        
        logger.info(f"Data quality check requested: {event}")
        data_summary = event.get("data_summary", "Sample data summary")
        self.data_quality_check(data_summary)

    def handle_explain_pipeline(self, event):
        """Handle pipeline explanation request from other agents."""
        # Input validation
        if not isinstance(event, dict):
            logger.warning("Invalid event type for pipeline explanation request")
            return
        
        logger.info(f"Pipeline explanation requested: {event}")
        pipeline_code = event.get("pipeline_code", "Sample ETL pipeline")
        self.explain_pipeline(pipeline_code)

    async def handle_pipeline_build_requested(self, event):
        """Handle data pipeline build requested event."""
        logger.info(f"Data pipeline build requested: {event}")
        try:
            # Perform pipeline build based on event data
            pipeline_name = event.get("pipeline_name", "ETL Pipeline")
            pipeline_type = event.get("pipeline_type", "etl")
            
            # Simulate pipeline build
            build_result = await self.build_pipeline(pipeline_name)
            
            await publish("data_pipeline_build_completed", {
                "request_id": event.get("request_id"),
                "pipeline_name": pipeline_name,
                "result": build_result
            })
        except Exception as e:
            logger.error(f"Error handling pipeline build request: {e}")

    async def handle_monitoring_requested(self, event):
        """Handle data monitoring requested event."""
        logger.info(f"Data monitoring requested: {event}")
        try:
            # Perform data monitoring based on event data
            pipeline_id = event.get("pipeline_id", "pipeline_001")
            monitoring_type = event.get("monitoring_type", "performance")
            
            # Simulate monitoring
            monitoring_result = self.monitor_pipeline(pipeline_id)
            
            await publish("data_monitoring_completed", {
                "request_id": event.get("request_id"),
                "pipeline_id": pipeline_id,
                "result": monitoring_result
            })
        except Exception as e:
            logger.error(f"Error handling monitoring request: {e}")

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize Message Bus Integration
        await self.initialize_message_bus_integration()
        
        print("📊 DataEngineer is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled" if self.message_bus_enabled else "Message Bus: Disabled")
        
        def sync_handler(event):
            asyncio.run(self.handle_data_quality_check_requested(event))

        subscribe("data_quality_check_requested", self.handle_data_quality_check_requested)
        subscribe("explain_pipeline", self.handle_explain_pipeline)

        logger.info("DataEngineerAgent ready and listening for events...")
        await self.collaborate_example()
        
        try:
            # Keep the agent running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("DataEngineer agent stopped.")
    
    async def run_async(self):
        """Run the agent with enhanced MCP and tracing initialization."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        # Initialize Message Bus Integration
        await self.initialize_message_bus_integration()
        
        print("📊 DataEngineer is running...")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Message Bus: Enabled" if self.message_bus_enabled else "Message Bus: Disabled")
        
        logger.info("DataEngineerAgent ready and listening for events...")
        await self.collaborate_example()
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the DataEngineer agent met MCP integration."""
        agent = cls()
        await agent.run_async()
    
    @classmethod
    async def run_agent_async(cls):
        """Class method to run the DataEngineer agent with enhanced MCP."""
        agent = cls()
        await agent.run_async()

def main():
    parser = argparse.ArgumentParser(description="Data Engineer Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "data-quality-check", "explain-pipeline", "build-pipeline",
                               "monitor-pipeline", "show-pipeline-history", "show-quality-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run", "enhanced-collaborate", "enhanced-security", 
                               "enhanced-performance", "trace-operation", "trace-performance", 
                               "trace-error", "tracing-summary",
                               "initialize-message-bus", "message-bus-status", "publish-event", "subscribe-event"])
    parser.add_argument("--format", choices=["md", "csv", "json"], default="md", help="Export format")
    parser.add_argument("--data-summary", default="Sample data summary", help="Data summary for quality check")
    parser.add_argument("--pipeline-code", default="Sample ETL pipeline", help="Pipeline code to explain")
    parser.add_argument("--pipeline-name", default="ETL Pipeline", help="Pipeline name for building")
    parser.add_argument("--pipeline-id", default="pipeline_001", help="Pipeline ID for monitoring")

    args = parser.parse_args()

    try:
        agent = DataEngineerAgent()

        if args.command == "help":
            agent.show_help()
        elif args.command == "data-quality-check":
            result = agent.data_quality_check(args.data_summary)
            print(json.dumps(result, indent=2))
        elif args.command == "explain-pipeline":
            result = agent.explain_pipeline(args.pipeline_code)
            print(json.dumps(result, indent=2))
        elif args.command == "build-pipeline":
            result = asyncio.run(agent.build_pipeline(args.pipeline_name))
            print(json.dumps(result, indent=2))
        elif args.command == "monitor-pipeline":
            result = agent.monitor_pipeline(args.pipeline_id)
            print(json.dumps(result, indent=2))
        elif args.command == "show-pipeline-history":
            agent.show_pipeline_history()
        elif args.command == "show-quality-history":
            agent.show_quality_history()
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
        # Enhanced MCP Phase 2 Commands
        elif args.command in ["enhanced-collaborate", "enhanced-security", "enhanced-performance", 
                             "trace-operation", "trace-performance", "trace-error", "tracing-summary"]:
            # Enhanced MCP commands
            if args.command == "enhanced-collaborate":
                result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
                    ["AiDeveloper", "BackendDeveloper", "DevOpsInfra", "QualityGuardian"], 
                    {"type": "data_engineering_review", "content": {"review_type": "data_pipeline_development"}}
                ))
                print(json.dumps(result, indent=2))
            elif args.command == "enhanced-security":
                result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
                    "data_engineering_data": {"pipelines": [], "quality_checks": [], "monitoring": []},
                    "security_requirements": ["data_validation", "pipeline_security", "monitoring_safety"]
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "enhanced-performance":
                result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
                    "data_engineering_data": {"pipelines": [], "quality_checks": [], "monitoring": []},
                    "performance_metrics": {"pipeline_speed": 85.5, "quality_score": 92.3}
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "trace-operation":
                result = asyncio.run(agent.trace_data_operation({
                    "operation_type": "data_engineering",
                    "pipeline_name": args.pipeline_name,
                    "pipelines": list(agent.pipeline_history)
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "trace-performance":
                result = asyncio.run(agent.trace_data_operation({
                    "operation_type": "performance_analysis",
                    "performance_metrics": {"pipeline_speed": 85.5, "quality_score": 92.3}
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "trace-error":
                result = asyncio.run(agent.trace_data_operation({
                    "operation_type": "error_analysis",
                    "error_data": {"error_type": "pipeline_failure", "error_message": "Pipeline failed"}
                }))
                print(json.dumps(result, indent=2))
            elif args.command == "tracing-summary":
                print("Tracing Summary for DataEngineer:")
                print(f"Enhanced MCP: {'Enabled' if agent.enhanced_mcp_enabled else 'Disabled'}")
                print(f"Tracing: {'Enabled' if agent.tracing_enabled else 'Disabled'}")
                print(f"Agent: {agent.agent_name}")
        # Message Bus Integration Commands
        elif args.command == "initialize-message-bus":
            result = asyncio.run(agent.initialize_message_bus_integration())
            print(f"Message Bus Integration: {'Enabled' if result else 'Failed'}")
        elif args.command == "message-bus-status":
            print(f"Message Bus Integration: {'Enabled' if agent.message_bus_enabled else 'Disabled'}")
        elif args.command == "publish-event":
            # Example: publish data quality check requested event
            event_data = {"data_summary": "Sample data", "request_id": "test-123"}
            asyncio.run(publish("data_quality_check_requested", event_data))
            print(f"Published event: data_quality_check_requested with data: {event_data}")
        elif args.command == "subscribe-event":
            # Example: subscribe to data events
            def event_handler(event):
                print(f"Received event: {event}")
            subscribe("data_quality_check_completed", event_handler)
            print("Subscribed to data_quality_check_completed events")
        else:
            print("Unknown command. Use 'help' to see available commands.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
