import subprocess
import sys
import pytest
import threading
import time
from bmad.agents.core.message_bus import subscribe, publish
import os

@pytest.mark.skipif(os.getenv("CI"), reason="Handmatige test, niet geschikt voor CI")
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
    result = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.Orchestrator.orchestrator", "start-workflow", "--workflow", "security_review"],
        capture_output=True, text=True, timeout=30
    )
    assert "Workflow *security_review* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout 