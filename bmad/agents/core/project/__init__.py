"""
BMAD Project Core Services

This module provides core project management services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main project components
from .project_manager import project_manager, ProjectManager

__all__ = [
    "project_manager",
    "ProjectManager"
] 