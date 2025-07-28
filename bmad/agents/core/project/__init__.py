"""
BMAD Project Core Services

This module provides core project management services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main project components
from .project_manager import ProjectManager, project_manager

__all__ = [
    "ProjectManager",
    "project_manager"
]
