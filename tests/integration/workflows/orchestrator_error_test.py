import subprocess
import sys

def test_error_workflow():
    result = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.Orchestrator.orchestrator", "start-workflow", "--workflow", "niet_bestaand"],
        capture_output=True, text=True
    )
    assert "niet gevonden" in result.stdout or result.returncode != 0 