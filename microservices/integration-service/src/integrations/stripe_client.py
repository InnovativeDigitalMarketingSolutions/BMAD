"""
Stripe Integration Client

This module provides the Stripe client for the Integration Service,
handling payment processing, billing, and subscription management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import stripe
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class PaymentIntent(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    client_secret: str
    created: int

class Customer(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created: int
    subscription: Optional[str] = None

class Subscription(BaseModel):
    id: str
    customer_id: str
    status: str
    current_period_start: int
    current_period_end: int
    plan_id: str

class StripeClient:
    """Stripe client for payment processing and billing."""
    
    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        stripe.api_key = api_key
        self.client = stripe
        
    async def create_payment_intent(self, amount: int, currency: str = "usd", 
                                  customer_id: Optional[str] = None) -> Optional[PaymentIntent]:
        """Create a payment intent."""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency
            }
            
            if customer_id:
                intent_data["customer"] = customer_id
                
            intent = stripe.PaymentIntent.create(**intent_data)
            
            return PaymentIntent(
                id=intent.id,
                amount=intent.amount,
                currency=intent.currency,
                status=intent.status,
                client_secret=intent.client_secret,
                created=intent.created
            )
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            return None
            
    async def confirm_payment_intent(self, payment_intent_id: str) -> Optional[PaymentIntent]:
        """Confirm a payment intent."""
        try:
            intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            return PaymentIntent(
                id=intent.id,
                amount=intent.amount,
                currency=intent.currency,
                status=intent.status,
                client_secret=intent.client_secret,
                created=intent.created
            )
        except Exception as e:
            logger.error(f"Failed to confirm payment intent {payment_intent_id}: {e}")
            return None
            
    async def get_payment_intent(self, payment_intent_id: str) -> Optional[PaymentIntent]:
        """Get payment intent by ID."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return PaymentIntent(
                id=intent.id,
                amount=intent.amount,
                currency=intent.currency,
                status=intent.status,
                client_secret=intent.client_secret,
                created=intent.created
            )
        except Exception as e:
            logger.error(f"Failed to get payment intent {payment_intent_id}: {e}")
            return None
            
    async def create_customer(self, email: str, name: Optional[str] = None) -> Optional[Customer]:
        """Create a new customer."""
        try:
            customer_data = {"email": email}
            if name:
                customer_data["name"] = name
                
            customer = stripe.Customer.create(**customer_data)
            
            return Customer(
                id=customer.id,
                email=customer.email,
                name=customer.name,
                created=customer.created,
                subscription=None
            )
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return None
            
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            
            # Get subscription if exists
            subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)
            subscription_id = subscriptions.data[0].id if subscriptions.data else None
            
            return Customer(
                id=customer.id,
                email=customer.email,
                name=customer.name,
                created=customer.created,
                subscription=subscription_id
            )
        except Exception as e:
            logger.error(f"Failed to get customer {customer_id}: {e}")
            return None
            
    async def update_customer(self, customer_id: str, **kwargs) -> Optional[Customer]:
        """Update customer."""
        try:
            customer = stripe.Customer.modify(customer_id, **kwargs)
            
            return Customer(
                id=customer.id,
                email=customer.email,
                name=customer.name,
                created=customer.created,
                subscription=None
            )
        except Exception as e:
            logger.error(f"Failed to update customer {customer_id}: {e}")
            return None
            
    async def delete_customer(self, customer_id: str) -> bool:
        """Delete customer."""
        try:
            stripe.Customer.delete(customer_id)
            logger.info(f"Customer deleted: {customer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete customer {customer_id}: {e}")
            return False
            
    async def create_subscription(self, customer_id: str, price_id: str) -> Optional[Subscription]:
        """Create a subscription."""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}]
            )
            
            return Subscription(
                id=subscription.id,
                customer_id=subscription.customer,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                plan_id=subscription.items.data[0].price.id
            )
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return None
            
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return Subscription(
                id=subscription.id,
                customer_id=subscription.customer,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                plan_id=subscription.items.data[0].price.id
            )
        except Exception as e:
            logger.error(f"Failed to get subscription {subscription_id}: {e}")
            return None
            
    async def cancel_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Cancel a subscription."""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            return Subscription(
                id=subscription.id,
                customer_id=subscription.customer,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                plan_id=subscription.items.data[0].price.id
            )
        except Exception as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            return None
            
    async def list_customers(self, limit: int = 100) -> List[Customer]:
        """List customers."""
        try:
            customers = stripe.Customer.list(limit=limit)
            
            result = []
            for customer in customers.data:
                result.append(Customer(
                    id=customer.id,
                    email=customer.email,
                    name=customer.name,
                    created=customer.created,
                    subscription=None
                ))
                
            return result
        except Exception as e:
            logger.error(f"Failed to list customers: {e}")
            return []
            
    async def list_subscriptions(self, customer_id: Optional[str] = None, limit: int = 100) -> List[Subscription]:
        """List subscriptions."""
        try:
            params = {"limit": limit}
            if customer_id:
                params["customer"] = customer_id
                
            subscriptions = stripe.Subscription.list(**params)
            
            result = []
            for subscription in subscriptions.data:
                result.append(Subscription(
                    id=subscription.id,
                    customer_id=subscription.customer,
                    status=subscription.status,
                    current_period_start=subscription.current_period_start,
                    current_period_end=subscription.current_period_end,
                    plan_id=subscription.items.data[0].price.id
                ))
                
            return result
        except Exception as e:
            logger.error(f"Failed to list subscriptions: {e}")
            return []
            
    async def get_billing_stats(self) -> Dict[str, Any]:
        """Get billing statistics."""
        try:
            # Get customer count
            customers = stripe.Customer.list(limit=1)
            total_customers = customers.total_count
            
            # Get subscription count
            subscriptions = stripe.Subscription.list(limit=1)
            total_subscriptions = subscriptions.total_count
            
            # Get revenue (last 30 days)
            thirty_days_ago = int((datetime.now().timestamp() - 30 * 24 * 60 * 60))
            charges = stripe.Charge.list(
                created={"gte": thirty_days_ago},
                limit=1
            )
            total_revenue = sum(charge.amount for charge in charges.data)
            
            return {
                "total_customers": total_customers,
                "total_subscriptions": total_subscriptions,
                "revenue_30_days": total_revenue / 100,  # Convert from cents
                "currency": "usd"
            }
        except Exception as e:
            logger.error(f"Failed to get billing stats: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Check Stripe service health."""
        try:
            # Test API connection by listing customers
            customers = stripe.Customer.list(limit=1)
            
            # Get billing stats
            stats = await self.get_billing_stats()
            
            return {
                "status": "healthy",
                "api_key_configured": bool(self.api_key),
                "webhook_secret_configured": bool(self.webhook_secret),
                "billing_stats": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_key_configured": bool(self.api_key),
                "webhook_secret_configured": bool(self.webhook_secret)
            } 