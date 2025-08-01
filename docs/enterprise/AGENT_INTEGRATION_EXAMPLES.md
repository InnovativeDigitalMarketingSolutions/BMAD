# Enterprise Features Agent Integration Examples

This document shows how to integrate enterprise features into BMAD agents using the provided decorators and utilities.

## Overview

The enterprise features integration provides:
- **Class Decorators**: Automatically add enterprise context to agent classes
- **Method Decorators**: Add permission checks, feature flag validation, and usage tracking
- **Context Managers**: Manage enterprise context for specific operations
- **Utility Functions**: Helper functions for enterprise operations

## Basic Agent Integration

### Using the @enterprise_agent Decorator

```python
from bmad.core.enterprise import enterprise_agent, enterprise_method

@enterprise_agent
class MyAgent:
    def __init__(self, **kwargs):
        # The decorator automatically extracts tenant_id and user_id from kwargs
        self.agent_name = "MyAgent"
        # ... other initialization code
    
    @enterprise_method(
        permission="execute_agents",
        feature_flag="agent_myagent",
        usage_metric="agent_executions"
    )
    def execute_task(self, task_data):
        """Execute a task with enterprise features enabled."""
        # This method automatically:
        # - Checks if user has 'execute_agents' permission
        # - Verifies 'agent_myagent' feature flag is enabled
        # - Tracks usage for billing
        # - Logs all events for audit
        
        result = self._process_task(task_data)
        return result
    
    def _process_task(self, task_data):
        # Your actual task processing logic
        return {"status": "completed", "data": task_data}
```

### Using Individual Decorators

```python
from bmad.core.enterprise import enterprise_required, enterprise_method

class AnotherAgent:
    def __init__(self, tenant_id=None, user_id=None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.agent_name = "AnotherAgent"
    
    @enterprise_required(permission="view_analytics")
    def get_analytics(self):
        """Get analytics data - requires view_analytics permission."""
        return {"analytics": "data"}
    
    @enterprise_method(
        permission="execute_workflows",
        feature_flag="workflow_orchestration"
    )
    def start_workflow(self, workflow_name):
        """Start a workflow with enterprise checks."""
        return {"workflow": workflow_name, "status": "started"}
```

## Advanced Integration Patterns

### Context Manager Usage

```python
from bmad.core.enterprise import enterprise_context, track_enterprise_usage

class WorkflowAgent:
    def execute_complex_workflow(self, tenant_id, user_id, workflow_data):
        with enterprise_context(tenant_id, user_id):
            # All operations within this context use the specified tenant/user
            
            # Track usage manually
            track_enterprise_usage("complex_workflows", 1)
            
            # Execute workflow steps
            step1_result = self._execute_step_1(workflow_data)
            step2_result = self._execute_step_2(step1_result)
            
            return {"workflow_complete": True, "results": [step1_result, step2_result]}
```

### Utility Functions

```python
from bmad.core.enterprise import (
    check_enterprise_feature,
    check_enterprise_permission,
    log_enterprise_event
)

class SecurityAgent:
    def perform_security_scan(self, scan_type):
        # Check if security scanning is enabled for the tenant
        if not check_enterprise_feature("security_scanning"):
            raise ValueError("Security scanning not enabled for this tenant")
        
        # Check if user has permission
        if not check_enterprise_permission("perform_security_scan"):
            raise ValueError("Insufficient permissions for security scanning")
        
        # Log the scan attempt
        log_enterprise_event(
            "security_scan",
            "security",
            "scan_start",
            {"scan_type": scan_type}
        )
        
        # Perform the scan
        scan_result = self._run_security_scan(scan_type)
        
        # Log completion
        log_enterprise_event(
            "security_scan",
            "security",
            "scan_complete",
            {"scan_type": scan_type, "result": scan_result}
        )
        
        return scan_result
```

## Real-World Agent Examples

### Product Owner Agent with Enterprise Features

