import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.ai.llm_client import ask_openai
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine

class RnDAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()

    def collaborate_example(self):
        print("[RnDAgent] Sharing experiment with AiDeveloper...")
        publish("experiment_requested", {"agent": "RnDAgent"})

    def handle_experiment_completed(self, event):
        print(f"[RnDAgent] Experiment completed: {event}")
        self.monitor.log_metric("experiment", event)
        allowed = self.policy_engine.evaluate_policy("experiment", event)
        print(f"[RnDAgent] Policy allowed: {allowed}")

    def run(self):
        subscribe("experiment_completed", self.handle_experiment_completed)
        print("[RnDAgent] Ready and listening for events...")
        self.collaborate_example()

if __name__ == "__main__":
    agent = RnDAgent()
    agent.run()
