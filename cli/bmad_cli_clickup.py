#!/usr/bin/env python3
"""
BMAD CLI - ClickUp Workflow Commands
===================================

CLI commando's voor BMAD ClickUp workflow management.

Gebruik:
    python bmad_cli_clickup.py adapt-template [project_id]
    python bmad_cli_clickup.py generate-planning [project_id]
    python bmad_cli_clickup.py create-sprints [project_id]
    python bmad_cli_clickup.py full-workflow [project_id]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# BMAD imports
sys.path.append(str(Path(__file__).parent.parent))
from bmad_clickup_workflow import BMADClickUpWorkflow


def adapt_template_command(project_id: str = "bmad-frontend"):
    """CLI commando voor template aanpassing."""
    print(f"🔧 Template aanpassen voor project: {project_id}")

    workflow = BMADClickUpWorkflow(project_id)
    template = workflow.adapt_clickup_template_to_bmad()

    if template:
        # Save template to file
        template_file = f"bmad_template_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"✅ Template opgeslagen: {template_file}")
        return True
    print("❌ Template aanpassing gefaald")
    return False


def generate_planning_command(project_id: str = "bmad-frontend"):
    """CLI commando voor planning generatie."""
    print(f"📋 Planning genereren voor project: {project_id}")

    workflow = BMADClickUpWorkflow(project_id)
    planning = workflow.generate_frontend_planning()

    if planning:
        # Save planning to file
        planning_file = f"bmad_planning_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(planning_file, "w", encoding="utf-8") as f:
            json.dump(planning, f, indent=2, ensure_ascii=False)

        print(f"✅ Planning opgeslagen: {planning_file}")
        return True
    print("❌ Planning generatie gefaald")
    return False


def create_sprints_command(project_id: str = "bmad-frontend"):
    """CLI commando voor sprint creatie in ClickUp."""
    print(f"🏃‍♂️ Sprints aanmaken in ClickUp voor project: {project_id}")

    workflow = BMADClickUpWorkflow(project_id)

    # Generate planning first
    planning = workflow.generate_frontend_planning()
    if not planning:
        print("❌ Kon planning niet genereren")
        return False

    # Create ClickUp structure
    template = workflow.adapt_clickup_template_to_bmad()
    structure_created = workflow.create_clickup_structure(template)

    if not structure_created:
        print("❌ Kon ClickUp structuur niet aanmaken")
        return False

    # Create sprint tasks
    tasks_created = workflow.create_sprint_tasks(planning)

    if tasks_created:
        print("✅ Sprints succesvol aangemaakt in ClickUp")
        return True
    print("❌ Sprint creatie gefaald")
    return False


def full_workflow_command(project_id: str = "bmad-frontend"):
    """CLI commando voor complete workflow."""
    print(f"🚀 Complete workflow uitvoeren voor project: {project_id}")

    workflow = BMADClickUpWorkflow(project_id)
    success = workflow.run_complete_workflow()

    if success:
        print("✅ Complete workflow succesvol voltooid!")
    else:
        print("❌ Workflow gefaald")

    return success


def list_projects_command():
    """CLI commando voor project overzicht."""
    print("📋 Beschikbare BMAD projecten:")

    try:
        from bmad.agents.core.project_manager import ProjectManager
        pm = ProjectManager()
        projects = pm.list_projects()

        for project in projects:
            print(f"  - {project['id']}: {project.get('name', 'Geen naam')}")
            if "clickup" in project:
                clickup_config = project["clickup"]
                print(f"    ClickUp Space: {clickup_config.get('space_id', 'Niet geconfigureerd')}")

        return True
    except Exception as e:
        print(f"❌ Kon projecten niet ophalen: {e}")
        return False


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BMAD ClickUp Workflow CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Voorbeelden:
  python bmad_cli_clickup.py adapt-template bmad-frontend
  python bmad_cli_clickup.py generate-planning bmad-frontend
  python bmad_cli_clickup.py create-sprints bmad-frontend
  python bmad_cli_clickup.py full-workflow bmad-frontend
  python bmad_cli_clickup.py list-projects
        """
    )

    parser.add_argument(
        "command",
        choices=["adapt-template", "generate-planning", "create-sprints", "full-workflow", "list-projects"],
        help="Het commando om uit te voeren"
    )

    parser.add_argument(
        "project_id",
        nargs="?",
        default="bmad-frontend",
        help="Project ID (default: bmad-frontend)"
    )

    args = parser.parse_args()

    # Check environment
    if not os.getenv("CLICKUP_API_KEY"):
        print("❌ CLICKUP_API_KEY niet gevonden in environment")
        print("Zorg dat je .env file geladen is: source .env")
        return False

    # Execute command
    if args.command == "adapt-template":
        return adapt_template_command(args.project_id)
    if args.command == "generate-planning":
        return generate_planning_command(args.project_id)
    if args.command == "create-sprints":
        return create_sprints_command(args.project_id)
    if args.command == "full-workflow":
        return full_workflow_command(args.project_id)
    if args.command == "list-projects":
        return list_projects_command()
    print(f"❌ Onbekend commando: {args.command}")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
