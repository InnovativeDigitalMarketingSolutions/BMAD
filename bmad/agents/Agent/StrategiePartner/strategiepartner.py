import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor

class StrategiePartnerAgent:
    def __init__(self):
        self.policy_engine = get_advanced_policy_engine()
        self.monitor = get_performance_monitor()

    def collaborate_example(self):
        print("[StrategiePartnerAgent] Collaborating with ProductOwner and Architect...")
        publish("alignment_check_requested", {"agent": "StrategiePartnerAgent"})

    def handle_alignment_check_completed(self, event):
        print(f"[StrategiePartnerAgent] Alignment check completed: {event}")
        self.monitor.log_metric("alignment_check", event)
        allowed = self.policy_engine.evaluate_policy("alignment", event)
        print(f"[StrategiePartnerAgent] Policy allowed: {allowed}")

    def run(self):
        subscribe("alignment_check_completed", self.handle_alignment_check_completed)
        print("[StrategiePartnerAgent] Ready and listening for events...")
        self.collaborate_example()

if __name__ == "__main__":
    agent = StrategiePartnerAgent()
    agent.run()
