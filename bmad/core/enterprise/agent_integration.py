"""
Enterprise Features Agent Integration

This module provides decorators and utilities to automatically integrate
enterprise features into all BMAD agents.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional

from bmad.core.enterprise.multi_tenancy import tenant_manager
from bmad.core.enterprise.user_management import permission_manager
from bmad.core.enterprise.billing import usage_tracker
from bmad.core.enterprise.access_control import feature_flag_manager
from bmad.core.enterprise.security import enterprise_security_manager

logger = logging.getLogger(__name__)

class EnterpriseContext:
    """Context manager for enterprise features in agents."""
    
    def __init__(self, tenant_id: Optional[str] = None, user_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self._previous_tenant = None
        self._previous_user = None
    
    def __enter__(self):
        # Store previous context
        self._previous_tenant = getattr(tenant_manager, '_current_tenant_id', None)
        self._previous_user = getattr(tenant_manager, '_current_user_id', None)
        
        # Set new context
        if self.tenant_id:
            tenant_manager._current_tenant_id = self.tenant_id
        if self.user_id:
            tenant_manager._current_user_id = self.user_id
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous context
        if self._previous_tenant is not None:
            tenant_manager._current_tenant_id = self._previous_tenant
        if self._previous_user is not None:
            tenant_manager._current_user_id = self._previous_user

def enterprise_required(permission: Optional[str] = None, feature_flag: Optional[str] = None):
    """
    Decorator to require enterprise features for agent methods.
    
    Args:
        permission: Required permission to execute the method
        feature_flag: Required feature flag to be enabled
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get tenant and user from agent context
            tenant_id = getattr(self, 'tenant_id', None)
            user_id = getattr(self, 'user_id', None)
            
            if not tenant_id or not user_id:
                logger.warning(f"Enterprise context not set for {func.__name__}")
                return func(self, *args, **kwargs)
            
            # Check feature flag if specified
            if feature_flag:
                if not feature_flag_manager.get_flag_value(feature_flag, tenant_id):
                    raise ValueError(f"Feature flag '{feature_flag}' not enabled for tenant {tenant_id}")
            
            # Check permission if specified
            if permission:
                if not permission_manager.has_permission(user_id, permission):
                    raise ValueError(f"Permission '{permission}' required for user {user_id}")
            
            # Log method execution
            enterprise_security_manager.log_audit_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="agent_method",
                resource="agent",
                action=func.__name__,
                details={
                    "agent_name": getattr(self, 'agent_name', 'unknown'),
                    "method": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                },
                success=True
            )
            
            # Track usage
            usage_tracker.record_usage(
                tenant_id=tenant_id,
                metric="agent_method_calls",
                value=1
            )
            
            # Execute the method
            try:
                result = func(self, *args, **kwargs)
                
                # Log successful execution
                enterprise_security_manager.log_audit_event(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    event_type="agent_method",
                    resource="agent",
                    action=f"{func.__name__}_complete",
                    details={"success": True},
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Log failed execution
                enterprise_security_manager.log_audit_event(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    event_type="agent_method",
                    resource="agent",
                    action=f"{func.__name__}_error",
                    details={"error": str(e)},
                    success=False
                )
                raise
        
        return wrapper
    return decorator

def enterprise_agent(cls):
    """
    Class decorator to automatically integrate enterprise features into agent classes.
    """
    original_init = cls.__init__
    
    def __init__(self, *args, **kwargs):
        # Extract enterprise context from kwargs
        self.tenant_id = kwargs.pop('tenant_id', None)
        self.user_id = kwargs.pop('user_id', None)
        
        # Call original init
        original_init(self, *args, **kwargs)
        
        # Set enterprise context if provided
        if self.tenant_id and self.user_id:
            self._set_enterprise_context()
    
    def _set_enterprise_context(self):
        """Set enterprise context for the agent."""
        if not self.tenant_id or not self.user_id:
            return
        
        # Verify tenant exists
        tenant = tenant_manager.get_tenant(self.tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {self.tenant_id} not found")
        
        # Verify user exists and belongs to tenant
        # TODO: Add user verification logic
        
        # Log agent initialization
        enterprise_security_manager.log_audit_event(
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            event_type="agent_init",
            resource="agent",
            action="initialize",
            details={
                "agent_name": getattr(self, 'agent_name', cls.__name__),
                "tenant_id": self.tenant_id
            },
            success=True
        )
        
        logger.info(f"Enterprise context set for {cls.__name__}: tenant={self.tenant_id}, user={self.user_id}")
    
    def _check_enterprise_limits(self, operation: str) -> bool:
        """Check if the current tenant has sufficient limits for the operation."""
        if not self.tenant_id:
            return True
        
        tenant = tenant_manager.get_tenant(self.tenant_id)
        if not tenant:
            return False
        
        # Check operation-specific limits
        if operation == "agent_execution":
            return tenant_manager.check_limit("max_agent_executions", 1)  # TODO: Get actual count
        elif operation == "api_calls":
            return tenant_manager.check_limit("max_api_calls", 1)  # TODO: Get actual count
        
        return True
    
    def _track_enterprise_usage(self, metric: str, value: int = 1):
        """Track enterprise usage metrics."""
        if not self.tenant_id:
            return
        
        usage_tracker.record_usage(
            tenant_id=self.tenant_id,
            metric=metric,
            value=value
        )
    
    def _log_enterprise_event(self, event_type: str, resource: str, action: str, 
                            details: Dict[str, Any], success: bool = True):
        """Log enterprise security events."""
        if not self.tenant_id or not self.user_id:
            return
        
        enterprise_security_manager.log_audit_event(
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            event_type=event_type,
            resource=resource,
            action=action,
            details=details,
            success=success
        )
    
    # Replace the original __init__ method
    cls.__init__ = __init__
    
    # Add enterprise methods to the class
    cls._set_enterprise_context = _set_enterprise_context
    cls._check_enterprise_limits = _check_enterprise_limits
    cls._track_enterprise_usage = _track_enterprise_usage
    cls._log_enterprise_event = _log_enterprise_event
    
    return cls

def enterprise_method(permission: Optional[str] = None, feature_flag: Optional[str] = None, 
                     usage_metric: Optional[str] = None):
    """
    Method decorator for enterprise features integration.
    
    Args:
        permission: Required permission to execute the method
        feature_flag: Required feature flag to be enabled
        usage_metric: Metric to track for usage billing
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check enterprise context
            if not hasattr(self, 'tenant_id') or not hasattr(self, 'user_id'):
                logger.warning(f"Enterprise context not available for {func.__name__}")
                return func(self, *args, **kwargs)
            
            tenant_id = self.tenant_id
            user_id = self.user_id
            
            if not tenant_id or not user_id:
                logger.warning(f"Enterprise context not set for {func.__name__}")
                return func(self, *args, **kwargs)
            
            # Check feature flag
            if feature_flag:
                if not feature_flag_manager.get_flag_value(feature_flag, tenant_id):
                    raise ValueError(f"Feature flag '{feature_flag}' not enabled for tenant {tenant_id}")
            
            # Check permission
            if permission:
                if not permission_manager.has_permission(user_id, permission):
                    raise ValueError(f"Permission '{permission}' required for user {user_id}")
            
            # Check limits - only if enterprise methods are available
            if hasattr(self, '_check_enterprise_limits'):
                if not self._check_enterprise_limits("agent_execution"):
                    raise ValueError("Enterprise limits exceeded")
            
            # Log method start - only if enterprise methods are available
            if hasattr(self, '_log_enterprise_event'):
                self._log_enterprise_event(
                    "agent_method",
                    "agent",
                    f"{func.__name__}_start",
                    {
                        "agent_name": getattr(self, 'agent_name', self.__class__.__name__),
                        "method": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                )
            
            # Track usage - ALWAYS track if metric is specified
            if usage_metric:
                if hasattr(self, '_track_enterprise_usage'):
                    self._track_enterprise_usage(usage_metric)
                else:
                    # Fallback to global usage tracking
                    track_enterprise_usage(usage_metric, 1, tenant_id)
            
            try:
                # Execute the method
                result = func(self, *args, **kwargs)
                
                # Log successful completion - only if enterprise methods are available
                if hasattr(self, '_log_enterprise_event'):
                    self._log_enterprise_event(
                        "agent_method",
                        "agent",
                        f"{func.__name__}_complete",
                        {"success": True}
                    )
                
                return result
                
            except Exception as e:
                # Log failure - only if enterprise methods are available
                if hasattr(self, '_log_enterprise_event'):
                    self._log_enterprise_event(
                        "agent_method",
                        "agent",
                        f"{func.__name__}_error",
                        {"error": str(e)},
                        success=False
                    )
                raise
        
        return wrapper
    return decorator

def enterprise_context(tenant_id: str, user_id: str):
    """
    Context manager for enterprise features.
    
    Args:
        tenant_id: The tenant ID to use
        user_id: The user ID to use
    """
    return EnterpriseContext(tenant_id, user_id)

# Utility functions for agents
def get_enterprise_context():
    """Get current enterprise context."""
    import os
    if os.getenv("DEV_MODE") == "true":
        return {
            'tenant_id': 'dev_tenant',
            'user_id': 'dev_user'
        }
    
    return {
        'tenant_id': getattr(tenant_manager, '_current_tenant_id', None),
        'user_id': getattr(tenant_manager, '_current_user_id', None)
    }

def set_enterprise_context(tenant_id: str, user_id: str):
    """Set enterprise context globally."""
    tenant_manager._current_tenant_id = tenant_id
    tenant_manager._current_user_id = user_id

def check_enterprise_feature(feature_flag: str, tenant_id: Optional[str] = None) -> bool:
    """Check if a feature flag is enabled for a tenant."""
    # Development mode - all features enabled
    import os
    if os.getenv("DEV_MODE") == "true":
        return True
    
    if not tenant_id:
        tenant_id = getattr(tenant_manager, '_current_tenant_id', None)
    
    if not tenant_id:
        return False
    
    return feature_flag_manager.get_flag_value(feature_flag, tenant_id)

def check_enterprise_permission(permission: str, user_id: Optional[str] = None) -> bool:
    """Check if a user has a specific permission."""
    # Development mode - all permissions granted
    import os
    if os.getenv("DEV_MODE") == "true":
        return True
    
    if not user_id:
        user_id = getattr(tenant_manager, '_current_user_id', None)
    
    if not user_id:
        return False
    
    return permission_manager.has_permission(user_id, permission)

def track_enterprise_usage(metric: str, value: int = 1, tenant_id: Optional[str] = None):
    """Track enterprise usage metrics."""
    if not tenant_id:
        tenant_id = getattr(tenant_manager, '_current_tenant_id', None)
    
    if not tenant_id:
        return
    
    usage_tracker.record_usage(
        tenant_id=tenant_id,
        metric=metric,
        value=value
    )

def log_enterprise_event(event_type: str, resource: str, action: str, 
                        details: Dict[str, Any], success: bool = True,
                        tenant_id: Optional[str] = None, user_id: Optional[str] = None):
    """Log enterprise security events."""
    if not tenant_id:
        tenant_id = getattr(tenant_manager, '_current_tenant_id', None)
    if not user_id:
        user_id = getattr(tenant_manager, '_current_user_id', None)
    
    if not tenant_id or not user_id:
        return
    
    enterprise_security_manager.log_audit_event(
        user_id=user_id,
        tenant_id=tenant_id,
        event_type=event_type,
        resource=resource,
        action=action,
        details=details,
        success=success
    ) 