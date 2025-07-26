import subprocess
import sys
import pytest

def test_show_metrics():
    result = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.Orchestrator.orchestrator", "show-metrics"],
        capture_output=True, text=True
    )
    assert "Orchestrator Metrics" in result.stdout 