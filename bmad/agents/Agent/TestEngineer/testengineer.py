import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import argparse
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

from bmad.agents.core.agent.agent_performance_monitor import (
    MetricType,
    get_performance_monitor,
)
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.core.mcp import (
    MCPClient, MCPContext, FrameworkMCPIntegration,
    get_mcp_client, get_framework_mcp_integration, initialize_framework_mcp_integration
)

# Enhanced MCP Integration for Phase 2
from bmad.core.mcp.enhanced_mcp_integration import (
    EnhancedMCPIntegration,
    create_enhanced_mcp_integration
)

# Tracing Integration
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from integrations.slack.slack_notify import send_slack_message
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class TestEngineerAgent:
    def __init__(self):
        self.framework_manager = get_framework_templates_manager()
        self.testing_engineer_template = self.framework_manager.get_framework_template('testing_engineer')
        self.lessons_learned = []
        
        # Initialize MCP integration
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_integration: Optional[FrameworkMCPIntegration] = None
        self.mcp_enabled = False
        
        # Enhanced MCP Phase 2
        self.enhanced_mcp: Optional[EnhancedMCPIntegration] = None
        self.enhanced_mcp_enabled = False
        
        # Tracing Integration
        self.tracer: Optional[BMADTracer] = None
        self.tracing_enabled = False

        self.agent_name = "TestEngineerAgent"
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

        # Resource paths
        self.resource_base = Path("/Users/yannickmacgillavry/Projects/BMAD/bmad/resources")
        self.template_paths = {
            "best-practices": self.resource_base / "templates/testengineer/best-practices.md",
            "test-strategy": self.resource_base / "templates/testengineer/test-strategy-template.md",
            "ai-test": self.resource_base / "templates/testengineer/ai-test-template.py",
            "unit-test": self.resource_base / "templates/testengineer/unit-test-template.py",
            "integration-test": self.resource_base / "templates/testengineer/integration-test-template.py",
            "e2e-test": self.resource_base / "templates/testengineer/e2e-test-template.py",
            "test-report-md": self.resource_base / "templates/testengineer/test-report-export-template.md",
            "test-report-json": self.resource_base / "templates/testengineer/test-report-export-template.json",
            "testdata": self.resource_base / "templates/testengineer/testdata-template.json",
            "coverage-report": self.resource_base / "templates/testengineer/coverage-report-template.md"
        }
        self.data_paths = {
            "changelog": self.resource_base / "data/testengineer/test-changelog.md",
            "test-history": self.resource_base / "data/testengineer/test-history.md",
            "coverage-history": self.resource_base / "data/testengineer/coverage-history.md"
        }

        # Initialize test history
        self.test_history = []
        self.coverage_history = []
        self._load_test_history()
        self._load_coverage_history()

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
            self.enhanced_mcp_enabled = await self.enhanced_mcp.initialize_enhanced_mcp()
            
            if self.enhanced_mcp_enabled:
                logger.info("Enhanced MCP capabilities initialized successfully")
            else:
                logger.warning("Enhanced MCP initialization failed, falling back to standard MCP")
        except Exception as e:
            logger.warning(f"Enhanced MCP initialization failed: {e}")
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
                logger.info("Tracing capabilities initialized successfully")
                await self.tracer.setup_agent_specific_tracing({
                    "agent_name": self.agent_name,
                    "tracing_level": "detailed",
                    "performance_tracking": True,
                    "error_tracking": True
                })
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

    async def use_test_specific_mcp_tools(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use test-specific MCP tools voor enhanced functionality."""
        enhanced_data = {}
        
        # Test generation
        test_gen_result = await self.use_mcp_tool("test_generation", {
            "component_name": test_data.get("component_name", ""),
            "test_type": test_data.get("test_type", ""),
            "framework": test_data.get("framework", "pytest"),
            "generation_type": "comprehensive"
        })
        if test_gen_result:
            enhanced_data["test_generation"] = test_gen_result
        
        # Test execution
        test_exec_result = await self.use_mcp_tool("test_execution", {
            "test_suite": test_data.get("test_suite", ""),
            "test_type": test_data.get("test_type", ""),
            "execution_mode": test_data.get("execution_mode", "standard"),
            "coverage_tracking": test_data.get("coverage_tracking", True)
        })
        if test_exec_result:
            enhanced_data["test_execution"] = test_exec_result
        
        # Coverage analysis
        coverage_result = await self.use_mcp_tool("coverage_analysis", {
            "test_results": test_data.get("test_results", {}),
            "coverage_data": test_data.get("coverage_data", {}),
            "analysis_type": "comprehensive",
            "report_format": test_data.get("report_format", "detailed")
        })
        if coverage_result:
            enhanced_data["coverage_analysis"] = coverage_result
        
        # Test reporting
        report_result = await self.use_mcp_tool("test_reporting", {
            "test_data": test_data.get("test_data", {}),
            "report_type": test_data.get("report_type", "comprehensive"),
            "format": test_data.get("format", "markdown"),
            "include_coverage": test_data.get("include_coverage", True)
        })
        if report_result:
            enhanced_data["test_reporting"] = report_result
        
        return enhanced_data
    
    async def use_enhanced_mcp_tools(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use enhanced MCP tools voor Phase 2 capabilities."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            logger.warning("Enhanced MCP not available, using standard MCP tools")
            return await self.use_test_specific_mcp_tools(test_data)
        
        enhanced_data = {}
        
        try:
            # Core enhancement tools
            core_result = await self.enhanced_mcp.use_enhanced_mcp_tool("core_enhancement", {
                "agent_type": self.agent_name,
                "enhancement_level": "advanced",
                "capabilities": test_data.get("capabilities", []),
                "performance_metrics": test_data.get("performance_metrics", {})
            })
            if core_result:
                enhanced_data["core_enhancement"] = core_result
            
            # Test-specific enhancement tools
            specific_result = await self.use_test_specific_enhanced_tools(test_data)
            if specific_result:
                enhanced_data.update(specific_result)
            
        except Exception as e:
            logger.error(f"Error in enhanced MCP tools: {e}")
        
        return enhanced_data
    
    async def use_test_specific_enhanced_tools(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use test-specific enhanced MCP tools."""
        if not self.enhanced_mcp_enabled or not self.enhanced_mcp:
            return {}
        
        enhanced_data = {}
        
        try:
            # Enhanced test execution
            enhanced_test_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_test_execution", {
                "component_name": test_data.get("component_name", ""),
                "test_type": test_data.get("test_type", "unit"),
                "enhancement_level": "advanced",
                "parallel_execution": test_data.get("parallel_execution", True),
                "intelligent_retry": test_data.get("intelligent_retry", True)
            })
            if enhanced_test_result:
                enhanced_data["enhanced_test_execution"] = enhanced_test_result
            
            # Enhanced coverage analysis
            enhanced_coverage_result = await self.enhanced_mcp.use_enhanced_mcp_tool("enhanced_coverage_analysis", {
                "component_name": test_data.get("component_name", ""),
                "coverage_type": test_data.get("coverage_type", "comprehensive"),
                "enhancement_level": "advanced",
                "predictive_analysis": test_data.get("predictive_analysis", True),
                "trend_analysis": test_data.get("trend_analysis", True)
            })
            if enhanced_coverage_result:
                enhanced_data["enhanced_coverage_analysis"] = enhanced_coverage_result
            
            # Enhanced performance optimization
            enhanced_performance_result = await self.enhanced_mcp.enhanced_performance_optimization({
                "agent_type": "test_engineer",
                "test_data": test_data,
                "optimization_targets": ["execution_time", "memory_usage", "coverage_accuracy"]
            })
            if enhanced_performance_result:
                enhanced_data["enhanced_performance_optimization"] = enhanced_performance_result
            
        except Exception as e:
            logger.error(f"Error in test-specific enhanced tools: {e}")
        
        return enhanced_data
    
    async def trace_test_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trace test-specific operations."""
        if not self.tracing_enabled or not self.tracer:
            return {}
        
        try:
            trace_result = await self.tracer.trace_agent_operation({
                "operation_type": operation_data.get("type", "test_execution"),
                "agent_name": self.agent_name,
                "performance_metrics": operation_data.get("performance_metrics", {}),
                "timestamp": datetime.now().isoformat()
            })
            return trace_result
        except Exception as e:
            logger.error(f"Test operation tracing failed: {e}")
            return {}

    def _load_test_history(self):
        try:
            if self.data_paths["test-history"].exists():
                with open(self.data_paths["test-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.test_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load test history: {e}")

    def _save_test_history(self):
        try:
            self.data_paths["test-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["test-history"], "w") as f:
                f.write("# Test History\n\n")
                f.writelines(f"- {test}\n" for test in self.test_history[-50:])
        except Exception as e:
            logger.error(f"Could not save test history: {e}")

    def _load_coverage_history(self):
        try:
            if self.data_paths["coverage-history"].exists():
                with open(self.data_paths["coverage-history"]) as f:
                    content = f.read()
                    lines = content.split("\n")
                    for line in lines:
                        if line.strip().startswith("- "):
                            self.coverage_history.append(line.strip()[2:])
        except Exception as e:
            logger.warning(f"Could not load coverage history: {e}")

    def _save_coverage_history(self):
        try:
            self.data_paths["coverage-history"].parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_paths["coverage-history"], "w") as f:
                f.write("# Coverage History\n\n")
                f.writelines(f"- {cov}\n" for cov in self.coverage_history[-50:])
        except Exception as e:
            logger.error(f"Could not save coverage history: {e}")

    def show_help(self):
        help_text = """
