import os
import sys

from flask import Flask, jsonify, redirect, request, send_from_directory

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bmad.agents.Agent.Orchestrator.orchestrator import METRICS, OrchestratorAgent
from bmad.agents.core.data.supabase_context import get_context, save_context

# Enterprise Features Integration
from bmad.core.enterprise.multi_tenancy import tenant_manager
from bmad.core.enterprise.user_management import user_manager, role_manager, permission_manager
from bmad.core.enterprise.billing import billing_manager, usage_tracker, subscription_manager
from bmad.core.enterprise.access_control import feature_flag_manager, access_control_manager
from bmad.core.enterprise.security import enterprise_security_manager

app = Flask(__name__)

orch = OrchestratorAgent()

# Enterprise Features Middleware
def get_tenant_from_request():
    """Extract tenant from request headers or subdomain."""
    tenant_id = request.headers.get('X-Tenant-ID')
    if not tenant_id:
        # Try to get from subdomain
        host = request.headers.get('Host', '')
        if '.' in host:
            subdomain = host.split('.')[0]
            tenant = tenant_manager.get_tenant_by_domain(f"{subdomain}.example.com")
            if tenant:
                tenant_id = tenant.id
    return tenant_id

def require_auth(f):
    """Decorator to require authentication."""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        # TODO: Implement JWT token validation
        # For now, just check if token exists
        if not token:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission):
    """Decorator to require specific permission."""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # TODO: Implement permission checking
            # For now, just pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Existing routes
@app.route("/orchestrator/start-workflow", methods=["POST"])
@require_auth
@require_permission("execute_workflows")
def start_workflow():
    data = request.json or {}
    workflow = data.get("workflow")
    data.get("parameters", {})
    if not workflow:
        return jsonify({"error": "workflow is required"}), 400
    
    # Check tenant limits
    tenant_id = get_tenant_from_request()
    if tenant_id:
        tenant = tenant_manager.get_tenant(tenant_id)
        if tenant and not tenant_manager.check_limit("max_workflows", 1):  # TODO: Get actual count
            return jsonify({"error": "Workflow limit exceeded"}), 403
    
    orch.start_workflow(workflow)
    return jsonify({"status": "started", "workflow": workflow})

@app.route("/orchestrator/status", methods=["GET"])
@require_auth
def orchestrator_status():
    return jsonify(orch.status)

@app.route("/orchestrator/workflow/<name>/status", methods=["GET"])
@require_auth
def workflow_status(name):
    status = orch.get_workflow_status(name)
    return jsonify({"workflow": name, "status": status})

@app.route("/orchestrator/metrics", methods=["GET"])
@require_auth
@require_permission("view_analytics")
def orchestrator_metrics():
    return jsonify(METRICS)

@app.route("/agent/<agent_name>/command", methods=["POST"])
@require_auth
@require_permission("execute_agents")
def agent_command(agent_name):
    data = request.json or {}
    command = data.get("command")
    
    # Check tenant limits
    tenant_id = get_tenant_from_request()
    if tenant_id:
        tenant = tenant_manager.get_tenant(tenant_id)
        if tenant and not tenant_manager.check_limit("max_agents", 1):  # TODO: Get actual count
            return jsonify({"error": "Agent limit exceeded"}), 403
    
    # Stub: publiceer event op message bus of roep agent direct aan
    # Voorbeeld: publish(f"{agent_name}_command", {"command": command})
    return jsonify({"status": "command received", "agent": agent_name, "command": command})

@app.route("/agent/<agent_name>/status", methods=["GET"])
@require_auth
def agent_status(agent_name):
    # Stub: haal status op uit context of agent
    status = orch.status.get(agent_name, "onbekend")
    return jsonify({"agent": agent_name, "status": status})

@app.route("/context/<agent>/<type>", methods=["GET"])
@require_auth
def get_agent_context(agent, type):
    result = get_context(agent, type)
    return jsonify(result)

@app.route("/context/<agent>/<type>", methods=["POST"])
@require_auth
@require_permission("edit_agents")
def post_agent_context(agent, type):
    payload = request.json or {}
    save_context(agent, type, payload)
    return jsonify({"status": "context saved", "agent": agent, "type": type})

# Enterprise Features API Routes

# Multi-Tenancy Routes
@app.route("/api/tenants", methods=["GET"])
@require_auth
@require_permission("view_tenants")
def list_tenants():
    tenants = tenant_manager.list_tenants()
    return jsonify([tenant.to_dict() for tenant in tenants])

@app.route("/api/tenants", methods=["POST"])
@require_auth
@require_permission("create_tenants")
def create_tenant():
    data = request.json or {}
    tenant = tenant_manager.create_tenant(
        name=data.get("name"),
        domain=data.get("domain"),
        plan=data.get("plan", "basic")
    )
    return jsonify(tenant.to_dict()), 201

@app.route("/api/tenants/<tenant_id>", methods=["GET"])
@require_auth
def get_tenant(tenant_id):
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        return jsonify({"error": "Tenant not found"}), 404
    return jsonify(tenant.to_dict())

@app.route("/api/tenants/<tenant_id>", methods=["PUT"])
@require_auth
@require_permission("edit_tenants")
def update_tenant(tenant_id):
    data = request.json or {}
    tenant = tenant_manager.update_tenant(tenant_id, **data)
    if not tenant:
        return jsonify({"error": "Tenant not found"}), 404
    return jsonify(tenant.to_dict())

