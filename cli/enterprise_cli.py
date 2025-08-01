"""
Enterprise Features CLI

Provides command-line interface for managing enterprise features including:
- Multi-tenancy management
- User management
- Billing and subscriptions
- Access control
- Security management
"""

import click
import json
import sys
from datetime import datetime, timedelta
from typing import Optional

from bmad.core.enterprise.multi_tenancy import tenant_manager
from bmad.core.enterprise.user_management import user_manager, role_manager, permission_manager
from bmad.core.enterprise.billing import billing_manager, usage_tracker, subscription_manager
from bmad.core.enterprise.access_control import feature_flag_manager, access_control_manager
from bmad.core.enterprise.security import enterprise_security_manager


@click.group()
def enterprise():
    """Enterprise Features Management CLI."""
    pass


# Multi-Tenancy Commands
@enterprise.group()
def tenants():
    """Manage tenants."""
    pass


@tenants.command()
@click.option('--name', required=True, help='Tenant name')
@click.option('--domain', required=True, help='Tenant domain')
@click.option('--plan', default='basic', type=click.Choice(['basic', 'professional', 'enterprise']), help='Subscription plan')
def create(name, domain, plan):
    """Create a new tenant."""
    try:
        tenant = tenant_manager.create_tenant(name=name, domain=domain, plan=plan)
        click.echo(f"✅ Tenant created successfully!")
        click.echo(f"   ID: {tenant.id}")
        click.echo(f"   Name: {tenant.name}")
        click.echo(f"   Domain: {tenant.domain}")
        click.echo(f"   Plan: {tenant.plan}")
        click.echo(f"   Status: {tenant.status}")
    except Exception as e:
        click.echo(f"❌ Error creating tenant: {e}", err=True)
        sys.exit(1)


@tenants.command()
def list():
    """List all tenants."""
    try:
        tenants = tenant_manager.list_tenants()
        if not tenants:
            click.echo("No tenants found.")
            return
        
        click.echo(f"Found {len(tenants)} tenants:")
        click.echo()
        
        for tenant in tenants:
            click.echo(f"  {tenant.id}")
            click.echo(f"    Name: {tenant.name}")
            click.echo(f"    Domain: {tenant.domain}")
            click.echo(f"    Plan: {tenant.plan}")
            click.echo(f"    Status: {tenant.status}")
            click.echo(f"    Created: {tenant.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error listing tenants: {e}", err=True)
        sys.exit(1)


@tenants.command()
@click.argument('tenant_id')
@click.option('--name', help='New tenant name')
@click.option('--plan', type=click.Choice(['basic', 'professional', 'enterprise']), help='New subscription plan')
@click.option('--status', type=click.Choice(['active', 'inactive', 'suspended']), help='New status')
def update(tenant_id, name, plan, status):
    """Update tenant properties."""
    try:
        updates = {}
        if name:
            updates['name'] = name
        if plan:
            updates['plan'] = plan
        if status:
            updates['status'] = status
        
        if not updates:
            click.echo("No updates specified.")
            return
        
        tenant = tenant_manager.update_tenant(tenant_id, **updates)
        if tenant:
            click.echo(f"✅ Tenant updated successfully!")
            click.echo(f"   ID: {tenant.id}")
            click.echo(f"   Name: {tenant.name}")
            click.echo(f"   Plan: {tenant.plan}")
            click.echo(f"   Status: {tenant.status}")
        else:
            click.echo(f"❌ Tenant not found: {tenant_id}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error updating tenant: {e}", err=True)
        sys.exit(1)


# User Management Commands
@enterprise.group()
def users():
    """Manage users."""
    pass


@users.command()
@click.option('--email', required=True, help='User email')
@click.option('--username', required=True, help='Username')
@click.option('--first-name', required=True, help='First name')
@click.option('--last-name', required=True, help='Last name')
@click.option('--tenant-id', required=True, help='Tenant ID')
@click.option('--password', required=True, help='Password')
@click.option('--role-ids', help='Comma-separated role IDs')
def create(email, username, first_name, last_name, tenant_id, password, role_ids):
    """Create a new user."""
    try:
        role_id_list = role_ids.split(',') if role_ids else []
        user = user_manager.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            tenant_id=tenant_id,
            password=password,
            role_ids=role_id_list
        )
        click.echo(f"✅ User created successfully!")
        click.echo(f"   ID: {user.id}")
        click.echo(f"   Email: {user.email}")
        click.echo(f"   Username: {user.username}")
        click.echo(f"   Status: {user.status.value}")
    except Exception as e:
        click.echo(f"❌ Error creating user: {e}", err=True)
        sys.exit(1)


