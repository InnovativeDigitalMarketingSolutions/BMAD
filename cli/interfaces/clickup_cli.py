"""
ClickUp CLI Interface

Thin wrapper interface for ClickUp CLI functionality.
"""

import sys
from cli.commands.clickup.commands import ClickUpCommands
from cli.commands.clickup.handlers import ClickUpHandlers

class ClickUpCLI:
    """ClickUp CLI class for BMAD workflow management."""
    
    def __init__(self, project_id: str = "bmad-frontend"):
        """Initialize ClickUp CLI with project configuration."""
        self.project_id = project_id
        self.handlers = ClickUpHandlers(project_id)
        self.commands = ClickUpCommands()
        
    def adapt_template(self) -> bool:
        """Adapt ClickUp template to BMAD workflow."""
        return self.handlers.adapt_template()
    
    def generate_planning(self) -> bool:
        """Generate frontend planning."""
        return self.handlers.generate_planning()
    
    def create_sprints(self) -> bool:
        """Create sprints in ClickUp."""
        return self.handlers.create_sprints()
    
    def run_full_workflow(self) -> bool:
        """Run complete workflow."""
        return self.handlers.run_full_workflow()
    
    @staticmethod
    def list_projects() -> bool:
        """List available BMAD projects."""
        return ClickUpHandlers.list_projects()
    
    def show_help(self):
        """Show help information."""
        return self.handlers.show_help()

def main():
    """Main CLI function."""
    commands = ClickUpCommands()
    success = commands.main()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 