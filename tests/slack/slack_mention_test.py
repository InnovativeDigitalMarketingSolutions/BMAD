import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
channel = os.getenv("SLACK_TEST_CHANNEL", "C097FTDU1A5")
bot_user_id = os.getenv("SLACK_BOT_USER_ID")  # Zet deze in je .env

text = f"<@{bot_user_id}> help"

response = requests.post(
    "https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
    json={"channel": channel, "text": text}
)
print("Status:", response.status_code)
print("Response:", response.text) 