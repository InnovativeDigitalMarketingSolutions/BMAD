"""
Unit tests for Enterprise Features Module

Tests multi-tenancy, user management, billing, access control, and security features.
"""

import pytest
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from pathlib import Path

from bmad.core.enterprise.multi_tenancy import (
    TenantManager, Tenant, TenantContext, tenant_manager
)
from bmad.core.enterprise.user_management import (
    UserManager, RoleManager, PermissionManager, User, Role, UserStatus, Permission,
    user_manager, role_manager, permission_manager
)
from bmad.core.enterprise.billing import (
    BillingManager, UsageTracker, SubscriptionManager, Plan, Subscription, UsageRecord,
    SubscriptionStatus, BillingPeriod, billing_manager, usage_tracker, subscription_manager
)
from bmad.core.enterprise.access_control import (
    FeatureFlagManager, AccessControlManager, FeatureFlag, AccessRule,
    FeatureFlagType, feature_flag_manager, access_control_manager
)
from bmad.core.enterprise.security import (
    EnterpriseSecurityManager, SecurityPolicy, AuditLog, SecurityLevel, AuditEventType,
    enterprise_security_manager
)


class TestMultiTenancy:
    """Test multi-tenancy functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def tenant_manager_instance(self, temp_storage):
        """Create tenant manager instance with temporary storage."""
        return TenantManager(storage_path=temp_storage)
    
    def test_create_tenant(self, tenant_manager_instance):
        """Test tenant creation."""
        tenant = tenant_manager_instance.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="professional"
        )
        
        assert tenant.name == "Test Company"
        assert tenant.domain == "test.com"
        assert tenant.plan == "professional"
        assert tenant.status == "active"
        assert len(tenant.id) > 0
        assert tenant.settings["max_agents"] == 20
        assert "analytics" in tenant.features
    
    def test_get_tenant(self, tenant_manager_instance):
        """Test getting tenant by ID."""
        tenant = tenant_manager_instance.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="basic"
        )
        
        retrieved_tenant = tenant_manager_instance.get_tenant(tenant.id)
        assert retrieved_tenant is not None
        assert retrieved_tenant.name == "Test Company"
    
    def test_get_tenant_by_domain(self, tenant_manager_instance):
        """Test getting tenant by domain."""
        tenant = tenant_manager_instance.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="basic"
        )
        
        retrieved_tenant = tenant_manager_instance.get_tenant_by_domain("test.com")
        assert retrieved_tenant is not None
        assert retrieved_tenant.id == tenant.id
    
    def test_update_tenant(self, tenant_manager_instance):
        """Test updating tenant."""
        tenant = tenant_manager_instance.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="basic"
        )
        
        updated_tenant = tenant_manager_instance.update_tenant(
            tenant.id,
            name="Updated Company",
            plan="enterprise"
        )
        
        assert updated_tenant.name == "Updated Company"
        assert updated_tenant.plan == "enterprise"
        assert updated_tenant.settings["max_agents"] == 100
    
    def test_is_feature_enabled(self, tenant_manager_instance):
        """Test feature flag checking."""
        tenant = tenant_manager_instance.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="enterprise"
        )
        
        tenant_manager_instance.set_current_tenant(tenant)
        
        assert tenant_manager_instance.is_feature_enabled("all_agents")
        assert tenant_manager_instance.is_feature_enabled("custom_integrations")
        assert not tenant_manager_instance.is_feature_enabled("nonexistent_feature")
    
    def test_check_limit(self, tenant_manager_instance):
        """Test limit checking."""
        tenant = tenant_manager_instance.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="basic"
        )
        
        tenant_manager_instance.set_current_tenant(tenant)
        
        assert tenant_manager_instance.check_limit("max_agents", 3)
        assert not tenant_manager_instance.check_limit("max_agents", 10)
        assert tenant_manager_instance.check_limit("nonexistent_limit", 100)


class TestUserManagement:
    """Test user management functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def user_manager_instance(self, temp_storage):
        """Create user manager instance with temporary storage."""
        return UserManager(storage_path=temp_storage)
    
    @pytest.fixture
    def role_manager_instance(self, temp_storage):
        """Create role manager instance with temporary storage."""
        return RoleManager(storage_path=temp_storage)
    
    def test_create_user(self, user_manager_instance):
        """Test user creation."""
        user = user_manager_instance.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            tenant_id="tenant123",
            password="SecurePass123!"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.tenant_id == "tenant123"
        assert user.status == UserStatus.PENDING
        assert user.password_hash is not None
    
    def test_authenticate_user(self, user_manager_instance):
        """Test user authentication."""
        user = user_manager_instance.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            tenant_id="tenant123",
            password="SecurePass123!"
        )
        
        # Activate user
        user_manager_instance.update_user(user.id, status=UserStatus.ACTIVE)
        
        # Test successful authentication
        authenticated_user = user_manager_instance.authenticate_user(
            "test@example.com",
            "SecurePass123!"
        )
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        
        # Test failed authentication
        failed_user = user_manager_instance.authenticate_user(
            "test@example.com",
            "WrongPassword"
        )
        assert failed_user is None
    
    def test_create_role(self, role_manager_instance):
        """Test role creation."""
        role = role_manager_instance.create_role(
            name="custom_role",
            description="Custom role for testing",
            permissions=[Permission.VIEW_AGENTS.value, Permission.EXECUTE_AGENTS.value]
        )
        
        assert role.name == "custom_role"
        assert role.description == "Custom role for testing"
        assert len(role.permissions) == 2
        assert Permission.VIEW_AGENTS.value in role.permissions
    
    def test_permission_checking(self, user_manager_instance, role_manager_instance):
        """Test permission checking."""
        # Create local permission manager with the same instances
        local_permission_manager = PermissionManager(user_manager_instance, role_manager_instance)
        
        # Create user with role
        user = user_manager_instance.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            tenant_id="tenant123",
            password="SecurePass123!"
        )
        
        # Create custom role
        role = role_manager_instance.create_role(
            name="custom_role",
            description="Custom role",
            permissions=[Permission.VIEW_AGENTS.value, Permission.EXECUTE_AGENTS.value]
        )
        
        # Assign role to user
        user_manager_instance.update_user(user.id, role_ids=[role.id])
        
        # Test permissions
        permissions = local_permission_manager.get_user_permissions(user.id)
        assert Permission.VIEW_AGENTS.value in permissions
        assert Permission.EXECUTE_AGENTS.value in permissions
        assert Permission.DELETE_AGENTS.value not in permissions
        
        assert local_permission_manager.has_permission(user.id, Permission.VIEW_AGENTS.value)
        assert not local_permission_manager.has_permission(user.id, Permission.DELETE_AGENTS.value)


