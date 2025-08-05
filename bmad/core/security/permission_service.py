"""
Enhanced Permission Service for BMAD API.

This module provides advanced permission checking capabilities including:
- Tenant-aware permission checking
- Role-based access control (RBAC)
- Permission caching and optimization
- Advanced permission patterns
"""

import logging
import os
from typing import List, Set, Optional, Dict, Any
from functools import wraps
from flask import request, jsonify

from bmad.core.enterprise.user_management import permission_manager, user_manager
from bmad.core.enterprise.security import enterprise_security_manager

logger = logging.getLogger(__name__)


class PermissionService:
    """Enhanced permission service for advanced permission checking."""
    
    def __init__(self):
        """Initialize the permission service."""
        self.permission_cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    def check_permission(self, user_id: str, permission: str, tenant_id: Optional[str] = None) -> bool:
        """Check if user has specific permission, optionally in specific tenant."""
        if tenant_id:
            return permission_manager.check_tenant_permission(user_id, tenant_id, permission)
        else:
            return permission_manager.has_permission(user_id, permission)
    
    def check_any_permission(self, user_id: str, permissions: List[str], tenant_id: Optional[str] = None) -> bool:
        """Check if user has any of the specified permissions."""
        if tenant_id:
            user_permissions = permission_manager.get_user_permissions_by_tenant(user_id, tenant_id)
            return any(perm in user_permissions for perm in permissions)
        else:
            return permission_manager.has_any_permission(user_id, permissions)
    
    def check_all_permissions(self, user_id: str, permissions: List[str], tenant_id: Optional[str] = None) -> bool:
        """Check if user has all of the specified permissions."""
        if tenant_id:
            user_permissions = permission_manager.get_user_permissions_by_tenant(user_id, tenant_id)
            return all(perm in user_permissions for perm in permissions)
        else:
            return permission_manager.has_all_permissions(user_id, permissions)
    
    def check_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role."""
        return permission_manager.has_role(user_id, role_name)
    
    def check_any_role(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return permission_manager.has_any_role(user_id, role_names)
    
    def check_all_roles(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has all of the specified roles."""
        return permission_manager.has_all_roles(user_id, role_names)
    
    def get_user_permissions(self, user_id: str, tenant_id: Optional[str] = None) -> Set[str]:
        """Get all permissions for a user, optionally filtered by tenant."""
        if tenant_id:
            return permission_manager.get_user_permissions_by_tenant(user_id, tenant_id)
        else:
            return permission_manager.get_user_permissions(user_id)
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """Get all role names for a user."""
        roles = permission_manager.get_user_roles(user_id)
        return [role.name for role in roles]
    
    def log_permission_check(self, user_id: str, permission: str, tenant_id: Optional[str], 
                           success: bool, endpoint: str) -> None:
        """Log permission check for audit purposes."""
        try:
            enterprise_security_manager.log_audit_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="authorization",
                resource="api",
                action="permission_check",
                details={
                    "permission": permission,
                    "endpoint": endpoint,
                    "success": success
                },
                ip_address=request.remote_addr,
                success=success
            )
        except Exception as e:
            logger.error(f"Failed to log permission check: {e}")


# Global permission service instance
permission_service = PermissionService()


