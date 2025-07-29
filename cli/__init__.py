"""
BMAD CLI Tools Package

This package contains all CLI tools for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import core CLI functionality
from .core import BaseCLI, CLIUtils

# Import CLI interfaces
from .interfaces.figma_cli import FigmaCLI

# Import other CLI tools (keeping existing structure for now)
from .bmad_cli_clickup import ClickUpCLI
from .langgraph_cli import LangGraphCLI
from .performance_monitor_cli import PerformanceMonitorCLI
from .project_cli import ProjectCLI
from .projects_cli import ProjectsCLI
# from .repository_integration_cli import RepositoryIntegrationCLI  # Temporarily disabled due to Prefect compatibility
from .test_sprites_cli import TestSpritesCLI
from .webhook_cli import WebhookCLI

__all__ = [
    "BaseCLI",
    "CLIUtils",
    "FigmaCLI",
    "ClickUpCLI",
    "LangGraphCLI",
    "PerformanceMonitorCLI",
    "ProjectCLI",
    "ProjectsCLI",
    # "RepositoryIntegrationCLI",  # Temporarily disabled due to Prefect compatibility
    "TestSpritesCLI",
    "WebhookCLI"
]
