"""
Unit tests for the Authentication Service.

This module contains comprehensive unit tests for all authentication
service components including user management, JWT handling, and security features.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from src.core.database import DatabaseService
from src.core.jwt import JWTService
from src.core.password import PasswordService
from src.core.mfa import MFAService
from src.core.audit import AuditService
from src.core.auth import AuthService
from src.models.schemas import UserRegister, UserLogin, TokenRefresh


class TestPasswordService:
    """Test password service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.password_service = PasswordService(bcrypt_rounds=4)  # Use lower rounds for testing
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = self.password_service.hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50
    
    def test_verify_password(self):
        """Test password verification."""
        password = "TestPassword123!"
        hashed = self.password_service.hash_password(password)
        
        assert self.password_service.verify_password(password, hashed) is True
        assert self.password_service.verify_password("wrongpassword", hashed) is False
    
    def test_validate_password_strength(self):
        """Test password strength validation."""
        # Valid password
        valid_password = "TestPassword123!"
        is_valid, error = self.password_service.validate_password_strength(valid_password)
        assert is_valid is True
        assert error == ""
        
        # Too short
        short_password = "Test1!"
        is_valid, error = self.password_service.validate_password_strength(short_password)
        assert is_valid is False
        assert "8 characters" in error
        
        # No uppercase
        no_upper = "testpassword123!"
        is_valid, error = self.password_service.validate_password_strength(no_upper)
        assert is_valid is False
        assert "uppercase" in error
        
        # No lowercase
        no_lower = "TESTPASSWORD123!"
        is_valid, error = self.password_service.validate_password_strength(no_lower)
        assert is_valid is False
        assert "lowercase" in error
        
        # No digit
        no_digit = "TestPassword!"
        is_valid, error = self.password_service.validate_password_strength(no_digit)
        assert is_valid is False
        assert "digit" in error
    
    def test_generate_secure_password(self):
        """Test secure password generation."""
        password = self.password_service.generate_secure_password(length=16)
        
        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    def test_hash_token(self):
        """Test token hashing."""
        token = "test_token_123"
        hashed = self.password_service.hash_token(token)
        
        assert hashed != token
        assert len(hashed) == 64  # SHA256 hash length
        assert hashed.isalnum()