@users.command()
@click.argument('tenant_id')
def list(tenant_id):
    """List users for a tenant."""
    try:
        users = user_manager.list_users_by_tenant(tenant_id)
        if not users:
            click.echo(f"No users found for tenant {tenant_id}.")
            return
        
        click.echo(f"Found {len(users)} users for tenant {tenant_id}:")
        click.echo()
        
        for user in users:
            click.echo(f"  {user.id}")
            click.echo(f"    Email: {user.email}")
            click.echo(f"    Username: {user.username}")
            click.echo(f"    Name: {user.first_name} {user.last_name}")
            click.echo(f"    Status: {user.status.value}")
            click.echo(f"    Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error listing users: {e}", err=True)
        sys.exit(1)


@users.command()
@click.argument('user_id')
@click.option('--status', type=click.Choice(['active', 'inactive', 'suspended', 'pending']), help='New status')
@click.option('--role-ids', help='Comma-separated role IDs')
def update(user_id, status, role_ids):
    """Update user properties."""
    try:
        updates = {}
        if status:
            updates['status'] = status
        if role_ids:
            updates['role_ids'] = role_ids.split(',')
        
        if not updates:
            click.echo("No updates specified.")
            return
        
        user = user_manager.update_user(user_id, **updates)
        if user:
            click.echo(f"✅ User updated successfully!")
            click.echo(f"   ID: {user.id}")
            click.echo(f"   Email: {user.email}")
            click.echo(f"   Status: {user.status.value}")
        else:
            click.echo(f"❌ User not found: {user_id}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error updating user: {e}", err=True)
        sys.exit(1)


# Role Management Commands
@enterprise.group()
def roles():
    """Manage roles."""
    pass


@roles.command()
@click.option('--name', required=True, help='Role name')
@click.option('--description', required=True, help='Role description')
@click.option('--permissions', required=True, help='Comma-separated permissions')
def create(name, description, permissions):
    """Create a new role."""
    try:
        permission_list = permissions.split(',')
        role = role_manager.create_role(
            name=name,
            description=description,
            permissions=permission_list
        )
        click.echo(f"✅ Role created successfully!")
        click.echo(f"   ID: {role.id}")
        click.echo(f"   Name: {role.name}")
        click.echo(f"   Description: {role.description}")
        click.echo(f"   Permissions: {', '.join(role.permissions)}")
    except Exception as e:
        click.echo(f"❌ Error creating role: {e}", err=True)
        sys.exit(1)


@roles.command()
def list():
    """List all roles."""
    try:
        roles = role_manager.list_roles()
        if not roles:
            click.echo("No roles found.")
            return
        
        click.echo(f"Found {len(roles)} roles:")
        click.echo()
        
        for role in roles:
            click.echo(f"  {role.id}")
            click.echo(f"    Name: {role.name}")
            click.echo(f"    Description: {role.description}")
            click.echo(f"    Permissions: {', '.join(role.permissions)}")
            click.echo(f"    System: {role.is_system}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error listing roles: {e}", err=True)
        sys.exit(1)


# Billing Commands
@enterprise.group()
def billing():
    """Manage billing and subscriptions."""
    pass


@billing.command()
def plans():
    """List available plans."""
    try:
        plans = billing_manager.list_plans()
        if not plans:
            click.echo("No plans found.")
            return
        
        click.echo(f"Found {len(plans)} plans:")
        click.echo()
        
        for plan in plans:
            click.echo(f"  {plan.id}")
            click.echo(f"    Name: {plan.name}")
            click.echo(f"    Description: {plan.description}")
            click.echo(f"    Monthly Price: ${plan.price_monthly}")
            click.echo(f"    Yearly Price: ${plan.price_yearly}")
            click.echo(f"    Features: {', '.join(plan.features)}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error listing plans: {e}", err=True)
        sys.exit(1)


