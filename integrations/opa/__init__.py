"""
BMAD OPA Integration Module

This module provides Open Policy Agent integration functionality for the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main integration components
from .opa_policy_engine import OPAPolicyEngine, PolicyResponse

__all__ = [
    "OPAPolicyEngine",
    "PolicyResponse"
] 