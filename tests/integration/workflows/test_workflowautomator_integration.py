#!/usr/bin/env python3
"""
Simple integration test for WorkflowAutomator agent
"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "bmad"))

def test_workflowautomator_basic_functionality():
    """Test basic WorkflowAutomator functionality."""
    print("🧪 Testing WorkflowAutomator basic functionality...")
    
    try:
        # Test if we can import the agent
        from bmad.agents.Agent.WorkflowAutomator.workflowautomator import WorkflowAutomatorAgent
        
        # Create agent instance
        agent = WorkflowAutomatorAgent()
        
        # Test basic methods
        help_text = agent.show_help()
        assert "WorkflowAutomator" in help_text
        assert "create-workflow" in help_text
        assert "execute-workflow" in help_text
        
        # Test resource completeness
        resource_result = agent.test_resource_completeness()
        assert resource_result["status"] == "complete"
        assert len(resource_result["missing_resources"]) == 0
        
        print("✅ WorkflowAutomator basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowAutomator basic functionality test failed: {e}")
        return False

def test_workflowautomator_workflow_creation():
    """Test WorkflowAutomator workflow creation."""
    print("🧪 Testing WorkflowAutomator workflow creation...")
    
    try:
        from bmad.agents.Agent.WorkflowAutomator.workflowautomator import WorkflowAutomatorAgent
        
        agent = WorkflowAutomatorAgent()
        
        # Test workflow creation
        workflow_result = agent.create_workflow(
            name="Test Workflow",
            description="Test workflow for integration testing",
            agents=["ProductOwner", "TestEngineer"],
            commands=["create-story", "run-tests"],
            priority="normal"
        )
        
        assert workflow_result["status"] == "created"
        assert "workflow_id" in workflow_result
        assert workflow_result["name"] == "Test Workflow"
        
        print("✅ WorkflowAutomator workflow creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowAutomator workflow creation test failed: {e}")
        return False

def test_workflowautomator_orchestrator_integration():
    """Test WorkflowAutomator integration with Orchestrator."""
    print("🧪 Testing WorkflowAutomator Orchestrator integration...")
    
    try:
        # Test if Orchestrator can handle WorkflowAutomator events
        from bmad.agents.Agent.Orchestrator.orchestrator import handle_workflow_execution_requested
        
        # Test event handling
        test_event = {
            "workflow_id": "test-workflow-123",
            "timestamp": "2025-01-27T15:00:00"
        }
        
        # This should not raise an exception
        handle_workflow_execution_requested(test_event)
        
        print("✅ WorkflowAutomator Orchestrator integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowAutomator Orchestrator integration test failed: {e}")
        return False

def test_workflowautomator_cli():
    """Test WorkflowAutomator CLI interface."""
    print("🧪 Testing WorkflowAutomator CLI...")
    
    try:
        import subprocess
        import tempfile
        
        # Test help command
        result = subprocess.run([
            sys.executable, "-m", "bmad.agents.Agent.WorkflowAutomator.workflowautomator", "help"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        assert result.returncode == 0
        assert "WorkflowAutomator" in result.stdout
        
        # Test test command
        result = subprocess.run([
            sys.executable, "-m", "bmad.agents.Agent.WorkflowAutomator.workflowautomator", "test"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        assert result.returncode == 0
        assert "complete" in result.stdout
        
        print("✅ WorkflowAutomator CLI test passed")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowAutomator CLI test failed: {e}")
        return False

def main():
    """Run all WorkflowAutomator integration tests."""
    print("🚀 Starting WorkflowAutomator Integration Tests...\n")
    
    tests = [
        test_workflowautomator_basic_functionality,
        test_workflowautomator_workflow_creation,
        test_workflowautomator_orchestrator_integration,
        test_workflowautomator_cli
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All WorkflowAutomator integration tests passed!")
        return 0
    else:
        print("❌ Some WorkflowAutomator integration tests failed!")
        return 1

if __name__ == "__main__":
    exit(main()) 