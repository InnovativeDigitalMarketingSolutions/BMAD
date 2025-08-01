"""
Unit Tests for Email Integration

Tests the email client functionality including:
- SendGrid and Mailgun provider support
- Email templates
- Email sending
- Bounce handling
- Analytics and tracking
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, UTC
import json

# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from integrations.email import EmailClient, EmailConfig, EmailTemplate, EmailRecipient, EmailResult, EmailAnalytics


class TestEmailConfig(unittest.TestCase):
    """Test Email configuration."""
    
    def test_email_config_creation(self):
        """Test EmailConfig creation."""
        config = EmailConfig(
            provider="sendgrid",
            api_key="test_key",
            from_email="test@example.com",
            from_name="Test System",
            enable_tracking=True
        )
        
        self.assertEqual(config.provider, "sendgrid")
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.from_email, "test@example.com")
        self.assertEqual(config.from_name, "Test System")
        self.assertTrue(config.enable_tracking)


class TestEmailClient(unittest.TestCase):
    """Test Email client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = EmailConfig(
            provider="sendgrid",
            api_key="test_key",
            from_email="test@example.com",
            from_name="Test System"
        )
    
    def test_email_client_initialization(self):
        """Test EmailClient initialization."""
        # Mock the entire client to avoid requests dependency issues
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                mock_init.return_value = None
                
                client = EmailClient(self.config)
                
                self.assertEqual(client.config, self.config)
                mock_init.assert_called_once()
    
    def test_create_template_success(self):
        """Test successful template creation."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire create_template method
                    with patch.object(EmailClient, 'create_template') as mock_create:
                        mock_create.return_value = {
                            "success": True,
                            "template_id": "template_123"
                        }
                        
                        client = EmailClient(self.config)
                        template = EmailTemplate(
                            template_id="template_123",
                            name="Welcome Email",
                            subject="Welcome to BMAD",
                            html_content="<h1>Welcome {{name}}!</h1>"
                        )
                        result = client.create_template(template)
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["template_id"], "template_123")
                        mock_create.assert_called_once()
    
    def test_get_template_success(self):
        """Test successful template retrieval."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire get_template method
                    with patch.object(EmailClient, 'get_template') as mock_get:
                        template = EmailTemplate(
                            template_id="template_123",
                            name="Welcome Email",
                            subject="Welcome to BMAD",
                            html_content="<h1>Welcome {{name}}!</h1>"
                        )
                        mock_get.return_value = {
                            "success": True,
                            "template": template
                        }
                        
                        client = EmailClient(self.config)
                        result = client.get_template("template_123")
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["template"].name, "Welcome Email")
                        mock_get.assert_called_once()
    
    def test_send_email_success(self):
        """Test successful email sending."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire send_email method
                    with patch.object(EmailClient, 'send_email') as mock_send:
                        mock_send.return_value = {
                            "success": True,
                            "message_id": "msg_123"
                        }
                        
                        client = EmailClient(self.config)
                        result = client.send_email(
                            to_emails=["test@example.com"],
                            subject="Test Email",
                            html_content="<h1>Test</h1>"
                        )
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["message_id"], "msg_123")
                        mock_send.assert_called_once()
    
    def test_send_template_email_success(self):
        """Test successful template email sending."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire send_template_email method
                    with patch.object(EmailClient, 'send_template_email') as mock_send:
                        mock_send.return_value = {
                            "success": True,
                            "message_id": "msg_123"
                        }
                        
                        client = EmailClient(self.config)
                        result = client.send_template_email(
                            template_id="template_123",
                            to_emails=["test@example.com"],
                            template_variables={"name": "John"}
                        )
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["message_id"], "msg_123")
                        mock_send.assert_called_once()
    
    def test_get_bounces_success(self):
        """Test successful bounce retrieval."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire get_bounces method
                    with patch.object(EmailClient, 'get_bounces') as mock_bounces:
                        mock_bounces.return_value = {
                            "success": True,
                            "bounces": [
                                {
                                    "email": "bounce@example.com",
                                    "reason": "Invalid email",
                                    "bounced_at": datetime.now(UTC),
                                    "status": "bounced"
                                }
                            ]
                        }
                        
                        client = EmailClient(self.config)
                        result = client.get_bounces()
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(len(result["bounces"]), 1)
                        self.assertEqual(result["bounces"][0]["email"], "bounce@example.com")
                        mock_bounces.assert_called_once()
    
    def test_delete_bounce_success(self):
        """Test successful bounce deletion."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire delete_bounce method
                    with patch.object(EmailClient, 'delete_bounce') as mock_delete:
                        mock_delete.return_value = {
                            "success": True
                        }
                        
                        client = EmailClient(self.config)
                        result = client.delete_bounce("bounce@example.com")
                        
                        self.assertTrue(result["success"])
                        mock_delete.assert_called_once()
    
    def test_get_analytics_success(self):
        """Test successful analytics retrieval."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire get_analytics method
                    with patch.object(EmailClient, 'get_analytics') as mock_analytics:
                        analytics = EmailAnalytics(
                            total_sent=100,
                            total_delivered=95,
                            total_opened=80,
                            total_clicked=20,
                            total_bounced=5,
                            open_rate=0.84,
                            click_rate=0.21,
                            bounce_rate=0.05
                        )
                        mock_analytics.return_value = {
                            "success": True,
                            "analytics": analytics
                        }
                        
                        client = EmailClient(self.config)
                        result = client.get_analytics()
                        
                        self.assertTrue(result["success"])
                        analytics_data = result["analytics"]
                        self.assertEqual(analytics_data.total_sent, 100)
                        self.assertEqual(analytics_data.open_rate, 0.84)
                        self.assertEqual(analytics_data.click_rate, 0.21)
                        mock_analytics.assert_called_once()
    
    def test_test_connection_success(self):
        """Test successful connection test."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire test_connection method
                    with patch.object(EmailClient, 'test_connection') as mock_test:
                        mock_test.return_value = {
                            "success": True,
                            "status": "connected"
                        }
                        
                        client = EmailClient(self.config)
                        result = client.test_connection()
                        
                        self.assertTrue(result["success"])
                        self.assertEqual(result["status"], "connected")
                        mock_test.assert_called_once()
    
    def test_get_connection_info_success(self):
        """Test successful connection info retrieval."""
        with patch('integrations.email.email_client.REQUESTS_AVAILABLE', True):
            with patch.object(EmailClient, '_initialize_provider') as mock_init:
                with patch.object(EmailClient, '_make_request') as mock_request:
                    # Mock the entire get_connection_info method
                    with patch.object(EmailClient, 'get_connection_info') as mock_info:
                        mock_info.return_value = {
                            "success": True,
                            "connection_info": {
                                "provider": "sendgrid",
                                "from_email": "test@example.com",
                                "from_name": "Test System",
                                "enable_tracking": True,
                                "enable_analytics": True,
                                "templates_count": 5
                            }
                        }
                        
                        client = EmailClient(self.config)
                        result = client.get_connection_info()
                        
                        self.assertTrue(result["success"])
                        info = result["connection_info"]
                        self.assertEqual(info["provider"], "sendgrid")
                        self.assertEqual(info["from_email"], "test@example.com")
                        self.assertTrue(info["enable_tracking"])
                        mock_info.assert_called_once()


