from bmad.agents.core.llm_client import ask_openai
from bmad.agents.core.message_bus import subscribe
import logging

def pipeline_advice(pipeline_config):
    prompt = f"Analyseer deze CI/CD pipeline config en doe 2 optimalisatievoorstellen:\n{pipeline_config}"
    result = ask_openai(prompt)
    logging.info(f"[DevOpsInfra][LLM Pipeline Advies]: {result}")
    return result

def incident_response(incident_desc):
    prompt = f"Vat dit incident samen en doe een aanbeveling voor monitoring:\n{incident_desc}"
    result = ask_openai(prompt)
    logging.info(f"[DevOpsInfra][LLM Incident Response]: {result}")
    return result

def on_pipeline_advice_requested(event):
    pipeline_config = event.get("pipeline_config", "")
    pipeline_advice(pipeline_config)

def on_incident_response_requested(event):
    incident_desc = event.get("incident_desc", "")
    incident_response(incident_desc)

def on_feedback_sentiment_analyzed(event):
    sentiment = event.get("sentiment", "")
    motivatie = event.get("motivatie", "")
    feedback = event.get("feedback", "")
    if sentiment == "negatief":
        prompt = f"Bedenk een DevOps-actie of monitoringvoorstel op basis van deze negatieve feedback: '{feedback}'. Motivatie: {motivatie}. Geef alleen het voorstel als JSON."
        structured_output = '{"devops_voorstel": "..."}'
        result = ask_openai(prompt, structured_output=structured_output)
        logging.info(f"[DevOpsInfra][LLM DevOps Voorstel]: {result}")

subscribe("pipeline_advice_requested", on_pipeline_advice_requested)
subscribe("incident_response_requested", on_incident_response_requested)
subscribe("feedback_sentiment_analyzed", on_feedback_sentiment_analyzed)
