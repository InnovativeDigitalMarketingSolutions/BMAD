import subprocess
import sys
import pytest

def test_start_workflow():
    result = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.Orchestrator.orchestrator", "start-workflow", "--workflow", "feature"],
        capture_output=True, text=True
    )
    assert "Workflow *feature* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout
    result2 = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.Orchestrator.orchestrator", "show-workflow-status", "--workflow", "feature"],
        capture_output=True, text=True
    )
    assert "afgerond" in result2.stdout or "lopend" in result2.stdout 