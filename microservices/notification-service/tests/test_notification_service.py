#!/usr/bin/env python3
"""
Comprehensive Test Suite voor Notification Service
Unit tests voor alle core services en API endpoints
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Import services
from src.core.database import DatabaseService
from src.core.template import TemplateService
from src.core.email import EmailService
from src.core.sms import SMSService
from src.core.slack import SlackService
from src.core.webhook import WebhookService
from src.core.delivery import DeliveryService, DeliveryRequest, BulkDeliveryRequest
from src.core.analytics import AnalyticsService, AnalyticsRequest

# Import main app
from src.main import app

# Test client
client = TestClient(app)

class TestDatabaseService:
    """Test DatabaseService functionality."""
    
    @pytest.fixture
    async def db_service(self):
        """Create database service instance."""
        service = DatabaseService()
        yield service
        await service.close()
    
    @pytest.mark.asyncio
    async def test_initialize(self, db_service):
        """Test database service initialization."""
        # Mock database connection
        with patch.object(db_service, '_create_engine') as mock_engine:
            mock_engine.return_value = MagicMock()
            await db_service.initialize()
            mock_engine.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_template(self, db_service):
        """Test template creation."""
        template_data = {
            "name": "Test Template",
            "content": "Hello {{name}}!",
            "channel": "email"
        }
        
        with patch.object(db_service, 'get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = AsyncMock()
            template_id = await db_service.create_template(template_data)
            assert template_id is not None
    
    @pytest.mark.asyncio
    async def test_get_template(self, db_service):
        """Test template retrieval."""
        template_id = "test-template-id"
        
        with patch.object(db_service, 'get_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = AsyncMock()
            template = await db_service.get_template(template_id)
            assert template is not None

class TestTemplateService:
    """Test TemplateService functionality."""
    
    @pytest.fixture
    def template_service(self):
        """Create template service instance."""
        db_service = MagicMock()
        return TemplateService(db_service)
    
    @pytest.mark.asyncio
    async def test_render_template(self, template_service):
        """Test template rendering."""
        template_id = "test-template"
        context = {"name": "John"}
        
        # Mock template retrieval
        template_service.db_service.get_template.return_value = {
            "content": "Hello {{name}}!",
            "channel": "email"
        }
        
        result = await template_service.render_template(template_id, context)
        assert result == "Hello John!"
    
    @pytest.mark.asyncio
    async def test_validate_template(self, template_service):
        """Test template validation."""
        template_content = "Hello {{name}}!"
        context = {"name": "John"}
        
        result = await template_service.validate_template(template_content, context)
        assert result["valid"] is True

class TestEmailService:
    """Test EmailService functionality."""
    
    @pytest.fixture
    def email_service(self):
        """Create email service instance."""
        db_service = MagicMock()
        return EmailService(db_service)
    
    @pytest.mark.asyncio
    async def test_send_notification(self, email_service):
        """Test email notification sending."""
        recipient = "test@example.com"
        content = "Test email content"
        metadata = {"subject": "Test Subject"}
        
        with patch('src.core.email.sendgrid.SendGridAPIClient') as mock_sendgrid:
            mock_client = MagicMock()
            mock_sendgrid.return_value = mock_client
            mock_client.send.return_value = MagicMock(status_code=202)
            
            result = await email_service.send_notification(recipient, content, metadata)
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_test_connection(self, email_service):
        """Test email connection testing."""
        test_data = {"api_key": "test-key"}
        
        with patch('src.core.email.sendgrid.SendGridAPIClient') as mock_sendgrid:
            mock_client = MagicMock()
            mock_sendgrid.return_value = mock_client
            mock_client.send.return_value = MagicMock(status_code=202)
            
            result = await email_service.test_connection(test_data)
            assert result["success"] is True

class TestSMSService:
    """Test SMSService functionality."""
    
    @pytest.fixture
    def sms_service(self):
        """Create SMS service instance."""
        db_service = MagicMock()
        return SMSService(db_service)
    
    @pytest.mark.asyncio
    async def test_send_notification(self, sms_service):
        """Test SMS notification sending."""
        recipient = "+1234567890"
        content = "Test SMS content"
        metadata = {}
        
        with patch('src.core.sms.Client') as mock_twilio:
            mock_client = MagicMock()
            mock_twilio.return_value = mock_client
            mock_client.messages.create.return_value = MagicMock(sid="test-sid")
            
            result = await sms_service.send_notification(recipient, content, metadata)
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_validate_phone_number(self, sms_service):
        """Test phone number validation."""
        phone_number = "+1234567890"
        
        result = await sms_service.validate_phone_number(phone_number)
        assert result["valid"] is True

class TestSlackService:
    """Test SlackService functionality."""
    
    @pytest.fixture
    def slack_service(self):
        """Create Slack service instance."""
        db_service = MagicMock()
        return SlackService(db_service)
    
    @pytest.mark.asyncio
    async def test_send_notification(self, slack_service):
        """Test Slack notification sending."""
        recipient = "#test-channel"
        content = "Test Slack message"
        metadata = {"webhook_url": "https://hooks.slack.com/test"}
        
        with patch('src.core.slack.aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await slack_service.send_notification(recipient, content, metadata)
            assert result["success"] is True

class TestWebhookService:
    """Test WebhookService functionality."""
    
    @pytest.fixture
    def webhook_service(self):
        """Create webhook service instance."""
        db_service = MagicMock()
        return WebhookService(db_service)
    
    @pytest.mark.asyncio
    async def test_send_notification(self, webhook_service):
        """Test webhook notification sending."""
        recipient = "https://api.example.com/webhook"
        content = {"message": "Test webhook"}
        metadata = {"method": "POST"}
        
        with patch('src.core.webhook.aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await webhook_service.send_notification(recipient, content, metadata)
            assert result["success"] is True

class TestDeliveryService:
    """Test DeliveryService functionality."""
    
    @pytest.fixture
    def delivery_service(self):
        """Create delivery service instance."""
        db_service = MagicMock()
        return DeliveryService(db_service)
    
    @pytest.mark.asyncio
    async def test_deliver_notification(self, delivery_service):
        """Test single notification delivery."""
        request = DeliveryRequest(
            template_id="test-template",
            channel="email",
            recipient="test@example.com",
            context={"name": "John"}
        )
        
        # Mock template service
        delivery_service.template_service.render_template.return_value = "Hello John!"
        
        # Mock email service
        delivery_service.email_service.send_notification.return_value = {
            "success": True,
            "message_id": "test-message-id"
        }
        
        # Mock database operations
        delivery_service.db_service.create_delivery.return_value = "test-delivery-id"
        
        result = await delivery_service.deliver_notification(request)
        assert result.status.value == "delivered"
    
    @pytest.mark.asyncio
    async def test_deliver_bulk_notifications(self, delivery_service):
        """Test bulk notification delivery."""
        request = BulkDeliveryRequest(
            template_id="test-template",
            channel="email",
            recipients=["test1@example.com", "test2@example.com"],
            context={"name": "John"}
        )
        
        # Mock template service
        delivery_service.template_service.render_template.return_value = "Hello John!"
        
        # Mock email service
        delivery_service.email_service.send_notification.return_value = {
            "success": True,
            "message_id": "test-message-id"
        }
        
        # Mock database operations
        delivery_service.db_service.create_batch.return_value = "test-batch-id"
        delivery_service.db_service.create_delivery.return_value = "test-delivery-id"
        
        result = await delivery_service.deliver_bulk_notifications(request)
        assert result.total_recipients == 2
        assert result.successful_deliveries == 2

class TestAnalyticsService:
    """Test AnalyticsService functionality."""
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance."""
        db_service = MagicMock()
        return AnalyticsService(db_service)
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, analytics_service):
        """Test performance metrics retrieval."""
        # Mock database statistics
        analytics_service.db_service.get_delivery_statistics.return_value = {
            "total_deliveries": 100,
            "successful_deliveries": 95,
            "failed_deliveries": 5,
            "average_response_time": 1.5,
            "throughput_per_hour": 50,
            "retry_rate": 2.0
        }
        
        metrics = await analytics_service.get_performance_metrics()
        assert metrics.total_deliveries == 100
        assert metrics.delivery_rate == 95.0
    
    @pytest.mark.asyncio
    async def test_get_channel_performance(self, analytics_service):
        """Test channel performance retrieval."""
        # Mock channel statistics
        analytics_service.db_service.get_channel_statistics.return_value = {
            "email": {
                "total_deliveries": 50,
                "successful_deliveries": 48,
                "failed_deliveries": 2,
                "average_response_time": 1.0,
                "error_breakdown": {"timeout": 1, "invalid_email": 1}
            }
        }
        
        performance = await analytics_service.get_channel_performance()
        assert len(performance) == 1
        assert performance[0].channel == "email"
        assert performance[0].delivery_rate == 96.0