class TestBilling:
    """Test billing functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def billing_manager_instance(self, temp_storage):
        """Create billing manager instance with temporary storage."""
        return BillingManager(storage_path=temp_storage)
    
    @pytest.fixture
    def usage_tracker_instance(self, temp_storage):
        """Create usage tracker instance with temporary storage."""
        return UsageTracker(storage_path=temp_storage)
    
    def test_create_plan(self, billing_manager_instance):
        """Test plan creation."""
        plan = billing_manager_instance.create_plan(
            name="Custom Plan",
            description="Custom plan for testing",
            price_monthly=49.99,
            price_yearly=499.99,
            features=["custom_feature"],
            limits={"max_agents": 15}
        )
        
        assert plan.name == "Custom Plan"
        assert plan.price_monthly == 49.99
        assert plan.price_yearly == 499.99
        assert "custom_feature" in plan.features
        assert plan.limits["max_agents"] == 15
    
    def test_create_subscription(self, billing_manager_instance):
        """Test subscription creation."""
        plan = billing_manager_instance.create_plan(
            name="Test Plan",
            description="Test plan",
            price_monthly=29.99,
            price_yearly=299.99,
            features=["test_feature"],
            limits={"max_agents": 10}
        )
        
        subscription = billing_manager_instance.create_subscription(
            tenant_id="tenant123",
            plan_id=plan.id,
            billing_period=BillingPeriod.MONTHLY
        )
        
        assert subscription.tenant_id == "tenant123"
        assert subscription.plan_id == plan.id
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.billing_period == BillingPeriod.MONTHLY
    
    def test_usage_tracking(self, usage_tracker_instance):
        """Test usage tracking."""
        # Record usage
        usage_tracker_instance.record_usage("tenant123", "api_calls", 5)
        usage_tracker_instance.record_usage("tenant123", "api_calls", 3)
        
        # Get current month usage
        usage = usage_tracker_instance.get_current_month_usage("tenant123", "api_calls")
        assert usage == 8
        
        # Get usage for specific period
        now = datetime.utcnow()
        start_date = now - timedelta(days=1)
        usage = usage_tracker_instance.get_usage("tenant123", "api_calls", start_date, now)
        assert usage == 8
    
    def test_subscription_manager(self, billing_manager_instance, usage_tracker_instance):
        """Test subscription manager."""
        subscription_manager = SubscriptionManager(billing_manager_instance, usage_tracker_instance)
        
        # Create plan and subscription
        plan = billing_manager_instance.create_plan(
            name="Test Plan",
            description="Test plan",
            price_monthly=29.99,
            price_yearly=299.99,
            features=["test_feature"],
            limits={"max_agents": 10}
        )
        
        subscription = billing_manager_instance.create_subscription(
            tenant_id="tenant123",
            plan_id=plan.id,
            billing_period=BillingPeriod.MONTHLY
        )
        
        # Test subscription status
        status = subscription_manager.check_subscription_status("tenant123")
        assert status is not None
        assert status.id == subscription.id
        
        # Test usage limits
        assert subscription_manager.check_usage_limits("tenant123", "max_agents", 5)
        assert not subscription_manager.check_usage_limits("tenant123", "max_agents", 15)
        
        # Test feature access
        assert subscription_manager.can_use_feature("tenant123", "test_feature")
        assert not subscription_manager.can_use_feature("tenant123", "nonexistent_feature")


class TestAccessControl:
    """Test access control functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def feature_flag_manager_instance(self, temp_storage):
        """Create feature flag manager instance with temporary storage."""
        return FeatureFlagManager(storage_path=temp_storage)
    
    @pytest.fixture
    def access_control_manager_instance(self, temp_storage):
        """Create access control manager instance with temporary storage."""
        return AccessControlManager(storage_path=temp_storage)
    
    def test_create_feature_flag(self, feature_flag_manager_instance):
        """Test feature flag creation."""
        flag = feature_flag_manager_instance.create_feature_flag(
            name="test_flag",
            description="Test feature flag",
            flag_type=FeatureFlagType.BOOLEAN,
            default_value=True
        )
        
        assert flag.name == "test_flag"
        assert flag.flag_type == FeatureFlagType.BOOLEAN
        assert flag.default_value is True
    
    def test_feature_flag_overrides(self, feature_flag_manager_instance):
        """Test feature flag tenant overrides."""
        flag = feature_flag_manager_instance.create_feature_flag(
            name="test_flag",
            description="Test feature flag",
            flag_type=FeatureFlagType.BOOLEAN,
            default_value=False
        )
        
        # Test default value
        assert feature_flag_manager_instance.get_flag_value("test_flag") is False
        
        # Test tenant override
        feature_flag_manager_instance.set_tenant_override("test_flag", "tenant123", True)
        assert feature_flag_manager_instance.get_flag_value("test_flag", "tenant123") is True
        
        # Test other tenant still gets default
        assert feature_flag_manager_instance.get_flag_value("test_flag", "tenant456") is False
    
    def test_access_control_rules(self, access_control_manager_instance):
        """Test access control rules."""
        rule = access_control_manager_instance.create_access_rule(
            name="test_rule",
            description="Test access rule",
            resource="test_resource",
            action="test_action",
            conditions={"min_role": "user"}
        )
        
        assert rule.name == "test_rule"
        assert rule.resource == "test_resource"
        assert rule.action == "test_action"
        assert rule.conditions["min_role"] == "user"
    
    def test_access_checking(self, access_control_manager_instance):
        """Test access checking."""
        # Create access rule for a specific resource/action combination
        access_control_manager_instance.create_access_rule(
            name="test_rule",
            description="Test access rule",
            resource="test_resource",
            action="test_action",
            conditions={"min_role": "user"}
        )
        
        # Test access with valid role
        assert access_control_manager_instance.check_access(
            user_id="user123",
            resource="test_resource",
            action="test_action",
            user_role="user"
        )
        
        # Test access with insufficient role
        assert not access_control_manager_instance.check_access(
            user_id="user123",
            resource="test_resource",
            action="test_action",
            user_role="viewer"
        )


