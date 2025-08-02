"""
Workflow Manager

This module provides workflow management functionality for the Workflow Service,
handling workflow creation, execution, monitoring, and lifecycle management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone, timedelta
import json
import uuid
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class WorkflowType(str, Enum):
    """Workflow type enumeration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    EVENT_DRIVEN = "event_driven"

class WorkflowStep(BaseModel):
    """Workflow step model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    step_type: str
    agent_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Workflow(BaseModel):
    """Workflow model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    workflow_type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.DRAFT
    steps: List[WorkflowStep] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration_seconds: float = 0.0

class WorkflowExecution(BaseModel):
    """Workflow execution model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    step_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None

class WorkflowManager:
    """Manages workflow lifecycle and operations."""
    
    def __init__(self, store=None, orchestrator=None):
        self.store = store
        self.orchestrator = orchestrator
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        
    async def create_workflow(self, name: str, workflow_type: WorkflowType,
                            description: Optional[str] = None,
                            steps: Optional[List[Dict[str, Any]]] = None,
                            config: Optional[Dict[str, Any]] = None,
                            metadata: Optional[Dict[str, Any]] = None,
                            tags: Optional[List[str]] = None) -> Workflow:
        """Create a new workflow."""
        try:
            # Convert step dictionaries to WorkflowStep objects
            workflow_steps = []
            if steps:
                for step_data in steps:
                    step = WorkflowStep(**step_data)
                    workflow_steps.append(step)
                    
            workflow = Workflow(
                name=name,
                description=description,
                workflow_type=workflow_type,
                steps=workflow_steps,
                config=config or {},
                metadata=metadata or {},
                tags=tags or []
            )
            
            # Store workflow
            if self.store:
                await self.store.save_workflow(workflow)
            else:
                self.workflows[workflow.id] = workflow
                
            logger.info(f"Created workflow: {workflow.id} ({name})")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
            
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        try:
            if self.store:
                return await self.store.get_workflow(workflow_id)
            else:
                return self.workflows.get(workflow_id)
                
        except Exception as e:
            logger.error(f"Failed to get workflow {workflow_id}: {e}")
            return None
            
    async def update_workflow(self, workflow_id: str, 
                            updates: Dict[str, Any]) -> Optional[Workflow]:
        """Update workflow."""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
                    
            workflow.updated_at = datetime.now(timezone.utc)
            
            # Store updated workflow
            if self.store:
                await self.store.save_workflow(workflow)
            else:
                self.workflows[workflow_id] = workflow
                
            logger.info(f"Updated workflow: {workflow_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            return None
            
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow."""
        try:
            if self.store:
                success = await self.store.delete_workflow(workflow_id)
            else:
                success = workflow_id in self.workflows
                if success:
                    del self.workflows[workflow_id]
                    
            if success:
                logger.info(f"Deleted workflow: {workflow_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False
            
    async def list_workflows(self, workflow_type: Optional[WorkflowType] = None,
                           status: Optional[WorkflowStatus] = None,
                           tags: Optional[List[str]] = None,
                           limit: int = 100) -> List[Workflow]:
        """List workflows with optional filtering."""
        try:
            if self.store:
                workflows = await self.store.list_workflows()
            else:
                workflows = list(self.workflows.values())
                
            # Apply filters
            if workflow_type:
                workflows = [w for w in workflows if w.workflow_type == workflow_type]
                
            if status:
                workflows = [w for w in workflows if w.status == status]
                
            if tags:
                workflows = [w for w in workflows if any(tag in w.tags for tag in tags)]
                
            # Sort by updated_at descending and limit
            workflows.sort(key=lambda x: x.updated_at, reverse=True)
            return workflows[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
            
    async def execute_workflow(self, workflow_id: str, 
                             input_data: Optional[Dict[str, Any]] = None) -> Optional[WorkflowExecution]:
        """Execute a workflow."""
        try:
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                logger.error(f"Workflow not found: {workflow_id}")
                return None
                
            # Create execution
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                input_data=input_data or {}
            )
            
            # Store execution
            if self.store:
                await self.store.save_execution(execution)
            else:
                self.executions[execution.id] = execution
                
            # Update workflow status
            workflow.status = WorkflowStatus.RUNNING
            workflow.execution_count += 1
            workflow.started_at = datetime.now(timezone.utc)
            await self.update_workflow(workflow_id, {"status": workflow.status})
            
            # Execute workflow using orchestrator
            if self.orchestrator:
                await self.orchestrator.execute_workflow(execution)
            else:
                # Simple execution without orchestrator
                await self._execute_workflow_simple(execution, workflow)
                
            logger.info(f"Started workflow execution: {execution.id}")
            return execution
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return None
            
    async def _execute_workflow_simple(self, execution: WorkflowExecution, workflow: Workflow):
        """Simple workflow execution without orchestrator."""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            
            # Execute steps based on workflow type
            if workflow.workflow_type == WorkflowType.SEQUENTIAL:
                await self._execute_sequential(execution, workflow)
            elif workflow.workflow_type == WorkflowType.PARALLEL:
                await self._execute_parallel(execution, workflow)
            elif workflow.workflow_type == WorkflowType.CONDITIONAL:
                await self._execute_conditional(execution, workflow)
            else:
                await self._execute_sequential(execution, workflow)
                
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            logger.error(f"Workflow execution failed: {e}")
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            if execution.started_at:
                execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
                
    async def _execute_sequential(self, execution: WorkflowExecution, workflow: Workflow):
        """Execute workflow steps sequentially."""
        for step in workflow.steps:
            try:
                step.status = "running"
                step.started_at = datetime.now(timezone.utc)
                
                # Simulate step execution
                await asyncio.sleep(1)  # Simulate work
                
                step.status = "completed"
                step.completed_at = datetime.now(timezone.utc)
                step.result = {"output": f"Step {step.name} completed"}
                
                execution.step_results[step.id] = step.result
                
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                step.completed_at = datetime.now(timezone.utc)
                raise
                
        execution.status = WorkflowStatus.COMPLETED
        execution.output_data = {"result": "Workflow completed successfully"}
        
    async def _execute_parallel(self, execution: WorkflowExecution, workflow: Workflow):
        """Execute workflow steps in parallel."""
        tasks = []
        for step in workflow.steps:
            task = self._execute_step(step)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            step = workflow.steps[i]
            if isinstance(result, Exception):
                step.status = "failed"
                step.error = str(result)
            else:
                step.status = "completed"
                step.result = result
                execution.step_results[step.id] = result
                
        # Check if all steps succeeded
        failed_steps = [s for s in workflow.steps if s.status == "failed"]
        if failed_steps:
            execution.status = WorkflowStatus.FAILED
            execution.error = f"{len(failed_steps)} steps failed"
        else:
            execution.status = WorkflowStatus.COMPLETED
            execution.output_data = {"result": "All parallel steps completed"}
            
    async def _execute_conditional(self, execution: WorkflowExecution, workflow: Workflow):
        """Execute workflow with conditional logic."""
        # Simple conditional execution - execute first step only
        if workflow.steps:
            step = workflow.steps[0]
            try:
                step.status = "running"
                step.started_at = datetime.now(timezone.utc)
                
                # Simulate conditional logic
                condition = workflow.config.get("condition", True)
                if condition:
                    await asyncio.sleep(1)
                    step.status = "completed"
                    step.result = {"output": "Condition met, step executed"}
                else:
                    step.status = "skipped"
                    step.result = {"output": "Condition not met, step skipped"}
                    
                step.completed_at = datetime.now(timezone.utc)
                execution.step_results[step.id] = step.result
                
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                step.completed_at = datetime.now(timezone.utc)
                raise
                
        execution.status = WorkflowStatus.COMPLETED
        execution.output_data = {"result": "Conditional workflow completed"}
        
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            await asyncio.sleep(1)  # Simulate work
            return {"output": f"Step {step.name} completed"}
        except Exception as e:
            raise e
            
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID."""
        try:
            if self.store:
                return await self.store.get_execution(execution_id)
            else:
                return self.executions.get(execution_id)
                
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return None
            
    async def list_executions(self, workflow_id: Optional[str] = None,
                            status: Optional[WorkflowStatus] = None,
                            limit: int = 100) -> List[WorkflowExecution]:
        """List workflow executions with optional filtering."""
        try:
            if self.store:
                executions = await self.store.list_executions()
            else:
                executions = list(self.executions.values())
                
            # Apply filters
            if workflow_id:
                executions = [e for e in executions if e.workflow_id == workflow_id]
                
            if status:
                executions = [e for e in executions if e.status == status]
                
            # Sort by started_at descending and limit
            executions.sort(key=lambda x: x.started_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
            return executions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list executions: {e}")
            return []
            
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a workflow execution."""
        try:
            execution = await self.get_execution(execution_id)
            if not execution:
                return False
                
            if execution.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                execution.status = WorkflowStatus.CANCELLED
                execution.completed_at = datetime.now(timezone.utc)
                
                # Store updated execution
                if self.store:
                    await self.store.save_execution(execution)
                else:
                    self.executions[execution_id] = execution
                    
                logger.info(f"Cancelled execution: {execution_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel execution {execution_id}: {e}")
            return False
            
    async def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        try:
            workflows = await self.list_workflows()
            executions = await self.list_executions()
            
            if not workflows:
                return {
                    "total_workflows": 0,
                    "total_executions": 0,
                    "workflow_types": {},
                    "status_distribution": {}
                }
                
            # Calculate statistics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
            failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])
            
            # Count by type
            type_counts = {}
            for workflow in workflows:
                type_counts[workflow.workflow_type] = type_counts.get(workflow.workflow_type, 0) + 1
                
            # Count by status
            status_counts = {}
            for workflow in workflows:
                status_counts[workflow.status] = status_counts.get(workflow.status, 0) + 1
                
            return {
                "total_workflows": len(workflows),
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                "workflow_types": type_counts,
                "status_distribution": status_counts
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow stats: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Check workflow manager health."""
        try:
            stats = await self.get_workflow_stats()
            
            return {
                "status": "healthy",
                "total_workflows": stats.get("total_workflows", 0),
                "total_executions": stats.get("total_executions", 0),
                "store_available": self.store is not None,
                "orchestrator_available": self.orchestrator is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "store_available": self.store is not None,
                "orchestrator_available": self.orchestrator is not None
            } 