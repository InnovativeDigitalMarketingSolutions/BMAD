import os
import requests
import pytest

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")

def test_slack_post():
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
        json={"channel": channel, "text": "Testbericht van bot (API-call)"}
    )
    assert response.status_code == 200
    assert response.json().get("ok") 