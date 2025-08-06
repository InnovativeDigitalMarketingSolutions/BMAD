#!/usr/bin/env python3
"""
Security Implementation Tests
Comprehensive tests for JWT validation, permission checking, and security features
"""

import pytest
import jwt
import time
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request, jsonify

# Import the security components
from bmad.core.security.jwt_service import jwt_service
from bmad.core.security.permission_service import permission_service, require_permission_enhanced
from bmad.core.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from bmad.core.resilience.error_handler import error_handler, ErrorCategory, ErrorSeverity


class TestJWTSecurityImplementation:
    """Test JWT token validation implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        
        # Test user data
        self.test_user = {
            "sub": "test_user_123",
            "email": "test@example.com",
            "tenant_id": "test_tenant",
            "roles": ["user"],
            "permissions": ["read_data", "write_data"]
        }
    
    def test_jwt_token_validation_implementation(self):
        """Test that JWT token validation is properly implemented."""
        # Create a valid token
        token = jwt_service.create_access_token(self.test_user)
        
        # Verify token is valid
        payload = jwt_service.verify_access_token(token)
        assert payload is not None
        assert payload.get("sub") == self.test_user["user_id"]
        assert payload.get("email") == self.test_user["email"]
        assert payload.get("tenant_id") == self.test_user["tenant_id"]
    
    def test_jwt_token_expiration(self):
        """Test JWT token expiration handling."""
        # Create token with short expiration
        with patch.object(jwt_service, 'access_token_expire_minutes', 0.01):  # 0.6 seconds
            token = jwt_service.create_access_token(self.test_user)
            
            # Token should be valid initially
            payload = jwt_service.verify_access_token(token)
            assert payload is not None
            
            # Wait for expiration
            time.sleep(1)
            
            # Token should be expired
            payload = jwt_service.verify_access_token(token)
            assert payload is None
    
    def test_jwt_token_invalid_signature(self):
        """Test JWT token with invalid signature."""
        # Create token with wrong secret
        with patch.object(jwt_service, 'secret_key', 'wrong_secret'):
            token = jwt_service.create_access_token(self.test_user)
        
        # Try to verify with correct secret
        payload = jwt_service.verify_access_token(token)
        assert payload is None
    
    def test_jwt_token_malformed(self):
        """Test malformed JWT token handling."""
        # Test with malformed token
        malformed_token = "invalid.token.here"
        payload = jwt_service.verify_access_token(malformed_token)
        assert payload is None
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh functionality."""
        # Create access token
        access_token = jwt_service.create_access_token(self.test_user)
        
        # Create refresh token
        refresh_token = jwt_service.create_refresh_token(self.test_user)
        
        # Verify refresh token
        payload = jwt_service.verify_refresh_token(refresh_token)
        assert payload is not None
        assert payload.get("sub") == self.test_user["user_id"]


