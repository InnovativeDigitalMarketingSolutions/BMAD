"""
End-to-End Tests for Enterprise Features
Tests complete enterprise workflows including multi-tenancy, billing, and security.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from bmad.core.enterprise.multi_tenancy import TenantManager
from bmad.core.enterprise.user_management import UserManager, RoleManager, PermissionManager
from bmad.core.enterprise.billing import BillingManager, BillingPeriod, UsageTracker
from bmad.core.enterprise.access_control import AccessControlManager
from bmad.core.enterprise.security import EnterpriseSecurityManager


class TestEnterpriseFeaturesE2E(unittest.TestCase):
    """End-to-End tests for enterprise features."""

    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.tenant_manager = TenantManager(storage_path=self.test_data_dir)
        self.user_manager = UserManager(storage_path=self.test_data_dir)
        self.role_manager = RoleManager(storage_path=self.test_data_dir)
        self.permission_manager = PermissionManager(self.user_manager, self.role_manager)
        self.billing_manager = BillingManager(storage_path=self.test_data_dir)
        self.usage_tracker = UsageTracker(storage_path=self.test_data_dir)
        self.access_control_manager = AccessControlManager(storage_path=self.test_data_dir)
        self.security_manager = EnterpriseSecurityManager(storage_path=self.test_data_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_data_dir, ignore_errors=True)

    def test_complete_tenant_onboarding_workflow(self):
        """Test complete tenant onboarding workflow."""
        # 1. Create tenant
        tenant = self.tenant_manager.create_tenant(
            name="Test Company",
            domain="testcompany.com",
            plan="enterprise"
        )
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant.name, "Test Company")

        # 2. Create admin user
        admin_user = self.user_manager.create_user(
            email="admin@testcompany.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user.email, "admin@testcompany.com")

        # 3. Create subscription
        subscription = self.billing_manager.create_subscription(
            tenant_id=tenant.id,
            plan_id="enterprise",
            billing_period=BillingPeriod.MONTHLY
        )
        self.assertIsNotNone(subscription)
        self.assertEqual(subscription.tenant_id, tenant.id)

        # 4. Set up access control
        access_rule = self.access_control_manager.create_access_rule(
            name="API Read Access",
            description="Allow admin users to read API",
            resource="api",
            action="read",
            conditions={"role": "admin", "active": True}
        )
        self.assertIsNotNone(access_rule)

        # 5. Verify complete setup
        tenant_data = self.tenant_manager.get_tenant(tenant.id)
        self.assertIsNotNone(tenant_data)
        self.assertEqual(tenant_data.status, "active")

    def test_multi_tenant_isolation(self):
        """Test that tenants are properly isolated."""
        # Create two tenants
        tenant1 = self.tenant_manager.create_tenant(
            name="Company A",
            domain="companya.com",
            plan="basic"
        )
        tenant2 = self.tenant_manager.create_tenant(
            name="Company B",
            domain="companyb.com",
            plan="enterprise"
        )

        # Create users in different tenants
        user1 = self.user_manager.create_user(
            email="user1@companya.com",
            username="user1",
            first_name="User",
            last_name="1",
            tenant_id=tenant1.id,
            password="securepassword123",
            role_ids=["user"]
        )
        user2 = self.user_manager.create_user(
            email="user2@companyb.com",
            username="user2",
            first_name="User",
            last_name="2",
            tenant_id=tenant2.id,
            password="securepassword123",
            role_ids=["admin"]
        )

        # Verify isolation
        tenant1_users = self.user_manager.list_users_by_tenant(tenant_id=tenant1.id)
        tenant2_users = self.user_manager.list_users_by_tenant(tenant_id=tenant2.id)

        self.assertEqual(len(tenant1_users), 1)
        self.assertEqual(len(tenant2_users), 1)
        self.assertEqual(tenant1_users[0].email, "user1@companya.com")
        self.assertEqual(tenant2_users[0].email, "user2@companyb.com")

    def test_billing_workflow_e2e(self):
        """Test complete billing workflow."""
        # 1. Create tenant and user
        tenant = self.tenant_manager.create_tenant(
            name="Billing Test Company",
            domain="billingtest.com",
            plan="pro"
        )
        user = self.user_manager.create_user(
            email="billing@billingtest.com",
            username="billing",
            first_name="Billing",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )

        # 2. Create subscription - use the first available plan
        available_plans = self.billing_manager.list_plans()
        self.assertGreater(len(available_plans), 0)
        plan = available_plans[0]  # Use the first available plan
        
        subscription = self.billing_manager.create_subscription(
            tenant_id=tenant.id,
            plan_id=plan.id,
            billing_period=BillingPeriod.MONTHLY
        )

        # 3. Track usage
        usage_result = self.billing_manager.track_usage(
            tenant_id=tenant.id,
            metric="api_calls",
            value=100
        )
        self.assertTrue(usage_result["success"])

        # 4. Generate invoice
        invoice_result = self.billing_manager.generate_invoice(
            tenant_id=tenant.id,
            subscription_id=subscription.id
        )
        self.assertTrue(invoice_result["success"])
        self.assertIsNotNone(invoice_result["invoice"])

        # 5. Verify billing data
        billing_summary = self.billing_manager.get_billing_summary(tenant_id=tenant.id)
        self.assertTrue(billing_summary["success"])
        self.assertEqual(billing_summary["summary"]["subscription"]["plan_id"], plan.id)

    def test_security_audit_workflow(self):
        """Test complete security audit workflow."""
        # 1. Create tenant and user
        tenant = self.tenant_manager.create_tenant(
            name="Security Test Company",
            domain="securitytest.com",
            plan="enterprise"
        )
        user = self.user_manager.create_user(
            email="security@securitytest.com",
            username="security",
            first_name="Security",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )

        # 2. Log security events
        self.security_manager.log_audit_event(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type="user_login",
            resource="auth",
            action="login",
            details={"ip": "192.168.1.1", "user_agent": "test-agent"}
        )

        self.security_manager.log_audit_event(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type="data_access",
            resource="user_data",
            action="read",
            details={"resource": "user_data", "action": "read"}
        )

        # 3. Generate security report
        security_report = self.security_manager.generate_security_report(
            tenant_id=tenant.id,
            start_date=datetime(2025, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 12, 31, tzinfo=UTC)
        )
        self.assertIsNotNone(security_report)
        self.assertIn("summary", security_report)
        self.assertIn("event_breakdown", security_report)

        # 4. Verify audit trail
        audit_events = self.security_manager.get_audit_logs(
            tenant_id=tenant.id,
            user_id=user.id
        )
        self.assertGreater(len(audit_events), 0)

    def test_access_control_workflow(self):
        """Test complete access control workflow."""
        # 1. Create tenant and users
        tenant = self.tenant_manager.create_tenant(
            name="Access Test Company",
            domain="accesstest.com",
            plan="enterprise"
        )
        admin_user = self.user_manager.create_user(
            email="admin@accesstest.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )
        regular_user = self.user_manager.create_user(
            email="user@accesstest.com",
            username="user",
            first_name="Regular",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["user"]
        )

        # 2. Create access rules
        admin_rule = self.access_control_manager.create_access_rule(
            name="API Full Access",
            description="Allow admin users full API access",
            resource="api",
            action="*",
            conditions={"role": "admin"}
        )
        user_rule = self.access_control_manager.create_access_rule(
            name="API Read Access",
            description="Allow users to read API",
            resource="api",
            action="read",
            conditions={"role": "user"}
        )

        # 3. Test access control
        admin_access = self.access_control_manager.check_access(
            user_id=admin_user.id,
            resource="api",
            action="write",
            user_role="admin",
            tenant_id=tenant.id
        )
        self.assertTrue(admin_access)

        user_access = self.access_control_manager.check_access(
            user_id=regular_user.id,
            resource="api",
            action="write",
            user_role="user",
            tenant_id=tenant.id
        )
        self.assertFalse(user_access)

        user_read_access = self.access_control_manager.check_access(
            user_id=regular_user.id,
            resource="api",
            action="read",
            user_role="user",
            tenant_id=tenant.id
        )
        self.assertTrue(user_read_access)

    def test_enterprise_integration_workflow(self):
        """Test integration between all enterprise components."""
        # 1. Complete tenant setup
        tenant = self.tenant_manager.create_tenant(
            name="Integration Test Company",
            domain="integrationtest.com",
            plan="enterprise"
        )
        user = self.user_manager.create_user(
            email="integration@integrationtest.com",
            username="integration",
            first_name="Integration",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )
        # Get available plan for enterprise subscription
        available_plans = self.billing_manager.list_plans()
        enterprise_plan = None
        for p in available_plans:
            if "enterprise" in p.name.lower():
                enterprise_plan = p
                break
        if not enterprise_plan:
            enterprise_plan = available_plans[0]  # Fallback to first plan
        
        subscription = self.billing_manager.create_subscription(
            tenant_id=tenant.id,
            plan_id=enterprise_plan.id,
            billing_period=BillingPeriod.MONTHLY
        )

        # 2. Set up security and access control
        self.security_manager.log_audit_event(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type="tenant_created",
            resource="tenant",
            action="create",
            details={"subscription_id": subscription.id}
        )

        access_rule = self.access_control_manager.create_access_rule(
            name="Enterprise Features Access",
            description="Allow admin users full enterprise features access",
            resource="enterprise_features",
            action="*",
            conditions={"role": "admin"}
        )

        # 3. Test complete workflow
        # Simulate API call
        api_access = self.access_control_manager.check_access(
            user_id=user.id,
            resource="enterprise_features",
            action="read",
            user_role="admin",
            tenant_id=tenant.id
        )
        self.assertTrue(api_access)

        # Track usage
        usage_result = self.billing_manager.track_usage(
            tenant_id=tenant.id,
            metric="api_calls",
            value=1
        )
        self.assertTrue(usage_result["success"])

        # Log audit event
        self.security_manager.log_audit_event(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type="api_call",
            resource="enterprise_features",
            action="read",
            details={"resource": "enterprise_features", "action": "read"}
        )

        # 4. Verify complete integration
        tenant_summary = self.tenant_manager.get_tenant_summary(tenant.id)
        self.assertTrue(tenant_summary["success"])
        self.assertEqual(tenant_summary["summary"]["status"], "active")
        self.assertIn("subscription", tenant_summary["summary"])
        self.assertIn("users", tenant_summary["summary"])


if __name__ == "__main__":
    unittest.main() 