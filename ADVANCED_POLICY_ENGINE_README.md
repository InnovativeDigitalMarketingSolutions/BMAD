# BMAD Advanced Policy Engine

## 📋 Overview

De **Advanced Policy Engine** is een uitgebreide uitbreiding van de basis OPA integratie die complexe policy conditions, inheritance, composition, dynamic updates, en versioning ondersteunt. Deze engine biedt enterprise-grade policy management voor BMAD agents en workflows.

## 🚀 Features

### **🔐 Complex Policy Conditions**
- **Time-based Conditions**: Business hours, day-of-week, hour-of-day restrictions
- **Resource-based Conditions**: CPU, memory, API call limits
- **Role-based Conditions**: User role validation en access control
- **Context-based Conditions**: Dynamic context evaluation
- **Composite Conditions**: AND/OR/NOT logic voor complexe rules
- **Inheritance Conditions**: Policy inheritance en overrides
- **Dynamic Conditions**: Runtime condition evaluation

### **📚 Policy Management**
- **Policy Versioning**: Complete version history en rollback
- **Policy Inheritance**: Parent-child policy relationships
- **Policy Composition**: Multi-policy evaluation
- **Dynamic Updates**: Runtime policy modifications
- **Policy Status Management**: Active, inactive, draft, deprecated states
- **Policy Expiration**: Time-based policy expiration

### **🎯 Advanced Evaluation**
- **Priority-based Evaluation**: Rule priority ordering
- **Condition Tracking**: Detailed condition success/failure tracking
- **Severity Levels**: Low, Medium, High, Critical severity
- **Metadata Support**: Rich policy metadata en tagging
- **Audit Trail**: Complete evaluation history

## 🏗️ Architecture

### **Core Components**

```python
# Policy Definition Structure
PolicyDefinition:
├── policy_id: str
├── policy_name: str
├── policy_type: PolicyType
├── version: str
├── rules: List[PolicyRule]
├── parent_policy: Optional[str]
├── inheritance_rules: Dict[str, Any]
├── status: PolicyStatus
├── created_at: datetime
├── updated_at: datetime
├── expires_at: Optional[datetime]
└── metadata: Dict[str, Any]

# Policy Rule Structure
PolicyRule:
├── rule_id: str
├── rule_name: str
├── policy_type: PolicyType
├── conditions: List[PolicyCondition]
├── actions: List[str]
├── priority: int
├── enabled: bool
├── description: str
└── metadata: Dict[str, Any]

# Policy Condition Structure
PolicyCondition:
├── condition_id: str
├── condition_type: str
├── parameters: Dict[str, Any]
├── description: str
├── severity: PolicySeverity
└── enabled: bool
```

### **Policy Types**
- `ACCESS_CONTROL`: Access control policies
- `RESOURCE_LIMITS`: Resource usage policies
- `SECURITY_POLICIES`: Security en compliance policies
- `WORKFLOW_POLICIES`: Workflow execution policies
- `BEHAVIOR_RULES`: Agent behavior policies
- `COMPOSITE_POLICY`: Multi-condition policies
- `INHERITED_POLICY`: Inherited policies
- `DYNAMIC_POLICY`: Runtime policies

### **Condition Types**
- `time_based`: Time window en schedule conditions
- `resource_based`: System resource conditions
- `role_based`: User role conditions
- `context_based`: Context value conditions
- `composite`: Multi-condition logic
- `inheritance`: Policy inheritance conditions
- `dynamic`: Runtime dynamic conditions

## 🛠️ Quick Start

### **1. Basic Usage**

```python
from bmad.agents.core.advanced_policy_engine import get_advanced_policy_engine

# Get the engine instance
engine = get_advanced_policy_engine()

# Evaluate a policy
from bmad.agents.core.opa_policy_engine import PolicyRequest

request = PolicyRequest(
    subject="user123",
    action="read",
    resource="document",
    context={
        "user_roles": ["admin"],
        "time": "2024-01-01T12:00:00",
        "cpu_usage": 45.2,
        "memory_usage": 67.8
    }
)

result = await engine.evaluate_policy("advanced_access_control", request)
print(f"Allowed: {result.allowed}")
print(f"Reason: {result.reason}")
```

### **2. Creating Custom Policies**

```python
# Create a custom policy
policy_data = {
    "policy_id": "custom_policy",
    "policy_name": "Custom Access Policy",
    "policy_type": "access_control",
    "version": "1.0.0",
    "rules": [
        {
            "rule_id": "custom_rule",
            "rule_name": "Custom Access Rule",
            "policy_type": "access_control",
            "priority": 100,
            "conditions": [
                {
                    "condition_id": "time_check",
                    "condition_type": "time_based",
                    "parameters": {
                        "time_window": {
                            "start": "09:00:00",
                            "end": "17:00:00"
                        }
                    },
                    "description": "Business hours only",
                    "severity": "medium",
                    "enabled": True
                }
            ],
            "actions": ["allow"],
            "description": "Custom access rule"
        }
    ],
    "status": "active"
}

policy = engine.create_policy(policy_data)
```

