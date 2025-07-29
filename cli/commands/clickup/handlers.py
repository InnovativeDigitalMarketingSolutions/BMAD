"""
ClickUp CLI Handlers

Business logic for ClickUp CLI commands.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# BMAD imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from bmad_clickup_workflow import BMADClickUpWorkflow

class ClickUpHandlers:
    """Handlers for ClickUp CLI commands."""
    
    def __init__(self, project_id: str = "bmad-frontend"):
        """Initialize ClickUp handlers with project configuration."""
        self.project_id = project_id
        self.workflow = BMADClickUpWorkflow(project_id)
        
    def adapt_template(self) -> bool:
        """Adapt ClickUp template to BMAD workflow."""
        print(f"🔧 Template aanpassen voor project: {self.project_id}")

        template = self.workflow.adapt_clickup_template_to_bmad()

        if template:
            # Save template to file
            template_file = f"bmad_template_{self.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            print(f"✅ Template opgeslagen: {template_file}")
            return True
        print("❌ Template aanpassing gefaald")
        return False
    
    def generate_planning(self) -> bool:
        """Generate frontend planning."""
        print(f"📋 Planning genereren voor project: {self.project_id}")

        planning = self.workflow.generate_frontend_planning()

        if planning:
            # Save planning to file
            planning_file = f"bmad_planning_{self.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(planning_file, "w", encoding="utf-8") as f:
                json.dump(planning, f, indent=2, ensure_ascii=False)

            print(f"✅ Planning opgeslagen: {planning_file}")
            return True
        print("❌ Planning generatie gefaald")
        return False
    
    def create_sprints(self) -> bool:
        """Create sprints in ClickUp."""
        print(f"🏃‍♂️ Sprints aanmaken in ClickUp voor project: {self.project_id}")

        # Generate planning first
        planning = self.workflow.generate_frontend_planning()
        if not planning:
            print("❌ Kon planning niet genereren")
            return False

        # Create ClickUp structure
        template = self.workflow.adapt_clickup_template_to_bmad()
        structure_created = self.workflow.create_clickup_structure(template)

        if not structure_created:
            print("❌ Kon ClickUp structuur niet aanmaken")
            return False

        # Create sprint tasks
        tasks_created = self.workflow.create_sprint_tasks(planning)

        if tasks_created:
            print("✅ Sprints succesvol aangemaakt in ClickUp")
            return True
        print("❌ Sprint creatie gefaald")
        return False
    
    def run_full_workflow(self) -> bool:
        """Run complete workflow."""
        print(f"🚀 Complete workflow uitvoeren voor project: {self.project_id}")

        success = self.workflow.run_complete_workflow()

        if success:
            print("✅ Complete workflow succesvol voltooid!")
        else:
            print("❌ Workflow gefaald")

        return success
    
    @staticmethod
    def list_projects() -> bool:
        """List available BMAD projects."""
        print("📋 Beschikbare BMAD projecten:")

        try:
            from bmad.agents.core.project.project_manager import ProjectManager
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
    
    def show_help(self):
        """Show help information."""
        help_text = """
BMAD ClickUp CLI - Workflow Management
=====================================

Beschikbare commando's:
  adapt-template     - Pas ClickUp template aan aan BMAD workflow
  generate-planning  - Genereer frontend planning
  create-sprints     - Maak sprints aan in ClickUp
  full-workflow      - Voer complete workflow uit
  list-projects      - Toon beschikbare projecten

Voorbeelden:
  python bmad_cli_clickup.py adapt-template bmad-frontend
  python bmad_cli_clickup.py generate-planning bmad-frontend
  python bmad_cli_clickup.py create-sprints bmad-frontend
  python bmad_cli_clickup.py full-workflow bmad-frontend
  python bmad_cli_clickup.py list-projects
        """
        print(help_text)

# Legacy function exports for backward compatibility
def adapt_template_command(project_id: str = "bmad-frontend"):
    """CLI commando voor template aanpassing."""
    handlers = ClickUpHandlers(project_id)
    return handlers.adapt_template()

def generate_planning_command(project_id: str = "bmad-frontend"):
    """CLI commando voor planning generatie."""
    handlers = ClickUpHandlers(project_id)
    return handlers.generate_planning()

def create_sprints_command(project_id: str = "bmad-frontend"):
    """CLI commando voor sprint creatie in ClickUp."""
    handlers = ClickUpHandlers(project_id)
    return handlers.create_sprints()

def full_workflow_command(project_id: str = "bmad-frontend"):
    """CLI commando voor complete workflow."""
    handlers = ClickUpHandlers(project_id)
    return handlers.run_full_workflow()

def list_projects_command():
    """CLI commando voor project overzicht."""
    return ClickUpHandlers.list_projects() 