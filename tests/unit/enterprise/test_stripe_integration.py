"""
Tests for Stripe integration in enterprise billing.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from bmad.core.enterprise.billing import (
    BillingManager, SubscriptionManager, UsageTracker,
    SubscriptionStatus, BillingPeriod, Plan, Subscription
)


class TestStripeIntegration:
    """Test Stripe integration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.billing_manager = BillingManager(storage_path="test_data/billing")
        self.subscription_manager = SubscriptionManager(
            self.billing_manager, 
            UsageTracker(storage_path="test_data/usage")
        )
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_stripe_client_initialization(self, mock_stripe_client, mock_stripe_config):
        """Test Stripe client initialization."""
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        billing_manager = BillingManager()
        
        assert billing_manager.stripe_client is not None
        mock_stripe_config.assert_called_once()
        mock_stripe_client.assert_called_once()
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', False)
    def test_stripe_not_available(self):
        """Test behavior when Stripe is not available."""
        billing_manager = BillingManager()
        
        assert billing_manager.stripe_client is None
        
        # Test that Stripe methods return error
        result = billing_manager.create_stripe_customer("test_tenant", "test@example.com", "Test User")
        assert result["success"] is False
        assert "Stripe not configured" in result["error"]
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch.dict('os.environ', {})
    def test_stripe_no_api_key(self, mock_stripe_client, mock_stripe_config):
        """Test behavior when Stripe API key is not configured."""
        billing_manager = BillingManager()
        
        assert billing_manager.stripe_client is None
        
        result = billing_manager.create_stripe_customer("test_tenant", "test@example.com", "Test User")
        assert result["success"] is False
        assert "Stripe not configured" in result["error"]
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_create_stripe_customer_success(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test successful Stripe customer creation."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_client_instance.create_customer.return_value = {
            "success": True,
            "data": {"id": "cus_test123"}
        }
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Mock tenant manager
        mock_tenant_manager.update_tenant.return_value = True
        
        billing_manager = BillingManager()
        
        result = billing_manager.create_stripe_customer("test_tenant", "test@example.com", "Test User")
        
        assert result["success"] is True
        assert result["data"]["id"] == "cus_test123"
        mock_client_instance.create_customer.assert_called_once()
        mock_tenant_manager.update_tenant.assert_called_once()
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_create_stripe_customer_failure(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test Stripe customer creation failure."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_client_instance.create_customer.return_value = {
            "success": False,
            "error": "Invalid API key"
        }
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        billing_manager = BillingManager()
        
        result = billing_manager.create_stripe_customer("test_tenant", "test@example.com", "Test User")
        
        assert result["success"] is False
        assert "Invalid API key" in result["error"]
        mock_tenant_manager.update_tenant.assert_not_called()
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_create_stripe_subscription_success(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test successful Stripe subscription creation."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_client_instance.create_subscription.return_value = {
            "success": True,
            "data": {
                "id": "sub_test123",
                "status": "active",
                "current_period_start": int(datetime.now().timestamp()),
                "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp())
            }
        }
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Mock tenant manager
        mock_tenant_manager.get_tenant.return_value = {
            "id": "test_tenant",
            "stripe_customer_id": "cus_test123"
        }
        
        billing_manager = BillingManager()
        
        result = billing_manager.create_stripe_subscription("test_tenant", "price_test123")
        
        assert result["success"] is True
        assert result["data"]["id"] == "sub_test123"
        mock_client_instance.create_subscription.assert_called_once()
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_create_stripe_subscription_no_customer(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test Stripe subscription creation with no customer ID."""
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Mock tenant manager
        mock_tenant_manager.get_tenant.return_value = {
            "id": "test_tenant",
            "stripe_customer_id": None
        }
        
        billing_manager = BillingManager()
        
        result = billing_manager.create_stripe_subscription("test_tenant", "price_test123")
        
        assert result["success"] is False
        assert "No Stripe customer ID" in result["error"]
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_cancel_stripe_subscription_success(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test successful Stripe subscription cancellation."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_client_instance.cancel_subscription.return_value = {
            "success": True,
            "data": {"id": "sub_test123", "status": "canceled"}
        }
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Create a test subscription
        subscription = Subscription(
            id="test_sub",
            tenant_id="test_tenant",
            plan_id="test_plan",
            status=SubscriptionStatus.ACTIVE,
            billing_period=BillingPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stripe_subscription_id="sub_test123"
        )
        
        billing_manager = BillingManager()
        billing_manager.subscriptions["test_sub"] = subscription
        
        result = billing_manager.cancel_stripe_subscription("test_tenant")
        
        assert result["success"] is True
        mock_client_instance.cancel_subscription.assert_called_once()
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_get_stripe_billing_summary_success(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test successful Stripe billing summary retrieval."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_client_instance.get_customer_summary.return_value = {
            "success": True,
            "customer": {"id": "cus_test123", "email": "test@example.com"},
            "subscriptions": [{"id": "sub_test123", "status": "active"}],
            "payment_methods": [{"id": "pm_test123", "type": "card"}],
            "invoices": [{"id": "in_test123", "amount_due": 1000}]
        }
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Mock tenant manager
        mock_tenant_manager.get_tenant.return_value = {
            "id": "test_tenant",
            "stripe_customer_id": "cus_test123"
        }
        
        billing_manager = BillingManager()
        
        result = billing_manager.get_stripe_billing_summary("test_tenant")
        
        assert result["success"] is True
        assert result["customer"]["id"] == "cus_test123"
        assert len(result["subscriptions"]) == 1
        assert len(result["payment_methods"]) == 1
        assert len(result["invoices"]) == 1
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_handle_stripe_webhook_success(self, mock_stripe_client, mock_stripe_config):
        """Test successful Stripe webhook handling."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Mock webhook event construction
        mock_client_instance.construct_webhook_event.return_value = {
            "success": True,
            "data": {
                "type": "customer.subscription.updated",
                "data": {
                    "object": {
                        "id": "sub_test123",
                        "status": "active",
                        "current_period_start": int(datetime.now().timestamp()),
                        "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp())
                    }
                }
            }
        }
        
        # Mock webhook event handling
        mock_client_instance.handle_webhook_event.return_value = {
            "success": True,
            "subscription_id": "sub_test123"
        }
        
        billing_manager = BillingManager()
        
        # Create a test subscription
        subscription = Subscription(
            id="test_sub",
            tenant_id="test_tenant",
            plan_id="test_plan",
            status=SubscriptionStatus.ACTIVE,
            billing_period=BillingPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stripe_subscription_id="sub_test123"
        )
        billing_manager.subscriptions["test_sub"] = subscription
        
        # Test webhook handling
        payload = b"test_payload"
        sig_header = "test_signature"
        
        result = billing_manager.handle_stripe_webhook(payload, sig_header)
        
        assert result["success"] is True
        mock_client_instance.construct_webhook_event.assert_called_once()
        mock_client_instance.handle_webhook_event.assert_called_once()
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_handle_stripe_webhook_invalid_signature(self, mock_stripe_client, mock_stripe_config):
        """Test Stripe webhook handling with invalid signature."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        # Mock webhook event construction failure
        mock_client_instance.construct_webhook_event.return_value = {
            "success": False,
            "error": "Invalid signature"
        }
        
        billing_manager = BillingManager()
        
        payload = b"test_payload"
        sig_header = "invalid_signature"
        
        result = billing_manager.handle_stripe_webhook(payload, sig_header)
        
        assert result["success"] is False
        assert "Invalid signature" in result["error"]
        mock_client_instance.handle_webhook_event.assert_not_called()
    
    def test_get_subscription_by_stripe_id(self):
        """Test getting subscription by Stripe ID."""
        billing_manager = BillingManager()
        
        # Create test subscriptions
        subscription1 = Subscription(
            id="sub1",
            tenant_id="tenant1",
            plan_id="plan1",
            status=SubscriptionStatus.ACTIVE,
            billing_period=BillingPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stripe_subscription_id="stripe_sub1"
        )
        
        subscription2 = Subscription(
            id="sub2",
            tenant_id="tenant2",
            plan_id="plan2",
            status=SubscriptionStatus.ACTIVE,
            billing_period=BillingPeriod.MONTHLY,
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stripe_subscription_id="stripe_sub2"
        )
        
        billing_manager.subscriptions["sub1"] = subscription1
        billing_manager.subscriptions["sub2"] = subscription2
        
        # Test finding subscription
        found = billing_manager._get_subscription_by_stripe_id("stripe_sub1")
        assert found is not None
        assert found.id == "sub1"
        
        # Test not finding subscription
        not_found = billing_manager._get_subscription_by_stripe_id("stripe_sub3")
        assert not_found is None


class TestStripeIntegrationWithLocalBilling:
    """Test Stripe integration with local billing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.billing_manager = BillingManager(storage_path="test_data/billing")
    
    def test_local_billing_still_works_without_stripe(self):
        """Test that local billing functionality still works without Stripe."""
        # Use a clean test directory
        import shutil
        import os
        test_dir = "test_data/billing_clean"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        billing_manager = BillingManager(storage_path=test_dir)
        
        # Create a plan
        plan = billing_manager.create_plan(
            name="Test Plan",
            description="Test plan for testing",
            price_monthly=29.99,
            price_yearly=299.99,
            features=["feature1", "feature2"],
            limits={"max_agents": 10}
        )
        
        assert plan is not None
        assert plan.name == "Test Plan"
        
        # Create a subscription
        subscription = billing_manager.create_subscription(
            tenant_id="test_tenant",
            plan_id=plan.id,
            billing_period=BillingPeriod.MONTHLY
        )
        
        assert subscription is not None
        assert subscription.tenant_id == "test_tenant"
        assert subscription.plan_id == plan.id
        
        # Get subscription - use the same subscription object for comparison
        retrieved = billing_manager.get_subscription_by_tenant("test_tenant")
        assert retrieved is not None
        assert retrieved.tenant_id == subscription.tenant_id
        assert retrieved.plan_id == subscription.plan_id
        
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    @patch('bmad.core.enterprise.billing.STRIPE_AVAILABLE', True)
    @patch('bmad.core.enterprise.billing.StripeConfig')
    @patch('bmad.core.enterprise.billing.StripeClient')
    @patch('bmad.core.enterprise.multi_tenancy.tenant_manager')
    @patch.dict('os.environ', {'STRIPE_API_KEY': 'test_key'})
    def test_hybrid_billing_local_and_stripe(self, mock_tenant_manager, mock_stripe_client, mock_stripe_config):
        """Test that both local and Stripe billing work together."""
        # Mock Stripe client
        mock_client_instance = Mock()
        mock_stripe_client.return_value = mock_client_instance
        mock_client_instance.create_customer.return_value = {
            "success": False,
            "error": "tenant_manager not available"
        }
        
        # Mock Stripe config
        mock_config_instance = Mock()
        mock_stripe_config.return_value = mock_config_instance
        
        billing_manager = BillingManager()
        
        # Local billing should still work
        plan = billing_manager.create_plan(
            name="Test Plan",
            description="Test plan for testing",
            price_monthly=29.99,
            price_yearly=299.99,
            features=["feature1", "feature2"],
            limits={"max_agents": 10}
        )
        
        assert plan is not None
        
        # Stripe should also be available
        assert billing_manager.stripe_client is not None
        
        # Test Stripe method (should fail gracefully if not configured properly)
        result = billing_manager.create_stripe_customer("test_tenant", "test@example.com", "Test User")
        # This will fail because we're not mocking tenant_manager properly, but it should not crash
        assert isinstance(result, dict)
        assert result["success"] is False 