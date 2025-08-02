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
        
        logger.info(f"{self.agent_name} Agent geïnitialiseerd met MCP integration")
    
    async def initialize_mcp(self):
        """Initialize MCP client and integration."""
        try:
            self.mcp_client = await get_mcp_client()
            self.mcp_integration = get_framework_mcp_integration()
            await initialize_framework_mcp_integration()
            self.mcp_enabled = True
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.warning(f"MCP initialization failed: {e}")
            self.mcp_enabled = False

    async def use_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use MCP tool voor enhanced functionality."""
        if not self.mcp_enabled or not self.mcp_client:
            logger.warning("MCP not available, using local tools")
            return None
        
        try:
            result = await self.mcp_client.execute_tool(tool_name, parameters)
            logger.info(f"MCP tool {tool_name} executed successfully")
            return result
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
        
        enhanced_data = await self.use_data_specific_mcp_tools(data_engineering_data)

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

    async def run(self):
        """Run the agent and listen for events met MCP integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
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
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the DataEngineer agent met MCP integration."""
        agent = cls()
        await agent.initialize_mcp()
        print("DataEngineer agent started with MCP integration")

def main():
    parser = argparse.ArgumentParser(description="Data Engineer Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "data-quality-check", "explain-pipeline", "build-pipeline",
                               "monitor-pipeline", "show-pipeline-history", "show-quality-history",
                               "show-best-practices", "show-changelog", "export-report", "test",
                               "collaborate", "run"])
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
        else:
            print("Unknown command. Use 'help' to see available commands.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
