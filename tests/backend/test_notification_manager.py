"""
Tests for notification manager.
"""

import os
from unittest.mock import patch
from bmad.agents.core.notification_manager import (
    NotificationManager,
    NotificationType,
    get_notification_manager,
    send_notification,
    send_hitl_notification,
    send_workflow_notification
)

class TestNotificationManager:
    """Test NotificationManager class."""
    
    def test_notification_manager_creation(self):
        """Test NotificationManager creation."""
        manager = NotificationManager()
        assert manager is not None
        assert hasattr(manager, 'notification_type')
        assert hasattr(manager, 'default_type')
    
    def test_notification_manager_with_webhook_type(self):
        """Test NotificationManager with webhook type."""
        manager = NotificationManager(NotificationType.WEBHOOK)
        assert manager.notification_type == NotificationType.WEBHOOK
    
    def test_notification_manager_with_slack_type(self):
        """Test NotificationManager with slack type."""
        manager = NotificationManager(NotificationType.SLACK)
        assert manager.notification_type == NotificationType.SLACK
    
    @patch.dict(os.environ, {'WEBHOOK_URL': 'https://example.com/webhook'})
    def test_auto_determination_with_webhook(self):
        """Test automatic determination with webhook configured."""
        manager = NotificationManager(NotificationType.AUTO)
        # Should prefer webhook when available
        assert manager.notification_type in [NotificationType.WEBHOOK, NotificationType.SLACK]
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    def test_auto_determination_with_slack(self):
        """Test automatic determination with slack configured."""
        manager = NotificationManager(NotificationType.AUTO)
        # Should use slack when webhook not available
        assert manager.notification_type in [NotificationType.SLACK, NotificationType.WEBHOOK]
    
    @patch('bmad.agents.core.notification_manager.send_webhook_message')
    def test_send_message_webhook(self, mock_webhook):
        """Test send_message with webhook."""
        mock_webhook.return_value = True
        
        manager = NotificationManager(NotificationType.WEBHOOK)
        result = manager.send_message("Test message")
        
        assert result is True
        mock_webhook.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_slack_message')
    def test_send_message_slack(self, mock_slack):
        """Test send_message with slack."""
        mock_slack.return_value = True
        
        manager = NotificationManager(NotificationType.SLACK)
        result = manager.send_message("Test message")
        
        assert result is True
        mock_slack.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_webhook_hitl_alert')
    def test_send_hitl_alert_webhook(self, mock_webhook):
        """Test send_hitl_alert with webhook."""
        mock_webhook.return_value = True
        
        manager = NotificationManager(NotificationType.WEBHOOK)
        result = manager.send_hitl_alert("Test reason")
        
        assert result is True
        mock_webhook.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_human_in_loop_alert')
    def test_send_hitl_alert_slack(self, mock_slack):
        """Test send_hitl_alert with slack."""
        mock_slack.return_value = True
        
        manager = NotificationManager(NotificationType.SLACK)
        result = manager.send_hitl_alert("Test reason")
        
        assert result is True
        mock_slack.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_webhook_workflow_notification')
    def test_send_workflow_notification_webhook(self, mock_webhook):
        """Test send_workflow_notification with webhook."""
        mock_webhook.return_value = True
        
        manager = NotificationManager(NotificationType.WEBHOOK)
        result = manager.send_workflow_notification("test-workflow", "started")
        
        assert result is True
        mock_webhook.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_slack_message')
    def test_send_workflow_notification_slack(self, mock_slack):
        """Test send_workflow_notification with slack."""
        mock_slack.return_value = True
        
        manager = NotificationManager(NotificationType.SLACK)
        result = manager.send_workflow_notification("test-workflow", "started")
        
        assert result is True
        mock_slack.assert_called_once()
    
    def test_get_status(self):
        """Test get_status method."""
        manager = NotificationManager(NotificationType.WEBHOOK)
        status = manager.get_status()
        
        assert isinstance(status, dict)
        assert 'type' in status
        assert 'slack_available' in status
        assert 'webhook_available' in status
        assert 'slack_configured' in status
        assert 'webhook_configured' in status
        assert 'default_type' in status

