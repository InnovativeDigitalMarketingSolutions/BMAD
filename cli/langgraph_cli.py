#!/usr/bin/env python3
"""
BMAD LangGraph Workflow CLI

Command-line interface voor het testen en demonstreren van LangGraph workflows.
"""

import argparse
import asyncio
import json
import sys
import time

# Add the project root to Python path
sys.path.insert(0, '.')

from bmad.agents.core.langgraph_workflow import (
    WorkflowDefinition,
    WorkflowTask,
    create_workflow_orchestrator
)


def create_demo_workflow() -> WorkflowDefinition:
    """Create a demo workflow for testing."""
    tasks = [
        WorkflowTask(
            id="product_owner_task",
            name="Create User Story",
            agent="ProductOwner",
            command="create_user_story"
        ),
        WorkflowTask(
            id="architect_task",
            name="Design System Architecture",
            agent="Architect",
            command="design_system",
            dependencies=["product_owner_task"]
        ),
        WorkflowTask(
            id="developer_task",
            name="Implement Feature",
            agent="FullstackDeveloper",
            command="implement_feature",
            dependencies=["architect_task"]
        ),
        WorkflowTask(
            id="test_task",
            name="Run Tests",
            agent="TestEngineer",
            command="run_tests",
            dependencies=["developer_task"]
        )
    ]
    
    return WorkflowDefinition(
        name="demo_workflow",
        description="Complete development workflow from user story to testing",
        tasks=tasks,
        max_parallel=2,
        timeout=1800,  # 30 minutes
        auto_retry=True,
        notify_on_completion=True,
        notify_on_failure=True
    )


def create_simple_workflow() -> WorkflowDefinition:
    """Create a simple workflow for basic testing."""
    tasks = [
        WorkflowTask(
            id="simple_task",
            name="Simple Task",
            agent="ProductOwner",
            command="simple_command"
        )
    ]
    
    return WorkflowDefinition(
        name="simple_workflow",
        description="Simple workflow for basic testing",
        tasks=tasks,
        max_parallel=1,
        timeout=300,  # 5 minutes
        auto_retry=False,
        notify_on_completion=False,
        notify_on_failure=False
    )


async def run_workflow_demo(workflow_name: str = "demo_workflow"):
    """Run a workflow demonstration."""
    print(f"🚀 Starting LangGraph Workflow Demo: {workflow_name}")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = create_workflow_orchestrator()
    
    # Create and register workflow
    if workflow_name == "demo_workflow":
        workflow_def = create_demo_workflow()
    elif workflow_name == "simple_workflow":
        workflow_def = create_simple_workflow()
    else:
        print(f"❌ Unknown workflow: {workflow_name}")
        return
    
    orchestrator.register_workflow(workflow_def)
    
    print(f"📋 Workflow registered: {workflow_def.name}")
    print(f"   Description: {workflow_def.description}")
    print(f"   Tasks: {len(workflow_def.tasks)}")
    print(f"   Max Parallel: {workflow_def.max_parallel}")
    print(f"   Timeout: {workflow_def.timeout}s")
    
    # Print task details
    print("\n📝 Task Details:")
    for task in workflow_def.tasks:
        print(f"   • {task.name} ({task.agent})")
        print(f"     Command: {task.command}")
        if task.dependencies:
            print(f"     Dependencies: {', '.join(task.dependencies)}")
        print()
    
    # Start workflow
    context = {
        "project": "BMAD Demo",
        "feature": "User Authentication",
        "priority": "high"
    }
    
    print(f"🎯 Starting workflow with context: {json.dumps(context, indent=2)}")
    
    workflow_id = orchestrator.start_workflow(workflow_name, context)
    print(f"✅ Workflow started with ID: {workflow_id}")
    
    # Monitor workflow
    print("\n📊 Monitoring workflow execution...")
    max_wait_time = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        status = orchestrator.get_workflow_status(workflow_id)
        if status:
            print(f"   Status: {status.get('status', 'unknown')}")
            print(f"   Active workflows: {status.get('active_workflows', 0)}")
        else:
            print("   Status: Not available")
        
        await asyncio.sleep(2)
    
    print("\n⏰ Demo completed (timeout reached)")
    print("=" * 60)


def show_workflow_status(workflow_id: str):
    """Show status of a specific workflow."""
    print(f"📊 Workflow Status: {workflow_id}")
    print("=" * 40)
    
    orchestrator = create_workflow_orchestrator()
    status = orchestrator.get_workflow_status(workflow_id)
    
    if status:
        print(f"Status: {status.get('status', 'unknown')}")
        print(f"Active workflows: {status.get('active_workflows', 0)}")
        print(f"Workflow ID: {status.get('workflow_id', 'unknown')}")
    else:
        print("❌ Workflow not found or status unavailable")


def list_workflows():
    """List all available workflows."""
    print("📋 Available Workflows")
    print("=" * 30)
    
    orchestrator = create_workflow_orchestrator()
    
    # Register demo workflows
    demo_workflow = create_demo_workflow()
    simple_workflow = create_simple_workflow()
    
    orchestrator.register_workflow(demo_workflow)
    orchestrator.register_workflow(simple_workflow)
    
    for name, workflow in orchestrator.workflow_definitions.items():
        print(f"• {name}")
        print(f"  Description: {workflow.description}")
        print(f"  Tasks: {len(workflow.tasks)}")
        print(f"  Max Parallel: {workflow.max_parallel}")
        print()


def test_langgraph_integration():
    """Test basic LangGraph integration."""
    print("🧪 Testing LangGraph Integration")
    print("=" * 40)
    
    try:
        # Test basic functionality
        orchestrator = create_workflow_orchestrator()
        print("✅ Orchestrator created successfully")
        
        # Test workflow creation
        workflow_def = create_simple_workflow()
        orchestrator.register_workflow(workflow_def)
        print("✅ Workflow registered successfully")
        
        # Test task execution
        task = WorkflowTask(
            id="test_task",
            name="Test Task",
            agent="ProductOwner",
            command="test_command"
        )
        
        context = {"test": "context"}
        result = asyncio.run(orchestrator._execute_product_owner_task(task, context))
        
        if result and "output" in result:
            print("✅ Task execution successful")
            print(f"   Output: {result['output']}")
        else:
            print("❌ Task execution failed")
        
        print("\n🎉 LangGraph integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ LangGraph integration test failed: {e}")
        return False
    
    return True


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD LangGraph Workflow CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python langgraph_cli.py demo                    # Run demo workflow
  python langgraph_cli.py simple                 # Run simple workflow
  python langgraph_cli.py status <workflow_id>   # Show workflow status
  python langgraph_cli.py list                   # List available workflows
  python langgraph_cli.py test                   # Test LangGraph integration
        """
    )
    
    parser.add_argument(
        "command",
        choices=["demo", "simple", "status", "list", "test"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "workflow_id",
        nargs="?",
        help="Workflow ID for status command"
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == "demo":
            asyncio.run(run_workflow_demo("demo_workflow"))
        elif args.command == "simple":
            asyncio.run(run_workflow_demo("simple_workflow"))
        elif args.command == "status":
            if not args.workflow_id:
                print("❌ Workflow ID required for status command")
                sys.exit(1)
            show_workflow_status(args.workflow_id)
        elif args.command == "list":
            list_workflows()
        elif args.command == "test":
            success = test_langgraph_integration()
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 