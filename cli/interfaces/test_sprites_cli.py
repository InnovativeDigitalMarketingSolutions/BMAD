"""
Test Sprites CLI Interface

Thin wrapper interface for Test Sprites CLI functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path
from cli.commands.test_sprites.commands import TestSpritesCommands
from cli.commands.test_sprites.handlers import TestSpritesHandlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TestSpritesCLI:
    """CLI for managing test sprites."""

    def __init__(self):
        self.handlers = TestSpritesHandlers()
        self.commands = TestSpritesCommands()

    async def list_sprites(self, sprite_type=None):
        """List all available sprites."""
        return await self.handlers.list_sprites(sprite_type)

    async def create_component_sprite(self, component_name: str, states=None,
                                    accessibility_checks=None, visual_checks=None):
        """Create a new component sprite."""
        return await self.handlers.create_component_sprite(component_name, states, accessibility_checks, visual_checks)

    async def create_accessibility_sprite(self, component_name: str, checks=None):
        """Create an accessibility sprite."""
        return await self.handlers.create_accessibility_sprite(component_name, checks)

    async def run_sprite_test(self, sprite_name: str, test_type: str = "all"):
        """Run tests for a specific sprite."""
        return await self.handlers.run_sprite_test(sprite_name, test_type)

    async def run_all_tests(self):
        """Run tests for all sprites."""
        return await self.handlers.run_all_tests()

    def show_sprite_details(self, sprite_name: str):
        """Show detailed information about a sprite."""
        return self.handlers.show_sprite_details(sprite_name)

    def export_report(self, format: str = "json", output_file=None):
        """Export test results as a report."""
        return self.handlers.export_report(format, output_file)

    def show_test_results(self, sprite_name=None):
        """Show test results."""
        return self.handlers.show_test_results(sprite_name)

def main():
    """Main CLI function."""
    commands = TestSpritesCommands()
    success = commands.main()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 