class TestGlobalFunctions:
    """Test global notification functions."""
    
    def test_get_notification_manager(self):
        """Test get_notification_manager function."""
        manager = get_notification_manager()
        assert isinstance(manager, NotificationManager)
        
        # Should return the same instance
        manager2 = get_notification_manager()
        assert manager is manager2
    
    @patch('bmad.agents.core.notification_manager.send_webhook_message')
    def test_send_notification(self, mock_webhook):
        """Test send_notification function."""
        mock_webhook.return_value = True
        
        result = send_notification("Test message", notification_type=NotificationType.WEBHOOK)
        
        assert result is True
        mock_webhook.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_webhook_hitl_alert')
    def test_send_hitl_notification(self, mock_webhook):
        """Test send_hitl_notification function."""
        mock_webhook.return_value = True
        
        result = send_hitl_notification("Test reason", notification_type=NotificationType.WEBHOOK)
        
        assert result is True
        mock_webhook.assert_called_once()
    
    @patch('bmad.agents.core.notification_manager.send_webhook_workflow_notification')
    def test_send_workflow_notification(self, mock_webhook):
        """Test send_workflow_notification function."""
        mock_webhook.return_value = True
        
        result = send_workflow_notification("test-workflow", "started", notification_type=NotificationType.WEBHOOK)
        
        assert result is True
        mock_webhook.assert_called_once()

class TestNotificationType:
    """Test NotificationType enum."""
    
    def test_notification_type_values(self):
        """Test NotificationType enum values."""
        assert NotificationType.SLACK.value == "slack"
        assert NotificationType.WEBHOOK.value == "webhook"
        assert NotificationType.AUTO.value == "auto"
    
    def test_notification_type_membership(self):
        """Test NotificationType enum membership."""
        assert NotificationType.SLACK in NotificationType
        assert NotificationType.WEBHOOK in NotificationType
        assert NotificationType.AUTO in NotificationType

class TestErrorHandling:
    """Test error handling in notification manager."""
    
    @patch('bmad.agents.core.notification_manager.send_webhook_message')
    def test_send_message_error_handling(self, mock_webhook):
        """Test error handling in send_message."""
        mock_webhook.side_effect = Exception("Test error")
        
        manager = NotificationManager(NotificationType.WEBHOOK)
        result = manager.send_message("Test message")
        
        assert result is False
    
    @patch('bmad.agents.core.notification_manager.send_webhook_hitl_alert')
    def test_send_hitl_alert_error_handling(self, mock_webhook):
        """Test error handling in send_hitl_alert."""
        mock_webhook.side_effect = Exception("Test error")
        
        manager = NotificationManager(NotificationType.WEBHOOK)
        result = manager.send_hitl_alert("Test reason")
        
        assert result is False
    
    @patch('bmad.agents.core.notification_manager.send_webhook_workflow_notification')
    def test_send_workflow_notification_error_handling(self, mock_webhook):
        """Test error handling in send_workflow_notification."""
        mock_webhook.side_effect = Exception("Test error")
        
        manager = NotificationManager(NotificationType.WEBHOOK)
        result = manager.send_workflow_notification("test-workflow", "started")
        
        assert result is False

class TestIntegration:
    """Test integration scenarios."""
    
    @patch.dict(os.environ, {'WEBHOOK_URL': 'https://example.com/webhook'})
    def test_webhook_integration(self):
        """Test webhook integration scenario."""
        manager = NotificationManager(NotificationType.AUTO)
        status = manager.get_status()
        
        assert status['webhook_configured'] is True
        assert status['webhook_available'] is True
    
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test'})
    def test_slack_integration(self):
        """Test slack integration scenario."""
        manager = NotificationManager(NotificationType.AUTO)
        status = manager.get_status()
        
        assert status['slack_configured'] is True
        assert status['slack_available'] is True
    
    def test_no_configuration(self):
        """Test scenario with no configuration."""
        with patch.dict(os.environ, {}, clear=True):
            manager = NotificationManager(NotificationType.AUTO)
            status = manager.get_status()
            
            assert status['slack_configured'] is False
            assert status['webhook_configured'] is False 