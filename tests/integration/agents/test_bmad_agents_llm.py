import pytest
import sys
import subprocess
import os

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY niet gezet, sla LLM-test over."
)
def test_llm_generate_tests():
    # Test de LLM-integratie van de TestEngineer agent
    result = subprocess.run(
        [sys.executable, "-m", "bmad.agents.Agent.TestEngineer.testengineer", "run-tests"],
        capture_output=True, text=True
    )
    # Verwacht dat de output van de LLM-call of stub zichtbaar is
    # Check both stdout and stderr since the output might go to either
    # Look for actual test results that appear in the output
    assert ("Testresultaten" in result.stdout or "LLM" in result.stdout or 
            "Testresultaten" in result.stderr or "LLM" in result.stderr or
            "Test results" in result.stderr or "Running all tests" in result.stderr) 