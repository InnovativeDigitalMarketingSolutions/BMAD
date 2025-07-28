"""
BMAD Prefect Workflow Orchestrator

Dit module biedt CI/CD workflow orchestration voor BMAD agents met Prefect.
Integreert naadloos met LangGraph workflows voor end-to-end development pipelines.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from prefect import flow, task, get_run_logger
from prefect.artifacts import create_markdown_artifact
from prefect.context import get_run_context
from prefect.server.schemas.schedules import CronSchedule
from prefect.deployments import Deployment
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.ai.confidence_scoring import confidence_scoring

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"

class DeploymentEnvironment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class PrefectWorkflowConfig:
    """Configuration for Prefect workflows."""
    name: str
    description: str
    workflow_type: WorkflowType
    environment: DeploymentEnvironment
    schedule: Optional[str] = None  # Cron schedule
    timeout_minutes: int = 60
    retries: int = 3
    retry_delay_seconds: int = 300
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentTaskConfig:
    """Configuration for agent tasks in Prefect workflows."""
    agent_name: str
    task_name: str
    command: str
    timeout_seconds: int = 300
    retries: int = 2
    retry_delay_seconds: int = 60
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

class PrefectWorkflowOrchestrator:
    """
    Prefect-based workflow orchestrator voor CI/CD pipelines.
    """
    
    def __init__(self):
        self.workflow_configs: Dict[str, PrefectWorkflowConfig] = {}
        self.agent_executors: Dict[str, Callable] = {}
        self.deployments: Dict[str, Deployment] = {}
        
        # Register default agent executors
        self._register_default_executors()
        
        # Register event handlers
        self._register_event_handlers()
    
    def register_workflow_config(self, config: PrefectWorkflowConfig):
        """Register a workflow configuration."""
        self.workflow_configs[config.name] = config
        logger.info(f"Workflow config '{config.name}' geregistreerd")
    
    def register_agent_executor(self, agent_name: str, executor: Callable):
        """Register an agent executor."""
        self.agent_executors[agent_name] = executor
        logger.info(f"Agent executor geregistreerd voor: {agent_name}")
    
    def create_deployment(self, workflow_name: str, agent_tasks: List[AgentTaskConfig]) -> str:
        """Create a Prefect deployment for a workflow."""
        if workflow_name not in self.workflow_configs:
            raise ValueError(f"Workflow config '{workflow_name}' niet gevonden")
        
        config = self.workflow_configs[workflow_name]
        
        # Create the flow function
        @flow(
            name=config.name,
            description=config.description,
            retries=config.retries,
            retry_delay_seconds=config.retry_delay_seconds,
            tags=config.tags
        )
        def bmad_workflow(**parameters):
            """BMAD workflow executed by Prefect."""
            return self._execute_workflow(workflow_name, agent_tasks, parameters)
        
        # Store the flow for later deployment
        self.deployments[workflow_name] = {
            "flow": bmad_workflow,
            "config": config,
            "agent_tasks": agent_tasks
        }
        
        logger.info(f"Flow '{config.name}' created for workflow '{workflow_name}'")
        return config.name
    
    def _execute_workflow(self, workflow_name: str, agent_tasks: List[AgentTaskConfig], parameters: Dict[str, Any]):
        """Execute a workflow with agent tasks."""
        logger = get_run_logger()
        context = get_run_context()
        
        logger.info(f"Starting BMAD workflow: {workflow_name}")
        logger.info(f"Parameters: {json.dumps(parameters, indent=2)}")
        
        # Create workflow context
        workflow_context = {
            "workflow_name": workflow_name,
            "run_id": context.flow_run.id,
            "start_time": datetime.now().isoformat(),
            "parameters": parameters,
            "environment": self.workflow_configs[workflow_name].environment.value
        }
        
        # Execute agent tasks
        results = {}
        for task_config in agent_tasks:
            try:
                result = self._execute_agent_task(task_config, workflow_context)
                results[task_config.task_name] = result
                
                # Create artifact for task result
                create_markdown_artifact(
                    key=f"{task_config.task_name}-result",
                    markdown=f"""
# Task Result: {task_config.task_name}

**Agent**: {task_config.agent_name}
**Command**: {task_config.command}
**Status**: ✅ Success
**Output**: {result.get('output', 'No output')}
**Confidence**: {result.get('confidence', 'N/A')}
                    """,
                    description=f"Result from {task_config.agent_name} task"
                )
                
            except Exception as e:
                logger.error(f"Task {task_config.task_name} failed: {e}")
                results[task_config.task_name] = {
                    "error": str(e),
                    "status": "failed"
                }
                
                # Create artifact for error
                create_markdown_artifact(
                    key=f"{task_config.task_name}-error",
                    markdown=f"""
# Task Error: {task_config.task_name}

**Agent**: {task_config.agent_name}
**Command**: {task_config.command}
**Status**: ❌ Failed
**Error**: {str(e)}
                    """,
                    description=f"Error from {task_config.agent_name} task"
                )
        
        # Create final summary artifact
        create_markdown_artifact(
            key=f"{workflow_name}-summary",
            markdown=f"""