# User Management Routes
@app.route("/api/users", methods=["GET"])
@require_auth
@require_permission("view_users")
def list_users():
    tenant_id = get_tenant_from_request()
    if not tenant_id:
        return jsonify({"error": "Tenant ID required"}), 400
    
    users = user_manager.list_users_by_tenant(tenant_id)
    return jsonify([user.to_dict() for user in users])

@app.route("/api/users", methods=["POST"])
@require_auth
@require_permission("create_users")
def create_user():
    data = request.json or {}
    user = user_manager.create_user(
        email=data.get("email"),
        username=data.get("username"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        tenant_id=data.get("tenant_id"),
        password=data.get("password"),
        role_ids=data.get("role_ids", [])
    )
    return jsonify(user.to_dict()), 201

@app.route("/api/users/<user_id>", methods=["PUT"])
@require_auth
@require_permission("edit_users")
def update_user(user_id):
    data = request.json or {}
    user = user_manager.update_user(user_id, **data)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

# Authentication Routes
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    user = user_manager.authenticate_user(
        email=data.get("email"),
        password=data.get("password")
    )
    
    if not user:
        # Log failed login attempt
        enterprise_security_manager.log_audit_event(
            user_id="unknown",
            tenant_id="unknown",
            event_type="login",
            resource="auth",
            action="login",
            details={"email": data.get("email")},
            ip_address=request.remote_addr,
            success=False
        )
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Log successful login
    enterprise_security_manager.log_audit_event(
        user_id=user.id,
        tenant_id=user.tenant_id,
        event_type="login",
        resource="auth",
        action="login",
        details={"method": "password"},
        ip_address=request.remote_addr,
        success=True
    )
    
    # TODO: Generate JWT token
    token = "dummy_token"  # Replace with actual JWT generation
    
    return jsonify({
        "user": user.to_dict(),
        "token": token,
        "tenant": tenant_manager.get_tenant(user.tenant_id).to_dict() if user.tenant_id else None
    })

# Billing Routes
@app.route("/api/billing/plans", methods=["GET"])
@require_auth
def list_plans():
    plans = billing_manager.list_plans()
    return jsonify([plan.to_dict() for plan in plans])

@app.route("/api/billing/subscription", methods=["GET"])
@require_auth
def get_subscription():
    tenant_id = get_tenant_from_request()
    if not tenant_id:
        return jsonify({"error": "Tenant ID required"}), 400
    
    subscription = subscription_manager.check_subscription_status(tenant_id)
    if not subscription:
        return jsonify({"error": "No active subscription"}), 404
    
    return jsonify(subscription.to_dict())

@app.route("/api/billing/usage", methods=["GET"])
@require_auth
def get_usage():
    tenant_id = get_tenant_from_request()
    if not tenant_id:
        return jsonify({"error": "Tenant ID required"}), 400
    
    period = request.args.get("period", "current_month")
    metrics = ["api_calls", "agent_executions", "workflow_executions", "storage_used"]
    
    usage_data = {}
    for metric in metrics:
        if period == "current_month":
            usage_data[metric] = usage_tracker.get_current_month_usage(tenant_id, metric)
        else:
            # TODO: Implement period-based usage
            usage_data[metric] = usage_tracker.get_current_month_usage(tenant_id, metric)
    
    return jsonify(usage_data)

# Feature Flags Routes
@app.route("/api/features/<flag_name>", methods=["GET"])
@require_auth
def get_feature_flag(flag_name):
    tenant_id = get_tenant_from_request()
    value = feature_flag_manager.get_flag_value(flag_name, tenant_id)
    return jsonify({"flag": flag_name, "value": value})

# Security Routes
@app.route("/api/security/compliance", methods=["GET"])
@require_auth
@require_permission("view_analytics")
def get_compliance():
    tenant_id = get_tenant_from_request()
    if not tenant_id:
        return jsonify({"error": "Tenant ID required"}), 400
    
    compliance = enterprise_security_manager.check_security_compliance(tenant_id)
    return jsonify(compliance)

@app.route("/api/security/audit-logs", methods=["GET"])
@require_auth
@require_permission("view_logs")
def get_audit_logs():
    tenant_id = get_tenant_from_request()
    days = int(request.args.get("days", 30))
    
    logs = enterprise_security_manager.get_audit_logs(
        tenant_id=tenant_id,
        limit=int(request.args.get("limit", 100))
    )
    
    return jsonify([log.to_dict() for log in logs])

@app.route("/api/security/report", methods=["GET"])
@require_auth
@require_permission("view_analytics")
def generate_security_report():
    tenant_id = get_tenant_from_request()
    days = int(request.args.get("days", 30))
    
    report = enterprise_security_manager.generate_security_report(
        tenant_id=tenant_id
    )
    
    return jsonify(report)

# Test routes
@app.route("/test/ping", methods=["GET"])
def test_ping():
    return jsonify({"pong": True})

@app.route("/test/echo", methods=["POST"])
def test_echo():
    return jsonify(request.json or {})

@app.route("/swagger-ui/<path:filename>")
def swagger_ui_static(filename):
    return send_from_directory("swagger-ui", filename)

@app.route("/openapi.yaml")
def openapi_spec():
    return send_from_directory("swagger-ui", "openapi.yaml")

@app.route("/swagger")
def swagger_redirect():
    return redirect("/swagger-ui/index.html")

if __name__ == "__main__":
    app.run(port=5001, debug=False)

# Export the Flask app for testing
__all__ = ['app']
