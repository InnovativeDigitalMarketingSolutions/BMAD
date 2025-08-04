"""
Unit tests for BMAD API security features.

Tests security headers, rate limiting, error handling, and authentication features.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Mock Flask modules to avoid import issues
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter.util'] = MagicMock()

from bmad.api import app


class TestAPISecurityHeaders:
    """Test cases for API security headers."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_security_headers_present(self):
        """Test that all security headers are present in responses."""
        response = self.client.get('/test/ping')
        
        # Check all security headers are present
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'
        assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
        assert 'Content-Security-Policy' in response.headers
        assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
        assert response.headers.get('Permissions-Policy') == 'geolocation=(), microphone=(), camera=()'
    
    def test_security_headers_all_endpoints(self):
        """Test that security headers are present on all endpoints."""
        endpoints = [
            '/test/ping',
            '/test/echo',
            '/api/auth/login',
            '/orchestrator/status'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.headers.get('X-Content-Type-Options') == 'nosniff'
            assert response.headers.get('X-Frame-Options') == 'DENY'


class TestAPIErrorHandling:
    """Test cases for API error handling."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_400_bad_request_handler(self):
        """Test 400 Bad Request error handler."""
        # Mock a bad request scenario
        with patch('bmad.api.request') as mock_request:
            mock_request.json = None
            mock_request.method = 'POST'
            
            response = self.client.post('/test/echo', data='invalid json')
            assert response.status_code == 400
            assert 'error' in response.get_json()
            assert 'message' in response.get_json()
    
    def test_404_not_found_handler(self):
        """Test 404 Not Found error handler."""
        response = self.client.get('/nonexistent/endpoint')
        assert response.status_code == 404
        assert 'error' in response.get_json()
        assert 'message' in response.get_json()
    
    def test_500_internal_error_handler(self):
        """Test 500 Internal Server Error handler."""
        # Mock an internal error scenario
        with patch('bmad.api.jsonify') as mock_jsonify:
            mock_jsonify.side_effect = Exception("Internal error")
            
            response = self.client.get('/test/ping')
            assert response.status_code == 500
            assert 'error' in response.get_json()
            assert 'message' in response.get_json()


class TestAPIRateLimiting:
    """Test cases for API rate limiting."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_rate_limiting_configured(self):
        """Test that rate limiting is properly configured."""
        # Check that limiter is configured
        assert hasattr(app, 'limiter')
        assert app.limiter is not None
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present."""
        response = self.client.get('/test/ping')
        
        # Check for rate limit headers
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
        assert 'X-RateLimit-Reset' in response.headers


class TestAPIAuthentication:
    """Test cases for API authentication."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints."""
        # Test protected endpoint without authentication
        response = self.client.get('/orchestrator/status')
        assert response.status_code == 401
        assert 'error' in response.get_json()
        assert 'message' in response.get_json()
    
    def test_authentication_with_valid_token(self):
        """Test authentication with valid JWT token."""
        # Mock JWT service and valid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock request headers
            with patch('bmad.api.request') as mock_request:
                mock_request.headers = {'Authorization': 'Bearer valid_token'}
                mock_request.remote_addr = '127.0.0.1'
                
                response = self.client.get('/orchestrator/status')
                assert response.status_code == 200
    
    def test_authentication_with_invalid_token(self):
        """Test authentication with invalid JWT token."""
        # Mock JWT service and invalid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = None
            
            # Mock request headers
            with patch('bmad.api.request') as mock_request:
                mock_request.headers = {'Authorization': 'Bearer invalid_token'}
                mock_request.remote_addr = '127.0.0.1'
                
                response = self.client.get('/orchestrator/status')
                assert response.status_code == 401
                assert 'error' in response.get_json()


class TestAPIPermissions:
    """Test cases for API permission system."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_permission_denied(self):
        """Test permission denied scenario."""
        # Mock JWT service with limited permissions
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["user"],
                "permissions": ["view_agents"]
            }
            
            # Mock permission service denying permission
            with patch('bmad.api.permission_service') as mock_permission_service:
                mock_permission_service.check_permission.return_value = False
                
                # Mock request headers
                with patch('bmad.api.request') as mock_request:
                    mock_request.headers = {'Authorization': 'Bearer valid_token'}
                    mock_request.remote_addr = '127.0.0.1'
                    mock_request.user = MagicMock(id="user123")
                    mock_request.tenant_id = "tenant123"
                    mock_request.endpoint = "/orchestrator/start-workflow"
                    
                    response = self.client.post('/orchestrator/start-workflow', 
                                              json={"workflow": "test"})
                    assert response.status_code == 403
                    assert 'error' in response.get_json()
    
    def test_permission_granted(self):
        """Test permission granted scenario."""
        # Mock JWT service with admin permissions
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock permission service granting permission
            with patch('bmad.api.permission_service') as mock_permission_service:
                mock_permission_service.check_permission.return_value = True
                
                # Mock request headers
                with patch('bmad.api.request') as mock_request:
                    mock_request.headers = {'Authorization': 'Bearer valid_token'}
                    mock_request.remote_addr = '127.0.0.1'
                    mock_request.user = MagicMock(id="user123")
                    mock_request.tenant_id = "tenant123"
                    mock_request.endpoint = "/orchestrator/start-workflow"
                    
                    response = self.client.post('/orchestrator/start-workflow', 
                                              json={"workflow": "test"})
                    assert response.status_code == 200


class TestAPITenantLimits:
    """Test cases for API tenant limit checking."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_tenant_workflow_limit_exceeded(self):
        """Test tenant workflow limit exceeded scenario."""
        # Mock JWT service with valid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock tenant manager with limit exceeded
            with patch('bmad.api.tenant_manager') as mock_tenant_manager:
                mock_tenant_manager.get_tenant.return_value = MagicMock()
                mock_tenant_manager.check_limit.return_value = False
                
                # Mock orchestrator with high workflow count
                with patch('bmad.api.orch') as mock_orch:
                    mock_orch.get_tenant_workflow_count.return_value = 10
                    
                    # Mock request headers
                    with patch('bmad.api.request') as mock_request:
                        mock_request.headers = {'Authorization': 'Bearer valid_token'}
                        mock_request.remote_addr = '127.0.0.1'
                        mock_request.user = MagicMock(id="user123")
                        mock_request.tenant_id = "tenant123"
                        mock_request.endpoint = "/orchestrator/start-workflow"
                        
                        response = self.client.post('/orchestrator/start-workflow', 
                                                  json={"workflow": "test"})
                        assert response.status_code == 403
                        assert 'error' in response.get_json()
                        assert 'limit exceeded' in response.get_json()['error'].lower()
    
    def test_tenant_agent_limit_exceeded(self):
        """Test tenant agent limit exceeded scenario."""
        # Mock JWT service with valid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock tenant manager with limit exceeded
            with patch('bmad.api.tenant_manager') as mock_tenant_manager:
                mock_tenant_manager.get_tenant.return_value = MagicMock()
                mock_tenant_manager.check_limit.return_value = False
                
                # Mock orchestrator with high agent count
                with patch('bmad.api.orch') as mock_orch:
                    mock_orch.get_tenant_agent_count.return_value = 20
                    
                    # Mock request headers
                    with patch('bmad.api.request') as mock_request:
                        mock_request.headers = {'Authorization': 'Bearer valid_token'}
                        mock_request.remote_addr = '127.0.0.1'
                        mock_request.user = MagicMock(id="user123")
                        mock_request.tenant_id = "tenant123"
                        mock_request.endpoint = "/agent/DataEngineer/command"
                        
                        response = self.client.post('/agent/DataEngineer/command', 
                                                  json={"command": "test"})
                        assert response.status_code == 403
                        assert 'error' in response.get_json()
                        assert 'limit exceeded' in response.get_json()['error'].lower()


class TestAPIPeriodBasedUsage:
    """Test cases for API period-based usage tracking."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_period_based_usage_current_month(self):
        """Test period-based usage with current_month period."""
        # Mock JWT service with valid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock usage tracker
            with patch('bmad.api.usage_tracker') as mock_usage_tracker:
                mock_usage_tracker.get_current_month_usage.return_value = 1250
                
                # Mock request headers
                with patch('bmad.api.request') as mock_request:
                    mock_request.headers = {'Authorization': 'Bearer valid_token'}
                    mock_request.remote_addr = '127.0.0.1'
                    mock_request.user = MagicMock(id="user123")
                    mock_request.tenant_id = "tenant123"
                    mock_request.endpoint = "/api/billing/usage"
                    mock_request.args = {'period': 'current_month'}
                    
                    response = self.client.get('/api/billing/usage?period=current_month')
                    assert response.status_code == 200
                    data = response.get_json()
                    assert 'api_calls' in data
                    assert data['api_calls'] == 1250
    
    def test_period_based_usage_current_quarter(self):
        """Test period-based usage with current_quarter period."""
        # Mock JWT service with valid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock usage tracker
            with patch('bmad.api.usage_tracker') as mock_usage_tracker:
                mock_usage_tracker.get_current_quarter_usage.return_value = 3500
                
                # Mock request headers
                with patch('bmad.api.request') as mock_request:
                    mock_request.headers = {'Authorization': 'Bearer valid_token'}
                    mock_request.remote_addr = '127.0.0.1'
                    mock_request.user = MagicMock(id="user123")
                    mock_request.tenant_id = "tenant123"
                    mock_request.endpoint = "/api/billing/usage"
                    mock_request.args = {'period': 'current_quarter'}
                    
                    response = self.client.get('/api/billing/usage?period=current_quarter')
                    assert response.status_code == 200
                    data = response.get_json()
                    assert 'api_calls' in data
                    assert data['api_calls'] == 3500
    
    def test_period_based_usage_unknown_period(self):
        """Test period-based usage with unknown period defaults to current_month."""
        # Mock JWT service with valid token
        with patch('bmad.api.jwt_service') as mock_jwt_service:
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            
            # Mock usage tracker
            with patch('bmad.api.usage_tracker') as mock_usage_tracker:
                mock_usage_tracker.get_current_month_usage.return_value = 1000
                
                # Mock request headers
                with patch('bmad.api.request') as mock_request:
                    mock_request.headers = {'Authorization': 'Bearer valid_token'}
                    mock_request.remote_addr = '127.0.0.1'
                    mock_request.user = MagicMock(id="user123")
                    mock_request.tenant_id = "tenant123"
                    mock_request.endpoint = "/api/billing/usage"
                    mock_request.args = {'period': 'unknown_period'}
                    
                    response = self.client.get('/api/billing/usage?period=unknown_period')
                    assert response.status_code == 200
                    data = response.get_json()
                    assert 'api_calls' in data
                    assert data['api_calls'] == 1000


class TestAPIIntegration:
    """Integration tests for API security features."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.client = app.test_client()
    
    def test_complete_authentication_flow(self):
        """Test complete authentication flow with security features."""
        # Test login endpoint
        response = self.client.post('/api/auth/login', 
                                  json={"email": "user@example.com", "password": "password123"})
        assert response.status_code == 200
        
        # Check security headers are present
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') == 'DENY'
        
        # Check rate limit headers are present
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
    
    def test_protected_endpoint_with_authentication(self):
        """Test protected endpoint with proper authentication."""
        # Mock JWT service and permission service
        with patch('bmad.api.jwt_service') as mock_jwt_service, \
             patch('bmad.api.permission_service') as mock_permission_service:
            
            mock_jwt_service.verify_access_token.return_value = {
                "sub": "user123",
                "email": "user@example.com",
                "tenant_id": "tenant123",
                "roles": ["admin"],
                "permissions": ["*"]
            }
            mock_permission_service.check_permission.return_value = True
            
            # Mock request context
            with patch('bmad.api.request') as mock_request:
                mock_request.headers = {'Authorization': 'Bearer valid_token'}
                mock_request.remote_addr = '127.0.0.1'
                mock_request.user = MagicMock(id="user123")
                mock_request.tenant_id = "tenant123"
                mock_request.endpoint = "/orchestrator/status"
                
                response = self.client.get('/orchestrator/status')
                assert response.status_code == 200
                
                # Check security headers
                assert response.headers.get('X-Content-Type-Options') == 'nosniff'
                assert response.headers.get('X-Frame-Options') == 'DENY' 