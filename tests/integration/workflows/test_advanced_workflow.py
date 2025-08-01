#!/usr/bin/env python3
"""
Test script voor advanced workflow orchestrator
"""
import os
import sys
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mock Prefect to avoid Pydantic compatibility issues
import unittest.mock
sys.modules['prefect'] = unittest.mock.MagicMock()
sys.modules['prefect.flow'] = unittest.mock.MagicMock()
sys.modules['prefect.deployments'] = unittest.mock.MagicMock()

import pytest
from bmad.agents.core.workflow.integrated_workflow_orchestrator import (
    IntegratedWorkflowOrchestrator, 
    WorkflowDefinition, 
    WorkflowTask, 
    WorkflowStatus, 
    TaskStatus
)

def test_workflow_definition():
    """Test workflow definition creatie."""
    # Maak een eenvoudige workflow definitie
    tasks = [
        WorkflowTask(
            id="po_1",
            name="Create User Stories",
            agent="ProductOwner",
            command="create-story"
        ),
        WorkflowTask(
            id="arch_1",
            name="Design Architecture",
            agent="Architect",
            command="design-system",
            dependencies=["po_1"]
        ),
        WorkflowTask(
            id="dev_1",
            name="Implement Frontend",
            agent="FullstackDeveloper",
            command="build-frontend",
            dependencies=["arch_1"]
        ),
        WorkflowTask(
            id="test_1",
            name="Run Tests",
            agent="TestEngineer",
            command="run-tests",
            dependencies=["dev_1"]
        ),
        WorkflowTask(
            id="quality_1",
            name="Quality Gate Check",
            agent="QualityGuardian",
            command="quality-gate-check",
            dependencies=["test_1"]
        )
    ]
    
    workflow_def = WorkflowDefinition(
        name="frontend_development",
        description="Complete frontend development workflow",
        tasks=tasks
    )
    
    # Test workflow definitie
    assert workflow_def.name == "frontend_development"
    assert len(workflow_def.tasks) == 5
    assert workflow_def.tasks[0].id == "po_1"
    assert workflow_def.tasks[1].dependencies == ["po_1"]
    assert workflow_def.tasks[4].agent == "QualityGuardian"

def test_workflow_registration():
    """Test workflow registratie."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Maak workflow definitie
    tasks = [
        WorkflowTask(
            id="task_1",
            name="Test Task",
            agent="ProductOwner",
            command="test"
        )
    ]
    
    workflow_def = WorkflowDefinition(
        name="test_workflow",
        description="Test workflow",
        tasks=tasks
    )
    
    # Registreer workflow
    orchestrator.register_workflow(workflow_def)
    
    # Check dat workflow geregistreerd is
    assert "test_workflow" in orchestrator.workflow_definitions
    assert orchestrator.workflow_definitions["test_workflow"] == workflow_def

def test_task_dependency_grouping():
    """Test task dependency grouping."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Maak taken met dependencies
    tasks = {
        "task_1": WorkflowTask(id="task_1", name="Task 1", agent="Agent1", command="cmd1"),
        "task_2": WorkflowTask(id="task_2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task_1"]),
        "task_3": WorkflowTask(id="task_3", name="Task 3", agent="Agent3", command="cmd3", dependencies=["task_1"]),
        "task_4": WorkflowTask(id="task_4", name="Task 4", agent="Agent4", command="cmd4", dependencies=["task_2", "task_3"])
    }
    
    # Group tasks by dependency
    groups = orchestrator._group_tasks_by_dependency(tasks)
    
    # Check grouping
    assert len(groups) == 3  # 3 dependency levels
    assert any(task.id == "task_1" for task in groups[0])  # First level (no dependencies)
    assert any(task.id == "task_2" for task in groups[1]) and any(task.id == "task_3" for task in groups[1])  # Second level
    assert any(task.id == "task_4" for task in groups[2])  # Third level

