"""
Enterprise Security Module

Provides enterprise-grade security features including audit logging,
security policies, and compliance monitoring for BMAD deployments.
"""

import uuid
import json
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditEventType(Enum):
    """Audit event type enumeration."""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    PERMISSION_CHANGE = "permission_change"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class SecurityPolicy:
    """Represents a security policy."""
    id: str
    name: str
    description: str
    policy_type: str
    rules: Dict[str, Any]
    security_level: SecurityLevel
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert security policy to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['security_level'] = self.security_level.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityPolicy':
        """Create security policy from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['security_level'] = SecurityLevel(data['security_level'])
        return cls(**data)


@dataclass
class AuditLog:
    """Represents an audit log entry."""
    id: str
    timestamp: datetime
    user_id: str
    tenant_id: str
    event_type: AuditEventType
    resource: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        """Create audit log from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['event_type'] = AuditEventType(data['event_type'])
        return cls(**data)


class EnterpriseSecurityManager:
    """Manages enterprise security features."""
    
    def __init__(self, storage_path: str = "data/security"):
        self.storage_path = storage_path
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.audit_logs: List[AuditLog] = []
        self._load_data()
        self._create_default_policies()
    
    def _load_data(self):
        """Load security data from storage."""
        try:
            import os
            from pathlib import Path
            
            # Load security policies
            policies_file = Path(self.storage_path) / "security_policies.json"
            if policies_file.exists():
                with open(policies_file, 'r') as f:
                    data = json.load(f)
                    for policy_data in data.values():
                        policy = SecurityPolicy.from_dict(policy_data)
                        self.security_policies[policy.id] = policy
            
            # Load audit logs
            audit_file = Path(self.storage_path) / "audit_logs.json"
            if audit_file.exists():
                with open(audit_file, 'r') as f:
                    data = json.load(f)
                    for log_data in data:
                        log = AuditLog.from_dict(log_data)
                        self.audit_logs.append(log)
                        
            logger.info(f"Loaded {len(self.security_policies)} security policies and {len(self.audit_logs)} audit logs")
        except Exception as e:
            logger.warning(f"Could not load security data: {e}")
    
    def _save_data(self):
        """Save security data to storage."""
        try:
            import os
            from pathlib import Path
            
            # Save security policies
            policies_file = Path(self.storage_path) / "security_policies.json"
            policies_file.parent.mkdir(parents=True, exist_ok=True)
            policies_data = {pid: policy.to_dict() for pid, policy in self.security_policies.items()}
            with open(policies_file, 'w') as f:
                json.dump(policies_data, f, indent=2)
            
            # Save audit logs (keep only last 10000 entries)
            audit_file = Path(self.storage_path) / "audit_logs.json"
            recent_logs = self.audit_logs[-10000:] if len(self.audit_logs) > 10000 else self.audit_logs
            audit_data = [log.to_dict() for log in recent_logs]
            with open(audit_file, 'w') as f:
                json.dump(audit_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save security data: {e}")
    
    def _create_default_policies(self):
        """Create default security policies if they don't exist."""
        if not self.security_policies:
            now = datetime.utcnow()
            
            # Password policy
            password_policy = SecurityPolicy(
                id=str(uuid.uuid4()),
                name="password_policy",
                description="Password complexity and expiration requirements",
                policy_type="password",
                rules={
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "max_age_days": 90,
                    "prevent_reuse": 5
                },
                security_level=SecurityLevel.MEDIUM,
                created_at=now,
                updated_at=now
            )
            
            # Session policy
            session_policy = SecurityPolicy(
                id=str(uuid.uuid4()),
                name="session_policy",
                description="Session management and timeout requirements",
                policy_type="session",
                rules={
                    "session_timeout_minutes": 30,
                    "max_concurrent_sessions": 5,
                    "require_https": True,
                    "secure_cookies": True
                },
                security_level=SecurityLevel.MEDIUM,
                created_at=now,
                updated_at=now
            )
            
            # Access control policy
            access_policy = SecurityPolicy(
                id=str(uuid.uuid4()),
                name="access_control_policy",
                description="Access control and permission requirements",
                policy_type="access_control",
                rules={
                    "require_mfa": False,
                    "max_login_attempts": 5,
                    "lockout_duration_minutes": 15,
                    "require_approval_for_sensitive_actions": True
                },
                security_level=SecurityLevel.HIGH,
                created_at=now,
                updated_at=now
            )
            
            # Data protection policy
            data_policy = SecurityPolicy(
                id=str(uuid.uuid4()),
                name="data_protection_policy",
                description="Data protection and encryption requirements",
                policy_type="data_protection",
                rules={
                    "encrypt_data_at_rest": True,
                    "encrypt_data_in_transit": True,
                    "data_retention_days": 2555,  # 7 years
                    "require_data_classification": True
                },
                security_level=SecurityLevel.CRITICAL,
                created_at=now,
                updated_at=now
            )
            
            self.security_policies[password_policy.id] = password_policy
            self.security_policies[session_policy.id] = session_policy
            self.security_policies[access_policy.id] = access_policy
            self.security_policies[data_policy.id] = data_policy
            self._save_data()
    
    def create_security_policy(self, name: str, description: str, policy_type: str,
                             rules: Dict[str, Any], security_level: SecurityLevel) -> SecurityPolicy:
        """Create a new security policy."""
        policy_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        policy = SecurityPolicy(
            id=policy_id,
            name=name,
            description=description,
            policy_type=policy_type,
            rules=rules,
            security_level=security_level,
            created_at=now,
            updated_at=now
        )
        
        self.security_policies[policy_id] = policy
        self._save_data()
        logger.info(f"Created security policy: {name} ({policy_id})")
        return policy
    
    def get_security_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get security policy by ID."""
        return self.security_policies.get(policy_id)
    
    def get_policies_by_type(self, policy_type: str) -> List[SecurityPolicy]:
        """Get security policies by type."""
        return [policy for policy in self.security_policies.values() 
                if policy.policy_type == policy_type and policy.is_active]
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against password policy."""
        password_policies = self.get_policies_by_type("password")
        if not password_policies:
            return {"valid": True, "errors": []}
        
        policy = password_policies[0]
        rules = policy.rules
        errors = []
        
        # Check minimum length
        if len(password) < rules.get("min_length", 8):
            errors.append(f"Password must be at least {rules['min_length']} characters long")
        
        # Check character requirements
        if rules.get("require_uppercase", False) and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if rules.get("require_lowercase", False) and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if rules.get("require_numbers", False) and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if rules.get("require_special_chars", False) and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "policy_level": policy.security_level.value
        }
    
    def log_audit_event(self, user_id: str, tenant_id: str, event_type: AuditEventType,
                       resource: str, action: str, details: Dict[str, Any],
                       ip_address: str = None, user_agent: str = None, success: bool = True):
        """Log an audit event."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            tenant_id=tenant_id,
            event_type=event_type,
            resource=resource,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        
        self.audit_logs.append(log)
        self._save_data()
        logger.info(f"Audit log: {event_type.value} - {user_id} - {resource} - {action}")
    
    def get_audit_logs(self, user_id: str = None, tenant_id: str = None,
                      event_type: AuditEventType = None, start_date: datetime = None,
                      end_date: datetime = None, limit: int = 100) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        logs = self.audit_logs
        
        # Apply filters
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if tenant_id:
            logs = [log for log in logs if log.tenant_id == tenant_id]
        
        if event_type:
            logs = [log for log in logs if log.event_type == event_type]
        
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]
        
        # Sort by timestamp (newest first) and limit
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def generate_security_report(self, tenant_id: str = None, 
                               start_date: datetime = None,
                               end_date: datetime = None) -> Dict[str, Any]:
        """Generate a security report."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        logs = self.get_audit_logs(tenant_id=tenant_id, start_date=start_date, end_date=end_date, limit=10000)
        
        # Analyze events
        event_counts = {}
        user_activity = {}
        security_violations = []
        
        for log in logs:
            # Count events by type
            event_type = log.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Track user activity
            user_activity[log.user_id] = user_activity.get(log.user_id, 0) + 1
            
            # Check for security violations
            if log.event_type == AuditEventType.SECURITY_VIOLATION or not log.success:
                security_violations.append(log)
        
        # Get policy compliance
        policy_compliance = {}
        for policy in self.security_policies.values():
            if policy.is_active:
                policy_compliance[policy.name] = {
                    "type": policy.policy_type,
                    "security_level": policy.security_level.value,
                    "rules": policy.rules
                }
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "tenant_id": tenant_id,
            "summary": {
                "total_events": len(logs),
                "unique_users": len(user_activity),
                "security_violations": len(security_violations)
            },
            "event_breakdown": event_counts,
            "top_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
            "security_violations": [log.to_dict() for log in security_violations],
            "policy_compliance": policy_compliance
        }
    
    def check_security_compliance(self, tenant_id: str) -> Dict[str, Any]:
        """Check security compliance for a tenant."""
        # Get recent audit logs
        recent_logs = self.get_audit_logs(tenant_id=tenant_id, limit=1000)
        
        # Check for security violations
        violations = [log for log in recent_logs if log.event_type == AuditEventType.SECURITY_VIOLATION]
        
        # Check login patterns
        login_events = [log for log in recent_logs if log.event_type == AuditEventType.LOGIN]
        failed_logins = [log for log in login_events if not log.success]
        
        # Check access patterns
        access_events = [log for log in recent_logs if log.event_type == AuditEventType.ACCESS]
        
        compliance_score = 100
        
        # Deduct points for violations
        compliance_score -= len(violations) * 10
        
        # Deduct points for failed logins
        if len(login_events) > 0:
            failure_rate = len(failed_logins) / len(login_events)
            compliance_score -= failure_rate * 20
        
        compliance_score = max(0, compliance_score)
        
        return {
            "tenant_id": tenant_id,
            "compliance_score": compliance_score,
            "security_violations": len(violations),
            "failed_login_rate": len(failed_logins) / len(login_events) if login_events else 0,
            "total_access_events": len(access_events),
            "assessment_date": datetime.utcnow().isoformat(),
            "recommendations": self._generate_security_recommendations(violations, failed_logins)
        }
    
    def _generate_security_recommendations(self, violations: List[AuditLog], 
                                         failed_logins: List[AuditLog]) -> List[str]:
        """Generate security recommendations based on audit data."""
        recommendations = []
        
        if len(violations) > 5:
            recommendations.append("High number of security violations detected. Review access controls and user permissions.")
        
        if len(failed_logins) > 10:
            recommendations.append("Multiple failed login attempts detected. Consider implementing account lockout policies.")
        
        if not recommendations:
            recommendations.append("Security posture appears healthy. Continue monitoring for any unusual activity.")
        
        return recommendations


# Global instance
enterprise_security_manager = EnterpriseSecurityManager() 