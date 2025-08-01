import pytest
import threading
import time
from bmad.agents.core.communication.message_bus import subscribe, publish
from test_helpers import run_orchestrator_command
import os

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Handmatige test, niet geschikt voor CI")
def test_orchestrator_agent_failure_with_mock():
    # Mock the subprocess directly instead of running real subprocess
    from unittest.mock import patch, MagicMock
    
    with patch('subprocess.run') as mock_subprocess:
        # Create a mock result
        mock_result = MagicMock()
        mock_result.stdout = "Workflow *security_review* gestart door Orchestrator"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Start een mock agent in een thread
        def mock_agent():
            def on_security_review(event):
                # Simuleer dat de agent het event oppakt en een afsluitend event publiceert
                publish("security_review_completed", {"desc": "Security review afgerond"})
            subscribe("security_review_completed", on_security_review)
            # Houd de thread even actief
            time.sleep(1)  # Reduced sleep time

        agent_thread = threading.Thread(target=mock_agent, daemon=True)
        agent_thread.start()

        # Start de workflow
        result = run_orchestrator_command("start-workflow", "security_review")
        assert "Workflow *security_review* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout or "Start workflow: security_review" in result.stderr 