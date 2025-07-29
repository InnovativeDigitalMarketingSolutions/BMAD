import pytest
import threading
import time
from bmad.agents.core.message_bus import subscribe, publish
from test_helpers import run_orchestrator_command
import os

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Handmatige test, niet geschikt voor CI")
def test_orchestrator_agent_failure_with_mock():
    # Start een mock agent in een thread
    def mock_agent():
        def on_security_review(event):
            # Simuleer dat de agent het event oppakt en een afsluitend event publiceert
            publish("security_review_completed", {"desc": "Security review afgerond"})
        subscribe("security_review_completed", on_security_review)
        # Houd de thread even actief
        time.sleep(10)

    agent_thread = threading.Thread(target=mock_agent, daemon=True)
    agent_thread.start()

    # Start de workflow
    result = run_orchestrator_command("start-workflow", "security_review")
    assert "Workflow *security_review* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout or "Start workflow: security_review" in result.stderr 