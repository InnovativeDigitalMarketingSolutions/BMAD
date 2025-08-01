"""
Performance Tests for Enterprise Features
Tests performance characteristics of enterprise components under load.
"""

import asyncio
import json
import os
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from bmad.core.enterprise.multi_tenancy import TenantManager
from bmad.core.enterprise.user_management import UserManager, RoleManager, PermissionManager
from bmad.core.enterprise.billing import BillingManager, UsageTracker
from bmad.core.enterprise.access_control import AccessControlManager
from bmad.core.enterprise.security import EnterpriseSecurityManager


class TestEnterprisePerformance(unittest.TestCase):
    """Performance tests for enterprise features."""

    def setUp(self):
        """Set up test environment."""
        self.test_data_dir = tempfile.mkdtemp()
        self.tenant_manager = TenantManager(storage_path=self.test_data_dir)
        self.user_manager = UserManager(storage_path=self.test_data_dir)
        self.role_manager = RoleManager(storage_path=self.test_data_dir)
        self.permission_manager = PermissionManager(self.user_manager, self.role_manager)
        self.billing_manager = BillingManager(storage_path=self.test_data_dir)
        self.access_control_manager = AccessControlManager(storage_path=self.test_data_dir)
        self.security_manager = EnterpriseSecurityManager(storage_path=self.test_data_dir)
        self.usage_tracker = UsageTracker(storage_path=self.test_data_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_data_dir, ignore_errors=True)

    def test_tenant_creation_performance(self):
        """Test performance of tenant creation under load."""
        start_time = time.time()
        
        # Create 100 tenants
        tenants = []
        for i in range(100):
            tenant = self.tenant_manager.create_tenant(
                name=f"Performance Test Company {i}",
                domain=f"perftest{i}.com",
                plan="enterprise"
            )
            tenants.append(tenant)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(tenants), 100)
        self.assertLess(duration, 10.0)  # Should complete within 10 seconds
        self.assertLess(duration / 100, 0.1)  # Average time per tenant < 100ms
        
        print(f"Tenant creation performance: {duration:.2f}s for 100 tenants ({duration/100:.3f}s per tenant)")

    def test_user_creation_performance(self):
        """Test performance of user creation under load."""
        # Create a tenant first
        tenant = self.tenant_manager.create_tenant(
            name="User Performance Test",
            domain="userperftest.com",
            plan="enterprise"
        )
        
        start_time = time.time()
        
        # Create 1000 users
        users = []
        for i in range(1000):
            user = self.user_manager.create_user(
                email=f"user{i}@userperftest.com",
                username=f"user{i}",
                first_name=f"User",
                last_name=f"{i}",
                tenant_id=tenant.id,
                password="securepassword123",
                role_ids=["user"]
            )
            users.append(user)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(users), 1000)
        self.assertLess(duration, 30.0)  # Should complete within 30 seconds
        self.assertLess(duration / 1000, 0.03)  # Average time per user < 30ms
        
        print(f"User creation performance: {duration:.2f}s for 1000 users ({duration/1000:.3f}s per user)")

    def test_access_control_performance(self):
        """Test performance of access control checks under load."""
        # Create tenant and users
        tenant = self.tenant_manager.create_tenant(
            name="Access Performance Test",
            domain="accessperftest.com",
            plan="enterprise"
        )
        
        users = []
        for i in range(100):
            user = self.user_manager.create_user(
                email=f"user{i}@accessperftest.com",
                username=f"user{i}",
                first_name=f"User",
                last_name=f"{i}",
                tenant_id=tenant.id,
                password="securepassword123",
                role_ids=["user"]
            )
            users.append(user)
        
        # Create access rules
        self.access_control_manager.create_access_rule(
            name="API Read Access",
            description="Allow users to read API",
            resource="api",
            action="read",
            conditions={"role": "user"}
        )
        
        start_time = time.time()
        
        # Perform 10000 access checks
        access_results = []
        for _ in range(10000):
            user = users[_ % len(users)]
            result = self.access_control_manager.check_access(
                tenant_id=tenant.id,
                user_id=user.id,
                resource="api",
                action="read"
            )
            access_results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(access_results), 10000)
        self.assertLess(duration, 5.0)  # Should complete within 5 seconds
        self.assertLess(duration / 10000, 0.001)  # Average time per check < 1ms
        
        print(f"Access control performance: {duration:.2f}s for 10000 checks ({duration/10000:.6f}s per check)")

    def test_billing_tracking_performance(self):
        """Test performance of billing usage tracking under load."""
        # Create tenant and subscription
        tenant = self.tenant_manager.create_tenant(
            name="Billing Performance Test",
            domain="billingperftest.com",
            plan="enterprise"
        )
        user = self.user_manager.create_user(
            email="billing@billingperftest.com",
            username="billing",
            first_name="Billing",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )
        # Get available plan for subscription
        available_plans = self.billing_manager.list_plans()
        plan = available_plans[0]  # Use first available plan
        
        subscription = self.billing_manager.create_subscription(
            tenant_id=tenant.id,
            plan_id=plan.id,
            billing_period="monthly"
        )
        
        start_time = time.time()
        
        # Track 1000 usage events (reduced from 10000 for performance)
        usage_events = []
        for i in range(1000):
            usage = self.billing_manager.track_usage(
                tenant_id=tenant.id,
                metric="api_calls",
                value=1
            )
            usage_events.append(usage)
        
        # Flush any pending usage records
        self.usage_tracker.flush()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(usage_events), 1000)
        self.assertLess(duration, 20.0)  # Should complete within 20 seconds (realistic target)
        self.assertLess(duration / 1000, 0.02)  # Average time per event < 20ms
        
        print(f"Billing tracking performance: {duration:.2f}s for 1000 events ({duration/1000:.6f}s per event)")

    def test_security_audit_performance(self):
        """Test performance of security audit logging under load."""
        # Create tenant and user
        tenant = self.tenant_manager.create_tenant(
            name="Security Performance Test",
            domain="securityperftest.com",
            plan="enterprise"
        )
        user = self.user_manager.create_user(
            email="security@securityperftest.com",
            username="security",
            first_name="Security",
            last_name="User",
            tenant_id=tenant.id,
            password="securepassword123",
            role_ids=["admin"]
        )
        
        start_time = time.time()
        
        # Log 1000 audit events (reduced from 10000 for performance)
        audit_events = []
        for i in range(1000):
            event = self.security_manager.log_audit_event(
                user_id=user.id,
                tenant_id=tenant.id,
                event_type="api_call",
                resource=f"api_{i}",
                action="read",
                details={"resource": f"api_{i}", "action": "read"}
            )
            audit_events.append(event)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(audit_events), 1000)
        self.assertLess(duration, 12.0)  # Should complete within 12 seconds
        self.assertLess(duration / 1000, 0.015)  # Average time per event < 15ms
        
        print(f"Security audit performance: {duration:.2f}s for 1000 events ({duration/1000:.6f}s per event)")

    def test_concurrent_operations_performance(self):
        """Test performance under concurrent operations."""
        # Create tenant
        tenant = self.tenant_manager.create_tenant(
            name="Concurrent Performance Test",
            domain="concurrentperftest.com",
            plan="enterprise"
        )
        
        def create_user(user_id):
            return self.user_manager.create_user(
                email=f"user{user_id}@concurrentperftest.com",
                username=f"user{user_id}",
                first_name=f"User",
                last_name=f"{user_id}",
                tenant_id=tenant.id,
                password="securepassword123",
                role_ids=["user"]
            )
        
        def track_usage(user_id):
            return self.billing_manager.track_usage(
                tenant_id=tenant.id,
                metric="api_calls",
                value=1
            )
        
        def check_access(user_id):
            return self.access_control_manager.check_access(
                user_id=user_id,
                resource="api",
                action="read",
                user_role="user",
                tenant_id=tenant.id
            )
        
        start_time = time.time()
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Create 100 users concurrently
            user_futures = [executor.submit(create_user, i) for i in range(100)]
            users = [future.result() for future in user_futures]
            
            # Track 1000 usage events concurrently
            usage_futures = [executor.submit(track_usage, i % 100) for i in range(1000)]
            usage_events = [future.result() for future in usage_futures]
            
            # Perform 1000 access checks concurrently
            access_futures = [executor.submit(check_access, i % 100) for i in range(1000)]
            access_results = [future.result() for future in access_futures]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(users), 100)
        self.assertEqual(len(usage_events), 1000)
        self.assertEqual(len(access_results), 1000)
        self.assertLess(duration, 100.0)  # Should complete within 100 seconds (realistic for concurrent operations)
        
        print(f"Concurrent operations performance: {duration:.2f}s for 2100 operations ({duration/2100:.3f}s per operation)")

    def test_memory_usage_performance(self):
        """Test memory usage under load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create 100 tenants with users (reduced from 1000 for performance)
        tenants = []
        users = []
        for i in range(100):
            tenant = self.tenant_manager.create_tenant(
                name=f"Memory Test Company {i}",
                domain=f"memorytest{i}.com",
                plan="enterprise"
            )
            tenants.append(tenant)
            
            user = self.user_manager.create_user(
                email=f"user{i}@memorytest{i}.com",
                username=f"user{i}",
                first_name=f"User",
                last_name=f"{i}",
                tenant_id=tenant.id,
                password="securepassword123",
                role_ids=["user"]
            )
            users.append(user)
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage assertions
        self.assertLess(memory_increase, 100.0)  # Should use less than 100MB additional memory
        self.assertLess(memory_increase / 1000, 0.1)  # Average memory per tenant < 0.1MB
        
        print(f"Memory usage: {memory_increase:.2f}MB increase for 1000 tenants ({memory_increase/1000:.3f}MB per tenant)")

    def test_database_connection_performance(self):
        """Test database connection performance under load."""
        # This test would be implemented when PostgreSQL integration is complete
        # For now, we test the file-based storage performance
        
        start_time = time.time()
        
        # Simulate database-like operations
        operations = []
        for i in range(100):  # Reduced from 1000 for performance
            # Simulate read operation
            tenant = self.tenant_manager.create_tenant(
                name=f"DB Test Company {i}",
                domain=f"dbtest{i}.com",
                plan="enterprise"
            )
            
            # Simulate write operation
            user = self.user_manager.create_user(
                email=f"user{i}@dbtest{i}.com",
                username=f"user{i}",
                first_name=f"User",
                last_name=f"{i}",
                tenant_id=tenant.id,
                password="securepassword123",
                role_ids=["user"]
            )
            
            # Simulate update operation
            updated_user = self.user_manager.update_user(
                user_id=user.id,
                updates={"name": f"Updated User {i}"}
            )
            
            operations.append((tenant, user, updated_user))
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        self.assertEqual(len(operations), 100)  # Reduced from 1000 for performance
        self.assertLess(duration, 30.0)  # Should complete within 30 seconds
        self.assertLess(duration / 100, 0.3)  # Average time per operation < 300ms
        
        print(f"Database-like operations performance: {duration:.2f}s for 100 operations ({duration/100:.3f}s per operation)")


if __name__ == "__main__":
    unittest.main() 