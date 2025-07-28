"""
BMAD Workflow Core Services

This module provides core workflow orchestration and management services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main workflow components
from .advanced_workflow import (
    AdvancedWorkflowOrchestrator,
    TaskStatus,
    WorkflowDefinition,
    WorkflowStatus,
    WorkflowTask,
)
from .integrated_workflow_orchestrator import (
    AgentWorkflowConfig,
    IntegratedWorkflowOrchestrator,
    IntegrationLevel,
)

__all__ = [
    "AdvancedWorkflowOrchestrator",
    "AgentWorkflowConfig",
    "IntegratedWorkflowOrchestrator",
    "IntegrationLevel",
    "TaskStatus",
    "WorkflowDefinition",
    "WorkflowStatus",
    "WorkflowTask"
]
