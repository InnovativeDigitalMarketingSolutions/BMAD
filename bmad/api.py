import os
import sys
import logging
from datetime import datetime, timedelta
import time

from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bmad_api.log')
    ]
)
logger = logging.getLogger(__name__)

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

# JWT Security Integration
from bmad.core.security.jwt_service import jwt_service
from bmad.core.security.permission_service import (
    permission_service,
    require_permission_enhanced,
    require_any_permission,
    require_all_permissions,
    require_role,
    require_any_role
)
from bmad.core.resilience.circuit_breaker import (
    get_external_api_circuit_breaker,
    get_database_circuit_breaker,
    CircuitBreakerOpenError
)
from bmad.core.resilience.error_handler import (
    error_handler,
    handle_errors,
    safe_execute
)

app = Flask(__name__)

# Security headers and CORS configuration
CORS(app, origins=os.getenv("ALLOWED_ORIGINS", "*").split(","))

# Environment flags
IS_DEV = os.getenv("DEV_MODE") == "true" or os.getenv("FLASK_ENV") == "development"

# Disable rate limiting entirely in dev mode
if IS_DEV:
    app.config["RATELIMIT_ENABLED"] = False

# App start time for uptime calculation
APP_START_TIME = datetime.utcnow()

def _get_agents_list():
    return [
        {"id": "orchestrator", "name": "Orchestrator", "status": "active", "type": "orchestrator"},
        {"id": "product-owner", "name": "ProductOwner", "status": "idle", "type": "planning"},
        {"id": "architect", "name": "Architect", "status": "idle", "type": "planning"},
        {"id": "scrummaster", "name": "Scrummaster", "status": "idle", "type": "management"},
        {"id": "frontend", "name": "FrontendDeveloper", "status": "idle", "type": "development"},
        {"id": "backend", "name": "BackendDeveloper", "status": "idle", "type": "development"},
        {"id": "fullstack", "name": "FullstackDeveloper", "status": "idle", "type": "development"},
        {"id": "mobile", "name": "MobileDeveloper", "status": "idle", "type": "development"},
        {"id": "data", "name": "DataEngineer", "status": "idle", "type": "development"},
        {"id": "devops", "name": "DevOpsInfra", "status": "idle", "type": "infrastructure"},
        {"id": "quality", "name": "QualityGuardian", "status": "idle", "type": "quality"},
        {"id": "docs", "name": "DocumentationAgent", "status": "idle", "type": "documentation"},
        {"id": "feedback", "name": "FeedbackAgent", "status": "idle", "type": "feedback"},
        {"id": "accessibility", "name": "AccessibilityAgent", "status": "idle", "type": "accessibility"},
        {"id": "release", "name": "ReleaseManager", "status": "idle", "type": "release"},
        {"id": "retro", "name": "Retrospective", "status": "idle", "type": "retrospective"},
        {"id": "rnd", "name": "RnD", "status": "idle", "type": "research"},
        {"id": "ai", "name": "AiDeveloper", "status": "idle", "type": "development"},
        {"id": "security", "name": "SecurityDeveloper", "status": "idle", "type": "security"},
        {"id": "strategy", "name": "StrategiePartner", "status": "idle", "type": "strategy"},
        {"id": "test", "name": "TestEngineer", "status": "idle", "type": "testing"},
        {"id": "uxui", "name": "UXUIDesigner", "status": "idle", "type": "design"},
        {"id": "workflow", "name": "WorkflowAutomator", "status": "idle", "type": "automation"},
    ]

# Rate limiting configuration
# Development mode: higher limits for testing
# Production mode: stricter limits for security
if IS_DEV:
    # Disable limits in dev to avoid 429 during rapid polling
    default_limits = []
else:
    default_limits = ["200 per day", "50 per hour", "10 per minute"]

if IS_DEV:
    class _NoopLimiter:
        def exempt(self, f):
            return f
    limiter = _NoopLimiter()
else:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=default_limits,
        storage_uri="memory://"
    )

