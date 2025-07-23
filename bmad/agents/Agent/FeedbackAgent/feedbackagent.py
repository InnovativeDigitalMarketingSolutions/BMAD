from bmad.agents.core.message_bus import publish, subscribe
from bmad.agents.core.supabase_context import save_context, get_context
import logging
from datetime import datetime
from bmad.agents.core.slack_notify import send_slack_message
from bmad.agents.core.llm_client import ask_openai
import hashlib

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def publish_feedback(feedback_text, agent="FeedbackAgent"):
    event = {"timestamp": datetime.now().isoformat(), "feedback": feedback_text, "agent": agent}
    publish("feedback_collected", event)
    save_context(agent, "feedback", {"feedback": feedback_text, "timestamp": event["timestamp"]}, updated_by=agent)
    logging.info(f"[FeedbackAgent] Feedback gepubliceerd en opgeslagen: {feedback_text}")
    send_slack_message(f"[FeedbackAgent] Nieuwe feedback ontvangen: {feedback_text}")

    def collaborate_example(self):
        """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
        publish("feedback_collected", {"status": "success", "agent": "FeedbackAgent"})
        save_context("FeedbackAgent", {"feedback_status": "collected"})
        print("Event gepubliceerd en context opgeslagen.")
        context = get_context("FeedbackAgent")
        print(f"Opgehaalde context: {context}")

def analyze_feedback_sentiment(feedback_text):
    prompt = f"Classificeer de volgende feedback als positief, negatief of neutraal en geef een korte motivatie: '{feedback_text}'"
    structured_output = '{"sentiment": "positief|negatief|neutraal", "motivatie": "..."}'
    result = ask_openai(prompt, structured_output=structured_output)
    logging.info(f"[FeedbackAgent][LLM Sentiment]: {result}")
    # Publiceer event zodat andere agents kunnen reageren
    publish("feedback_sentiment_analyzed", {"feedback": feedback_text, "sentiment": result.get("sentiment"), "motivatie": result.get("motivatie")})
    # Stuur Slack notificatie met feedback mogelijkheid
    send_slack_message(f"[FeedbackAgent] Sentimentanalyse: {result}", feedback_id=hashlib.sha256(feedback_text.encode()).hexdigest())
    return result

def summarize_feedback(feedback_list):
    prompt = f"Vat de volgende feedback samen in maximaal 3 bullets:\n" + "\n".join(feedback_list)
    result = ask_openai(prompt)
    logging.info(f"[FeedbackAgent][LLM Samenvatting]: {result}")
    return result

def on_feedback_received(event):
    feedback = event.get("feedback", "")
    analyze_feedback_sentiment(feedback)

def on_summarize_feedback(event):
    feedback_list = event.get("feedback_list", [])
    summarize_feedback(feedback_list)

subscribe("feedback_received", on_feedback_received)
subscribe("summarize_feedback", on_summarize_feedback)
