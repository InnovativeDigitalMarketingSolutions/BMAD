"""
Project CLI Interface

Thin wrapper interface for project CLI commands.
"""

import sys
from typing import Optional

from cli.commands.project.commands import ProjectCommands
from cli.commands.project.handlers import ProjectHandlers


class ProjectCLI:
    """Project CLI class for BMAD project management."""
    
    def __init__(self):
        """Initialize Project CLI."""
        self.commands = ProjectCommands()
        self.handlers = ProjectHandlers()
        
    def list_projects(self):
        """List all projects."""
        return self.handlers.list_projects()
    
    def create_project(self, project_id: str, name: str, description: str = "", folder_id: str = None, list_id: str = None):
        """Create a new project."""
        return self.handlers.create_project(project_id, name, description, folder_id, list_id)
    
    def set_active_project(self, project_id: str):
        """Set active project."""
        return self.handlers.set_active_project(project_id)
    
    def show_project(self, project_id: str = None):
        """Show project details."""
        return self.handlers.show_project(project_id)
    
    def update_project(self, project_id: str, name: str = None, description: str = None, folder_id: str = None, list_id: str = None):
        """Update project configuration."""
        return self.handlers.update_project(project_id, name, description, folder_id, list_id)
    
    def delete_project(self, project_id: str):
        """Delete project."""
        return self.handlers.delete_project(project_id)
    
    def show_help(self):
        """Show help information."""
        self.commands.print_help()


def main():
    """Main CLI function."""
    commands = ProjectCommands()
    success = commands.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 