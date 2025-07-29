import hashlib
import hmac
import json
import logging
import os
import time

import requests
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, make_response, request

from bmad.agents.core.communication.message_bus import publish
from integrations.slack.slack_notify import send_slack_message

load_dotenv()

app = Flask(__name__)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="[%(levelname)s] %(message)s")

# (Optioneel) Slack bot token en signing secret uit env vars
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/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")

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

if not SLACK_BOT_TOKEN:
    raise RuntimeError("SLACK_BOT_TOKEN niet gezet!")

def verify_slack_signature(request):
    if not SLACK_SIGNING_SECRET:
        logging.warning("[Slack] Geen SLACK_SIGNING_SECRET ingesteld!")
        return True  # Voor dev, in prod: return False
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    if not timestamp or not slack_signature:
        return False
    # Voorkom replay attacks (optioneel: timestamp check)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        logging.warning("[Slack] Request timestamp te oud.")
        return False
    # Genereer signature
    req_body = request.get_data(as_text=True)
    basestring = f"v0:{timestamp}:{req_body}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(my_signature, slack_signature):
        logging.warning(f"[Slack] Ongeldige Slack signature! Verwacht: {my_signature}, Ontvangen: {slack_signature}")
        return False
    return True

# Voeg een set toe om recent verwerkte event_ts bij te houden
RECENT_EVENT_TS = set()

# Haal deduplicatie op event_id uit slack_events()
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    # Slack URL verification vóór signature check
    if data.get("type") == "url_verification" or "challenge" in data:
        return jsonify({"challenge": data.get("challenge")})
    if not verify_slack_signature(request):
        abort(401)
    logging.info(f"[Slack Event] Ontvangen: {data}")
    event = data.get("event", {})
    event_type = event.get("type")
    if not event_type:
        logging.warning("Geen event type gevonden in payload.")
        return "", 200
    # Event dispatcher
    if event_type == "message" or event_type == "app_mention":
        handle_message_event(event)
    elif event_type == "reaction_added":
        handle_reaction_event(event)
    else:
        logging.info(f"Onbekend event type: {event_type}")
    forward_event_to_agents(event)
    return "", 200

@app.route("/slack/interactivity", methods=["POST"])
def slack_interactivity():
    if not verify_slack_signature(request):
        abort(401)
    payload = request.form.get("payload")
    if not payload:
        return make_response("No payload", 400)
    data = json.loads(payload)
    user = data.get("user", {}).get("id")
    actions = data.get("actions", [])
    channel = data.get("channel", {}).get("id")
    response_url = data.get("response_url")
    if not actions:
        return make_response("No actions", 400)
    action = actions[0]
    action_id = action.get("action_id")
    value = action.get("value")
    # HITL acties verwerken
    if action_id in ("hitl_approve", "hitl_reject"):
        approved = action_id == "hitl_approve"
        alert_id = value.split("_", 1)[-1] if value else None
        logging.info(f"[HITL] User {user} {'keurde goed' if approved else 'wees af'} alert {alert_id}")
        # Publiceer event op message bus
        publish("hitl_decision", {
            "alert_id": alert_id,
            "approved": approved,
            "user": user,
            "channel": channel
        })
        # Stuur bevestiging terug naar Slack
        msg = f"{'✅ Actie goedgekeurd' if approved else '❌ Actie afgewezen'} door <@{user}>."
        requests.post(response_url, json={"text": msg, "replace_original": True})
        return make_response("", 200)
    return make_response("Onbekende actie", 200)

def handle_message_event(event):
    # Negeer berichten van bots (inclusief jezelf)
    if event.get("subtype") == "bot_message" or event.get("bot_id"):
        return
    # Deduplicatie op event_ts
    event_ts = event.get("ts")
    if event_ts:
        if event_ts in RECENT_EVENT_TS:
            logging.info(f"[Deduplicatie] Event met ts {event_ts} al verwerkt, sla over.")
            return
        RECENT_EVENT_TS.add(event_ts)
        if len(RECENT_EVENT_TS) > 1000:
            RECENT_EVENT_TS.pop()
    user = event.get("user")
    text = event.get("text") or ""
    channel = event.get("channel")
    mention = f"<@{user}>" if user else "gebruiker"
    logging.info(f"[Slack] Bericht van {user} in {channel}: {text}")
    # Testreactie naar Slack
    send_slack_message(f"👋 Hallo {mention}! Je bericht '{text}' is ontvangen.", channel, use_api=True)
    # Command parsing: herken /agent <agentnaam> <commando> of @agentnaam <commando>
    if text:
        import re
        # /agent <agentnaam> <commando>
        match = re.match(r"^/agent\\s+(\\w+)\\s+(.+)$", text.strip(), re.IGNORECASE)
        # @agentnaam <commando>
        mention_match = re.match(r"^<@([A-Z0-9]+)>\\s+(.+)$", text.strip())
        if match:
            agent_name = match.group(1)
            command = match.group(2)
            logging.info(f"[Command Parsing] Commando voor agent '{agent_name}': {command}")
            # Routering naar agent via message bus
            publish("slack_command", {
                "agent": agent_name,
                "command": command,
                "user": user,
                "channel": channel
            })
            send_slack_message(f"Commando ontvangen voor agent '{agent_name}': {command}", channel, use_api=True)
            return
        if mention_match:
            # Optioneel: lookup Slack user ID naar agentnaam
            mentioned_id = mention_match.group(1)
            command = mention_match.group(2)
            logging.info(f"[Command Parsing] Mentioned agent ID '{mentioned_id}' met commando: {command}")
            publish("slack_command", {
                "agent_id": mentioned_id,
                "command": command,
                "user": user,
                "channel": channel
            })
            send_slack_message(f"Commando ontvangen voor agent ID '{mentioned_id}': {command}", channel, use_api=True)
            return
        # Voorbeeld: automatisch reageren op een triggerwoord
        if "hallo agent" in text.lower():
            send_slack_message("👋 Hallo! Ik ben een BMAD agent.", channel, use_api=True)


def handle_reaction_event(event):
    user = event.get("user")
    reaction = event.get("reaction")
    item = event.get("item", {})
    logging.info(f"[Slack] {user} voegde :{reaction}: toe aan {item}")
    # Voorbeeld: stuur een notificatie naar een agent of log het


def forward_event_to_agents(event):
    # Stub: hier kun je events doorsturen naar andere agenten of message bus
    logging.info(f"[Router] Event doorsturen naar andere agenten: {event}")
    # Voorbeeld: message_bus.publish('slack_event', event)


def send_message_to_slack(channel, text):
    # Stuur een bericht naar Slack via chat.postMessage API (vereist bot token)
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        logging.info(f"[Slack] Bericht verstuurd naar {channel}")
    else:
        logging.error(f"[Slack] Fout bij versturen bericht: {response.text}")

if __name__ == "__main__":
    print("Start Slack event server op http://localhost:5000/slack/events")
    print("Gebruik ngrok om deze endpoint publiek te maken:")
    print("  ngrok http 5000")
    app.run(host="0.0.0.0", port=5000)
