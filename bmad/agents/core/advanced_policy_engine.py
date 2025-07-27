"""
BMAD Advanced Policy Engine

Uitgebreide policy engine met complexe conditions, inheritance, composition,
dynamic updates, en versioning. Bouwt voort op de basis OPA integratie.
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import yaml

# Import BMAD modules
from .opa_policy_engine import OPAPolicyEngine, PolicyRequest, PolicyResponse

logger = logging.getLogger(__name__)

class PolicyType(Enum):
    """Types of policies."""
    ACCESS_CONTROL = "access_control"
    RESOURCE_LIMITS = "resource_limits"
    SECURITY_POLICIES = "security_policies"
    WORKFLOW_POLICIES = "workflow_policies"
    BEHAVIOR_RULES = "behavior_rules"
    COMPOSITE_POLICY = "composite_policy"
    INHERITED_POLICY = "inherited_policy"
    DYNAMIC_POLICY = "dynamic_policy"

class PolicySeverity(Enum):
    """Policy severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    def __lt__(self, other):
        if not isinstance(other, PolicySeverity):
            return NotImplemented
        severity_order = {
            PolicySeverity.LOW: 1,
            PolicySeverity.MEDIUM: 2,
            PolicySeverity.HIGH: 3,
            PolicySeverity.CRITICAL: 4
        }
        return severity_order[self] < severity_order[other]
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other

