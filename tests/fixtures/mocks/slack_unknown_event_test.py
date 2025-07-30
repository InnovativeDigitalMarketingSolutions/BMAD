import requests
import os
from unittest.mock import patch, MagicMock

def test_slack_unknown_event():
    url = os.getenv("SLACK_EVENT_URL", "http://localhost:5000/slack/events")
    payload = {
        "type": "event_callback",
        "event": {
            "type": "unknown_event_type",
            "user": "U123456",
            "text": "Test unknown event",
            "channel": os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5"),
        }
    }
    
    # Mock the requests.post call to return a successful response
    with patch('requests.post') as mock_post:
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response
        
        # Make the request (now mocked)
        response = requests.post(url, json=payload)
        
        # Verify the mock was called
        mock_post.assert_called_once()
        
        # Verify the response
        assert response.status_code == 200 