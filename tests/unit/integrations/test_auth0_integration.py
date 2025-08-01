"""
Unit Tests for Auth0 Integration

Tests the Auth0 client functionality including:
- User management
- Role management
- Permission management
- Token validation
- API interactions
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, UTC
import json

# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from integrations.auth0 import Auth0Client, Auth0Config, Auth0User, Auth0Role


class TestAuth0Config(unittest.TestCase):
    """Test Auth0 configuration."""
    
    def test_auth0_config_creation(self):
        """Test Auth0Config creation."""
        config = Auth0Config(
            domain="test.auth0.com",
            client_id="test_client_id",
            client_secret="test_client_secret",
            audience="https://api.test.com"
        )
        
        self.assertEqual(config.domain, "test.auth0.com")
        self.assertEqual(config.client_id, "test_client_id")
        self.assertEqual(config.client_secret, "test_client_secret")
        self.assertEqual(config.audience, "https://api.test.com")
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_delay, 1.0)


class TestAuth0Client(unittest.TestCase):
    """Test Auth0 client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = Auth0Config(
            domain="test.auth0.com",
            client_id="test_client_id",
            client_secret="test_client_secret",
            audience="https://api.test.com"
        )
        
        # Mock requests for all tests
        self.requests_patcher = patch('integrations.auth0.auth0_client.requests')
        self.mock_requests = self.requests_patcher.start()
    
    def tearDown(self):
        """Clean up test environment."""
        self.requests_patcher.stop()
    
    def test_auth0_client_initialization(self):
        """Test Auth0Client initialization."""
        client = Auth0Client(self.config)
        
        self.assertEqual(client.config, self.config)
        self.assertEqual(client.base_url, "https://test.auth0.com")
        self.assertEqual(client.api_url, "https://test.auth0.com/api/v2")
        self.assertEqual(client.token_cache, {})
    
    @patch('integrations.auth0.auth0_client.datetime')
    def test_get_management_token_success(self, mock_datetime):
        """Test successful management token retrieval."""
        mock_datetime.now.return_value = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        
        # Mock successful token response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 3600
        }
        mock_response.raise_for_status.return_value = None
        self.mock_requests.post.return_value = mock_response
        
        client = Auth0Client(self.config)
        token = client._get_management_token()
        
        self.assertEqual(token, "test_access_token")
        self.mock_requests.post.assert_called_once()
    
    def test_get_management_token_failure(self):
        """Test management token retrieval failure."""
        # Mock failed request
        self.mock_requests.post.side_effect = Exception("Network error")
        
        client = Auth0Client(self.config)
        token = client._get_management_token()
        
        self.assertIsNone(token)
    
    def test_create_user_success(self):
        """Test successful user creation."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock successful API response
            mock_response = Mock()
            mock_response.json.return_value = {
                "user_id": "auth0|test123",
                "email": "test@example.com",
                "name": "Test User"
            }
            mock_response.raise_for_status.return_value = None
            self.mock_requests.post.return_value = mock_response
            
            client = Auth0Client(self.config)
            result = client.create_user(
                email="test@example.com",
                password="securepassword123",
                name="Test User"
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["email"], "test@example.com")
            self.mock_requests.post.assert_called_once()
    
    def test_create_user_failure(self):
        """Test user creation failure."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock failed request
            self.mock_requests.post.side_effect = Exception("API error")
            
            client = Auth0Client(self.config)
            result = client.create_user(
                email="test@example.com",
                password="securepassword123"
            )
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)
    
    def test_get_user_success(self):
        """Test successful user retrieval."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock successful API response
            mock_response = Mock()
            mock_response.json.return_value = {
                "user_id": "auth0|test123",
                "email": "test@example.com",
                "name": "Test User"
            }
            mock_response.raise_for_status.return_value = None
            self.mock_requests.get.return_value = mock_response
            
            client = Auth0Client(self.config)
            result = client.get_user("auth0|test123")
            
            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["user_id"], "auth0|test123")
            self.mock_requests.get.assert_called_once()
    
    def test_create_role_success(self):
        """Test successful role creation."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock successful API response
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "rol_test123",
                "name": "admin",
                "description": "Administrator role"
            }
            mock_response.raise_for_status.return_value = None
            self.mock_requests.post.return_value = mock_response
            
            client = Auth0Client(self.config)
            result = client.create_role(
                name="admin",
                description="Administrator role"
            )
            
            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["name"], "admin")
            self.mock_requests.post.assert_called_once()
    
    def test_assign_roles_to_user_success(self):
        """Test successful role assignment."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.raise_for_status.return_value = None
            self.mock_requests.post.return_value = mock_response
            
            client = Auth0Client(self.config)
            result = client.assign_roles_to_user(
                user_id="auth0|test123",
                role_ids=["rol_admin", "rol_user"]
            )
            
            self.assertTrue(result["success"])
            self.mock_requests.post.assert_called_once()
    
    def test_validate_token_success(self):
        """Test successful token validation."""
        # Mock JWT header
        with patch('jwt.get_unverified_header') as mock_header:
            mock_header.return_value = {"kid": "test_key_id"}
            
            # Mock JWKS response
            mock_jwks_response = Mock()
            mock_jwks_response.json.return_value = {
                "keys": [{
                    "kid": "test_key_id",
                    "kty": "RSA",
                    "n": "test_n",
                    "e": "AQAB"
                }]
            }
            mock_jwks_response.raise_for_status.return_value = None
            self.mock_requests.get.return_value = mock_jwks_response
            
            # Mock JWT decode
            with patch('jwt.decode') as mock_decode:
                mock_decode.return_value = {
                    "sub": "auth0|test123",
                    "aud": "https://api.test.com",
                    "iss": "https://test.auth0.com/"
                }
                
                client = Auth0Client(self.config)
                result = client.validate_token("test_token")
                
                self.assertTrue(result["success"])
                self.assertEqual(result["data"]["sub"], "auth0|test123")
    
    def test_validate_token_failure(self):
        """Test token validation failure."""
        # Mock JWT header failure
        with patch('jwt.get_unverified_header') as mock_header:
            mock_header.side_effect = Exception("Invalid token")
            
            client = Auth0Client(self.config)
            result = client.validate_token("invalid_token")
            
            self.assertFalse(result["success"])
            self.assertIn("error", result)
    
    def test_get_user_summary_success(self):
        """Test successful user summary retrieval."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock user response
            mock_user_response = Mock()
            mock_user_response.json.return_value = {
                "user_id": "auth0|test123",
                "email": "test@example.com",
                "name": "Test User",
                "last_login": "2025-01-01T12:00:00.000Z",
                "logins_count": 5,
                "blocked": False,
                "email_verified": True
            }
            mock_user_response.raise_for_status.return_value = None
            
            # Mock roles response
            mock_roles_response = Mock()
            mock_roles_response.json.return_value = [
                {"id": "rol_admin", "name": "admin"},
                {"id": "rol_user", "name": "user"}
            ]
            mock_roles_response.raise_for_status.return_value = None
            
            # Mock logs response
            mock_logs_response = Mock()
            mock_logs_response.json.return_value = [
                {"event": "login", "date": "2025-01-01T12:00:00.000Z"},
                {"event": "logout", "date": "2025-01-01T11:00:00.000Z"}
            ]
            mock_logs_response.raise_for_status.return_value = None
            
            # Configure mock to return different responses
            self.mock_requests.get.side_effect = [
                mock_user_response,
                mock_roles_response,
                mock_logs_response
            ]
            
            client = Auth0Client(self.config)
            result = client.get_user_summary("auth0|test123")
            
            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["user"]["email"], "test@example.com")
            self.assertEqual(len(result["data"]["roles"]), 2)
            self.assertEqual(len(result["data"]["recent_logs"]), 2)
            self.assertEqual(result["data"]["summary"]["total_roles"], 2)
            self.assertEqual(result["data"]["summary"]["total_logs"], 2)
    
    def test_block_user_success(self):
        """Test successful user blocking."""
        # Mock management token
        with patch.object(Auth0Client, '_get_management_token', return_value="test_token"):
            # Mock successful API response
            mock_response = Mock()
            mock_response.json.return_value = {
                "user_id": "auth0|test123",
                "blocked": True
            }
            mock_response.raise_for_status.return_value = None
            self.mock_requests.put.return_value = mock_response
            
            client = Auth0Client(self.config)
            result = client.block_user("auth0|test123")
            
            self.assertTrue(result["success"])
            self.assertEqual(result["data"]["blocked"], True)
            self.mock_requests.put.assert_called_once()
    
    def test_generate_password_reset_token_success(self):
        """Test successful password reset token generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Password reset email sent"}
        mock_response.raise_for_status.return_value = None
        self.mock_requests.post.return_value = mock_response
        
        client = Auth0Client(self.config)
        result = client.generate_password_reset_token("test@example.com")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["message"], "Password reset email sent")
        self.mock_requests.post.assert_called_once()


class TestAuth0DataClasses(unittest.TestCase):
    """Test Auth0 data classes."""
    
    def test_auth0_user_creation(self):
        """Test Auth0User creation."""
        user = Auth0User(
            user_id="auth0|test123",
            email="test@example.com",
            name="Test User",
            email_verified=True
        )
        
        self.assertEqual(user.user_id, "auth0|test123")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.email_verified)
        self.assertFalse(user.blocked)
    
    def test_auth0_role_creation(self):
        """Test Auth0Role creation."""
        role = Auth0Role(
            id="rol_admin",
            name="admin",
            description="Administrator role",
            permissions=["read:users", "write:users"]
        )
        
        self.assertEqual(role.id, "rol_admin")
        self.assertEqual(role.name, "admin")
        self.assertEqual(role.description, "Administrator role")
        self.assertEqual(role.permissions, ["read:users", "write:users"])


if __name__ == "__main__":
    unittest.main() 