class TestSecurity:
    """Test security functionality."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def security_manager_instance(self, temp_storage):
        """Create security manager instance with temporary storage."""
        return EnterpriseSecurityManager(storage_path=temp_storage)
    
    def test_create_security_policy(self, security_manager_instance):
        """Test security policy creation."""
        policy = security_manager_instance.create_security_policy(
            name="test_policy",
            description="Test security policy",
            policy_type="test_type",
            rules={"test_rule": True},
            security_level=SecurityLevel.HIGH
        )
        
        assert policy.name == "test_policy"
        assert policy.policy_type == "test_type"
        assert policy.security_level == SecurityLevel.HIGH
        assert policy.rules["test_rule"] is True
    
    def test_password_validation(self, security_manager_instance):
        """Test password validation."""
        # Test valid password
        result = security_manager_instance.validate_password("SecurePass123!")
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        
        # Test invalid password
        result = security_manager_instance.validate_password("weak")
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_audit_logging(self, security_manager_instance):
        """Test audit logging."""
        security_manager_instance.log_audit_event(
            user_id="user123",
            tenant_id="tenant123",
            event_type=AuditEventType.LOGIN,
            resource="auth",
            action="login",
            details={"method": "password"},
            ip_address="192.168.1.1",
            success=True
        )
        
        logs = security_manager_instance.get_audit_logs(user_id="user123")
        assert len(logs) == 1
        assert logs[0].event_type == AuditEventType.LOGIN
        assert logs[0].user_id == "user123"
        assert logs[0].success is True
    
    def test_security_report(self, security_manager_instance):
        """Test security report generation."""
        # Log some events
        security_manager_instance.log_audit_event(
            user_id="user123",
            tenant_id="tenant123",
            event_type=AuditEventType.LOGIN,
            resource="auth",
            action="login",
            details={},
            success=True
        )
        
        security_manager_instance.log_audit_event(
            user_id="user123",
            tenant_id="tenant123",
            event_type=AuditEventType.SECURITY_VIOLATION,
            resource="agents",
            action="unauthorized_access",
            details={},
            success=False
        )
        
        report = security_manager_instance.generate_security_report(tenant_id="tenant123")
        
        assert report["tenant_id"] == "tenant123"
        assert report["summary"]["total_events"] == 2
        assert report["summary"]["security_violations"] == 1
        assert "login" in report["event_breakdown"]
        assert "security_violation" in report["event_breakdown"]
    
    def test_security_compliance(self, security_manager_instance):
        """Test security compliance checking."""
        # Log some events
        security_manager_instance.log_audit_event(
            user_id="user123",
            tenant_id="tenant123",
            event_type=AuditEventType.LOGIN,
            resource="auth",
            action="login",
            details={},
            success=True
        )
        
        compliance = security_manager_instance.check_security_compliance("tenant123")
        
        assert compliance["tenant_id"] == "tenant123"
        assert "compliance_score" in compliance
        assert "recommendations" in compliance
        assert isinstance(compliance["compliance_score"], (int, float))


class TestEnterpriseIntegration:
    """Test enterprise features integration."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_tenant_user_workflow(self, temp_storage):
        """Test complete tenant and user workflow."""
        # Create tenant
        tenant_manager = TenantManager(storage_path=temp_storage)
        tenant = tenant_manager.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="professional"
        )
        
        # Create user
        user_manager = UserManager(storage_path=temp_storage)
        user = user_manager.create_user(
            email="admin@test.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            tenant_id=tenant.id,
            password="SecurePass123!"
        )
        
        # Activate user
        user_manager.update_user(user.id, status=UserStatus.ACTIVE)
        
        # Create role
        role_manager = RoleManager(storage_path=temp_storage)
        role = role_manager.create_role(
            name="admin_role",
            description="Administrator role",
            permissions=[p.value for p in Permission]
        )
        
        # Assign role to user
        user_manager.update_user(user.id, role_ids=[role.id])
        
        # Create local permission manager with the same instances
        local_permission_manager = PermissionManager(user_manager, role_manager)
        
        # Verify permissions
        permissions = local_permission_manager.get_user_permissions(user.id)
        assert len(permissions) > 0
        assert Permission.VIEW_AGENTS.value in permissions
    
    def test_billing_integration(self, temp_storage):
        """Test billing integration with tenants."""
        # Create tenant
        tenant_manager = TenantManager(storage_path=temp_storage)
        tenant = tenant_manager.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="basic"
        )
        
        # Create subscription
        billing_manager = BillingManager(storage_path=temp_storage)
        plan = billing_manager.list_plans()[0]  # Get first available plan
        
        subscription = billing_manager.create_subscription(
            tenant_id=tenant.id,
            plan_id=plan.id,
            billing_period=BillingPeriod.MONTHLY
        )
        
        # Track usage
        usage_tracker = UsageTracker(storage_path=temp_storage)
        usage_tracker.record_usage(tenant.id, "api_calls", 10)
        
        # Check subscription status
        subscription_manager = SubscriptionManager(billing_manager, usage_tracker)
        status = subscription_manager.check_subscription_status(tenant.id)
        assert status is not None
        assert status.status == SubscriptionStatus.ACTIVE
    
    def test_security_audit_workflow(self, temp_storage):
        """Test security audit workflow."""
        # Create tenant
        tenant_manager = TenantManager(storage_path=temp_storage)
        tenant = tenant_manager.create_tenant(
            name="Test Company",
            domain="test.com",
            plan="enterprise"
        )
        
        # Create user
        user_manager = UserManager(storage_path=temp_storage)
        user = user_manager.create_user(
            email="user@test.com",
            username="user",
            first_name="Test",
            last_name="User",
            tenant_id=tenant.id,
            password="SecurePass123!"
        )
        
        # Log security events
        security_manager = EnterpriseSecurityManager(storage_path=temp_storage)
        security_manager.log_audit_event(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type=AuditEventType.LOGIN,
            resource="auth",
            action="login",
            details={},
            success=True
        )
        
        # Generate security report
        report = security_manager.generate_security_report(tenant_id=tenant.id)
        assert report["tenant_id"] == tenant.id
        assert report["summary"]["total_events"] == 1
        
        # Check compliance
        compliance = security_manager.check_security_compliance(tenant.id)
        assert compliance["tenant_id"] == tenant.id
        assert "compliance_score" in compliance


if __name__ == "__main__":
    pytest.main([__file__]) 