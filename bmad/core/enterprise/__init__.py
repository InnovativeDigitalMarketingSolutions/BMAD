"""
Enterprise Features Module

This module provides enterprise-grade features for BMAD including:
- Multi-tenancy support
- User management and authentication
- Subscription and billing integration
- Advanced access control
- Enterprise security features
"""

from .multi_tenancy import TenantManager, TenantContext
from .user_management import UserManager, RoleManager, PermissionManager
from .billing import BillingManager, SubscriptionManager, UsageTracker
from .access_control import AccessControlManager, FeatureFlagManager
from .security import EnterpriseSecurityManager
from .agent_integration import (
    enterprise_agent,
    enterprise_method,
    enterprise_required,
    enterprise_context,
    get_enterprise_context,
    set_enterprise_context,
    check_enterprise_feature,
    check_enterprise_permission,
    track_enterprise_usage,
    log_enterprise_event
)

__all__ = [
    'TenantManager',
    'TenantContext',
    'UserManager',
    'RoleManager',
    'PermissionManager',
    'BillingManager',
    'SubscriptionManager',
    'UsageTracker',
    'AccessControlManager',
    'FeatureFlagManager',
    'EnterpriseSecurityManager',
    'enterprise_agent',
    'enterprise_method',
    'enterprise_required',
    'enterprise_context',
    'get_enterprise_context',
    'set_enterprise_context',
    'check_enterprise_feature',
    'check_enterprise_permission',
    'track_enterprise_usage',
    'log_enterprise_event'
] 