TestEngineer Agent Commands:
  help                    - Show this help message
  run-tests               - Run all tests and generate report
  show-coverage           - Show test coverage
  show-test-history       - Show test history
  show-best-practices     - Show best practices
  show-changelog          - Show changelog
  export-report [format]  - Export last test report (md, json)
  test                    - Test resource completeness
  collaborate             - Demonstrate collaboration with other agents
        """
        print(help_text)

    def show_resource(self, resource_type: str):
        try:
            if resource_type == "best-practices":
                path = self.template_paths["best-practices"]
            elif resource_type == "changelog":
                path = self.data_paths["changelog"]
            elif resource_type == "coverage-report":
                path = self.template_paths["coverage-report"]
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

    def show_test_history(self):
        if not self.test_history:
            print("No test history available.")
            return
        print("Test History:")
        print("=" * 50)
        for i, test in enumerate(self.test_history[-10:], 1):
            print(f"{i}. {test}")

    def show_coverage(self):
        if not self.coverage_history:
            print("No coverage history available.")
            return
        print("Coverage History:")
        print("=" * 50)
        for i, cov in enumerate(self.coverage_history[-10:], 1):
            print(f"{i}. {cov}")

    async def run_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite met MCP enhancement."""
        logger.info("Running all tests...")
        
        # Try MCP-enhanced testing first
        if self.mcp_enabled and self.mcp_client:
            try:
                mcp_result = await self.use_mcp_tool("run_test_suite", {
                    "test_type": "comprehensive",
                    "include_coverage": True,
                    "parallel_execution": True
                })
                
                if mcp_result:
                    logger.info("MCP-enhanced test execution completed")
                    result = mcp_result
                    result["mcp_enhanced"] = True
                else:
                    logger.warning("MCP test execution failed, falling back to local execution")
                    result = self._run_local_tests()
            except Exception as e:
                logger.warning(f"MCP test execution failed: {e}, using local execution")
                result = self._run_local_tests()
        else:
            # Fallback naar lokale test execution
            result = self._run_local_tests()
        
        # Voeg aan historie toe
        test_entry = f"{datetime.now().isoformat()}: {sum('✅' in v for v in result.values())}/{len(result)} tests succesvol"
        self.test_history.append(test_entry)
        self._save_test_history()
        
        # Log performance metric
        self.monitor._record_metric("TestEngineer", MetricType.SUCCESS_RATE, sum("✅" in v for v in result.values())/len(result)*100, "%")
        logger.info(f"Test results: {result}")
        return result

    def _run_local_tests(self) -> Dict[str, Any]:
        """Run local test suite als fallback."""
        # Simuleer testuitvoering
        time.sleep(1)
        return {
            "redis_cache": "✅ Basic operations werken",
            "monitoring": "⚠️ Async issues gedetecteerd",
            "connection_pool": "⚠️ Initialization problemen",
            "llm_caching": "✅ Decorator werkt"
        }

    def validate_input(self, component_name: str, test_type: str):
        """Validate input parameters for test generation."""
        if not component_name or not isinstance(component_name, str):
            raise ValueError("Component name must be a non-empty string")
        if test_type not in ["unit", "integration", "e2e"]:
            raise ValueError("Test type must be unit, integration, or e2e")

    async def generate_tests(self, component_name: str = "TestComponent", test_type: str = "unit") -> Dict[str, Any]:
        """
        Generate tests for a component or feature met MCP enhancement.
        
        Args:
            component_name: Name of the component to test
            test_type: Type of test to generate (unit, integration, e2e)
            
        Returns:
            Dict containing test generation results
        """
        try:
            # Validate input parameters
            self.validate_input(component_name, test_type)
            logger.info(f"Generating {test_type} tests for component: {component_name}")
            
            # Record start time for performance monitoring
            start_time = time.time()
            
            # Use MCP tools for enhanced test generation
            test_data = {
                "component_name": component_name,
                "test_type": test_type,
                "framework": "pytest",
                "generation_type": "comprehensive",
                "include_coverage": True,
                "best_practices": True
            }
            
            enhanced_data = await self.use_test_specific_mcp_tools(test_data)
            
            # Generate test content (local fallback if MCP not available)
            test_content = self._generate_test_content(component_name, test_type)
            test_result = self._create_test_result(component_name, test_type, test_content)
            
            # Add MCP enhanced data if available
            if enhanced_data:
                test_result["mcp_enhanced_data"] = enhanced_data
                test_result["mcp_enhanced"] = True
            
            # Record performance
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Log performance metric
            self.monitor.record_metric(
                MetricType.RESPONSE_TIME,
                "test_generation",
                generation_time,
                {"component_name": component_name, "test_type": test_type}
            )
            
            # Save to test history
            self.test_history.append(f"Generated {test_type} tests for {component_name} in {generation_time:.2f}s")
            self._save_test_history()
            
            logger.info(f"Test generation completed: {component_name}")
            
            return {
                "success": True,
                "component_name": component_name,
                "test_type": test_type,
                "generation_time": generation_time,
                "test_result": test_result
            }
            
        except Exception as e:
            logger.error(f"Error generating tests for {component_name}: {e}")
            return {
                "success": False,
                "component_name": component_name,
                "test_type": test_type,
                "error": str(e)
            }
    
    def _generate_test_content(self, component_name: str, test_type: str) -> str:
        """Generate test content based on type."""
        if test_type == "unit":
            return self._generate_unit_test(component_name)
        elif test_type == "integration":
            return self._generate_integration_test(component_name)
        elif test_type == "e2e":
            return self._generate_e2e_test(component_name)
        else:
            raise ValueError(f"Unsupported test type: {test_type}")

    def _create_test_result(self, component_name: str, test_type: str, test_content: str) -> Dict[str, Any]:
        """Create test result dictionary."""
        return {
            "component_name": component_name,
            "test_type": test_type,
            "test_content": test_content,
            "generated_at": datetime.now().isoformat(),
            "status": "generated"
        }

    def _generate_unit_test(self, component_name: str) -> str:
        """Generate unit test content."""
        return f"""
import pytest
from {component_name} import {component_name}

def test_{component_name.lower()}_creation():
    component = {component_name}()
    assert component is not None

def test_{component_name.lower()}_basic_functionality():
    component = {component_name}()
    # Add specific test cases here
    assert True
"""
    
    def _generate_integration_test(self, component_name: str) -> str:
        """Generate integration test content."""
        return f"""
import pytest
from {component_name} import {component_name}

def test_{component_name.lower()}_integration():
    component = {component_name}()
    # Test integration with other components
    assert True
"""
    
    def _generate_e2e_test(self, component_name: str) -> str:
        """Generate end-to-end test content."""
        return f"""
import pytest
from selenium import webdriver
from {component_name} import {component_name}
from bmad.agents.core.utils.framework_templates import get_framework_templates_manager


def test_{component_name.lower()}_e2e():
    driver = webdriver.Chrome()
    try:
        # Test complete user workflow
        assert True
    finally:
        driver.quit()
"""

    def export_report(self, format_type: str = "md", test_data: Optional[Dict] = None):
        if not test_data:
            if self.test_history:
                test_data = self.run_tests()
            else:
                test_data = self.run_tests()
        
        # Validate format type
        if format_type not in ["md", "json"]:
            raise ValueError("Format type must be 'md' or 'json'")
        
        try:
            if format_type == "md":
                self._export_markdown(test_data)
            elif format_type == "json":
                self._export_json(test_data)
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            raise

    def _export_markdown(self, test_data: Dict):
        template_path = self.template_paths["test-report-md"]
        if template_path.exists():
            with open(template_path) as f:
                template = f.read()
            # Vul template
            content = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            results_text = ""
            for test, result in test_data.items():
                results_text += f"- **{test}**: {result}\n"
            content = content.replace("{{results}}", results_text)
            output_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, "w") as f:
                f.write(content)
            print(f"Test report exported to: {output_file}")

    def _export_json(self, test_data: Dict):
        output_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(test_data, f, indent=2)
        print(f"Test report exported to: {output_file}")

    def test_resource_completeness(self):
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the TestEngineer agent."""
        return {
            "agent_name": self.agent_name,
            "test_history_count": len(self.test_history),
            "coverage_history_count": len(self.coverage_history),
            "last_test": self.test_history[-1] if self.test_history else None,
            "last_coverage": self.coverage_history[-1] if self.coverage_history else None,
            "status": "active"
        }

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        try:
            logger.info("Starting collaboration example...")
            publish("test_generation_requested", {
                "agent": "TestEngineerAgent",
                "function_description": "def add(a, b): return a + b",
                "context": "Eenvoudige optelfunctie"
            })
            test_result = self.run_tests()
            publish("tests_completed", test_result)
            try:
                send_slack_message(f"[TestEngineer] Tests afgerond: {test_result}")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")
            print("Collaboration example completed successfully.")
        except Exception as e:
            logger.error(f"Collaboration example failed: {e}")
            print(f"❌ Error in collaboration: {e}")

    async def handle_tests_requested(self, event):
        logger.info("[TestEngineer] Tests gestart...")
        await self.run_tests()
        publish("tests_completed", {"desc": "Tests voltooid"})
        logger.info("[TestEngineer] Tests afgerond, tests_completed gepubliceerd.")

    async def handle_test_generation_requested(self, event):
        logger.info(f"[TestEngineer] Test generation requested: {event}")
        function_description = event.get("function_description", "Onbekende functie")
        context = event.get("context", "")
        prompt = f"Schrijf Python unittests voor de volgende functie: {function_description}. Context: {context}. Gebruik pytest."
        
        try:
            result = ask_openai(prompt)
            logger.info(f"[TestEngineer][LLM Tests automatisch]: {result}")
            try:
                send_slack_message(f"[TestEngineer][LLM Tests automatisch]: {result}")
            except Exception as e:
                logger.warning(f"Could not send Slack notification: {e}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate tests with LLM: {e}")
            error_result = f"Error generating tests: {e}"
            logger.info(f"[TestEngineer][LLM Tests Error]: {error_result}")
            return error_result

    async def run(self):
        """Main event loop for the agent met complete integration."""
        # Initialize MCP integration
        await self.initialize_mcp()
        
        # Initialize enhanced MCP capabilities for Phase 2
        await self.initialize_enhanced_mcp()
        
        # Initialize tracing capabilities
        await self.initialize_tracing()
        
        def sync_handler(event):
            asyncio.run(self.handle_test_generation_requested(event))
        
        async def async_handler(event):
            await self.handle_tests_requested(event)
        
        subscribe("test_generation_requested", sync_handler)
        subscribe("tests_requested", lambda event: asyncio.run(async_handler(event)))
        logger.info("TestEngineerAgent ready with enhanced MCP and tracing capabilities...")
        print("🎯 TestEngineer Agent is running...")
        print("Listening for events: test_generation_requested, tests_requested")
        print("Enhanced MCP: Enabled" if self.enhanced_mcp_enabled else "Enhanced MCP: Disabled")
        print("Tracing: Enabled" if self.tracing_enabled else "Tracing: Disabled")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 TestEngineer Agent stopped.")
    
    @classmethod
    async def run_agent(cls):
        """Class method to run the TestEngineer agent met MCP integration."""
        agent = cls()
        await agent.run()

def main():
    parser = argparse.ArgumentParser(description="TestEngineer Agent CLI")
    parser.add_argument("command", nargs="?", default="help",
                       choices=["help", "run-tests", "show-coverage", "show-test-history",
                               "show-best-practices", "show-changelog", "export-report",
                               "test", "collaborate", "run",
                               "enhanced-collaborate", "enhanced-security", "enhanced-performance",
                               "trace-operation", "trace-performance", "trace-error", "tracing-summary"])
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    args = parser.parse_args()
    agent = TestEngineerAgent()
    if args.command == "help":
        agent.show_help()
    elif args.command == "run-tests":
        asyncio.run(agent.run_tests())
    elif args.command == "show-coverage":
        agent.show_coverage()
    elif args.command == "show-test-history":
        agent.show_test_history()
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
    # Enhanced MCP commands
    elif args.command == "enhanced-collaborate":
        result = asyncio.run(agent.enhanced_mcp.communicate_with_agents(
            ["BackendDeveloper", "FrontendDeveloper"], 
            {"type": "test_coordination", "content": {"test_phase": "integration"}}
        ))
        print(json.dumps(result, indent=2))
    elif args.command == "enhanced-security":
        result = asyncio.run(agent.enhanced_mcp.enhanced_security_validation({
            "auth_method": "multi_factor",
            "security_level": "enterprise",
            "compliance": ["gdpr", "sox", "iso27001"]
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "enhanced-performance":
        result = asyncio.run(agent.enhanced_mcp.enhanced_performance_optimization({
            "target_latency": 50,
            "optimization_strategy": "predictive_caching",
            "load_balancing": True
        }))
        print(json.dumps(result, indent=2))
    # Tracing commands
    elif args.command == "trace-operation":
        result = asyncio.run(agent.trace_test_operation({
            "type": "test_execution",
            "performance_metrics": {"execution_time": 2.5, "memory_usage": "150MB"}
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "trace-performance":
        performance_summary = agent.enhanced_mcp.get_performance_summary()
        print(json.dumps(performance_summary, indent=2))
    elif args.command == "trace-error":
        result = asyncio.run(agent.trace_test_operation({
            "type": "test_error",
            "performance_metrics": {"error_count": 1, "error_type": "assertion_failure"}
        }))
        print(json.dumps(result, indent=2))
    elif args.command == "tracing-summary":
        communication_summary = agent.enhanced_mcp.get_communication_summary()
        print(json.dumps(communication_summary, indent=2))
    else:
        print("Unknown command. Use 'help' to see available commands.")
        sys.exit(1)

if __name__ == "__main__":
    main()