# Workflow Summary: {workflow_name}

**Environment**: {workflow_context['environment']}
**Run ID**: {workflow_context['run_id']}

## Task Results:
{chr(10).join([f"- **{task_name}**: {'✅ Success' if result.get('status') != 'failed' else '❌ Failed'}" for task_name, result in results.items()])}
            """,
            description=f"Summary of {workflow_name} workflow execution"
        )
        
        # Calculate success metrics
        total_count = len(results)
        success_count = sum(1 for result in results.values() if result.get('status') != 'failed')
        
        logger.info(f"Workflow {workflow_name} completed. Success: {success_count}/{total_count}")
        
        # Publish workflow completion event
        publish("workflow_completed", {
            "workflow_name": workflow_name,
            "run_id": workflow_context['run_id'],
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "workflow_name": workflow_name,
            "run_id": workflow_context['run_id'],
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "status": "completed" if success_count == total_count else "partial" if success_count > 0 else "failed"
        }
    
    def _execute_agent_task(self, task_config: AgentTaskConfig, workflow_context: Dict[str, Any]):
        """Execute a single agent task."""
        logger = get_run_logger()
        
        logger.info(f"Executing task: {task_config.task_name} with agent: {task_config.agent_name}")
        
        # Find executor for agent
        executor = self.agent_executors.get(task_config.agent_name)
        if not executor:
            raise ValueError(f"Geen executor gevonden voor agent: {task_config.agent_name}")
        
        # Execute task
        result = executor(
            task_name=task_config.task_name,
            command=task_config.command,
            parameters=task_config.parameters,
            context=workflow_context
        )
        
        # Enhance result with confidence scoring
        if isinstance(result, dict) and "output" in result:
            enhanced_result = confidence_scoring.enhance_agent_output(
                output=result["output"],
                agent_name=task_config.agent_name,
                task_type=task_config.command,
                context=workflow_context
            )
            result.update(enhanced_result)
        
        result["status"] = "success"
        result["task_name"] = task_config.task_name
        result["agent_name"] = task_config.agent_name
        
        logger.info(f"Task {task_config.task_name} completed successfully")
        return result
    
    def _register_default_executors(self):
        """Register default agent executors."""
        self.register_agent_executor("ProductOwner", self._execute_product_owner_task)
        self.register_agent_executor("Architect", self._execute_architect_task)
        self.register_agent_executor("FullstackDeveloper", self._execute_fullstack_task)
        self.register_agent_executor("TestEngineer", self._execute_test_task)
        self.register_agent_executor("DevOpsInfra", self._execute_devops_task)
        self.register_agent_executor("SecurityDeveloper", self._execute_security_task)
    
    def _execute_product_owner_task(self, task_name: str, command: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute ProductOwner task."""
        logger = get_run_logger()
        logger.info(f"ProductOwner executing: {command}")
        
        # Simulate task execution
        time.sleep(2)
        
        return {
            "output": f"ProductOwner completed: {command}",
            "agent": "ProductOwner",
            "task_name": task_name,
            "command": command,
            "parameters": parameters
        }
    
    def _execute_architect_task(self, task_name: str, command: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute Architect task."""
        logger = get_run_logger()
        logger.info(f"Architect executing: {command}")
        
        # Simulate task execution
        time.sleep(3)
        
        return {
            "output": f"Architect completed: {command}",
            "agent": "Architect",
            "task_name": task_name,
            "command": command,
            "parameters": parameters
        }
    
    def _execute_fullstack_task(self, task_name: str, command: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute FullstackDeveloper task."""
        logger = get_run_logger()
        logger.info(f"FullstackDeveloper executing: {command}")
        
        # Simulate task execution
        time.sleep(4)
        
        return {
            "output": f"FullstackDeveloper completed: {command}",
            "agent": "FullstackDeveloper",
            "task_name": task_name,
            "command": command,
            "parameters": parameters
        }
    
    def _execute_test_task(self, task_name: str, command: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute TestEngineer task."""
        logger = get_run_logger()
        logger.info(f"TestEngineer executing: {command}")
        
        # Simulate task execution
        time.sleep(3)
        
        return {
            "output": f"TestEngineer completed: {command}",
            "agent": "TestEngineer",
            "task_name": task_name,
            "command": command,
            "parameters": parameters
        }
    
    def _execute_devops_task(self, task_name: str, command: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute DevOpsInfra task."""
        logger = get_run_logger()
        logger.info(f"DevOpsInfra executing: {command}")
        
        # Simulate task execution
        time.sleep(5)
        
        return {
            "output": f"DevOpsInfra completed: {command}",
            "agent": "DevOpsInfra",
            "task_name": task_name,
            "command": command,
            "parameters": parameters
        }
    
    def _execute_security_task(self, task_name: str, command: str, parameters: Dict[str, Any], context: Dict[str, Any]):
        """Execute SecurityDeveloper task."""
        logger = get_run_logger()
        logger.info(f"SecurityDeveloper executing: {command}")
        
        # Simulate task execution
        time.sleep(4)
        
        return {
            "output": f"SecurityDeveloper completed: {command}",
            "agent": "SecurityDeveloper",
            "task_name": task_name,
            "command": command,
            "parameters": parameters
        }
    
    def _register_event_handlers(self):
        """Register event handlers."""
        subscribe("workflow_completed", self._handle_workflow_completion)
        subscribe("deployment_requested", self._handle_deployment_request)
    
    def _handle_workflow_completion(self, event: Dict[str, Any]):
        """Handle workflow completion event."""
        workflow_name = event.get("workflow_name")
        run_id = event.get("run_id")
        success_count = event.get("success_count", 0)
        total_count = event.get("total_count", 0)
        
        logger.info(f"Workflow {workflow_name} (run: {run_id}) completed: {success_count}/{total_count} tasks successful")
        
        # Send notification based on success rate
        if success_count == total_count:
            publish("workflow_success", event)
        elif success_count > 0:
            publish("workflow_partial_success", event)
        else:
            publish("workflow_failure", event)
    
    def _handle_deployment_request(self, event: Dict[str, Any]):
        """Handle deployment request event."""
        workflow_name = event.get("workflow_name")
        environment = event.get("environment", "development")
        
        logger.info(f"Deployment requested for workflow {workflow_name} to {environment}")
        
        # Trigger deployment workflow
        publish("deployment_triggered", {
            "workflow_name": workflow_name,
            "environment": environment,
            "timestamp": datetime.now().isoformat()
        })

# Convenience functions
def create_prefect_orchestrator() -> PrefectWorkflowOrchestrator:
    """Create a new Prefect workflow orchestrator."""
    return PrefectWorkflowOrchestrator()

def create_development_workflow_config() -> PrefectWorkflowConfig:
    """Create a development workflow configuration."""
    return PrefectWorkflowConfig(
        name="bmad-development-pipeline",
        description="Complete development pipeline from user story to testing",
        workflow_type=WorkflowType.DEVELOPMENT,
        environment=DeploymentEnvironment.DEVELOPMENT,
        timeout_minutes=120,
        retries=2,
        tags=["development", "bmad", "pipeline"]
    )

def create_deployment_workflow_config() -> PrefectWorkflowConfig:
    """Create a deployment workflow configuration."""
    return PrefectWorkflowConfig(
        name="bmad-deployment-pipeline",
        description="Deployment pipeline for BMAD applications",
        workflow_type=WorkflowType.DEPLOYMENT,
        environment=DeploymentEnvironment.STAGING,
        timeout_minutes=180,
        retries=3,
        tags=["deployment", "bmad", "pipeline"]
    )

def create_testing_workflow_config() -> PrefectWorkflowConfig:
    """Create a testing workflow configuration."""
    return PrefectWorkflowConfig(
        name="bmad-testing-pipeline",
        description="Comprehensive testing pipeline",
        workflow_type=WorkflowType.TESTING,
        environment=DeploymentEnvironment.DEVELOPMENT,
        schedule="0 */6 * * *",  # Every 6 hours
        timeout_minutes=90,
        retries=2,
        tags=["testing", "bmad", "pipeline"]
    )

# Predefined agent task configurations
def get_development_tasks() -> List[AgentTaskConfig]:
    """Get predefined development workflow tasks."""
    return [
        AgentTaskConfig(
            agent_name="ProductOwner",
            task_name="create_user_story",
            command="create_user_story",
            parameters={"priority": "high"}
        ),
        AgentTaskConfig(
            agent_name="Architect",
            task_name="design_system",
            command="design_system",
            dependencies=["create_user_story"],
            parameters={"architecture_type": "microservices"}
        ),
        AgentTaskConfig(
            agent_name="FullstackDeveloper",
            task_name="implement_feature",
            command="implement_feature",
            dependencies=["design_system"],
            parameters={"framework": "react-fastapi"}
        ),
        AgentTaskConfig(
            agent_name="TestEngineer",
            task_name="run_tests",
            command="run_tests",
            dependencies=["implement_feature"],
            parameters={"test_type": "unit,integration,e2e"}
        )
    ]

def get_deployment_tasks() -> List[AgentTaskConfig]:
    """Get predefined deployment workflow tasks."""
    return [
        AgentTaskConfig(
            agent_name="DevOpsInfra",
            task_name="build_application",
            command="build_application",
            parameters={"build_type": "docker"}
        ),
        AgentTaskConfig(
            agent_name="SecurityDeveloper",
            task_name="security_scan",
            command="security_scan",
            dependencies=["build_application"],
            parameters={"scan_type": "vulnerability,secrets"}
        ),
        AgentTaskConfig(
            agent_name="DevOpsInfra",
            task_name="deploy_application",
            command="deploy_application",
            dependencies=["security_scan"],
            parameters={"environment": "staging"}
        ),
        AgentTaskConfig(
            agent_name="TestEngineer",
            task_name="smoke_tests",
            command="smoke_tests",
            dependencies=["deploy_application"],
            parameters={"test_scope": "critical_paths"}
        )
    ] 