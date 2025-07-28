"""
Tests for webhook notification system.
"""

import os
from unittest.mock import patch, MagicMock
from bmad.agents.core.webhook_notify import (
    WebhookNotifier, 
    send_webhook_message,
    send_webhook_hitl_alert,
    send_webhook_workflow_notification
)

class TestWebhookNotifier:
    """Test webhook notification functionality."""
    
    def test_initialization(self):
        """Test webhook notifier initialization."""
        with patch.dict(os.environ, {}, clear=True):
            notifier = WebhookNotifier()
            assert notifier.webhook_urls == {}
            assert notifier.default_channel == "general"
    
    def test_load_webhook_config(self):
        """Test webhook configuration loading."""
        with patch.dict(os.environ, {
            "WEBHOOK_URL": "https://example.com/webhook",
            "WEBHOOK_URL_ALERTS": "https://example.com/alerts",
            "WEBHOOK_DEFAULT_CHANNEL": "test-channel"
        }):
            notifier = WebhookNotifier()
            assert notifier.webhook_urls["default"] == "https://example.com/webhook"
            assert notifier.webhook_urls["alerts"] == "https://example.com/alerts"
            assert notifier.default_channel == "test-channel"
    
    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """Test successful message sending."""
        with patch.dict(os.environ, {"WEBHOOK_URL": "https://example.com/webhook"}):
            notifier = WebhookNotifier()
            
            # Mock successful response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = notifier.send_message("Test message", "test-channel")
            
            assert result is True
            mock_post.assert_called_once()
            
            # Check payload
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://example.com/webhook"
            payload = call_args[1]['json']
            assert payload['text'] == "Test message"
            assert payload['channel'] == "test-channel"
            assert payload['source'] == "BMAD"
    
    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        """Test message sending failure."""
        with patch.dict(os.environ, {"WEBHOOK_URL": "https://example.com/webhook"}):
            notifier = WebhookNotifier()
            
            # Mock failed response
            mock_post.side_effect = Exception("Network error")
            
            result = notifier.send_message("Test message")
            
            assert result is False
    
    def test_send_message_no_webhook_configured(self):
        """Test message sending when no webhook is configured."""
        with patch.dict(os.environ, {}, clear=True):
            notifier = WebhookNotifier()
            result = notifier.send_message("Test message")
            assert result is False
    
    def test_send_message_use_api_false(self):
        """Test message sending with use_api=False."""
        with patch.dict(os.environ, {}, clear=True):
            notifier = WebhookNotifier()
            result = notifier.send_message("Test message", use_api=False)
            assert result is True
    
    def test_send_hitl_alert(self):
        """Test HITL alert sending."""
        with patch.dict(os.environ, {"WEBHOOK_URL": "https://example.com/webhook"}):
            notifier = WebhookNotifier()
            
            with patch.object(notifier, 'send_message') as mock_send:
                mock_send.return_value = True
                
                result = notifier.send_human_in_loop_alert(
                    "Test HITL reason",
                    "test-channel",
                    "test-user",
                    "alert-123"
                )
                
                assert result is True
                mock_send.assert_called_once()
                
                # Check the message content
                call_args = mock_send.call_args
                message = call_args[0][0]
                assert "Human-in-the-Loop Alert" in message
                assert "Test HITL reason" in message
                assert "test-user" in message
                assert "alert-123" in message
    
    def test_send_workflow_notification(self):
        """Test workflow notification sending."""
        with patch.dict(os.environ, {"WEBHOOK_URL": "https://example.com/webhook"}):
            notifier = WebhookNotifier()
            
            with patch.object(notifier, 'send_message') as mock_send:
                mock_send.return_value = True
                
                result = notifier.send_workflow_notification(
                    "test-workflow",
                    "completed",
                    "test-channel"
                )
                
                assert result is True
                mock_send.assert_called_once()
                
                # Check the message content
                call_args = mock_send.call_args
                message = call_args[0][0]
                assert "Workflow Update" in message
                assert "test-workflow" in message
                assert "completed" in message
                assert "✅" in message  # Status emoji

class TestWebhookConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('bmad.agents.core.webhook_notify.webhook_notifier')
    def test_send_webhook_message(self, mock_notifier):
        """Test send_webhook_message convenience function."""
        mock_notifier.send_message.return_value = True
        
        result = send_webhook_message("Test message", "test-channel")
        
        assert result is True
        mock_notifier.send_message.assert_called_once_with(
            "Test message", "test-channel", True
        )
    
    @patch('bmad.agents.core.webhook_notify.webhook_notifier')
    def test_send_webhook_hitl_alert(self, mock_notifier):
        """Test send_webhook_hitl_alert convenience function."""
        mock_notifier.send_human_in_loop_alert.return_value = True
        
        result = send_webhook_hitl_alert(
            "Test reason", "test-channel", "test-user", "alert-123"
        )
        
        assert result is True
        mock_notifier.send_human_in_loop_alert.assert_called_once_with(
            "Test reason", "test-channel", "test-user", "alert-123", True
        )
    
    @patch('bmad.agents.core.webhook_notify.webhook_notifier')
    def test_send_webhook_workflow_notification(self, mock_notifier):
        """Test send_webhook_workflow_notification convenience function."""
        mock_notifier.send_workflow_notification.return_value = True
        
        result = send_webhook_workflow_notification(
            "test-workflow", "started", "test-channel"
        )
        
        assert result is True
        mock_notifier.send_workflow_notification.assert_called_once_with(
            "test-workflow", "started", "test-channel", True
        )

class TestWebhookIntegration:
    """Test webhook integration scenarios."""
    
    @patch('requests.post')
    def test_full_webhook_workflow(self, mock_post):
        """Test a complete webhook workflow."""
        with patch.dict(os.environ, {
            "WEBHOOK_URL": "https://example.com/webhook",
            "WEBHOOK_URL_ALERTS": "https://example.com/alerts"
        }):
            # Mock successful responses
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Create fresh notifier instance with new environment
            from bmad.agents.core.webhook_notify import WebhookNotifier
            notifier = WebhookNotifier()
            
            # Test workflow notification
            result1 = notifier.send_workflow_notification(
                "feature-development", "started", "general"
            )
            assert result1 is True
            
            # Test HITL alert
            result2 = notifier.send_human_in_loop_alert(
                "Deployment approval required",
                "alerts",
                "admin",
                "deploy-123"
            )
            assert result2 is True
            
            # Test regular message
            result3 = notifier.send_message(
                "Workflow completed successfully",
                "general"
            )
            assert result3 is True
            
            # Verify all calls were made
            assert mock_post.call_count == 3 