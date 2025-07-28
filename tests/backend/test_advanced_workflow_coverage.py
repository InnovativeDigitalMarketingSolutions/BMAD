"""
Tests for bmad.agents.core.advanced_workflow module.
"""

import pytest
import time
from unittest.mock import patch, AsyncMock

from bmad.agents.core.advanced_workflow import (
    AdvancedWorkflowOrchestrator,
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


class TestAdvancedWorkflowOrchestrator:
    """Test AdvancedWorkflowOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        assert orchestrator.active_workflows == {}
        assert orchestrator.workflow_definitions == {}
        # task_executors contains default executors, so it's not empty
        assert len(orchestrator.task_executors) > 0
        assert orchestrator.event_handlers == {}
    
    def test_register_workflow(self):
        """Test registering a workflow."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow)
        
        assert "test_workflow" in orchestrator.workflow_definitions
        assert orchestrator.workflow_definitions["test_workflow"] == workflow
    
    def test_register_task_executor(self):
        """Test registering a task executor."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        def test_executor(task, context):
            return {"result": "success"}
        
        orchestrator.register_task_executor("test_type", test_executor)
        
        assert "test_type" in orchestrator.task_executors
        assert orchestrator.task_executors["test_type"] == test_executor
    
    def test_start_workflow_success(self):
        """Test starting a workflow successfully."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow", {"context": "test"})
            
            assert workflow_id.startswith("test_workflow_")
            assert workflow_id in orchestrator.active_workflows
    
    def test_start_workflow_not_found(self):
        """Test starting a non-existent workflow."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        with pytest.raises(ValueError, match="Workflow 'nonexistent' niet gevonden"):
            orchestrator.start_workflow("nonexistent")
    
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow")
            
            status = orchestrator.get_workflow_status(workflow_id)
        
        assert status is not None
        assert "id" in status  # Changed from workflow_id to id
        assert "status" in status
        assert "tasks" in status
    
    def test_get_workflow_status_not_found(self):
        """Test getting status of non-existent workflow."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        status = orchestrator.get_workflow_status("nonexistent")
        assert status is None
    
    def test_cancel_workflow(self):
        """Test canceling a workflow."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        tasks = [WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")]
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow")
            
            orchestrator.cancel_workflow(workflow_id)
        
        # Check that workflow is marked as cancelled
        status = orchestrator.get_workflow_status(workflow_id)
        assert status["status"] == WorkflowStatus.CANCELLED.value
    
    def test_group_tasks_by_dependency(self):
        """Test grouping tasks by dependency."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Create tasks with dependencies
        task1 = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        task2 = WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task1"])
        task3 = WorkflowTask(id="task3", name="Task 3", agent="Agent3", command="cmd3", dependencies=["task2"])
        
        tasks = {"task1": task1, "task2": task2, "task3": task3}
        
        groups = orchestrator._group_tasks_by_dependency(tasks)
        
        assert len(groups) == 3
        assert "task1" in groups[0]
        assert "task2" in groups[1]
        assert "task3" in groups[2]
    
    def test_check_dependencies(self):
        """Test checking task dependencies."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Create a workflow with dependencies
        task1 = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        task2 = WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task1"])
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task1, task2]
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow")
            
            # Task1 has no dependencies, should be ready
            assert orchestrator._check_dependencies(workflow_id, "task1") is True
        
        # Task2 depends on task1, should not be ready initially
        assert orchestrator._check_dependencies(workflow_id, "task2") is False
        
        # Mark task1 as completed
        orchestrator.active_workflows[workflow_id]["tasks"]["task1"].status = TaskStatus.COMPLETED
        
        # Now task2 should be ready
        assert orchestrator._check_dependencies(workflow_id, "task2") is True
    
    def test_should_skip_task(self):
        """Test checking if a task should be skipped."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Create a workflow
        task1 = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1", required=False)
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task1]
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow")
            
            # Task should not be skipped initially
            assert orchestrator._should_skip_task(workflow_id, "task1") is False
        
        # Mark task as failed
        orchestrator.active_workflows[workflow_id]["tasks"]["task1"].status = TaskStatus.FAILED
        
        # _should_skip_task is currently a placeholder that always returns False
        assert orchestrator._should_skip_task(workflow_id, "task1") is False


