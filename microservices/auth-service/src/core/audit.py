"""
Audit service for the Authentication Service.

This module handles audit logging for security events and user actions.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)


class AuditService:
    """Audit service for security event logging."""
    
    def __init__(self, database_service):
        """Initialize the audit service."""
        self.db = database_service
    
    async def log_event(
        self,
        action: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Log an audit event.
        
        Args:
            action: The action performed
            user_id: ID of the user performing the action
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            details: Additional details about the event
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            audit_data = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            await self.db.create_audit_log(audit_data)
            
            # Also log to application logs
            logger.info(
                f"Audit event: {action} by user {user_id} on {resource_type}:{resource_id}",
                extra={
                    "audit_event": True,
                    "user_id": user_id,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "ip_address": ip_address
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return False
    
    async def log_login_success(self, user_id: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log successful login."""
        return await self.log_event(
            action="login_success",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "authentication"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_login_failure(self, email: str, reason: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log failed login attempt."""
        return await self.log_event(
            action="login_failure",
            user_id=None,
            resource_type="user",
            resource_id=email,
            details={
                "event_type": "authentication",
                "reason": reason,
                "email": email
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_logout(self, user_id: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log user logout."""
        return await self.log_event(
            action="logout",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "authentication"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_password_change(self, user_id: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log password change."""
        return await self.log_event(
            action="password_change",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "security"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_password_reset_request(self, email: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log password reset request."""
        return await self.log_event(
            action="password_reset_request",
            user_id=None,
            resource_type="user",
            resource_id=email,
            details={
                "event_type": "security",
                "email": email
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_password_reset_complete(self, user_id: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log password reset completion."""
        return await self.log_event(
            action="password_reset_complete",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "security"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_user_registration(self, user_id: str, email: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log user registration."""
        return await self.log_event(
            action="user_registration",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={
                "event_type": "user_management",
                "email": email
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_user_update(self, user_id: str, updated_by: str, changes: Dict[str, Any], ip_address: str = None, user_agent: str = None) -> bool:
        """Log user update."""
        return await self.log_event(
            action="user_update",
            user_id=updated_by,
            resource_type="user",
            resource_id=user_id,
            details={
                "event_type": "user_management",
                "changes": changes
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_user_deletion(self, user_id: str, deleted_by: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log user deletion."""
        return await self.log_event(
            action="user_deletion",
            user_id=deleted_by,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "user_management"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_role_assignment(self, user_id: str, role_id: str, assigned_by: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log role assignment."""
        return await self.log_event(
            action="role_assignment",
            user_id=assigned_by,
            resource_type="role",
            resource_id=role_id,
            details={
                "event_type": "authorization",
                "target_user_id": user_id
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_role_removal(self, user_id: str, role_id: str, removed_by: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log role removal."""
        return await self.log_event(
            action="role_removal",
            user_id=removed_by,
            resource_type="role",
            resource_id=role_id,
            details={
                "event_type": "authorization",
                "target_user_id": user_id
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_mfa_enable(self, user_id: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log MFA enablement."""
        return await self.log_event(
            action="mfa_enable",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "security"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_mfa_disable(self, user_id: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log MFA disablement."""
        return await self.log_event(
            action="mfa_disable",
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            details={"event_type": "security"},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_session_revocation(self, user_id: str, session_id: str, revoked_by: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Log session revocation."""
        return await self.log_event(
            action="session_revocation",
            user_id=revoked_by,
            resource_type="session",
            resource_id=session_id,
            details={
                "event_type": "security",
                "target_user_id": user_id
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_suspicious_activity(self, user_id: str = None, activity_type: str = None, details: Dict[str, Any] = None, ip_address: str = None, user_agent: str = None) -> bool:
        """Log suspicious activity."""
        return await self.log_event(
            action="suspicious_activity",
            user_id=user_id,
            resource_type="security",
            resource_id=activity_type,
            details={
                "event_type": "security",
                "activity_type": activity_type,
                **(details or {})
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def get_audit_logs(
        self,
        user_id: str = None,
        action: str = None,
        resource_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with filtering.
        
        Args:
            user_id: Filter by user ID
            action: Filter by action
            resource_type: Filter by resource type
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of audit log entries
        """
        try:
            # For now, we'll use the basic list function
            # In a real implementation, you'd add filtering logic here
            logs = await self.db.list_audit_logs(user_id=user_id, skip=skip, limit=limit)
            return logs
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []
    
    async def get_security_events(self, user_id: str = None, days: int = 30) -> Dict[str, int]:
        """
        Get security event statistics.
        
        Args:
            user_id: Filter by user ID
            days: Number of days to look back
            
        Returns:
            Dict with event counts
        """
        try:
            # This would be implemented with proper database queries
            # For now, return empty stats
            return {
                "login_success": 0,
                "login_failure": 0,
                "password_change": 0,
                "password_reset": 0,
                "mfa_enable": 0,
                "mfa_disable": 0,
                "suspicious_activity": 0
            }
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return {}
    
    def format_audit_log(self, log_entry: Dict[str, Any]) -> str:
        """
        Format an audit log entry for display.
        
        Args:
            log_entry: The audit log entry
            
        Returns:
            Formatted string representation
        """
        try:
            timestamp = log_entry.get("created_at", "")
            action = log_entry.get("action", "")
            user_id = log_entry.get("user_id", "unknown")
            resource_type = log_entry.get("resource_type", "")
            resource_id = log_entry.get("resource_id", "")
            ip_address = log_entry.get("ip_address", "")
            
            return f"[{timestamp}] {action} by {user_id} on {resource_type}:{resource_id} from {ip_address}"
        except Exception as e:
            logger.error(f"Failed to format audit log: {e}")
            return str(log_entry) 