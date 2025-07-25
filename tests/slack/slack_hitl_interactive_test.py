import os
import sys
import time
import pytest
from bmad.agents.core.slack_notify import send_human_in_loop_alert
from bmad.agents.core.message_bus import subscribe

@pytest.mark.skipif(os.getenv("CI"), reason="Handmatige test, niet geschikt voor CI")
def test_slack_hitl_interactive():
    channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
    alert_id = "test-hitl-interactive-001"
    events = []
    def on_hitl_decision(event):
        events.append(event)
    subscribe("hitl_decision", on_hitl_decision)
    send_human_in_loop_alert(
        reason="Test HITL interactiviteit.",
        channel=channel,
        user_mention=None,
        alert_id=alert_id,
        use_api=True
    )
    time.sleep(10)  # Wacht kort op interactie
    assert True  # Kan alleen handmatig in Slack gecontroleerd worden 