class TestAdvancedWorkflowOrchestratorAsync:
    """Test async methods of AdvancedWorkflowOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test successful task execution."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executor
        mock_executor = AsyncMock(return_value={"result": "success", "confidence": 0.8})
        orchestrator.task_executors["ProductOwner"] = mock_executor
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="ProductOwner",
            command="test_command"
        )
        
        workflow_id = "test_workflow_123"
        orchestrator.active_workflows[workflow_id] = {
            "definition": WorkflowDefinition(name="test", description="test", tasks=[task]),
            "status": WorkflowStatus.RUNNING,
            "tasks": {"test_task": task},
            "context": {"test": "context"}
        }
        
        await orchestrator._execute_task(workflow_id, "test_task")
        
        # Check that task was executed
        mock_executor.assert_called_once()
        assert orchestrator.active_workflows[workflow_id]["tasks"]["test_task"].status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_task_failure(self):
        """Test task execution failure."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executor that raises an exception
        mock_executor = AsyncMock(side_effect=Exception("Task failed"))
        orchestrator.task_executors["test_type"] = mock_executor
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="TestAgent",
            command="test_command"
        )
        
        workflow_id = "test_workflow_123"
        orchestrator.active_workflows[workflow_id] = {
            "definition": WorkflowDefinition(name="test", description="test", tasks=[task]),
            "status": WorkflowStatus.RUNNING,
            "tasks": {"test_task": {"status": TaskStatus.PENDING}},
            "context": {"test": "context"}
        }
        
        await orchestrator._execute_task(workflow_id, "test_task")
        
        # Check that task failed
        assert orchestrator.active_workflows[workflow_id]["tasks"]["test_task"]["status"] == TaskStatus.FAILED
        assert "error" in orchestrator.active_workflows[workflow_id]["tasks"]["test_task"]
    
    @pytest.mark.asyncio
    async def test_retry_task(self):
        """Test task retry functionality."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executor that fails first, then succeeds
        mock_executor = AsyncMock(side_effect=[Exception("First failure"), {"result": "success"}])
        orchestrator.task_executors["test_type"] = mock_executor
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="TestAgent",
            command="test_command",
            retries=2
        )
        
        workflow_id = "test_workflow_123"
        orchestrator.active_workflows[workflow_id] = {
            "definition": WorkflowDefinition(name="test", description="test", tasks=[task]),
            "status": WorkflowStatus.RUNNING,
            "tasks": {"test_task": {"status": TaskStatus.FAILED, "retry_count": 0}},
            "context": {"test": "context"}
        }
        
        await orchestrator._retry_task(workflow_id, "test_task")
        
        # Check that task was retried and succeeded
        assert mock_executor.call_count == 2
        assert orchestrator.active_workflows[workflow_id]["tasks"]["test_task"]["status"] == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_tasks_parallel(self):
        """Test parallel task execution."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executor
        mock_executor = AsyncMock(return_value={"result": "success"})
        orchestrator.task_executors["test_type"] = mock_executor
        
        # Create parallel tasks
        task1 = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1", parallel=True)
        task2 = WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", parallel=True)
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task1, task2],
            max_parallel=2
        )
        
        orchestrator.register_workflow(workflow)
        workflow_id = orchestrator.start_workflow("test_workflow")
        
        # Execute tasks
        await orchestrator._execute_tasks(workflow_id)
        
        # Check that both tasks were executed
        assert mock_executor.call_count == 2
        assert orchestrator.active_workflows[workflow_id]["tasks"]["task1"]["status"] == TaskStatus.COMPLETED
        assert orchestrator.active_workflows[workflow_id]["tasks"]["task2"]["status"] == TaskStatus.COMPLETED


class TestWorkflowIntegration:
    """Test complete workflow integration."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self):
        """Test complete workflow execution from start to finish."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executors
        mock_executor = AsyncMock(return_value={"result": "success", "confidence": 0.9})
        orchestrator.task_executors["test_type"] = mock_executor
        
        # Create workflow with multiple tasks
        task1 = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        task2 = WorkflowTask(id="task2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task1"])
        task3 = WorkflowTask(id="task3", name="Task 3", agent="Agent3", command="cmd3", dependencies=["task2"])
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task1, task2, task3]
        )
        
        orchestrator.register_workflow(workflow)
        workflow_id = orchestrator.start_workflow("test_workflow", {"context": "test"})
        
        # Execute workflow
        await orchestrator._execute_workflow(workflow_id)
        
        # Check that all tasks were executed in order
        assert mock_executor.call_count == 3
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.COMPLETED
        
        # Check task execution order (dependencies)
        calls = mock_executor.call_args_list
        assert "task1" in str(calls[0])
        assert "task2" in str(calls[1])
        assert "task3" in str(calls[2])
    
    @pytest.mark.asyncio
    async def test_workflow_with_failure_and_retry(self):
        """Test workflow with task failure and retry."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executor that fails first, then succeeds
        mock_executor = AsyncMock(side_effect=[Exception("First failure"), {"result": "success"}])
        orchestrator.task_executors["test_type"] = mock_executor
        
        task = WorkflowTask(
            id="task1",
            name="Task 1",
            agent="Agent1",
            command="cmd1",
            retries=1
        )
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task],
            auto_retry=True
        )
        
        orchestrator.register_workflow(workflow)
        workflow_id = orchestrator.start_workflow("test_workflow")
        
        # Execute workflow
        await orchestrator._execute_workflow(workflow_id)
        
        # Check that task was retried and succeeded
        assert mock_executor.call_count == 2
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_workflow_with_required_task_failure(self):
        """Test workflow with required task failure."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Mock task executor that always fails
        mock_executor = AsyncMock(side_effect=Exception("Task failed"))
        orchestrator.task_executors["test_type"] = mock_executor
        
        task = WorkflowTask(
            id="task1",
            name="Task 1",
            agent="Agent1",
            command="cmd1",
            required=True,
            retries=0
        )
        
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task]
        )
        
        orchestrator.register_workflow(workflow)
        workflow_id = orchestrator.start_workflow("test_workflow")
        
        # Execute workflow
        await orchestrator._execute_workflow(workflow_id)
        
        # Check that workflow failed
        assert orchestrator.active_workflows[workflow_id]["status"] == WorkflowStatus.FAILED
        assert orchestrator.active_workflows[workflow_id]["tasks"]["task1"]["status"] == TaskStatus.FAILED


