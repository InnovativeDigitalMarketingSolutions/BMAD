"""
Projects CLI Interface

Thin wrapper interface for projects CLI commands.
"""

import sys
from typing import Optional

from cli.commands.projects.commands import ProjectsCommands
from cli.commands.projects.handlers import ProjectsHandlers


class ProjectsCLI:
    """Projects CLI class for BMAD project management."""
    
    def __init__(self):
        """Initialize Projects CLI."""
        self.commands = ProjectsCommands()
        self.handlers = ProjectsHandlers()
        
    def list_projects(self):
        """List all projects."""
        return self.handlers.list_projects()
    
    def create_project(self, project_id: str, name: str, description: str = ""):
        """Create a new project."""
        return self.handlers.create_project(project_id, name, description)
    
    def add_requirement(self, project_id: str, requirement: str, category: str = "general"):
        """Add requirement to project."""
        return self.handlers.add_requirement(project_id, requirement, category)
    
    def add_user_story(self, project_id: str, story: str, priority: str = "medium"):
        """Add user story to project."""
        return self.handlers.add_user_story(project_id, story, priority)
    
    def show_project_info(self):
        """Show project information."""
        return self.handlers.show_project_info()
    
    def show_help(self):
        """Show help information."""
        self.commands.print_help()


def main():
    """Main CLI function."""
    commands = ProjectsCommands()
    success = commands.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 