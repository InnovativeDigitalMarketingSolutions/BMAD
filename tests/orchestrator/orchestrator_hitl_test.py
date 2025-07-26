import subprocess
import sys
import pytest

def test_hitl_workflow():
    result = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.Orchestrator.orchestrator", "start-workflow", "--workflow", "automated_deployment"],
        capture_output=True, text=True
    )
    assert "Workflow *automated_deployment* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout 