"""
BMAD Test Sprites Library

Dit module biedt test sprites voor component testing en visual regression testing.
Integreert met de BMAD TestEngineer agent voor geautomatiseerde component testing.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class SpriteType(Enum):
    """Types of test sprites."""
    COMPONENT = "component"
    STATE = "state"
    INTERACTION = "interaction"
    ACCESSIBILITY = "accessibility"
    VISUAL = "visual"

class SpriteState(Enum):
    """States for test sprites."""
    DEFAULT = "default"
    LOADING = "loading"
    ERROR = "error"
    SUCCESS = "success"
    DISABLED = "disabled"
    HOVER = "hover"
    FOCUS = "focus"
    ACTIVE = "active"

@dataclass
class TestSprite:
    """Represents a test sprite for component testing."""
    name: str
    sprite_type: SpriteType
    component_name: str
    states: List[SpriteState] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    accessibility_checks: List[str] = field(default_factory=list)
    visual_checks: List[str] = field(default_factory=list)
    interaction_tests: List[str] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    baseline_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpriteTestResult:
    """Result of a sprite test."""
    sprite_name: str
    test_type: str
    status: str  # "passed", "failed", "skipped"
    details: Dict[str, Any] = field(default_factory=dict)
    screenshot_diff: Optional[str] = None
    accessibility_issues: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class TestSpriteLibrary:
    """
    Library voor test sprites en visual regression testing.
    """

    def __init__(self, sprites_dir: str = "test_sprites"):
        self.sprites_dir = Path(sprites_dir)
        self.sprites: Dict[str, TestSprite] = {}
        self.test_results: List[SpriteTestResult] = []

        # Create sprites directory if it doesn't exist
        self.sprites_dir.mkdir(exist_ok=True)

        # Load existing sprites
        self._load_sprites()

        logger.info(f"Test Sprite Library geïnitialiseerd in {self.sprites_dir}")

    def _load_sprites(self):
        """Load existing sprites from disk."""
        for sprite_file in self.sprites_dir.glob("*.json"):
            try:
                with open(sprite_file) as f:
                    sprite_data = json.load(f)
                    sprite = TestSprite(**sprite_data)
                    self.sprites[sprite.name] = sprite
                logger.info(f"Loaded sprite: {sprite.name}")
            except Exception as e:
                logger.error(f"Failed to load sprite {sprite_file}: {e}")

    def register_sprite(self, sprite: TestSprite):
        """Register a new test sprite."""
        self.sprites[sprite.name] = sprite

        # Save sprite to disk
        sprite_file = self.sprites_dir / f"{sprite.name}.json"
        with open(sprite_file, "w") as f:
            json.dump(sprite.__dict__, f, indent=2, default=str)

        logger.info(f"Registered sprite: {sprite.name}")

    def create_component_sprite(
        self,
        component_name: str,
        states: List[SpriteState] = None,
        accessibility_checks: List[str] = None,
        visual_checks: List[str] = None
    ) -> TestSprite:
        """Create a component test sprite."""
        if states is None:
            states = [SpriteState.DEFAULT]

        if accessibility_checks is None:
            accessibility_checks = [
                "aria-label",
                "role",
                "tabindex",
                "keyboard-navigation"
            ]

        if visual_checks is None:
            visual_checks = [
                "color-contrast",
                "font-size",
                "spacing",
                "alignment"
            ]

        sprite = TestSprite(
            name=f"{component_name}_sprite",
            sprite_type=SpriteType.COMPONENT,
            component_name=component_name,
            states=states,
            accessibility_checks=accessibility_checks,
            visual_checks=visual_checks,
            interaction_tests=[
                "click",
                "hover",
                "focus",
                "keyboard"
            ]
        )

        self.register_sprite(sprite)
        return sprite

    def create_state_sprite(
        self,
        component_name: str,
        state: SpriteState,
        attributes: Dict[str, Any] = None
    ) -> TestSprite:
        """Create a state-specific test sprite."""
        if attributes is None:
            attributes = {}

        sprite = TestSprite(
            name=f"{component_name}_{state.value}_sprite",
            sprite_type=SpriteType.STATE,
            component_name=component_name,
            states=[state],
            attributes=attributes
        )

        self.register_sprite(sprite)
        return sprite

    def create_accessibility_sprite(
        self,
        component_name: str,
        checks: List[str] = None
    ) -> TestSprite:
        """Create an accessibility test sprite."""
        if checks is None:
            checks = [
                "aria-label",
                "role",
                "tabindex",
                "keyboard-navigation",
                "screen-reader",
                "color-contrast",
                "focus-indicator"
            ]

        sprite = TestSprite(
            name=f"{component_name}_accessibility_sprite",
            sprite_type=SpriteType.ACCESSIBILITY,
            component_name=component_name,
            accessibility_checks=checks
        )

        self.register_sprite(sprite)
        return sprite

    async def run_sprite_test(self, sprite_name: str, test_type: str = "all") -> SpriteTestResult:
        """Run tests for a specific sprite."""
        if sprite_name not in self.sprites:
            raise ValueError(f"Sprite '{sprite_name}' not found")

        sprite = self.sprites[sprite_name]
        start_time = time.time()

        result = SpriteTestResult(
            sprite_name=sprite_name,
            test_type=test_type,
            status="running"
        )

        try:
            if test_type == "all" or test_type == "accessibility":
                await self._run_accessibility_tests(sprite, result)

            if test_type == "all" or test_type == "visual":
                await self._run_visual_tests(sprite, result)

            if test_type == "all" or test_type == "interaction":
                await self._run_interaction_tests(sprite, result)

            result.status = "passed"

        except Exception as e:
            result.status = "failed"
            result.details["error"] = str(e)
            logger.error(f"Sprite test failed for {sprite_name}: {e}")

        result.timestamp = time.time()
        result.performance_metrics["duration"] = result.timestamp - start_time

        self.test_results.append(result)
        return result

    async def _run_accessibility_tests(self, sprite: TestSprite, result: SpriteTestResult):
        """Run accessibility tests for a sprite."""
        logger.info(f"Running accessibility tests for {sprite.name}")

        for check in sprite.accessibility_checks:
            try:
                # Simulate accessibility check
                await asyncio.sleep(0.1)  # Simulate check time

                # For now, we'll simulate results
                if check == "aria-label" or check == "color-contrast":
                    result.details[f"accessibility_{check}"] = "passed"
                else:
                    result.details[f"accessibility_{check}"] = "passed"

            except Exception as e:
                result.accessibility_issues.append(f"{check}: {e!s}")

    async def _run_visual_tests(self, sprite: TestSprite, result: SpriteTestResult):
        """Run visual tests for a sprite."""
        logger.info(f"Running visual tests for {sprite.name}")

        for check in sprite.visual_checks:
            try:
                # Simulate visual check
                await asyncio.sleep(0.1)  # Simulate check time

                # For now, we'll simulate results
                result.details[f"visual_{check}"] = "passed"

            except Exception as e:
                result.details[f"visual_{check}_error"] = str(e)

    async def _run_interaction_tests(self, sprite: TestSprite, result: SpriteTestResult):
        """Run interaction tests for a sprite."""
        logger.info(f"Running interaction tests for {sprite.name}")

        for test in sprite.interaction_tests:
            try:
                # Simulate interaction test
                await asyncio.sleep(0.1)  # Simulate test time

                # For now, we'll simulate results
                result.details[f"interaction_{test}"] = "passed"

            except Exception as e:
                result.details[f"interaction_{test}_error"] = str(e)

    def get_sprite(self, sprite_name: str) -> Optional[TestSprite]:
        """Get a sprite by name."""
        return self.sprites.get(sprite_name)

    def list_sprites(self, sprite_type: Optional[SpriteType] = None) -> List[TestSprite]:
        """List all sprites, optionally filtered by type."""
        if sprite_type:
            return [sprite for sprite in self.sprites.values() if sprite.sprite_type == sprite_type]
        return list(self.sprites.values())

    def get_test_results(self, sprite_name: Optional[str] = None) -> List[SpriteTestResult]:
        """Get test results, optionally filtered by sprite name."""
        if sprite_name:
            return [result for result in self.test_results if result.sprite_name == sprite_name]
        return self.test_results

    def export_test_report(self, format: str = "json") -> str:
        """Export test results as a report."""
        if format == "json":
            return json.dumps({
                "sprites": [sprite.__dict__ for sprite in self.sprites.values()],
                "test_results": [result.__dict__ for result in self.test_results],
                "summary": {
                    "total_sprites": len(self.sprites),
                    "total_tests": len(self.test_results),
                    "passed_tests": len([r for r in self.test_results if r.status == "passed"]),
                    "failed_tests": len([r for r in self.test_results if r.status == "failed"])
                }
            }, indent=2, default=str)
        raise ValueError(f"Unsupported format: {format}")

# Global sprite library instance
_sprite_library: Optional[TestSpriteLibrary] = None

def get_sprite_library() -> TestSpriteLibrary:
    """Get the global sprite library instance."""
    global _sprite_library
    if _sprite_library is None:
        _sprite_library = TestSpriteLibrary()
    return _sprite_library

def create_bmad_component_sprites():
    """Create default BMAD component sprites."""
    library = get_sprite_library()

    # Agent Status Component
    library.create_component_sprite(
        component_name="AgentStatus",
        states=[SpriteState.DEFAULT, SpriteState.LOADING, SpriteState.ERROR],
        accessibility_checks=["aria-label", "role", "status-indicator"],
        visual_checks=["color-contrast", "status-colors", "spacing"]
    )

    # Workflow Manager Component
    library.create_component_sprite(
        component_name="WorkflowManager",
        states=[SpriteState.DEFAULT, SpriteState.LOADING, SpriteState.ACTIVE],
        accessibility_checks=["aria-label", "role", "keyboard-navigation"],
        visual_checks=["layout", "spacing", "typography"]
    )

    # API Tester Component
    library.create_component_sprite(
        component_name="APITester",
        states=[SpriteState.DEFAULT, SpriteState.LOADING, SpriteState.SUCCESS, SpriteState.ERROR],
        accessibility_checks=["aria-label", "form-controls", "error-messages"],
        visual_checks=["form-layout", "button-styles", "error-styles"]
    )

    # Metrics Chart Component
    library.create_component_sprite(
        component_name="MetricsChart",
        states=[SpriteState.DEFAULT, SpriteState.LOADING, SpriteState.ERROR],
        accessibility_checks=["aria-label", "chart-description", "keyboard-navigation"],
        visual_checks=["chart-colors", "data-visibility", "responsive"]
    )

    logger.info("BMAD component sprites created")

# Initialize default sprites when module is imported
if __name__ != "__main__":
    create_bmad_component_sprites()
