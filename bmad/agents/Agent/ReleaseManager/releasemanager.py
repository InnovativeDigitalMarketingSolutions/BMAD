import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
import logging
from integrations.slack.slack_notify import send_slack_message

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def on_tests_passed(event):
    logging.info("[ReleaseManager] Tests geslaagd, release flow gestart.")
    send_slack_message("[ReleaseManager] Tests geslaagd, release flow gestart.")
    # Start release flow (stub)

def on_release_approved(event):
    logging.info("[ReleaseManager] Release goedgekeurd door PO, release wordt live gezet.")
    send_slack_message("[ReleaseManager] Release goedgekeurd door PO, release wordt live gezet.")
    # Zet release live (stub)

def on_deployment_failed(event):
    logging.error("[ReleaseManager] Deployment failed! Rollback gestart.")
    send_slack_message("[ReleaseManager] Deployment failed! Rollback gestart.")
    # Start rollback (stub)

from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.data.supabase_context import save_context, get_context
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.ai.confidence_scoring import confidence_scoring

subscribe("tests_passed", on_tests_passed)
subscribe("release_approved", on_release_approved)
subscribe("deployment_failed", on_deployment_failed)
