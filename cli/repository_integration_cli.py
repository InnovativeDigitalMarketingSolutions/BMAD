#!/usr/bin/env python3
"""
BMAD Repository Integration CLI

Dit CLI tool demonstreert en test alle nieuwe repository integraties:
- OpenRouter voor multi-LLM routing
- OpenTelemetry voor observability
- OPA voor policy enforcement
- Prefect voor CI/CD workflows
"""

import asyncio
import argparse
import logging
from typing import Dict, Any

# Import BMAD modules
from bmad.agents.core.openrouter_client import (
    OpenRouterClient
)
from bmad.agents.core.opentelemetry_tracing import (
    initialize_tracing, TracingConfig, TraceLevel, ExporterType
)
from bmad.agents.core.opa_policy_engine import (
    initialize_policy_engine, PolicyRequest
)
from bmad.agents.core.prefect_workflow import (
    create_prefect_orchestrator, PrefectWorkflowConfig, WorkflowType, DeploymentEnvironment
)
from bmad.agents.core.langgraph_workflow import (
    create_workflow_orchestrator, WorkflowTask, WorkflowDefinition
)

logger = logging.getLogger(__name__)

class RepositoryIntegrationCLI:
    """CLI voor het testen van repository integraties."""
    
    def __init__(self):
        self.openrouter_client = None
        self.tracer = None
        self.policy_engine = None
        self.prefect_orchestrator = None
        self.langgraph_orchestrator = None
    
    async def initialize_components(self, config: Dict[str, Any]):
        """Initialize all integration components."""
        logger.info("Initializing repository integration components...")
        
        # Initialize OpenRouter client
        if config.get("openrouter_api_key"):
            self.openrouter_client = OpenRouterClient(config["openrouter_api_key"])
            logger.info("✅ OpenRouter client geïnitialiseerd")
        
        # Initialize OpenTelemetry tracing
        tracing_config = TracingConfig(
            service_name="bmad-repository-integration",
            environment=config.get("environment", "development"),
            trace_level=TraceLevel.DETAILED,
            exporters=[ExporterType.CONSOLE, ExporterType.PROMETHEUS],
            prometheus_port=config.get("prometheus_port", 8000)
        )
        self.tracer = initialize_tracing(tracing_config)
        logger.info("✅ OpenTelemetry tracing geïnitialiseerd")
        
        # Initialize OPA policy engine
        opa_url = config.get("opa_url", "http://localhost:8181")
        self.policy_engine = initialize_policy_engine(opa_url)
        logger.info("✅ OPA policy engine geïnitialiseerd")
        
        # Initialize Prefect orchestrator
        self.prefect_orchestrator = create_prefect_orchestrator()
        logger.info("✅ Prefect orchestrator geïnitialiseerd")
        
        # Initialize LangGraph orchestrator
        self.langgraph_orchestrator = create_workflow_orchestrator()
        logger.info("✅ LangGraph orchestrator geïnitialiseerd")
    
    async def test_openrouter_integration(self):
        """Test OpenRouter multi-LLM integration."""
        if not self.openrouter_client:
            logger.warning("OpenRouter client niet geïnitialiseerd")
            return
        
        logger.info("🧪 Testing OpenRouter integration...")
        
        test_prompts = [
            "Explain the concept of multi-agent systems in software development.",
            "What are the benefits of using OpenTelemetry for observability?",
            "How does policy-based access control improve system security?"
        ]
        
        strategies = ["development", "production", "testing"]
        
        for i, prompt in enumerate(test_prompts):
            strategy = strategies[i % len(strategies)]
            logger.info(f"Testing strategy: {strategy}")
            
            try:
                with self.tracer.trace_agent_execution("OpenRouter", "generate_response") as span:
                    response = await self.openrouter_client.generate_response(
                        prompt=prompt,
                        strategy_name=strategy,
                        context={"test_id": f"test_{i+1}"}
                    )
                    
                    span.set_attribute("strategy", strategy)
                    span.set_attribute("tokens_used", response.tokens_used)
                    span.set_attribute("cost", response.cost)
                    
                    logger.info(f"✅ Response from {response.provider}/{response.model}:")
                    logger.info(f"   Content: {response.content[:100]}...")
                    logger.info(f"   Tokens: {response.tokens_used}")
                    logger.info(f"   Cost: ${response.cost:.4f}")
                    logger.info(f"   Latency: {response.latency:.2f}s")
                    logger.info(f"   Confidence: {response.confidence_score:.2f}")
                    
            except Exception as e:
                logger.error(f"❌ OpenRouter test failed: {e}")
    
    async def test_opentelemetry_integration(self):
        """Test OpenTelemetry tracing and metrics."""
        if not self.tracer:
            logger.warning("OpenTelemetry tracer niet geïnitialiseerd")
            return
        
        logger.info("🧪 Testing OpenTelemetry integration...")
        
        # Test agent execution tracing
        agents = ["ProductOwner", "Architect", "FullstackDeveloper", "TestEngineer"]
        
        for agent in agents:
            try:
                with self.tracer.trace_agent_execution(agent, "test_task", "test_workflow") as span:
                    # Simulate agent work
                    await asyncio.sleep(0.1)
                    
                    # Add custom events and attributes
                    self.tracer.add_span_event(span, "agent_started", {"agent": agent})
                    self.tracer.add_span_attribute(span, "test_mode", True)
                    
                    # Simulate some work
                    await asyncio.sleep(0.2)
                    
                    self.tracer.add_span_event(span, "agent_completed", {"result": "success"})
                    
                    logger.info(f"✅ Traced agent execution: {agent}")
                    
            except Exception as e:
                logger.error(f"❌ OpenTelemetry test failed for {agent}: {e}")
        
        # Test workflow tracing
        try:
            with self.tracer.trace_workflow_execution("test_workflow", "workflow_123") as span:
                await asyncio.sleep(0.3)
                self.tracer.add_span_event(span, "workflow_step", {"step": "integration_test"})
                logger.info("✅ Traced workflow execution")
                
        except Exception as e:
            logger.error(f"❌ Workflow tracing test failed: {e}")
        
        # Test LLM call tracing
        try:
            self.tracer.trace_llm_call(
                provider="openai",
                model="gpt-4o-mini",
                prompt_tokens=100,
                completion_tokens=50,
                status="success"
            )
            logger.info("✅ Traced LLM call")
            
        except Exception as e:
            logger.error(f"❌ LLM tracing test failed: {e}")
    
    async def test_opa_policy_integration(self):
        """Test OPA policy enforcement."""
        if not self.policy_engine:
            logger.warning("OPA policy engine niet geïnitialiseerd")
            return
        
        logger.info("🧪 Testing OPA policy integration...")
        
        # Test cases
        test_cases = [
            {
                "subject": "ProductOwner",
                "action": "create_user_story",
                "resource": "backlog",
                "expected": True
            },
            {
                "subject": "ProductOwner",
                "action": "deploy_application",
                "resource": "production",
                "expected": False
            },
            {
                "subject": "FullstackDeveloper",
                "action": "implement_feature",
                "resource": "codebase",
                "expected": True
            },
            {
                "subject": "TestEngineer",
                "action": "run_tests",
                "resource": "test_suite",
                "expected": True
            },
            {
                "subject": "SecurityDeveloper",
                "action": "security_scan",
                "resource": "codebase",
                "expected": True
            }
        ]
        
        for test_case in test_cases:
            try:
                request = PolicyRequest(
                    subject=test_case["subject"],
                    action=test_case["action"],
                    resource=test_case["resource"],
                    context={"test_mode": True}
                )
                
                response = await self.policy_engine.evaluate_policy(request)
                
                if response.allowed == test_case["expected"]:
                    logger.info(f"✅ Policy test passed: {test_case['subject']} -> {test_case['action']}")
                else:
                    logger.warning(f"⚠️ Policy test unexpected: {test_case['subject']} -> {test_case['action']} (expected: {test_case['expected']}, got: {response.allowed})")
                
                logger.info(f"   Decision: {response.decision.value}")
                logger.info(f"   Reason: {response.reason}")
                
            except Exception as e:
                logger.error(f"❌ Policy test failed: {e}")
        
        # Test workflow permissions
        try:
            response = await self.policy_engine.check_workflow_permission(
                agent_name="Architect",
                workflow_id="workflow_123",
                action="workflow_modify",
                workflow_context={"workflow_status": "running"}
            )
            
            logger.info(f"✅ Workflow permission test: {response.decision.value}")
            
        except Exception as e:
            logger.error(f"❌ Workflow permission test failed: {e}")
    
    async def test_prefect_integration(self):
        """Test Prefect CI/CD workflow integration."""
        if not self.prefect_orchestrator:
            logger.warning("Prefect orchestrator niet geïnitialiseerd")
            return
        
        logger.info("🧪 Testing Prefect integration...")
        
        # Create test workflow config
        test_config = PrefectWorkflowConfig(
            name="integration_test_workflow",
            description="Test workflow for repository integration",
            workflow_type=WorkflowType.DEVELOPMENT,
            environment=DeploymentEnvironment.DEVELOPMENT,
            timeout_minutes=10,
            tags=["integration-test", "bmad"]
        )
        
        try:
            # Register workflow config
            self.prefect_orchestrator.register_workflow_config(test_config)
            logger.info("✅ Prefect workflow config geregistreerd")
            
            # Create deployment
            deployment_id = self.prefect_orchestrator.create_deployment(
                workflow_name="integration_test_workflow",
                agent_tasks=[]
            )
            
            logger.info(f"✅ Prefect deployment created: {deployment_id}")
            
        except Exception as e:
            logger.error(f"❌ Prefect test failed: {e}")
    
    async def test_langgraph_integration(self):
        """Test LangGraph workflow integration."""
        if not self.langgraph_orchestrator:
            logger.warning("LangGraph orchestrator niet geïnitialiseerd")
            return
        
        logger.info("🧪 Testing LangGraph integration...")
        
        # Create test workflow
        tasks = [
            WorkflowTask(
                id="test_task_1",
                name="Test Task 1",
                agent="ProductOwner",
                command="create_user_story"
            ),
            WorkflowTask(
                id="test_task_2",
                name="Test Task 2",
                agent="Architect",
                command="design_system",
                dependencies=["test_task_1"]
            )
        ]
        
        workflow_def = WorkflowDefinition(
            name="integration_test_workflow",
            description="Test workflow for repository integration",
            tasks=tasks,
            max_parallel=2,
            timeout=300
        )
        
        try:
            # Register workflow
            self.langgraph_orchestrator.register_workflow(workflow_def)
            logger.info("✅ LangGraph workflow geregistreerd")
            
            # Start workflow
            workflow_id = self.langgraph_orchestrator.start_workflow(
                "integration_test_workflow",
                {"test_mode": True, "integration_test": True}
            )
            
            logger.info(f"✅ LangGraph workflow started: {workflow_id}")
            
            # Check status
            await asyncio.sleep(1)
            status = self.langgraph_orchestrator.get_workflow_status(workflow_id)
            if status:
                logger.info(f"✅ Workflow status: {status.get('status', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ LangGraph test failed: {e}")
    
    async def run_cost_analysis(self):
        """Run cost analysis for OpenRouter usage."""
        if not self.openrouter_client:
            logger.warning("OpenRouter client niet geïnitialiseerd")
            return
        
        logger.info("💰 Running cost analysis...")
        
        try:
            # Get provider stats
            stats = self.openrouter_client.get_provider_stats()
            logger.info("Provider Statistics:")
            for provider, stat in stats.items():
                logger.info(f"  {provider}:")
                logger.info(f"    Total calls: {stat['total_calls']}")
                logger.info(f"    Total tokens: {stat['total_tokens']}")
                logger.info(f"    Total cost: ${stat['total_cost']:.4f}")
                logger.info(f"    Avg latency: {stat['avg_latency']:.2f}s")
            
            # Get cost analysis
            cost_analysis = self.openrouter_client.get_cost_analysis(days=1)
            logger.info("Cost Analysis (last 24 hours):")
            logger.info(f"  Total cost: ${cost_analysis['total_cost']:.4f}")
            logger.info(f"  Total tokens: {cost_analysis['total_tokens']}")
            logger.info(f"  Provider breakdown:")
            for provider, breakdown in cost_analysis['provider_breakdown'].items():
                logger.info(f"    {provider}: ${breakdown['cost']:.4f} ({breakdown['calls']} calls)")
                
        except Exception as e:
            logger.error(f"❌ Cost analysis failed: {e}")
    
    async def export_policies(self, output_file: str):
        """Export OPA policies to file."""
        if not self.policy_engine:
            logger.warning("OPA policy engine niet geïnitialiseerd")
            return
        
        try:
            policies_json = self.policy_engine.export_policies("json")
            
            with open(output_file, 'w') as f:
                f.write(policies_json)
            
            logger.info(f"✅ Policies exported to: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Policy export failed: {e}")
    
    async def run_all_tests(self, config: Dict[str, Any]):
        """Run all integration tests."""
        logger.info("🚀 Starting repository integration tests...")
        
        # Initialize components
        await self.initialize_components(config)
        
        # Run tests
        await self.test_openrouter_integration()
        await self.test_opentelemetry_integration()
        await self.test_opa_policy_integration()
        await self.test_prefect_integration()
        await self.test_langgraph_integration()
        
        # Run analysis
        await self.run_cost_analysis()
        
        logger.info("🎉 All repository integration tests completed!")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="BMAD Repository Integration CLI")
    parser.add_argument("--openrouter-api-key", help="OpenRouter API key")
    parser.add_argument("--opa-url", default="http://localhost:8181", help="OPA server URL")
    parser.add_argument("--environment", default="development", help="Environment")
    parser.add_argument("--prometheus-port", type=int, default=8000, help="Prometheus port")
    parser.add_argument("--test", choices=["openrouter", "opentelemetry", "opa", "prefect", "langgraph", "all"], 
                       default="all", help="Specific test to run")
    parser.add_argument("--export-policies", help="Export policies to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    config = {
        "openrouter_api_key": args.openrouter_api_key or "test_api_key_for_integration_tests",
        "opa_url": args.opa_url,
        "environment": args.environment,
        "prometheus_port": args.prometheus_port
    }
    
    # Create CLI instance
    cli = RepositoryIntegrationCLI()
    
    async def run():
        if args.export_policies:
            await cli.initialize_components(config)
            await cli.export_policies(args.export_policies)
        elif args.test == "all":
            await cli.run_all_tests(config)
        elif args.test == "openrouter":
            await cli.initialize_components(config)
            await cli.test_openrouter_integration()
        elif args.test == "opentelemetry":
            await cli.initialize_components(config)
            await cli.test_opentelemetry_integration()
        elif args.test == "opa":
            await cli.initialize_components(config)
            await cli.test_opa_policy_integration()
        elif args.test == "prefect":
            await cli.initialize_components(config)
            await cli.test_prefect_integration()
        elif args.test == "langgraph":
            await cli.initialize_components(config)
            await cli.test_langgraph_integration()
    
    # Run async main
    asyncio.run(run())

if __name__ == "__main__":
    main() 