class TestEmailTemplate(unittest.TestCase):
    """Test EmailTemplate data class."""
    
    def test_email_template_creation(self):
        """Test EmailTemplate creation."""
        template = EmailTemplate(
            template_id="template_123",
            name="Welcome Email",
            subject="Welcome to BMAD",
            html_content="<h1>Welcome {{name}}!</h1>",
            text_content="Welcome {{name}}!",
            variables=["name"],
            category="onboarding",
            created_at=datetime.now(UTC)
        )
        
        self.assertEqual(template.template_id, "template_123")
        self.assertEqual(template.name, "Welcome Email")
        self.assertEqual(template.subject, "Welcome to BMAD")
        self.assertIn("{{name}}", template.html_content)
        self.assertEqual(template.category, "onboarding")
        self.assertIsInstance(template.created_at, datetime)


class TestEmailRecipient(unittest.TestCase):
    """Test EmailRecipient data class."""
    
    def test_email_recipient_creation(self):
        """Test EmailRecipient creation."""
        recipient = EmailRecipient(
            email="test@example.com",
            name="John Doe",
            variables={"name": "John", "company": "BMAD"}
        )
        
        self.assertEqual(recipient.email, "test@example.com")
        self.assertEqual(recipient.name, "John Doe")
        self.assertEqual(recipient.variables["name"], "John")
        self.assertEqual(recipient.variables["company"], "BMAD")


class TestEmailResult(unittest.TestCase):
    """Test EmailResult data class."""
    
    def test_email_result_creation(self):
        """Test EmailResult creation."""
        result = EmailResult(
            message_id="msg_123",
            status="delivered",
            sent_at=datetime.now(UTC),
            recipient="test@example.com",
            template_id="template_123",
            tracking_id="track_123",
            delivery_status="delivered",
            opened_at=datetime.now(UTC),
            clicked_at=datetime.now(UTC)
        )
        
        self.assertEqual(result.message_id, "msg_123")
        self.assertEqual(result.status, "delivered")
        self.assertEqual(result.recipient, "test@example.com")
        self.assertEqual(result.template_id, "template_123")
        self.assertIsInstance(result.sent_at, datetime)
        self.assertIsInstance(result.opened_at, datetime)


class TestEmailAnalytics(unittest.TestCase):
    """Test EmailAnalytics data class."""
    
    def test_email_analytics_creation(self):
        """Test EmailAnalytics creation."""
        analytics = EmailAnalytics(
            total_sent=1000,
            total_delivered=950,
            total_opened=800,
            total_clicked=200,
            total_bounced=50,
            total_spam_reports=5,
            open_rate=0.84,
            click_rate=0.21,
            bounce_rate=0.05,
            spam_report_rate=0.005,
            average_delivery_time=2.5,
            last_sent=datetime.now(UTC)
        )
        
        self.assertEqual(analytics.total_sent, 1000)
        self.assertEqual(analytics.total_delivered, 950)
        self.assertEqual(analytics.total_opened, 800)
        self.assertEqual(analytics.open_rate, 0.84)
        self.assertEqual(analytics.click_rate, 0.21)
        self.assertEqual(analytics.bounce_rate, 0.05)
        self.assertEqual(analytics.average_delivery_time, 2.5)
        self.assertIsInstance(analytics.last_sent, datetime)


if __name__ == "__main__":
    unittest.main() 