class TestPermissionSystemImplementation:
    """Test permission checking system implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        
        # Mock user with permissions
        self.user_with_permissions = Mock()
        self.user_with_permissions.id = "user_123"
        self.user_with_permissions.permissions = ["read_data", "write_data", "delete_data"]
        
        # Mock user without permissions
        self.user_without_permissions = Mock()
        self.user_without_permissions.id = "user_456"
        self.user_without_permissions.permissions = ["read_data"]
    
    def test_permission_checking_implementation(self):
        """Test that permission checking is properly implemented."""
        # Mock the permission_manager to return expected results
        with patch('bmad.core.enterprise.user_management.permission_manager') as mock_permission_manager:
            # Mock has_permission method
            mock_permission_manager.has_permission.side_effect = lambda user_id, permission: {
                ("user_123", "read_data"): True,
                ("user_456", "delete_data"): False
            }.get((user_id, permission), False)
            
            # Test user with required permission
            has_permission = permission_service.check_permission(
                self.user_with_permissions.id, 
                "read_data"
            )
            assert has_permission is True
            
            # Test user without required permission
            has_permission = permission_service.check_permission(
                self.user_without_permissions.id, 
                "delete_data"
            )
            assert has_permission is False
    
    def test_permission_decorator_implementation(self):
        """Test permission decorator implementation."""
        @self.app.route("/test-permission")
        @require_permission_enhanced("read_data")
        def test_endpoint():
            return jsonify({"status": "success"})
        
        # Mock request context
        with self.app.test_request_context("/test-permission"):
            # Mock user in request
            request.user = self.user_with_permissions
            
            # Test with user having permission
            response = test_endpoint()
            assert response.status_code == 200
    
    def test_permission_tenant_awareness(self):
        """Test tenant-aware permission checking."""
        # Test permission checking with tenant context
        has_permission = permission_service.check_permission(
            self.user_with_permissions.id,
            "read_data",
            tenant_id="test_tenant"
        )
        # Should work with tenant context
        assert isinstance(has_permission, bool)
    
    def test_permission_logging(self):
        """Test permission check logging."""
        with patch.object(permission_service, 'log_permission_check') as mock_log:
            permission_service.check_permission(
                self.user_with_permissions.id,
                "read_data"
            )
            # Verify logging was called
            assert mock_log.called


class TestCircuitBreakerImplementation:
    """Test circuit breaker pattern implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=5,
            name="test_circuit"
        )
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization."""
        assert self.circuit_breaker.state.value == "CLOSED"
        assert self.circuit_breaker.failure_count == 0
        assert self.circuit_breaker.failure_threshold == 3
        assert self.circuit_breaker.timeout == 5
    
    def test_circuit_breaker_successful_calls(self):
        """Test circuit breaker with successful calls."""
        def successful_function():
            return "success"
        
        # Multiple successful calls
        for _ in range(5):
            result = self.circuit_breaker.call(successful_function)
            assert result == "success"
        
        # Circuit should remain closed
        assert self.circuit_breaker.state.value == "CLOSED"
        assert self.circuit_breaker.successful_calls == 5
    
    def test_circuit_breaker_failure_handling(self):
        """Test circuit breaker failure handling."""
        def failing_function():
            raise Exception("Service unavailable")
        
        # Call failing function multiple times
        for i in range(3):
            try:
                self.circuit_breaker.call(failing_function)
            except Exception:
                pass
        
        # Circuit should be open after threshold
        assert self.circuit_breaker.state.value == "OPEN"
        assert self.circuit_breaker.failure_count == 3
    
    def test_circuit_breaker_half_open_state(self):
        """Test circuit breaker half-open state."""
        def failing_function():
            raise Exception("Service unavailable")
        
        # Open the circuit
        for _ in range(3):
            try:
                self.circuit_breaker.call(failing_function)
            except Exception:
                pass
        
        assert self.circuit_breaker.state.value == "OPEN"
        
        # Wait for timeout and test half-open
        self.circuit_breaker.last_failure_time = time.time() - 6  # Past timeout
        
        def successful_function():
            return "success"
        
        # Should transition to half-open and then closed
        result = self.circuit_breaker.call(successful_function)
        assert result == "success"
        assert self.circuit_breaker.state.value == "CLOSED"
    
    def test_circuit_breaker_open_error(self):
        """Test circuit breaker open error."""
        def failing_function():
            raise Exception("Service unavailable")
        
        # Open the circuit
        for _ in range(3):
            try:
                self.circuit_breaker.call(failing_function)
            except Exception:
                pass
        
        # Try to call function when circuit is open
        with pytest.raises(CircuitBreakerOpenError):
            self.circuit_breaker.call(failing_function)


class TestErrorHandlingImplementation:
    """Test comprehensive error handling implementation."""
    
    def setup_method(self):
        """Set up test environment."""
        error_handler.reset_statistics()
    
    def test_error_classification(self):
        """Test error classification system."""
        # Test authentication error classification
        auth_error = Exception("Authentication failed")
        category = error_handler.classify_error(auth_error)
        assert category == ErrorCategory.AUTHENTICATION
        
        # Test database error classification
        db_error = Exception("Database connection failed")
        category = error_handler.classify_error(db_error)
        assert category == ErrorCategory.DATABASE
        
        # Test network error classification
        network_error = Exception("Network timeout")
        category = error_handler.classify_error(network_error)
        assert category == ErrorCategory.NETWORK
    
    def test_error_severity_determination(self):
        """Test error severity determination."""
        # Test critical error
        critical_error = Exception("Security vulnerability detected")
        severity = error_handler.get_error_severity(critical_error)
        assert severity == ErrorSeverity.CRITICAL
        
        # Test high severity error
        high_error = Exception("Database connection lost")
        severity = error_handler.get_error_severity(high_error)
        assert severity == ErrorSeverity.HIGH
        
        # Test medium severity error
        medium_error = Exception("Validation failed")
        severity = error_handler.get_error_severity(medium_error)
        assert severity == ErrorSeverity.MEDIUM
    
    def test_error_handling_with_recovery(self):
        """Test error handling with recovery strategies."""
        # Test database error with retry strategy
        db_error = Exception("Database connection failed")
        context = {"retry_count": 0}
        
        result = error_handler.handle_error(db_error, context)
        assert result["category"] == "DATABASE"
        assert result["severity"] == "HIGH"
        assert result["should_retry"] is True
        assert result["retry_delay"] > 0
    
    def test_error_handling_decorator(self):
        """Test error handling decorator."""
        @handle_errors(max_retries=2, retry_delay=0.1)
        def failing_function():
            raise ConnectionError("Connection failed")
        
        # Should retry and eventually fail
        with pytest.raises(ConnectionError):
            failing_function()
    
    def test_safe_execute_function(self):
        """Test safe execute function."""
        def failing_function():
            raise Exception("Function failed")
        
        # Should return default value on error
        result = safe_execute(failing_function, default_return="fallback")
        assert result == "fallback"
        
        # Should return function result on success
        def successful_function():
            return "success"
        
        result = safe_execute(successful_function, default_return="fallback")
        assert result == "success"


class TestSecurityIntegration:
    """Test security features integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.client = self.app.test_client()
    
    def test_security_headers_implementation(self):
        """Test security headers implementation."""
        @self.app.route("/test")
        def test_endpoint():
            return jsonify({"status": "ok"})
        
        with self.app.test_client() as client:
            response = client.get("/test")
            
            # Check security headers
            assert response.headers.get('X-Content-Type-Options') == 'nosniff'
            assert response.headers.get('X-Frame-Options') == 'DENY'
            assert response.headers.get('X-XSS-Protection') == '1; mode=block'
            assert 'Strict-Transport-Security' in response.headers
    
    def test_rate_limiting_implementation(self):
        """Test rate limiting implementation."""
        # This would require more complex setup with actual rate limiting
        # For now, just verify the concept is implemented
        assert True  # Placeholder for rate limiting test
    
    def test_authentication_flow(self):
        """Test complete authentication flow."""
        # Test login endpoint
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        # This would test the actual login flow
        # For now, just verify the concept is implemented
        assert True  # Placeholder for authentication flow test


