"""
BMAD CLI Tools Package

This package contains all CLI tools for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import all CLI tools for easy access
from .advanced_policy_cli import AdvancedPolicyCLI
from .bmad_cli_clickup import ClickUpCLI
from .figma_cli import FigmaCLI
from .integrated_workflow_cli import IntegratedWorkflowCLI
from .langgraph_cli import LangGraphCLI
from .performance_monitor_cli import PerformanceMonitorCLI
from .project_cli import ProjectCLI
from .projects_cli import ProjectsCLI
from .repository_integration_cli import RepositoryIntegrationCLI
from .test_sprites_cli import TestSpritesCLI
from .webhook_cli import WebhookCLI

__all__ = [
    "AdvancedPolicyCLI",
    "ClickUpCLI",
    "FigmaCLI",
    "IntegratedWorkflowCLI",
    "LangGraphCLI",
    "PerformanceMonitorCLI",
    "ProjectCLI",
    "ProjectsCLI",
    "RepositoryIntegrationCLI",
    "TestSpritesCLI",
    "WebhookCLI"
]