# Clear rate limiting storage on startup for development
if IS_DEV:
    try:
        limiter.storage.reset_all()
    except AttributeError:
        # Memory storage doesn't have reset_all, so we'll just continue
        pass

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# Rate limit headers outside DEV
@app.after_request
def add_rate_limit_headers(response):
    if not IS_DEV:
        # If Flask-Limiter is active, it usually injects headers itself. Ensure presence with sensible defaults.
        response.headers.setdefault('X-RateLimit-Limit', os.getenv('RATE_LIMIT_LIMIT', '100'))
        # Remaining is illustrative; a real implementation would reflect actual remaining from limiter state
        response.headers.setdefault('X-RateLimit-Remaining', os.getenv('RATE_LIMIT_REMAINING', '99'))
        reset_ts = os.getenv('RATE_LIMIT_RESET') or str(int(time.time()) + 60)
        response.headers.setdefault('X-RateLimit-Reset', reset_ts)
    return response

# Global error handling
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    logger.warning(f"Bad request: {error}")
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    logger.warning(f"Unauthorized access: {error}")
    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    logger.warning(f"Forbidden access: {error}")
    return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    logger.info(f"Resource not found: {error}")
    return jsonify({"error": "Not found", "message": "Resource not found"}), 404

@app.errorhandler(429)
def too_many_requests(error):
    """Handle 429 Too Many Requests errors."""
    logger.warning(f"Rate limit exceeded: {error}")
    return jsonify({"error": "Too many requests", "message": "Rate limit exceeded"}), 429

# Decorator helper: disable rate limit in dev for specific routes
def dev_unlimited(f):
    if IS_DEV:
        try:
            from flask_limiter.util import EXEMPT
            f._limiter_exempt = True  # mark as exempt for older versions
        except Exception:
            pass
        try:
            limiter.exempt(f)
        except Exception:
            pass
    return f

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

@app.errorhandler(CircuitBreakerOpenError)
def circuit_breaker_open(error):
    """Handle circuit breaker open errors."""
    logger.warning(f"Circuit breaker open: {error}")
    return jsonify({
        "error": "Service temporarily unavailable", 
        "message": "The service is currently experiencing issues. Please try again later.",
        "retry_after": 60
    }), 503

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

orch = OrchestratorAgent()