def require_permission_enhanced(permission: str, tenant_aware: bool = False):
    """Enhanced permission decorator with tenant awareness and better error handling."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Development mode bypass
            if os.getenv("DEV_MODE") == "true":
                return f(*args, **kwargs)
            
            try:
                # Get user from request (set by require_auth decorator)
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                user = request.user
                user_id = getattr(user, 'id', None)
                tenant_id = getattr(request, 'tenant_id', None)
                
                if not user_id:
                    return jsonify({"error": "Invalid user context"}), 401
                
                # Check permission
                has_permission = False
                if tenant_aware and tenant_id:
                    has_permission = permission_service.check_permission(user_id, permission, tenant_id)
                else:
                    has_permission = permission_service.check_permission(user_id, permission)
                
                # Log permission check
                permission_service.log_permission_check(
                    user_id=user_id,
                    permission=permission,
                    tenant_id=tenant_id,
                    success=has_permission,
                    endpoint=request.endpoint
                )
                
                if not has_permission:
                    return jsonify({
                        "error": "Insufficient permissions",
                        "required_permission": permission,
                        "user_permissions": list(permission_service.get_user_permissions(user_id, tenant_id))
                    }), 403
                
            except Exception as e:
                logger.error(f"Permission check failed: {e}")
                return jsonify({"error": "Permission check failed"}), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_permission(permissions: List[str], tenant_aware: bool = False):
    """Decorator to require any of the specified permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Development mode bypass
            if os.getenv("DEV_MODE") == "true":
                return f(*args, **kwargs)
            
            try:
                # Get user from request
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                user = request.user
                user_id = getattr(user, 'id', None)
                tenant_id = getattr(request, 'tenant_id', None)
                
                if not user_id:
                    return jsonify({"error": "Invalid user context"}), 401
                
                # Check permissions
                has_permission = False
                if tenant_aware and tenant_id:
                    has_permission = permission_service.check_any_permission(user_id, permissions, tenant_id)
                else:
                    has_permission = permission_service.check_any_permission(user_id, permissions)
                
                # Log permission check
                permission_service.log_permission_check(
                    user_id=user_id,
                    permission=f"any_of:{','.join(permissions)}",
                    tenant_id=tenant_id,
                    success=has_permission,
                    endpoint=request.endpoint
                )
                
                if not has_permission:
                    return jsonify({
                        "error": "Insufficient permissions",
                        "required_permissions": permissions,
                        "user_permissions": list(permission_service.get_user_permissions(user_id, tenant_id))
                    }), 403
                
            except Exception as e:
                logger.error(f"Permission check failed: {e}")
                return jsonify({"error": "Permission check failed"}), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_all_permissions(permissions: List[str], tenant_aware: bool = False):
    """Decorator to require all of the specified permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Development mode bypass
            if os.getenv("DEV_MODE") == "true":
                return f(*args, **kwargs)
            
            try:
                # Get user from request
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                user = request.user
                user_id = getattr(user, 'id', None)
                tenant_id = getattr(request, 'tenant_id', None)
                
                if not user_id:
                    return jsonify({"error": "Invalid user context"}), 401
                
                # Check permissions
                has_permission = False
                if tenant_aware and tenant_id:
                    has_permission = permission_service.check_all_permissions(user_id, permissions, tenant_id)
                else:
                    has_permission = permission_service.check_all_permissions(user_id, permissions)
                
                # Log permission check
                permission_service.log_permission_check(
                    user_id=user_id,
                    permission=f"all_of:{','.join(permissions)}",
                    tenant_id=tenant_id,
                    success=has_permission,
                    endpoint=request.endpoint
                )
                
                if not has_permission:
                    return jsonify({
                        "error": "Insufficient permissions",
                        "required_permissions": permissions,
                        "user_permissions": list(permission_service.get_user_permissions(user_id, tenant_id))
                    }), 403
                
            except Exception as e:
                logger.error(f"Permission check failed: {e}")
                return jsonify({"error": "Permission check failed"}), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role_name: str):
    """Decorator to require specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Development mode bypass
            if os.getenv("DEV_MODE") == "true":
                return f(*args, **kwargs)
            
            try:
                # Get user from request
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                user = request.user
                user_id = getattr(user, 'id', None)
                tenant_id = getattr(request, 'tenant_id', None)
                
                if not user_id:
                    return jsonify({"error": "Invalid user context"}), 401
                
                # Check role
                has_role = permission_service.check_role(user_id, role_name)
                
                # Log role check
                permission_service.log_permission_check(
                    user_id=user_id,
                    permission=f"role:{role_name}",
                    tenant_id=tenant_id,
                    success=has_role,
                    endpoint=request.endpoint
                )
                
                if not has_role:
                    return jsonify({
                        "error": "Insufficient role",
                        "required_role": role_name,
                        "user_roles": permission_service.get_user_roles(user_id)
                    }), 403
                
            except Exception as e:
                logger.error(f"Role check failed: {e}")
                return jsonify({"error": "Role check failed"}), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_role(role_names: List[str]):
    """Decorator to require any of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Development mode bypass
            if os.getenv("DEV_MODE") == "true":
                return f(*args, **kwargs)
            
            try:
                # Get user from request
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                user = request.user
                user_id = getattr(user, 'id', None)
                tenant_id = getattr(request, 'tenant_id', None)
                
                if not user_id:
                    return jsonify({"error": "Invalid user context"}), 401
                
                # Check roles
                has_role = permission_service.check_any_role(user_id, role_names)
                
                # Log role check
                permission_service.log_permission_check(
                    user_id=user_id,
                    permission=f"any_role:{','.join(role_names)}",
                    tenant_id=tenant_id,
                    success=has_role,
                    endpoint=request.endpoint
                )
                
                if not has_role:
                    return jsonify({
                        "error": "Insufficient role",
                        "required_roles": role_names,
                        "user_roles": permission_service.get_user_roles(user_id)
                    }), 403
                
            except Exception as e:
                logger.error(f"Role check failed: {e}")
                return jsonify({"error": "Role check failed"}), 500
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Import os for DEV_MODE check
import os 