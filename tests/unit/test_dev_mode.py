"""
Test Development Mode Authentication Bypass

Tests that DEV_MODE=true properly bypasses authentication
and provides development context.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bmad.api import app


class TestDevMode(unittest.TestCase):
    """Test development mode functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_dev_mode_authentication_bypass(self):
        """Test that DEV_MODE bypasses authentication."""
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            # Test an endpoint that requires authentication
            response = self.app.get('/orchestrator/status')
            
            # Should succeed without authentication headers
            self.assertEqual(response.status_code, 200)
    
    def test_dev_mode_without_env_var(self):
        """Test that authentication is required when DEV_MODE is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Test an endpoint that requires authentication
            response = self.app.get('/orchestrator/status')
            
            # Should fail without authentication
            self.assertEqual(response.status_code, 401)
    
    def test_dev_mode_tenant_context(self):
        """Test that DEV_MODE provides dev tenant context."""
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            # Test tenant-dependent endpoint
            response = self.app.get('/api/tenants')
            
            # Should succeed with dev tenant context
            self.assertEqual(response.status_code, 200)
    
    def test_dev_mode_user_context(self):
        """Test that DEV_MODE provides dev user context."""
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            # Test user-dependent endpoint
            response = self.app.get('/api/users')
            
            # Should succeed with dev user context
            self.assertEqual(response.status_code, 200)
    
    def test_dev_mode_workflow_execution(self):
        """Test that DEV_MODE allows workflow execution."""
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            # Test workflow execution endpoint
            response = self.app.post('/orchestrator/start-workflow',
                                   json={'workflow': 'test_workflow'})
            
            # Should succeed without authentication
            self.assertEqual(response.status_code, 200)
    
    def test_dev_mode_agent_commands(self):
        """Test that DEV_MODE allows agent commands."""
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            # Test agent command endpoint
            response = self.app.post('/agent/test_agent/command',
                                   json={'command': 'test_command'})
            
            # Should succeed without authentication
            self.assertEqual(response.status_code, 200)
    
    def test_dev_mode_enterprise_features(self):
        """Test that DEV_MODE enables all enterprise features."""
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            # Test various enterprise endpoints
            endpoints = [
                '/api/billing/plans',
                '/api/features/test_flag',
                '/api/security/compliance'
            ]
            
            for endpoint in endpoints:
                response = self.app.get(endpoint)
                # Should succeed with dev permissions
                self.assertEqual(response.status_code, 200, 
                               f"Endpoint {endpoint} failed with status {response.status_code}")


if __name__ == "__main__":
    unittest.main() 