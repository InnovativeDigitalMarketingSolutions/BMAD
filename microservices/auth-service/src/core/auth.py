"""
Authentication service for the Authentication Service.

This module orchestrates all authentication operations including
user registration, login, token management, and authorization.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import logging
import secrets

from .database import DatabaseService
from .jwt import JWTService
from .password import PasswordService
from .mfa import MFAService
from .audit import AuditService

logger = logging.getLogger(__name__)


class AuthService:
    """Main authentication service."""
    
    def __init__(
        self,
        database_service: DatabaseService,
        jwt_service: JWTService,
        password_service: PasswordService,
        mfa_service: MFAService,
        audit_service: AuditService
    ):
        """Initialize the authentication service."""
        self.db = database_service
        self.jwt = jwt_service
        self.password = password_service
        self.mfa = mfa_service
        self.audit = audit_service
    
    async def register_user(
        self,
        email: str,
        password: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            username: Optional username
            first_name: Optional first name
            last_name: Optional last name
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing user information and tokens
        """
        try:
            # Validate password strength
            is_valid, error_message = self.password.validate_password_strength(password)
            if not is_valid:
                return {
                    "success": False,
                    "error": "password_validation_failed",
                    "message": error_message
                }
            
            # Check if user already exists
            existing_user = await self.db.get_user_by_email(email)
            if existing_user:
                return {
                    "success": False,
                    "error": "user_already_exists",
                    "message": "User with this email already exists"
                }
            
            if username:
                existing_username = await self.db.get_user_by_username(username)
                if existing_username:
                    return {
                        "success": False,
                        "error": "username_taken",
                        "message": "Username is already taken"
                    }
            
            # Hash password
            password_hash = self.password.hash_password(password)
            
            # Create user
            user_data = {
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "password_hash": password_hash,
                "status": "active",
                "email_verified": False,
                "mfa_enabled": False
            }
            
            user = await self.db.create_user(user_data)
            
            # Log registration
            await self.audit.log_user_registration(
                user_id=user.id,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Create tokens
            token_pair = self.jwt.create_token_pair(
                user_id=user.id,
                email=user.email
            )
            
            # Create session
            session_data = {
                "user_id": user.id,
                "token_hash": self.jwt.hash_token(token_pair["access_token"]),
                "refresh_token_hash": self.jwt.hash_token(token_pair["refresh_token"]),
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=self.jwt.access_token_expire_minutes),
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            await self.db.create_session(session_data)
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "status": user.status,
                    "email_verified": user.email_verified,
                    "mfa_enabled": user.mfa_enabled
                },
                "tokens": token_pair
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {
                "success": False,
                "error": "registration_failed",
                "message": "Failed to register user"
            }
    
    async def login_user(
        self,
        email: str,
        password: str,
        mfa_token: Optional[str] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            email: User's email address
            password: User's password
            mfa_token: Optional MFA token
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing authentication result
        """
        try:
            # Get user by email
            user = await self.db.get_user_by_email(email)
            if not user:
                await self.audit.log_login_failure(
                    email=email,
                    reason="user_not_found",
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return {
                    "success": False,
                    "error": "invalid_credentials",
                    "message": "Invalid email or password"
                }
            
            # Check user status
            if user.status != "active":
                await self.audit.log_login_failure(
                    email=email,
                    reason="account_inactive",
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return {
                    "success": False,
                    "error": "account_inactive",
                    "message": "Account is not active"
                }
            
            # Verify password
            if not self.password.verify_password(password, user.password_hash):
                await self.audit.log_login_failure(
                    email=email,
                    reason="invalid_password",
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return {
                    "success": False,
                    "error": "invalid_credentials",
                    "message": "Invalid email or password"
                }
            
            # Check MFA if enabled
            if user.mfa_enabled:
                if not mfa_token:
                    return {
                        "success": False,
                        "error": "mfa_required",
                        "message": "MFA token required",
                        "mfa_required": True
                    }
                
                # Verify MFA token
                mfa_result = self.mfa.verify_mfa_token(
                    secret=user.mfa_secret,
                    token=mfa_token
                )
                
                if not mfa_result["valid"]:
                    await self.audit.log_login_failure(
                        email=email,
                        reason="invalid_mfa",
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    return {
                        "success": False,
                        "error": "invalid_mfa",
                        "message": "Invalid MFA token"
                    }
            
            # Update last login
            await self.db.update_user(user.id, {
                "last_login": datetime.now(timezone.utc)
            })
            
            # Get user roles and permissions
            roles = await self.db.get_user_roles(user.id)
            role_names = [role.name for role in roles]
            permissions = []
            for role in roles:
                permissions.extend(role.permissions)
            
            # Create tokens
            token_pair = self.jwt.create_token_pair(
                user_id=user.id,
                email=user.email,
                roles=role_names,
                permissions=permissions
            )
            
            # Create session
            session_data = {
                "user_id": user.id,
                "token_hash": self.jwt.hash_token(token_pair["access_token"]),
                "refresh_token_hash": self.jwt.hash_token(token_pair["refresh_token"]),
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=self.jwt.access_token_expire_minutes),
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            await self.db.create_session(session_data)
            
            # Log successful login
            await self.audit.log_login_success(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "status": user.status,
                    "email_verified": user.email_verified,
                    "mfa_enabled": user.mfa_enabled,
                    "roles": role_names,
                    "permissions": permissions
                },
                "tokens": token_pair
            }
            
        except Exception as e:
            logger.error(f"User login failed: {e}")
            return {
                "success": False,
                "error": "login_failed",
                "message": "Failed to authenticate user"
            }
    
    async def logout_user(
        self,
        user_id: str,
        session_id: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Logout a user.
        
        Args:
            user_id: User ID
            session_id: Session ID to revoke
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing logout result
        """
        try:
            # Revoke session
            success = await self.db.revoke_session(session_id)
            
            if success:
                # Log logout
                await self.audit.log_logout(
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                return {
                    "success": True,
                    "message": "Logged out successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "session_not_found",
                    "message": "Session not found"
                }
                
        except Exception as e:
            logger.error(f"User logout failed: {e}")
            return {
                "success": False,
                "error": "logout_failed",
                "message": "Failed to logout user"
            }
    
    async def refresh_token(
        self,
        refresh_token: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing new access token
        """
        try:
            # Verify refresh token
            payload = self.jwt.verify_refresh_token(refresh_token)
            if not payload:
                return {
                    "success": False,
                    "error": "invalid_refresh_token",
                    "message": "Invalid refresh token"
                }
            
            user_id = payload.get("sub")
            
            # Get user
            user = await self.db.get_user_by_id(user_id)
            if not user or user.status != "active":
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found or inactive"
                }
            
            # Get user roles and permissions
            roles = await self.db.get_user_roles(user.id)
            role_names = [role.name for role in roles]
            permissions = []
            for role in roles:
                permissions.extend(role.permissions)
            
            # Create new access token
            new_access_token = self.jwt.create_access_token({
                "sub": user.id,
                "email": user.email,
                "roles": role_names,
                "permissions": permissions
            })
            
            return {
                "success": True,
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.jwt.access_token_expire_minutes * 60,
                "user_id": user.id,
                "email": user.email
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {
                "success": False,
                "error": "refresh_failed",
                "message": "Failed to refresh token"
            }
    
    async def validate_token(
        self,
        token: str,
        required_permissions: Optional[List[str]] = None,
        required_roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate access token.
        
        Args:
            token: Access token to validate
            required_permissions: Required permissions
            required_roles: Required roles
            
        Returns:
            Dict containing validation result
        """
        try:
            # Verify token
            payload = self.jwt.verify_access_token(token)
            if not payload:
                return {
                    "valid": False,
                    "error": "invalid_token",
                    "message": "Invalid token"
                }
            
            user_id = payload.get("sub")
            
            # Get user
            user = await self.db.get_user_by_id(user_id)
            if not user or user.status != "active":
                return {
                    "valid": False,
                    "error": "user_not_found",
                    "message": "User not found or inactive"
                }
            
            # Check permissions if required
            if required_permissions:
                user_permissions = payload.get("permissions", [])
                if not self.jwt.has_any_permission(token, required_permissions):
                    return {
                        "valid": False,
                        "error": "insufficient_permissions",
                        "message": "Insufficient permissions"
                    }
            
            # Check roles if required
            if required_roles:
                user_roles = payload.get("roles", [])
                if not self.jwt.has_any_role(token, required_roles):
                    return {
                        "valid": False,
                        "error": "insufficient_roles",
                        "message": "Insufficient roles"
                    }
            
            return {
                "valid": True,
                "user_id": user_id,
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {
                "valid": False,
                "error": "validation_failed",
                "message": "Failed to validate token"
            }
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing password change result
        """
        try:
            # Get user
            user = await self.db.get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": "User not found"
                }
            
            # Verify current password
            if not self.password.verify_password(current_password, user.password_hash):
                return {
                    "success": False,
                    "error": "invalid_current_password",
                    "message": "Current password is incorrect"
                }
            
            # Validate new password
            is_valid, error_message = self.password.validate_password_strength(new_password)
            if not is_valid:
                return {
                    "success": False,
                    "error": "password_validation_failed",
                    "message": error_message
                }
            
            # Hash new password
            new_password_hash = self.password.hash_password(new_password)
            
            # Update password
            await self.db.update_user(user_id, {
                "password_hash": new_password_hash
            })
            
            # Revoke all sessions
            await self.db.revoke_user_sessions(user_id)
            
            # Log password change
            await self.audit.log_password_change(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return {
                "success": False,
                "error": "password_change_failed",
                "message": "Failed to change password"
            }
    
    async def request_password_reset(
        self,
        email: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Request password reset.
        
        Args:
            email: User's email address
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing reset request result
        """
        try:
            # Get user
            user = await self.db.get_user_by_email(email)
            if not user:
                # Don't reveal if user exists
                return {
                    "success": True,
                    "message": "If the email exists, a reset link has been sent"
                }
            
            # Generate reset token
            reset_token = self.password.generate_password_reset_token()
            token_hash = self.password.hash_token(reset_token)
            
            # Store reset token
            token_data = {
                "user_id": user.id,
                "token_hash": token_hash,
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)
            }
            
            await self.db.create_password_reset_token(token_data)
            
            # Log reset request
            await self.audit.log_password_reset_request(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "success": True,
                "message": "If the email exists, a reset link has been sent",
                "reset_token": reset_token  # In production, this would be sent via email
            }
            
        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            return {
                "success": False,
                "error": "reset_request_failed",
                "message": "Failed to process reset request"
            }
    
    async def reset_password(
        self,
        reset_token: str,
        new_password: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Reset password using reset token.
        
        Args:
            reset_token: Reset token
            new_password: New password
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing reset result
        """
        try:
            # Hash token for lookup
            token_hash = self.password.hash_token(reset_token)
            
            # Get reset token
            reset_token_record = await self.db.get_password_reset_token(token_hash)
            if not reset_token_record:
                return {
                    "success": False,
                    "error": "invalid_reset_token",
                    "message": "Invalid or expired reset token"
                }
            
            # Validate new password
            is_valid, error_message = self.password.validate_password_strength(new_password)
            if not is_valid:
                return {
                    "success": False,
                    "error": "password_validation_failed",
                    "message": error_message
                }
            
            # Hash new password
            new_password_hash = self.password.hash_password(new_password)
            
            # Update user password
            await self.db.update_user(reset_token_record.user_id, {
                "password_hash": new_password_hash
            })
            
            # Mark token as used
            await self.db.mark_password_reset_token_used(reset_token_record.id)
            
            # Revoke all sessions
            await self.db.revoke_user_sessions(reset_token_record.user_id)
            
            # Log password reset
            await self.audit.log_password_reset_complete(
                user_id=reset_token_record.user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "success": True,
                "message": "Password reset successfully"
            }
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {
                "success": False,
                "error": "reset_failed",
                "message": "Failed to reset password"
            } 