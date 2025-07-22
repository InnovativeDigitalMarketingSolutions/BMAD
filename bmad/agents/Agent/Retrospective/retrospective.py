from bmad.agents.core.message_bus import publish
from bmad.agents.core.supabase_context import save_context
import logging
from datetime import datetime
from bmad.agents.core.slack_notify import send_slack_message
from bmad.agents.core.llm_client import ask_openai

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def publish_improvement(action, agent="Retrospective"):
    event = {"timestamp": datetime.now().isoformat(), "improvement": action, "agent": agent}
    publish("improvement_action", event)
    save_context(agent, "improvement", {"improvement": action, "timestamp": event["timestamp"]}, updated_by=agent)
    logging.info(f"[Retrospective] Verbeteractie gepubliceerd en opgeslagen: {action}")
    send_slack_message(f"[Retrospective] Verbeteractie gepubliceerd: {action}")

def summarize_retro(feedback_list):
    prompt = f"Vat de volgende retro-feedback samen in maximaal 3 bullets:\n" + "\n".join(feedback_list)
    result = ask_openai(prompt)
    logging.info(f"[Retrospective][LLM Retro-samenvatting]: {result}")
    return result

def generate_retro_actions(feedback_list):
    prompt = f"Bedenk 3 concrete verbeteracties op basis van deze retro-feedback:\n" + "\n".join(feedback_list)
    result = ask_openai(prompt)
    logging.info(f"[Retrospective][LLM Actiepunten]: {result}")
    return result

def on_retro_feedback(event):
    feedback_list = event.get("feedback_list", [])
    summarize_retro(feedback_list)

def on_generate_actions(event):
    feedback_list = event.get("feedback_list", [])
    generate_retro_actions(feedback_list)

def on_feedback_sentiment_analyzed(event):
    sentiment = event.get("sentiment", "")
    motivatie = event.get("motivatie", "")
    feedback = event.get("feedback", "")
    if sentiment == "negatief":
        prompt = f"Bedenk 2 concrete verbeteracties op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen de acties als JSON."
        structured_output = '{"verbeteracties": ["actie 1", "actie 2"]}'
        result = ask_openai(prompt, structured_output=structured_output)
        logging.info(f"[Retrospective][LLM Verbeteracties]: {result}")

from bmad.agents.core.message_bus import subscribe
subscribe("retro_feedback", on_retro_feedback)
subscribe("generate_actions", on_generate_actions)
subscribe("feedback_sentiment_analyzed", on_feedback_sentiment_analyzed)
