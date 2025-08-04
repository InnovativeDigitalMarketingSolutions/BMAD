"""
Unit tests for JWT service implementation.

Tests JWT token creation, validation, and management functionality.
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from bmad.core.security.jwt_service import JWTService


class TestJWTService:
    """Test cases for JWT service functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.jwt_service = JWTService(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7
        )
        self.test_user_data = {
            "sub": "test_user_123",
            "email": "test@example.com",
            "tenant_id": "test_tenant_456",
            "roles": ["user", "admin"],
            "permissions": ["read", "write", "execute"]
        }
    
    def test_jwt_service_initialization(self):
        """Test JWT service initialization."""
        assert self.jwt_service.secret_key == "test-secret-key"
        assert self.jwt_service.algorithm == "HS256"
        assert self.jwt_service.access_token_expire_minutes == 30
        assert self.jwt_service.refresh_token_expire_days == 7
    
    def test_jwt_service_initialization_with_env_var(self):
        """Test JWT service initialization with environment variable."""
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "env-secret-key"}):
            jwt_service = JWTService()
            assert jwt_service.secret_key == "env-secret-key"
    
    def test_create_access_token(self):
        """Test access token creation."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        payload = jwt.decode(token, self.jwt_service.secret_key, algorithms=[self.jwt_service.algorithm])
        assert payload["sub"] == self.test_user_data["sub"]
        assert payload["email"] == self.test_user_data["email"]
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token = self.jwt_service.create_refresh_token(self.test_user_data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify token
        payload = jwt.decode(token, self.jwt_service.secret_key, algorithms=[self.jwt_service.algorithm])
        assert payload["sub"] == self.test_user_data["sub"]
        assert payload["email"] == self.test_user_data["email"]
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        payload = self.jwt_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == self.test_user_data["sub"]
        assert payload["email"] == self.test_user_data["email"]
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        payload = self.jwt_service.verify_token("invalid.token.here")
        assert payload is None
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        # Create token with very short expiration
        with patch.object(self.jwt_service, 'access_token_expire_minutes', -1):
            token = self.jwt_service.create_access_token(self.test_user_data)
        
        payload = self.jwt_service.verify_token(token)
        assert payload is None
    
    def test_verify_access_token(self):
        """Test access token verification."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        payload = self.jwt_service.verify_access_token(token)
        
        assert payload is not None
        assert payload["type"] == "access"
    
    def test_verify_access_token_with_refresh_token(self):
        """Test access token verification with refresh token (should fail)."""
        token = self.jwt_service.create_refresh_token(self.test_user_data)
        payload = self.jwt_service.verify_access_token(token)
        
        assert payload is None
    
    def test_verify_refresh_token(self):
        """Test refresh token verification."""
        token = self.jwt_service.create_refresh_token(self.test_user_data)
        payload = self.jwt_service.verify_refresh_token(token)
        
        assert payload is not None
        assert payload["type"] == "refresh"
    
    def test_verify_refresh_token_with_access_token(self):
        """Test refresh token verification with access token (should fail)."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        payload = self.jwt_service.verify_refresh_token(token)
        
        assert payload is None
    
    def test_is_token_expired_valid(self):
        """Test token expiration check with valid token."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        is_expired = self.jwt_service.is_token_expired(token)
        
        assert is_expired is False
    
    def test_is_token_expired_invalid(self):
        """Test token expiration check with invalid token."""
        is_expired = self.jwt_service.is_token_expired("invalid.token.here")
        assert is_expired is True
    
    def test_create_token_pair(self):
        """Test token pair creation."""
        token_data = self.jwt_service.create_token_pair(
            user_id=self.test_user_data["sub"],
            email=self.test_user_data["email"],
            tenant_id=self.test_user_data["tenant_id"],
            roles=self.test_user_data["roles"],
            permissions=self.test_user_data["permissions"]
        )
        
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "token_type" in token_data
        assert "expires_in" in token_data
        assert "refresh_expires_in" in token_data
        assert "user_id" in token_data
        assert "email" in token_data
        assert "tenant_id" in token_data
        
        assert token_data["token_type"] == "bearer"
        assert token_data["user_id"] == self.test_user_data["sub"]
        assert token_data["email"] == self.test_user_data["email"]
        assert token_data["tenant_id"] == self.test_user_data["tenant_id"]
    
    def test_refresh_access_token(self):
        """Test access token refresh."""
        # Create token pair
        token_data = self.jwt_service.create_token_pair(
            user_id=self.test_user_data["sub"],
            email=self.test_user_data["email"],
            tenant_id=self.test_user_data["tenant_id"],
            roles=self.test_user_data["roles"],
            permissions=self.test_user_data["permissions"]
        )
        
        # Refresh access token
        refresh_data = self.jwt_service.refresh_access_token(token_data["refresh_token"])
        
        assert refresh_data is not None
        assert "access_token" in refresh_data
        assert "token_type" in refresh_data
        assert "expires_in" in refresh_data
        assert "user_id" in refresh_data
        assert "email" in refresh_data
        assert "tenant_id" in refresh_data
        
        assert refresh_data["token_type"] == "bearer"
        assert refresh_data["user_id"] == self.test_user_data["sub"]
        assert refresh_data["email"] == self.test_user_data["email"]
        assert refresh_data["tenant_id"] == self.test_user_data["tenant_id"]
    
    def test_refresh_access_token_invalid(self):
        """Test access token refresh with invalid refresh token."""
        refresh_data = self.jwt_service.refresh_access_token("invalid.refresh.token")
        assert refresh_data is None
    
    def test_extract_user_id_from_token(self):
        """Test user ID extraction from token."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        user_id = self.jwt_service.extract_user_id_from_token(token)
        
        assert user_id == self.test_user_data["sub"]
    
    def test_extract_tenant_id_from_token(self):
        """Test tenant ID extraction from token."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        tenant_id = self.jwt_service.extract_tenant_id_from_token(token)
        
        assert tenant_id == self.test_user_data["tenant_id"]
    
    def test_extract_roles_from_token(self):
        """Test roles extraction from token."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        roles = self.jwt_service.extract_roles_from_token(token)
        
        assert roles == self.test_user_data["roles"]
    
    def test_extract_permissions_from_token(self):
        """Test permissions extraction from token."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        permissions = self.jwt_service.extract_permissions_from_token(token)
        
        assert permissions == self.test_user_data["permissions"]
    
    def test_has_permission_true(self):
        """Test permission check with valid permission."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_permission = self.jwt_service.has_permission(token, "read")
        
        assert has_permission is True
    
    def test_has_permission_false(self):
        """Test permission check with invalid permission."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_permission = self.jwt_service.has_permission(token, "invalid_permission")
        
        assert has_permission is False
    
    def test_has_permission_wildcard(self):
        """Test permission check with wildcard permission."""
        test_data = self.test_user_data.copy()
        test_data["permissions"] = ["*"]
        token = self.jwt_service.create_access_token(test_data)
        has_permission = self.jwt_service.has_permission(token, "any_permission")
        
        assert has_permission is True
    
    def test_has_role_true(self):
        """Test role check with valid role."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_role = self.jwt_service.has_role(token, "admin")
        
        assert has_role is True
    
    def test_has_role_false(self):
        """Test role check with invalid role."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_role = self.jwt_service.has_role(token, "invalid_role")
        
        assert has_role is False
    
    def test_has_any_role_true(self):
        """Test any role check with valid roles."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_any_role = self.jwt_service.has_any_role(token, ["admin", "user"])
        
        assert has_any_role is True
    
    def test_has_any_role_false(self):
        """Test any role check with invalid roles."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_any_role = self.jwt_service.has_any_role(token, ["invalid_role1", "invalid_role2"])
        
        assert has_any_role is False
    
    def test_has_all_roles_true(self):
        """Test all roles check with valid roles."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_all_roles = self.jwt_service.has_all_roles(token, ["user", "admin"])
        
        assert has_all_roles is True
    
    def test_has_all_roles_false(self):
        """Test all roles check with invalid roles."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_all_roles = self.jwt_service.has_all_roles(token, ["user", "admin", "invalid_role"])
        
        assert has_all_roles is False
    
    def test_has_any_permission_true(self):
        """Test any permission check with valid permissions."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_any_permission = self.jwt_service.has_any_permission(token, ["read", "write"])
        
        assert has_any_permission is True
    
    def test_has_any_permission_false(self):
        """Test any permission check with invalid permissions."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_any_permission = self.jwt_service.has_any_permission(token, ["invalid_perm1", "invalid_perm2"])
        
        assert has_any_permission is False
    
    def test_has_all_permissions_true(self):
        """Test all permissions check with valid permissions."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_all_permissions = self.jwt_service.has_all_permissions(token, ["read", "write"])
        
        assert has_all_permissions is True
    
    def test_has_all_permissions_false(self):
        """Test all permissions check with invalid permissions."""
        token = self.jwt_service.create_access_token(self.test_user_data)
        has_all_permissions = self.jwt_service.has_all_permissions(token, ["read", "write", "invalid_perm"])
        
        assert has_all_permissions is False
    
    def test_error_handling_invalid_token(self):
        """Test error handling with invalid token."""
        # Test all extraction methods with invalid token
        invalid_token = "invalid.token.here"
        
        assert self.jwt_service.extract_user_id_from_token(invalid_token) is None
        assert self.jwt_service.extract_tenant_id_from_token(invalid_token) is None
        assert self.jwt_service.extract_roles_from_token(invalid_token) == []
        assert self.jwt_service.extract_permissions_from_token(invalid_token) == []
        assert self.jwt_service.has_permission(invalid_token, "read") is False
        assert self.jwt_service.has_role(invalid_token, "admin") is False
    
    def test_custom_expiration(self):
        """Test token creation with custom expiration."""
        custom_expiry = timedelta(hours=2)
        token = self.jwt_service.create_access_token(self.test_user_data, expires_delta=custom_expiry)
        
        payload = jwt.decode(token, self.jwt_service.secret_key, algorithms=[self.jwt_service.algorithm])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        
        # Check that expiration is approximately 2 hours from issued time
        time_diff = exp_time - iat_time
        assert abs(time_diff.total_seconds() - 7200) < 10  # Allow 10 seconds tolerance


class TestJWTServiceIntegration:
    """Integration tests for JWT service with real scenarios."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.jwt_service = JWTService(
            secret_key="integration-test-secret",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7
        )
    
    def test_complete_authentication_flow(self):
        """Test complete authentication flow."""
        # 1. Create token pair
        token_data = self.jwt_service.create_token_pair(
            user_id="user123",
            email="user@example.com",
            tenant_id="tenant456",
            roles=["user"],
            permissions=["read", "write"]
        )
        
        # 2. Verify access token
        access_payload = self.jwt_service.verify_access_token(token_data["access_token"])
        assert access_payload is not None
        assert access_payload["sub"] == "user123"
        assert access_payload["email"] == "user@example.com"
        assert access_payload["tenant_id"] == "tenant456"
        assert access_payload["roles"] == ["user"]
        assert access_payload["permissions"] == ["read", "write"]
        
        # 3. Verify refresh token
        refresh_payload = self.jwt_service.verify_refresh_token(token_data["refresh_token"])
        assert refresh_payload is not None
        assert refresh_payload["sub"] == "user123"
        
        # 4. Refresh access token
        new_token_data = self.jwt_service.refresh_access_token(token_data["refresh_token"])
        assert new_token_data is not None
        # Note: Tokens might be identical if created at the same time, which is acceptable
        # The important thing is that the refresh process works
        
        # 5. Verify new access token
        new_payload = self.jwt_service.verify_access_token(new_token_data["access_token"])
        assert new_payload is not None
        assert new_payload["sub"] == "user123"
    
    def test_permission_based_access_control(self):
        """Test permission-based access control."""
        # Create token with specific permissions
        token = self.jwt_service.create_access_token({
            "sub": "user123",
            "email": "user@example.com",
            "roles": ["editor"],
            "permissions": ["read", "write", "edit"]
        })
        
        # Test permission checks
        assert self.jwt_service.has_permission(token, "read") is True
        assert self.jwt_service.has_permission(token, "write") is True
        assert self.jwt_service.has_permission(token, "edit") is True
        assert self.jwt_service.has_permission(token, "delete") is False
        assert self.jwt_service.has_permission(token, "admin") is False
        
        # Test role checks
        assert self.jwt_service.has_role(token, "editor") is True
        assert self.jwt_service.has_role(token, "admin") is False
        
        # Test multiple permission checks
        assert self.jwt_service.has_any_permission(token, ["read", "delete"]) is True
        assert self.jwt_service.has_all_permissions(token, ["read", "write"]) is True
        assert self.jwt_service.has_all_permissions(token, ["read", "write", "delete"]) is False
    
    def test_tenant_isolation(self):
        """Test tenant isolation in tokens."""
        # Create tokens for different tenants
        tenant1_token = self.jwt_service.create_access_token({
            "sub": "user123",
            "email": "user@example.com",
            "tenant_id": "tenant1",
            "roles": ["user"],
            "permissions": ["read"]
        })
        
        tenant2_token = self.jwt_service.create_access_token({
            "sub": "user123",
            "email": "user@example.com",
            "tenant_id": "tenant2",
            "roles": ["user"],
            "permissions": ["read"]
        })
        
        # Verify tenant isolation
        assert self.jwt_service.extract_tenant_id_from_token(tenant1_token) == "tenant1"
        assert self.jwt_service.extract_tenant_id_from_token(tenant2_token) == "tenant2"
        assert self.jwt_service.extract_tenant_id_from_token(tenant1_token) != "tenant2" 