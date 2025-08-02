"""
Unit tests for Enterprise CLI module.

Tests the command-line interface for enterprise features including:
- Multi-tenancy management
- User management
- Billing and subscriptions
- Access control
- Security management
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from datetime import datetime
import sys

# Mock zware externe dependencies
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['opentelemetry.sdk.trace'] = MagicMock()
sys.modules['opentelemetry.sdk.trace.export'] = MagicMock()
sys.modules['opentelemetry.sdk.resources'] = MagicMock()
sys.modules['opentelemetry.exporter'] = MagicMock()
sys.modules['opentelemetry.exporter.jaeger'] = MagicMock()
sys.modules['opentelemetry.exporter.jaeger.thrift'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.http'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.http.trace_exporter'] = MagicMock()
sys.modules['opentelemetry.instrumentation'] = MagicMock()
sys.modules['opentelemetry.instrumentation.requests'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['langgraph.graph'] = MagicMock()
sys.modules['langgraph.checkpoint'] = MagicMock()
sys.modules['langgraph.checkpoint.memory'] = MagicMock()
sys.modules['psutil'] = MagicMock()

# Import the CLI module
import cli.enterprise_cli as enterprise_cli


class TestEnterpriseCLI:
    """Test cases for Enterprise CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_tenant = MagicMock()
        self.mock_tenant.id = "tenant-123"
        self.mock_tenant.name = "Test Tenant"
        self.mock_tenant.domain = "test.com"
        self.mock_tenant.plan = "professional"
        self.mock_tenant.status = "active"
        self.mock_tenant.created_at = datetime(2024, 1, 1, 12, 0, 0)

    def test_enterprise_group_help(self):
        """Test enterprise group help command."""
        result = self.runner.invoke(enterprise_cli.enterprise, ['--help'])
        assert result.exit_code == 0
        assert "Enterprise Features Management CLI" in result.output

    # Multi-Tenancy Tests
    @patch('cli.enterprise_cli.tenant_manager')
    def test_create_tenant_success(self, mock_tenant_manager):
        """Test successful tenant creation."""
        mock_tenant_manager.create_tenant.return_value = self.mock_tenant
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'create',
            '--name', 'Test Tenant',
            '--domain', 'test.com',
            '--plan', 'professional'
        ])
        
        assert result.exit_code == 0
        assert "✅ Tenant created successfully!" in result.output
        assert "ID: tenant-123" in result.output
        assert "Name: Test Tenant" in result.output
        mock_tenant_manager.create_tenant.assert_called_once_with(
            name='Test Tenant', domain='test.com', plan='professional'
        )

    @patch('cli.enterprise_cli.tenant_manager')
    def test_create_tenant_error(self, mock_tenant_manager):
        """Test tenant creation with error."""
        mock_tenant_manager.create_tenant.side_effect = Exception("Database error")
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'create',
            '--name', 'Test Tenant',
            '--domain', 'test.com',
            '--plan', 'professional'
        ])
        
        assert result.exit_code == 1
        assert "❌ Error creating tenant: Database error" in result.output

    @patch('cli.enterprise_cli.tenant_manager')
    def test_list_tenants_success(self, mock_tenant_manager):
        """Test successful tenant listing."""
        mock_tenant_manager.list_tenants.return_value = [self.mock_tenant]
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'list'
        ])
        
        assert result.exit_code == 0
        assert "Found 1 tenants:" in result.output
        assert "tenant-123" in result.output
        assert "Test Tenant" in result.output

    @patch('cli.enterprise_cli.tenant_manager')
    def test_list_tenants_empty(self, mock_tenant_manager):
        """Test tenant listing with no tenants."""
        mock_tenant_manager.list_tenants.return_value = []
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'list'
        ])
        
        assert result.exit_code == 0
        assert "No tenants found." in result.output

    @patch('cli.enterprise_cli.tenant_manager')
    def test_update_tenant_success(self, mock_tenant_manager):
        """Test successful tenant update."""
        mock_tenant_manager.update_tenant.return_value = self.mock_tenant
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'update', 'tenant-123',
            '--name', 'Updated Tenant',
            '--plan', 'enterprise'
        ])
        
        assert result.exit_code == 0
        assert "✅ Tenant updated successfully!" in result.output
        mock_tenant_manager.update_tenant.assert_called_once_with(
            'tenant-123', name='Updated Tenant', plan='enterprise'
        )

    @patch('cli.enterprise_cli.tenant_manager')
    def test_update_tenant_no_updates(self, mock_tenant_manager):
        """Test tenant update with no updates specified."""
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'update', 'tenant-123'
        ])
        
        assert result.exit_code == 0
        assert "No updates specified." in result.output
        mock_tenant_manager.update_tenant.assert_not_called()

    # User Management Tests
    @patch('cli.enterprise_cli.user_manager')
    def test_create_user_success(self, mock_user_manager):
        """Test successful user creation."""
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user_manager.create_user.return_value = mock_user
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'users', 'create',
            '--email', 'test@example.com',
            '--username', 'testuser',
            '--first-name', 'Test',
            '--last-name', 'User',
            '--tenant-id', 'tenant-123',
            '--password', 'password123'
        ])
        
        assert result.exit_code == 0
        assert "✅ User created successfully!" in result.output
        assert "ID: user-123" in result.output

    @patch('cli.enterprise_cli.user_manager')
    def test_list_users_success(self, mock_user_manager):
        """Test successful user listing."""
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.status.value = "active"
        mock_user.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_user_manager.list_users_by_tenant.return_value = [mock_user]
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'users', 'list', 'tenant-123'
        ])
        
        assert result.exit_code == 0
        assert "Found 1 users for tenant tenant-123:" in result.output
        assert "user-123" in result.output

    # Role Management Tests
    @patch('cli.enterprise_cli.role_manager')
    def test_create_role_success(self, mock_role_manager):
        """Test successful role creation."""
        mock_role = MagicMock()
        mock_role.id = "role-123"
        mock_role.name = "Admin"
        mock_role_manager.create_role.return_value = mock_role
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'roles', 'create',
            '--name', 'Admin',
            '--description', 'Administrator role',
            '--permissions', 'read,write,delete'
        ])
        
        assert result.exit_code == 0
        assert "✅ Role created successfully!" in result.output
        assert "ID: role-123" in result.output

    @patch('cli.enterprise_cli.role_manager')
    def test_list_roles_success(self, mock_role_manager):
        """Test successful role listing."""
        mock_role = MagicMock()
        mock_role.id = "role-123"
        mock_role.name = "Admin"
        mock_role.description = "Administrator role"
        mock_role_manager.list_roles.return_value = [mock_role]
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'roles', 'list'
        ])
        
        assert result.exit_code == 0
        assert "Found 1 roles:" in result.output
        assert "role-123" in result.output

    # Billing Tests
    @patch('cli.enterprise_cli.billing_manager')
    def test_list_plans_success(self, mock_billing_manager):
        """Test successful plan listing."""
        mock_plan = MagicMock()
        mock_plan.id = "plan-123"
        mock_plan.name = "Professional"
        mock_plan.price = 99.99
        mock_billing_manager.list_plans.return_value = [mock_plan]
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'billing', 'plans'
        ])
        
        assert result.exit_code == 0
        assert "Found 1 plans:" in result.output
        assert "plan-123" in result.output

    @patch('cli.enterprise_cli.subscription_manager')
    def test_subscribe_success(self, mock_subscription_manager):
        """Test successful subscription creation."""
        mock_subscription = MagicMock()
        mock_subscription.id = "sub-123"
        mock_subscription.status = "active"
        mock_subscription_manager.create_subscription.return_value = mock_subscription
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'billing', 'subscribe',
            '--tenant-id', 'tenant-123',
            '--plan-id', 'plan-123',
            '--period', 'monthly'
        ])
        
        assert result.exit_code == 0
        assert "✅ Subscription created successfully!" in result.output
        assert "ID:" in result.output

    @patch('cli.enterprise_cli.usage_tracker')
    def test_record_usage_success(self, mock_usage_tracker):
        """Test successful usage recording."""
        mock_usage_tracker.record_usage.return_value = True
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'billing', 'record-usage',
            '--tenant-id', 'tenant-123',
            '--metric', 'api_calls',
            '--value', '1000'
        ])
        
        assert result.exit_code == 0
        assert "✅ Usage recorded successfully!" in result.output
        mock_usage_tracker.record_usage.assert_called_once_with(
            'tenant-123', 'api_calls', 1000
        )

    # Feature Flag Tests
    @patch('cli.enterprise_cli.feature_flag_manager')
    def test_create_feature_flag_success(self, mock_feature_flag_manager):
        """Test successful feature flag creation."""
        mock_flag = MagicMock()
        mock_flag.name = "new_feature"
        mock_flag.type = "boolean"
        mock_feature_flag_manager.create_flag.return_value = mock_flag
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'features', 'create',
            '--name', 'new_feature',
            '--description', 'New feature flag',
            '--type', 'boolean',
            '--default-value', 'false'
        ])
        
        assert result.exit_code == 0
        assert "✅ Feature flag created successfully!" in result.output
        assert "ID:" in result.output

    @patch('cli.enterprise_cli.feature_flag_manager')
    def test_get_feature_flag_success(self, mock_feature_flag_manager):
        """Test successful feature flag retrieval."""
        mock_feature_flag_manager.get_flag.return_value = "true"
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'features', 'get', 'new_feature'
        ])
        
        assert result.exit_code == 0
        assert "Feature flag: new_feature" in result.output
        assert "Value:" in result.output

    @patch('cli.enterprise_cli.feature_flag_manager')
    def test_set_feature_override_success(self, mock_feature_flag_manager):
        """Test successful feature flag override."""
        mock_feature_flag_manager.set_override.return_value = True
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'features', 'set-override', 'new_feature',
            '--tenant-id', 'tenant-123',
            '--value', 'true'
        ])
        
        assert result.exit_code == 0
        assert "✅ Override set successfully!" in result.output

    # Security Tests
    @patch('cli.enterprise_cli.enterprise_security_manager')
    def test_validate_password_success(self, mock_security_manager):
        """Test successful password validation."""
        # Create a proper mock that matches the expected structure
        mock_result = MagicMock()
        mock_result.valid = True
        mock_result.score = 85
        mock_result.feedback = ['Good password']
        # Mock the dictionary-like access that the CLI expects
        mock_result.__getitem__ = MagicMock(side_effect=lambda key: {
            'policy_level': 'strong',
            'score': 85,
            'feedback': ['Good password']
        }.get(key, MagicMock()))
        
        mock_security_manager.validate_password.return_value = mock_result
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'security', 'validate-password',
            '--password', 'StrongPassword123!'
        ])
        
        assert result.exit_code == 0
        assert "✅ Password is valid" in result.output

    @patch('cli.enterprise_cli.enterprise_security_manager')
    def test_validate_password_weak(self, mock_security_manager):
        """Test weak password validation."""
        # Create a proper mock that matches the expected structure
        mock_result = {
            'valid': False,
            'errors': ['Too short', 'No special characters'],
            'policy_level': 'weak'
        }
        
        mock_security_manager.validate_password.return_value = mock_result
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'security', 'validate-password',
            '--password', 'weak'
        ])
        
        assert result.exit_code == 0
        assert "❌ Password is invalid" in result.output

    @patch('cli.enterprise_cli.enterprise_security_manager')
    def test_audit_logs_success(self, mock_security_manager):
        """Test successful audit logs retrieval."""
        mock_log = MagicMock()
        mock_log.id = "log-123"
        mock_log.action = "login"
        mock_log.user_id = "user-123"
        mock_log.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        mock_log.event_type.value = "login"
        mock_log.resource = "api"
        mock_log.success = True
        mock_log.ip_address = "192.168.1.1"
        mock_security_manager.get_audit_logs.return_value = [mock_log]
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'security', 'audit-logs',
            '--days', '30'
        ])
        
        assert result.exit_code == 0
        assert "Found 1 audit logs:" in result.output
        assert "user-123" in result.output

    @patch('cli.enterprise_cli.enterprise_security_manager')
    def test_security_report_success(self, mock_security_manager):
        """Test successful security report generation."""
        # Create a proper mock that matches the expected structure
        mock_report = {
            'report_period': {
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            },
            'tenant_id': 'tenant-123',
            'summary': {
                'total_events': 100,
                'unique_users': 25,
                'security_violations': 3
            },
            'event_breakdown': {
                'login': 50,
                'logout': 45,
                'access_denied': 5
            },
            'security_violations': [
                {
                    'timestamp': '2024-01-15 10:30:00',
                    'user_id': 'user-123',
                    'action': 'failed_login'
                }
            ]
        }
        
        mock_security_manager.generate_security_report.return_value = mock_report
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'security', 'report',
            '--days', '30'
        ])
        
        assert result.exit_code == 0
        assert "Security Report" in result.output

    @patch('cli.enterprise_cli.enterprise_security_manager')
    def test_compliance_check_success(self, mock_security_manager):
        """Test successful compliance check."""
        # Create a proper mock that matches the expected structure
        mock_compliance = {
            'tenant_id': 'tenant-123',
            'assessment_date': '2024-01-31',
            'compliance_score': 85,
            'security_violations': 2,
            'failed_login_rate': 0.05,
            'total_access_events': 1000,
            'recommendations': [
                'Implement multi-factor authentication',
                'Review access logs regularly'
            ]
        }
        
        mock_security_manager.check_security_compliance.return_value = mock_compliance
        
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'security', 'compliance',
            '--tenant-id', 'tenant-123'
        ])
        
        assert result.exit_code == 0
        assert "Security Compliance Report" in result.output

    # Error Handling Tests
    def test_missing_required_options(self):
        """Test error handling for missing required options."""
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'create'
        ])
        
        assert result.exit_code != 0
        assert "Error: Missing option" in result.output

    def test_invalid_choice_options(self):
        """Test error handling for invalid choice options."""
        result = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'create',
            '--name', 'Test',
            '--domain', 'test.com',
            '--plan', 'invalid_plan'
        ])
        
        assert result.exit_code != 0
        assert "Error: Invalid value" in result.output

    # Integration Tests
    @patch('cli.enterprise_cli.tenant_manager')
    @patch('cli.enterprise_cli.user_manager')
    def test_tenant_user_workflow(self, mock_user_manager, mock_tenant_manager):
        """Test complete tenant and user workflow."""
        # Create tenant
        mock_tenant_manager.create_tenant.return_value = self.mock_tenant
        result1 = self.runner.invoke(enterprise_cli.enterprise, [
            'tenants', 'create',
            '--name', 'Test Tenant',
            '--domain', 'test.com',
            '--plan', 'professional'
        ])
        assert result1.exit_code == 0
        
        # Create user for tenant
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user_manager.create_user.return_value = mock_user
        
        result2 = self.runner.invoke(enterprise_cli.enterprise, [
            'users', 'create',
            '--email', 'test@example.com',
            '--username', 'testuser',
            '--first-name', 'Test',
            '--last-name', 'User',
            '--tenant-id', 'tenant-123',
            '--password', 'password123'
        ])
        assert result2.exit_code == 0
        
        # Verify both operations were called
        mock_tenant_manager.create_tenant.assert_called_once()
        mock_user_manager.create_user.assert_called_once() 