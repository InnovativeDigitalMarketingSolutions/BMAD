"""
Figma CLI Interface

Thin wrapper interface for Figma CLI commands.
"""

import sys
from typing import Optional

from cli.commands.figma.commands import FigmaCommands
from cli.commands.figma.handlers import FigmaHandlers


class FigmaCLI:
    """Figma CLI class for BMAD Figma integration."""
    
    def __init__(self):
        """Initialize Figma CLI."""
        self.commands = FigmaCommands()
        self.handlers = FigmaHandlers()
        
    def test_connection(self, file_id: str) -> bool:
        """Test Figma API connection."""
        return self.handlers.test_connection(file_id)
    
    def generate_components(self, file_id: str, output_dir: str = "components") -> bool:
        """Generate Next.js components from Figma file."""
        return self.handlers.generate_components(file_id, output_dir)
    
    def analyze_design(self, file_id: str) -> bool:
        """Analyze Figma design."""
        return self.handlers.analyze_design(file_id)
    
    def generate_documentation(self, file_id: str, output_file: Optional[str] = None) -> bool:
        """Generate documentation for Figma file."""
        return self.handlers.generate_documentation(file_id, output_file)
    
    def start_monitoring(self, file_id: str) -> bool:
        """Start monitoring Figma file for changes."""
        return self.handlers.start_monitoring(file_id)
    
    def show_help(self):
        """Show help information."""
        self.commands.print_help()


def main():
    """Main CLI function."""
    commands = FigmaCommands()
    success = commands.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 