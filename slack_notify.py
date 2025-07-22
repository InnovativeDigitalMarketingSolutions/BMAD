import requests
import sys

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/your/webhook/url"  # Vervang door je eigen webhook

def send_slack_message(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("Slack notificatie verzonden.")
    else:
        print(f"Slack notificatie mislukt: {response.status_code} {response.text}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = "BMAD notificatie: testbericht."
    send_slack_message(msg) 