from test_helpers import run_orchestrator_command

def test_start_workflow():
    result = run_orchestrator_command("start-workflow", "feature")
    assert "Workflow *feature* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout or "Start workflow: feature" in result.stderr
    
    result2 = run_orchestrator_command("show-workflow-status", "feature")
    assert "afgerond" in result2.stdout or "lopend" in result2.stdout or "onbekend" in result2.stdout 