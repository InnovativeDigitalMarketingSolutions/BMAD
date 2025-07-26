from flask import Flask, request, jsonify, send_from_directory, redirect
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bmad.agents.Agent.Orchestrator.orchestrator import OrchestratorAgent, METRICS
from bmad.agents.core.supabase_context import save_context, get_context

app = Flask(__name__)

orch = OrchestratorAgent()

@app.route("/orchestrator/start-workflow", methods=["POST"])
def start_workflow():
    data = request.json or {}
    workflow = data.get("workflow")
    parameters = data.get("parameters", {})
    if not workflow:
        return jsonify({"error": "workflow is required"}), 400
    orch.start_workflow(workflow)
    return jsonify({"status": "started", "workflow": workflow})

@app.route("/orchestrator/status", methods=["GET"])
def orchestrator_status():
    return jsonify(orch.status)

@app.route("/orchestrator/workflow/<name>/status", methods=["GET"])
def workflow_status(name):
    status = orch.get_workflow_status(name)
    return jsonify({"workflow": name, "status": status})

@app.route("/orchestrator/metrics", methods=["GET"])
def orchestrator_metrics():
    return jsonify(METRICS)

@app.route("/agent/<agent_name>/command", methods=["POST"])
def agent_command(agent_name):
    data = request.json or {}
    command = data.get("command")
    # Stub: publiceer event op message bus of roep agent direct aan
    # Voorbeeld: publish(f"{agent_name}_command", {"command": command})
    return jsonify({"status": "command received", "agent": agent_name, "command": command})

@app.route("/agent/<agent_name>/status", methods=["GET"])
def agent_status(agent_name):
    # Stub: haal status op uit context of agent
    status = orch.status.get(agent_name, "onbekend")
    return jsonify({"agent": agent_name, "status": status})

@app.route("/context/<agent>/<type>", methods=["GET"])
def get_agent_context(agent, type):
    result = get_context(agent, type)
    return jsonify(result)

@app.route("/context/<agent>/<type>", methods=["POST"])
def post_agent_context(agent, type):
    payload = request.json or {}
    save_context(agent, type, payload)
    return jsonify({"status": "context saved", "agent": agent, "type": type})

@app.route("/test/ping", methods=["GET"])
def test_ping():
    return jsonify({"pong": True})

@app.route("/test/echo", methods=["POST"])
def test_echo():
    return jsonify(request.json or {})

@app.route('/swagger-ui/<path:filename>')
def swagger_ui_static(filename):
    return send_from_directory('swagger-ui', filename)

@app.route('/openapi.yaml')
def openapi_spec():
    return send_from_directory('swagger-ui', 'openapi.yaml')

@app.route('/swagger')
def swagger_redirect():
    return redirect('/swagger-ui/index.html')

if __name__ == "__main__":
    app.run(port=5001, debug=True) 