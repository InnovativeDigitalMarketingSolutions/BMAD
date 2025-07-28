"""
Tests for bmad.agents.core.workflow.integrated_workflow_orchestrator module.
"""

import pytest
import time
from unittest.mock import patch, AsyncMock

# Mock Prefect to avoid Pydantic compatibility issues
import sys
import unittest.mock
sys.modules['prefect'] = unittest.mock.MagicMock()
sys.modules['prefect.flow'] = unittest.mock.MagicMock()
sys.modules['prefect.deployments'] = unittest.mock.MagicMock()

from bmad.agents.core.workflow.integrated_workflow_orchestrator import (
    IntegratedWorkflowOrchestrator,
    WorkflowDefinition,
    WorkflowTask,
    WorkflowStatus,
    TaskStatus
)


class TestWorkflowTask:
    """Test WorkflowTask dataclass."""
    
    def test_workflow_task_creation(self):
        """Test creating a WorkflowTask."""
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="TestAgent",
            command="test_command"
        )
        
        assert task.id == "test_task"
        assert task.name == "Test Task"
        assert task.agent == "TestAgent"
        assert task.command == "test_command"
        assert task.status == TaskStatus.PENDING
        assert task.dependencies == []
        assert task.timeout == 300
        assert task.retries == 3
        assert task.parallel is False
        assert task.required is True
    
    def test_workflow_task_with_dependencies(self):
        """Test creating a WorkflowTask with dependencies."""
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="TestAgent",
            command="test_command",
            dependencies=["task1", "task2"]
        )
        
        assert task.dependencies == ["task1", "task2"]
    
    def test_workflow_task_custom_settings(self):
        """Test creating a WorkflowTask with custom settings."""
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="TestAgent",
            command="test_command",
            timeout=600,
            retries=5,
            parallel=True,
            required=False
        )
        
        assert task.timeout == 600
        assert task.retries == 5
        assert task.parallel is True
        assert task.required is False


class TestWorkflowDefinition:
    """Test WorkflowDefinition dataclass."""
    
    def test_workflow_definition_creation(self):
        """Test creating a WorkflowDefinition."""
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1"),
            WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2")
        ]
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        assert workflow.name == "test_workflow"
        assert workflow.description == "Test workflow"
        assert len(workflow.tasks) == 2
        assert workflow.max_parallel == 3
        assert workflow.timeout == 3600
        assert workflow.auto_retry is True
        assert workflow.notify_on_completion is True
        assert workflow.notify_on_failure is True
    
    def test_workflow_definition_custom_settings(self):
        """Test creating a WorkflowDefinition with custom settings."""
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks,
            max_parallel=5,
            timeout=7200,
            auto_retry=False,
            notify_on_completion=False,
            notify_on_failure=False
        )
        
        assert workflow.max_parallel == 5
        assert workflow.timeout == 7200
        assert workflow.auto_retry is False
        assert workflow.notify_on_completion is False
        assert workflow.notify_on_failure is False


