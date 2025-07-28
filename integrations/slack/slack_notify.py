import logging
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def send_slack_message(text, channel=None, feedback_id=None, use_api=False, blocks=None):
    """
    Stuur een bericht naar Slack via webhook of chat.postMessage API.
    :param text: Berichttekst (str)
    :param channel: Slack-kanaal of user-id (str)
    :param feedback_id: Optioneel, unieke id voor feedback tracking
    :param use_api: Gebruik Slack API (chat.postMessage) i.p.v. webhook
    :param blocks: Optioneel, Slack Block Kit blocks (list)
    """
    if use_api:
        if not SLACK_BOT_TOKEN:
            raise ValueError("SLACK_BOT_TOKEN is niet ingesteld!")
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {"text": text}
        if channel:
            payload["channel"] = channel
        if blocks:
            payload["blocks"] = blocks
        elif feedback_id:
            payload["blocks"] = _feedback_blocks(text, feedback_id)
        # Debug prints
        print("DEBUG SLACK_BOT_TOKEN:", os.getenv("SLACK_BOT_TOKEN"))
        print("DEBUG channel:", channel)
        print("DEBUG type(channel):", type(channel))
        print("DEBUG repr(channel):", repr(channel))
        response = requests.post(url, headers=headers, json=payload)
        print("[Slack API] Response:", response.status_code, response.text)
        if not response.ok or not response.json().get("ok"):
            raise Exception(f"[Slack] Notificatie mislukt: {response.status_code} {response.text}")
        logging.info("[Slack] Notificatie verzonden via chat.postMessage.")
    else:
        if not SLACK_WEBHOOK_URL:
            raise ValueError("SLACK_WEBHOOK_URL is niet ingesteld!")
        payload = {"text": text}
        if channel:
            payload["channel"] = channel
        if blocks:
            payload["blocks"] = blocks
        elif feedback_id:
            payload["blocks"] = _feedback_blocks(text, feedback_id)
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        print("[Slack Webhook] Response:", response.status_code, response.text)
        if response.status_code != 200:
            raise Exception(f"[Slack] Webhook notificatie mislukt: {response.status_code} {response.text}")
        logging.info("[Slack] Notificatie verzonden via webhook.")

def _feedback_blocks(text, feedback_id):
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        {"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": ":thumbsup:"}, "value": f"up_{feedback_id}", "action_id": "feedback_up"},
            {"type": "button", "text": {"type": "plain_text", "text": ":thumbsdown:"}, "value": f"down_{feedback_id}", "action_id": "feedback_down"}
        ]}
    ]

def send_human_in_loop_alert(reason, channel=None, user_mention=None, alert_id=None, use_api=True):
    """
    Stuur een human-in-the-loop alert naar Slack met goedkeur/afwijs knoppen.
    :param reason: Reden voor human-in-the-loop (str)
    :param channel: Slack-kanaal of user-id (str)
    :param user_mention: Optioneel, Slack user-id of @mention (str)
    :param alert_id: Unieke id voor deze alert (str)
    :param use_api: Gebruik Slack API (chat.postMessage)
    """
    if not alert_id:
        import uuid
        alert_id = str(uuid.uuid4())
    mention_text = f"<@{user_mention}> " if user_mention else ""
    text = f":rotating_light: *Human-in-the-loop vereist!* {mention_text}{reason}"
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        {"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "✅ Goedkeuren"}, "style": "primary", "value": f"approve_{alert_id}", "action_id": "hitl_approve"},
            {"type": "button", "text": {"type": "plain_text", "text": "❌ Afwijzen"}, "style": "danger", "value": f"reject_{alert_id}", "action_id": "hitl_reject"}
        ]}
    ]
    send_slack_message(text, channel=channel, use_api=use_api, blocks=blocks)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = "BMAD notificatie: testbericht."
    send_slack_message(msg)
    # send_slack_message(msg, channel="#algemeen", use_api=True)
    # send_slack_message("Geef feedback op deze actie:", channel="#algemeen", feedback_id="test123", use_api=True)
    if len(sys.argv) > 1 and sys.argv[1] == "hitl":
        send_human_in_loop_alert(
            reason="Er is handmatige review nodig voor deze deployment.",
            channel="#devops-alerts",
            user_mention=None,
            alert_id="demo123"
        )