```python
from bmad.core.enterprise import enterprise_agent, enterprise_method

@enterprise_agent
class ProductOwnerAgent:
    def __init__(self, **kwargs):
        self.agent_name = "ProductOwner"
        # ... initialization code
    
    @enterprise_method(
        permission="create_user_stories",
        feature_flag="product_management",
        usage_metric="user_stories_created"
    )
    def create_user_story(self, story_data):
        """Create a user story with enterprise validation."""
        # Validate story data
        validated_data = self._validate_story_data(story_data)
        
        # Create the story
        story = self._create_story(validated_data)
        
        # Track story creation
        self._track_enterprise_usage("user_stories_created")
        
        return story
    
    @enterprise_method(
        permission="view_product_backlog",
        feature_flag="product_management"
    )
    def get_backlog(self):
        """Get product backlog - requires view permission."""
        return self._retrieve_backlog()
    
    @enterprise_method(
        permission="prioritize_backlog",
        feature_flag="advanced_product_management"
    )
    def prioritize_backlog(self, priorities):
        """Prioritize backlog items - requires advanced features."""
        return self._update_priorities(priorities)
```

### Test Engineer Agent with Enterprise Features

```python
from bmad.core.enterprise import enterprise_agent, enterprise_method

@enterprise_agent
class TestEngineerAgent:
    def __init__(self, **kwargs):
        self.agent_name = "TestEngineer"
        # ... initialization code
    
    @enterprise_method(
        permission="run_tests",
        feature_flag="automated_testing",
        usage_metric="test_executions"
    )
    def run_test_suite(self, test_suite):
        """Run a test suite with enterprise tracking."""
        # Check test limits
        if not self._check_enterprise_limits("test_execution"):
            raise ValueError("Test execution limit exceeded")
        
        # Run tests
        results = self._execute_tests(test_suite)
        
        # Track usage
        self._track_enterprise_usage("test_executions", len(results))
        
        return results
    
    @enterprise_method(
        permission="view_test_reports",
        feature_flag="test_analytics"
    )
    def generate_test_report(self, test_results):
        """Generate test report with analytics."""
        return self._create_report(test_results)
    
    @enterprise_method(
        permission="manage_test_data",
        feature_flag="test_data_management"
    )
    def setup_test_data(self, data_config):
        """Setup test data with enterprise validation."""
        return self._configure_test_data(data_config)
```

### DevOps Agent with Enterprise Features

```python
from bmad.core.enterprise import enterprise_agent, enterprise_method

@enterprise_agent
class DevOpsAgent:
    def __init__(self, **kwargs):
        self.agent_name = "DevOps"
        # ... initialization code
    
    @enterprise_method(
        permission="deploy_to_production",
        feature_flag="production_deployment",
        usage_metric="deployments"
    )
    def deploy_to_production(self, deployment_config):
        """Deploy to production with enterprise security."""
        # Log deployment attempt
        self._log_enterprise_event(
            "deployment",
            "infrastructure",
            "deploy_start",
            {"environment": "production", "config": deployment_config}
        )
        
        # Perform deployment
        result = self._execute_deployment(deployment_config)
        
        # Track deployment
        self._track_enterprise_usage("deployments")
        
        return result
    
    @enterprise_method(
        permission="view_infrastructure",
        feature_flag="infrastructure_monitoring"
    )
    def get_infrastructure_status(self):
        """Get infrastructure status."""
        return self._get_status()
    
    @enterprise_method(
        permission="scale_infrastructure",
        feature_flag="auto_scaling"
    )
    def scale_infrastructure(self, scaling_config):
        """Scale infrastructure with enterprise limits."""
        # Check scaling limits
        if not self._check_enterprise_limits("infrastructure_scaling"):
            raise ValueError("Infrastructure scaling limit exceeded")
        
        return self._execute_scaling(scaling_config)
```

## Integration with Existing Agents

### Adding Enterprise Features to Existing Agents

For existing agents, you can add enterprise features incrementally:

```python
# Existing agent
class ExistingAgent:
    def __init__(self):
        self.agent_name = "ExistingAgent"
    
    def some_method(self):
        return "result"

# Add enterprise features
from bmad.core.enterprise import enterprise_method

class ExistingAgent:
    def __init__(self, tenant_id=None, user_id=None):
        self.agent_name = "ExistingAgent"
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    @enterprise_method(permission="execute_agents")
    def some_method(self):
        return "result"
```

