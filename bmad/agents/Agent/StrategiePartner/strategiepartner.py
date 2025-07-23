from bmad.agents.core.message_bus import publish
from bmad.agents.core.supabase_context import get_context
import logging
from datetime import datetime
from bmad.agents.core.slack_notify import send_slack_message

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def alignment_check():
    logging.info("[StrategiePartner] Alignment-check gestart.")
    send_slack_message("[StrategiePartner] Alignment-check gestart.")
    publish("alignment_check", {"timestamp": datetime.now().isoformat(), "initiator": "StrategiePartner"})
    # Haal feedback op van alle agents
    for agent in ["ProductOwner", "Architect", "TestEngineer", "ReleaseManager", "RnD", "FullstackDeveloper"]:
        feedback = get_context(agent, context_type="feedback")
        logging.info(f"[StrategiePartner] Feedback van {agent}: {feedback}")
