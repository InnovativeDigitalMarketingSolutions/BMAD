"""
Access Control Module

Provides feature flags, access control, and permission management
for enterprise BMAD deployments.
"""

import uuid
import json
import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, UTC
from enum import Enum

logger = logging.getLogger(__name__)


class FeatureFlagType(Enum):
    """Feature flag type enumeration."""
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    JSON = "json"


@dataclass
class FeatureFlag:
    """Represents a feature flag."""
    id: str
    name: str
    description: str
    flag_type: FeatureFlagType
    default_value: Any
    tenant_overrides: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feature flag to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['flag_type'] = self.flag_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureFlag':
        """Create feature flag from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['flag_type'] = FeatureFlagType(data['flag_type'])
        return cls(**data)


@dataclass
class AccessRule:
    """Represents an access control rule."""
    id: str
    name: str
    description: str
    resource: str
    action: str
    conditions: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert access rule to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccessRule':
        """Create access rule from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class FeatureFlagManager:
    """Manages feature flags."""
    
    def __init__(self, storage_path: str = "data/feature_flags"):
        self.storage_path = storage_path
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self._load_feature_flags()
        self._create_default_flags()
    
    def _load_feature_flags(self):
        """Load feature flags from storage."""
        try:
            import os
            from pathlib import Path
            
            flags_file = Path(self.storage_path) / "feature_flags.json"
            if flags_file.exists():
                with open(flags_file, 'r') as f:
                    data = json.load(f)
                    for flag_data in data.values():
                        flag = FeatureFlag.from_dict(flag_data)
                        self.feature_flags[flag.id] = flag
                logger.info(f"Loaded {len(self.feature_flags)} feature flags")
        except Exception as e:
            logger.warning(f"Could not load feature flags: {e}")
    
    def _save_feature_flags(self):
        """Save feature flags to storage."""
        try:
            import os
            from pathlib import Path
            
            flags_file = Path(self.storage_path) / "feature_flags.json"
            flags_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {fid: flag.to_dict() for fid, flag in self.feature_flags.items()}
            with open(flags_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save feature flags: {e}")
    
    def _create_default_flags(self):
        """Create default feature flags if they don't exist."""
        if not self.feature_flags:
            now = datetime.now(UTC)
            
            # Advanced analytics flag
            analytics_flag = FeatureFlag(
                id=str(uuid.uuid4()),
                name="advanced_analytics",
                description="Enable advanced analytics features",
                flag_type=FeatureFlagType.BOOLEAN,
                default_value=False,
                tenant_overrides={},
                created_at=now,
                updated_at=now
            )
            
            # Custom integrations flag
            integrations_flag = FeatureFlag(
                id=str(uuid.uuid4()),
                name="custom_integrations",
                description="Enable custom integrations",
                flag_type=FeatureFlagType.BOOLEAN,
                default_value=False,
                tenant_overrides={},
                created_at=now,
                updated_at=now
            )
            
            # AI model selection flag
            ai_model_flag = FeatureFlag(
                id=str(uuid.uuid4()),
                name="ai_model_selection",
                description="Allow users to select AI models",
                flag_type=FeatureFlagType.STRING,
                default_value="gpt-4",
                tenant_overrides={},
                created_at=now,
                updated_at=now
            )
            
            self.feature_flags[analytics_flag.id] = analytics_flag
            self.feature_flags[integrations_flag.id] = integrations_flag
            self.feature_flags[ai_model_flag.id] = ai_model_flag
            self._save_feature_flags()
    
    def create_feature_flag(self, name: str, description: str, flag_type: FeatureFlagType,
                          default_value: Any) -> FeatureFlag:
        """Create a new feature flag."""
        flag_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        flag = FeatureFlag(
            id=flag_id,
            name=name,
            description=description,
            flag_type=flag_type,
            default_value=default_value,
            tenant_overrides={},
            created_at=now,
            updated_at=now
        )
        
        self.feature_flags[flag_id] = flag
        self._save_feature_flags()
        logger.info(f"Created feature flag: {name} ({flag_id})")
        return flag
    
    def get_feature_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Get feature flag by ID."""
        return self.feature_flags.get(flag_id)
    
    def get_feature_flag_by_name(self, name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name."""
        for flag in self.feature_flags.values():
            if flag.name == name:
                return flag
        return None
    
    def get_flag_value(self, flag_name: str, tenant_id: str = None) -> Any:
        """Get feature flag value for a tenant."""
        flag = self.get_feature_flag_by_name(flag_name)
        if not flag or not flag.is_active:
            return flag.default_value if flag else None
        
        # Check for tenant override
        if tenant_id and tenant_id in flag.tenant_overrides:
            return flag.tenant_overrides[tenant_id]
        
        return flag.default_value
    
    def set_tenant_override(self, flag_name: str, tenant_id: str, value: Any) -> bool:
        """Set tenant-specific override for a feature flag."""
        flag = self.get_feature_flag_by_name(flag_name)
        if not flag:
            return False
        
        flag.tenant_overrides[tenant_id] = value
        flag.updated_at = datetime.now(UTC)
        self._save_feature_flags()
        logger.info(f"Set override for flag {flag_name}: tenant {tenant_id} = {value}")
        return True
    
    def remove_tenant_override(self, flag_name: str, tenant_id: str) -> bool:
        """Remove tenant-specific override for a feature flag."""
        flag = self.get_feature_flag_by_name(flag_name)
        if not flag or tenant_id not in flag.tenant_overrides:
            return False
        
        del flag.tenant_overrides[tenant_id]
        flag.updated_at = datetime.now(UTC)
        self._save_feature_flags()
        logger.info(f"Removed override for flag {flag_name}: tenant {tenant_id}")
        return True
    
    def list_feature_flags(self) -> List[FeatureFlag]:
        """List all feature flags."""
        return list(self.feature_flags.values())


class AccessControlManager:
    """Manages access control rules."""
    
    def __init__(self, storage_path: str = "data/access_control"):
        self.storage_path = storage_path
        self.access_rules: Dict[str, AccessRule] = {}
        self._load_access_rules()
        self._create_default_rules()
    
    def _load_access_rules(self):
        """Load access rules from storage."""
        try:
            import os
            from pathlib import Path
            
            rules_file = Path(self.storage_path) / "access_rules.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    data = json.load(f)
                    for rule_data in data.values():
                        rule = AccessRule.from_dict(rule_data)
                        self.access_rules[rule.id] = rule
                logger.info(f"Loaded {len(self.access_rules)} access rules")
        except Exception as e:
            logger.warning(f"Could not load access rules: {e}")
    
    def _save_access_rules(self):
        """Save access rules to storage."""
        try:
            import os
            from pathlib import Path
            
            rules_file = Path(self.storage_path) / "access_rules.json"
            rules_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {rid: rule.to_dict() for rid, rule in self.access_rules.items()}
            with open(rules_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save access rules: {e}")
    
    def _create_default_rules(self):
        """Create default access rules if they don't exist."""
        if not self.access_rules:
            now = datetime.now(UTC)
            
            # Agent access rules
            agent_view_rule = AccessRule(
                id=str(uuid.uuid4()),
                name="agent_view",
                description="Allow viewing agents",
                resource="agents",
                action="view",
                conditions={"min_role": "viewer"},
                created_at=now,
                updated_at=now
            )
            
            agent_create_rule = AccessRule(
                id=str(uuid.uuid4()),
                name="agent_create",
                description="Allow creating agents",
                resource="agents",
                action="create",
                conditions={"min_role": "user", "subscription_required": True},
                created_at=now,
                updated_at=now
            )
            
            # Workflow access rules
            workflow_view_rule = AccessRule(
                id=str(uuid.uuid4()),
                name="workflow_view",
                description="Allow viewing workflows",
                resource="workflows",
                action="view",
                conditions={"min_role": "viewer"},
                created_at=now,
                updated_at=now
            )
            
            workflow_create_rule = AccessRule(
                id=str(uuid.uuid4()),
                name="workflow_create",
                description="Allow creating workflows",
                resource="workflows",
                action="create",
                conditions={"min_role": "user", "subscription_required": True},
                created_at=now,
                updated_at=now
            )
            
            self.access_rules[agent_view_rule.id] = agent_view_rule
            self.access_rules[agent_create_rule.id] = agent_create_rule
            self.access_rules[workflow_view_rule.id] = workflow_view_rule
            self.access_rules[workflow_create_rule.id] = workflow_create_rule
            self._save_access_rules()
    
    def create_access_rule(self, name: str, description: str, resource: str,
                          action: str, conditions: Dict[str, Any]) -> AccessRule:
        """Create a new access rule."""
        rule_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        rule = AccessRule(
            id=rule_id,
            name=name,
            description=description,
            resource=resource,
            action=action,
            conditions=conditions,
            created_at=now,
            updated_at=now
        )
        
        self.access_rules[rule_id] = rule
        self._save_access_rules()
        logger.info(f"Created access rule: {name} ({rule_id})")
        return rule
    
    def get_access_rule(self, rule_id: str) -> Optional[AccessRule]:
        """Get access rule by ID."""
        return self.access_rules.get(rule_id)
    
    def get_access_rules_for_resource(self, resource: str, action: str) -> List[AccessRule]:
        """Get access rules for a specific resource and action."""
        rules = []
        for rule in self.access_rules.values():
            if (rule.resource == resource and 
                rule.is_active):
                # Check if action matches or if rule allows all actions
                if rule.action == action or rule.action == "*":
                    rules.append(rule)
        return rules
    
    def check_access(self, user_id: str, resource: str, action: str,
                    user_role: str = None, tenant_id: str = None) -> bool:
        """Check if user has access to a resource."""
        rules = self.get_access_rules_for_resource(resource, action)
        
        if not rules:
            # No rules found, deny by default
            return False
        
        for rule in rules:
            if self._evaluate_rule_conditions(rule, user_id, user_role, tenant_id):
                return True
        
        return False
    
    def _evaluate_rule_conditions(self, rule: AccessRule, user_id: str,
                                user_role: str, tenant_id: str) -> bool:
        """Evaluate rule conditions."""
        conditions = rule.conditions
        
        # Check role requirement (support both "role" and "min_role")
        if "role" in conditions:
            required_role = conditions["role"]
            if user_role != required_role:
                return False
        elif "min_role" in conditions:
            min_role = conditions["min_role"]
            if not self._role_satisfies_minimum(user_role, min_role):
                return False
        
        # Check subscription requirement
        if conditions.get("subscription_required", False):
            if not self._has_active_subscription(tenant_id):
                return False
        
        # Check tenant-specific conditions
        if "tenant_plan" in conditions:
            required_plan = conditions["tenant_plan"]
            if not self._tenant_has_plan(tenant_id, required_plan):
                return False
        
        return True
    
    def _role_satisfies_minimum(self, user_role: str, min_role: str) -> bool:
        """Check if user role satisfies minimum requirement."""
        role_hierarchy = {
            "viewer": 1,
            "user": 2,
            "admin": 3
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        min_level = role_hierarchy.get(min_role, 0)
        
        # viewer (1) should not satisfy user (2) requirement
        return user_level >= min_level
    
    def _has_active_subscription(self, tenant_id: str) -> bool:
        """Check if tenant has active subscription."""
        # This would integrate with the subscription manager
        # For now, return True as placeholder
        return True
    
    def _tenant_has_plan(self, tenant_id: str, required_plan: str) -> bool:
        """Check if tenant has required plan."""
        # This would integrate with the billing manager
        # For now, return True as placeholder
        return True


# Global instances
feature_flag_manager = FeatureFlagManager()
access_control_manager = AccessControlManager() 