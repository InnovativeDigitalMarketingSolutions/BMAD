import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from bmad.agents.core.communication.message_bus import publish, subscribe
from bmad.agents.core.agent.test_sprites import get_sprite_library
from bmad.agents.core.agent.agent_performance_monitor import get_performance_monitor
from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine

class AccessibilityAgent:
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.policy_engine = get_advanced_policy_engine()
        self.sprite_library = get_sprite_library()

    def collaborate_example(self):
        print("[AccessibilityAgent] Start accessibility audit via TestEngineer...")
        publish("accessibility_audit_requested", {"agent": "AccessibilityAgent"})

    def handle_audit_completed(self, event):
        print(f"[AccessibilityAgent] Audit completed: {event}")
        self.monitor.log_metric("accessibility_audit", event)
        allowed = self.policy_engine.evaluate_policy("accessibility", event)
        print(f"[AccessibilityAgent] Policy allowed: {allowed}")

    def run(self):
        subscribe("accessibility_audit_completed", self.handle_audit_completed)
        print("[AccessibilityAgent] Ready and listening for events...")
        self.collaborate_example()

if __name__ == "__main__":
    agent = AccessibilityAgent()
    agent.run()
