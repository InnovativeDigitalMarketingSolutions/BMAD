from test_helpers import run_orchestrator_command

def test_hitl_workflow():
    result = run_orchestrator_command("start-workflow", "automated_deployment")
    assert "Workflow *automated_deployment* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout or "Start workflow: automated_deployment" in result.stderr 