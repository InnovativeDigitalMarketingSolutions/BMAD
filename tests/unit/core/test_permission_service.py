"""
Unit tests for enhanced permission service implementation.

Tests advanced permission checking capabilities including tenant-aware permissions,
role-based access control, and enhanced permission patterns.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Pragmatic mocking: Mock Flask request context at module level
sys.modules['flask'] = MagicMock()
sys.modules['flask.request'] = MagicMock()
sys.modules['flask.jsonify'] = MagicMock()

from bmad.core.security.permission_service import PermissionService, permission_service
from bmad.core.enterprise.user_management import User, Role, UserStatus, Permission


class TestPermissionService:
    """Test cases for enhanced permission service functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.permission_service = PermissionService()
        
        # Mock user data
        self.test_user = User(
            id="test_user_123",
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            tenant_id="test_tenant_456",
            role_ids=["role_1", "role_2"],
            status=UserStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Mock role data
        self.test_role_1 = Role(
            id="role_1",
            name="admin",
            description="Administrator role",
            permissions=["view_agents", "execute_agents", "view_analytics"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_system=False
        )
        
        self.test_role_2 = Role(
            id="role_2",
            name="user",
            description="Regular user role",
            permissions=["view_agents"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_system=False
        )
    
    def test_permission_service_initialization(self):
        """Test permission service initialization."""
        assert self.permission_service.permission_cache == {}
        assert self.permission_service.cache_ttl == 300
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_permission_without_tenant(self, mock_permission_manager):
        """Test permission checking without tenant context."""
        mock_permission_manager.has_permission.return_value = True
        
        result = self.permission_service.check_permission("user123", "view_agents")
        
        assert result is True
        mock_permission_manager.has_permission.assert_called_with("user123", "view_agents")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_permission_with_tenant(self, mock_permission_manager):
        """Test permission checking with tenant context."""
        mock_permission_manager.check_tenant_permission.return_value = True
        
        result = self.permission_service.check_permission("user123", "view_agents", "tenant456")
        
        assert result is True
        mock_permission_manager.check_tenant_permission.assert_called_with("user123", "tenant456", "view_agents")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_any_permission_without_tenant(self, mock_permission_manager):
        """Test any permission checking without tenant context."""
        mock_permission_manager.has_any_permission.return_value = True
        
        result = self.permission_service.check_any_permission("user123", ["view_agents", "execute_agents"])
        
        assert result is True
        mock_permission_manager.has_any_permission.assert_called_with("user123", ["view_agents", "execute_agents"])
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_any_permission_with_tenant(self, mock_permission_manager):
        """Test any permission checking with tenant context."""
        mock_permission_manager.get_user_permissions_by_tenant.return_value = {"view_agents", "execute_agents"}
        
        result = self.permission_service.check_any_permission("user123", ["view_agents", "execute_agents"], "tenant456")
        
        assert result is True
        mock_permission_manager.get_user_permissions_by_tenant.assert_called_with("user123", "tenant456")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_all_permissions_without_tenant(self, mock_permission_manager):
        """Test all permissions checking without tenant context."""
        mock_permission_manager.has_all_permissions.return_value = True
        
        result = self.permission_service.check_all_permissions("user123", ["view_agents", "execute_agents"])
        
        assert result is True
        mock_permission_manager.has_all_permissions.assert_called_with("user123", ["view_agents", "execute_agents"])
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_all_permissions_with_tenant(self, mock_permission_manager):
        """Test all permissions checking with tenant context."""
        mock_permission_manager.get_user_permissions_by_tenant.return_value = {"view_agents", "execute_agents"}
        
        result = self.permission_service.check_all_permissions("user123", ["view_agents", "execute_agents"], "tenant456")
        
        assert result is True
        mock_permission_manager.get_user_permissions_by_tenant.assert_called_with("user123", "tenant456")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_role(self, mock_permission_manager):
        """Test role checking."""
        mock_permission_manager.has_role.return_value = True
        
        result = self.permission_service.check_role("user123", "admin")
        
        assert result is True
        mock_permission_manager.has_role.assert_called_with("user123", "admin")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_any_role(self, mock_permission_manager):
        """Test any role checking."""
        mock_permission_manager.has_any_role.return_value = True
        
        result = self.permission_service.check_any_role("user123", ["admin", "user"])
        
        assert result is True
        mock_permission_manager.has_any_role.assert_called_with("user123", ["admin", "user"])
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_check_all_roles(self, mock_permission_manager):
        """Test all roles checking."""
        mock_permission_manager.has_all_roles.return_value = True
        
        result = self.permission_service.check_all_roles("user123", ["admin", "user"])
        
        assert result is True
        mock_permission_manager.has_all_roles.assert_called_with("user123", ["admin", "user"])
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_get_user_permissions_without_tenant(self, mock_permission_manager):
        """Test getting user permissions without tenant context."""
        mock_permission_manager.get_user_permissions.return_value = {"view_agents", "execute_agents"}
        
        result = self.permission_service.get_user_permissions("user123")
        
        assert result == {"view_agents", "execute_agents"}
        mock_permission_manager.get_user_permissions.assert_called_with("user123")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_get_user_permissions_with_tenant(self, mock_permission_manager):
        """Test getting user permissions with tenant context."""
        mock_permission_manager.get_user_permissions_by_tenant.return_value = {"view_agents", "execute_agents"}
        
        result = self.permission_service.get_user_permissions("user123", "tenant456")
        
        assert result == {"view_agents", "execute_agents"}
        mock_permission_manager.get_user_permissions_by_tenant.assert_called_with("user123", "tenant456")
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_get_user_roles(self, mock_permission_manager):
        """Test getting user roles."""
        mock_roles = [self.test_role_1, self.test_role_2]
        mock_permission_manager.get_user_roles.return_value = mock_roles
        
        result = self.permission_service.get_user_roles("user123")
        
        assert result == ["admin", "user"]
        mock_permission_manager.get_user_roles.assert_called_with("user123")
    
    @patch('bmad.core.security.permission_service.enterprise_security_manager')
    def test_log_permission_check_success(self, mock_security_manager):
        """Test logging successful permission check."""
        # Mock request context completely to avoid Flask issues
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.remote_addr = "127.0.0.1"
            
            self.permission_service.log_permission_check(
                user_id="user123",
                permission="view_agents",
                tenant_id="tenant456",
                success=True,
                endpoint="/api/test"
            )
            
            mock_security_manager.log_audit_event.assert_called_once()
            call_args = mock_security_manager.log_audit_event.call_args
            # Check the details dict for permission
            details = call_args[1]["details"]
            assert details["permission"] == "view_agents"
            assert call_args[1]["user_id"] == "user123"
            assert call_args[1]["tenant_id"] == "tenant456"
            assert call_args[1]["success"] is True
    
    @patch('bmad.core.security.permission_service.enterprise_security_manager')
    def test_log_permission_check_failure(self, mock_security_manager):
        """Test logging failed permission check."""
        # Mock request context completely to avoid Flask issues
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.remote_addr = "127.0.0.1"
            
            self.permission_service.log_permission_check(
                user_id="user123",
                permission="view_agents",
                tenant_id="tenant456",
                success=False,
                endpoint="/api/test"
            )
            
            mock_security_manager.log_audit_event.assert_called_once()
            call_args = mock_security_manager.log_audit_event.call_args
            # Check the details dict for permission
            details = call_args[1]["details"]
            assert details["permission"] == "view_agents"
            assert call_args[1]["user_id"] == "user123"
            assert call_args[1]["tenant_id"] == "tenant456"
            assert call_args[1]["success"] is False
    
    @patch('bmad.core.security.permission_service.enterprise_security_manager')
    def test_log_permission_check_exception_handling(self, mock_security_manager):
        """Test exception handling in permission check logging."""
        mock_security_manager.log_audit_event.side_effect = Exception("Logging failed")
        
        # Should not raise exception
        self.permission_service.log_permission_check(
            user_id="user123",
            permission="view_agents",
            tenant_id="tenant456",
            success=True,
            endpoint="/api/test"
        )


class TestPermissionDecorators:
    """Test cases for permission decorators."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.permission_service = PermissionService()
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    def test_require_permission_enhanced_dev_mode(self, mock_permission_service, mock_getenv):
        """Test enhanced permission decorator in development mode."""
        mock_getenv.return_value = "true"
        
        from bmad.core.security.permission_service import require_permission_enhanced
        
        @require_permission_enhanced("view_agents")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    def test_require_permission_enhanced_success(self, mock_permission_service, mock_getenv):
        """Test enhanced permission decorator with successful permission check."""
        mock_getenv.return_value = "false"
        mock_permission_service.check_permission.return_value = True
        mock_permission_service.get_user_permissions.return_value = {"view_agents"}
        
        from bmad.core.security.permission_service import require_permission_enhanced
        
        # Mock Flask request context completely
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.user = MagicMock(id="user123")
            mock_request.tenant_id = "tenant456"
            mock_request.endpoint = "/api/test"
            
            @require_permission_enhanced("view_agents", tenant_aware=True)
            def test_function():
                return "success"
            
            result = test_function()
            assert result == "success"
            mock_permission_service.check_permission.assert_called_with("user123", "view_agents", "tenant456")
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    @patch('bmad.core.security.permission_service.jsonify')
    def test_require_permission_enhanced_failure(self, mock_jsonify, mock_permission_service, mock_getenv):
        """Test enhanced permission decorator with failed permission check."""
        mock_getenv.return_value = "false"
        mock_permission_service.check_permission.return_value = False
        mock_permission_service.get_user_permissions.return_value = {"other_permission"}
        mock_jsonify.return_value = {"error": "Insufficient permissions"}
        
        from bmad.core.security.permission_service import require_permission_enhanced
        
        # Mock Flask request context completely
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.user = MagicMock(id="user123")
            mock_request.tenant_id = "tenant456"
            mock_request.endpoint = "/api/test"
            
            @require_permission_enhanced("view_agents", tenant_aware=True)
            def test_function():
                return "success"
            
            result = test_function()
            # Decorator returns (response, status_code) tuple
            assert result[0] == {"error": "Insufficient permissions"}
            assert result[1] == 403
            mock_permission_service.check_permission.assert_called_with("user123", "view_agents", "tenant456")
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    def test_require_any_permission_success(self, mock_permission_service, mock_getenv):
        """Test any permission decorator with successful permission check."""
        mock_getenv.return_value = "false"
        mock_permission_service.check_any_permission.return_value = True
        mock_permission_service.get_user_permissions.return_value = {"view_agents"}
        
        from bmad.core.security.permission_service import require_any_permission
        
        # Mock Flask request context completely
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.user = MagicMock(id="user123")
            mock_request.tenant_id = "tenant456"
            mock_request.endpoint = "/api/test"
            
            @require_any_permission(["view_agents", "execute_agents"], tenant_aware=True)
            def test_function():
                return "success"
            
            result = test_function()
            assert result == "success"
            mock_permission_service.check_any_permission.assert_called_with("user123", ["view_agents", "execute_agents"], "tenant456")
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    def test_require_all_permissions_success(self, mock_permission_service, mock_getenv):
        """Test all permissions decorator with successful permission check."""
        mock_getenv.return_value = "false"
        mock_permission_service.check_all_permissions.return_value = True
        mock_permission_service.get_user_permissions.return_value = {"view_agents", "execute_agents"}
        
        from bmad.core.security.permission_service import require_all_permissions
        
        # Mock Flask request context completely
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.user = MagicMock(id="user123")
            mock_request.tenant_id = "tenant456"
            mock_request.endpoint = "/api/test"
            
            @require_all_permissions(["view_agents", "execute_agents"], tenant_aware=True)
            def test_function():
                return "success"
            
            result = test_function()
            assert result == "success"
            mock_permission_service.check_all_permissions.assert_called_with("user123", ["view_agents", "execute_agents"], "tenant456")
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    def test_require_role_success(self, mock_permission_service, mock_getenv):
        """Test role decorator with successful role check."""
        mock_getenv.return_value = "false"
        mock_permission_service.check_role.return_value = True
        mock_permission_service.get_user_roles.return_value = ["admin"]
        
        from bmad.core.security.permission_service import require_role
        
        # Mock Flask request context completely
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.user = MagicMock(id="user123")
            mock_request.tenant_id = "tenant456"
            mock_request.endpoint = "/api/test"
            
            @require_role("admin")
            def test_function():
                return "success"
            
            result = test_function()
            assert result == "success"
            mock_permission_service.check_role.assert_called_with("user123", "admin")
    
    @patch('bmad.core.security.permission_service.os.getenv')
    @patch('bmad.core.security.permission_service.permission_service')
    def test_require_any_role_success(self, mock_permission_service, mock_getenv):
        """Test any role decorator with successful role check."""
        mock_getenv.return_value = "false"
        mock_permission_service.check_any_role.return_value = True
        mock_permission_service.get_user_roles.return_value = ["admin", "user"]
        
        from bmad.core.security.permission_service import require_any_role
        
        # Mock Flask request context completely
        with patch('bmad.core.security.permission_service.request') as mock_request:
            mock_request.user = MagicMock(id="user123")
            mock_request.tenant_id = "tenant456"
            mock_request.endpoint = "/api/test"
            
            @require_any_role(["admin", "user"])
            def test_function():
                return "success"
            
            result = test_function()
            assert result == "success"
            mock_permission_service.check_any_role.assert_called_with("user123", ["admin", "user"])


class TestPermissionServiceIntegration:
    """Integration tests for permission service with real scenarios."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.permission_service = PermissionService()
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_complete_permission_workflow(self, mock_permission_manager):
        """Test complete permission workflow."""
        # Setup mocks with proper return values
        mock_permission_manager.get_user_permissions.return_value = {"view_agents", "execute_agents", "view_analytics"}
        mock_permission_manager.get_user_permissions_by_tenant.return_value = {"view_agents", "execute_agents"}
        mock_permission_manager.has_permission.return_value = True
        mock_permission_manager.check_tenant_permission.return_value = True
        mock_permission_manager.has_any_permission.return_value = True
        mock_permission_manager.has_all_permissions.return_value = True
        mock_permission_manager.has_role.return_value = True
        mock_permission_manager.has_any_role.return_value = True
        mock_permission_manager.has_all_roles.return_value = True
        
        # Test permission checking
        assert self.permission_service.check_permission("user123", "view_agents") is True
        assert self.permission_service.check_permission("user123", "view_agents", "tenant456") is True
        
        # Test multiple permissions
        assert self.permission_service.check_any_permission("user123", ["view_agents", "execute_agents"]) is True
        assert self.permission_service.check_all_permissions("user123", ["view_agents", "execute_agents"]) is True
        
        # Test role checking
        assert self.permission_service.check_role("user123", "admin") is True
        assert self.permission_service.check_any_role("user123", ["admin", "user"]) is True
        assert self.permission_service.check_all_roles("user123", ["admin", "user"]) is True
        
        # Test getting permissions
        permissions = self.permission_service.get_user_permissions("user123")
        assert permissions == {"view_agents", "execute_agents", "view_analytics"}
        
        tenant_permissions = self.permission_service.get_user_permissions("user123", "tenant456")
        assert tenant_permissions == {"view_agents", "execute_agents"}
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_tenant_isolation(self, mock_permission_manager):
        """Test tenant isolation in permission checking."""
        # Setup mocks for different tenants with proper return values
        mock_permission_manager.get_user_permissions_by_tenant.side_effect = lambda user_id, tenant_id: {
            "tenant1": {"view_agents", "execute_agents"},
            "tenant2": {"view_agents"}
        }.get(tenant_id, set())
        
        # Mock check_tenant_permission to return True for tenant1, False for tenant2
        def mock_check_tenant_permission(user_id, tenant_id, permission):
            if tenant_id == "tenant1" and permission == "execute_agents":
                return True
            elif tenant_id == "tenant2" and permission == "execute_agents":
                return False
            return True
        
        mock_permission_manager.check_tenant_permission.side_effect = mock_check_tenant_permission
        
        # Test tenant-specific permissions
        tenant1_permissions = self.permission_service.get_user_permissions("user123", "tenant1")
        assert tenant1_permissions == {"view_agents", "execute_agents"}
        
        tenant2_permissions = self.permission_service.get_user_permissions("user123", "tenant2")
        assert tenant2_permissions == {"view_agents"}
        
        # Test permission checking in different tenants
        assert self.permission_service.check_permission("user123", "execute_agents", "tenant1") is True
        assert self.permission_service.check_permission("user123", "execute_agents", "tenant2") is False
    
    @patch('bmad.core.security.permission_service.permission_manager')
    def test_permission_denial_scenarios(self, mock_permission_manager):
        """Test permission denial scenarios."""
        # Setup mocks for denied permissions
        mock_permission_manager.has_permission.return_value = False
        mock_permission_manager.check_tenant_permission.return_value = False
        mock_permission_manager.has_any_permission.return_value = False
        mock_permission_manager.has_all_permissions.return_value = False
        mock_permission_manager.has_role.return_value = False
        mock_permission_manager.has_any_role.return_value = False
        mock_permission_manager.has_all_roles.return_value = False
        
        # Test permission denial
        assert self.permission_service.check_permission("user123", "admin_permission") is False
        assert self.permission_service.check_permission("user123", "admin_permission", "tenant456") is False
        
        # Test multiple permissions denial
        assert self.permission_service.check_any_permission("user123", ["admin_permission", "system_permission"]) is False
        assert self.permission_service.check_all_permissions("user123", ["admin_permission", "system_permission"]) is False
        
        # Test role denial
        assert self.permission_service.check_role("user123", "admin") is False
        assert self.permission_service.check_any_role("user123", ["admin", "system"]) is False
        assert self.permission_service.check_all_roles("user123", ["admin", "system"]) is False 