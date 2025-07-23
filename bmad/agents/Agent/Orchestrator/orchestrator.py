import logging
import argparse
from bmad.agents.core.message_bus import publish, subscribe, get_events
from bmad.agents.core.supabase_context import save_context, get_context
from bmad.agents.core.llm_client import ask_openai
from datetime import datetime
import sys
import json
from bmad.agents.core.slack_notify import send_slack_message
import time
from bmad.agents.core.slack_notify import send_human_in_loop_alert
from dotenv import load_dotenv
load_dotenv()

# Metrics storage (in-memory, kan later naar Prometheus of Supabase)
METRICS = {
    'slack_commands_received': 0,
    'hitl_decisions': 0,
    'workflows_started': 0,
    'workflows_completed': 0,
    'workflow_paused': 0,
}

def log_metric(metric_name):
    if metric_name in METRICS:
        METRICS[metric_name] += 1
        logging.info(f"[Metrics] {metric_name}: {METRICS[metric_name]}")
    else:
        METRICS[metric_name] = 1
        logging.info(f"[Metrics] {metric_name}: 1 (nieuw)")

def handle_slack_command(event):
    data = event['data']
    command = data.get('command')
    agent = data.get('agent')
    channel = data.get('channel')
    user = data.get('user')
    log_metric('slack_commands_received')
    logging.info(f"[Orchestrator] Slack commando ontvangen: {command} voor agent {agent} door user {user}")
    if command == "start workflow":
        send_slack_message(f"Workflow 'feature' wordt gestart door Orchestrator.", channel=channel, use_api=True)
        orch = OrchestratorAgent()
        orch.start_workflow("feature")
        log_metric('workflows_started')
    else:
        send_slack_message(f"Commando '{command}' voor agent '{agent}' wordt door Orchestrator gerouteerd.", channel=channel, use_api=True)
        # Eventueel publish naar specifieke agent event

def handle_hitl_decision(event):
    data = event['data']
    alert_id = data.get('alert_id')
    approved = data.get('approved')
    user = data.get('user')
    channel = data.get('channel')
    log_metric('hitl_decisions')
    logging.info(f"[Orchestrator] HITL beslissing: {'goedgekeurd' if approved else 'afgewezen'} door {user} voor alert {alert_id}")
    if approved:
        send_slack_message(f"✅ Human-in-the-loop: Actie goedgekeurd door <@{user}>. Workflow wordt vervolgd.", channel=channel, use_api=True)
        log_metric('workflows_completed')
        # Hier vervolgactie, bijvoorbeeld deployment starten
    else:
        send_slack_message(f"❌ Human-in-the-loop: Actie afgewezen door <@{user}>. Workflow wordt gepauzeerd.", channel=channel, use_api=True)
        log_metric('workflow_paused')
        # Hier workflow pauzeren of annuleren

subscribe('slack_command', handle_slack_command)
subscribe('hitl_decision', handle_hitl_decision)

EVENT_LOG_PATH = "event_log.json"

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

WORKFLOW_TEMPLATES = {
    # --- Bestaande workflows ---
    "feature": [
        {"event_type": "new_task", "task_desc": "Nieuwe feature ontwikkelen"},
        {"event_type": "user_story_requested", "requirement": "Feature requirement"},
        {"event_type": "test_generation_requested", "function_description": "Feature test"},
    ],
    "incident_response": [
        {"event_type": "incident_reported", "incident_desc": "Incident details"},
        {"event_type": "incident_response_requested", "incident_desc": "Incident details"},
    ],
    # --- Geavanceerde workflows ---
    "automated_deployment": [
        {"event_type": "build_triggered", "desc": "Build gestart"},
        {"event_type": "tests_requested", "desc": "Tests uitvoeren"},
        {"event_type": "tests_completed", "desc": "Tests voltooid"},
        {"event_type": "hitl_required", "desc": "Goedkeuring voor deployment", "hitl": True},
        {"event_type": "deployment_executed", "desc": "Deployment uitgevoerd"},
        {"event_type": "deployment_completed", "desc": "Deployment afgerond"},
    ],
    "feature_delivery": [
        {"event_type": "feature_planned", "desc": "Feature gepland"},
        {"event_type": "tasks_assigned", "desc": "Taken toegewezen"},
        {"event_type": "development_started", "desc": "Ontwikkeling gestart"},
        {"event_type": "testing_started", "desc": "Testen gestart"},
        {"event_type": "acceptance_required", "desc": "Acceptatie vereist", "hitl": True},
        {"event_type": "feature_delivered", "desc": "Feature opgeleverd"},
    ],
    "security_review": [
        {"event_type": "security_scan_started", "desc": "Security scan gestart"},
        {"event_type": "security_findings_reported", "desc": "Security bevindingen gerapporteerd"},
        {"event_type": "hitl_required", "desc": "Security review goedkeuring", "hitl": True},
        {"event_type": "security_review_completed", "desc": "Security review afgerond"},
    ],
    "retrospective_feedback": [
        {"event_type": "retro_planned", "desc": "Retrospective gepland"},
        {"event_type": "feedback_collected", "desc": "Feedback verzameld"},
        {"event_type": "trends_analyzed", "desc": "Trends geanalyseerd"},
        {"event_type": "retro_results_shared", "desc": "Resultaten gedeeld in Slack"},
    ],
}

