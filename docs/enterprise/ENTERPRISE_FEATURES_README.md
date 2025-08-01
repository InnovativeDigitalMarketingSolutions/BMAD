# Enterprise Features Documentation

## Overview

BMAD Enterprise Features provide a comprehensive suite of enterprise-grade capabilities for multi-tenant deployments, including user management, billing, access control, and security features.

## Table of Contents

1. [Multi-Tenancy](#multi-tenancy)
2. [User Management](#user-management)
3. [Billing & Subscriptions](#billing--subscriptions)
4. [Access Control](#access-control)
5. [Security](#security)
6. [CLI Usage](#cli-usage)
7. [API Reference](#api-reference)
8. [Configuration](#configuration)
9. [Deployment](#deployment)

## Multi-Tenancy

### Overview

Multi-tenancy support provides complete tenant isolation, allowing multiple organizations to use BMAD while maintaining data separation and security.

### Features

- **Tenant Isolation**: Complete data and resource isolation between tenants
- **Plan-based Limits**: Different resource limits based on subscription plans
- **Feature Flags**: Tenant-specific feature enablement
- **Domain-based Routing**: Automatic tenant identification by domain

### Usage

```python
from bmad.core.enterprise.multi_tenancy import tenant_manager

# Create a new tenant
tenant = tenant_manager.create_tenant(
    name="Acme Corporation",
    domain="acme.com",
    plan="professional"
)

# Set current tenant context
tenant_manager.set_current_tenant(tenant)

# Check feature availability
if tenant_manager.is_feature_enabled("advanced_analytics"):
    # Enable advanced analytics
    pass

# Check resource limits
if tenant_manager.check_limit("max_agents", current_agent_count):
    # Create new agent
    pass
```

### Tenant Plans

| Plan | Max Agents | Max Workflows | Storage | API Rate Limit | Features |
|------|------------|---------------|---------|----------------|----------|
| Basic | 5 | 10 | 1GB | 1,000/hr | Core agents, Basic workflows, Email support |
| Professional | 20 | 50 | 10GB | 5,000/hr | Core agents, Advanced workflows, Priority support, Analytics |
| Enterprise | 100 | 500 | 100GB | 50,000/hr | All agents, Custom workflows, Dedicated support, Advanced analytics, Custom integrations |

## User Management

### Overview

Comprehensive user management with role-based access control (RBAC), authentication, and permission management.

### Features

- **User Authentication**: Secure password-based authentication
- **Role-based Access Control**: Granular permission management
- **Tenant Association**: Users belong to specific tenants
- **User Lifecycle**: Complete user management from creation to deletion

### Usage

```python
from bmad.core.enterprise.user_management import user_manager, role_manager, permission_manager

# Create a user
user = user_manager.create_user(
    email="john.doe@acme.com",
    username="johndoe",
    first_name="John",
    last_name="Doe",
    tenant_id="tenant123",
    password="SecurePass123!"
)

# Create a role
role = role_manager.create_role(
    name="developer",
    description="Software developer role",
    permissions=["view_agents", "create_agents", "execute_agents"]
)

# Assign role to user
user_manager.update_user(user.id, role_ids=[role.id])

# Check permissions
if permission_manager.has_permission(user.id, "create_agents"):
    # Allow agent creation
    pass
```

### Default Roles

| Role | Permissions | Description |
|------|-------------|-------------|
| viewer | view_agents, view_workflows | Read-only access |
| user | view_agents, execute_agents, view_workflows, execute_workflows | Standard user access |
| admin | All permissions | Full system access |

## Billing & Subscriptions

### Overview

Complete billing and subscription management with usage tracking, plan management, and subscription lifecycle management.

### Features

- **Subscription Plans**: Flexible plan management
- **Usage Tracking**: Comprehensive usage monitoring
- **Billing Periods**: Monthly and yearly billing cycles
- **Usage Limits**: Automatic limit enforcement

### Usage

```python
from bmad.core.enterprise.billing import billing_manager, usage_tracker, subscription_manager

# Create a subscription
subscription = billing_manager.create_subscription(
    tenant_id="tenant123",
    plan_id="plan456",
    billing_period=BillingPeriod.MONTHLY
)

# Track usage
usage_tracker.record_usage("tenant123", "api_calls", 10)
usage_tracker.record_usage("tenant123", "agent_executions", 5)

# Check subscription status
status = subscription_manager.check_subscription_status("tenant123")
if status and status.status == SubscriptionStatus.ACTIVE:
    # Allow operations
    pass

# Check usage limits
if subscription_manager.check_usage_limits("tenant123", "max_agents", current_count):
    # Allow agent creation
    pass
```

### Usage Metrics

Common usage metrics that can be tracked:

- `api_calls`: API request count
- `agent_executions`: Agent execution count
- `workflow_executions`: Workflow execution count
- `storage_used`: Storage usage in MB
- `user_sessions`: Active user sessions

## Access Control

### Overview

Feature flags and access control rules provide granular control over feature availability and resource access.

### Features

- **Feature Flags**: Dynamic feature enablement/disablement
- **Access Rules**: Granular resource access control
- **Tenant Overrides**: Tenant-specific feature configurations
- **Condition-based Access**: Complex access control conditions

### Usage

```python
from bmad.core.enterprise.access_control import feature_flag_manager, access_control_manager

# Create a feature flag
flag = feature_flag_manager.create_feature_flag(
    name="beta_features",
    description="Enable beta features",
    flag_type=FeatureFlagType.BOOLEAN,
    default_value=False
)

# Set tenant-specific override
feature_flag_manager.set_tenant_override("beta_features", "tenant123", True)

# Check feature availability
if feature_flag_manager.get_flag_value("beta_features", "tenant123"):
    # Enable beta features
    pass

# Create access rule
rule = access_control_manager.create_access_rule(
    name="agent_creation",
    description="Allow agent creation",
    resource="agents",
    action="create",
    conditions={"min_role": "user", "subscription_required": True}
)

# Check access
if access_control_manager.check_access(
    user_id="user123",
    resource="agents",
    action="create",
    user_role="user",
    tenant_id="tenant123"
):
    # Allow agent creation
    pass
```

## Security

### Overview

Enterprise-grade security features including audit logging, security policies, and compliance monitoring.

### Features

- **Audit Logging**: Comprehensive activity logging
- **Security Policies**: Configurable security requirements
- **Compliance Monitoring**: Automated compliance checking
- **Password Policies**: Enforceable password requirements

### Usage

```python
from bmad.core.enterprise.security import enterprise_security_manager

# Log security events
enterprise_security_manager.log_audit_event(
    user_id="user123",
    tenant_id="tenant123",
    event_type=AuditEventType.LOGIN,
    resource="auth",
    action="login",
    details={"method": "password"},
    ip_address="192.168.1.1",
    success=True
)

# Validate password
result = enterprise_security_manager.validate_password("MyPassword123!")
if result["valid"]:
    # Password meets requirements
    pass
else:
    # Show validation errors
    for error in result["errors"]:
        print(f"Password error: {error}")

# Generate security report
report = enterprise_security_manager.generate_security_report(
    tenant_id="tenant123",
    start_date=datetime.utcnow() - timedelta(days=30)
)

# Check compliance
compliance = enterprise_security_manager.check_security_compliance("tenant123")
print(f"Compliance score: {compliance['compliance_score']}/100")
```

### Security Policies

Default security policies include:

- **Password Policy**: Minimum length, character requirements, expiration
- **Session Policy**: Timeout settings, concurrent session limits
- **Access Control Policy**: MFA requirements, login attempt limits
- **Data Protection Policy**: Encryption requirements, retention policies

## CLI Usage

### Installation

The Enterprise Features CLI is included with BMAD and can be accessed via:

```bash
python -m cli.enterprise_cli
```

### Common Commands

#### Tenant Management

```bash
# Create a tenant
python -m cli.enterprise_cli tenants create --name "Acme Corp" --domain "acme.com" --plan professional

# List tenants
python -m cli.enterprise_cli tenants list

# Update tenant
python -m cli.enterprise_cli tenants update <tenant_id> --plan enterprise
```

#### User Management

```bash
# Create a user
python -m cli.enterprise_cli users create --email "john@acme.com" --username "john" --first-name "John" --last-name "Doe" --tenant-id <tenant_id> --password "SecurePass123!"

# List users for tenant
python -m cli.enterprise_cli users list <tenant_id>

# Update user
python -m cli.enterprise_cli users update <user_id> --status active
```

#### Billing Management

```bash
# List plans
python -m cli.enterprise_cli billing plans

# Create subscription
python -m cli.enterprise_cli billing subscribe --tenant-id <tenant_id> --plan-id <plan_id> --period monthly

# Record usage
python -m cli.enterprise_cli billing record-usage --tenant-id <tenant_id> --metric api_calls --value 100
```

#### Feature Flags

```bash
# Create feature flag
python -m cli.enterprise_cli features create --name "beta_features" --description "Beta features" --type boolean --default-value false

# Get flag value
python -m cli.enterprise_cli features get beta_features --tenant-id <tenant_id>

# Set override
python -m cli.enterprise_cli features set-override beta_features --tenant-id <tenant_id> --value true
```

#### Security

```bash
# Validate password
python -m cli.enterprise_cli security validate-password --password "MyPassword123!"

# View audit logs
python -m cli.enterprise_cli security audit-logs --tenant-id <tenant_id> --days 30

# Generate security report
python -m cli.enterprise_cli security report --tenant-id <tenant_id> --days 30

# Check compliance
python -m cli.enterprise_cli security compliance --tenant-id <tenant_id>
```

## API Reference

### Multi-Tenancy API

#### TenantManager

```python
class TenantManager:
    def create_tenant(self, name: str, domain: str, plan: str = "basic") -> Tenant
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]
    def update_tenant(self, tenant_id: str, **kwargs) -> Optional[Tenant]
    def delete_tenant(self, tenant_id: str) -> bool
    def list_tenants(self) -> List[Tenant]
    def is_feature_enabled(self, feature: str) -> bool
    def check_limit(self, limit_name: str, current_usage: int) -> bool
```

#### Tenant

```python
@dataclass
class Tenant:
    id: str
    name: str
    domain: str
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    limits: Dict[str, Any]
    features: List[str]
```

### User Management API

#### UserManager

```python
class UserManager:
    def create_user(self, email: str, username: str, first_name: str, last_name: str,
                   tenant_id: str, password: str, role_ids: List[str] = None) -> User
    def get_user(self, user_id: str) -> Optional[User]
    def get_user_by_email(self, email: str) -> Optional[User]
    def authenticate_user(self, email: str, password: str) -> Optional[User]
    def update_user(self, user_id: str, **kwargs) -> Optional[User]
    def delete_user(self, user_id: str) -> bool
    def list_users_by_tenant(self, tenant_id: str) -> List[User]
```

#### PermissionManager

```python
class PermissionManager:
    def get_user_permissions(self, user_id: str) -> Set[str]
    def has_permission(self, user_id: str, permission: str) -> bool
    def has_any_permission(self, user_id: str, permissions: List[str]) -> bool
    def has_all_permissions(self, user_id: str, permissions: List[str]) -> bool
```

### Billing API

#### BillingManager

```python
class BillingManager:
    def create_plan(self, name: str, description: str, price_monthly: float,
                   price_yearly: float, features: List[str], limits: Dict[str, Any]) -> Plan
    def create_subscription(self, tenant_id: str, plan_id: str,
                          billing_period: BillingPeriod) -> Subscription
    def get_subscription_by_tenant(self, tenant_id: str) -> Optional[Subscription]
    def cancel_subscription(self, subscription_id: str) -> bool
```

#### UsageTracker

```python
class UsageTracker:
    def record_usage(self, tenant_id: str, metric: str, value: int = 1)
    def get_usage(self, tenant_id: str, metric: str, period_start: datetime,
                 period_end: datetime) -> int
    def get_current_month_usage(self, tenant_id: str, metric: str) -> int
```

### Access Control API

#### FeatureFlagManager

```python
class FeatureFlagManager:
    def create_feature_flag(self, name: str, description: str, flag_type: FeatureFlagType,
                          default_value: Any) -> FeatureFlag
    def get_flag_value(self, flag_name: str, tenant_id: str = None) -> Any
    def set_tenant_override(self, flag_name: str, tenant_id: str, value: Any) -> bool
    def remove_tenant_override(self, flag_name: str, tenant_id: str) -> bool
```

#### AccessControlManager

```python
class AccessControlManager:
    def create_access_rule(self, name: str, description: str, resource: str,
                          action: str, conditions: Dict[str, Any]) -> AccessRule
    def check_access(self, user_id: str, resource: str, action: str,
                    user_role: str = None, tenant_id: str = None) -> bool
```

### Security API

#### EnterpriseSecurityManager

```python
class EnterpriseSecurityManager:
    def create_security_policy(self, name: str, description: str, policy_type: str,
                             rules: Dict[str, Any], security_level: SecurityLevel) -> SecurityPolicy
    def validate_password(self, password: str) -> Dict[str, Any]
    def log_audit_event(self, user_id: str, tenant_id: str, event_type: AuditEventType,
                       resource: str, action: str, details: Dict[str, Any],
                       ip_address: str = None, user_agent: str = None, success: bool = True)
    def get_audit_logs(self, user_id: str = None, tenant_id: str = None,
                      event_type: AuditEventType = None, start_date: datetime = None,
                      end_date: datetime = None, limit: int = 100) -> List[AuditLog]
    def generate_security_report(self, tenant_id: str = None, start_date: datetime = None,
                               end_date: datetime = None) -> Dict[str, Any]
    def check_security_compliance(self, tenant_id: str) -> Dict[str, Any]
```

## Configuration

### Environment Variables

```bash
# Storage paths
BMAD_ENTERPRISE_STORAGE_PATH=/path/to/enterprise/data

# Security settings
BMAD_SECURITY_AUDIT_LOG_RETENTION_DAYS=2555
BMAD_SECURITY_PASSWORD_MIN_LENGTH=8
BMAD_SECURITY_SESSION_TIMEOUT_MINUTES=30

# Billing settings
BMAD_BILLING_DEFAULT_PLAN=basic
BMAD_BILLING_USAGE_TRACKING_ENABLED=true
```

### Configuration Files

Enterprise features can be configured via JSON configuration files:

```json
{
  "multi_tenancy": {
    "storage_path": "data/tenants",
    "default_plan": "basic"
  },
  "user_management": {
    "storage_path": "data/users",
    "password_policy": {
      "min_length": 8,
      "require_uppercase": true,
      "require_lowercase": true,
      "require_numbers": true,
      "require_special_chars": true
    }
  },
  "billing": {
    "storage_path": "data/billing",
    "usage_tracking": {
      "enabled": true,
      "retention_days": 2555
    }
  },
  "security": {
    "storage_path": "data/security",
    "audit_logging": {
      "enabled": true,
      "retention_days": 2555
    }
  }
}
```

## Deployment

### Prerequisites

- Python 3.8+
- BMAD core system
- Storage directory with write permissions

### Installation

1. **Install BMAD with Enterprise Features**:
   ```bash
   pip install bmad[enterprise]
   ```

2. **Initialize Enterprise Features**:
   ```bash
   python -m bmad.core.enterprise
   ```

3. **Create Initial Configuration**:
   ```bash
   python -m cli.enterprise_cli tenants create --name "Default Tenant" --domain "default.com" --plan enterprise
   ```

### Production Deployment

1. **Database Setup** (Optional):
   - Configure external database for production use
   - Set up database migrations
   - Configure connection pooling

2. **Security Configuration**:
   - Enable HTTPS
   - Configure firewall rules
   - Set up monitoring and alerting

3. **Backup Configuration**:
   - Set up automated backups
   - Configure disaster recovery procedures
   - Test backup and restore procedures

4. **Monitoring Setup**:
   - Configure application monitoring
   - Set up log aggregation
   - Configure alerting for security events

### Scaling Considerations

- **Horizontal Scaling**: Enterprise features support horizontal scaling
- **Load Balancing**: Use load balancers for high availability
- **Caching**: Implement caching for frequently accessed data
- **Database Optimization**: Optimize database queries and indexes

## Support

For enterprise features support:

1. **Documentation**: Check this documentation first
2. **CLI Help**: Use `python -m cli.enterprise_cli --help`
3. **Logs**: Check application logs for detailed error information
4. **Community**: Join the BMAD community for support

## License

Enterprise features are part of the BMAD project and follow the same licensing terms. 