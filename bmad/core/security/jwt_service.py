"""
JWT service for BMAD API authentication.

This module handles JWT token creation, validation, and management for the BMAD API.
Based on the microservices/auth-service implementation and backend development patterns.
"""

import jwt
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import secrets
import hashlib

logger = logging.getLogger(__name__)


class JWTService:
    """JWT service for token management in BMAD API."""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        """Initialize the JWT service."""
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "bmad-dev-secret-key-change-in-production")
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        logger.info("JWT service initialized")
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create an access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.PyJWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode an access token."""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a refresh token."""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired."""
        try:
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.PyJWTError:
            return True
    
    def create_token_pair(
        self,
        user_id: str,
        email: str,
        tenant_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create access and refresh token pair."""
        # Common claims
        claims = {
            "sub": user_id,
            "email": email,
            "tenant_id": tenant_id,
            "roles": roles or [],
            "permissions": permissions or []
        }
        
        # Create tokens
        access_token = self.create_access_token(claims)
        refresh_token = self.create_refresh_token(claims)
        
        # Calculate expiration
        access_expires = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        refresh_expires = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,  # seconds
            "refresh_expires_in": self.refresh_token_expire_days * 24 * 60 * 60,  # seconds
            "user_id": user_id,
            "email": email,
            "tenant_id": tenant_id
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        # Create new access token with same claims
        claims = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "tenant_id": payload.get("tenant_id"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", [])
        }
        
        access_token = self.create_access_token(claims)
        access_expires = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "tenant_id": payload.get("tenant_id")
        }
    
    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from token."""
        payload = self.verify_access_token(token)
        if payload:
            return payload.get("sub")
        return None
    
    def extract_tenant_id_from_token(self, token: str) -> Optional[str]:
        """Extract tenant ID from token."""
        payload = self.verify_access_token(token)
        if payload:
            return payload.get("tenant_id")
        return None
    
    def extract_roles_from_token(self, token: str) -> List[str]:
        """Extract roles from token."""
        payload = self.verify_access_token(token)
        if payload:
            return payload.get("roles", [])
        return []
    
    def extract_permissions_from_token(self, token: str) -> List[str]:
        """Extract permissions from token."""
        payload = self.verify_access_token(token)
        if payload:
            return payload.get("permissions", [])
        return []
    
    def has_permission(self, token: str, permission: str) -> bool:
        """Check if token has specific permission."""
        permissions = self.extract_permissions_from_token(token)
        return permission in permissions or "*" in permissions
    
    def has_role(self, token: str, role: str) -> bool:
        """Check if token has specific role."""
        roles = self.extract_roles_from_token(token)
        return role in roles
    
    def has_any_role(self, token: str, roles: List[str]) -> bool:
        """Check if token has any of the specified roles."""
        token_roles = self.extract_roles_from_token(token)
        return any(role in token_roles for role in roles)
    
    def has_all_roles(self, token: str, roles: List[str]) -> bool:
        """Check if token has all of the specified roles."""
        token_roles = self.extract_roles_from_token(token)
        return all(role in token_roles for role in roles)
    
    def has_any_permission(self, token: str, permissions: List[str]) -> bool:
        """Check if token has any of the specified permissions."""
        token_permissions = self.extract_permissions_from_token(token)
        return any(perm in token_permissions for perm in permissions) or "*" in token_permissions
    
    def has_all_permissions(self, token: str, permissions: List[str]) -> bool:
        """Check if token has all of the specified permissions."""
        token_permissions = self.extract_permissions_from_token(token)
        return all(perm in token_permissions for perm in permissions) or "*" in token_permissions


# Global JWT service instance
jwt_service = JWTService() 