### **3. Policy Inheritance**

```python
# Create a child policy that inherits from parent
child_policy = {
    "policy_id": "child_policy",
    "policy_name": "Child Policy",
    "policy_type": "access_control",
    "version": "1.0.0",
    "parent_policy": "advanced_access_control",  # Inherit from parent
    "rules": [
        # Additional rules specific to child
    ],
    "status": "active"
}

# Evaluate with inheritance
result = await engine.evaluate_inherited_policy("child_policy", request)
```

## 📊 CLI Usage

### **List Policies**
```bash
python3 advanced_policy_cli.py list-policies
python3 advanced_policy_cli.py list-policies --type access_control
```

### **Show Policy Details**
```bash
python3 advanced_policy_cli.py show-policy advanced_access_control
```

### **Evaluate Policy**
```bash
# Create request template first
python3 advanced_policy_cli.py create-request-template my_request

# Edit the template file (my_request.json)
# Then evaluate
python3 advanced_policy_cli.py evaluate-policy advanced_access_control my_request.json
```

### **Create Policy from File**
```bash
# Create policy template
python3 advanced_policy_cli.py create-policy-template my_policy

# Edit the template file (my_policy.json)
# Then create the policy
python3 advanced_policy_cli.py create-policy my_policy.json
```

### **Update Policy**
```bash
# Create updates file
echo '{"version": "2.0.0", "status": "active"}' > updates.json

# Update policy
python3 advanced_policy_cli.py update-policy policy_id updates.json "Updated version"
```

### **Policy Versioning**
```bash
# Show policy versions
python3 advanced_policy_cli.py show-versions policy_id

# Rollback to specific version
python3 advanced_policy_cli.py rollback-policy policy_id 1.0.0
```

## 🔧 Integration with BMAD

### **Integrated Workflow Orchestrator**

De Advanced Policy Engine is volledig geïntegreerd in de `IntegratedWorkflowOrchestrator`:

```python
from bmad.agents.core.integrated_workflow_orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Advanced policy evaluation is automatically applied during workflow execution
result = await orchestrator.execute_integrated_workflow(
    workflow_name="product-development",
    context={"user_roles": ["admin"]},
    integration_level="full"
)
```

### **Agent Configuration**

Agents kunnen geconfigureerd worden met specifieke policy rules:

```python
# Agent config with advanced policies
config = AgentWorkflowConfig(
    agent_name="product-owner",
    integration_level=IntegrationLevel.FULL,
    policy_rules=["access_control", "resource_limits", "workflow_policies"]
)
```

### **Policy Enforcement**

De engine wordt automatisch gebruikt voor:
- **Workflow Policy Enforcement**: Bij workflow execution
- **Task Policy Enforcement**: Bij individuele task execution
- **Agent Policy Enforcement**: Bij agent operations

## 📋 Default Policies

### **1. Advanced Access Control Policy**
- **Policy ID**: `advanced_access_control`
- **Type**: Access Control
- **Features**:
  - Time-based access (business hours)
  - Role-based access control
  - Priority: 200

### **2. Advanced Resource Management Policy**
- **Policy ID**: `advanced_resource_management`
- **Type**: Resource Limits
- **Features**:
  - CPU usage threshold (80%)
  - Memory usage threshold (85%)
  - API calls limit (1000)
  - Priority: 150

### **3. Composite Security Policy**
- **Policy ID**: `composite_security_policy`
- **Type**: Composite Policy
- **Features**:
  - Multi-factor security check
  - Role + time combination
  - Priority: 300

## 🔍 Condition Evaluators

### **Time-based Conditions**
```python
# Business hours
{
    "condition_type": "time_based",
    "parameters": {
        "time_window": {
            "start": "09:00:00",
            "end": "17:00:00"
        },
        "day_of_week": [0, 1, 2, 3, 4]  # Monday to Friday
    }
}
```

### **Resource-based Conditions**
```python
# CPU threshold
{
    "condition_type": "resource_based",
    "parameters": {
        "cpu_threshold": 80
    }
}

# Memory threshold
{
    "condition_type": "resource_based",
    "parameters": {
        "memory_threshold": 85
    }
}

# API calls limit
{
    "condition_type": "resource_based",
    "parameters": {
        "api_calls_limit": 1000
    }
}
```

### **Role-based Conditions**
```python
{
    "condition_type": "role_based",
    "parameters": {
        "required_roles": ["admin", "manager", "developer"]
    }
}
```

### **Composite Conditions**
```python
{
    "condition_type": "composite",
    "parameters": {
        "operator": "AND",
        "conditions": [
            {
                "condition_type": "role_based",
                "parameters": {"required_roles": ["admin"]}
            },
            {
                "condition_type": "time_based",
                "parameters": {"time_window": {"start": "00:00:00", "end": "23:59:59"}}
            }
        ]
    }
}
```

