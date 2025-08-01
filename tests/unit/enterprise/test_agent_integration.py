"""
Tests for Enterprise Features Agent Integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from typing import Dict, Any

from bmad.core.enterprise.agent_integration import (
    enterprise_agent,
    enterprise_method,
    enterprise_required,
    enterprise_context,
    get_enterprise_context,
    set_enterprise_context,
    check_enterprise_feature,
    check_enterprise_permission,
    track_enterprise_usage,
    log_enterprise_event
)

# Test agent class for testing decorators
class TestAgent:
    def __init__(self, tenant_id=None, user_id=None):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.agent_name = "TestAgent"
    
    def basic_method(self):
        return "basic_result"
    
    @enterprise_method(permission="test_permission", usage_metric="agent_method_calls")
    def enterprise_method(self):
        return "enterprise_result"
    
    @enterprise_required(permission="required_permission")
    def required_method(self):
        return "required_result"
    
    # Add enterprise methods for testing
    def _check_enterprise_limits(self, operation: str) -> bool:
        return True
    
    def _track_enterprise_usage(self, metric: str, value: int = 1):
        # Actually call the global usage tracker for testing
        from bmad.core.enterprise.agent_integration import track_enterprise_usage
        track_enterprise_usage(metric, value, self.tenant_id)
    
    def _log_enterprise_event(self, event_type: str, resource: str, action: str, 
                            details: Dict[str, Any], success: bool = True):
        pass

@enterprise_agent
class DecoratedTestAgent:
    def __init__(self, **kwargs):
        self.agent_name = "DecoratedTestAgent"
    
    @enterprise_method(permission="execute_agents", usage_metric="agent_executions")
    def execute_task(self, task_data):
        return {"status": "completed", "data": task_data}

class TestEnterpriseAgentDecorator:
    """Test the @enterprise_agent class decorator."""
    
    def test_enterprise_agent_initialization(self):
        """Test that enterprise agent decorator properly initializes."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            mock_tenant.get_tenant.return_value = Mock()
            
            agent = DecoratedTestAgent(tenant_id="test_tenant", user_id="test_user")
            
            assert agent.tenant_id == "test_tenant"
            assert agent.user_id == "test_user"
            assert hasattr(agent, '_set_enterprise_context')
            assert hasattr(agent, '_check_enterprise_limits')
            assert hasattr(agent, '_track_enterprise_usage')
            assert hasattr(agent, '_log_enterprise_event')
    
    def test_enterprise_agent_without_context(self):
        """Test enterprise agent without tenant/user context."""
        agent = DecoratedTestAgent()
        
        assert agent.tenant_id is None
        assert agent.user_id is None
    
    def test_enterprise_agent_invalid_tenant(self):
        """Test enterprise agent with invalid tenant."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            mock_tenant.get_tenant.return_value = None
            
            with pytest.raises(ValueError, match="Tenant.*not found"):
                DecoratedTestAgent(tenant_id="invalid_tenant", user_id="test_user")

class TestEnterpriseMethodDecorator:
    """Test the @enterprise_method decorator."""
    
    def test_enterprise_method_with_permission(self):
        """Test enterprise method with permission check."""
        with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
            mock_permission.has_permission.return_value = True
            
            agent = TestAgent(tenant_id="test_tenant", user_id="test_user")
            result = agent.enterprise_method()
            
            assert result == "enterprise_result"
            mock_permission.has_permission.assert_called_with("test_user", "test_permission")
    
    def test_enterprise_method_without_permission(self):
        """Test enterprise method with insufficient permissions."""
        with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
            mock_permission.has_permission.return_value = False
            
            agent = TestAgent(tenant_id="test_tenant", user_id="test_user")
            
            with pytest.raises(ValueError, match="Permission.*required"):
                agent.enterprise_method()
    
    def test_enterprise_method_without_context(self):
        """Test enterprise method without enterprise context."""
        agent = TestAgent()  # No tenant_id or user_id
        
        # Should execute without enterprise checks
        result = agent.enterprise_method()
        assert result == "enterprise_result"
    
    def test_enterprise_method_with_usage_tracking(self):
        """Test enterprise method with usage tracking."""
        with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
            with patch('bmad.core.enterprise.agent_integration.usage_tracker') as mock_usage:
                mock_permission.has_permission.return_value = True
                
                agent = TestAgent(tenant_id="test_tenant", user_id="test_user")
                result = agent.enterprise_method()
                
                # Verify usage was tracked
                mock_usage.record_usage.assert_called_with(
                    tenant_id="test_tenant",
                    metric="agent_method_calls",
                    value=1
                )
                
                assert result == "enterprise_result"

class TestEnterpriseRequiredDecorator:
    """Test the @enterprise_required decorator."""
    
    def test_enterprise_required_with_permission(self):
        """Test enterprise_required with valid permission."""
        with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
            mock_permission.has_permission.return_value = True
            
            agent = TestAgent(tenant_id="test_tenant", user_id="test_user")
            result = agent.required_method()
            
            assert result == "required_result"
            mock_permission.has_permission.assert_called_with("test_user", "required_permission")
    
    def test_enterprise_required_without_permission(self):
        """Test enterprise_required with insufficient permissions."""
        with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
            mock_permission.has_permission.return_value = False
            
            agent = TestAgent(tenant_id="test_tenant", user_id="test_user")
            
            with pytest.raises(ValueError, match="Permission.*required"):
                agent.required_method()

class TestEnterpriseContext:
    """Test the enterprise_context context manager."""
    
    def test_enterprise_context_manager(self):
        """Test enterprise context manager functionality."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            # Set initial context
            mock_tenant._current_tenant_id = "initial_tenant"
            mock_tenant._current_user_id = "initial_user"
            
            with enterprise_context("new_tenant", "new_user"):
                assert mock_tenant._current_tenant_id == "new_tenant"
                assert mock_tenant._current_user_id == "new_user"
            
            # Context should be restored
            assert mock_tenant._current_tenant_id == "initial_tenant"
            assert mock_tenant._current_user_id == "initial_user"
    
    def test_enterprise_context_with_exception(self):
        """Test enterprise context manager with exception."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            mock_tenant._current_tenant_id = "initial_tenant"
            mock_tenant._current_user_id = "initial_user"
            
            try:
                with enterprise_context("new_tenant", "new_user"):
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # Context should still be restored
            assert mock_tenant._current_tenant_id == "initial_tenant"
            assert mock_tenant._current_user_id == "initial_user"

class TestUtilityFunctions:
    """Test utility functions for enterprise features."""
    
    def test_get_enterprise_context(self):
        """Test getting enterprise context."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            mock_tenant._current_tenant_id = "test_tenant"
            mock_tenant._current_user_id = "test_user"
            
            # Mock DEV_MODE to be False for this test
            with patch.dict(os.environ, {'DEV_MODE': 'false'}):
                context = get_enterprise_context()
                
                assert context['tenant_id'] == "test_tenant"
                assert context['user_id'] == "test_user"
    
    def test_set_enterprise_context(self):
        """Test setting enterprise context."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            set_enterprise_context("test_tenant", "test_user")
            
            assert mock_tenant._current_tenant_id == "test_tenant"
            assert mock_tenant._current_user_id == "test_user"
    
    def test_check_enterprise_feature(self):
        """Test checking enterprise feature flags."""
        with patch('bmad.core.enterprise.agent_integration.feature_flag_manager') as mock_flags:
            mock_flags.get_flag_value.return_value = True
            
            # Mock DEV_MODE to be False for this test
            with patch.dict(os.environ, {'DEV_MODE': 'false'}):
                result = check_enterprise_feature("test_feature", "test_tenant")
                
                assert result is True
                mock_flags.get_flag_value.assert_called_with("test_feature", "test_tenant")
    
    def test_check_enterprise_permission(self):
        """Test checking enterprise permissions."""
        with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
            mock_permission.has_permission.return_value = True
            
            # Mock DEV_MODE to be False for this test
            with patch.dict(os.environ, {'DEV_MODE': 'false'}):
                result = check_enterprise_permission("test_permission", "test_user")
                
                assert result is True
                mock_permission.has_permission.assert_called_with("test_user", "test_permission")
    
    def test_track_enterprise_usage(self):
        """Test tracking enterprise usage."""
        with patch('bmad.core.enterprise.agent_integration.usage_tracker') as mock_usage:
            track_enterprise_usage("test_metric", 5, "test_tenant")
            
            mock_usage.record_usage.assert_called_with(
                tenant_id="test_tenant",
                metric="test_metric",
                value=5
            )
    
    def test_log_enterprise_event(self):
        """Test logging enterprise events."""
        with patch('bmad.core.enterprise.agent_integration.enterprise_security_manager') as mock_security:
            log_enterprise_event(
                "test_event",
                "test_resource",
                "test_action",
                {"test": "data"},
                True,
                "test_tenant",
                "test_user"
            )
            
            mock_security.log_audit_event.assert_called_with(
                user_id="test_user",
                tenant_id="test_tenant",
                event_type="test_event",
                resource="test_resource",
                action="test_action",
                details={"test": "data"},
                success=True
            )

class TestEnterpriseIntegration:
    """Test complete enterprise integration scenarios."""
    
    def test_complete_agent_workflow(self):
        """Test complete agent workflow with enterprise features."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
                with patch('bmad.core.enterprise.agent_integration.usage_tracker') as mock_usage:
                    with patch('bmad.core.enterprise.agent_integration.enterprise_security_manager') as mock_security:
                        # Setup mocks
                        mock_tenant.get_tenant.return_value = Mock()
                        mock_permission.has_permission.return_value = True
                        
                        # Create agent with enterprise features
                        agent = DecoratedTestAgent(tenant_id="test_tenant", user_id="test_user")
                        
                        # Execute task
                        result = agent.execute_task({"test": "data"})
                        
                        # Verify results
                        assert result == {"status": "completed", "data": {"test": "data"}}
                        
                        # Verify enterprise features were used
                        mock_tenant.get_tenant.assert_called_with("test_tenant")
                        mock_permission.has_permission.assert_called_with("test_user", "execute_agents")
                        mock_usage.record_usage.assert_called()
                        mock_security.log_audit_event.assert_called()
    
    def test_enterprise_features_without_context(self):
        """Test that agents work without enterprise context."""
        agent = DecoratedTestAgent()
        
        # Should work without enterprise context
        result = agent.execute_task({"test": "data"})
        assert result == {"status": "completed", "data": {"test": "data"}}
    
    def test_enterprise_features_with_invalid_permissions(self):
        """Test enterprise features with invalid permissions."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            with patch('bmad.core.enterprise.agent_integration.permission_manager') as mock_permission:
                mock_tenant.get_tenant.return_value = Mock()
                mock_permission.has_permission.return_value = False
                
                agent = DecoratedTestAgent(tenant_id="test_tenant", user_id="test_user")
                
                with pytest.raises(ValueError, match="Permission.*required"):
                    agent.execute_task({"test": "data"})

class TestEnterpriseLimits:
    """Test enterprise limit checking functionality."""
    
    def test_enterprise_limits_check(self):
        """Test enterprise limits checking."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            mock_tenant.get_tenant.return_value = Mock()
            mock_tenant.check_limit.return_value = True
            
            agent = DecoratedTestAgent(tenant_id="test_tenant", user_id="test_user")
            
            # Test limit checking
            result = agent._check_enterprise_limits("agent_execution")
            assert result is True
            
            mock_tenant.check_limit.assert_called_with("max_agent_executions", 1)
    
    def test_enterprise_limits_exceeded(self):
        """Test enterprise limits when exceeded."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            mock_tenant.get_tenant.return_value = Mock()
            mock_tenant.check_limit.return_value = False
            
            agent = DecoratedTestAgent(tenant_id="test_tenant", user_id="test_user")
            
            # Test limit checking
            result = agent._check_enterprise_limits("agent_execution")
            assert result is False

class TestEnterpriseAuditLogging:
    """Test enterprise audit logging functionality."""
    
    def test_enterprise_audit_logging(self):
        """Test enterprise audit logging."""
        with patch('bmad.core.enterprise.agent_integration.tenant_manager') as mock_tenant:
            with patch('bmad.core.enterprise.agent_integration.enterprise_security_manager') as mock_security:
                mock_tenant.get_tenant.return_value = Mock()
                
                agent = DecoratedTestAgent(tenant_id="test_tenant", user_id="test_user")
                
                # Test audit logging
                agent._log_enterprise_event(
                    "test_event",
                    "test_resource",
                    "test_action",
                    {"test": "data"}
                )
                
                mock_security.log_audit_event.assert_called_with(
                    user_id="test_user",
                    tenant_id="test_tenant",
                    event_type="test_event",
                    resource="test_resource",
                    action="test_action",
                    details={"test": "data"},
                    success=True
                )
    
    def test_enterprise_audit_logging_without_context(self):
        """Test enterprise audit logging without context."""
        agent = DecoratedTestAgent()
        
        # Should not log without context
        agent._log_enterprise_event(
            "test_event",
            "test_resource",
            "test_action",
            {"test": "data"}
        )
        
        # No exception should be raised
        assert True 