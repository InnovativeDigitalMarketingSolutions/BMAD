import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

response = requests.get(
    "https://slack.com/api/conversations.list",
    headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
)
print("Status:", response.status_code)
print("Response:", response.text) 