def test_dependency_checking():
    """Test dependency checking."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Setup workflow state
    workflow_id = "test_workflow"
    orchestrator.active_workflows[workflow_id] = {
        "tasks": {
            "task_1": WorkflowTask(id="task_1", name="Task 1", agent="Agent1", command="cmd1", status=TaskStatus.COMPLETED),
            "task_2": WorkflowTask(id="task_2", name="Task 2", agent="Agent2", command="cmd2", dependencies=["task_1"], status=TaskStatus.PENDING)
        }
    }
    
    # Test dependency check
    assert orchestrator._check_dependencies(workflow_id, "task_2")
    
    # Test failed dependency
    orchestrator.active_workflows[workflow_id]["tasks"]["task_1"].status = TaskStatus.FAILED
    assert not orchestrator._check_dependencies(workflow_id, "task_2")

@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Maak een eenvoudige workflow
    tasks = [
        WorkflowTask(
            id="po_1",
            name="Create User Stories",
            agent="ProductOwner",
            command="create-story"
        ),
        WorkflowTask(
            id="arch_1",
            name="Design Architecture",
            agent="Architect",
            command="design-system",
            dependencies=["po_1"]
        )
    ]
    
    workflow_def = WorkflowDefinition(
        name="simple_workflow",
        description="Simple test workflow",
        tasks=tasks
    )
    
    # Registreer workflow
    orchestrator.register_workflow(workflow_def)
    
    # Start workflow
    workflow_id = orchestrator.start_workflow("simple_workflow", {"project": "test"})
    
    # Wacht even voor execution
    await asyncio.sleep(1)
    
    # Check workflow status
    status = orchestrator.get_workflow_status(workflow_id)
    assert status is not None
    assert status["name"] == "simple_workflow"
    assert status["status"] in [WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED]  # Compare enums instead of strings

def test_workflow_status_tracking():
    """Test workflow status tracking."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Setup mock workflow
    workflow_id = "test_workflow"
    orchestrator.active_workflows[workflow_id] = {
        "id": workflow_id,
        "name": "test_workflow",
        "status": WorkflowStatus.RUNNING,
        "start_time": 1000.0,
        "end_time": None,
        "metrics": {
            "total_tasks": 2,
            "completed_tasks": 1,
            "failed_tasks": 0
        },
        "tasks": {
            "task_1": {
                "id": "task_1",
                "status": "completed",
                "confidence": 0.85,
                "result": {"output": "Task 1 completed"}
            },
            "task_2": {
                "id": "task_2",
                "status": "pending",
                "confidence": None,
                "result": None
            }
        }
    }
    
    # Get status
    status = orchestrator.get_workflow_status(workflow_id)
    
    # Check status
    assert status["id"] == workflow_id
    assert status["name"] == "test_workflow"
    assert status["status"] == WorkflowStatus.RUNNING  # Compare enum instead of string
    assert status["metrics"]["total_tasks"] == 2
    assert status["metrics"]["completed_tasks"] == 1
    assert len(status["tasks"]) == 2
    assert status["tasks"]["task_1"]["status"] == "completed"
    assert status["tasks"]["task_1"]["confidence"] == 0.85

def test_workflow_cancellation():
    """Test workflow cancellation."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Setup mock workflow
    workflow_id = "test_workflow"
    orchestrator.active_workflows[workflow_id] = {
        "id": workflow_id,
        "name": "test_workflow",
        "status": WorkflowStatus.RUNNING,
        "start_time": 1000.0,
        "end_time": None
    }
    
    # Cancel workflow
    orchestrator.cancel_workflow(workflow_id)
    
    # Check status - accept either CANCELLED or FAILED
    workflow = orchestrator.active_workflows[workflow_id]
    assert workflow["status"] in [WorkflowStatus.CANCELLED, WorkflowStatus.FAILED]
    assert workflow["end_time"] is not None

def test_parallel_task_execution():
    """Test parallel task execution."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Maak taken die parallel kunnen worden uitgevoerd
    tasks = {
        "task_1": WorkflowTask(id="task_1", name="Task 1", agent="Agent1", command="cmd1", parallel=True),
        "task_2": WorkflowTask(id="task_2", name="Task 2", agent="Agent2", command="cmd2", parallel=True),
        "task_3": WorkflowTask(id="task_3", name="Task 3", agent="Agent3", command="cmd3", dependencies=["task_1", "task_2"])
    }
    
    # Group tasks by dependency
    groups = orchestrator._group_tasks_by_dependency(tasks)
    
    # Check dat parallel tasks in dezelfde group zitten
    assert len(groups) == 2  # 2 dependency levels
    assert any(task.id == "task_1" for task in groups[0]) and any(task.id == "task_2" for task in groups[0])  # Parallel tasks
    assert any(task.id == "task_3" for task in groups[1])  # Dependent task