class PolicyStatus(Enum):
    """Policy status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"

@dataclass
class PolicyCondition:
    """Represents a policy condition."""
    condition_id: str
    condition_type: str
    parameters: Dict[str, Any]
    description: str
    severity: PolicySeverity = PolicySeverity.MEDIUM
    enabled: bool = True

@dataclass
class PolicyRule:
    """Represents a policy rule."""
    rule_id: str
    rule_name: str
    policy_type: PolicyType
    conditions: List[PolicyCondition]
    actions: List[str]
    priority: int = 100
    enabled: bool = True
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyDefinition:
    """Represents a complete policy definition."""
    policy_id: str
    policy_name: str
    policy_type: PolicyType
    version: str
    rules: List[PolicyRule]
    parent_policy: Optional[str] = None
    inheritance_rules: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyEvaluationResult:
    """Result of a policy evaluation."""
    policy_id: str
    rule_id: str
    allowed: bool
    reason: str
    conditions_met: List[str]
    conditions_failed: List[str]
    severity: PolicySeverity
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyVersion:
    """Represents a policy version."""
    version_id: str
    policy_id: str
    version_number: str
    content: Dict[str, Any]
    created_at: datetime
    created_by: str
    change_description: str
    is_active: bool = False

class AdvancedPolicyEngine:
    """
    Advanced policy engine with complex conditions, inheritance, and dynamic updates.
    """
    
    def __init__(self, opa_url: str = "http://localhost:8181", policies_dir: str = "policies"):
        self.opa_engine = OPAPolicyEngine(opa_url=opa_url)
        self.policies_dir = Path(policies_dir)
        self.policies_dir.mkdir(exist_ok=True)
        
        # Policy storage
        self.policies: Dict[str, PolicyDefinition] = {}
        self.policy_versions: Dict[str, List[PolicyVersion]] = {}
        self.policy_cache: Dict[str, Any] = {}
        
        # Condition evaluators
        self.condition_evaluators: Dict[str, Callable] = {}
        self._register_default_evaluators()
        
        # Policy inheritance registry
        self.inheritance_registry: Dict[str, List[str]] = {}
        
        # Dynamic policy updates
        self.policy_update_callbacks: List[Callable] = []
        self.last_policy_sync = datetime.now()
        
        # Load existing policies
        self._load_policies()
        
        logger.info("Advanced Policy Engine geïnitialiseerd")
    
    def _register_default_evaluators(self):
        """Register default condition evaluators."""
        self.condition_evaluators.update({
            "time_based": self._evaluate_time_condition,
            "resource_based": self._evaluate_resource_condition,
            "role_based": self._evaluate_role_condition,
            "context_based": self._evaluate_context_condition,
            "composite": self._evaluate_composite_condition,
            "inheritance": self._evaluate_inheritance_condition,
            "dynamic": self._evaluate_dynamic_condition
        })
    
    def _evaluate_time_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate time-based conditions."""
        params = condition.parameters
        current_time = datetime.now()
        
        if "time_window" in params:
            # Handle time-only strings (HH:MM:SS)
            start_str = params["time_window"]["start"]
            end_str = params["time_window"]["end"]
            
            # Convert to full datetime for today
            today = current_time.date()
            try:
                if len(start_str) <= 8:  # Time only (HH:MM:SS)
                    start_time = datetime.combine(today, datetime.strptime(start_str, "%H:%M:%S").time())
                    end_time = datetime.combine(today, datetime.strptime(end_str, "%H:%M:%S").time())
                else:  # Full datetime
                    start_time = datetime.fromisoformat(start_str)
                    end_time = datetime.fromisoformat(end_str)
                
                return start_time <= current_time <= end_time
            except ValueError:
                logger.warning(f"Invalid time format in condition {condition.condition_id}")
                return False
        
        if "day_of_week" in params:
            return current_time.weekday() in params["day_of_week"]
        
        if "hour_of_day" in params:
            return current_time.hour in params["hour_of_day"]
        
        return True
    
    def _evaluate_resource_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate resource-based conditions."""
        params = condition.parameters
        
        if "cpu_threshold" in params:
            cpu_usage = context.get("cpu_usage", 0)
            return cpu_usage <= params["cpu_threshold"]
        
        if "memory_threshold" in params:
            memory_usage = context.get("memory_usage", 0)
            return memory_usage <= params["memory_threshold"]
        
        if "api_calls_limit" in params:
            api_calls = context.get("api_calls_count", 0)
            return api_calls <= params["api_calls_limit"]
        
        return True
    
    def _evaluate_role_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate role-based conditions."""
        params = condition.parameters
        user_roles = context.get("user_roles", [])
        required_roles = params.get("required_roles", [])
        
        if not required_roles:
            return True
        
        return any(role in user_roles for role in required_roles)
    
    def _evaluate_context_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate context-based conditions."""
        params = condition.parameters
        
        for key, expected_value in params.get("context_values", {}).items():
            actual_value = context.get(key)
            if actual_value != expected_value:
                return False
        
        return True
    
    def _evaluate_composite_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate composite conditions."""
        params = condition.parameters
        operator = params.get("operator", "AND")
        sub_conditions = params.get("conditions", [])
        
        results = []
        for sub_condition_data in sub_conditions:
            sub_condition = PolicyCondition(**sub_condition_data)
            evaluator = self.condition_evaluators.get(sub_condition.condition_type)
            if evaluator:
                results.append(evaluator(sub_condition, context))
        
        if operator == "AND":
            return all(results)
        elif operator == "OR":
            return any(results)
        elif operator == "NOT":
            return not any(results)
        
        return True
    
    def _evaluate_inheritance_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate inheritance conditions."""
        params = condition.parameters
        policy_id = params.get("policy_id")
        
        if not policy_id or policy_id not in self.policies:
            return False
        
        parent_policy = self.policies[policy_id]
        return parent_policy.status == PolicyStatus.ACTIVE
    
    def _evaluate_dynamic_condition(self, condition: PolicyCondition, context: Dict[str, Any]) -> bool:
        """Evaluate dynamic conditions."""
        params = condition.parameters
        dynamic_key = params.get("dynamic_key")
        dynamic_value = params.get("dynamic_value")
        
        if dynamic_key and dynamic_value:
            actual_value = context.get(dynamic_key)
            return actual_value == dynamic_value
        
        return True
    
    def create_policy(self, policy_data: Dict[str, Any]) -> PolicyDefinition:
        """Create a new policy definition."""
        policy_id = policy_data.get("policy_id") or f"policy_{int(time.time())}"
        
        # Create policy rules
        rules = []
        for rule_data in policy_data.get("rules", []):
            conditions = []
            for condition_data in rule_data.get("conditions", []):
                # Convert severity string to enum if needed
                if isinstance(condition_data.get("severity"), str):
                    condition_data["severity"] = PolicySeverity(condition_data["severity"])
                condition = PolicyCondition(**condition_data)
                conditions.append(condition)
            
            rule = PolicyRule(
                rule_id=rule_data.get("rule_id"),
                rule_name=rule_data.get("rule_name"),
                policy_type=PolicyType(rule_data.get("policy_type")),
                conditions=conditions,
                actions=rule_data.get("actions", []),
                priority=rule_data.get("priority", 100),
                description=rule_data.get("description", "")
            )
            rules.append(rule)
        
        # Create policy definition
        policy = PolicyDefinition(
            policy_id=policy_id,
            policy_name=policy_data.get("policy_name"),
            policy_type=PolicyType(policy_data.get("policy_type")),
            version=policy_data.get("version", "1.0.0"),
            rules=rules,
            parent_policy=policy_data.get("parent_policy"),
            inheritance_rules=policy_data.get("inheritance_rules", {}),
            status=PolicyStatus(policy_data.get("status", "active")),
            metadata=policy_data.get("metadata", {})
        )
        
        # Store policy
        self.policies[policy_id] = policy
        
        # Create version
        self._create_policy_version(policy, "Initial version")
        
        # Update inheritance registry
        if policy.parent_policy:
            if policy.parent_policy not in self.inheritance_registry:
                self.inheritance_registry[policy.parent_policy] = []
            self.inheritance_registry[policy.parent_policy].append(policy_id)
        
        # Save to file
        self._save_policy(policy)
        
        logger.info(f"Policy created: {policy_id}")
        return policy
    
    def _create_policy_version(self, policy: PolicyDefinition, change_description: str):
        """Create a new policy version."""
        version_id = f"{policy.policy_id}_v{policy.version}_{int(time.time())}"
        
        version = PolicyVersion(
            version_id=version_id,
            policy_id=policy.policy_id,
            version_number=policy.version,
            content=self._policy_to_dict(policy),
            created_at=datetime.now(),
            created_by="system",
            change_description=change_description,
            is_active=(policy.status == PolicyStatus.ACTIVE)
        )
        
        if policy.policy_id not in self.policy_versions:
            self.policy_versions[policy.policy_id] = []
        
        self.policy_versions[policy.policy_id].append(version)
        
        # Deactivate other versions
        for v in self.policy_versions[policy.policy_id]:
            if v.version_id != version_id:
                v.is_active = False
    
    def _policy_to_dict(self, policy: PolicyDefinition) -> Dict[str, Any]:
        """Convert policy to dictionary."""
        return {
            "policy_id": policy.policy_id,
            "policy_name": policy.policy_name,
            "policy_type": policy.policy_type.value,
            "version": policy.version,
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "policy_type": rule.policy_type.value,
                    "conditions": [
                        {
                            "condition_id": cond.condition_id,
                            "condition_type": cond.condition_type,
                            "parameters": cond.parameters,
                            "description": cond.description,
                            "severity": cond.severity.value if hasattr(cond.severity, 'value') else cond.severity,
                            "enabled": cond.enabled
                        }
                        for cond in rule.conditions
                    ],
                    "actions": rule.actions,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "description": rule.description,
                    "metadata": rule.metadata
                }
                for rule in policy.rules
            ],
            "parent_policy": policy.parent_policy,
            "inheritance_rules": policy.inheritance_rules,
            "status": policy.status.value,
            "created_at": policy.created_at.isoformat(),
            "updated_at": policy.updated_at.isoformat(),
            "expires_at": policy.expires_at.isoformat() if policy.expires_at else None,
            "metadata": policy.metadata
        }
    
    def _save_policy(self, policy: PolicyDefinition):
        """Save policy to file."""
        policy_file = self.policies_dir / f"{policy.policy_id}.json"
        with open(policy_file, 'w') as f:
            json.dump(self._policy_to_dict(policy), f, indent=2, default=str)
    
    def _load_policies(self):
        """Load policies from files."""
        for policy_file in self.policies_dir.glob("*.json"):
            try:
                with open(policy_file, 'r') as f:
                    policy_data = json.load(f)
                
                # Convert string values back to enums
                policy_data["policy_type"] = PolicyType(policy_data["policy_type"])
                policy_data["status"] = PolicyStatus(policy_data["status"])
                
                # Convert rules and conditions
                rules = []
                for rule_data in policy_data["rules"]:
                    rule_data["policy_type"] = PolicyType(rule_data["policy_type"])
                    
                    conditions = []
                    for condition_data in rule_data["conditions"]:
                        condition_data["severity"] = PolicySeverity(condition_data["severity"])
                        conditions.append(PolicyCondition(**condition_data))
                    
                    rule_data["conditions"] = conditions
                    rules.append(PolicyRule(**rule_data))
                
                policy_data["rules"] = rules
                
                # Convert datetime strings back to datetime objects
                if "created_at" in policy_data and isinstance(policy_data["created_at"], str):
                    policy_data["created_at"] = datetime.fromisoformat(policy_data["created_at"])
                if "updated_at" in policy_data and isinstance(policy_data["updated_at"], str):
                    policy_data["updated_at"] = datetime.fromisoformat(policy_data["updated_at"])
                if "expires_at" in policy_data and policy_data["expires_at"] and isinstance(policy_data["expires_at"], str):
                    policy_data["expires_at"] = datetime.fromisoformat(policy_data["expires_at"])
                
                # Create policy definition
                policy_id = policy_data["policy_id"]
                self.policies[policy_id] = PolicyDefinition(**policy_data)
                logger.info(f"Loaded policy: {policy_id}")
                
            except Exception as e:
                logger.error(f"Failed to load policy from {policy_file}: {e}")
    
    async def evaluate_policy(self, policy_id: str, request: PolicyRequest) -> PolicyEvaluationResult:
        """Evaluate a specific policy."""
        if policy_id not in self.policies:
            return PolicyEvaluationResult(
                policy_id=policy_id,
                rule_id="",
                allowed=False,
                reason=f"Policy {policy_id} not found",
                conditions_met=[],
                conditions_failed=[],
                severity=PolicySeverity.HIGH,
                timestamp=datetime.now()
            )
        
        policy = self.policies[policy_id]
        
        # Check if policy is active
        if policy.status != PolicyStatus.ACTIVE:
            return PolicyEvaluationResult(
                policy_id=policy_id,
                rule_id="",
                allowed=False,
                reason=f"Policy {policy_id} is not active (status: {policy.status.value})",
                conditions_met=[],
                conditions_failed=[],
                severity=PolicySeverity.MEDIUM,
                timestamp=datetime.now()
            )
        
        # Check expiration
        if policy.expires_at and datetime.now() > policy.expires_at:
            return PolicyEvaluationResult(
                policy_id=policy_id,
                rule_id="",
                allowed=False,
                reason=f"Policy {policy_id} has expired",
                conditions_met=[],
                conditions_failed=[],
                severity=PolicySeverity.HIGH,
                timestamp=datetime.now()
            )
        
        # Evaluate rules in priority order
        sorted_rules = sorted(policy.rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Evaluate conditions
            conditions_met = []
            conditions_failed = []
            
            for condition in rule.conditions:
                if not condition.enabled:
                    continue
                
                evaluator = self.condition_evaluators.get(condition.condition_type)
                if evaluator:
                    if evaluator(condition, request.context):
                        conditions_met.append(condition.condition_id)
                    else:
                        conditions_failed.append(condition.condition_id)
                else:
                    conditions_failed.append(condition.condition_id)
            
            # If all conditions are met, apply the rule
            if not conditions_failed:
                allowed = "allow" in rule.actions
                reason = f"Rule {rule.rule_name} applied successfully"
                
                return PolicyEvaluationResult(
                    policy_id=policy_id,
                    rule_id=rule.rule_id,
                    allowed=allowed,
                    reason=reason,
                    conditions_met=conditions_met,
                    conditions_failed=conditions_failed,
                    severity=max([c.severity for c in rule.conditions], default=PolicySeverity.MEDIUM),
                    timestamp=datetime.now(),
                    metadata={"rule_name": rule.rule_name, "actions": rule.actions}
                )
        
        # No rules matched
        return PolicyEvaluationResult(
            policy_id=policy_id,
            rule_id="",
            allowed=False,
            reason=f"No matching rules found in policy {policy_id}",
            conditions_met=[],
            conditions_failed=[],
            severity=PolicySeverity.MEDIUM,
            timestamp=datetime.now()
        )
    
    async def evaluate_composite_policy(self, policy_ids: List[str], request: PolicyRequest) -> List[PolicyEvaluationResult]:
        """Evaluate multiple policies and return composite result."""
        results = []
        
        for policy_id in policy_ids:
            result = await self.evaluate_policy(policy_id, request)
            results.append(result)
        
        return results
    
    async def evaluate_inherited_policy(self, policy_id: str, request: PolicyRequest) -> PolicyEvaluationResult:
        """Evaluate a policy with inheritance."""
        if policy_id not in self.policies:
            return PolicyEvaluationResult(
                policy_id=policy_id,
                rule_id="",
                allowed=False,
                reason=f"Policy {policy_id} not found",
                conditions_met=[],
                conditions_failed=[],
                severity=PolicySeverity.HIGH,
                timestamp=datetime.now()
            )
        
        policy = self.policies[policy_id]
        
        # Evaluate parent policies first
        if policy.parent_policy:
            parent_result = await self.evaluate_inherited_policy(policy.parent_policy, request)
            if not parent_result.allowed:
                return parent_result
        
        # Evaluate current policy
        return await self.evaluate_policy(policy_id, request)
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any], change_description: str) -> PolicyDefinition:
        """Update an existing policy."""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")
        
        policy = self.policies[policy_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        policy.updated_at = datetime.now()
        
        # Create new version
        self._create_policy_version(policy, change_description)
        
        # Save to file
        self._save_policy(policy)
        
        # Trigger update callbacks
        for callback in self.policy_update_callbacks:
            try:
                callback(policy_id, updates)
            except Exception as e:
                logger.error(f"Policy update callback failed: {e}")
        
        logger.info(f"Policy updated: {policy_id}")
        return policy
    
    def rollback_policy(self, policy_id: str, version_number: str) -> PolicyDefinition:
        """Rollback a policy to a specific version."""
        if policy_id not in self.policy_versions:
            raise ValueError(f"No versions found for policy {policy_id}")
        
        versions = self.policy_versions[policy_id]
        target_version = None
        
        for version in versions:
            if version.version_number == version_number:
                target_version = version
                break
        
        if not target_version:
            raise ValueError(f"Version {version_number} not found for policy {policy_id}")
        
        # Restore policy from version
        policy_data = target_version.content
        policy_data["policy_type"] = PolicyType(policy_data["policy_type"])
        policy_data["status"] = PolicyStatus(policy_data["status"])
        
        # Recreate policy
        self.policies[policy_id] = self.create_policy(policy_data)
        
        # Create rollback version
        self._create_policy_version(self.policies[policy_id], f"Rollback to version {version_number}")
        
        logger.info(f"Policy rolled back: {policy_id} to version {version_number}")
        return self.policies[policy_id]
    
    def get_policy_versions(self, policy_id: str) -> List[PolicyVersion]:
        """Get all versions of a policy."""
        return self.policy_versions.get(policy_id, [])
    
    def add_policy_update_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Add a callback for policy updates."""
        self.policy_update_callbacks.append(callback)
    
    def create_default_policies(self):
        """Create default advanced policies."""
        
        # Advanced Access Control Policy
        advanced_access_policy = {
            "policy_id": "advanced_access_control",
            "policy_name": "Advanced Access Control",
            "policy_type": "access_control",
            "version": "2.0.0",
            "rules": [
                {
                    "rule_id": "time_based_access",
                    "rule_name": "Time-based Access Control",
                    "policy_type": "access_control",
                    "priority": 200,
                    "conditions": [
                        {
                            "condition_id": "business_hours",
                            "condition_type": "time_based",
                            "parameters": {
                                "time_window": {
                                    "start": "09:00:00",
                                    "end": "17:00:00"
                                },
                                "day_of_week": [0, 1, 2, 3, 4]  # Monday to Friday
                            },
                            "description": "Allow access during business hours",
                            "severity": "medium",
                            "enabled": True
                        },
                        {
                            "condition_id": "role_check",
                            "condition_type": "role_based",
                            "parameters": {
                                "required_roles": ["admin", "manager", "developer"]
                            },
                            "description": "Check user roles",
                            "severity": "high",
                            "enabled": True
                        }
                    ],
                    "actions": ["allow"],
                    "description": "Time and role-based access control"
                }
            ],
            "status": "active",
            "metadata": {
                "category": "security",
                "tags": ["access_control", "time_based", "role_based"]
            }
        }
        
        # Resource Management Policy
        resource_policy = {
            "policy_id": "advanced_resource_management",
            "policy_name": "Advanced Resource Management",
            "policy_type": "resource_limits",
            "version": "2.0.0",
            "rules": [
                {
                    "rule_id": "resource_thresholds",
                    "rule_name": "Resource Threshold Monitoring",
                    "policy_type": "resource_limits",
                    "priority": 150,
                    "conditions": [
                        {
                            "condition_id": "cpu_limit",
                            "condition_type": "resource_based",
                            "parameters": {
                                "cpu_threshold": 80
                            },
                            "description": "CPU usage threshold",
                            "severity": "high",
                            "enabled": True
                        },
                        {
                            "condition_id": "memory_limit",
                            "condition_type": "resource_based",
                            "parameters": {
                                "memory_threshold": 85
                            },
                            "description": "Memory usage threshold",
                            "severity": "high",
                            "enabled": True
                        },
                        {
                            "condition_id": "api_limit",
                            "condition_type": "resource_based",
                            "parameters": {
                                "api_calls_limit": 1000
                            },
                            "description": "API calls limit",
                            "severity": "medium",
                            "enabled": True
                        }
                    ],
                    "actions": ["allow", "monitor"],
                    "description": "Resource usage monitoring and limits"
                }
            ],
            "status": "active",
            "metadata": {
                "category": "performance",
                "tags": ["resource_management", "monitoring", "limits"]
            }
        }
        
        # Composite Security Policy
        composite_security_policy = {
            "policy_id": "composite_security_policy",
            "policy_name": "Composite Security Policy",
            "policy_type": "composite_policy",
            "version": "1.0.0",
            "rules": [
                {
                    "rule_id": "security_composite",
                    "rule_name": "Multi-factor Security Check",
                    "policy_type": "composite_policy",
                    "priority": 300,
                    "conditions": [
                        {
                            "condition_id": "composite_security",
                            "condition_type": "composite",
                            "parameters": {
                                "operator": "AND",
                                "conditions": [
                                    {
                                        "condition_id": "role_check",
                                        "condition_type": "role_based",
                                        "parameters": {
                                            "required_roles": ["admin", "security_officer"]
                                        },
                                        "description": "Security role check",
                                        "severity": "critical",
                                        "enabled": True
                                    },
                                    {
                                        "condition_id": "time_check",
                                        "condition_type": "time_based",
                                        "parameters": {
                                            "time_window": {
                                                "start": "00:00:00",
                                                "end": "23:59:59"
                                            }
                                        },
                                        "description": "24/7 access",
                                        "severity": "medium",
                                        "enabled": True
                                    }
                                ]
                            },
                            "description": "Composite security conditions",
                            "severity": "critical",
                            "enabled": True
                        }
                    ],
                    "actions": ["allow", "audit"],
                    "description": "Multi-factor security policy"
                }
            ],
            "status": "active",
            "metadata": {
                "category": "security",
                "tags": ["composite", "multi_factor", "audit"]
            }
        }
        
        # Create policies
        self.create_policy(advanced_access_policy)
        self.create_policy(resource_policy)
        self.create_policy(composite_security_policy)
        
        logger.info("Default advanced policies created")

# Global advanced policy engine instance
_advanced_policy_engine: Optional[AdvancedPolicyEngine] = None

def get_advanced_policy_engine() -> AdvancedPolicyEngine:
    """Get the global advanced policy engine instance."""
    global _advanced_policy_engine
    if _advanced_policy_engine is None:
        _advanced_policy_engine = AdvancedPolicyEngine()
        _advanced_policy_engine.create_default_policies()
    return _advanced_policy_engine 