# Enterprise Features Middleware
def get_tenant_from_request():
    """Extract tenant from request headers or subdomain."""
    # Development mode - always return dev tenant
    if IS_DEV:
        return "dev_tenant"
    
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
        # Development mode bypass
        if IS_DEV:
            # Set development user and tenant
            request.tenant_id = "dev_tenant"
            request.user = type('User', (), {
                'id': 'dev_user',
                'email': 'dev@bmad.local',
                'roles': ['admin'],
                'permissions': ['*']  # All permissions in dev mode
            })()
            return f(*args, **kwargs)
        
        # Production authentication with JWT validation
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({"error": "Invalid token"}), 401
        
        # JWT token validation
        try:
            payload = jwt_service.verify_access_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Extract user information from token
            user_id = payload.get("sub")
            email = payload.get("email")
            tenant_id = payload.get("tenant_id")
            roles = payload.get("roles", [])
            permissions = payload.get("permissions", [])
            
            # Set user information on request object
            request.user = type('User', (), {
                'id': user_id,
                'email': email,
                'roles': roles,
                'permissions': permissions
            })()
            request.tenant_id = tenant_id
            
            # Log successful authentication
            enterprise_security_manager.log_audit_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="authentication",
                resource="api",
                action="token_validation",
                details={"endpoint": request.endpoint},
                ip_address=request.remote_addr,
                success=True
            )
            
        except Exception as e:
            # Log failed authentication
            enterprise_security_manager.log_audit_event(
                user_id="unknown",
                tenant_id="unknown",
                event_type="authentication",
                resource="api",
                action="token_validation",
                details={"error": str(e), "endpoint": request.endpoint},
                ip_address=request.remote_addr,
                success=False
            )
            return jsonify({"error": "Authentication failed"}), 401
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_permission(permission):
    """Decorator to require specific permission."""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Development mode bypass - admin has all permissions
            if IS_DEV:
                return f(*args, **kwargs)
            
            # Permission checking implementation
            try:
                # Get user from request (set by require_auth decorator)
                if not hasattr(request, 'user'):
                    return jsonify({"error": "Authentication required"}), 401
                
                user = request.user
                user_permissions = getattr(user, 'permissions', [])
                
                # Check if user has required permission
                if permission not in user_permissions and "*" not in user_permissions:
                    # Log permission denied
                    enterprise_security_manager.log_audit_event(
                        user_id=user.id,
                        tenant_id=getattr(request, 'tenant_id', None),
                        event_type="authorization",
                        resource="api",
                        action="permission_check",
                        details={"required_permission": permission, "user_permissions": user_permissions, "endpoint": request.endpoint},
                        ip_address=request.remote_addr,
                        success=False
                    )
                    return jsonify({"error": "Insufficient permissions"}), 403
                
                # Log successful permission check
                enterprise_security_manager.log_audit_event(
                    user_id=user.id,
                    tenant_id=getattr(request, 'tenant_id', None),
                    event_type="authorization",
                    resource="api",
                    action="permission_check",
                    details={"required_permission": permission, "endpoint": request.endpoint},
                    ip_address=request.remote_addr,
                    success=True
                )
                
            except Exception as e:
                # Log permission check error
                enterprise_security_manager.log_audit_event(
                    user_id=getattr(request, 'user', type('User', (), {'id': 'unknown'})().id),
                    tenant_id=getattr(request, 'tenant_id', None),
                    event_type="authorization",
                    resource="api",
                    action="permission_check",
                    details={"error": str(e), "endpoint": request.endpoint},
                    ip_address=request.remote_addr,
                    success=False
                )
                return jsonify({"error": "Permission check failed"}), 500
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Existing routes
@app.route("/orchestrator/start-workflow", methods=["POST"])
@require_auth
@require_permission_enhanced("execute_workflows", tenant_aware=True)
def start_workflow():
    data = request.json or {}
    workflow = data.get("workflow")
    
    if not workflow:
        return jsonify({"error": "workflow is required"}), 400
    
    # Check tenant limits
    tenant_id = get_tenant_from_request()
    if tenant_id:
        tenant = tenant_manager.get_tenant(tenant_id)
        if tenant:
            # Get actual workflow count for tenant
            current_workflows = orch.get_tenant_workflow_count(tenant_id)
            if not tenant_manager.check_limit("max_workflows", current_workflows + 1):
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