class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_readiness_check(self):
        """Test readiness check endpoint."""
        response = client.get("/health/ready")
        assert response.status_code == 200
    
    def test_liveness_check(self):
        """Test liveness check endpoint."""
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
    
    def test_create_template(self):
        """Test template creation endpoint."""
        template_data = {
            "name": "Test Template",
            "content": "Hello {{name}}!",
            "channel": "email"
        }
        
        with patch('src.main.TemplateService') as mock_template_service:
            mock_service = MagicMock()
            mock_template_service.return_value = mock_service
            mock_service.create_template.return_value = "test-template-id"
            
            response = client.post("/templates", json=template_data)
            assert response.status_code == 200
            assert response.json()["template_id"] == "test-template-id"
    
    def test_deliver_notification(self):
        """Test notification delivery endpoint."""
        delivery_request = {
            "template_id": "test-template",
            "channel": "email",
            "recipient": "test@example.com",
            "context": {"name": "John"}
        }
        
        with patch('src.main.DeliveryService') as mock_delivery_service:
            mock_service = MagicMock()
            mock_delivery_service.return_value = mock_service
            mock_service.deliver_notification.return_value = MagicMock(
                delivery_id="test-delivery-id",
                status=MagicMock(value="delivered"),
                message="Success"
            )
            
            response = client.post("/deliver", json=delivery_request)
            assert response.status_code == 200
    
    def test_get_performance_metrics(self):
        """Test performance metrics endpoint."""
        with patch('src.main.AnalyticsService') as mock_analytics_service:
            mock_service = MagicMock()
            mock_analytics_service.return_value = mock_service
            mock_service.get_performance_metrics.return_value = MagicMock(
                total_deliveries=100,
                successful_deliveries=95,
                failed_deliveries=5,
                delivery_rate=95.0,
                average_response_time=1.5,
                throughput_per_hour=50,
                retry_rate=2.0
            )
            
            response = client.get("/analytics/performance")
            assert response.status_code == 200

