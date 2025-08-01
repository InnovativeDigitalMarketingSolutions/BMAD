import os
import pytest
from integrations.slack.slack_notify import send_slack_message
from unittest.mock import patch, MagicMock

def test_agent_notify():
    channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
    
    # Mock DEV_MODE to be False so Slack notifications are sent
    with patch.dict('os.environ', {'DEV_MODE': 'false', 'SLACK_BOT_TOKEN': 'test_token'}):
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
            
            send_slack_message("Testnotificatie vanuit agent_notify_test.py", channel, use_api=True)
            
            # Verify the mock was called
            mock_post.assert_called_once()
            assert True  # Test passed 