class TestIntegratedWorkflowOrchestrator:
    """Test IntegratedWorkflowOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        assert orchestrator.workflow_definitions == {}
        assert orchestrator.active_workflows == {}
        assert orchestrator.task_executors == {}
        assert orchestrator.max_parallel_workflows == 5
        assert orchestrator.workflow_timeout == 3600
    
    def test_register_workflow(self):
        """Test workflow registration."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        workflow = WorkflowDefinition(name="test_workflow", description="Test", tasks=tasks)
        
        orchestrator.register_workflow(workflow)
        
        assert "test_workflow" in orchestrator.workflow_definitions
        assert orchestrator.workflow_definitions["test_workflow"] == workflow
    
    def test_register_task_executor(self):
        """Test task executor registration."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        def test_executor(task, context):
            return {"output": "test"}
        
        orchestrator.register_task_executor("TestAgent", test_executor)
        
        assert "TestAgent" in orchestrator.task_executors
        assert orchestrator.task_executors["TestAgent"] == test_executor
    
    def test_start_workflow_success(self):
        """Test successful workflow start."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        workflow = WorkflowDefinition(name="test_workflow", description="Test", tasks=tasks)
        orchestrator.register_workflow(workflow)
        
        workflow_id = orchestrator.start_workflow("test_workflow", {"project": "test"})
        
        assert workflow_id is not None
        assert workflow_id in orchestrator.active_workflows
        assert orchestrator.active_workflows[workflow_id]["name"] == "test_workflow"
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.RUNNING
    
    def test_start_workflow_not_found(self):
        """Test starting non-existent workflow."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        workflow_id = orchestrator.start_workflow("non_existent", {})
        
        assert workflow_id is None
    
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Setup mock workflow
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": "test_workflow",
            "status": WorkflowStatus.RUNNING,
            "start_time": time.time(),
            "end_time": None,
            "metrics": {
                "total_tasks": 2,
                "completed_tasks": 1,
                "failed_tasks": 0,
                "skipped_tasks": 0
            },
            "tasks": {
                "task1": WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1", status=TaskStatus.COMPLETED),
                "task2": WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", status=TaskStatus.RUNNING)
            }
        }
        
        status = orchestrator.get_workflow_status(workflow_id)
        
        assert status["id"] == workflow_id
        assert status["name"] == "test_workflow"
        assert status["status"] == "running"
        assert status["metrics"]["total_tasks"] == 2
        assert status["metrics"]["completed_tasks"] == 1
        assert len(status["tasks"]) == 2
    
    def test_get_workflow_status_not_found(self):
        """Test getting status of non-existent workflow."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        status = orchestrator.get_workflow_status("non_existent")
        
        assert status is None
    
    def test_cancel_workflow(self):
        """Test workflow cancellation."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Setup mock workflow
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": "test_workflow",
            "status": WorkflowStatus.RUNNING,
            "start_time": time.time(),
            "end_time": None
        }
        
        result = orchestrator.cancel_workflow(workflow_id)
        
        assert result is True
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.CANCELLED
        assert orchestrator.active_workflows[workflow_id]["end_time"] is not None
    
    def test_group_tasks_by_dependency(self):
        """Test task dependency grouping."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        tasks = {
            "task1": WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1"),
            "task2": WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task1"]),
            "task3": WorkflowTask(id="task3", name="Task 3", agent="Agent3", command="cmd3", dependencies=["task1"]),
            "task4": WorkflowTask(id="task4", name="Task 4", agent="Agent4", command="cmd4", dependencies=["task2", "task3"])
        }
        
        groups = orchestrator._group_tasks_by_dependency(tasks)
        
        assert len(groups) == 3
        assert "task1" in groups[0]
        assert "task2" in groups[1] and "task3" in groups[1]
        assert "task4" in groups[2]
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Setup workflow state
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "tasks": {
                "task1": WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1", status=TaskStatus.COMPLETED),
                "task2": WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task1"], status=TaskStatus.PENDING)
            }
        }
        
        # Test dependency check
        assert orchestrator._check_dependencies(workflow_id, "task2")
        
        # Test failed dependency
        orchestrator.active_workflows[workflow_id]["tasks"]["task1"].status = TaskStatus.FAILED
        assert not orchestrator._check_dependencies(workflow_id, "task2")
    
    def test_should_skip_task(self):
        """Test task skip logic."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Setup workflow state
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "tasks": {
                "task1": WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1", status=TaskStatus.COMPLETED),
                "task2": WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", status=TaskStatus.SKIPPED),
                "task3": WorkflowTask(id="task3", name="Task 3", agent="Agent3", command="cmd3", status=TaskStatus.PENDING)
            }
        }
        
        # Test skip logic
        assert not orchestrator._should_skip_task(workflow_id, "task1")  # Already completed
        assert orchestrator._should_skip_task(workflow_id, "task2")  # Already skipped
        assert not orchestrator._should_skip_task(workflow_id, "task3")  # Pending


class TestIntegratedWorkflowOrchestratorAsync:
    """Test async methods of IntegratedWorkflowOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test successful task execution."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor
        async def mock_executor(task, context):
            return {"output": "success", "confidence": 0.9}
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        task = WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1")
        context = {"project": "test"}
        
        result = await orchestrator._execute_task(task, context)
        
        assert result["output"] == "success"
        assert result["confidence"] == 0.9
        assert task.status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_task_failure(self):
        """Test task execution failure."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor that raises exception
        async def mock_executor(task, context):
            raise Exception("Task failed")
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        task = WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1")
        context = {"project": "test"}
        
        result = await orchestrator._execute_task(task, context)
        
        assert result is None
        assert task.status == TaskStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_retry_task(self):
        """Test task retry logic."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor that fails first, then succeeds
        call_count = 0
        async def mock_executor(task, context):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Task failed")
            return {"output": "success"}
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        task = WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1", retries=2)
        context = {"project": "test"}
        
        result = await orchestrator._execute_task(task, context)
        
        assert result["output"] == "success"
        assert task.status == TaskStatus.COMPLETED
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_tasks_parallel(self):
        """Test parallel task execution."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor
        async def mock_executor(task, context):
            return {"output": f"success_{task.id}"}
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1", parallel=True),
            WorkflowTask(id="task2", name="Task 2", agent="TestAgent", command="cmd2", parallel=True)
        ]
        context = {"project": "test"}
        
        results = await orchestrator._execute_tasks_parallel(tasks, context)
        
        assert len(results) == 2
        assert results[0]["output"] == "success_task1"
        assert results[1]["output"] == "success_task2"


class TestWorkflowIntegration:
    """Test complete workflow integration."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self):
        """Test complete workflow execution."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor
        async def mock_executor(task, context):
            return {"output": f"completed_{task.id}"}
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        # Create workflow
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1"),
            WorkflowTask(id="task2", name="Task 2", agent="TestAgent", command="cmd2", dependencies=["task1"])
        ]
        workflow = WorkflowDefinition(name="test_workflow", description="Test", tasks=tasks)
        orchestrator.register_workflow(workflow)
        
        # Start and execute workflow
        workflow_id = orchestrator.start_workflow("test_workflow", {"project": "test"})
        await orchestrator._execute_workflow(workflow_id)
        
        # Check results
        status = orchestrator.get_workflow_status(workflow_id)
        assert status["status"] == "completed"
        assert status["metrics"]["completed_tasks"] == 2
    
    @pytest.mark.asyncio
    async def test_workflow_with_failure_and_retry(self):
        """Test workflow with task failure and retry."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor with retry logic
        call_count = {"task1": 0, "task2": 0}
        async def mock_executor(task, context):
            call_count[task.id] += 1
            if task.id == "task1" and call_count[task.id] == 1:
                raise Exception("Task failed")
            return {"output": f"completed_{task.id}"}
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        # Create workflow
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1", retries=2),
            WorkflowTask(id="task2", name="Task 2", agent="TestAgent", command="cmd2", dependencies=["task1"])
        ]
        workflow = WorkflowDefinition(name="test_workflow", description="Test", tasks=tasks)
        orchestrator.register_workflow(workflow)
        
        # Start and execute workflow
        workflow_id = orchestrator.start_workflow("test_workflow", {"project": "test"})
        await orchestrator._execute_workflow(workflow_id)
        
        # Check results
        status = orchestrator.get_workflow_status(workflow_id)
        assert status["status"] == "completed"
        assert call_count["task1"] == 2  # Retried once
        assert call_count["task2"] == 1  # Executed once
    
    @pytest.mark.asyncio
    async def test_workflow_with_required_task_failure(self):
        """Test workflow with required task failure."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Mock task executor that always fails
        async def mock_executor(task, context):
            raise Exception("Task failed")
        
        orchestrator.register_task_executor("TestAgent", mock_executor)
        
        # Create workflow
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="TestAgent", command="cmd1", required=True),
            WorkflowTask(id="task2", name="Task 2", agent="TestAgent", command="cmd2", dependencies=["task1"])
        ]
        workflow = WorkflowDefinition(name="test_workflow", description="Test", tasks=tasks)
        orchestrator.register_workflow(workflow)
        
        # Start and execute workflow
        workflow_id = orchestrator.start_workflow("test_workflow", {"project": "test"})
        await orchestrator._execute_workflow(workflow_id)
        
        # Check results
        status = orchestrator.get_workflow_status(workflow_id)
        assert status["status"] == "failed"
        assert status["metrics"]["failed_tasks"] == 1


class TestWorkflowEventHandling:
    """Test workflow event handling."""
    
    def test_handle_review_approval(self):
        """Test handling review approval event."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Setup workflow with pending review
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": "test_workflow",
            "status": WorkflowStatus.PAUSED,
            "current_task": "review_task",
            "tasks": {
                "review_task": WorkflowTask(id="review_task", name="Review", agent="Reviewer", command="review", status=TaskStatus.PENDING)
            }
        }
        
        # Handle approval
        result = orchestrator.handle_review_approval(workflow_id, "review_task", "Approved")
        
        assert result is True
        assert orchestrator.active_workflows[workflow_id]["tasks"]["review_task"].status == TaskStatus.COMPLETED
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.RUNNING
    
    def test_handle_review_rejection(self):
        """Test handling review rejection event."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        # Setup workflow with pending review
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": "test_workflow",
            "status": WorkflowStatus.PAUSED,
            "current_task": "review_task",
            "tasks": {
                "review_task": WorkflowTask(id="review_task", name="Review", agent="Reviewer", command="review", status=TaskStatus.PENDING)
            }
        }
        
        # Handle rejection
        result = orchestrator.handle_review_rejection(workflow_id, "review_task", "Rejected - needs changes")
        
        assert result is True
        assert orchestrator.active_workflows[workflow_id]["tasks"]["review_task"].status == TaskStatus.FAILED
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.FAILED


class TestWorkflowNotifications:
    """Test workflow notifications."""
    
    @patch('bmad.agents.core.workflow.integrated_workflow_orchestrator.publish')
    def test_notify_workflow_completion(self, mock_publish):
        """Test workflow completion notification."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": "test_workflow",
            "status": WorkflowStatus.COMPLETED,
            "metrics": {"total_tasks": 2, "completed_tasks": 2}
        }
        
        orchestrator._notify_workflow_completion(workflow_id)
        
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        assert call_args[0] == "workflow_completed"
        assert call_args[1]["workflow_id"] == workflow_id
    
    @patch('bmad.agents.core.workflow.integrated_workflow_orchestrator.publish')
    def test_notify_workflow_failure(self, mock_publish):
        """Test workflow failure notification."""
        orchestrator = IntegratedWorkflowOrchestrator()
        
        workflow_id = "test_workflow"
        orchestrator.active_workflows[workflow_id] = {
            "id": workflow_id,
            "name": "test_workflow",
            "status": WorkflowStatus.FAILED,
            "metrics": {"total_tasks": 2, "failed_tasks": 1}
        }
        
        orchestrator._notify_workflow_failure(workflow_id, "Task failed")
        
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        assert call_args[0] == "workflow_failed"
        assert call_args[1]["workflow_id"] == workflow_id
        assert call_args[1]["error"] == "Task failed" 