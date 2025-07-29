import os
import pytest
from bmad.agents.core.slack_notify import send_slack_message

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Handmatige test, niet geschikt voor CI")
def test_agent_notify():
    channel = os.getenv("SLACK_DEFAULT_CHANNEL", "C097FTDU1A5")
    send_slack_message("Testnotificatie vanuit agent_notify_test.py", channel, use_api=True)
    assert True  # Kan alleen handmatig in Slack gecontroleerd worden 