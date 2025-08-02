import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.agents.Agent.WorkflowAutomator.workflowautomator import (
    WorkflowAutomatorAgent,
    WorkflowError,
    WorkflowValidationError,
    WorkflowExecutionError,
    WorkflowStatus,
    WorkflowPriority,
    WorkflowStep,
    Workflow
)


class TestWorkflowAutomatorAgent:
    """Test suite for WorkflowAutomatorAgent."""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test."""
        agent = WorkflowAutomatorAgent()
        # Reset state for each test
        agent.workflows = {}
        agent.execution_history = []
        agent.performance_metrics = {}
        agent.scheduled_workflows = {}
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_name == "WorkflowAutomator"
        assert isinstance(agent.workflows, dict)
        assert isinstance(agent.execution_history, list)
        assert isinstance(agent.performance_metrics, dict)
        assert isinstance(agent.scheduled_workflows, dict)

    @pytest.mark.asyncio
    async def test_validate_input_success(self, agent):
        """Test successful input validation."""
        assert agent._validate_input("test")
        assert agent._validate_input(42)
        assert agent._validate_input(True)

    @pytest.mark.asyncio
    async def test_validate_input_failure(self, agent):
        """Test input validation failure."""
        assert not agent._validate_input(None)
        assert not agent._validate_input("")

    def test_show_help(self, agent, capsys):
        """Test show_help method."""
        await agent.show_help()
        captured = capsys.readouterr()
        assert "WorkflowAutomator Agent" in captured.out
        assert "create-workflow" in captured.out
        assert "execute-workflow" in captured.out
        assert "optimize-workflow" in captured.out
        assert "monitor-workflow" in captured.out

    @pytest.mark.asyncio
    async def test_create_workflow_success(self, agent):
        """Test successful workflow creation."""
        result = agent.create_workflow(
            name="Test Workflow",
            description="Test workflow for unit testing",
            agents=["ProductOwner", "TestEngineer"],
            commands=["create-story", "run-tests"],
            priority="normal"
        )
        
        assert result["status"] == "created"
        assert "workflow_id" in result
        assert result["name"] == "Test Workflow"
        assert result["description"] == "Test workflow for unit testing"
        assert len(result["steps"]) == 2
        assert result["priority"] == "normal"

    def test_create_workflow_empty_name(self, agent):
        """Test workflow creation with empty name."""
        with pytest.raises(WorkflowValidationError, match="Invalid input parameters"):
            agent.create_workflow(
                name="",
                description="Test",
                agents=["ProductOwner"],
                commands=["create-story"]
            )

    def test_create_workflow_mismatched_agents_commands(self, agent):
        """Test workflow creation with mismatched agents and commands."""
        with pytest.raises(WorkflowValidationError, match="Number of agents and commands must match"):
            agent.create_workflow(
                name="Test",
                description="Test",
                agents=["ProductOwner", "TestEngineer"],
                commands=["create-story"]
            )

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, agent):
        """Test successful workflow execution."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then execute it
        result = await agent.execute_workflow(workflow_id)
        
        assert result["status"] == "executed"
        assert result["workflow_id"] == workflow_id
        assert "execution_time" in result

    def test_execute_workflow_not_found(self, agent):
        """Test workflow execution with non-existent workflow."""
        with pytest.raises(WorkflowExecutionError, match="Workflow non-existent-id not found"):
            await agent.execute_workflow("non-existent-id")

    @pytest.mark.asyncio
    async def test_optimize_workflow_success(self, agent):
        """Test successful workflow optimization."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then optimize it
        result = agent.optimize_workflow(workflow_id)
        
        assert result["status"] == "optimized"
        assert result["workflow_id"] == workflow_id
        assert "optimizations" in result

    def test_optimize_workflow_not_found(self, agent):
        """Test workflow optimization with non-existent workflow."""
        with pytest.raises(WorkflowExecutionError, match="Workflow non-existent-id not found"):
            agent.optimize_workflow("non-existent-id")

    @pytest.mark.asyncio
    async def test_monitor_workflow_success(self, agent):
        """Test successful workflow monitoring."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then monitor it
        result = agent.monitor_workflow(workflow_id)
        
        assert result["status"] == "monitored"
        assert result["workflow_id"] == workflow_id
        assert "metrics" in result

    def test_monitor_workflow_not_found(self, agent):
        """Test workflow monitoring with non-existent workflow."""
        with pytest.raises(WorkflowExecutionError, match="Workflow non-existent-id not found"):
            agent.monitor_workflow("non-existent-id")

    @pytest.mark.asyncio
    async def test_schedule_workflow_success(self, agent):
        """Test successful workflow scheduling."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then schedule it
        result = agent.schedule_workflow(workflow_id, "daily 09:00")
        
        assert result["status"] == "scheduled"
        assert result["workflow_id"] == workflow_id
        assert "schedule" in result

    @pytest.mark.asyncio
    async def test_pause_workflow_success(self, agent):
        """Test successful workflow pausing."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Set workflow status to running first
        from bmad.agents.Agent.WorkflowAutomator.workflowautomator import WorkflowStatus
        workflow = agent.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        
        # Then pause it
        result = agent.pause_workflow(workflow_id)
        
        assert result["status"] == "paused"
        assert result["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_resume_workflow_success(self, agent):
        """Test successful workflow resuming."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Set workflow status to paused first
        from bmad.agents.Agent.WorkflowAutomator.workflowautomator import WorkflowStatus
        workflow = agent.workflows[workflow_id]
        workflow.status = WorkflowStatus.PAUSED
        
        # Then resume it
        result = agent.resume_workflow(workflow_id)
        
        assert result["status"] == "resumed"
        assert result["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_cancel_workflow_success(self, agent):
        """Test successful workflow cancellation."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then cancel it
        result = agent.cancel_workflow(workflow_id)
        
        assert result["status"] == "cancelled"
        assert result["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_analyze_workflow_success(self, agent):
        """Test successful workflow analysis."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then analyze it
        result = agent.analyze_workflow(workflow_id)
        
        assert result["status"] == "analyzed"
        assert result["workflow_id"] == workflow_id
        assert "analysis" in result

    @pytest.mark.asyncio
    async def test_auto_recover_success(self, agent):
        """Test successful auto recovery."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then auto recover it
        result = agent.auto_recover(workflow_id)
        
        assert result["status"] == "recovered"
        assert result["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_parallel_execution_success(self, agent):
        """Test successful parallel execution."""
        # Create multiple workflows
        workflow1 = agent.create_workflow(
            name="Workflow 1",
            description="Test workflow 1",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow2 = agent.create_workflow(
            name="Workflow 2",
            description="Test workflow 2",
            agents=["TestEngineer"],
            commands=["run-tests"],
            priority="normal"
        )
        
        # Execute in parallel
        result = agent.parallel_execution([workflow1["workflow_id"], workflow2["workflow_id"]])
        
        assert result["status"] == "executed"
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_conditional_execution_success(self, agent):
        """Test successful conditional execution."""
        # First create a workflow
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        # Then execute conditionally
        result = await agent.conditional_execution(workflow_id, "true")
        
        assert result["status"] == "executed"
        assert result["workflow_id"] == workflow_id

    def test_show_workflow_history(self, agent, capsys):
        """Test show_workflow_history method."""
        agent.show_workflow_history()
        captured = capsys.readouterr()
        assert "workflow" in captured.out.lower()

    def test_show_performance_metrics(self, agent, capsys):
        """Test show_performance_metrics method."""
        agent.show_performance_metrics()
        captured = capsys.readouterr()
        assert "performance" in captured.out.lower()

    def test_show_automation_stats(self, agent, capsys):
        """Test show_automation_stats method."""
        agent.show_automation_stats()
        captured = capsys.readouterr()
        assert "Workflow Automation Statistics" in captured.out

    def test_test_resource_completeness(self, agent, capsys):
        """Test test_resource_completeness method."""
        result = agent.test_resource_completeness()
        assert result["status"] == "complete"
        assert len(result["missing_resources"]) == 0

    @pytest.mark.asyncio
    async def test_collaborate_example(self, agent, capsys):
        """Test collaborate_example method."""
        result = await agent.collaborate_example()
        assert result["status"] == "collaboration_completed"

    def test_handle_workflow_execution_requested(self, agent):
        """Test workflow execution requested event handler."""
        # Create a workflow first
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        event_data = {"workflow_id": workflow_id}
        agent.handle_workflow_execution_requested(event_data)
        # Should not raise any exceptions

    def test_handle_workflow_pause_requested(self, agent):
        """Test workflow pause requested event handler."""
        event_data = {"workflow_id": "test-123"}
        agent.handle_workflow_pause_requested(event_data)
        # Should not raise any exceptions

    def test_handle_workflow_resume_requested(self, agent):
        """Test workflow resume requested event handler."""
        event_data = {"workflow_id": "test-123"}
        agent.handle_workflow_resume_requested(event_data)
        # Should not raise any exceptions

    def test_handle_workflow_cancel_requested(self, agent):
        """Test workflow cancel requested event handler."""
        event_data = {"workflow_id": "test-123"}
        agent.handle_workflow_cancel_requested(event_data)
        # Should not raise any exceptions

    def test_handle_workflow_optimization_requested(self, agent):
        """Test workflow optimization requested event handler."""
        # Create a workflow first
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        event_data = {"workflow_id": workflow_id}
        agent.handle_workflow_optimization_requested(event_data)
        # Should not raise any exceptions

    def test_handle_workflow_monitoring_requested(self, agent):
        """Test workflow monitoring requested event handler."""
        # Create a workflow first
        workflow_result = await agent.create_workflow(
            name="Test Workflow",
            description="Test workflow",
            agents=["ProductOwner"],
            commands=["create-story"],
            priority="normal"
        )
        workflow_id = workflow_result["workflow_id"]
        
        event_data = {"workflow_id": workflow_id}
        agent.handle_workflow_monitoring_requested(event_data)
        # Should not raise any exceptions

    def test_evaluate_condition_true(self, agent):
        """Test condition evaluation with true condition."""
        result = agent._evaluate_condition("true")
        assert result is True

    def test_evaluate_condition_false(self, agent):
        """Test condition evaluation with false condition."""
        result = agent._evaluate_condition("false")
        assert result is False

    def test_evaluate_condition_complex(self, agent):
        """Test condition evaluation with complex condition."""
        result = agent._evaluate_condition("1 == 1")
        assert result is True

    def test_workflow_step_creation(self):
        """Test WorkflowStep dataclass creation."""
        step = WorkflowStep(
            id="test-step",
            agent="ProductOwner",
            command="create-story",
            parameters={"param1": "value1"},
            dependencies=["step1"],
            timeout=300,
            retry_count=3
        )
        
        assert step.id == "test-step"
        assert step.agent == "ProductOwner"
        assert step.command == "create-story"
        assert step.parameters == {"param1": "value1"}
        assert step.dependencies == ["step1"]
        assert step.timeout == 300
        assert step.retry_count == 3
        assert step.status == WorkflowStatus.PENDING

    def test_workflow_creation(self):
        """Test Workflow dataclass creation."""
        steps = [
            WorkflowStep(
                id="step1",
                agent="ProductOwner",
                command="create-story",
                parameters={},
                dependencies=[]
            )
        ]
        
        workflow = Workflow(
            id="test-workflow",
            name="Test Workflow",
            description="Test workflow",
            steps=steps,
            priority=WorkflowPriority.NORMAL,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert workflow.id == "test-workflow"
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test workflow"
        assert len(workflow.steps) == 1
        assert workflow.priority == WorkflowPriority.NORMAL
        assert workflow.status == WorkflowStatus.PENDING 