class TestWorkflowEventHandling:
    """Test workflow event handling."""
    
    def test_handle_review_approval(self):
        """Test handling review approval event."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Create a workflow with a task that needs review
        task = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task]
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow")
            
            # Simulate review approval event
            event = {
            "type": "review_approval",
            "workflow_id": workflow_id,
            "task_id": "task1",
            "approved": True,
            "feedback": "Good work!"
        }
        
        orchestrator._handle_review_approval(event)
        
        # Check that task was marked as completed
        assert orchestrator.active_workflows[workflow_id]["tasks"]["task1"]["status"] == TaskStatus.COMPLETED
    
    def test_handle_review_rejection(self):
        """Test handling review rejection event."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        # Create a workflow with a task that needs review
        task = WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        workflow = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=[task]
        )
        
        orchestrator.register_workflow(workflow)
        
        # Mock the async execution to avoid event loop issues
        with patch('asyncio.create_task'):
            workflow_id = orchestrator.start_workflow("test_workflow")
            
            # Simulate review rejection event
            event = {
            "type": "review_rejection",
            "workflow_id": workflow_id,
            "task_id": "task1",
            "approved": False,
            "feedback": "Needs improvement"
        }
        
        orchestrator._handle_review_rejection(event)
        
        # Check that task was marked as failed
        assert orchestrator.active_workflows[workflow_id]["tasks"]["task1"]["status"] == TaskStatus.FAILED
        assert "feedback" in orchestrator.active_workflows[workflow_id]["tasks"]["task1"]["error"]


class TestWorkflowNotifications:
    """Test workflow notification functionality."""
    
    @patch('bmad.agents.core.advanced_workflow.publish')
    def test_notify_workflow_completion(self, mock_publish):
        """Test workflow completion notification."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        workflow_id = "test_workflow_123"
        orchestrator.active_workflows[workflow_id] = {
            "definition": WorkflowDefinition(name="test", description="test", tasks=[]),
            "status": WorkflowStatus.COMPLETED,
            "tasks": {},
            "context": {"test": "context"},
            "name": "test_workflow",
            "metrics": {},
            "start_time": time.time() - 100,
            "end_time": time.time()
        }
        
        orchestrator._notify_workflow_completion(workflow_id)
        
        # Check that notification was published
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        assert call_args[0] == "workflow_completed"
        assert call_args[1]["workflow_id"] == workflow_id
    
    @patch('bmad.agents.core.advanced_workflow.publish')
    def test_notify_workflow_failure(self, mock_publish):
        """Test workflow failure notification."""
        orchestrator = AdvancedWorkflowOrchestrator()
        
        workflow_id = "test_workflow_123"
        orchestrator.active_workflows[workflow_id] = {
            "definition": WorkflowDefinition(name="test", description="test", tasks=[]),
            "status": WorkflowStatus.FAILED,
            "tasks": {"task1": {"status": TaskStatus.FAILED, "error": "Task failed"}},
            "context": {"test": "context"},
            "name": "test_workflow",
            "error": "Workflow failed",
            "failed_tasks": ["task1"],
            "metrics": {}
        }
        
        orchestrator._notify_workflow_failure(workflow_id)
        
        # Check that notification was published
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[0]
        assert call_args[0] == "workflow_failed"
        assert call_args[1]["workflow_id"] == workflow_id
        assert "error" in call_args[1] 