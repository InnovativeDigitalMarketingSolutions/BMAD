import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
channel = "C097FTDU1A5"  # Vervang door jouw channel ID

response = requests.get(
    "https://slack.com/api/conversations.members",
    headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
    params={"channel": channel}
)
print("Status:", response.status_code)
print("Response:", response.text) 