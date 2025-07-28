import logging
from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent
from dotenv import load_dotenv
load_dotenv()

def test_automated_deployment():
    orch = OrchestratorAgent()
    logging.info("[TEST] Start automated_deployment workflow test...")
    orch.start_workflow("automated_deployment", slack_channel="#devops-alerts")
    logging.info("[TEST] automated_deployment workflow test afgerond.")

if __name__ == "__main__":
    test_automated_deployment() 