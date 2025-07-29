"""
BMAD CLI Core Module

Core functionality for CLI tools including base classes and utilities.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

from .base_cli import BaseCLI
from .utils import CLIUtils

__all__ = ["BaseCLI", "CLIUtils"] 