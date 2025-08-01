"""
Multi-Tenancy Support Module

Provides tenant isolation and management for enterprise BMAD deployments.
Supports tenant-specific configurations, data isolation, and resource management.
"""

import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, UTC
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)


@dataclass
class Tenant:
    """Represents a tenant in the multi-tenant system."""
    id: str
    name: str
    domain: str
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    limits: Dict[str, Any]
    features: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tenant':
        """Create tenant from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class TenantContext:
    """Thread-local tenant context for request isolation."""
    
    def __init__(self):
        self._context = threading.local()
    
    @property
    def current_tenant(self) -> Optional[Tenant]:
        """Get current tenant from context."""
        return getattr(self._context, 'tenant', None)
    
    @current_tenant.setter
    def current_tenant(self, tenant: Tenant):
        """Set current tenant in context."""
        self._context.tenant = tenant
    
    def clear(self):
        """Clear current tenant context."""
        if hasattr(self._context, 'tenant'):
            delattr(self._context, 'tenant')
    
    @contextmanager
    def tenant_context(self, tenant: Tenant):
        """Context manager for tenant operations."""
        previous_tenant = self.current_tenant
        try:
            self.current_tenant = tenant
            yield
        finally:
            self.current_tenant = previous_tenant


class TenantManager:
    """Manages tenant operations and isolation."""
    
    def __init__(self, storage_path: str = "data/tenants"):
        self.storage_path = storage_path
        self.tenants: Dict[str, Tenant] = {}
        self.context = TenantContext()
        self._load_tenants()
    
    def _load_tenants(self):
        """Load tenants from storage."""
        try:
            import os
            import json
            from pathlib import Path
            
            tenant_file = Path(self.storage_path) / "tenants.json"
            if tenant_file.exists():
                with open(tenant_file, 'r') as f:
                    data = json.load(f)
                    for tenant_data in data.values():
                        tenant = Tenant.from_dict(tenant_data)
                        self.tenants[tenant.id] = tenant
                logger.info(f"Loaded {len(self.tenants)} tenants from storage")
        except Exception as e:
            logger.warning(f"Could not load tenants: {e}")
    
    def _save_tenants(self):
        """Save tenants to storage."""
        try:
            import os
            from pathlib import Path
            
            tenant_file = Path(self.storage_path) / "tenants.json"
            tenant_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {tid: tenant.to_dict() for tid, tenant in self.tenants.items()}
            with open(tenant_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save tenants: {e}")
    
    def create_tenant(self, name: str, domain: str, plan: str = "basic") -> Tenant:
        """Create a new tenant."""
        tenant_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        # Default settings based on plan
        settings = self._get_default_settings(plan)
        limits = self._get_default_limits(plan)
        features = self._get_default_features(plan)
        
        tenant = Tenant(
            id=tenant_id,
            name=name,
            domain=domain,
            plan=plan,
            status="active",
            created_at=now,
            updated_at=now,
            settings=settings,
            limits=limits,
            features=features
        )
        
        self.tenants[tenant_id] = tenant
        self._save_tenants()
        logger.info(f"Created tenant: {name} ({tenant_id})")
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        for tenant in self.tenants.values():
            if tenant.domain == domain:
                return tenant
        return None
    
    def update_tenant(self, tenant_id: str, **kwargs) -> Optional[Tenant]:
        """Update tenant properties."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        
        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        # Update settings and limits if plan changed
        if 'plan' in kwargs:
            tenant.settings = self._get_default_settings(tenant.plan)
            tenant.limits = self._get_default_limits(tenant.plan)
            tenant.features = self._get_default_features(tenant.plan)
        
        tenant.updated_at = datetime.now(UTC)
        self._save_tenants()
        logger.info(f"Updated tenant: {tenant.name}")
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        del self.tenants[tenant_id]
        self._save_tenants()
        logger.info(f"Deleted tenant: {tenant.name}")
        return True
    
    def list_tenants(self) -> List[Tenant]:
        """List all tenants."""
        return list(self.tenants.values())
    
    def get_current_tenant(self) -> Optional[Tenant]:
        """Get current tenant from context."""
        return self.context.current_tenant
    
    def set_current_tenant(self, tenant: Tenant):
        """Set current tenant in context."""
        self.context.current_tenant = tenant
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled for current tenant."""
        tenant = self.get_current_tenant()
        if not tenant:
            return False
        return feature in tenant.features
    
    def check_limit(self, limit_name: str, current_usage: int) -> bool:
        """Check if tenant is within limits."""
        tenant = self.get_current_tenant()
        if not tenant:
            return False
        
        limit = tenant.limits.get(limit_name)
        if limit is None:
            return True
        
        return current_usage <= limit
    
    def _get_default_settings(self, plan: str) -> Dict[str, Any]:
        """Get default settings for plan."""
        defaults = {
            "basic": {
                "max_agents": 5,
                "max_workflows": 10,
                "storage_limit_gb": 1,
                "api_rate_limit": 1000
            },
            "professional": {
                "max_agents": 20,
                "max_workflows": 50,
                "storage_limit_gb": 10,
                "api_rate_limit": 5000
            },
            "enterprise": {
                "max_agents": 100,
                "max_workflows": 500,
                "storage_limit_gb": 100,
                "api_rate_limit": 50000
            }
        }
        return defaults.get(plan, defaults["basic"])
    
    def _get_default_limits(self, plan: str) -> Dict[str, Any]:
        """Get default limits for plan."""
        return self._get_default_settings(plan)
    
    def _get_default_features(self, plan: str) -> List[str]:
        """Get default features for plan."""
        defaults = {
            "basic": ["core_agents", "basic_workflows", "email_support"],
            "professional": ["core_agents", "advanced_workflows", "priority_support", "analytics"],
            "enterprise": ["all_agents", "custom_workflows", "dedicated_support", "advanced_analytics", "custom_integrations"]
        }
        return defaults.get(plan, defaults["basic"])

    def get_tenant_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive tenant summary including subscription and user data."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return {"success": False, "error": "Tenant not found"}
        
        # Get subscription data
        subscription_data = None
        try:
            from .billing import billing_manager
            subscription = billing_manager.get_subscription_by_tenant(tenant_id)
            if subscription:
                subscription_data = {
                    "id": subscription.id,
                    "plan_id": subscription.plan_id,
                    "status": subscription.status.value,
                    "billing_period": subscription.billing_period.value
                }
        except ImportError:
            subscription_data = None
        
        # Get user data
        user_data = None
        try:
            from .user_management import user_manager
            users = user_manager.list_users_by_tenant(tenant_id)
            user_data = {
                "total_users": len(users),
                "active_users": len([u for u in users if u.status.value == "active"]),
                "admin_users": len([u for u in users if "admin" in u.role_ids])
            }
        except ImportError:
            user_data = None
        
        summary = {
            "tenant_id": tenant_id,
            "name": tenant.name,
            "domain": tenant.domain,
            "plan": tenant.plan,
            "status": tenant.status,
            "created_at": tenant.created_at.isoformat(),
            "updated_at": tenant.updated_at.isoformat(),
            "features": tenant.features,
            "limits": tenant.limits,
            "subscription": subscription_data,
            "users": user_data
        }
        
        return {"success": True, "summary": summary}


# Global tenant manager instance
tenant_manager = TenantManager() 