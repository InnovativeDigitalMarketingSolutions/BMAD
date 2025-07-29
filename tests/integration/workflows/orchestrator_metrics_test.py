import subprocess
import sys

def test_show_metrics():
    result = subprocess.run(
        [sys.executable, "bmad/agents/Agent/Orchestrator/orchestrator.py", "show-metrics"],
        capture_output=True, text=True
    )
    assert "Orchestrator Metrics" in result.stdout 