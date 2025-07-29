"""
Test Sprites CLI Handlers

Business logic for Test Sprites CLI commands.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add BMAD to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import BMAD modules
from bmad.agents.core.agent.test_sprites import SpriteState, SpriteType, get_sprite_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TestSpritesHandlers:
    """Handlers for Test Sprites CLI commands."""
    
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

# Legacy function exports for backward compatibility
async def list_sprites(sprite_type: Optional[str] = None):
    handlers = TestSpritesHandlers()
    return await handlers.list_sprites(sprite_type)

async def create_component_sprite(component_name: str, states: Optional[str] = None,
                                accessibility_checks: Optional[str] = None, visual_checks: Optional[str] = None):
    handlers = TestSpritesHandlers()
    return await handlers.create_component_sprite(component_name, states, accessibility_checks, visual_checks)

async def create_accessibility_sprite(component_name: str, checks: Optional[str] = None):
    handlers = TestSpritesHandlers()
    return await handlers.create_accessibility_sprite(component_name, checks)

async def run_sprite_test(sprite_name: str, test_type: str = "all"):
    handlers = TestSpritesHandlers()
    return await handlers.run_sprite_test(sprite_name, test_type)

async def run_all_tests():
    handlers = TestSpritesHandlers()
    return await handlers.run_all_tests()

def show_sprite_details(sprite_name: str):
    handlers = TestSpritesHandlers()
    return handlers.show_sprite_details(sprite_name)

def export_report(format: str = "json", output_file: Optional[str] = None):
    handlers = TestSpritesHandlers()
    return handlers.export_report(format, output_file)

def show_test_results(sprite_name: Optional[str] = None):
    handlers = TestSpritesHandlers()
    return handlers.show_test_results(sprite_name) 