class TestErrorHandling:
    """Test error handling."""
    
    def test_validation_error(self):
        """Test validation error handling."""
        # Invalid delivery request
        invalid_request = {
            "template_id": "",  # Invalid empty template_id
            "channel": "invalid_channel",  # Invalid channel
            "recipient": ""  # Invalid empty recipient
        }
        
        response = client.post("/deliver", json=invalid_request)
        assert response.status_code == 400
    
    def test_not_found_error(self):
        """Test not found error handling."""
        response = client.get("/templates/non-existent-template")
        assert response.status_code == 404
    
    def test_internal_server_error(self):
        """Test internal server error handling."""
        with patch('src.main.TemplateService') as mock_template_service:
            mock_service = MagicMock()
            mock_template_service.return_value = mock_service
            mock_service.create_template.side_effect = Exception("Database error")
            
            response = client.post("/templates", json={"name": "Test"})
            assert response.status_code == 500

class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_delivery_flow(self):
        """Test complete delivery flow."""
        # This would test the full integration between services
        # For now, we'll test the orchestration
        db_service = MagicMock()
        delivery_service = DeliveryService(db_service)
        
        # Mock all dependencies
        delivery_service.template_service.render_template.return_value = "Hello World!"
        delivery_service.email_service.send_notification.return_value = {
            "success": True,
            "message_id": "test-id"
        }
        delivery_service.db_service.create_delivery.return_value = "delivery-id"
        
        request = DeliveryRequest(
            template_id="test-template",
            channel="email",
            recipient="test@example.com",
            context={"name": "World"}
        )
        
        result = await delivery_service.deliver_notification(request)
        assert result.status.value == "delivered"
        assert result.delivery_id == "delivery-id"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 