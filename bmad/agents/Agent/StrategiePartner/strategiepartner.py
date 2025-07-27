import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.ai.confidence_scoring import confidence_scoring
from integrations.slack.slack_notify import send_slack_message
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def alignment_check():
    logging.info("[StrategiePartner] Alignment-check gestart.")
    send_slack_message("[StrategiePartner] Alignment-check gestart.")
    publish("alignment_check", {"timestamp": datetime.now().isoformat(), "initiator": "StrategiePartner"})
    # Haal feedback op van alle agents
    for agent in ["ProductOwner", "Architect", "TestEngineer", "ReleaseManager", "RnD", "FullstackDeveloper"]:
        feedback = get_context(agent, context_type="feedback")
        logging.info(f"[StrategiePartner] Feedback van {agent}: {feedback}")
