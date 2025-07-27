import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.communication.message_bus import publish, subscribe
from integrations.opentelemetry.opentelemetry_tracing import BMADTracer
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from integrations.prefect.prefect_workflow import PrefectWorkflowOrchestrator

class BackendDeveloperAgent:
    def __init__(self):
        self.tracer = BMADTracer()
        self.policy_engine = get_advanced_policy_engine()
        self.workflow = PrefectWorkflowOrchestrator()

    def collaborate_example(self):
        print("[BackendDeveloperAgent] Collaborating with FullstackDeveloper and Architect...")
        publish("api_change_requested", {"agent": "BackendDeveloperAgent"})

    def handle_api_change_completed(self, event):
        print(f"[BackendDeveloperAgent] API change completed: {event}")
        self.tracer.record_event("api_change_completed", event)
        allowed = self.policy_engine.evaluate_policy("api_change", event)
        print(f"[BackendDeveloperAgent] Policy allowed: {allowed}")

    def run(self):
        subscribe("api_change_completed", self.handle_api_change_completed)
        print("[BackendDeveloperAgent] Ready and listening for events...")
        self.collaborate_example()

if __name__ == "__main__":
    agent = BackendDeveloperAgent()
    agent.run()