@billing.command()
@click.option('--tenant-id', required=True, help='Tenant ID')
@click.option('--plan-id', required=True, help='Plan ID')
@click.option('--period', default='monthly', type=click.Choice(['monthly', 'yearly']), help='Billing period')
def subscribe(tenant_id, plan_id, period):
    """Create a subscription for a tenant."""
    try:
        billing_period = subscription_manager.billing_manager.BillingPeriod.MONTHLY if period == 'monthly' else subscription_manager.billing_manager.BillingPeriod.YEARLY
        
        subscription = billing_manager.create_subscription(
            tenant_id=tenant_id,
            plan_id=plan_id,
            billing_period=billing_period
        )
        click.echo(f"✅ Subscription created successfully!")
        click.echo(f"   ID: {subscription.id}")
        click.echo(f"   Tenant: {subscription.tenant_id}")
        click.echo(f"   Plan: {subscription.plan_id}")
        click.echo(f"   Status: {subscription.status.value}")
        click.echo(f"   Period: {subscription.billing_period.value}")
    except Exception as e:
        click.echo(f"❌ Error creating subscription: {e}", err=True)
        sys.exit(1)


@billing.command()
@click.option('--tenant-id', required=True, help='Tenant ID')
@click.option('--metric', required=True, help='Usage metric')
@click.option('--value', required=True, type=int, help='Usage value')
def record_usage(tenant_id, metric, value):
    """Record usage for a tenant."""
    try:
        usage_tracker.record_usage(tenant_id, metric, value)
        click.echo(f"✅ Usage recorded successfully!")
        click.echo(f"   Tenant: {tenant_id}")
        click.echo(f"   Metric: {metric}")
        click.echo(f"   Value: {value}")
    except Exception as e:
        click.echo(f"❌ Error recording usage: {e}", err=True)
        sys.exit(1)


# Feature Flags Commands
@enterprise.group()
def features():
    """Manage feature flags."""
    pass


@features.command()
@click.option('--name', required=True, help='Feature flag name')
@click.option('--description', required=True, help='Feature flag description')
@click.option('--type', required=True, type=click.Choice(['boolean', 'string', 'number', 'json']), help='Flag type')
@click.option('--default-value', required=True, help='Default value')
def create(name, description, type, default_value):
    """Create a new feature flag."""
    try:
        flag_type = getattr(feature_flag_manager.FeatureFlagType, type.upper())
        
        # Parse default value based on type
        if type == 'boolean':
            parsed_value = default_value.lower() == 'true'
        elif type == 'number':
            parsed_value = float(default_value)
        elif type == 'json':
            parsed_value = json.loads(default_value)
        else:
            parsed_value = default_value
        
        flag = feature_flag_manager.create_feature_flag(
            name=name,
            description=description,
            flag_type=flag_type,
            default_value=parsed_value
        )
        click.echo(f"✅ Feature flag created successfully!")
        click.echo(f"   ID: {flag.id}")
        click.echo(f"   Name: {flag.name}")
        click.echo(f"   Type: {flag.flag_type.value}")
        click.echo(f"   Default Value: {flag.default_value}")
    except Exception as e:
        click.echo(f"❌ Error creating feature flag: {e}", err=True)
        sys.exit(1)


@features.command()
@click.argument('flag_name')
@click.option('--tenant-id', help='Tenant ID for override')
def get(flag_name, tenant_id):
    """Get feature flag value."""
    try:
        value = feature_flag_manager.get_flag_value(flag_name, tenant_id)
        click.echo(f"Feature flag: {flag_name}")
        click.echo(f"Value: {value}")
        if tenant_id:
            click.echo(f"Tenant: {tenant_id}")
    except Exception as e:
        click.echo(f"❌ Error getting feature flag: {e}", err=True)
        sys.exit(1)


@features.command()
@click.argument('flag_name')
@click.option('--tenant-id', required=True, help='Tenant ID')
@click.option('--value', required=True, help='Override value')
def set_override(flag_name, tenant_id, value):
    """Set tenant-specific override for a feature flag."""
    try:
        success = feature_flag_manager.set_tenant_override(flag_name, tenant_id, value)
        if success:
            click.echo(f"✅ Override set successfully!")
            click.echo(f"   Flag: {flag_name}")
            click.echo(f"   Tenant: {tenant_id}")
            click.echo(f"   Value: {value}")
        else:
            click.echo(f"❌ Feature flag not found: {flag_name}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error setting override: {e}", err=True)
        sys.exit(1)


