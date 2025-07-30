import os
import pytest
from integrations.slack.slack_notify import send_human_in_loop_alert
from unittest.mock import patch, MagicMock

def test_slack_hitl():
    channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
    
    # Mock the requests.post call to return a successful Slack response
    with patch('requests.post') as mock_post:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "channel": channel,
            "ts": "1234567890.123456"
        }
        mock_post.return_value = mock_response
        
        send_human_in_loop_alert(
            reason="Test HITL alert via script.",
            channel=channel,
            user_mention=None,
            alert_id="test-hitl-001",
            use_api=True
        )
        
        # Verify the mock was called
        mock_post.assert_called_once()
        assert True  # Test passed 