@app.route("/api/metrics", methods=["GET"])
@limiter.exempt
@require_auth
@require_permission("view_analytics")
@dev_unlimited
def api_metrics():
    # Compose BMADMetrics structure expected by frontend
    agents = _get_agents_list()
    total_agents = len(agents)
    active_agents = sum(1 for a in agents if a.get("status") == "active")

    # Uptime in a human-readable format
    uptime_seconds = (datetime.utcnow() - APP_START_TIME).total_seconds()
    uptime_str = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"

    metrics = {
        "system_health": {
            "status": "healthy",
            "uptime": uptime_str,
            "memory_usage": "N/A",
            "cpu_usage": "N/A",
            "disk_usage": "N/A",
            "network_sent_mb": "N/A",
            "network_recv_mb": "N/A",
            "agent_success_rate": 92,
            "average_response_time": 120,
            "system_health_score": 95
        },
        "agents": {
            "total": total_agents,
            "active": active_agents,
            "idle": total_agents - active_agents,
        },
        "workflows": {
            "total": 0,
            "running": 0,
            "pending": 0,
            "completed": 0,
        }
    }

    return jsonify({
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/agents", methods=["GET"])
@require_auth
def list_agents():
    agents = [
        {"id": "orchestrator", "name": "Orchestrator", "status": "active", "type": "orchestrator"},
        {"id": "product-owner", "name": "ProductOwner", "status": "idle", "type": "planning"},
        {"id": "architect", "name": "Architect", "status": "idle", "type": "planning"},
        {"id": "scrummaster", "name": "Scrummaster", "status": "idle", "type": "management"},
        {"id": "frontend", "name": "FrontendDeveloper", "status": "idle", "type": "development"},
        {"id": "backend", "name": "BackendDeveloper", "status": "idle", "type": "development"},
        {"id": "fullstack", "name": "FullstackDeveloper", "status": "idle", "type": "development"},
        {"id": "mobile", "name": "MobileDeveloper", "status": "idle", "type": "development"},
        {"id": "data", "name": "DataEngineer", "status": "idle", "type": "development"},
        {"id": "devops", "name": "DevOpsInfra", "status": "idle", "type": "infrastructure"},
        {"id": "quality", "name": "QualityGuardian", "status": "idle", "type": "quality"},
        {"id": "docs", "name": "DocumentationAgent", "status": "idle", "type": "documentation"},
        {"id": "feedback", "name": "FeedbackAgent", "status": "idle", "type": "feedback"},
        {"id": "accessibility", "name": "AccessibilityAgent", "status": "idle", "type": "accessibility"},
        {"id": "release", "name": "ReleaseManager", "status": "idle", "type": "release"},
        {"id": "retro", "name": "Retrospective", "status": "idle", "type": "retrospective"},
        {"id": "rnd", "name": "RnD", "status": "idle", "type": "research"},
        {"id": "ai", "name": "AiDeveloper", "status": "idle", "type": "development"},
        {"id": "security", "name": "SecurityDeveloper", "status": "idle", "type": "security"},
        {"id": "strategy", "name": "StrategiePartner", "status": "idle", "type": "strategy"},
        {"id": "test", "name": "TestEngineer", "status": "idle", "type": "testing"},
        {"id": "uxui", "name": "UXUIDesigner", "status": "idle", "type": "design"},
        {"id": "workflow", "name": "WorkflowAutomator", "status": "idle", "type": "automation"},
    ]
    return jsonify({
        "agents": agents,
        "total": len(agents),
        "active": sum(1 for a in agents if a.get("status") == "active"),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/agent/<agent_name>/command", methods=["POST"])
@require_auth
@require_permission_enhanced("execute_agents", tenant_aware=True)
def agent_command(agent_name):
    data = request.json or {}
    command = data.get("command")
    
    # Check tenant limits
    tenant_id = get_tenant_from_request()
    if tenant_id:
        tenant = tenant_manager.get_tenant(tenant_id)
        if tenant:
            # Get actual agent count for tenant
            current_agents = orch.get_tenant_agent_count(tenant_id)
            if not tenant_manager.check_limit("max_agents", current_agents + 1):
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
    
    # Generate JWT token pair
    try:
        # Get user roles and permissions
        user_roles = role_manager.get_user_roles(user.id)
        user_permissions = permission_manager.get_user_permissions(user.id)
        
        # Create token pair
        token_data = jwt_service.create_token_pair(
            user_id=user.id,
            email=user.email,
            tenant_id=user.tenant_id,
            roles=[role.name for role in user_roles],
            permissions=[perm.name for perm in user_permissions]
        )
        
        return jsonify({
            "user": user.to_dict(),
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "token_type": token_data["token_type"],
            "expires_in": token_data["expires_in"],
            "refresh_expires_in": token_data["refresh_expires_in"],
            "tenant": tenant_manager.get_tenant(user.tenant_id).to_dict() if user.tenant_id else None
        })
        
    except Exception as e:
        logger.error(f"JWT token generation failed: {e}")
        return jsonify({"error": "Token generation failed"}), 500

@app.route("/api/auth/refresh", methods=["POST"])
def refresh_token():
    """Refresh access token using refresh token."""
    data = request.json or {}
    refresh_token = data.get("refresh_token")
    
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 400
    
    try:
        # Refresh access token
        token_data = jwt_service.refresh_access_token(refresh_token)
        
        if not token_data:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        return jsonify({
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
            "expires_in": token_data["expires_in"]
        })
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return jsonify({"error": "Token refresh failed"}), 500

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
        elif period == "current_quarter":
            usage_data[metric] = usage_tracker.get_current_quarter_usage(tenant_id, metric)
        elif period == "current_year":
            usage_data[metric] = usage_tracker.get_current_year_usage(tenant_id, metric)
        elif period == "last_month":
            usage_data[metric] = usage_tracker.get_last_month_usage(tenant_id, metric)
        elif period == "last_quarter":
            usage_data[metric] = usage_tracker.get_last_quarter_usage(tenant_id, metric)
        elif period == "last_year":
            usage_data[metric] = usage_tracker.get_last_year_usage(tenant_id, metric)
        else:
            # Default to current month for unknown periods
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

# Frontend utility routes for live data (dev-friendly)
@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/performance", methods=["GET"])
def api_performance():
    # Minimal structure expected by frontend: { metrics: [...], alerts: [...] }
    return jsonify({
        "metrics": [],
        "alerts": []
    })

@app.route("/api/logs", methods=["GET"])
def api_logs():
    # Minimal structure expected by frontend: { logs: [...] }
    return jsonify({
        "logs": []
    })

@app.route("/api/metrics-lite", methods=["GET"])
def api_metrics_lite():
    # Same payload shape as /api/metrics but without auth/rate-limit for dev UI
    agents = _get_agents_list()
    total_agents = len(agents)
    active_agents = sum(1 for a in agents if a.get("status") == "active")
    uptime_seconds = (datetime.utcnow() - APP_START_TIME).total_seconds()
    uptime_str = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
    metrics = {
        "system_health": {
            "status": "healthy",
            "uptime": uptime_str,
            "memory_usage": "N/A",
            "cpu_usage": "N/A",
            "disk_usage": "N/A",
            "network_sent_mb": "N/A",
            "network_recv_mb": "N/A",
            "agent_success_rate": 92,
            "average_response_time": 120,
            "system_health_score": 95
        },
        "agents": {
            "total": total_agents,
            "active": active_agents,
            "idle": total_agents - active_agents,
        },
        "workflows": {
            "total": 0,
            "running": 0,
            "pending": 0,
            "completed": 0,
        }
    }
    return jsonify({"metrics": metrics, "timestamp": datetime.utcnow().isoformat()})

@app.route("/health/circuit-breakers", methods=["GET"])
@require_auth
@require_permission("view_analytics")
def circuit_breaker_health():
    """Get circuit breaker health status."""
    from bmad.core.resilience.circuit_breaker import get_all_circuit_breakers
    
    stats = get_all_circuit_breakers()
    overall_health = "healthy"
    
    # Check if any circuit breakers are open
    open_circuits = [name for name, data in stats.items() if data["state"] == "OPEN"]
    if open_circuits:
        overall_health = "degraded"
    
    return jsonify({
        "status": overall_health,
        "circuit_breakers": stats,
        "open_circuits": open_circuits,
        "total_circuits": len(stats)
    })

@app.route("/health/error-handling", methods=["GET"])
@require_auth
@require_permission("view_analytics")
def error_handling_health():
    """Get error handling health status."""
    stats = error_handler.get_error_statistics()
    
    # Determine overall health based on error counts
    total_errors = stats["total_errors"]
    if total_errors == 0:
        overall_health = "healthy"
    elif total_errors < 10:
        overall_health = "warning"
    else:
        overall_health = "degraded"
    
    return jsonify({
        "status": overall_health,
        "error_statistics": stats,
        "total_errors": total_errors,
        "error_categories": list(stats["error_counts"].keys())
    })

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
    app.run(port=5003, debug=False)

# Export the Flask app for testing
__all__ = ['app']
