"""
BMAD Advanced Workflow Orchestrator

Dit module biedt geavanceerde workflow orchestration voor complexe
multi-agent samenwerking met dependencies, parallel execution en error handling.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from bmad.agents.core.ai.confidence_scoring import confidence_scoring
from bmad.agents.core.communication.message_bus import publish, subscribe

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowTask:
    """Represents a single task in a workflow."""
    id: str
    name: str
    agent: str
    command: str
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # seconds
    retries: int = 3
    parallel: bool = False
    required: bool = True
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence_score: Optional[float] = None

@dataclass
class WorkflowDefinition:
    """Represents a complete workflow definition."""
    name: str
    description: str
    tasks: List[WorkflowTask]
    max_parallel: int = 3
    timeout: int = 3600  # 1 hour
    auto_retry: bool = True
    notify_on_completion: bool = True
    notify_on_failure: bool = True

class AdvancedWorkflowOrchestrator:
    """
    Advanced workflow orchestrator voor complexe multi-agent workflows.
    """

    def __init__(self):
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.task_executors: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, Callable] = {}

        # Register default task executors
        self._register_default_executors()

        # Register event handlers
        self._register_event_handlers()

    def register_workflow(self, workflow_def: WorkflowDefinition):
        """Registreer een workflow definitie."""
        self.workflow_definitions[workflow_def.name] = workflow_def
        logger.info(f"Workflow '{workflow_def.name}' geregistreerd met {len(workflow_def.tasks)} taken")

    def register_task_executor(self, task_type: str, executor: Callable):
        """Registreer een task executor voor een specifiek task type."""
        self.task_executors[task_type] = executor
        logger.info(f"Task executor geregistreerd voor type: {task_type}")

    def start_workflow(self, workflow_name: str, context: Dict[str, Any] = None) -> str:
        """Start een workflow en retourneer workflow ID."""
        if workflow_name not in self.workflow_definitions:
            raise ValueError(f"Workflow '{workflow_name}' niet gevonden")

        workflow_def = self.workflow_definitions[workflow_name]
        workflow_id = f"{workflow_name}_{int(time.time())}"

        # Initialize workflow
        workflow_state = {
            "id": workflow_id,
            "name": workflow_name,
            "definition": workflow_def,
            "status": WorkflowStatus.PENDING,
            "context": context or {},
            "tasks": {task.id: task for task in workflow_def.tasks},
            "completed_tasks": [],
            "failed_tasks": [],
            "start_time": time.time(),
            "end_time": None,
            "metrics": {
                "total_tasks": len(workflow_def.tasks),
                "completed_tasks": 0,
                "failed_tasks": 0,
                "skipped_tasks": 0
            }
        }

        self.active_workflows[workflow_id] = workflow_state

        # Start workflow execution
        asyncio.create_task(self._execute_workflow(workflow_id))

        logger.info(f"Workflow '{workflow_name}' gestart met ID: {workflow_id}")
        return workflow_id

    async def _execute_workflow(self, workflow_id: str):
        """Execute een workflow asynchroon."""
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = WorkflowStatus.RUNNING

        try:
            # Execute tasks in dependency order
            await self._execute_tasks(workflow_id)

            # Check if workflow completed successfully
            if workflow["metrics"]["failed_tasks"] == 0:
                workflow["status"] = WorkflowStatus.COMPLETED
                logger.info(f"Workflow {workflow_id} succesvol voltooid")

                if workflow["definition"].notify_on_completion:
                    self._notify_workflow_completion(workflow_id)
            else:
                workflow["status"] = WorkflowStatus.FAILED
                logger.error(f"Workflow {workflow_id} gefaald met {workflow['metrics']['failed_tasks']} fouten")

                if workflow["definition"].notify_on_failure:
                    self._notify_workflow_failure(workflow_id)

        except Exception as e:
            workflow["status"] = WorkflowStatus.FAILED
            workflow["error"] = str(e)
            logger.error(f"Workflow {workflow_id} gefaald met exception: {e}")

        finally:
            workflow["end_time"] = time.time()

    async def _execute_tasks(self, workflow_id: str):
        """Execute alle taken in een workflow."""
        workflow = self.active_workflows[workflow_id]
        tasks = workflow["tasks"]

        # Group tasks by dependency level
        task_groups = self._group_tasks_by_dependency(tasks)

        for group in task_groups:
            # Execute tasks in parallel within each group
            if len(group) == 1 or not any(tasks[task_id].parallel for task_id in group):
                # Sequential execution
                for task_id in group:
                    await self._execute_task(workflow_id, task_id)
            else:
                # Parallel execution
                parallel_tasks = [task_id for task_id in group if tasks[task_id].parallel]
                sequential_tasks = [task_id for task_id in group if not tasks[task_id].parallel]

                # Execute sequential tasks first
                for task_id in sequential_tasks:
                    await self._execute_task(workflow_id, task_id)

                # Execute parallel tasks
                if parallel_tasks:
                    await asyncio.gather(*[
                        self._execute_task(workflow_id, task_id)
                        for task_id in parallel_tasks
                    ])

    async def _execute_task(self, workflow_id: str, task_id: str):
        """Execute een enkele taak."""
        workflow = self.active_workflows[workflow_id]
        task = workflow["tasks"][task_id]

        # Check if task should be skipped
        if not task.required and self._should_skip_task(workflow_id, task_id):
            task.status = TaskStatus.SKIPPED
            workflow["metrics"]["skipped_tasks"] += 1
            logger.info(f"Task {task_id} overgeslagen")
            return

        # Check dependencies
        if not self._check_dependencies(workflow_id, task_id):
            task.status = TaskStatus.FAILED
            task.error = "Dependencies not met"
            workflow["metrics"]["failed_tasks"] += 1
            logger.error(f"Task {task_id} gefaald: dependencies not met")
            return

        # Execute task
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()

        try:
            # Find executor for task type
            executor = self.task_executors.get(task.agent)
            if not executor:
                raise ValueError(f"Geen executor gevonden voor agent: {task.agent}")

            # Execute task
            result = await executor(task, workflow["context"])

            # Process result with confidence scoring
            if isinstance(result, dict) and "output" in result:
                enhanced_result = confidence_scoring.enhance_agent_output(
                    output=result["output"],
                    agent_name=task.agent,
                    task_type=task.command,
                    context=workflow["context"]
                )

                task.confidence_score = enhanced_result["confidence"]
                task.result = enhanced_result

                # Check if review is required
                if enhanced_result["review_required"]:
                    self._request_review(workflow_id, task_id, enhanced_result)

            task.status = TaskStatus.COMPLETED
            task.end_time = time.time()
            workflow["completed_tasks"].append(task_id)
            workflow["metrics"]["completed_tasks"] += 1

            logger.info(f"Task {task_id} voltooid (confidence: {task.confidence_score:.2f})")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = time.time()
            workflow["failed_tasks"].append(task_id)
            workflow["metrics"]["failed_tasks"] += 1

            logger.error(f"Task {task_id} gefaald: {e}")

            # Retry if configured
            if task.retries > 0:
                await self._retry_task(workflow_id, task_id)

    async def _retry_task(self, workflow_id: str, task_id: str):
        """Retry een gefaalde taak."""
        workflow = self.active_workflows[workflow_id]
        task = workflow["tasks"][task_id]

        if task.retries > 0:
            task.retries -= 1
            task.status = TaskStatus.PENDING
            task.error = None

            logger.info(f"Retrying task {task_id} ({task.retries} retries left)")

            # Wait before retry
            await asyncio.sleep(5)

            # Re-execute task
            await self._execute_task(workflow_id, task_id)

    def _group_tasks_by_dependency(self, tasks: Dict[str, WorkflowTask]) -> List[List[str]]:
        """Group tasks by dependency level for execution order."""
        groups = []
        remaining_tasks = set(tasks.keys())

        while remaining_tasks:
            # Find tasks with no unsatisfied dependencies
            ready_tasks = []
            for task_id in remaining_tasks:
                task = tasks[task_id]
                if all(dep in [t for group in groups for t in group] for dep in task.dependencies):
                    ready_tasks.append(task_id)

            if not ready_tasks:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected in tasks: {remaining_tasks}")

            groups.append(ready_tasks)
            remaining_tasks -= set(ready_tasks)

        return groups

    def _check_dependencies(self, workflow_id: str, task_id: str) -> bool:
        """Check of alle dependencies van een taak zijn voldaan."""
        workflow = self.active_workflows[workflow_id]
        task = workflow["tasks"][task_id]

        for dep_id in task.dependencies:
            if dep_id not in workflow["tasks"]:
                return False

            dep_task = workflow["tasks"][dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False

        return True

    def _should_skip_task(self, workflow_id: str, task_id: str) -> bool:
        """Bepaal of een taak overgeslagen moet worden."""
        # Implementeer skip logic hier
        return False

    def _request_review(self, workflow_id: str, task_id: str, enhanced_result: Dict[str, Any]):
        """Request review voor een taak."""
        workflow = self.active_workflows[workflow_id]
        task = workflow["tasks"][task_id]

        review_request = {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "agent": task.agent,
            "task_name": task.name,
            "confidence": enhanced_result["confidence"],
            "review_level": enhanced_result["review_level"],
            "output": enhanced_result["output"],
            "timestamp": datetime.now().isoformat()
        }

        # Publish review request event
        publish("workflow_review_requested", review_request)

        logger.info(f"Review requested for task {task_id} (confidence: {enhanced_result['confidence']:.2f})")

    def _notify_workflow_completion(self, workflow_id: str):
        """Notificeer workflow completion."""
        workflow = self.active_workflows[workflow_id]

        completion_event = {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "status": "completed",
            "metrics": workflow["metrics"],
            "duration": workflow["end_time"] - workflow["start_time"],
            "timestamp": datetime.now().isoformat()
        }

        publish("workflow_completed", completion_event)

    def _notify_workflow_failure(self, workflow_id: str):
        """Notificeer workflow failure."""
        workflow = self.active_workflows[workflow_id]

        failure_event = {
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "status": "failed",
            "error": workflow.get("error"),
            "failed_tasks": workflow["failed_tasks"],
            "metrics": workflow["metrics"],
            "timestamp": datetime.now().isoformat()
        }

        publish("workflow_failed", failure_event)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Haal workflow status op."""
        if workflow_id not in self.active_workflows:
            return None

        workflow = self.active_workflows[workflow_id]

        return {
            "id": workflow_id,
            "name": workflow["name"],
            "status": workflow["status"].value,
            "start_time": workflow["start_time"],
            "end_time": workflow["end_time"],
            "duration": (workflow["end_time"] or time.time()) - workflow["start_time"],
            "metrics": workflow["metrics"],
            "tasks": {
                task_id: {
                    "name": task.name,
                    "status": task.status.value,
                    "confidence": task.confidence_score,
                    "error": task.error
                }
                for task_id, task in workflow["tasks"].items()
            }
        }

    def cancel_workflow(self, workflow_id: str):
        """Cancel een actieve workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = WorkflowStatus.CANCELLED
            workflow["end_time"] = time.time()

            logger.info(f"Workflow {workflow_id} geannuleerd")

    def _register_default_executors(self):
        """Registreer default task executors."""
        # Placeholder executors - deze zouden vervangen worden door echte agent calls
        self.register_task_executor("ProductOwner", self._execute_product_owner_task)
        self.register_task_executor("Architect", self._execute_architect_task)
        self.register_task_executor("FullstackDeveloper", self._execute_fullstack_task)
        self.register_task_executor("TestEngineer", self._execute_test_task)

    async def _execute_product_owner_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute een ProductOwner taak."""
        # Simuleer ProductOwner taak execution
        await asyncio.sleep(2)

        return {
            "output": f"ProductOwner taak '{task.name}' voltooid",
            "user_stories": ["Story 1", "Story 2"],
            "priority": "high"
        }

    async def _execute_architect_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute een Architect taak."""
        # Simuleer Architect taak execution
        await asyncio.sleep(3)

        return {
            "output": f"Architect taak '{task.name}' voltooid",
            "design": "System design document",
            "components": ["Component 1", "Component 2"]
        }

    async def _execute_fullstack_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute een FullstackDeveloper taak."""
        # Simuleer FullstackDeveloper taak execution
        await asyncio.sleep(5)

        return {
            "output": f"FullstackDeveloper taak '{task.name}' voltooid",
            "code": "Generated code",
            "tests": "Unit tests"
        }

    async def _execute_test_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute een TestEngineer taak."""
        # Simuleer TestEngineer taak execution
        await asyncio.sleep(2)

        return {
            "output": f"TestEngineer taak '{task.name}' voltooid",
            "test_results": "All tests passed",
            "coverage": "95%"
        }

    def _register_event_handlers(self):
        """Registreer event handlers."""
        subscribe("workflow_review_approved", self._handle_review_approval)
        subscribe("workflow_review_rejected", self._handle_review_rejection)

    def _handle_review_approval(self, event: Dict[str, Any]):
        """Handle review approval."""
        workflow_id = event.get("workflow_id")
        task_id = event.get("task_id")

        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            if task_id in workflow["tasks"]:
                task = workflow["tasks"][task_id]
                task.status = TaskStatus.COMPLETED
                logger.info(f"Review approved for task {task_id}")

    def _handle_review_rejection(self, event: Dict[str, Any]):
        """Handle review rejection."""
        workflow_id = event.get("workflow_id")
        task_id = event.get("task_id")

        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            if task_id in workflow["tasks"]:
                task = workflow["tasks"][task_id]
                task.status = TaskStatus.FAILED
                task.error = "Review rejected"
                logger.info(f"Review rejected for task {task_id}")

# Global instance
advanced_workflow = AdvancedWorkflowOrchestrator()