### Conditional Enterprise Features

```python
from bmad.core.enterprise import check_enterprise_feature, enterprise_context

class HybridAgent:
    def execute_with_enterprise(self, tenant_id, user_id, data):
        # Check if enterprise features are available
        if tenant_id and user_id and check_enterprise_feature("agent_enterprise"):
            # Use enterprise context
            with enterprise_context(tenant_id, user_id):
                return self._execute_enterprise(data)
        else:
            # Fall back to basic execution
            return self._execute_basic(data)
```

## Best Practices

### 1. Always Check Permissions

```python
@enterprise_method(permission="specific_permission")
def sensitive_operation(self):
    # This ensures only authorized users can execute this method
    pass
```

### 2. Use Feature Flags for New Features

```python
@enterprise_method(feature_flag="new_feature")
def new_feature_method(self):
    # This ensures the feature is enabled for the tenant
    pass
```

### 3. Track Usage for Billing

```python
@enterprise_method(usage_metric="expensive_operation")
def expensive_operation(self):
    # This tracks usage for billing purposes
    pass
```

### 4. Log Important Events

```python
def important_operation(self):
    self._log_enterprise_event(
        "important_operation",
        "agent",
        "operation_start",
        {"details": "operation details"}
    )
    
    # ... perform operation ...
    
    self._log_enterprise_event(
        "important_operation",
        "agent",
        "operation_complete",
        {"result": "success"}
    )
```

### 5. Handle Enterprise Context Gracefully

```python
def method_with_optional_enterprise(self):
    if hasattr(self, 'tenant_id') and self.tenant_id:
        # Enterprise features available
        self._track_enterprise_usage("method_calls")
        self._log_enterprise_event("method_call", "agent", "execute", {})
    
    # Execute method regardless
    return self._execute_method()
```

## Testing Enterprise Integration

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

def test_enterprise_agent_initialization():
    with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
        mock_tenant.get_tenant.return_value = Mock()
        
        agent = MyAgent(tenant_id="test_tenant", user_id="test_user")
        
        assert agent.tenant_id == "test_tenant"
        assert agent.user_id == "test_user"

def test_enterprise_method_permission_check():
    with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
        mock_permission.has_permission.return_value = False
        
        agent = MyAgent(tenant_id="test_tenant", user_id="test_user")
        
        with pytest.raises(ValueError, match="Permission.*required"):
            agent.execute_task({})
```

### Integration Tests

```python
def test_enterprise_workflow_integration():
    # Test complete workflow with enterprise features
    agent = MyAgent(tenant_id="test_tenant", user_id="test_user")
    
    # Mock enterprise services
    with patch('bmad.core.enterprise.agent_integration.usage_tracker') as mock_usage:
        with patch('bmad.core.enterprise.agent_integration.enterprise_security_manager') as mock_security:
            result = agent.execute_task({"test": "data"})
            
            # Verify usage was tracked
            mock_usage.record_usage.assert_called()
            
            # Verify events were logged
            mock_security.log_audit_event.assert_called()
            
            assert result is not None
```

## Migration Guide

### From Basic Agents to Enterprise Agents

1. **Add the decorator**:
   ```python
   # Before
   class MyAgent:
       pass
   
   # After
   @enterprise_agent
   class MyAgent:
       pass
   ```

2. **Update initialization**:
   ```python
   # Before
   agent = MyAgent()
   
   # After
   agent = MyAgent(tenant_id="tenant123", user_id="user456")
   ```

3. **Add method decorators**:
   ```python
   # Before
   def execute_task(self):
       pass
   
   # After
   @enterprise_method(permission="execute_agents")
   def execute_task(self):
       pass
   ```

4. **Update tests**:
   ```python
   # Before
   def test_agent():
       agent = MyAgent()
       result = agent.execute_task()
   
   # After
   def test_agent():
       agent = MyAgent(tenant_id="test", user_id="test")
       result = agent.execute_task()
   ```

This integration approach ensures that all BMAD agents can benefit from enterprise features while maintaining backward compatibility and providing a clear migration path. 