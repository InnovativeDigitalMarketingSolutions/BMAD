"""
Tests for bmad.agents.core.langgraph_workflow module.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from bmad.agents.core.langgraph_workflow import (
    LangGraphWorkflowOrchestrator,
    WorkflowDefinition,
    WorkflowTask,
    WorkflowStatus,
    TaskStatus,
    WorkflowState,
    create_workflow_orchestrator,
    register_workflow_definition
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
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        ]
        
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


class TestLangGraphWorkflowOrchestrator:
    """Test LangGraphWorkflowOrchestrator class."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        assert isinstance(orchestrator.workflow_definitions, dict)
        assert isinstance(orchestrator.task_executors, dict)
        assert isinstance(orchestrator.event_handlers, dict)
        assert isinstance(orchestrator.active_workflows, dict)
        
        # Check that default executors are registered
        assert "ProductOwner" in orchestrator.task_executors
        assert "Architect" in orchestrator.task_executors
        assert "FullstackDeveloper" in orchestrator.task_executors
        assert "TestEngineer" in orchestrator.task_executors
    
    def test_register_workflow(self):
        """Test registering a workflow."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="Agent1", command="cmd1")
        ]
        
        workflow_def = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow_def)
        
        assert "test_workflow" in orchestrator.workflow_definitions
        assert orchestrator.workflow_definitions["test_workflow"] == workflow_def
    
    def test_register_task_executor(self):
        """Test registering a task executor."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        def test_executor(task, context):
            return {"output": "test result"}
        
        orchestrator.register_task_executor("TestAgent", test_executor)
        
        assert "TestAgent" in orchestrator.task_executors
        assert orchestrator.task_executors["TestAgent"] == test_executor
    
    def test_start_workflow_success(self):
        """Test starting a workflow successfully."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="ProductOwner", command="cmd1")
        ]
        
        workflow_def = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow_def)
        
        workflow_id = orchestrator.start_workflow("test_workflow", {"test": "context"})
        
        assert workflow_id.startswith("test_workflow_")
        assert workflow_id in orchestrator.active_workflows
    
    def test_start_workflow_not_found(self):
        """Test starting a workflow that doesn't exist."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        with pytest.raises(ValueError, match="Workflow 'nonexistent' niet gevonden"):
            orchestrator.start_workflow("nonexistent")
    
    def test_get_workflow_status(self):
        """Test getting workflow status."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        # Test with non-existent workflow
        status = orchestrator.get_workflow_status("nonexistent")
        assert status is None
        
        # Test with existing workflow (simplified)
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="ProductOwner", command="cmd1")
        ]
        
        workflow_def = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow_def)
        workflow_id = orchestrator.start_workflow("test_workflow")
        
        status = orchestrator.get_workflow_status(workflow_id)
        assert status is not None
        assert "workflow_id" in status
        assert "status" in status
    
    def test_cancel_workflow(self):
        """Test canceling a workflow."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="ProductOwner", command="cmd1")
        ]
        
        workflow_def = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow_def)
        workflow_id = orchestrator.start_workflow("test_workflow")
        
        assert workflow_id in orchestrator.active_workflows
        
        orchestrator.cancel_workflow(workflow_id)
        
        assert workflow_id not in orchestrator.active_workflows
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        # Task with no dependencies
        task_no_deps = WorkflowTask(
            id="task1",
            name="Task 1",
            agent="ProductOwner",
            command="cmd1"
        )
        
        state = {
            "completed_tasks": [],
            "failed_tasks": [],
            "skipped_tasks": []
        }
        
        assert orchestrator._check_dependencies(state, task_no_deps) is True
        
        # Task with dependencies that are met
        task_with_deps = WorkflowTask(
            id="task2",
            name="Task 2",
            agent="ProductOwner",
            command="cmd2",
            dependencies=["task1"]
        )
        
        state["completed_tasks"] = ["task1"]
        
        assert orchestrator._check_dependencies(state, task_with_deps) is True
        
        # Task with dependencies that are not met
        state["completed_tasks"] = []
        
        assert orchestrator._check_dependencies(state, task_with_deps) is False
    
    def test_should_skip_task(self):
        """Test task skip logic."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        task = WorkflowTask(
            id="task1",
            name="Task 1",
            agent="ProductOwner",
            command="cmd1",
            required=False
        )
        
        state = {}
        
        # Currently always returns False
        assert orchestrator._should_skip_task(state, task) is False


class TestLangGraphWorkflowOrchestratorAsync:
    """Test async methods of LangGraphWorkflowOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_execute_product_owner_task(self):
        """Test ProductOwner task execution."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="ProductOwner",
            command="create_user_story"
        )
        
        context = {"project": "test_project"}
        
        result = await orchestrator._execute_product_owner_task(task, context)
        
        assert isinstance(result, dict)
        assert "output" in result
        assert "agent" in result
        assert "task_id" in result
        assert result["agent"] == "ProductOwner"
        assert result["task_id"] == "test_task"
        assert "create_user_story" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_architect_task(self):
        """Test Architect task execution."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="Architect",
            command="design_system"
        )
        
        context = {"project": "test_project"}
        
        result = await orchestrator._execute_architect_task(task, context)
        
        assert isinstance(result, dict)
        assert "output" in result
        assert "agent" in result
        assert "task_id" in result
        assert result["agent"] == "Architect"
        assert result["task_id"] == "test_task"
        assert "design_system" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_fullstack_task(self):
        """Test FullstackDeveloper task execution."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="FullstackDeveloper",
            command="implement_feature"
        )
        
        context = {"project": "test_project"}
        
        result = await orchestrator._execute_fullstack_task(task, context)
        
        assert isinstance(result, dict)
        assert "output" in result
        assert "agent" in result
        assert "task_id" in result
        assert result["agent"] == "FullstackDeveloper"
        assert result["task_id"] == "test_task"
        assert "implement_feature" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_test_task(self):
        """Test TestEngineer task execution."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="TestEngineer",
            command="run_tests"
        )
        
        context = {"project": "test_project"}
        
        result = await orchestrator._execute_test_task(task, context)
        
        assert isinstance(result, dict)
        assert "output" in result
        assert "agent" in result
        assert "task_id" in result
        assert result["agent"] == "TestEngineer"
        assert result["task_id"] == "test_task"
        assert "run_tests" in result["output"]
    
    @pytest.mark.asyncio
    async def test_retry_task(self):
        """Test task retry logic."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="ProductOwner",
            command="test_command",
            retries=2
        )
        
        state = {
            "failed_tasks": ["test_task"],
            "task_errors": {"test_task": "Test error"}
        }
        
        initial_retries = task.retries
        
        await orchestrator._retry_task(state, task)
        
        # Check that retries decreased
        assert task.retries == initial_retries - 1
        
        # Check that task was removed from failed tasks
        assert "test_task" not in state["failed_tasks"]
        assert "test_task" not in state["task_errors"]


class TestWorkflowIntegration:
    """Test complete workflow integration."""
    
    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self):
        """Test a simple workflow with one task."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        tasks = [
            WorkflowTask(
                id="task1",
                name="Create User Story",
                agent="ProductOwner",
                command="create_user_story"
            )
        ]
        
        workflow_def = WorkflowDefinition(
            name="simple_workflow",
            description="Simple test workflow",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow_def)
        
        workflow_id = orchestrator.start_workflow("simple_workflow", {"project": "test"})
        
        assert workflow_id.startswith("simple_workflow_")
        assert workflow_id in orchestrator.active_workflows
        
        # Wait a bit for async execution
        await asyncio.sleep(0.1)
        
        # Check status
        status = orchestrator.get_workflow_status(workflow_id)
        assert status is not None
    
    @pytest.mark.asyncio
    async def test_workflow_with_dependencies(self):
        """Test workflow with task dependencies."""
        orchestrator = LangGraphWorkflowOrchestrator()
        
        tasks = [
            WorkflowTask(
                id="task1",
                name="Create User Story",
                agent="ProductOwner",
                command="create_user_story"
            ),
            WorkflowTask(
                id="task2",
                name="Design System",
                agent="Architect",
                command="design_system",
                dependencies=["task1"]
            )
        ]
        
        workflow_def = WorkflowDefinition(
            name="dependency_workflow",
            description="Workflow with dependencies",
            tasks=tasks
        )
        
        orchestrator.register_workflow(workflow_def)
        
        workflow_id = orchestrator.start_workflow("dependency_workflow", {"project": "test"})
        
        assert workflow_id.startswith("dependency_workflow_")
        assert workflow_id in orchestrator.active_workflows
        
        # For now, just test that the workflow was created successfully
        # The actual execution will be tested in integration tests
        assert workflow_id is not None


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_workflow_orchestrator(self):
        """Test create_workflow_orchestrator function."""
        orchestrator = create_workflow_orchestrator()
        
        assert isinstance(orchestrator, LangGraphWorkflowOrchestrator)
        assert "ProductOwner" in orchestrator.task_executors
    
    def test_register_workflow_definition(self):
        """Test register_workflow_definition function."""
        tasks = [
            WorkflowTask(id="task1", name="Task 1", agent="ProductOwner", command="cmd1")
        ]
        
        workflow_def = register_workflow_definition(
            name="test_workflow",
            description="Test workflow",
            tasks=tasks,
            max_parallel=5
        )
        
        assert isinstance(workflow_def, WorkflowDefinition)
        assert workflow_def.name == "test_workflow"
        assert workflow_def.description == "Test workflow"
        assert len(workflow_def.tasks) == 1
        assert workflow_def.max_parallel == 5


class TestWorkflowState:
    """Test WorkflowState TypedDict."""
    
    def test_workflow_state_structure(self):
        """Test WorkflowState structure."""
        state = WorkflowState(
            workflow_id="test_workflow_123",
            workflow_name="test_workflow",
            current_task=None,
            completed_tasks=[],
            failed_tasks=[],
            skipped_tasks=[],
            task_results={},
            task_errors={},
            context={"project": "test"},
            status="pending",
            start_time=time.time(),
            end_time=None,
            metrics={
                "completed_tasks": 0,
                "failed_tasks": 0,
                "skipped_tasks": 0,
                "total_tasks": 1
            }
        )
        
        assert state["workflow_id"] == "test_workflow_123"
        assert state["workflow_name"] == "test_workflow"
        assert state["current_task"] is None
        assert isinstance(state["completed_tasks"], list)
        assert isinstance(state["failed_tasks"], list)
        assert isinstance(state["skipped_tasks"], list)
        assert isinstance(state["task_results"], dict)
        assert isinstance(state["task_errors"], dict)
        assert isinstance(state["context"], dict)
        assert state["status"] == "pending"
        assert isinstance(state["start_time"], float)
        assert state["end_time"] is None
        assert isinstance(state["metrics"], dict) 