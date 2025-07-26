import os
import sys
import pytest
from bmad.agents.core.slack_notify import send_human_in_loop_alert

@pytest.mark.skipif(os.getenv("CI"), reason="Handmatige test, niet geschikt voor CI")
def test_slack_hitl():
    channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
    send_human_in_loop_alert(
        reason="Test HITL alert via script.",
        channel=channel,
        user_mention=None,
        alert_id="test-hitl-001",
        use_api=True
    )
    assert True  # Kan alleen handmatig in Slack gecontroleerd worden 