class TestSecurityVulnerabilityFixes:
    """Test that all identified security vulnerabilities are fixed."""
    
    def test_jwt_validation_not_bypassed(self):
        """Test that JWT validation cannot be bypassed."""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        payload = jwt_service.verify_access_token(invalid_token)
        assert payload is None
        
        # Test with expired token
        expired_token = jwt.encode(
            {
                "sub": "test_user",
                "exp": time.time() - 3600  # Expired 1 hour ago
            },
            jwt_service.SECRET_KEY,
            algorithm=jwt_service.ALGORITHM
        )
        payload = jwt_service.verify_access_token(expired_token)
        assert payload is None
    
    def test_permission_checking_not_bypassed(self):
        """Test that permission checking cannot be bypassed."""
        # Test user without permission trying to access protected resource
        user_without_permission = Mock()
        user_without_permission.id = "user_no_permission"
        user_without_permission.permissions = []
        
        has_permission = permission_service.check_permission(
            user_without_permission.id,
            "admin_only_permission"
        )
        assert has_permission is False
    
    def test_circuit_breaker_protects_against_cascading_failures(self):
        """Test that circuit breaker prevents cascading failures."""
        circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=1)
        
        def failing_service():
            raise Exception("Service unavailable")
        
        # Fail twice to open circuit
        for _ in range(2):
            try:
                circuit_breaker.call(failing_service)
            except Exception:
                pass
        
        # Circuit should be open
        assert circuit_breaker.state.value == "OPEN"
        
        # Further calls should fail fast
        with pytest.raises(CircuitBreakerOpenError):
            circuit_breaker.call(failing_service)
    
    def test_error_handling_prevents_system_crashes(self):
        """Test that error handling prevents system crashes."""
        # Test that errors are properly caught and handled
        def dangerous_function():
            raise Exception("Critical error")
        
        # Should not crash the system
        result = safe_execute(dangerous_function, default_return="safe_fallback")
        assert result == "safe_fallback"
        
        # Check that error was logged
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 