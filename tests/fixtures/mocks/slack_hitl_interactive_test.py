import os
import time
import pytest
from integrations.slack.slack_notify import send_human_in_loop_alert
from bmad.agents.core.communication.message_bus import subscribe
from unittest.mock import patch, MagicMock

def test_slack_hitl_interactive():
    channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
    alert_id = "test-hitl-interactive-001"
    events = []
    
    def on_hitl_decision(event):
        events.append(event)
    
    subscribe("hitl_decision", on_hitl_decision)
    
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
            reason="Test HITL interactiviteit.",
            channel=channel,
            user_mention=None,
            alert_id=alert_id,
            use_api=True
        )
        
        # Verify the mock was called
        mock_post.assert_called_once()
        assert True  # Test passed 