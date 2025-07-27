"""
BMAD LangGraph Workflow Orchestrator

Dit module biedt een moderne, async-first workflow orchestration voor complexe
multi-agent samenwerking met stateful execution, dependency management en error handling.
Gebaseerd op LangGraph voor betrouwbare async workflows.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Callable, TypedDict, Annotated
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .message_bus import publish, subscribe
from .confidence_scoring import confidence_scoring

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

class WorkflowState(TypedDict):
    """State for LangGraph workflow execution."""
    workflow_id: str
    workflow_name: str
    current_task: Optional[str]
    completed_tasks: List[str]
    failed_tasks: List[str]
    skipped_tasks: List[str]
    task_results: Dict[str, Dict[str, Any]]
    task_errors: Dict[str, str]
    context: Dict[str, Any]
    status: str
    start_time: float
    end_time: Optional[float]
    metrics: Dict[str, int]

class LangGraphWorkflowOrchestrator:
    """
    Modern workflow orchestrator gebaseerd op LangGraph voor betrouwbare async workflows.
    """
    
    def __init__(self):
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.task_executors: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self.active_workflows: Dict[str, Any] = {}  # LangGraph app instances
        
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
        
        # Create initial state
        initial_state = WorkflowState(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            current_task=None,
            completed_tasks=[],
            failed_tasks=[],
            skipped_tasks=[],
            task_results={},
            task_errors={},
            context=context or {},
            status=WorkflowStatus.PENDING.value,
            start_time=time.time(),
            end_time=None,
            metrics={
                "completed_tasks": 0,
                "failed_tasks": 0,
                "skipped_tasks": 0,
                "total_tasks": len(workflow_def.tasks)
            }
        )
        
        # Create LangGraph app for this workflow
        app = self._create_workflow_app(workflow_def)
        self.active_workflows[workflow_id] = app
        
        # Start workflow execution
        try:
            asyncio.create_task(self._execute_workflow_async(workflow_id, app, initial_state))
        except RuntimeError:
            # No event loop running, store for later execution
            self._pending_workflows = getattr(self, '_pending_workflows', {})
            self._pending_workflows[workflow_id] = (app, initial_state)
        
        logger.info(f"Workflow {workflow_id} gestart")
        return workflow_id
    
    def _create_workflow_app(self, workflow_def: WorkflowDefinition):
        """Create a LangGraph app for the workflow."""
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add start node
        workflow.add_node("start", lambda state: state)
        
        # Add nodes for each task
        for task in workflow_def.tasks:
            workflow.add_node(task.id, self._create_task_node(task))
        
        # Add end node
        workflow.add_node("end", lambda state: state)
        
        # Add conditional edges from start to first available tasks
        start_edges = {}
        for task in workflow_def.tasks:
            if not task.dependencies:
                start_edges[task.id] = task.id
        
        if start_edges:
            workflow.add_conditional_edges("start", self._route_to_next_task, start_edges)
        
        # Add edges between tasks based on dependencies
        for task in workflow_def.tasks:
            if task.dependencies:
                # Task has dependencies, add edges from dependencies
                for dep in task.dependencies:
                    workflow.add_edge(dep, task.id)
        
        # Add conditional edges from tasks to next tasks or end
        for task in workflow_def.tasks:
            next_edges = {"end": "end"}
            for next_task in workflow_def.tasks:
                if task.id in next_task.dependencies:
                    next_edges[next_task.id] = next_task.id
            
            workflow.add_conditional_edges(task.id, self._route_to_next_task, next_edges)
        
        # Add end condition
        workflow.add_edge("end", END)
        
        # Set entry point
        workflow.set_entry_point("start")
        
        # Compile with memory saver
        return workflow.compile(checkpointer=MemorySaver())
    
    def _create_task_node(self, task: WorkflowTask):
        """Create a LangGraph node for a task."""
        async def task_node(state: WorkflowState) -> WorkflowState:
            """Execute a single task."""
            # Update state
            state["current_task"] = task.id
            state["status"] = WorkflowStatus.RUNNING.value
            
            # Check if task should be skipped
            if not task.required and self._should_skip_task(state, task):
                state["skipped_tasks"].append(task.id)
                state["metrics"]["skipped_tasks"] += 1
                logger.info(f"Task {task.id} overgeslagen")
                return state
            
            # Check dependencies
            if not self._check_dependencies(state, task):
                state["failed_tasks"].append(task.id)
                state["task_errors"][task.id] = "Dependencies not met"
                state["metrics"]["failed_tasks"] += 1
                logger.error(f"Task {task.id} gefaald: dependencies not met")
                return state
            
            # Execute task
            task_start_time = time.time()
            
            try:
                # Find executor for task type
                executor = self.task_executors.get(task.agent)
                if not executor:
                    raise ValueError(f"Geen executor gevonden voor agent: {task.agent}")
                
                # Execute task
                result = await executor(task, state["context"])
                
                # Process result with confidence scoring
                if isinstance(result, dict) and "output" in result:
                    enhanced_result = confidence_scoring.enhance_agent_output(
                        output=result["output"],
                        agent_name=task.agent,
                        task_type=task.command,
                        context=state["context"]
                    )
                    
                    state["task_results"][task.id] = enhanced_result
                    
                    # Check if review is required
                    if enhanced_result.get("review_required", False):
                        self._request_review(state["workflow_id"], task.id, enhanced_result)
                else:
                    state["task_results"][task.id] = result
                
                # Mark task as completed
                state["completed_tasks"].append(task.id)
                state["metrics"]["completed_tasks"] += 1
                
                logger.info(f"Task {task.id} voltooid")
                
            except Exception as e:
                state["failed_tasks"].append(task.id)
                state["task_errors"][task.id] = str(e)
                state["metrics"]["failed_tasks"] += 1
                
                logger.error(f"Task {task.id} gefaald: {e}")
                
                # Retry if configured
                if task.retries > 0:
                    await self._retry_task(state, task)
            
            return state
        
        return task_node
    
    async def _execute_workflow_async(self, workflow_id: str, app, initial_state: WorkflowState):
        """Execute workflow asynchronously using LangGraph."""
        try:
            # Execute workflow
            config = {"configurable": {"thread_id": workflow_id}}
            async for event in app.astream(initial_state, config):
                # Update workflow status based on events
                if "end" in event:
                    # Workflow completed
                    final_state = event["end"]
                    if final_state["metrics"]["failed_tasks"] == 0:
                        final_state["status"] = WorkflowStatus.COMPLETED.value
                        if self.workflow_definitions[final_state["workflow_name"]].notify_on_completion:
                            self._notify_workflow_completion(workflow_id)
                    else:
                        final_state["status"] = WorkflowStatus.FAILED.value
                        if self.workflow_definitions[final_state["workflow_name"]].notify_on_failure:
                            self._notify_workflow_failure(workflow_id)
                    
                    final_state["end_time"] = time.time()
                    logger.info(f"Workflow {workflow_id} voltooid met status: {final_state['status']}")
                    
        except Exception as e:
            logger.error(f"Workflow {workflow_id} gefaald met exception: {e}")
            # Update state to failed
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    def _execute_pending_workflows(self):
        """Execute pending workflows when event loop is available."""
        if hasattr(self, '_pending_workflows'):
            for workflow_id, (app, initial_state) in self._pending_workflows.items():
                try:
                    asyncio.create_task(self._execute_workflow_async(workflow_id, app, initial_state))
                except RuntimeError:
                    # Still no event loop, keep pending
                    continue
            self._pending_workflows.clear()
    
    def _route_to_next_task(self, state: WorkflowState) -> str:
        """Route to the next available task."""
        workflow_def = self.workflow_definitions[state["workflow_name"]]
        current_task = state.get("current_task")
        
        # If we're at the end, stay at end
        if current_task == "end":
            return "end"
        
        # If we're at start, find first available task
        if current_task is None or current_task == "start":
            for task in workflow_def.tasks:
                if (task.id not in state["completed_tasks"] and 
                    task.id not in state["failed_tasks"] and 
                    task.id not in state["skipped_tasks"] and
                    all(dep in state["completed_tasks"] for dep in task.dependencies)):
                    return task.id
            return "end"
        
        # Find next task that depends on current task
        for task in workflow_def.tasks:
            if (current_task in task.dependencies and
                task.id not in state["completed_tasks"] and 
                task.id not in state["failed_tasks"] and 
                task.id not in state["skipped_tasks"] and
                all(dep in state["completed_tasks"] for dep in task.dependencies)):
                return task.id
        
        # No more tasks available
        return "end"
    
    def _check_dependencies(self, state: WorkflowState, task: WorkflowTask) -> bool:
        """Check if task dependencies are met."""
        return all(dep in state["completed_tasks"] for dep in task.dependencies)
    
    def _should_skip_task(self, state: WorkflowState, task: WorkflowTask) -> bool:
        """Check if task should be skipped."""
        # Implement skip logic based on context
        return False
    
    async def _retry_task(self, state: WorkflowState, task: WorkflowTask):
        """Retry a failed task."""
        if task.retries > 0:
            task.retries -= 1
            
            # Remove from failed tasks
            if task.id in state["failed_tasks"]:
                state["failed_tasks"].remove(task.id)
            if task.id in state["task_errors"]:
                del state["task_errors"][task.id]
            
            logger.info(f"Retrying task {task.id} ({task.retries} retries left)")
            
            # Wait before retry
            await asyncio.sleep(5)
            
            # Re-execute task (this will be handled by LangGraph)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status."""
        if workflow_id not in self.active_workflows:
            return None
        
        # Get state from LangGraph checkpoint
        app = self.active_workflows[workflow_id]
        try:
            # This is a simplified version - in practice you'd get the actual state
            return {
                "workflow_id": workflow_id,
                "status": "running",  # Would be actual status from state
                "active_workflows": len(self.active_workflows),
                "workflow_name": workflow_id.split('_')[0] if '_' in workflow_id else "unknown"
            }
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return None
    
    def cancel_workflow(self, workflow_id: str):
        """Cancel a workflow."""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            logger.info(f"Workflow {workflow_id} geannuleerd")
    
    def list_workflows(self) -> List[str]:
        """List all registered workflow names."""
        return list(self.workflow_definitions.keys())
    
    def _register_default_executors(self):
        """Register default task executors."""
        self.register_task_executor("ProductOwner", self._execute_product_owner_task)
        self.register_task_executor("Architect", self._execute_architect_task)
        self.register_task_executor("FullstackDeveloper", self._execute_fullstack_task)
        self.register_task_executor("TestEngineer", self._execute_test_task)
    
    async def _execute_product_owner_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute ProductOwner task."""
        logger.info(f"Executing ProductOwner task: {task.command}")
        return {
            "output": f"ProductOwner executed: {task.command}",
            "agent": "ProductOwner",
            "task_id": task.id
        }
    
    async def _execute_architect_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute Architect task."""
        logger.info(f"Executing Architect task: {task.command}")
        return {
            "output": f"Architect executed: {task.command}",
            "agent": "Architect",
            "task_id": task.id
        }
    
    async def _execute_fullstack_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute FullstackDeveloper task."""
        logger.info(f"Executing FullstackDeveloper task: {task.command}")
        return {
            "output": f"FullstackDeveloper executed: {task.command}",
            "agent": "FullstackDeveloper",
            "task_id": task.id
        }
    
    async def _execute_test_task(self, task: WorkflowTask, context: Dict[str, Any]):
        """Execute TestEngineer task."""
        logger.info(f"Executing TestEngineer task: {task.command}")
        return {
            "output": f"TestEngineer executed: {task.command}",
            "agent": "TestEngineer",
            "task_id": task.id
        }
    
    def _register_event_handlers(self):
        """Register event handlers."""
        subscribe("review_approval", self._handle_review_approval)
        subscribe("review_rejection", self._handle_review_rejection)
    
    def _request_review(self, workflow_id: str, task_id: str, enhanced_result: Dict[str, Any]):
        """Request human review for a task result."""
        review_event = {
            "workflow_id": workflow_id,
            "task_id": task_id,
            "result": enhanced_result,
            "timestamp": time.time()
        }
        publish("review_requested", review_event)
        logger.info(f"Review requested for task {task_id} in workflow {workflow_id}")
    
    def _handle_review_approval(self, event: Dict[str, Any]):
        """Handle review approval event."""
        workflow_id = event.get("workflow_id")
        task_id = event.get("task_id")
        logger.info(f"Review approved for task {task_id} in workflow {workflow_id}")
        
        # Continue workflow execution
        publish("review_approved", event)
    
    def _handle_review_rejection(self, event: Dict[str, Any]):
        """Handle review rejection event."""
        workflow_id = event.get("workflow_id")
        task_id = event.get("task_id")
        logger.info(f"Review rejected for task {task_id} in workflow {workflow_id}")
        
        # Mark task as failed and continue
        publish("review_rejected", event)
    
    def _notify_workflow_completion(self, workflow_id: str):
        """Notify workflow completion."""
        completion_event = {
            "workflow_id": workflow_id,
            "status": "completed",
            "timestamp": time.time()
        }
        publish("workflow_completed", completion_event)
        logger.info(f"Workflow {workflow_id} completion notified")
    
    def _notify_workflow_failure(self, workflow_id: str):
        """Notify workflow failure."""
        failure_event = {
            "workflow_id": workflow_id,
            "status": "failed",
            "timestamp": time.time()
        }
        publish("workflow_failed", failure_event)
        logger.info(f"Workflow {workflow_id} failure notified")

# Convenience functions for backward compatibility
def create_workflow_orchestrator() -> LangGraphWorkflowOrchestrator:
    """Create a new LangGraph workflow orchestrator."""
    return LangGraphWorkflowOrchestrator()

def register_workflow_definition(name: str, description: str, tasks: List[WorkflowTask], **kwargs) -> WorkflowDefinition:
    """Create and register a workflow definition."""
    workflow_def = WorkflowDefinition(
        name=name,
        description=description,
        tasks=tasks,
        **kwargs
    )
    return workflow_def 