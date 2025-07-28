#!/usr/bin/env python3
"""
BMAD Test Sprites CLI

CLI tool voor het beheren van test sprites en visual regression testing.
Integreert met de BMAD TestEngineer agent voor geautomatiseerde component testing.
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent))

# Import BMAD modules
from bmad.agents.core.test_sprites import SpriteState, SpriteType, get_sprite_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TestSpritesCLI:
    """CLI for managing test sprites."""

    def __init__(self):
        self.library = get_sprite_library()

    async def list_sprites(self, sprite_type: Optional[str] = None):
        """List all available sprites."""
        print("🧪 BMAD Test Sprites")
        print("=" * 50)

        if sprite_type:
            try:
                sprite_type_enum = SpriteType(sprite_type.lower())
                sprites = self.library.list_sprites(sprite_type_enum)
            except ValueError:
                print(f"❌ Invalid sprite type: {sprite_type}")
                print(f"Valid types: {[t.value for t in SpriteType]}")
                return
        else:
            sprites = self.library.list_sprites()

        if not sprites:
            print("❌ Geen sprites gevonden")
            return

        for i, sprite in enumerate(sprites, 1):
            print(f"{i}. {sprite.name}")
            print(f"   📋 Type: {sprite.sprite_type.value}")
            print(f"   🧩 Component: {sprite.component_name}")
            print(f"   🔄 States: {[s.value for s in sprite.states]}")
            print(f"   ♿ Accessibility: {len(sprite.accessibility_checks)} checks")
            print(f"   🎨 Visual: {len(sprite.visual_checks)} checks")
            print(f"   🖱️  Interactions: {len(sprite.interaction_tests)} tests")
            print()

    async def create_component_sprite(
        self,
        component_name: str,
        states: Optional[str] = None,
        accessibility_checks: Optional[str] = None,
        visual_checks: Optional[str] = None
    ):
        """Create a new component sprite."""
        print(f"🎨 Creating component sprite for: {component_name}")
        print("=" * 50)

        # Parse states
        sprite_states = [SpriteState.DEFAULT]
        if states:
            try:
                state_list = [s.strip() for s in states.split(",")]
                sprite_states = [SpriteState(state.lower()) for state in state_list]
            except ValueError as e:
                print(f"❌ Invalid state: {e}")
                print(f"Valid states: {[s.value for s in SpriteState]}")
                return

        # Parse accessibility checks
        accessibility_list = None
        if accessibility_checks:
            accessibility_list = [c.strip() for c in accessibility_checks.split(",")]

        # Parse visual checks
        visual_list = None
        if visual_checks:
            visual_list = [c.strip() for c in visual_checks.split(",")]

        try:
            sprite = self.library.create_component_sprite(
                component_name=component_name,
                states=sprite_states,
                accessibility_checks=accessibility_list,
                visual_checks=visual_list
            )

            print(f"✅ Component sprite created: {sprite.name}")
            print(f"   📋 Type: {sprite.sprite_type.value}")
            print(f"   🔄 States: {[s.value for s in sprite.states]}")
            print(f"   ♿ Accessibility: {len(sprite.accessibility_checks)} checks")
            print(f"   🎨 Visual: {len(sprite.visual_checks)} checks")
            print(f"   🖱️  Interactions: {len(sprite.interaction_tests)} tests")

        except Exception as e:
            print(f"❌ Failed to create sprite: {e}")

    async def create_accessibility_sprite(self, component_name: str, checks: Optional[str] = None):
        """Create an accessibility sprite."""
        print(f"♿ Creating accessibility sprite for: {component_name}")
        print("=" * 50)

        # Parse checks
        checks_list = None
        if checks:
            checks_list = [c.strip() for c in checks.split(",")]

        try:
            sprite = self.library.create_accessibility_sprite(
                component_name=component_name,
                checks=checks_list
            )

            print(f"✅ Accessibility sprite created: {sprite.name}")
            print(f"   📋 Type: {sprite.sprite_type.value}")
            print(f"   ♿ Checks: {len(sprite.accessibility_checks)}")

        except Exception as e:
            print(f"❌ Failed to create accessibility sprite: {e}")

    async def run_sprite_test(self, sprite_name: str, test_type: str = "all"):
        """Run tests for a specific sprite."""
        print(f"🧪 Running tests for sprite: {sprite_name}")
        print(f"🔧 Test type: {test_type}")
        print("=" * 50)

        try:
            result = await self.library.run_sprite_test(sprite_name, test_type)

            print(f"📊 Test Results for {result.sprite_name}")
            print(f"   📈 Status: {result.status}")
            print(f"   ⏱️  Duration: {result.performance_metrics.get('duration', 0):.2f}s")

            if result.status == "passed":
                print("   ✅ All tests passed!")
            else:
                print(f"   ❌ Tests failed: {result.details.get('error', 'Unknown error')}")

            # Show detailed results
            if result.details:
                print("\n📋 Detailed Results:")
                for key, value in result.details.items():
                    print(f"   {key}: {value}")

            if result.accessibility_issues:
                print("\n♿ Accessibility Issues:")
                for issue in result.accessibility_issues:
                    print(f"   ⚠️  {issue}")

        except Exception as e:
            print(f"❌ Test execution failed: {e}")

    async def run_all_tests(self):
        """Run tests for all sprites."""
        print("🧪 Running tests for all sprites")
        print("=" * 50)

        sprites = self.library.list_sprites()

        if not sprites:
            print("❌ Geen sprites gevonden om te testen")
            return

        results = []
        for sprite in sprites:
            print(f"🔍 Testing {sprite.name}...")
            try:
                result = await self.library.run_sprite_test(sprite.name, "all")
                results.append(result)
                status_emoji = "✅" if result.status == "passed" else "❌"
                print(f"   {status_emoji} {sprite.name}: {result.status}")
            except Exception as e:
                print(f"   ❌ {sprite.name}: Failed - {e}")

        # Summary
        print("\n📊 Test Summary:")
        print(f"   Total sprites: {len(sprites)}")
        print(f"   Passed: {len([r for r in results if r.status == 'passed'])}")
        print(f"   Failed: {len([r for r in results if r.status == 'failed'])}")

    def show_sprite_details(self, sprite_name: str):
        """Show detailed information about a sprite."""
        sprite = self.library.get_sprite(sprite_name)

        if not sprite:
            print(f"❌ Sprite '{sprite_name}' not found")
            return

        print(f"🧪 Sprite Details: {sprite.name}")
        print("=" * 50)
        print(f"📋 Type: {sprite.sprite_type.value}")
        print(f"🧩 Component: {sprite.component_name}")
        print(f"🔄 States: {[s.value for s in sprite.states]}")

        if sprite.attributes:
            print(f"📝 Attributes: {sprite.attributes}")

        if sprite.accessibility_checks:
            print("\n♿ Accessibility Checks:")
            for check in sprite.accessibility_checks:
                print(f"   • {check}")

        if sprite.visual_checks:
            print("\n🎨 Visual Checks:")
            for check in sprite.visual_checks:
                print(f"   • {check}")

        if sprite.interaction_tests:
            print("\n🖱️  Interaction Tests:")
            for test in sprite.interaction_tests:
                print(f"   • {test}")

        if sprite.metadata:
            print(f"\n📊 Metadata: {sprite.metadata}")

    def export_report(self, format: str = "json", output_file: Optional[str] = None):
        """Export test results as a report."""
        print(f"📊 Exporting test report in {format} format")
        print("=" * 50)

        try:
            report = self.library.export_test_report(format)

            if output_file:
                with open(output_file, "w") as f:
                    f.write(report)
                print(f"✅ Report exported to: {output_file}")
            else:
                print(report)

        except Exception as e:
            print(f"❌ Failed to export report: {e}")

    def show_test_results(self, sprite_name: Optional[str] = None):
        """Show test results."""
        print("📊 Test Results")
        print("=" * 50)

        results = self.library.get_test_results(sprite_name)

        if not results:
            print("❌ Geen test resultaten gevonden")
            return

        for result in results:
            status_emoji = "✅" if result.status == "passed" else "❌"
            print(f"{status_emoji} {result.sprite_name}")
            print(f"   📋 Type: {result.test_type}")
            print(f"   📈 Status: {result.status}")
            print(f"   ⏱️  Duration: {result.performance_metrics.get('duration', 0):.2f}s")
            print(f"   🕐 Timestamp: {datetime.fromtimestamp(result.timestamp)}")
            print()

async def main():
    """Main CLI function."""
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
    list_parser.add_argument("--type", choices=[t.value for t in SpriteType],
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = TestSpritesCLI()

    try:
        if args.command == "list-sprites":
            await cli.list_sprites(args.type)

        elif args.command == "create-component":
            await cli.create_component_sprite(
                component_name=args.component_name,
                states=args.states,
                accessibility_checks=args.accessibility_checks,
                visual_checks=args.visual_checks
            )

        elif args.command == "create-accessibility":
            await cli.create_accessibility_sprite(
                component_name=args.component_name,
                checks=args.checks
            )

        elif args.command == "test-sprite":
            await cli.run_sprite_test(
                sprite_name=args.sprite_name,
                test_type=args.type
            )

        elif args.command == "run-all-tests":
            await cli.run_all_tests()

        elif args.command == "show-sprite":
            cli.show_sprite_details(args.sprite_name)

        elif args.command == "export-report":
            cli.export_report(format=args.format, output_file=args.output)

        elif args.command == "show-results":
            cli.show_test_results(sprite_name=args.sprite)

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CLI error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
