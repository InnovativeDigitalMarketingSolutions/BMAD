import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
channel = "C097FTDU1A5"  # Vervang door jouw channel ID
text = "Testbericht van bot (losse API-call)"

response = requests.post(
    "https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
    json={"channel": channel, "text": text}
)
print("Status:", response.status_code)
print("Response:", response.text) 