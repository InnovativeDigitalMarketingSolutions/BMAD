"""
BMAD Integrated Workflow Orchestrator

Dit module integreert alle nieuwe repository integraties (LangGraph, OpenRouter, 
OpenTelemetry, OPA, Prefect) met de bestaande BMAD agent workflows voor een
complete enterprise-ready multi-agent orchestration systeem.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing BMAD core modules
from .message_bus import publish, subscribe
from .confidence_scoring import confidence_scoring
from .advanced_workflow import WorkflowTask, WorkflowDefinition, WorkflowStatus, TaskStatus

# Import new repository integrations
from .langgraph_workflow import LangGraphWorkflowOrchestrator
from .openrouter_client import OpenRouterClient, LLMConfig, RoutingStrategy
from .opentelemetry_tracing import BMADTracer, TracingConfig, TraceLevel
from .opa_policy_engine import OPAPolicyEngine, PolicyRule, PolicyRequest
from .prefect_workflow import PrefectWorkflowOrchestrator, PrefectWorkflowConfig

logger = logging.getLogger(__name__)

class IntegrationLevel(Enum):
    """Integration levels for different components."""
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL = "full"

@dataclass
class AgentWorkflowConfig:
    """Configuration for agent workflow integration."""
    agent_name: str
    integration_level: IntegrationLevel = IntegrationLevel.ENHANCED
    enable_tracing: bool = True
    enable_policy_enforcement: bool = True
    enable_cost_tracking: bool = True
    enable_workflow_orchestration: bool = True
    llm_provider: str = "openrouter"
    policy_rules: List[str] = field(default_factory=list)
    workflow_timeout: int = 3600
    max_retries: int = 3

@dataclass
class IntegratedWorkflowResult:
    """Result of an integrated workflow execution."""
    workflow_id: str
    status: WorkflowStatus
    agent_results: Dict[str, Any]
    tracing_data: Optional[Dict[str, Any]] = None
    policy_decisions: Optional[List[Dict[str, Any]]] = None
    cost_analysis: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    execution_time: Optional[float] = None

class IntegratedWorkflowOrchestrator:
    """
    Integrated workflow orchestrator that combines all repository integrations
    with existing BMAD agent workflows.
    """
    
    def __init__(self):
        # Initialize all integration components
        self._initialize_integrations()
        
        # Workflow state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.agent_configs: Dict[str, AgentWorkflowConfig] = {}
        
        # Register default agent configurations
        self._register_default_agent_configs()
        
        # Register default workflows
        self._register_default_workflows()
        
        logger.info("Integrated Workflow Orchestrator geïnitialiseerd")
    
    def _initialize_integrations(self):
        """Initialize all repository integrations."""
        try:
            # Initialize OpenRouter client
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_api_key:
                self.openrouter_client = OpenRouterClient(
                    api_key=openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                logger.info("OpenRouter client geïnitialiseerd")
            else:
                self.openrouter_client = None
                logger.warning("OpenRouter API key niet gevonden, LLM routing uitgeschakeld")
            
            # Initialize OpenTelemetry tracer
            tracing_config = TracingConfig(
                service_name=os.getenv("OTEL_SERVICE_NAME", "bmad-agents"),
                environment=os.getenv("OTEL_ENVIRONMENT", "development")
            )
            self.tracer = BMADTracer(config=tracing_config)
            logger.info("OpenTelemetry tracer geïnitialiseerd")
            
            # Initialize OPA policy engine
            opa_url = os.getenv("OPA_URL", "http://localhost:8181")
            self.policy_engine = OPAPolicyEngine(opa_url=opa_url)
            logger.info("OPA policy engine geïnitialiseerd")
            
            # Initialize LangGraph workflow orchestrator
            self.langgraph_orchestrator = LangGraphWorkflowOrchestrator()
            logger.info("LangGraph workflow orchestrator geïnitialiseerd")
            
            # Initialize Prefect workflow orchestrator
            self.prefect_orchestrator = PrefectWorkflowOrchestrator()
            logger.info("Prefect workflow orchestrator geïnitialiseerd")
            
        except Exception as e:
            logger.error(f"Fout bij initialiseren van integraties: {e}")
            raise
    
    def _register_default_agent_configs(self):
        """Register default configurations for all BMAD agents."""
        default_configs = {
            "product-owner": AgentWorkflowConfig(
                agent_name="product-owner",
                integration_level=IntegrationLevel.FULL,
                policy_rules=["access_control", "resource_limits", "workflow_policies"]
            ),
            "scrummaster": AgentWorkflowConfig(
                agent_name="scrummaster",
                integration_level=IntegrationLevel.ENHANCED,
                policy_rules=["access_control", "workflow_policies"]
            ),
            "architect": AgentWorkflowConfig(
                agent_name="architect",
                integration_level=IntegrationLevel.FULL,
                policy_rules=["access_control", "security_policies", "resource_limits"]
            ),
            "fullstack": AgentWorkflowConfig(
                agent_name="fullstack",
                integration_level=IntegrationLevel.ENHANCED,
                policy_rules=["access_control", "resource_limits"]
            ),
            "backend": AgentWorkflowConfig(
                agent_name="backend",
                integration_level=IntegrationLevel.ENHANCED,
                policy_rules=["access_control", "security_policies"]
            ),
            "frontend": AgentWorkflowConfig(
                agent_name="frontend",
                integration_level=IntegrationLevel.ENHANCED,
                policy_rules=["access_control", "resource_limits"]
            ),
            "ai": AgentWorkflowConfig(
                agent_name="ai",
                integration_level=IntegrationLevel.FULL,
                policy_rules=["access_control", "security_policies", "ai_policies"]
            ),
            "test": AgentWorkflowConfig(
                agent_name="test",
                integration_level=IntegrationLevel.ENHANCED,
                policy_rules=["access_control", "quality_policies"]
            ),
            "security": AgentWorkflowConfig(
                agent_name="security",
                integration_level=IntegrationLevel.FULL,
                policy_rules=["access_control", "security_policies", "compliance_policies"]
            ),
            "devops": AgentWorkflowConfig(
                agent_name="devops",
                integration_level=IntegrationLevel.FULL,
                policy_rules=["access_control", "infrastructure_policies", "deployment_policies"]
            )
        }
        
        for agent_name, config in default_configs.items():
            self.agent_configs[agent_name] = config
        
        logger.info(f"Default agent configuraties geregistreerd voor {len(default_configs)} agents")
    
    def _register_default_workflows(self):
        """Register default BMAD workflows."""
        # Product Development Workflow
        product_dev_workflow = WorkflowDefinition(
            name="product-development",
            description="Complete product development workflow van user story tot deployment",
            tasks=[
                WorkflowTask(
                    id="create-story",
                    name="Create User Story",
                    agent="product-owner",
                    command="create-story",
                    dependencies=[],
                    timeout=300
                ),
                WorkflowTask(
                    id="design-system",
                    name="Design System Architecture",
                    agent="architect",
                    command="design-system",
                    dependencies=["create-story"],
                    timeout=600
                ),
                WorkflowTask(
                    id="build-backend",
                    name="Build Backend API",
                    agent="backend",
                    command="build-api",
                    dependencies=["design-system"],
                    timeout=900
                ),
                WorkflowTask(
                    id="build-frontend",
                    name="Build Frontend Components",
                    agent="frontend",
                    command="build-component",
                    dependencies=["design-system"],
                    timeout=900
                ),
                WorkflowTask(
                    id="run-tests",
                    name="Run Tests",
                    agent="test",
                    command="run-tests",
                    dependencies=["build-backend", "build-frontend"],
                    timeout=600
                ),
                WorkflowTask(
                    id="security-scan",
                    name="Security Scan",
                    agent="security",
                    command="security-scan",
                    dependencies=["run-tests"],
                    timeout=300
                ),
                WorkflowTask(
                    id="deploy",
                    name="Deploy to Production",
                    agent="devops",
                    command="deploy",
                    dependencies=["security-scan"],
                    timeout=600
                )
            ],
            max_parallel=3,
            timeout=3600
        )
        
        self.register_workflow(product_dev_workflow)
        
        # AI Development Workflow
        ai_dev_workflow = WorkflowDefinition(
            name="ai-development",
            description="AI/ML development workflow met model training en deployment",
            tasks=[
                WorkflowTask(
                    id="design-ai",
                    name="Design AI Architecture",
                    agent="architect",
                    command="design-ai-system",
                    dependencies=[],
                    timeout=600
                ),
                WorkflowTask(
                    id="build-pipeline",
                    name="Build AI Pipeline",
                    agent="ai",
                    command="build-pipeline",
                    dependencies=["design-ai"],
                    timeout=900
                ),
                WorkflowTask(
                    id="train-model",
                    name="Train AI Model",
                    agent="ai",
                    command="train-model",
                    dependencies=["build-pipeline"],
                    timeout=1800
                ),
                WorkflowTask(
                    id="test-ai",
                    name="Test AI Model",
                    agent="test",
                    command="test-ai-model",
                    dependencies=["train-model"],
                    timeout=600
                ),
                WorkflowTask(
                    id="deploy-ai",
                    name="Deploy AI Model",
                    agent="ai",
                    command="deploy-model",
                    dependencies=["test-ai"],
                    timeout=900
                )
            ],
            max_parallel=2,
            timeout=7200
        )
        
        self.register_workflow(ai_dev_workflow)
        
        logger.info("Default workflows geregistreerd")
    
    def register_workflow(self, workflow_def: WorkflowDefinition):
        """Register a workflow definition."""
        self.workflow_definitions[workflow_def.name] = workflow_def
        logger.info(f"Workflow '{workflow_def.name}' geregistreerd met {len(workflow_def.tasks)} taken")
    
    def register_agent_config(self, agent_name: str, config: AgentWorkflowConfig):
        """Register configuration for a specific agent."""
        self.agent_configs[agent_name] = config
        logger.info(f"Configuratie geregistreerd voor agent: {agent_name}")
    
    async def execute_integrated_workflow(
        self, 
        workflow_name: str, 
        context: Dict[str, Any] = None,
        integration_level: IntegrationLevel = IntegrationLevel.ENHANCED
    ) -> IntegratedWorkflowResult:
        """
        Execute a workflow with full integration of all repository components.
        """
        if workflow_name not in self.workflow_definitions:
            raise ValueError(f"Workflow '{workflow_name}' niet gevonden")
        
        workflow_def = self.workflow_definitions[workflow_name]
        workflow_id = f"{workflow_name}_{int(time.time())}"
        
        # Initialize result tracking
        result = IntegratedWorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            agent_results={},
            tracing_data={},
            policy_decisions=[],
            cost_analysis={},
            performance_metrics={}
        )
        
        start_time = time.time()
        
        try:
            # Start tracing
            if integration_level in [IntegrationLevel.ENHANCED, IntegrationLevel.FULL]:
                with self.tracer.start_span(f"workflow.{workflow_name}", level=TraceLevel.INFO) as span:
                    span.set_attribute("workflow.id", workflow_id)
                    span.set_attribute("workflow.name", workflow_name)
                    span.set_attribute("integration.level", integration_level.value)
                    
                    # Execute workflow with tracing
                    result = await self._execute_workflow_with_integrations(
                        workflow_def, workflow_id, context, integration_level, span
                    )
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            result.status = WorkflowStatus.FAILED
            result.error_details = str(e)
        finally:
            result.execution_time = time.time() - start_time
            logger.info(f"Workflow '{workflow_name}' voltooid in {result.execution_time:.2f}s")
        
        return result
    
    async def _execute_workflow_with_integrations(
        self,
        workflow_def: WorkflowDefinition,
        workflow_id: str,
        context: Dict[str, Any],
        integration_level: IntegrationLevel,
        span
    ) -> IntegratedWorkflowResult:
        """Execute workflow with all integrations enabled."""
        
        # Initialize result
        result = IntegratedWorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            agent_results={},
            tracing_data={},
            policy_decisions=[],
            cost_analysis={},
            performance_metrics={}
        )
        
        # Policy enforcement
        if integration_level in [IntegrationLevel.ENHANCED, IntegrationLevel.FULL]:
            policy_result = await self._enforce_workflow_policies(workflow_def, context)
            result.policy_decisions.append(policy_result)
            
            if not policy_result.get("allow", True):
                result.status = WorkflowStatus.FAILED
                result.error_details = f"Policy violation: {policy_result.get('reason', 'Unknown')}"
                return result
        
        # Execute tasks with integrations
        for task in workflow_def.tasks:
            task_result = await self._execute_task_with_integrations(
                task, workflow_id, context, integration_level, span
            )
            
            result.agent_results[task.id] = task_result
            
            if task_result.get("status") == "failed":
                result.status = WorkflowStatus.FAILED
                result.error_details = task_result.get("error", "Task execution failed")
                break
        
        if result.status == WorkflowStatus.RUNNING:
            result.status = WorkflowStatus.COMPLETED
        
        return result
    
    async def _execute_task_with_integrations(
        self,
        task: WorkflowTask,
        workflow_id: str,
        context: Dict[str, Any],
        integration_level: IntegrationLevel,
        parent_span
    ) -> Dict[str, Any]:
        """Execute a single task with all integrations enabled."""
        
        agent_config = self.agent_configs.get(task.agent, AgentWorkflowConfig(agent_name=task.agent))
        
        with self.tracer.start_span(f"task.{task.id}", parent=parent_span) as span:
            span.set_attribute("task.id", task.id)
            span.set_attribute("task.agent", task.agent)
            span.set_attribute("task.command", task.command)
            
            task_result = {
                "task_id": task.id,
                "agent": task.agent,
                "command": task.command,
                "status": "pending",
                "start_time": time.time(),
                "integrations": {}
            }
            
            try:
                # Policy enforcement for task
                if agent_config.enable_policy_enforcement:
                    policy_result = await self._enforce_task_policies(task, context)
                    task_result["integrations"]["policy"] = policy_result
                    
                    if not policy_result.get("allow", True):
                        task_result["status"] = "failed"
                        task_result["error"] = f"Policy violation: {policy_result.get('reason', 'Unknown')}"
                        return task_result
                
                # Execute task with LLM integration if available
                if self.openrouter_client and agent_config.integration_level in [IntegrationLevel.ENHANCED, IntegrationLevel.FULL]:
                    llm_result = await self._execute_task_with_llm(task, context, span)
                    task_result["integrations"]["llm"] = llm_result
                
                # Execute actual task
                execution_result = await self._execute_agent_task(task, context)
                task_result.update(execution_result)
                
                # Cost tracking
                if agent_config.enable_cost_tracking and self.openrouter_client:
                    cost_result = await self._track_task_costs(task, task_result)
                    task_result["integrations"]["cost"] = cost_result
                
                task_result["status"] = "completed"
                
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                task_result["status"] = "failed"
                task_result["error"] = str(e)
                span.record_exception(e)
            
            task_result["end_time"] = time.time()
            task_result["duration"] = task_result["end_time"] - task_result["start_time"]
            
            return task_result
    
    async def _enforce_workflow_policies(
        self, 
        workflow_def: WorkflowDefinition, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce policies for workflow execution."""
        policy_request = PolicyRequest(
            subject=f"workflow-{workflow_def.name}",
            action="execute",
            resource="workflow",
            context={
                "workflow_name": workflow_def.name,
                "task_count": len(workflow_def.tasks),
                "max_parallel": workflow_def.max_parallel,
                "timeout": workflow_def.timeout,
                **context
            }
        )
        
        return await self.policy_engine.evaluate_policy(policy_request)
    
    async def _enforce_task_policies(
        self, 
        task: WorkflowTask, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce policies for task execution."""
        policy_request = PolicyRequest(
            subject=f"agent-{task.agent}",
            action=task.command,
            resource="task",
            context={
                "task_id": task.id,
                "agent": task.agent,
                "command": task.command,
                "timeout": task.timeout,
                **context
            }
        )
        
        return await self.policy_engine.evaluate_policy(policy_request)
    
    async def _execute_task_with_llm(
        self, 
        task: WorkflowTask, 
        context: Dict[str, Any],
        span
    ) -> Dict[str, Any]:
        """Execute task with LLM assistance via OpenRouter."""
        try:
            # Create LLM config for task
            llm_config = LLMConfig(
                model="openai/gpt-4",
                provider="openai",
                max_tokens=1000,
                temperature=0.1
            )
            
            # Generate task prompt
            prompt = self._generate_task_prompt(task, context)
            
            # Call LLM
            response = await self.openrouter_client.call_llm(
                config=llm_config,
                prompt=prompt,
                context=context
            )
            
            span.set_attribute("llm.provider", response.provider)
            span.set_attribute("llm.model", response.model)
            span.set_attribute("llm.tokens_used", response.tokens_used)
            span.set_attribute("llm.cost", response.cost)
            
            return {
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency": response.latency,
                "response": response.content
            }
            
        except Exception as e:
            logger.error(f"LLM execution failed: {e}")
            return {"error": str(e)}
    
    def _generate_task_prompt(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Generate a prompt for task execution."""
        return f"""
        Je bent een {task.agent} agent die de taak '{task.command}' moet uitvoeren.
        
        Taak details:
        - ID: {task.id}
        - Agent: {task.agent}
        - Commando: {task.command}
        - Timeout: {task.timeout}s
        
        Context: {json.dumps(context, indent=2)}
        
        Voer deze taak uit en geef een gestructureerd antwoord terug.
        """
    
    async def _execute_agent_task(
        self, 
        task: WorkflowTask, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual agent task."""
        # This would integrate with the existing BMAD agent system
        # For now, we'll simulate the execution
        
        # Simulate task execution
        await asyncio.sleep(1)  # Simulate work
        
        return {
            "output": f"Task {task.id} executed successfully",
            "data": {
                "task_id": task.id,
                "agent": task.agent,
                "command": task.command
            }
        }
    
    async def _track_task_costs(
        self, 
        task: WorkflowTask, 
        task_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track costs for task execution."""
        llm_data = task_result.get("integrations", {}).get("llm", {})
        
        return {
            "llm_cost": llm_data.get("cost", 0),
            "total_cost": llm_data.get("cost", 0),
            "currency": "USD",
            "task_id": task.id
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow."""
        return self.active_workflows.get(workflow_id)
    
    def list_workflows(self) -> List[str]:
        """List all available workflows."""
        return list(self.workflow_definitions.keys())
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentWorkflowConfig]:
        """Get configuration for a specific agent."""
        return self.agent_configs.get(agent_name)
    
    async def start_langgraph_workflow(self, workflow_name: str, context: Dict[str, Any] = None):
        """Start a LangGraph workflow."""
        return await self.langgraph_orchestrator.start_workflow(workflow_name, context)
    
    async def start_prefect_workflow(self, config: PrefectWorkflowConfig):
        """Start a Prefect workflow."""
        return await self.prefect_orchestrator.create_deployment(config)
    
    def get_tracing_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get tracing data for a workflow."""
        # This would return actual tracing data from OpenTelemetry
        return {"workflow_id": workflow_id, "traces": []}
    
    def get_cost_analysis(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get cost analysis for a workflow."""
        # This would aggregate costs from all tasks
        return {"workflow_id": workflow_id, "total_cost": 0, "breakdown": {}}
    
    def get_performance_metrics(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a workflow."""
        # This would return performance metrics
        return {"workflow_id": workflow_id, "metrics": {}}

# Global orchestrator instance
_orchestrator = None

def get_orchestrator() -> IntegratedWorkflowOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IntegratedWorkflowOrchestrator()
    return _orchestrator 