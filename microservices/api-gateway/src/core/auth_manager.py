"""
Authentication Manager for API Gateway JWT validation and user authentication.
"""

import logging
import time
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from enum import Enum

from jose import JWTError, jwt
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    """Token types."""
    ACCESS = "access"
    REFRESH = "refresh"


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    token_type: TokenType = Field(TokenType.ACCESS, description="Token type")


class AuthConfig(BaseModel):
    """Authentication configuration."""
    secret_key: str = Field(..., description="JWT secret key")
    algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(30, description="Access token expiration")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration")
    issuer: str = Field("bmad-gateway", description="Token issuer")


class AuthManager:
    """Manages JWT authentication and authorization."""
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.blacklisted_tokens: set = set()
        self._initialized = False
        
    async def initialize(self):
        """Initialize the authentication manager."""
        try:
            # Validate configuration
            if not self.config.secret_key:
                raise ValueError("Secret key is required")
            
            self._initialized = True
            logger.info("Authentication manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize auth manager: {e}")
            raise
    
    def create_access_token(self, user_id: str, email: str, roles: List[str], permissions: List[str]) -> str:
        """Create a new access token."""
        if not self._initialized:
            raise RuntimeError("Auth manager not initialized")
        
        try:
            payload = {
                "sub": user_id,
                "email": email,
                "roles": roles,
                "permissions": permissions,
                "exp": datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes),
                "iat": datetime.utcnow(),
                "token_type": TokenType.ACCESS.value
            }
            
            token = jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
            logger.info(f"Created access token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a new refresh token."""
        if not self._initialized:
            raise RuntimeError("Auth manager not initialized")
        
        try:
            payload = {
                "sub": user_id,
                "exp": datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days),
                "iat": datetime.utcnow(),
                "token_type": TokenType.REFRESH.value
            }
            
            token = jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
            logger.info(f"Created refresh token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise
    
    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """Validate and decode a JWT token."""
        if not self._initialized:
            raise RuntimeError("Auth manager not initialized")
        
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                logger.warning("Token is blacklisted")
                return None
            
            # Decode token
            payload = jwt.decode(
                token, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer
            )
            
            # Validate token type
            token_type = payload.get("token_type")
            if not token_type or token_type not in [t.value for t in TokenType]:
                logger.warning("Invalid token type")
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if not exp or datetime.utcnow().timestamp() > exp:
                logger.warning("Token expired")
                return None
            
            # Create token payload object
            token_payload = TokenPayload(
                sub=payload["sub"],
                email=payload.get("email", ""),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                exp=exp,
                iat=payload.get("iat", 0),
                token_type=TokenType(token_type)
            )
            
            logger.debug(f"Token validated for user {token_payload.sub}")
            return token_payload
            
        except JWTError as e:
            logger.warning(f"JWT validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """Extract token from Authorization header."""
        if not authorization_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            parts = authorization_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return None
            
            return parts[1]
            
        except Exception as e:
            logger.error(f"Error extracting token from header: {e}")
            return None
    
    def has_permission(self, token_payload: TokenPayload, required_permission: str) -> bool:
        """Check if user has required permission."""
        if not token_payload:
            return False
        
        # Admin role has all permissions
        if UserRole.ADMIN.value in token_payload.roles:
            return True
        
        # Check specific permission
        return required_permission in token_payload.permissions
    
    def has_role(self, token_payload: TokenPayload, required_role: str) -> bool:
        """Check if user has required role."""
        if not token_payload:
            return False
        
        return required_role in token_payload.roles
    
    def blacklist_token(self, token: str):
        """Add token to blacklist."""
        self.blacklisted_tokens.add(token)
        logger.info("Token added to blacklist")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self.blacklisted_tokens
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token information without validation."""
        try:
            # Decode without verification to get payload
            payload = jwt.decode(
                token, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm],
                options={"verify_signature": False}
            )
            
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "token_type": payload.get("token_type"),
                "expires_at": datetime.fromtimestamp(payload.get("exp", 0)).isoformat() if payload.get("exp") else None,
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0)).isoformat() if payload.get("iat") else None
            }
            
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        try:
            # Validate refresh token
            payload = self.validate_token(refresh_token)
            if not payload or payload.token_type != TokenType.REFRESH:
                return None
            
            # Create new access token
            # Note: We need to get user details from the refresh token or user service
            # For now, we'll create a minimal access token
            new_access_token = self.create_access_token(
                user_id=payload.sub,
                email="",  # Would need to get from user service
                roles=[],  # Would need to get from user service
                permissions=[]  # Would need to get from user service
            )
            
            logger.info(f"Refreshed access token for user {payload.sub}")
            return new_access_token
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return None
    
    def get_blacklist_size(self) -> int:
        """Get number of blacklisted tokens."""
        return len(self.blacklisted_tokens)
    
    def cleanup_expired_blacklist(self):
        """Clean up expired tokens from blacklist."""
        # This is a simple implementation
        # In production, you might want to store blacklisted tokens with expiration times
        # and clean them up periodically
        logger.info(f"Blacklist cleanup: {len(self.blacklisted_tokens)} tokens")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the auth manager."""
        try:
            return {
                "status": "healthy",
                "blacklisted_tokens": len(self.blacklisted_tokens),
                "algorithm": self.config.algorithm,
                "access_token_expire_minutes": self.config.access_token_expire_minutes,
                "refresh_token_expire_days": self.config.refresh_token_expire_days
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 