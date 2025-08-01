"""
Billing and Subscription Management Module

Provides billing integration, subscription management, and usage tracking
for enterprise BMAD deployments.
"""

import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Subscription status enumeration."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIAL = "trial"


class BillingPeriod(Enum):
    """Billing period enumeration."""
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Plan:
    """Represents a subscription plan."""
    id: str
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    features: List[str]
    limits: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """Create plan from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class Subscription:
    """Represents a subscription."""
    id: str
    tenant_id: str
    plan_id: str
    status: SubscriptionStatus
    billing_period: BillingPeriod
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary."""
        data = asdict(self)
        data['current_period_start'] = self.current_period_start.isoformat()
        data['current_period_end'] = self.current_period_end.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['status'] = self.status.value
        data['billing_period'] = self.billing_period.value
        if self.cancelled_at:
            data['cancelled_at'] = self.cancelled_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create subscription from dictionary."""
        data['current_period_start'] = datetime.fromisoformat(data['current_period_start'])
        data['current_period_end'] = datetime.fromisoformat(data['current_period_end'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['status'] = SubscriptionStatus(data['status'])
        data['billing_period'] = BillingPeriod(data['billing_period'])
        if data.get('cancelled_at'):
            data['cancelled_at'] = datetime.fromisoformat(data['cancelled_at'])
        return cls(**data)


@dataclass
class UsageRecord:
    """Represents a usage record."""
    id: str
    tenant_id: str
    metric: str
    value: int
    timestamp: datetime
    period_start: datetime
    period_end: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert usage record to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['period_start'] = self.period_start.isoformat()
        data['period_end'] = self.period_end.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageRecord':
        """Create usage record from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['period_start'] = datetime.fromisoformat(data['period_start'])
        data['period_end'] = datetime.fromisoformat(data['period_end'])
        return cls(**data)


