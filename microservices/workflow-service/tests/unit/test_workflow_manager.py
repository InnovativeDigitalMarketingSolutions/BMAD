"""
Unit tests for WorkflowManager
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.workflow_manager import (
    WorkflowManager, Workflow, WorkflowExecution, 
    WorkflowType, WorkflowStatus, WorkflowStep
)


class TestWorkflowManager:
    """Test cases for WorkflowManager."""
    
    @pytest.fixture
    def workflow_manager(self):
        """Create a WorkflowManager instance for testing."""
        return WorkflowManager()
        
    @pytest.fixture
    def sample_workflow_data(self):
        """Sample workflow data for testing."""
        return {
            "name": "Test Workflow",
            "workflow_type": WorkflowType.SEQUENTIAL,
            "description": "A test workflow",
            "steps": [
                {
                    "name": "Step 1",
                    "step_type": "agent_execution",
                    "agent_id": "agent_001",
                    "config": {"timeout": 30}
                },
                {
                    "name": "Step 2", 
                    "step_type": "data_processing",
                    "config": {"batch_size": 100}
                }
            ],
            "config": {"max_retries": 3},
            "metadata": {"created_by": "test_user"},
            "tags": ["test", "workflow"]
        }
        
    @pytest.mark.asyncio
    async def test_create_workflow(self, workflow_manager, sample_workflow_data):
        """Test workflow creation."""
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"],
            description=sample_workflow_data["description"],
            steps=sample_workflow_data["steps"],
            config=sample_workflow_data["config"],
            metadata=sample_workflow_data["metadata"],
            tags=sample_workflow_data["tags"]
        )
        
        assert workflow is not None
        assert workflow.name == sample_workflow_data["name"]
        assert workflow.workflow_type == sample_workflow_data["workflow_type"]
        assert workflow.description == sample_workflow_data["description"]
        assert len(workflow.steps) == 2
        assert workflow.config == sample_workflow_data["config"]
        assert workflow.metadata == sample_workflow_data["metadata"]
        assert workflow.tags == sample_workflow_data["tags"]
        assert workflow.status == WorkflowStatus.DRAFT
        
    @pytest.mark.asyncio
    async def test_get_workflow(self, workflow_manager, sample_workflow_data):
        """Test getting workflow by ID."""
        # Create workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        
        # Get workflow
        retrieved_workflow = await workflow_manager.get_workflow(workflow.id)
        
        assert retrieved_workflow is not None
        assert retrieved_workflow.id == workflow.id
        assert retrieved_workflow.name == workflow.name
        
    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, workflow_manager):
        """Test getting non-existent workflow."""
        workflow = await workflow_manager.get_workflow("non-existent-id")
        assert workflow is None
        
    @pytest.mark.asyncio
    async def test_update_workflow(self, workflow_manager, sample_workflow_data):
        """Test workflow update."""
        # Create workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        
        # Update workflow
        updates = {
            "name": "Updated Workflow",
            "description": "Updated description",
            "status": WorkflowStatus.ACTIVE
        }
        
        updated_workflow = await workflow_manager.update_workflow(workflow.id, updates)
        
        assert updated_workflow is not None
        assert updated_workflow.name == "Updated Workflow"
        assert updated_workflow.description == "Updated description"
        assert updated_workflow.status == WorkflowStatus.ACTIVE
        
    @pytest.mark.asyncio
    async def test_delete_workflow(self, workflow_manager, sample_workflow_data):
        """Test workflow deletion."""
        # Create workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        
        # Delete workflow
        success = await workflow_manager.delete_workflow(workflow.id)
        assert success is True
        
        # Verify workflow is deleted
        retrieved_workflow = await workflow_manager.get_workflow(workflow.id)
        assert retrieved_workflow is None
        
    @pytest.mark.asyncio
    async def test_list_workflows(self, workflow_manager, sample_workflow_data):
        """Test listing workflows."""
        # Create multiple workflows
        workflow1 = await workflow_manager.create_workflow(
            name="Workflow 1",
            workflow_type=WorkflowType.SEQUENTIAL
        )
        workflow2 = await workflow_manager.create_workflow(
            name="Workflow 2", 
            workflow_type=WorkflowType.PARALLEL
        )
        
        # List all workflows
        workflows = await workflow_manager.list_workflows()
        assert len(workflows) >= 2
        
        # Filter by type
        sequential_workflows = await workflow_manager.list_workflows(
            workflow_type=WorkflowType.SEQUENTIAL
        )
        assert len(sequential_workflows) >= 1
        assert all(w.workflow_type == WorkflowType.SEQUENTIAL for w in sequential_workflows)
        
    @pytest.mark.asyncio
    async def test_execute_workflow(self, workflow_manager, sample_workflow_data):
        """Test workflow execution."""
        # Create workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"],
            steps=sample_workflow_data["steps"]
        )
        
        # Execute workflow
        execution = await workflow_manager.execute_workflow(
            workflow_id=workflow.id,
            input_data={"test_input": "value"}
        )
        
        assert execution is not None
        assert execution.workflow_id == workflow.id
        assert execution.input_data == {"test_input": "value"}
        assert execution.status in [WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED]
        
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, workflow_manager):
        """Test executing non-existent workflow."""
        execution = await workflow_manager.execute_workflow("non-existent-id")
        assert execution is None
        
    @pytest.mark.asyncio
    async def test_get_execution(self, workflow_manager, sample_workflow_data):
        """Test getting execution by ID."""
        # Create and execute workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        execution = await workflow_manager.execute_workflow(workflow.id)
        
        # Get execution
        retrieved_execution = await workflow_manager.get_execution(execution.id)
        
        assert retrieved_execution is not None
        assert retrieved_execution.id == execution.id
        assert retrieved_execution.workflow_id == workflow.id
        
    @pytest.mark.asyncio
    async def test_list_executions(self, workflow_manager, sample_workflow_data):
        """Test listing executions."""
        # Create and execute workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        execution1 = await workflow_manager.execute_workflow(workflow.id)
        execution2 = await workflow_manager.execute_workflow(workflow.id)
        
        # List executions
        executions = await workflow_manager.list_executions()
        assert len(executions) >= 2
        
        # Filter by workflow
        workflow_executions = await workflow_manager.list_executions(
            workflow_id=workflow.id
        )
        assert len(workflow_executions) >= 2
        assert all(e.workflow_id == workflow.id for e in workflow_executions)
        
    @pytest.mark.asyncio
    async def test_cancel_execution(self, workflow_manager, sample_workflow_data):
        """Test execution cancellation."""
        # Create and execute workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        execution = await workflow_manager.execute_workflow(workflow.id)
        
        # Cancel execution
        success = await workflow_manager.cancel_execution(execution.id)
        assert success is True
        
        # Verify execution is cancelled
        cancelled_execution = await workflow_manager.get_execution(execution.id)
        assert cancelled_execution.status == WorkflowStatus.CANCELLED
        
    @pytest.mark.asyncio
    async def test_get_workflow_stats(self, workflow_manager, sample_workflow_data):
        """Test getting workflow statistics."""
        # Create and execute workflow
        workflow = await workflow_manager.create_workflow(
            name=sample_workflow_data["name"],
            workflow_type=sample_workflow_data["workflow_type"]
        )
        await workflow_manager.execute_workflow(workflow.id)
        
        # Get stats
        stats = await workflow_manager.get_workflow_stats()
        
        assert stats is not None
        assert "total_workflows" in stats
        assert "total_executions" in stats
        assert "workflow_types" in stats
        assert "status_distribution" in stats
        assert stats["total_workflows"] >= 1
        assert stats["total_executions"] >= 1
        
    @pytest.mark.asyncio
    async def test_health_check(self, workflow_manager):
        """Test health check."""
        health = await workflow_manager.health_check()
        
        assert health is not None
        assert "status" in health
        assert "total_workflows" in health
        assert "total_executions" in health
        assert "store_available" in health
        assert "orchestrator_available" in health
        
    @pytest.mark.asyncio
    async def test_sequential_execution(self, workflow_manager):
        """Test sequential workflow execution."""
        workflow = await workflow_manager.create_workflow(
            name="Sequential Test",
            workflow_type=WorkflowType.SEQUENTIAL,
            steps=[
                {"name": "Step 1", "step_type": "test"},
                {"name": "Step 2", "step_type": "test"}
            ]
        )
        
        execution = await workflow_manager.execute_workflow(workflow.id)
        
        # Wait for execution to complete
        await asyncio.sleep(2)
        
        # Get updated execution
        updated_execution = await workflow_manager.get_execution(execution.id)
        assert updated_execution.status == WorkflowStatus.COMPLETED
        
    @pytest.mark.asyncio
    async def test_parallel_execution(self, workflow_manager):
        """Test parallel workflow execution."""
        workflow = await workflow_manager.create_workflow(
            name="Parallel Test",
            workflow_type=WorkflowType.PARALLEL,
            steps=[
                {"name": "Step 1", "step_type": "test"},
                {"name": "Step 2", "step_type": "test"}
            ]
        )
        
        execution = await workflow_manager.execute_workflow(workflow.id)
        
        # Wait for execution to complete
        await asyncio.sleep(2)
        
        # Get updated execution
        updated_execution = await workflow_manager.get_execution(execution.id)
        assert updated_execution.status == WorkflowStatus.COMPLETED
        
    @pytest.mark.asyncio
    async def test_conditional_execution(self, workflow_manager):
        """Test conditional workflow execution."""
        workflow = await workflow_manager.create_workflow(
            name="Conditional Test",
            workflow_type=WorkflowType.CONDITIONAL,
            config={"condition": True},
            steps=[
                {"name": "Conditional Step", "step_type": "test"}
            ]
        )
        
        execution = await workflow_manager.execute_workflow(workflow.id)
        
        # Wait for execution to complete
        await asyncio.sleep(2)
        
        # Get updated execution
        updated_execution = await workflow_manager.get_execution(execution.id)
        assert updated_execution.status == WorkflowStatus.COMPLETED 