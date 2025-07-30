import sys
from unittest.mock import patch

def mock_slack_notifications():
    """Mock Slack notifications to prevent API calls during tests"""
    def mock_send_slack_message(*args, **kwargs):
        print(f"[MOCK SLACK] Message: {args[0] if args else 'No message'}")
        return True
    
    def mock_send_human_in_loop_alert(*args, **kwargs):
        print(f"[MOCK SLACK] HITL Alert: {args[0] if args else 'No alert'}")
        return True
    
    return patch.multiple(
        'integrations.slack.slack_notify',
        send_slack_message=mock_send_slack_message,
        send_human_in_loop_alert=mock_send_human_in_loop_alert
    )

def run_orchestrator_command(command, workflow=None):
    """Run orchestrator command with mocked Slack notifications"""
    with mock_slack_notifications():
        import subprocess
        cmd = [sys.executable, "bmad/agents/Agent/Orchestrator/orchestrator.py", command]
        if workflow:
            cmd.extend(["--workflow", workflow])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result 