class BillingManager:
    """Manages billing operations."""
    
    def __init__(self, storage_path: str = "data/billing"):
        self.storage_path = storage_path
        self.plans: Dict[str, Plan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self._load_data()
        self._create_default_plans()
    
    def _load_data(self):
        """Load billing data from storage."""
        try:
            import os
            from pathlib import Path
            
            # Load plans
            plans_file = Path(self.storage_path) / "plans.json"
            if plans_file.exists():
                with open(plans_file, 'r') as f:
                    data = json.load(f)
                    for plan_data in data.values():
                        plan = Plan.from_dict(plan_data)
                        self.plans[plan.id] = plan
            
            # Load subscriptions
            subscriptions_file = Path(self.storage_path) / "subscriptions.json"
            if subscriptions_file.exists():
                with open(subscriptions_file, 'r') as f:
                    data = json.load(f)
                    for sub_data in data.values():
                        subscription = Subscription.from_dict(sub_data)
                        self.subscriptions[subscription.id] = subscription
                        
            logger.info(f"Loaded {len(self.plans)} plans and {len(self.subscriptions)} subscriptions")
        except Exception as e:
            logger.warning(f"Could not load billing data: {e}")
    
    def _save_data(self):
        """Save billing data to storage."""
        try:
            import os
            from pathlib import Path
            
            # Save plans
            plans_file = Path(self.storage_path) / "plans.json"
            plans_file.parent.mkdir(parents=True, exist_ok=True)
            plans_data = {pid: plan.to_dict() for pid, plan in self.plans.items()}
            with open(plans_file, 'w') as f:
                json.dump(plans_data, f, indent=2)
            
            # Save subscriptions
            subscriptions_file = Path(self.storage_path) / "subscriptions.json"
            subscriptions_data = {sid: sub.to_dict() for sid, sub in self.subscriptions.items()}
            with open(subscriptions_file, 'w') as f:
                json.dump(subscriptions_data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save billing data: {e}")
    
    def _create_default_plans(self):
        """Create default plans if they don't exist."""
        if not self.plans:
            now = datetime.utcnow()
            
            # Basic plan
            basic_plan = Plan(
                id=str(uuid.uuid4()),
                name="Basic",
                description="Perfect for small teams and startups",
                price_monthly=29.99,
                price_yearly=299.99,
                features=["core_agents", "basic_workflows", "email_support"],
                limits={
                    "max_agents": 5,
                    "max_workflows": 10,
                    "storage_limit_gb": 1,
                    "api_rate_limit": 1000
                },
                created_at=now,
                updated_at=now
            )
            
            # Professional plan
            pro_plan = Plan(
                id=str(uuid.uuid4()),
                name="Professional",
                description="Ideal for growing businesses",
                price_monthly=99.99,
                price_yearly=999.99,
                features=["core_agents", "advanced_workflows", "priority_support", "analytics"],
                limits={
                    "max_agents": 20,
                    "max_workflows": 50,
                    "storage_limit_gb": 10,
                    "api_rate_limit": 5000
                },
                created_at=now,
                updated_at=now
            )
            
            # Enterprise plan
            enterprise_plan = Plan(
                id=str(uuid.uuid4()),
                name="Enterprise",
                description="For large organizations with custom needs",
                price_monthly=299.99,
                price_yearly=2999.99,
                features=["all_agents", "custom_workflows", "dedicated_support", "advanced_analytics", "custom_integrations"],
                limits={
                    "max_agents": 100,
                    "max_workflows": 500,
                    "storage_limit_gb": 100,
                    "api_rate_limit": 50000
                },
                created_at=now,
                updated_at=now
            )
            
            self.plans[basic_plan.id] = basic_plan
            self.plans[pro_plan.id] = pro_plan
            self.plans[enterprise_plan.id] = enterprise_plan
            self._save_data()
    
    def create_plan(self, name: str, description: str, price_monthly: float,
                   price_yearly: float, features: List[str], limits: Dict[str, Any]) -> Plan:
        """Create a new plan."""
        plan_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        plan = Plan(
            id=plan_id,
            name=name,
            description=description,
            price_monthly=price_monthly,
            price_yearly=price_yearly,
            features=features,
            limits=limits,
            created_at=now,
            updated_at=now
        )
        
        self.plans[plan_id] = plan
        self._save_data()
        logger.info(f"Created plan: {name} ({plan_id})")
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID."""
        return self.plans.get(plan_id)
    
    def list_plans(self) -> List[Plan]:
        """List all active plans."""
        return [plan for plan in self.plans.values() if plan.is_active]
    
    def create_subscription(self, tenant_id: str, plan_id: str,
                          billing_period: BillingPeriod) -> Subscription:
        """Create a new subscription."""
        subscription_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Calculate period dates
        if billing_period == BillingPeriod.MONTHLY:
            period_end = now + timedelta(days=30)
        else:
            period_end = now + timedelta(days=365)
        
        subscription = Subscription(
            id=subscription_id,
            tenant_id=tenant_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            billing_period=billing_period,
            current_period_start=now,
            current_period_end=period_end,
            created_at=now,
            updated_at=now
        )
        
        self.subscriptions[subscription_id] = subscription
        self._save_data()
        logger.info(f"Created subscription: {subscription_id} for tenant {tenant_id}")
        return subscription
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)
    
    def get_subscription_by_tenant(self, tenant_id: str) -> Optional[Subscription]:
        """Get active subscription for tenant."""
        for subscription in self.subscriptions.values():
            if (subscription.tenant_id == tenant_id and 
                subscription.status == SubscriptionStatus.ACTIVE):
                return subscription
        return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        subscription.updated_at = datetime.utcnow()
        self._save_data()
        logger.info(f"Cancelled subscription: {subscription_id}")
        return True


class UsageTracker:
    """Tracks usage metrics for billing."""
    
    def __init__(self, storage_path: str = "data/usage"):
        self.storage_path = storage_path
        self.usage_records: List[UsageRecord] = []
        self._load_usage()
    
    def _load_usage(self):
        """Load usage records from storage."""
        try:
            import os
            from pathlib import Path
            
            usage_file = Path(self.storage_path) / "usage.json"
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    data = json.load(f)
                    for record_data in data:
                        record = UsageRecord.from_dict(record_data)
                        self.usage_records.append(record)
                logger.info(f"Loaded {len(self.usage_records)} usage records")
        except Exception as e:
            logger.warning(f"Could not load usage records: {e}")
    
    def _save_usage(self):
        """Save usage records to storage."""
        try:
            import os
            from pathlib import Path
            
            usage_file = Path(self.storage_path) / "usage.json"
            usage_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = [record.to_dict() for record in self.usage_records]
            with open(usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save usage records: {e}")
    
    def record_usage(self, tenant_id: str, metric: str, value: int = 1):
        """Record usage for a tenant."""
        now = datetime.utcnow()
        
        # Create period boundaries (monthly)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            period_end = now.replace(year=now.year + 1, month=1, day=1)
        else:
            period_end = now.replace(month=now.month + 1, day=1)
        
        record = UsageRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            metric=metric,
            value=value,
            timestamp=now,
            period_start=period_start,
            period_end=period_end
        )
        
        self.usage_records.append(record)
        self._save_usage()
        logger.debug(f"Recorded usage: {metric}={value} for tenant {tenant_id}")
    
    def get_usage(self, tenant_id: str, metric: str, period_start: datetime,
                 period_end: datetime) -> int:
        """Get usage for a tenant and metric in a period."""
        total = 0
        for record in self.usage_records:
            if (record.tenant_id == tenant_id and 
                record.metric == metric and
                record.timestamp >= period_start and
                record.timestamp <= period_end):
                total += record.value
        return total
    
    def get_current_month_usage(self, tenant_id: str, metric: str) -> int:
        """Get current month usage for a tenant and metric."""
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.get_usage(tenant_id, metric, period_start, now)


class SubscriptionManager:
    """Manages subscription operations."""
    
    def __init__(self, billing_manager: BillingManager, usage_tracker: UsageTracker):
        self.billing_manager = billing_manager
        self.usage_tracker = usage_tracker
    
    def check_subscription_status(self, tenant_id: str) -> Optional[Subscription]:
        """Check subscription status for a tenant."""
        subscription = self.billing_manager.get_subscription_by_tenant(tenant_id)
        if not subscription:
            return None
        
        # Check if subscription is expired
        if subscription.current_period_end < datetime.utcnow():
            subscription.status = SubscriptionStatus.PAST_DUE
            subscription.updated_at = datetime.utcnow()
            self.billing_manager._save_data()
        
        return subscription
    
    def check_usage_limits(self, tenant_id: str, metric: str, current_usage: int) -> bool:
        """Check if tenant is within usage limits."""
        subscription = self.check_subscription_status(tenant_id)
        if not subscription:
            return False
        
        plan = self.billing_manager.get_plan(subscription.plan_id)
        if not plan:
            return False
        
        limit = plan.limits.get(metric)
        if limit is None:
            return True
        
        return current_usage <= limit
    
    def can_use_feature(self, tenant_id: str, feature: str) -> bool:
        """Check if tenant can use a specific feature."""
        subscription = self.check_subscription_status(tenant_id)
        if not subscription:
            return False
        
        plan = self.billing_manager.get_plan(subscription.plan_id)
        if not plan:
            return False
        
        return feature in plan.features


# Global instances
billing_manager = BillingManager()
usage_tracker = UsageTracker()
subscription_manager = SubscriptionManager(billing_manager, usage_tracker) 