def test_task_executor_registration():
    """Test task executor registratie."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Test custom executor
    def custom_executor(task, context):
        return {"output": f"Custom execution for {task.name}"}
    
    orchestrator.register_task_executor("CustomAgent", custom_executor)
    
    # Check dat executor geregistreerd is
    assert "CustomAgent" in orchestrator.task_executors
    assert orchestrator.task_executors["CustomAgent"] == custom_executor

def test_qualityguardian_workflow_integration():
    """Test QualityGuardian agent workflow integratie."""
    orchestrator = IntegratedWorkflowOrchestrator()
    
    # Maak workflow met QualityGuardian integratie
    tasks = [
        WorkflowTask(
            id="dev_1",
            name="Develop Feature",
            agent="FullstackDeveloper",
            command="build-component"
        ),
        WorkflowTask(
            id="test_1",
            name="Run Tests",
            agent="TestEngineer",
            command="run-tests",
            dependencies=["dev_1"]
        ),
        WorkflowTask(
            id="quality_1",
            name="Quality Analysis",
            agent="QualityGuardian",
            command="analyze-code-quality",
            dependencies=["dev_1"]
        ),
        WorkflowTask(
            id="security_1",
            name="Security Scan",
            agent="QualityGuardian",
            command="security-scan",
            dependencies=["dev_1"]
        ),
        WorkflowTask(
            id="quality_gate_1",
            name="Quality Gate Check",
            agent="QualityGuardian",
            command="quality-gate-check",
            dependencies=["test_1", "quality_1", "security_1"]
        )
    ]
    
    workflow_def = WorkflowDefinition(
        name="quality_assured_development",
        description="Development workflow with quality assurance",
        tasks=tasks
    )
    
    # Test workflow definitie
    assert workflow_def.name == "quality_assured_development"
    assert len(workflow_def.tasks) == 5
    
    # Test QualityGuardian tasks
    quality_tasks = [task for task in workflow_def.tasks if task.agent == "QualityGuardian"]
    assert len(quality_tasks) == 3
    
    # Test dependencies
    quality_gate_task = next(task for task in workflow_def.tasks if task.id == "quality_gate_1")
    assert len(quality_gate_task.dependencies) == 3
    assert "test_1" in quality_gate_task.dependencies
    assert "quality_1" in quality_gate_task.dependencies
    assert "security_1" in quality_gate_task.dependencies
    
    # Registreer workflow
    orchestrator.register_workflow(workflow_def)
    assert "quality_assured_development" in orchestrator.workflow_definitions

if __name__ == "__main__":
    # Run tests
    print("🧪 Testing Advanced Workflow...")
    
    try:
        # Basic tests
        test_workflow_definition()
        print("✅ Workflow definition test passed")
        
        test_workflow_registration()
        print("✅ Workflow registration test passed")
        
        test_task_dependency_grouping()
        print("✅ Task dependency grouping test passed")
        
        test_dependency_checking()
        print("✅ Dependency checking test passed")
        
        test_workflow_status_tracking()
        print("✅ Workflow status tracking test passed")
        
        test_workflow_cancellation()
        print("✅ Workflow cancellation test passed")
        
        test_parallel_task_execution()
        print("✅ Parallel task execution test passed")
        
        test_task_executor_registration()
        print("✅ Task executor registration test passed")
        
        test_qualityguardian_workflow_integration()
        print("✅ QualityGuardian workflow integration test passed")
        
        # Async test
        asyncio.run(test_workflow_execution())
        print("✅ Workflow execution test passed")
        
        print("\n🎉 Alle advanced workflow tests geslaagd!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 