class TestJWTService:
    """Test JWT service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.jwt_service = JWTService(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7
        )
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"user_id": "123", "email": "test@example.com"}
        token = self.jwt_service.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 100
        
        # Verify token
        payload = self.jwt_service.verify_access_token(token)
        assert payload is not None
        assert payload["user_id"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"user_id": "123", "email": "test@example.com"}
        token = self.jwt_service.create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 100
        
        # Verify token
        payload = self.jwt_service.verify_refresh_token(token)
        assert payload is not None
        assert payload["user_id"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "refresh"
    
    def test_verify_token(self):
        """Test token verification."""
        data = {"user_id": "123", "email": "test@example.com"}
        token = self.jwt_service.create_access_token(data)
        
        # Valid token
        payload = self.jwt_service.verify_token(token)
        assert payload is not None
        
        # Invalid token
        invalid_payload = self.jwt_service.verify_token("invalid_token")
        assert invalid_payload is None
    
    def test_create_token_pair(self):
        """Test token pair creation."""
        result = self.jwt_service.create_token_pair(
            user_id="123",
            email="test@example.com",
            roles=["user"],
            permissions=["read:own"]
        )
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert "expires_in" in result
        assert "user_id" in result
        assert "email" in result
        
        # Verify tokens
        access_payload = self.jwt_service.verify_access_token(result["access_token"])
        refresh_payload = self.jwt_service.verify_refresh_token(result["refresh_token"])
        
        assert access_payload is not None
        assert refresh_payload is not None
        assert access_payload["sub"] == "123"
        assert refresh_payload["sub"] == "123"
    
    def test_refresh_access_token(self):
        """Test access token refresh."""
        # Create token pair
        token_pair = self.jwt_service.create_token_pair(
            user_id="123",
            email="test@example.com"
        )
        
        # Refresh access token
        result = self.jwt_service.refresh_access_token(token_pair["refresh_token"])
        
        assert result is not None
        assert "access_token" in result
        assert "token_type" in result
        assert "expires_in" in result
        
        # Verify new access token
        payload = self.jwt_service.verify_access_token(result["access_token"])
        assert payload is not None
        assert payload["sub"] == "123"
    
    def test_extract_user_id_from_token(self):
        """Test user ID extraction from token."""
        token_pair = self.jwt_service.create_token_pair(
            user_id="123",
            email="test@example.com"
        )
        
        user_id = self.jwt_service.extract_user_id_from_token(token_pair["access_token"])
        assert user_id == "123"
    
    def test_permission_checking(self):
        """Test permission checking functionality."""
        token_pair = self.jwt_service.create_token_pair(
            user_id="123",
            email="test@example.com",
            permissions=["read:own", "write:own"]
        )
        
        # Check specific permission
        assert self.jwt_service.has_permission(token_pair["access_token"], "read:own") is True
        assert self.jwt_service.has_permission(token_pair["access_token"], "admin:all") is False
        
        # Check any permission
        assert self.jwt_service.has_any_permission(
            token_pair["access_token"], 
            ["read:own", "admin:all"]
        ) is True
        
        # Check all permissions
        assert self.jwt_service.has_all_permissions(
            token_pair["access_token"], 
            ["read:own", "write:own"]
        ) is True
    
    def test_role_checking(self):
        """Test role checking functionality."""
        token_pair = self.jwt_service.create_token_pair(
            user_id="123",
            email="test@example.com",
            roles=["user", "editor"]
        )
        
        # Check specific role
        assert self.jwt_service.has_role(token_pair["access_token"], "user") is True
        assert self.jwt_service.has_role(token_pair["access_token"], "admin") is False
        
        # Check any role
        assert self.jwt_service.has_any_role(
            token_pair["access_token"], 
            ["user", "admin"]
        ) is True
        
        # Check all roles
        assert self.jwt_service.has_all_roles(
            token_pair["access_token"], 
            ["user", "editor"]
        ) is True


class TestMFAService:
    """Test MFA service functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mfa_service = MFAService(issuer_name="TestApp")
    
    def test_generate_secret(self):
        """Test TOTP secret generation."""
        secret = self.mfa_service.generate_secret()
        
        assert isinstance(secret, str)
        assert len(secret) >= 16
        assert self.mfa_service.validate_secret(secret) is True
    
    def test_generate_backup_codes(self):
        """Test backup code generation."""
        codes = self.mfa_service.generate_backup_codes(count=5)
        
        assert len(codes) == 5
        for code in codes:
            assert len(code) == 8
            assert code.isalnum()
    
    def test_verify_totp(self):
        """Test TOTP verification."""
        secret = self.mfa_service.generate_secret()
        
        # Get current TOTP
        current_totp = self.mfa_service.get_current_totp(secret)
        
        # Verify current TOTP
        assert self.mfa_service.verify_totp(secret, current_totp) is True
        
        # Verify invalid TOTP
        assert self.mfa_service.verify_totp(secret, "000000") is False
    
    def test_verify_backup_code(self):
        """Test backup code verification."""
        codes = self.mfa_service.generate_backup_codes(count=3)
        hashed_codes = [self.mfa_service.hash_backup_code(code) for code in codes]
        
        # Verify valid backup code
        matched_code = self.mfa_service.verify_backup_code(codes[0], hashed_codes)
        assert matched_code == hashed_codes[0]
        
        # Verify invalid backup code
        invalid_result = self.mfa_service.verify_backup_code("INVALID", hashed_codes)
        assert invalid_result is None
    
    def test_setup_mfa(self):
        """Test MFA setup."""
        result = self.mfa_service.setup_mfa("test@example.com")
        
        assert "secret" in result
        assert "qr_code" in result
        assert "backup_codes" in result
        assert len(result["backup_codes"]) == 10
        
        # Verify secret is valid
        assert self.mfa_service.validate_secret(result["secret"]) is True
        
        # Verify QR code is generated
        assert result["qr_code"].startswith("data:image/png;base64,")
    
    def test_verify_mfa_token(self):
        """Test MFA token verification."""
        secret = self.mfa_service.generate_secret()
        backup_codes = self.mfa_service.generate_backup_codes()
        hashed_backup_codes = [self.mfa_service.hash_backup_code(code) for code in backup_codes]
        
        # Test TOTP verification
        current_totp = self.mfa_service.get_current_totp(secret)
        result = self.mfa_service.verify_mfa_token(secret, current_totp, hashed_backup_codes)
        
        assert result["valid"] is True
        assert result["type"] == "totp"
        
        # Test backup code verification
        result = self.mfa_service.verify_mfa_token(secret, backup_codes[0], hashed_backup_codes)
        
        assert result["valid"] is True
        assert result["type"] == "backup"
        
        # Test invalid token
        result = self.mfa_service.verify_mfa_token(secret, "000000", hashed_backup_codes)
        
        assert result["valid"] is False
        assert result["type"] == "invalid"


