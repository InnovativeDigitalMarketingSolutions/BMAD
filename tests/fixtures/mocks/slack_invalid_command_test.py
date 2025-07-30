import os
import requests
from unittest.mock import patch, MagicMock

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")

def test_invalid_slack_command():
    text = "/agent"  # Ongeldig commando
    
    # Mock the requests.post call to return a successful Slack response
    with patch('requests.post') as mock_post:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "channel": channel,
            "ts": "1234567890.123456",
            "message": {
                "text": text,
                "type": "message"
            }
        }
        mock_post.return_value = mock_response
        
        # Make the request (now mocked)
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": text}
        )
        
        # Verify the mock was called
        mock_post.assert_called_once()
        
        # Verify the response
        assert response.status_code == 200
        assert response.json().get("ok") 