# Documentatie van workflows:
"""
Workflows:
- automated_deployment: Build, test, HITL-goedkeuring, deployment, afronding
- incident_response: Incidentmelding, response, escalatie
- feature_delivery: Planning, taaktoewijzing, ontwikkeling, testen, HITL-acceptatie, oplevering
- security_review: Security scan, findings, HITL-review, afronding
- retrospective_feedback: Retro plannen, feedback verzamelen, trends analyseren, delen
"""

# Uitgebreide start_workflow met HITL en Slack notificaties

class OrchestratorAgent:
    def __init__(self):
        self.status = {}
        self.event_log = self.load_event_log()

    def load_event_log(self):
        try:
            with open(EVENT_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_event_log(self):
        with open(EVENT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.event_log, f, indent=2)

    def log_event(self, event):
        event["timestamp"] = datetime.now().isoformat()
        self.event_log.append(event)
        self.save_event_log()

    def route_event(self, event):
        event_type = event.get("event_type")
        self.log_event(event)
        if event_type == "feedback":
            publish("feedback_received", event)
        elif event_type == "pipeline_advice":
            publish("pipeline_advice_requested", event)
        logging.info(f"[Orchestrator] Event gerouteerd: {event_type}")

    def monitor_agents(self):
        agents = ["ProductOwner", "Architect", "TestEngineer", "FeedbackAgent", "DevOpsInfra", "Retrospective"]
        for agent in agents:
            status = get_context(agent, context_type="status")
            self.status[agent] = status
        logging.info(f"[Orchestrator] Agent status: {self.status}")
        print("Agent status:", self.status)

    def intelligent_task_assignment(self, task_desc):
        prompt = f"Welke agent is het meest geschikt voor deze taak: '{task_desc}'? Kies uit: ProductOwner, Architect, TestEngineer, FeedbackAgent, DevOpsInfra, Retrospective. Geef alleen de agentnaam als JSON."
        structured_output = '{"agent": "..."}'
        result = ask_openai(prompt, structured_output=structured_output)
        agent = result.get("agent")
        logging.info(f"[Orchestrator] LLM adviseert agent: {agent} voor taak: {task_desc}")
        return agent

    def start_workflow(self, workflow_name, slack_channel="#devops-alerts"):
        """
        Start een workflow en coördineer alle stappen, inclusief HITL-momenten.
        :param workflow_name: Naam van de workflow (str)
        :param slack_channel: Slack kanaal voor notificaties (str)
        """
        if workflow_name not in WORKFLOW_TEMPLATES:
            logging.error(f"Workflow '{workflow_name}' niet gevonden.")
            send_slack_message(f":x: Workflow '{workflow_name}' niet gevonden.", channel=slack_channel, use_api=True)
            return

        logging.info(f"[Orchestrator] Start workflow: {workflow_name}")
        send_slack_message(f":rocket: Workflow *{workflow_name}* gestart door Orchestrator.", channel=slack_channel, use_api=True)

        for event in WORKFLOW_TEMPLATES[workflow_name]:
            event_type = event["event_type"]
            desc = event.get("desc", event_type)
            # HITL-moment: stuur alert en wacht op beslissing
            if event.get("hitl"):
                alert_id = f"{workflow_name}_{event_type}_{int(time.time())}"
                send_human_in_loop_alert(
                    reason=desc,
                    channel=slack_channel,
                    alert_id=alert_id
                )
                logging.info(f"[Orchestrator] HITL-alert verstuurd: {desc} (alert_id={alert_id})")
                send_slack_message(f":hourglass_flowing_sand: Wachten op goedkeuring voor stap: *{desc}*.", channel=slack_channel, use_api=True)
                # Wacht op HITL-beslissing
                approved = self.wait_for_hitl_decision(alert_id)
                if not approved:
                    send_slack_message(f":no_entry: Workflow *{workflow_name}* gepauzeerd of afgebroken door HITL.", channel=slack_channel, use_api=True)
                    logging.warning(f"[Orchestrator] Workflow '{workflow_name}' gepauzeerd/afgebroken door HITL.")
                    break
                else:
                    send_slack_message(f":white_check_mark: HITL-goedkeuring ontvangen, workflow vervolgt.", channel=slack_channel, use_api=True)
            else:
                publish(event_type, event)
                logging.info(f"[Orchestrator] Event gepubliceerd: {event_type} ({desc})")
                send_slack_message(f":information_source: Stap *{desc}* gestart.", channel=slack_channel, use_api=True)
                # Optioneel: wacht op bevestiging van agent (kan uitgebreid worden)

        send_slack_message(f":tada: Workflow *{workflow_name}* afgerond (of gepauzeerd).", channel=slack_channel, use_api=True)
        logging.info(f"[Orchestrator] Workflow '{workflow_name}' afgerond of gepauzeerd.")

    def list_workflows(self):
        print("Beschikbare workflows:")
        for wf in WORKFLOW_TEMPLATES:
            print(f"- {wf}")

    def show_status(self):
        self.monitor_agents()

    def show_history(self):
        print("Event history:")
        for event in self.event_log:
            print(event)

    def replay_history(self):
        print("Replaying event history...")
        for event in self.event_log:
            publish(event.get("event_type"), event)
            print(f"Event gereplayed: {event}")

    def wait_for_hitl_decision(self, alert_id, timeout=3600):
        """
        Wacht op een hitl_decision event met het juiste alert_id.
        :param alert_id: Unieke alert_id van de HITL stap (str)
        :param timeout: Timeout in seconden (int)
        :return: True als goedgekeurd, False als afgewezen of timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            events = get_events("hitl_decision")
            for e in events:
                if e["data"].get("alert_id") == alert_id:
                    approved = e["data"].get("approved")
                    logging.info(f"[Orchestrator] HITL-beslissing ontvangen: {'goedgekeurd' if approved else 'afgewezen'} (alert_id={alert_id})")
                    return approved
            time.sleep(5)
        logging.warning(f"[Orchestrator] Timeout bij wachten op HITL-beslissing (alert_id={alert_id})")
        return False

# --- Productieklare agent-handler voorbeeld ---
# Plaats dit in de relevante agent (bijv. DevOpsInfra, TestEngineer, etc.)
from bmad.agents.core.message_bus import subscribe, publish

def handle_build_triggered(event):
    logging.info("[DevOpsInfra] Build gestart...")
    # Simuleer build (in productie: start build pipeline)
    time.sleep(2)
    publish("tests_requested", {"desc": "Tests uitvoeren"})
    logging.info("[DevOpsInfra] Build afgerond, tests_requested gepubliceerd.")

subscribe("build_triggered", handle_build_triggered)

# Herhaal dit patroon voor andere events en agents.


def main():
    parser = argparse.ArgumentParser(description="Orchestrator Agent CLI")
    parser.add_argument("command", help="Commando: start-workflow, show-status, list-workflows, show-history, replay-history, help")
    parser.add_argument("--workflow", help="Workflow naam voor start-workflow")
    args = parser.parse_args()
    orch = OrchestratorAgent()
    if args.command == "start-workflow":
        if not args.workflow:
            print("Geef een workflow op met --workflow")
            sys.exit(1)
        orch.start_workflow(args.workflow)
    elif args.command == "show-status":
        orch.show_status()
    elif args.command == "list-workflows":
        orch.list_workflows()
    elif args.command == "show-history":
        orch.show_history()
    elif args.command == "replay-history":
        orch.replay_history()
    elif args.command == "help":
        print("Beschikbare commando's: start-workflow, show-status, list-workflows, show-history, replay-history, help")
    else:
        print(f"Onbekend commando: {args.command}")
        print("Gebruik 'help' voor opties.")

def print_metrics():
    print("\n[Orchestrator Metrics]")
    for k, v in METRICS.items():
        print(f"- {k}: {v}")

if __name__ == "__main__":
    print("Orchestrator is actief en luistert naar Slack events...")
    main()
    # Metrics monitor loop (optioneel)
    while True:
        time.sleep(60)
        print_metrics() 