# Security Commands
@enterprise.group()
def security():
    """Manage security features."""
    pass


@security.command()
@click.option('--password', required=True, help='Password to validate')
def validate_password(password):
    """Validate password against security policy."""
    try:
        result = enterprise_security_manager.validate_password(password)
        if result["valid"]:
            click.echo(f"✅ Password is valid!")
            click.echo(f"   Policy Level: {result['policy_level']}")
        else:
            click.echo(f"❌ Password is invalid!")
            click.echo(f"   Policy Level: {result['policy_level']}")
            click.echo(f"   Errors:")
            for error in result["errors"]:
                click.echo(f"     - {error}")
    except Exception as e:
        click.echo(f"❌ Error validating password: {e}", err=True)
        sys.exit(1)


@security.command()
@click.option('--tenant-id', help='Tenant ID for filtering')
@click.option('--days', default=30, type=int, help='Number of days to look back')
def audit_logs(tenant_id, days):
    """View audit logs."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        logs = enterprise_security_manager.get_audit_logs(
            tenant_id=tenant_id,
            start_date=start_date,
            limit=50
        )
        
        if not logs:
            click.echo("No audit logs found.")
            return
        
        click.echo(f"Found {len(logs)} audit logs:")
        click.echo()
        
        for log in logs:
            click.echo(f"  {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"    User: {log.user_id}")
            click.echo(f"    Event: {log.event_type.value}")
            click.echo(f"    Resource: {log.resource}")
            click.echo(f"    Action: {log.action}")
            click.echo(f"    Success: {log.success}")
            if log.ip_address:
                click.echo(f"    IP: {log.ip_address}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error viewing audit logs: {e}", err=True)
        sys.exit(1)


@security.command()
@click.option('--tenant-id', help='Tenant ID for report')
@click.option('--days', default=30, type=int, help='Number of days for report')
def report(tenant_id, days):
    """Generate security report."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        report = enterprise_security_manager.generate_security_report(
            tenant_id=tenant_id,
            start_date=start_date
        )
        
        click.echo(f"Security Report")
        click.echo(f"==============")
        click.echo(f"Period: {report['report_period']['start_date']} to {report['report_period']['end_date']}")
        click.echo(f"Tenant: {report['tenant_id'] or 'All'}")
        click.echo()
        click.echo(f"Summary:")
        click.echo(f"  Total Events: {report['summary']['total_events']}")
        click.echo(f"  Unique Users: {report['summary']['unique_users']}")
        click.echo(f"  Security Violations: {report['summary']['security_violations']}")
        click.echo()
        
        if report['event_breakdown']:
            click.echo(f"Event Breakdown:")
            for event_type, count in report['event_breakdown'].items():
                click.echo(f"  {event_type}: {count}")
            click.echo()
        
        if report['security_violations']:
            click.echo(f"Security Violations:")
            for violation in report['security_violations'][:5]:  # Show first 5
                click.echo(f"  {violation['timestamp']} - {violation['user_id']} - {violation['action']}")
            click.echo()
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}", err=True)
        sys.exit(1)


@security.command()
@click.option('--tenant-id', required=True, help='Tenant ID')
def compliance(tenant_id):
    """Check security compliance for a tenant."""
    try:
        compliance = enterprise_security_manager.check_security_compliance(tenant_id)
        
        click.echo(f"Security Compliance Report")
        click.echo(f"========================")
        click.echo(f"Tenant: {compliance['tenant_id']}")
        click.echo(f"Assessment Date: {compliance['assessment_date']}")
        click.echo(f"Compliance Score: {compliance['compliance_score']}/100")
        click.echo()
        click.echo(f"Metrics:")
        click.echo(f"  Security Violations: {compliance['security_violations']}")
        click.echo(f"  Failed Login Rate: {compliance['failed_login_rate']:.2%}")
        click.echo(f"  Total Access Events: {compliance['total_access_events']}")
        click.echo()
        click.echo(f"Recommendations:")
        for recommendation in compliance['recommendations']:
            click.echo(f"  - {recommendation}")
    except Exception as e:
        click.echo(f"❌ Error checking compliance: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    enterprise() 