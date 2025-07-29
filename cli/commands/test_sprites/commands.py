"""
Test Sprites CLI Commands

Command-line argument parsing and dispatch for Test Sprites CLI.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from .handlers import TestSpritesHandlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TestSpritesCommands:
    """Command-line interface for Test Sprites CLI."""
    
    def __init__(self):
        self.handlers = TestSpritesHandlers()
    
    def setup_parser(self):
        """Setup argument parser."""
        parser = argparse.ArgumentParser(
            description="BMAD Test Sprites CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # List all sprites
  python test_sprites_cli.py list-sprites
  
  # List component sprites only
  python test_sprites_cli.py list-sprites --type component
  
  # Create a component sprite
  python test_sprites_cli.py create-component MyComponent --states default,loading,error
  
  # Create an accessibility sprite
  python test_sprites_cli.py create-accessibility MyComponent --checks aria-label,role,tabindex
  
  # Run tests for a sprite
  python test_sprites_cli.py test-sprite MyComponent_sprite --type all
  
  # Run all tests
  python test_sprites_cli.py run-all-tests
  
  # Show sprite details
  python test_sprites_cli.py show-sprite MyComponent_sprite
  
  # Export test report
  python test_sprites_cli.py export-report --format json --output results.json
            """
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # List sprites command
        list_parser = subparsers.add_parser("list-sprites", help="List all available sprites")
        list_parser.add_argument("--type", choices=["component", "accessibility"],
                                help="Filter by sprite type")

        # Create component sprite command
        create_component_parser = subparsers.add_parser("create-component", help="Create a component sprite")
        create_component_parser.add_argument("component_name", help="Name of the component")
        create_component_parser.add_argument("--states", help="Comma-separated list of states")
        create_component_parser.add_argument("--accessibility-checks", help="Comma-separated list of accessibility checks")
        create_component_parser.add_argument("--visual-checks", help="Comma-separated list of visual checks")

        # Create accessibility sprite command
        create_accessibility_parser = subparsers.add_parser("create-accessibility", help="Create an accessibility sprite")
        create_accessibility_parser.add_argument("component_name", help="Name of the component")
        create_accessibility_parser.add_argument("--checks", help="Comma-separated list of accessibility checks")

        # Test sprite command
        test_parser = subparsers.add_parser("test-sprite", help="Run tests for a specific sprite")
        test_parser.add_argument("sprite_name", help="Name of the sprite to test")
        test_parser.add_argument("--type", choices=["all", "accessibility", "visual", "interaction"],
                                default="all", help="Type of tests to run")

        # Run all tests command
        subparsers.add_parser("run-all-tests", help="Run tests for all sprites")

        # Show sprite details command
        show_parser = subparsers.add_parser("show-sprite", help="Show detailed information about a sprite")
        show_parser.add_argument("sprite_name", help="Name of the sprite")

        # Export report command
        export_parser = subparsers.add_parser("export-report", help="Export test results as a report")
        export_parser.add_argument("--format", choices=["json"], default="json", help="Report format")
        export_parser.add_argument("--output", help="Output file path")

        # Show test results command
        results_parser = subparsers.add_parser("show-results", help="Show test results")
        results_parser.add_argument("--sprite", help="Filter by sprite name")

        return parser
    
    def execute_command(self, args):
        """Execute the parsed command."""
        if not args.command:
            self.setup_parser().print_help()
            return

        try:
            if args.command == "list-sprites":
                return asyncio.run(self.handlers.list_sprites(args.type))

            elif args.command == "create-component":
                return asyncio.run(self.handlers.create_component_sprite(
                    component_name=args.component_name,
                    states=args.states,
                    accessibility_checks=args.accessibility_checks,
                    visual_checks=args.visual_checks
                ))

            elif args.command == "create-accessibility":
                return asyncio.run(self.handlers.create_accessibility_sprite(
                    component_name=args.component_name,
                    checks=args.checks
                ))

            elif args.command == "test-sprite":
                return asyncio.run(self.handlers.run_sprite_test(
                    sprite_name=args.sprite_name,
                    test_type=args.type
                ))

            elif args.command == "run-all-tests":
                return asyncio.run(self.handlers.run_all_tests())

            elif args.command == "show-sprite":
                return self.handlers.show_sprite_details(args.sprite_name)

            elif args.command == "export-report":
                return self.handlers.export_report(format=args.format, output_file=args.output)

            elif args.command == "show-results":
                return self.handlers.show_test_results(sprite_name=args.sprite)

        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"CLI error: {e}", exc_info=True)
    
    def main(self):
        """Main CLI function."""
        parser = self.setup_parser()
        args = parser.parse_args()
        return self.execute_command(args)

# Legacy function for backward compatibility
async def main():
    """Main CLI function."""
    commands = TestSpritesCommands()
    return commands.main() 