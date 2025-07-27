import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.ai.confidence_scoring import confidence_scoring
from integrations.slack.slack_notify import send_slack_message
import logging

def collaborate_example():
    """Voorbeeld van samenwerking: publiceer event en deel context via Supabase."""
    publish("pipeline_validated", {"status": "success", "agent": "DataEngineer"})
    save_context("DataEngineer", {"pipeline_status": "validated"})
    print("Event gepubliceerd en context opgeslagen.")
    context = get_context("DataEngineer")
    print(f"Opgehaalde context: {context}")

def data_quality_check(data_summary):
    prompt = f"Analyseer de volgende data-samenvatting en geef suggesties voor kwaliteitscontroles:\n{data_summary}"
    result = ask_openai(prompt)
    logging.info(f"[DataEngineer][LLM Data Quality]: {result}")
    return result

def explain_pipeline(pipeline_code):
    prompt = f"Leg in het kort uit wat deze ETL pipeline doet:\n{pipeline_code}"
    result = ask_openai(prompt)
    logging.info(f"[DataEngineer][LLM Pipeline Uitleg]: {result}")
    return result

def on_data_quality_check_requested(event):
    data_summary = event.get("data_summary", "")
    data_quality_check(data_summary)

def on_explain_pipeline(event):
    pipeline_code = event.get("pipeline_code", "")
    explain_pipeline(pipeline_code)

subscribe("data_quality_check_requested", on_data_quality_check_requested)
subscribe("explain_pipeline", on_explain_pipeline)
