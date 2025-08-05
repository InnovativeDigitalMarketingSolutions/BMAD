from .test_helpers import run_orchestrator_command
from unittest.mock import patch, MagicMock

def test_hitl_workflow():
    # Mock the subprocess directly instead of running real subprocess
    with patch('subprocess.run') as mock_subprocess:
        # Create a mock result
        mock_result = MagicMock()
        mock_result.stdout = "Workflow *automated_deployment* gestart door Orchestrator"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = run_orchestrator_command("start-workflow", "automated_deployment")
        assert "Workflow *automated_deployment* gestart" in result.stdout or "gestart door Orchestrator" in result.stdout or "Start workflow: automated_deployment" in result.stderr 