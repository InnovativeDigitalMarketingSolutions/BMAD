import os
import requests

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/your/webhook/url")


def send_slack_message(text, channel=None, feedback_id=None):
    """
    Stuur een bericht naar Slack via de ingestelde webhook. Optioneel met feedback buttons.
    :param text: Berichttekst (str)
    :param channel: Optioneel Slack-kanaal (str)
    :param feedback_id: Optioneel, unieke id voor feedback tracking
    """
    payload = {"text": text}
    if channel:
        payload["channel"] = channel
    if feedback_id:
        # Voeg Slack Block Kit buttons toe voor feedback
        payload["blocks"] = [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "actions", "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": ":thumbsup:"}, "value": f"up_{feedback_id}", "action_id": "feedback_up"},
                {"type": "button", "text": {"type": "plain_text", "text": ":thumbsdown:"}, "value": f"down_{feedback_id}", "action_id": "feedback_down"}
            ]}
        ]
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("Slack notificatie verzonden.")
    else:
        print(f"Slack notificatie mislukt: {response.status_code} {response.text}")

# Voorbeeld: endpoint voor feedback (te implementeren met Flask/FastAPI)
# @app.route('/slack/feedback', methods=['POST'])
# def handle_feedback():
#     data = request.json
#     feedback_id = data['actions'][0]['value']
#     feedback_type = 'up' if 'up_' in feedback_id else 'down'
#     # Log feedback, update prompt, etc.
#     return "", 200 