class TestAuthService:
    """Test main authentication service."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        self.mock_db = Mock(spec=DatabaseService)
        self.mock_jwt = Mock(spec=JWTService)
        self.mock_password = Mock(spec=PasswordService)
        self.mock_mfa = Mock(spec=MFAService)
        self.mock_audit = Mock(spec=AuditService)
        
        # Configure mocks
        self.mock_password.validate_password_strength.return_value = (True, "")
        self.mock_password.hash_password.return_value = "hashed_password"
        
        # Configure JWT service mock with required attributes
        self.mock_jwt.access_token_expire_minutes = 30
        self.mock_jwt.refresh_token_expire_days = 7
        
        return {
            "db": self.mock_db,
            "jwt": self.mock_jwt,
            "password": self.mock_password,
            "mfa": self.mock_mfa,
            "audit": self.mock_audit
        }
    
    @pytest.fixture
    def auth_service(self, mock_services):
        """Create auth service with mock dependencies."""
        return AuthService(
            database_service=mock_services["db"],
            jwt_service=mock_services["jwt"],
            password_service=mock_services["password"],
            mfa_service=mock_services["mfa"],
            audit_service=mock_services["audit"]
        )
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service):
        """Test successful user registration."""
        # Mock database responses
        self.mock_db.get_user_by_email.return_value = None
        self.mock_db.get_user_by_username.return_value = None
        
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        self.mock_db.create_user.return_value = mock_user
        
        # Mock JWT token creation
        self.mock_jwt.create_token_pair.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
            "expires_in": 1800,
            "user_id": "user123",
            "email": "test@example.com"
        }
        
        # Mock session creation
        self.mock_db.create_session.return_value = Mock()
        
        # Test registration
        result = await auth_service.register_user(
            email="test@example.com",
            password="TestPassword123!",
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        
        assert result["success"] is True
        assert "user" in result
        assert "tokens" in result
        assert result["user"]["id"] == "user123"
        assert result["user"]["email"] == "test@example.com"
        
        # Verify mocks were called
        self.mock_password.validate_password_strength.assert_called_once()
        self.mock_password.hash_password.assert_called_once()
        self.mock_db.create_user.assert_called_once()
        self.mock_jwt.create_token_pair.assert_called_once()
        self.mock_db.create_session.assert_called_once()
        self.mock_audit.log_user_registration.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_password_validation_failure(self, auth_service):
        """Test user registration with invalid password."""
        # Mock password validation failure
        self.mock_password.validate_password_strength.return_value = (False, "Password too weak")
        
        result = await auth_service.register_user(
            email="test@example.com",
            password="weak",
            username="testuser"
        )
        
        assert result["success"] is False
        assert result["error"] == "password_validation_failed"
        assert "Password too weak" in result["message"]
    
    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, auth_service):
        """Test user registration with existing email."""
        # Mock existing user
        self.mock_db.get_user_by_email.return_value = Mock()
        
        result = await auth_service.register_user(
            email="existing@example.com",
            password="TestPassword123!"
        )
        
        assert result["success"] is False
        assert result["error"] == "user_already_exists"
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, auth_service):
        """Test successful user login."""
        # Mock user
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.status = "active"
        mock_user.password_hash = "hashed_password"
        mock_user.mfa_enabled = False
        self.mock_db.get_user_by_email.return_value = mock_user
        
        # Mock password verification
        self.mock_password.verify_password.return_value = True
        
        # Mock user update
        self.mock_db.update_user.return_value = mock_user
        
        # Mock roles
        self.mock_db.get_user_roles.return_value = []
        
        # Mock JWT token creation
        self.mock_jwt.create_token_pair.return_value = {
            "access_token": "access_token_123",
            "refresh_token": "refresh_token_123",
            "token_type": "bearer",
            "expires_in": 1800,
            "user_id": "user123",
            "email": "test@example.com"
        }
        
        # Mock session creation
        self.mock_db.create_session.return_value = Mock()
        
        # Test login
        result = await auth_service.login_user(
            email="test@example.com",
            password="TestPassword123!"
        )
        
        assert result["success"] is True
        assert "user" in result
        assert "tokens" in result
        assert result["user"]["id"] == "user123"
        
        # Verify mocks were called
        self.mock_password.verify_password.assert_called_once()
        self.mock_db.update_user.assert_called_once()
        self.mock_jwt.create_token_pair.assert_called_once()
        self.mock_db.create_session.assert_called_once()
        self.mock_audit.log_login_success.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, auth_service):
        """Test user login with invalid credentials."""
        # Mock user not found
        self.mock_db.get_user_by_email.return_value = None
        
        result = await auth_service.login_user(
            email="nonexistent@example.com",
            password="TestPassword123!"
        )
        
        assert result["success"] is False
        assert result["error"] == "invalid_credentials"
        self.mock_audit.log_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user_inactive_account(self, auth_service):
        """Test user login with inactive account."""
        # Mock inactive user
        mock_user = Mock()
        mock_user.status = "inactive"
        self.mock_db.get_user_by_email.return_value = mock_user
        
        result = await auth_service.login_user(
            email="inactive@example.com",
            password="TestPassword123!"
        )
        
        assert result["success"] is False
        assert result["error"] == "account_inactive"
        self.mock_audit.log_login_failure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_token_success(self, auth_service):
        """Test successful token validation."""
        # Mock JWT verification
        self.mock_jwt.verify_access_token.return_value = {
            "sub": "user123",
            "email": "test@example.com",
            "roles": ["user"],
            "permissions": ["read:own"]
        }
        
        # Mock user
        mock_user = Mock()
        mock_user.status = "active"
        self.mock_db.get_user_by_id.return_value = mock_user
        
        result = await auth_service.validate_token("valid_token")
        
        assert result["valid"] is True
        assert result["user_id"] == "user123"
        assert result["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_validate_token_invalid(self, auth_service):
        """Test invalid token validation."""
        # Mock JWT verification failure
        self.mock_jwt.verify_access_token.return_value = None
        
        result = await auth_service.validate_token("invalid_token")
        
        assert result["valid"] is False
        assert result["error"] == "invalid_token"
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service):
        """Test successful password change."""
        # Mock user
        mock_user = Mock()
        mock_user.id = "user123"
        self.mock_db.get_user_by_id.return_value = mock_user
        
        # Mock password verification
        self.mock_password.verify_password.return_value = True
        
        # Mock password validation
        self.mock_password.validate_password_strength.return_value = (True, "")
        
        # Mock password hashing
        self.mock_password.hash_password.return_value = "new_hashed_password"
        
        # Mock user update
        self.mock_db.update_user.return_value = mock_user
        
        # Mock session revocation
        self.mock_db.revoke_user_sessions.return_value = 5
        
        result = await auth_service.change_password(
            user_id="user123",
            current_password="OldPassword123!",
            new_password="NewPassword123!"
        )
        
        assert result["success"] is True
        assert "changed successfully" in result["message"]
        
        # Verify mocks were called
        self.mock_password.verify_password.assert_called_once()
        self.mock_password.validate_password_strength.assert_called_once()
        self.mock_password.hash_password.assert_called_once()
        self.mock_db.update_user.assert_called_once()
        self.mock_db.revoke_user_sessions.assert_called_once()
        self.mock_audit.log_password_change.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 