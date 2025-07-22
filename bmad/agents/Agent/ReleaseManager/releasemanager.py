from bmad.agents.core.message_bus import subscribe
import logging
from bmad.agents.core.slack_notify import send_slack_message

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

subscribe("tests_passed", on_tests_passed)
subscribe("release_approved", on_release_approved)
subscribe("deployment_failed", on_deployment_failed)
