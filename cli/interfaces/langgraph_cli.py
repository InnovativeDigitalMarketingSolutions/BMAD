"""
LangGraph CLI Interface

Thin wrapper interface for LangGraph CLI functionality.
"""

import asyncio
import sys
from cli.commands.langgraph.commands import LangGraphCommands
from cli.commands.langgraph.handlers import LangGraphHandlers

class LangGraphCLI:
    """LangGraph CLI class for BMAD workflow management."""
    
    def __init__(self):
        """Initialize LangGraph CLI."""
        self.handlers = LangGraphHandlers()
        self.commands = LangGraphCommands()
        
    def create_demo_workflow(self):
        """Create a demo workflow for testing."""
        return self.handlers.create_demo_workflow()
    
    def create_simple_workflow(self):
        """Create a simple workflow for basic testing."""
        return self.handlers.create_simple_workflow()
    
    async def run_workflow_demo(self, workflow_name: str = "demo_workflow"):
        """Run a workflow demonstration."""
        return await self.handlers.run_workflow_demo(workflow_name)
    
    def show_workflow_status(self, workflow_id: str):
        """Show workflow status."""
        return self.handlers.show_workflow_status(workflow_id)
    
    def list_workflows(self):
        """List all workflows."""
        return self.handlers.list_workflows()
    
    def test_integration(self):
        """Test LangGraph integration."""
        return self.handlers.test_langgraph_integration()
    
    def show_help(self):
        """Show help information."""
        return self.commands.show_help()

def main():
    """Main CLI function."""
    commands = LangGraphCommands()
    success = commands.main()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 