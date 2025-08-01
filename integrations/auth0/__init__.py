"""
Auth0 Integration Module

Provides enterprise-grade authentication and authorization capabilities.
"""

from .auth0_client import (
    Auth0Client,
    Auth0Config,
    Auth0User,
    Auth0Role,
    Auth0Permission
)

__all__ = [
    "Auth0Client",
    "Auth0Config", 
    "Auth0User",
    "Auth0Role",
    "Auth0Permission"
] 