"""
Stripe Integration Client

Provides comprehensive Stripe integration for enterprise billing including:
- Payment method management
- Subscription billing
- Invoice generation
- Webhook handling
- Error handling and retry logic
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import stripe
from stripe.error import StripeError

logger = logging.getLogger(__name__)

@dataclass
class StripeConfig:
    """Configuration for Stripe integration."""
    api_key: str
    webhook_secret: Optional[str] = None
    api_version: str = "2023-10-16"
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class PaymentMethod:
    """Payment method information."""
    id: str
    type: str
    last4: Optional[str] = None
    brand: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False

@dataclass
class Subscription:
    """Subscription information."""
    id: str
    customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    plan_id: Optional[str] = None
    quantity: int = 1

@dataclass
class Invoice:
    """Invoice information."""
    id: str
    customer_id: str
    amount_due: int
    amount_paid: int
    status: str
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    invoice_pdf: Optional[str] = None

class StripeClient:
    """
    Comprehensive Stripe client for enterprise billing.
    """
    
    def __init__(self, config: StripeConfig):
        """Initialize Stripe client with configuration."""
        self.config = config
        stripe.api_key = config.api_key
        stripe.api_version = config.api_version
        
        logger.info("Stripe client initialized")
    
    def _handle_stripe_error(self, error: StripeError, operation: str) -> Dict[str, Any]:
        """Handle Stripe errors with retry logic."""
        logger.error(f"Stripe error in {operation}: {error}")
        
        if hasattr(error, 'code'):
            error_code = error.code
        else:
            error_code = 'unknown'
        
        return {
            "success": False,
            "error": str(error),
            "error_code": error_code,
            "operation": operation
        }
    
    def _retry_operation(self, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """Retry operation with exponential backoff."""
        for attempt in range(self.config.max_retries):
            try:
                return {"success": True, "data": operation_func(*args, **kwargs)}
            except StripeError as e:
                if attempt == self.config.max_retries - 1:
                    return self._handle_stripe_error(e, operation_func.__name__)
                
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"Stripe operation failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return {"success": False, "error": "Max retries exceeded"}
    
    # Customer Management
    def create_customer(self, email: str, name: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a new Stripe customer."""
        def _create():
            return stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
        
        return self._retry_operation(_create)
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information."""
        def _get():
            return stripe.Customer.retrieve(customer_id)
        
        return self._retry_operation(_get)
    
    def update_customer(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Update customer information."""
        def _update():
            return stripe.Customer.modify(customer_id, **kwargs)
        
        return self._retry_operation(_update)
    
    def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        """Delete a customer."""
        def _delete():
            return stripe.Customer.delete(customer_id)
        
        return self._retry_operation(_delete)
    
    # Payment Method Management
    def create_payment_method(self, customer_id: str, payment_method_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment method for a customer."""
        def _create():
            payment_method = stripe.PaymentMethod.create(
                type=payment_method_data.get('type', 'card'),
                card=payment_method_data.get('card', {}),
                billing_details=payment_method_data.get('billing_details', {})
            )
            
            # Attach to customer
            payment_method.attach(customer=customer_id)
            
            return payment_method
        
        return self._retry_operation(_create)
    
    def get_payment_methods(self, customer_id: str) -> Dict[str, Any]:
        """Get all payment methods for a customer."""
        def _get():
            return stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
        
        return self._retry_operation(_get)
    
    def set_default_payment_method(self, customer_id: str, payment_method_id: str) -> Dict[str, Any]:
        """Set default payment method for a customer."""
        def _set():
            return stripe.Customer.modify(
                customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
        
        return self._retry_operation(_set)
    
    def delete_payment_method(self, payment_method_id: str) -> Dict[str, Any]:
        """Delete a payment method."""
        def _delete():
            return stripe.PaymentMethod.detach(payment_method_id)
        
        return self._retry_operation(_delete)
    
    # Subscription Management
    def create_subscription(self, customer_id: str, price_id: str, quantity: int = 1, 
                          metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a subscription for a customer."""
        def _create():
            return stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id, 'quantity': quantity}],
                metadata=metadata or {},
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
        
        return self._retry_operation(_create)
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription information."""
        def _get():
            return stripe.Subscription.retrieve(subscription_id)
        
        return self._retry_operation(_get)
    
    def update_subscription(self, subscription_id: str, **kwargs) -> Dict[str, Any]:
        """Update subscription."""
        def _update():
            return stripe.Subscription.modify(subscription_id, **kwargs)
        
        return self._retry_operation(_update)
    
    def cancel_subscription(self, subscription_id: str, cancel_at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel a subscription."""
        def _cancel():
            if cancel_at_period_end:
                return stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                return stripe.Subscription.cancel(subscription_id)
        
        return self._retry_operation(_cancel)
    
    def get_subscriptions(self, customer_id: str) -> Dict[str, Any]:
        """Get all subscriptions for a customer."""
        def _get():
            return stripe.Subscription.list(customer=customer_id)
        
        return self._retry_operation(_get)
    
    # Invoice Management
    def create_invoice(self, customer_id: str, subscription_id: Optional[str] = None,
                      items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create an invoice."""
        def _create():
            invoice_data = {
                'customer': customer_id,
                'auto_advance': True
            }
            
            if subscription_id:
                invoice_data['subscription'] = subscription_id
            
            if items:
                invoice_data['invoice_items'] = items
            
            return stripe.Invoice.create(**invoice_data)
        
        return self._retry_operation(_create)
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice information."""
        def _get():
            return stripe.Invoice.retrieve(invoice_id)
        
        return self._retry_operation(_get)
    
    def finalize_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Finalize an invoice."""
        def _finalize():
            return stripe.Invoice.finalize_invoice(invoice_id)
        
        return self._retry_operation(_finalize)
    
    def pay_invoice(self, invoice_id: str, payment_method_id: Optional[str] = None) -> Dict[str, Any]:
        """Pay an invoice."""
        def _pay():
            payment_data = {}
            if payment_method_id:
                payment_data['payment_method'] = payment_method_id
            
            return stripe.Invoice.pay(invoice_id, **payment_data)
        
        return self._retry_operation(_pay)
    
    def get_invoices(self, customer_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get all invoices for a customer."""
        def _get():
            return stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
        
        return self._retry_operation(_get)
    
    # Price Management
    def create_price(self, product_id: str, unit_amount: int, currency: str = 'usd',
                    recurring: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a price for a product."""
        def _create():
            price_data = {
                'product': product_id,
                'unit_amount': unit_amount,
                'currency': currency
            }
            
            if recurring:
                price_data['recurring'] = recurring
            
            return stripe.Price.create(**price_data)
        
        return self._retry_operation(_create)
    
    def get_prices(self, product_id: Optional[str] = None, active: bool = True) -> Dict[str, Any]:
        """Get prices."""
        def _get():
            params = {'active': active}
            if product_id:
                params['product'] = product_id
            
            return stripe.Price.list(**params)
        
        return self._retry_operation(_get)
    
    # Product Management
    def create_product(self, name: str, description: Optional[str] = None,
                      metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a product."""
        def _create():
            product_data = {'name': name}
            
            if description:
                product_data['description'] = description
            
            if metadata:
                product_data['metadata'] = metadata
            
            return stripe.Product.create(**product_data)
        
        return self._retry_operation(_create)
    
    def get_products(self, active: bool = True) -> Dict[str, Any]:
        """Get products."""
        def _get():
            return stripe.Product.list(active=active)
        
        return self._retry_operation(_get)
    
    # Webhook Handling
    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Construct webhook event from payload."""
        try:
            if not self.config.webhook_secret:
                raise ValueError("Webhook secret not configured")
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.config.webhook_secret
            )
            
            return {"success": True, "data": event}
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return {"success": False, "error": str(e)}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook events."""
        event_type = event.get('type')
        logger.info(f"Processing webhook event: {event_type}")
        
        handlers = {
            'customer.subscription.created': self._handle_subscription_created,
            'customer.subscription.updated': self._handle_subscription_updated,
            'customer.subscription.deleted': self._handle_subscription_deleted,
            'invoice.payment_succeeded': self._handle_payment_succeeded,
            'invoice.payment_failed': self._handle_payment_failed,
            'payment_method.attached': self._handle_payment_method_attached,
            'payment_method.detached': self._handle_payment_method_detached
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event)
        else:
            logger.info(f"No handler for event type: {event_type}")
            return {"success": True, "message": "Event ignored"}
    
    def _handle_subscription_created(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created event."""
        subscription = event['data']['object']
        logger.info(f"Subscription created: {subscription['id']}")
        return {"success": True, "subscription_id": subscription['id']}
    
    def _handle_subscription_updated(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated event."""
        subscription = event['data']['object']
        logger.info(f"Subscription updated: {subscription['id']}")
        return {"success": True, "subscription_id": subscription['id']}
    
    def _handle_subscription_deleted(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted event."""
        subscription = event['data']['object']
        logger.info(f"Subscription deleted: {subscription['id']}")
        return {"success": True, "subscription_id": subscription['id']}
    
    def _handle_payment_succeeded(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded event."""
        invoice = event['data']['object']
        logger.info(f"Payment succeeded for invoice: {invoice['id']}")
        return {"success": True, "invoice_id": invoice['id']}
    
    def _handle_payment_failed(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed event."""
        invoice = event['data']['object']
        logger.warning(f"Payment failed for invoice: {invoice['id']}")
        return {"success": True, "invoice_id": invoice['id']}
    
    def _handle_payment_method_attached(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment method attached event."""
        payment_method = event['data']['object']
        logger.info(f"Payment method attached: {payment_method['id']}")
        return {"success": True, "payment_method_id": payment_method['id']}
    
    def _handle_payment_method_detached(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment method detached event."""
        payment_method = event['data']['object']
        logger.info(f"Payment method detached: {payment_method['id']}")
        return {"success": True, "payment_method_id": payment_method['id']}
    
    # Utility Methods
    def format_amount(self, amount: float, currency: str = 'usd') -> int:
        """Convert decimal amount to Stripe amount (cents)."""
        if currency.lower() in ['jpy', 'krw']:
            return int(amount)
        else:
            return int(amount * 100)
    
    def format_amount_from_stripe(self, amount: int, currency: str = 'usd') -> float:
        """Convert Stripe amount (cents) to decimal amount."""
        if currency.lower() in ['jpy', 'krw']:
            return float(amount)
        else:
            return float(amount) / 100
    
    def get_customer_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive customer summary."""
        customer_result = self.get_customer(customer_id)
        if not customer_result['success']:
            return customer_result
        
        subscriptions_result = self.get_subscriptions(customer_id)
        payment_methods_result = self.get_payment_methods(customer_id)
        invoices_result = self.get_invoices(customer_id)
        
        return {
            "success": True,
            "customer": customer_result['data'],
            "subscriptions": subscriptions_result.get('data', {}).get('data', []) if subscriptions_result['success'] else [],
            "payment_methods": payment_methods_result.get('data', {}).get('data', []) if payment_methods_result['success'] else [],
            "invoices": invoices_result.get('data', {}).get('data', []) if invoices_result['success'] else []
        } 