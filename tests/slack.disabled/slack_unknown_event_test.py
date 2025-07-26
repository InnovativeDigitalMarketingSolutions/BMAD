import requests
import os
import pytest

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
    response = requests.post(url, json=payload)
    assert response.status_code == 200 