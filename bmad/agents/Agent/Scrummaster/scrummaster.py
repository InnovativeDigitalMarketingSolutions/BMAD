import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.prefect.prefect_workflow import PrefectWorkflowOrchestrator


class ScrummasterAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.workflow = PrefectWorkflowOrchestrator()

    def collaborate_example(self):
        print("[ScrummasterAgent] Collaborating with ProductOwner and Retrospective...")
        publish("sprint_planning_requested", {"agent": "ScrummasterAgent"})

    def handle_sprint_review_completed(self, event):
        print(f"[ScrummasterAgent] Sprint review completed: {event}")
        self.monitor.log_metric("sprint_review", event)
        allowed = self.policy_engine.evaluate_policy("sprint_review", event)
        print(f"[ScrummasterAgent] Policy allowed: {allowed}")

    def run(self):
        subscribe("sprint_review_completed", self.handle_sprint_review_completed)
        print("[ScrummasterAgent] Ready and listening for events...")
        self.collaborate_example()

if __name__ == "__main__":
    agent = ScrummasterAgent()
    agent.run()