## 📈 Performance & Monitoring

### **Policy Evaluation Metrics**
- **Evaluation Time**: Per policy en rule
- **Condition Success Rate**: Per condition type
- **Policy Hit Rate**: Policy usage statistics
- **Version Usage**: Policy version distribution

### **Integration with Performance Monitor**
```python
# Get policy performance metrics
performance_data = orchestrator.get_performance_metrics(workflow_id)
policy_metrics = performance_data.get("policy_metrics", {})
```

## 🔧 Configuration

### **Environment Variables**
```bash
# OPA Server URL (for basic policies)
OPA_URL=http://localhost:8181

# Policy storage directory
POLICIES_DIR=policies

# Policy evaluation timeout
POLICY_EVALUATION_TIMEOUT=30
```

### **Policy Storage**
Policies worden opgeslagen in JSON formaat in de `policies/` directory:
```
policies/
├── advanced_access_control.json
├── advanced_resource_management.json
├── composite_security_policy.json
└── custom_policies/
    ├── custom_policy_1.json
    └── custom_policy_2.json
```

## 🚀 Advanced Features

### **Dynamic Policy Updates**
```python
# Add policy update callback
def policy_update_handler(policy_id: str, updates: Dict[str, Any]):
    print(f"Policy {policy_id} updated: {updates}")

engine.add_policy_update_callback(policy_update_handler)
```

### **Policy Rollback**
```python
# Rollback to previous version
policy = engine.rollback_policy("policy_id", "1.0.0")
```

### **Composite Policy Evaluation**
```python
# Evaluate multiple policies
results = await engine.evaluate_composite_policy(
    ["policy1", "policy2", "policy3"], 
    request
)
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Policy Not Found**
   ```
   ❌ Policy 'policy_id' not found
   ```
   **Solution**: Check if policy exists with `list-policies`

2. **Invalid Condition Parameters**
   ```
   ❌ Invalid time format in condition condition_id
   ```
   **Solution**: Verify time format (HH:MM:SS or ISO format)

3. **Policy Evaluation Failed**
   ```
   ❌ Advanced policy evaluation failed for policy_id
   ```
   **Solution**: Check policy definition and condition parameters

### **Debug Mode**
```python
import logging
logging.getLogger("bmad.agents.core.advanced_policy_engine").setLevel(logging.DEBUG)
```

## 📚 Examples

### **Complete Policy Example**
```json
{
    "policy_id": "enterprise_access_policy",
    "policy_name": "Enterprise Access Control",
    "policy_type": "access_control",
    "version": "1.0.0",
    "rules": [
        {
            "rule_id": "business_hours_access",
            "rule_name": "Business Hours Access",
            "policy_type": "access_control",
            "priority": 200,
            "conditions": [
                {
                    "condition_id": "time_window",
                    "condition_type": "time_based",
                    "parameters": {
                        "time_window": {
                            "start": "08:00:00",
                            "end": "18:00:00"
                        },
                        "day_of_week": [0, 1, 2, 3, 4]
                    },
                    "description": "Business hours access",
                    "severity": "medium",
                    "enabled": true
                },
                {
                    "condition_id": "role_check",
                    "condition_type": "role_based",
                    "parameters": {
                        "required_roles": ["employee", "manager", "admin"]
                    },
                    "description": "Valid role required",
                    "severity": "high",
                    "enabled": true
                }
            ],
            "actions": ["allow"],
            "description": "Allow access during business hours for valid roles"
        }
    ],
    "status": "active",
    "metadata": {
        "category": "security",
        "tags": ["access_control", "business_hours", "role_based"]
    }
}
```

### **Request Example**
```json
{
    "subject": "user123",
    "action": "read",
    "resource": "document",
    "context": {
        "user_roles": ["employee"],
        "time": "2024-01-01T14:30:00",
        "ip_address": "192.168.1.100",
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "api_calls_count": 150
    }
}
```

## 🔮 Future Enhancements

### **Planned Features**
- **Policy Templates**: Reusable policy templates
- **Policy Analytics**: Advanced policy usage analytics
- **Policy Testing**: Automated policy testing framework
- **Policy Migration**: Policy migration tools
- **Policy Compliance**: Compliance reporting en auditing
- **Policy Optimization**: Automatic policy optimization

### **Integration Roadmap**
- **GraphQL API**: Policy management API
- **Web UI**: Visual policy editor
- **Policy Marketplace**: Shared policy library
- **Real-time Updates**: WebSocket policy updates
- **Policy ML**: Machine learning policy optimization

## 📞 Support

Voor vragen en ondersteuning:
- **Documentation**: Zie de BMAD main README
- **Issues**: GitHub issues
- **Examples**: Zie de `examples/` directory
- **CLI Help**: `python3 advanced_policy_cli.py --help`

---

**Advanced Policy Engine** - Enterprise-grade policy management voor BMAD agents en workflows 🚀 