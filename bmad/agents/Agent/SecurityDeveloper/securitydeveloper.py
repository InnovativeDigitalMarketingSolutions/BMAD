import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import logging
import time
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.ai.confidence_scoring import confidence_scoring
from integrations.slack.slack_notify import send_slack_message

def notify_security_event(event):
    send_slack_message(f"[SecurityDeveloper] Security event: {event}")

def security_review(code_snippet):
    prompt = f"Geef een security review van de volgende code/config:\n{code_snippet}"
    result = ask_openai(prompt)
    logging.info(f"[SecurityDeveloper][LLM Security Review]: {result}")
    return result

def summarize_incidents(incident_list):
    prompt = f"Vat de volgende security-incidenten samen in maximaal 3 bullets:\n" + "\n".join(incident_list)
    result = ask_openai(prompt)
    logging.info(f"[SecurityDeveloper][LLM Incident-samenvatting]: {result}")
    return result

def on_security_review_requested(event):
    code_snippet = event.get("code_snippet", "")
    security_review(code_snippet)

def on_summarize_incidents(event):
    incident_list = event.get("incident_list", [])
    summarize_incidents(incident_list)

def handle_security_scan_started(event):
    logging.info("[SecurityDeveloper] Security scan gestart...")
    time.sleep(2)
    publish("security_findings_reported", {"desc": "Security bevindingen gerapporteerd"})
    logging.info("[SecurityDeveloper] Security findings gepubliceerd.")

def handle_security_findings_reported(event):
    logging.info("[SecurityDeveloper] Wacht op HITL-review...")
    # HITL wordt afgehandeld door orchestrator
    pass

from bmad.agents.core.communication.message_bus import subscribe
subscribe("security_review_requested", on_security_review_requested)
subscribe("summarize_incidents", on_summarize_incidents)
subscribe("security_scan_started", handle_security_scan_started)
subscribe("security_findings_reported", handle_security_findings_reported)
