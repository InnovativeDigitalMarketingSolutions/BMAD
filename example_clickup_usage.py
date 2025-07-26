#!/usr/bin/env python3
"""
Voorbeeld gebruik van ClickUp integratie met BMAD agents
Dit script toont hoe je de ClickUp integratie kunt gebruiken met verschillende agents.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def example_product_owner_clickup():
    """Voorbeeld van hoe de ProductOwner agent ClickUp gebruikt."""
    print("📝 ProductOwner Agent - ClickUp Integration Example")
    print("=" * 60)
    
    try:
        sys.path.append('bmad')
        from agents.core.clickup_integration import clickup_integration
        
        # Voorbeeld: ProductOwner maakt een nieuw project aan
        project_name = "CoPilot AI Business Suite"
        project_type = "web_app"
        description = "Een geavanceerde AI-powered business suite met multi-agent systeem"
        
        print(f"Creating project: {project_name}")
        project_id = clickup_integration.create_project(
            project_name=project_name,
            project_type=project_type,
            description=description
        )
        
        if project_id:
            print(f"✅ Project created with ID: {project_id}")
            
            # Voorbeeld: User stories synchroniseren
            user_stories = [
                {
                    "title": "User Authentication",
                    "as_a": "end user",
                    "i_want": "secure login and registration",
                    "so_that": "I can access the platform safely",
                    "acceptance_criteria": "Login form, JWT tokens, password validation",
                    "priority": "high",
                    "story_points": "5"
                },
                {
                    "title": "Agent Dashboard",
                    "as_a": "developer",
                    "i_want": "monitor agent activities",
                    "so_that": "I can track progress and performance",
                    "acceptance_criteria": "Real-time metrics, agent status, activity logs",
                    "priority": "medium",
                    "story_points": "8"
                }
            ]
            
            print("\nSynchronizing user stories...")
            success = clickup_integration.sync_user_stories(project_name, user_stories)
            
            if success:
                print("✅ User stories synchronized successfully")
            else:
                print("❌ Failed to sync user stories")
                
        else:
            print("❌ Failed to create project")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_scrum_master_clickup():
    """Voorbeeld van hoe de ScrumMaster agent ClickUp gebruikt."""
    print("\n🎯 ScrumMaster Agent - ClickUp Integration Example")
    print("=" * 60)
    
    try:
        sys.path.append('bmad')
        from agents.core.clickup_integration import clickup_integration
        
        project_name = "CoPilot AI Business Suite"
        
        # Voorbeeld: Agent taken aanmaken
        agent_tasks = [
            {
                "agent": "FrontendDeveloper",
                "description": "Implement user authentication UI components",
                "hours": 8
            },
            {
                "agent": "BackendDeveloper", 
                "description": "Create authentication API endpoints",
                "hours": 12
            },
            {
                "agent": "SecurityDeveloper",
                "description": "Implement JWT security and validation",
                "hours": 6
            }
        ]
        
        print("Creating agent tasks...")
        for task in agent_tasks:
            task_id = clickup_integration.create_agent_task(
                project_name=project_name,
                agent_name=task["agent"],
                task_description=task["description"],
                estimated_hours=task["hours"]
            )
            
            if task_id:
                print(f"✅ Created task for {task['agent']}: {task_id}")
            else:
                print(f"❌ Failed to create task for {task['agent']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def example_task_management():
    """Voorbeeld van task management met ClickUp."""
    print("\n📋 Task Management - ClickUp Integration Example")
    print("=" * 60)
    
    try:
        sys.path.append('bmad')
        from agents.core.clickup_integration import clickup_integration
        
        project_name = "CoPilot AI Business Suite"
        
        # Haal project taken op
        print("Fetching project tasks...")
        tasks = clickup_integration.get_project_tasks(project_name)
        
        if tasks:
            print(f"Found {len(tasks)} tasks:")
            for task in tasks[:3]:  # Toon eerste 3 taken
                print(f"  - {task['name']} ({task['status']})")
                
            # Voorbeeld: Update task status
            if tasks:
                first_task = tasks[0]
                print(f"\nUpdating task status: {first_task['name']}")
                
                success = clickup_integration.update_task_status(
                    task_id=first_task['id'],
                    status="in progress"
                )
                
                if success:
                    print("✅ Task status updated successfully")
                else:
                    print("❌ Failed to update task status")
        else:
            print("No tasks found for project")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_project_metrics():
    """Voorbeeld van project metrics ophalen."""
    print("\n📊 Project Metrics - ClickUp Integration Example")
    print("=" * 60)
    
    try:
        sys.path.append('bmad')
        from agents.core.clickup_integration import clickup_integration
        
        project_name = "CoPilot AI Business Suite"
        
        # Haal project metrics op
        print("Fetching project metrics...")
        metrics = clickup_integration.get_project_metrics(project_name)
        
        if metrics:
            print("Project Metrics:")
            print(f"  Total Tasks: {metrics.get('total_tasks', 0)}")
            print(f"  Completed: {metrics.get('completed_tasks', 0)}")
            print(f"  In Progress: {metrics.get('in_progress_tasks', 0)}")
            print(f"  Pending: {metrics.get('pending_tasks', 0)}")
            print(f"  Completion Rate: {metrics.get('completion_rate', 0)}%")
        else:
            print("No metrics available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main example function."""
    print("🚀 ClickUp Integration Examples")
    print("=" * 60)
    
    # Check if ClickUp is enabled
    if not os.getenv("CLICKUP_API_KEY"):
        print("❌ CLICKUP_API_KEY not set. Please update your .env file first.")
        print("\nRequired environment variables:")
        print("  CLICKUP_API_KEY=your_api_key")
        print("  CLICKUP_SPACE_ID=your_space_id")
        print("  CLICKUP_FOLDER_ID=your_folder_id")
        print("  CLICKUP_LIST_ID=your_list_id")
        return
    
    # Run examples
    example_product_owner_clickup()
    example_scrum_master_clickup()
    example_task_management()
    example_project_metrics()
    
    print("\n🎉 Examples completed!")
    print("\nNext steps:")
    print("1. Run the test script: python test_clickup_integration.py")
    print("2. Test with real agents: python bmad/agents/Agent/ProductOwner/productowner.py")
    print("3. Monitor webhook events in your n8n workflow")

if __name__ == "__main__":
    main() 