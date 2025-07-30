import subprocess
import sys
import pytest

AGENTS = [
    {
        "name": "ProductOwner",
        "module": "bmad.agents.Agent.ProductOwner.product_owner",
        "help_kw": "ProductOwner Agent",
        "workflow_cmd": "create-story",
        "workflow_expect": "Geen project geladen"
    },
    {
        "name": "FullstackDeveloper",
        "module": "bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper",
        "help_kw": "FullstackDeveloper Agent Commands",
        "workflow_cmd": "implement-story",
        "workflow_expect": "Pull Request"
    },
    {
        "name": "TestEngineer",
        "module": "bmad.agents.Agent.TestEngineer.testengineer",
        "help_kw": "TestEngineer Agent Commands",
        "workflow_cmd": "run-tests",
        "workflow_expect": "Running all tests"
    },
]

@pytest.mark.parametrize("agent", AGENTS)
def test_agent_help(agent):
    result = subprocess.run(
        [sys.executable, "-m", agent["module"]],
        capture_output=True, text=True
    )
    assert agent["help_kw"] in result.stdout

@pytest.mark.parametrize("agent", AGENTS)
def test_agent_workflow_command(agent):
    result = subprocess.run(
        [sys.executable, "-m", agent["module"], agent["workflow_cmd"]],
        capture_output=True, text=True
    )
    # Check both stdout and stderr for TestEngineer
    if agent["name"] == "TestEngineer":
        assert agent["workflow_expect"] in result.stdout or agent["workflow_expect"] in result.stderr
    else:
        assert agent["workflow_expect"] in result.stdout 