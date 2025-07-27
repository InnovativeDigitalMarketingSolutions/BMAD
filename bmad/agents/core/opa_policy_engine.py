"""
BMAD OPA Policy Engine

Dit module biedt granular autonomy en gedragspolicies voor BMAD agents via Open Policy Agent.
Maakt actions traceerbaar en controleerbaar met policy-based access control en behavior rules.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import yaml
from .opentelemetry_tracing import get_tracer, trace_agent

logger = logging.getLogger(__name__)

class PolicyType(Enum):
    ACCESS_CONTROL = "access_control"
    BEHAVIOR_RULES = "behavior_rules"
    RESOURCE_LIMITS = "resource_limits"
    SECURITY_POLICIES = "security_policies"
    WORKFLOW_POLICIES = "workflow_policies"

class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"

@dataclass
class PolicyRule:
    """Represents a policy rule."""
    name: str
    policy_type: PolicyType
    description: str
    rego_code: str
    enabled: bool = True
    priority: int = 100
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyRequest:
    """Request for policy evaluation."""
    subject: str  # Agent or user ID
    action: str   # Action being performed
    resource: str # Resource being accessed
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None

@dataclass
class PolicyResponse:
    """Response from policy evaluation."""
    decision: Decision
    allowed: bool
    reason: str
    conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None

@dataclass
class AgentPolicy:
    """Policy configuration for an agent."""
    agent_name: str
    allowed_actions: List[str] = field(default_factory=list)
    denied_actions: List[str] = field(default_factory=list)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    behavior_rules: List[str] = field(default_factory=list)
    security_level: str = "standard"
    autonomy_level: str = "medium"

class OPAPolicyEngine:
    """
    Open Policy Agent integration voor BMAD policy enforcement.
    """
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url
        self.policies: Dict[str, PolicyRule] = {}
        self.agent_policies: Dict[str, AgentPolicy] = {}
        self.http_session = None
        
        # Initialize default policies
        self._initialize_default_policies()
        
        # Initialize agent policies
        self._initialize_agent_policies()
        
        logger.info(f"OPA Policy Engine geïnitialiseerd met endpoint: {opa_url}")
    
    async def _get_http_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for OPA communication."""
        if self.http_session is None or self.http_session.closed:
            self.http_session = aiohttp.ClientSession()
        return self.http_session
    
    def _initialize_default_policies(self):
        """Initialize default policy rules."""
        default_policies = [
            PolicyRule(
                name="agent_access_control",
                policy_type=PolicyType.ACCESS_CONTROL,
                description="Basic access control for agents",
                rego_code="""
package bmad.access_control

default allow = false

allow {
    input.subject = "system"
}

allow {
    input.subject = "orchestrator"
}

allow {
    startswith(input.subject, "agent_")
    input.action = "read"
}

allow {
    startswith(input.subject, "agent_")
    input.action = "execute"
    input.resource = "own_tasks"
}

allow {
    startswith(input.subject, "agent_")
    input.action = "execute"
    input.resource = "workflow_tasks"
    input.context.workflow_id != ""
}
""",
                priority=100
            ),
            PolicyRule(
                name="resource_limits",
                policy_type=PolicyType.RESOURCE_LIMITS,
                description="Resource usage limits for agents",
                rego_code="""
package bmad.resource_limits

default allow = true

allow = false {
    input.context.tokens_used > 10000
}

allow = false {
    input.context.execution_time > 300
}

allow = false {
    input.context.memory_usage > 512
}
""",
                priority=200
            ),
            PolicyRule(
                name="security_policies",
                policy_type=PolicyType.SECURITY_POLICIES,
                description="Security policies for agent actions",
                rego_code="""
package bmad.security

default allow = true

allow = false {
    input.action = "file_write"
    not startswith(input.resource, "/tmp/")
    not startswith(input.resource, "./")
}

allow = false {
    input.action = "network_access"
    not input.context.allowed_domains[input.resource]
}

allow = false {
    input.action = "system_command"
    not input.context.allowed_commands[input.resource]
}
""",
                priority=150
            ),
            PolicyRule(
                name="workflow_policies",
                policy_type=PolicyType.WORKFLOW_POLICIES,
                description="Workflow execution policies",
                rego_code="""
package bmad.workflow

default allow = true

allow = false {
    input.action = "workflow_start"
    input.context.workflow_type = "production"
    input.subject != "orchestrator"
}

allow = false {
    input.action = "workflow_modify"
    input.context.workflow_status = "running"
    input.subject != "orchestrator"
}

allow = false {
    input.action = "workflow_delete"
    input.context.workflow_status = "completed"
    input.context.retention_days < 30
}
""",
                priority=120
            ),
        ]
        
        for policy in default_policies:
            self.policies[policy.name] = policy
    
    def _initialize_agent_policies(self):
        """Initialize default agent policies."""
        agent_policies = {
            "ProductOwner": AgentPolicy(
                agent_name="ProductOwner",
                allowed_actions=["create_user_story", "prioritize_backlog", "review_requirements"],
                resource_limits={"max_tokens": 8000, "max_execution_time": 600},
                security_level="high",
                autonomy_level="high"
            ),
            "Architect": AgentPolicy(
                agent_name="Architect",
                allowed_actions=["design_system", "create_architecture", "review_design"],
                resource_limits={"max_tokens": 12000, "max_execution_time": 900},
                security_level="high",
                autonomy_level="high"
            ),
            "FullstackDeveloper": AgentPolicy(
                agent_name="FullstackDeveloper",
                allowed_actions=["implement_feature", "write_tests", "debug_code"],
                resource_limits={"max_tokens": 15000, "max_execution_time": 1200},
                security_level="medium",
                autonomy_level="medium"
            ),
            "TestEngineer": AgentPolicy(
                agent_name="TestEngineer",
                allowed_actions=["run_tests", "create_test_plan", "analyze_coverage"],
                resource_limits={"max_tokens": 10000, "max_execution_time": 800},
                security_level="medium",
                autonomy_level="medium"
            ),
            "DevOpsInfra": AgentPolicy(
                agent_name="DevOpsInfra",
                allowed_actions=["deploy_application", "manage_infrastructure", "monitor_systems"],
                resource_limits={"max_tokens": 8000, "max_execution_time": 600},
                security_level="high",
                autonomy_level="low"
            ),
            "SecurityDeveloper": AgentPolicy(
                agent_name="SecurityDeveloper",
                allowed_actions=["security_scan", "vulnerability_assessment", "security_review"],
                resource_limits={"max_tokens": 12000, "max_execution_time": 900},
                security_level="critical",
                autonomy_level="low"
            ),
        }
        
        self.agent_policies.update(agent_policies)
    
    async def evaluate_policy(
        self,
        request: PolicyRequest,
        policy_names: Optional[List[str]] = None
    ) -> PolicyResponse:
        """
        Evaluate policies for a given request.
        
        Args:
            request: Policy evaluation request
            policy_names: Specific policies to evaluate (None for all)
            
        Returns:
            PolicyResponse with decision and metadata
        """
        tracer = get_tracer()
        start_time = time.time()
        
        if request.timestamp is None:
            request.timestamp = start_time
        
        # Get agent policy if applicable
        agent_policy = self.agent_policies.get(request.subject)
        
        # Prepare input for OPA
        opa_input = {
            "subject": request.subject,
            "action": request.action,
            "resource": request.resource,
            "context": request.context,
            "timestamp": request.timestamp,
            "agent_policy": agent_policy.__dict__ if agent_policy else None,
        }
        
        # Determine which policies to evaluate
        if policy_names is None:
            policies_to_evaluate = list(self.policies.values())
        else:
            policies_to_evaluate = [
                self.policies[name] for name in policy_names 
                if name in self.policies
            ]
        
        # Sort by priority (lower number = higher priority)
        policies_to_evaluate.sort(key=lambda p: p.priority)
        
        # Evaluate each policy
        decisions = []
        for policy in policies_to_evaluate:
            if not policy.enabled:
                continue
            
            try:
                decision = await self._evaluate_single_policy(policy, opa_input)
                decisions.append(decision)
                
                # If policy denies, stop evaluation
                if not decision["allow"]:
                    break
                    
            except Exception as e:
                logger.error(f"Policy evaluation failed for {policy.name}: {e}")
                # Use fallback evaluation when OPA server is not available
                if "Cannot connect to host" in str(e):
                    logger.warning("OPA server not available, using fallback policy evaluation")
                    return self._fallback_policy_evaluation(request)
                else:
                    decisions.append({
                        "policy": policy.name,
                        "allow": False,
                        "reason": f"Policy evaluation error: {e}"
                    })
                    break
        
        # Determine final decision
        final_decision = self._determine_final_decision(decisions)
        
        # Create response
        response = PolicyResponse(
            decision=final_decision["decision"],
            allowed=final_decision["allow"],
            reason=final_decision["reason"],
            conditions=final_decision.get("conditions", []),
            metadata={
                "policies_evaluated": len(decisions),
                "evaluation_time": time.time() - start_time,
                "policy_decisions": decisions,
            },
            trace_id=tracer.get_trace_id() if tracer else None
        )
        
        # Log policy evaluation
        logger.info(f"Policy evaluation: {request.subject} -> {request.action} -> {response.decision.value}")
        
        return response
    
    async def _evaluate_single_policy(self, policy: PolicyRule, opa_input: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single policy using OPA."""
        try:
            session = await self._get_http_session()
            
            # Prepare OPA query
            query_url = f"{self.opa_url}/v1/query"
            query_data = {
                "query": "data.bmad.allow",
                "input": opa_input,
                "unknowns": ["data.bmad"]
            }
            
            # Add policy code to unknowns
            query_data["unknowns"].append(f"data.bmad.{policy.name}")
            
            async with session.post(query_url, json=query_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if policy allows the action
                    allow = result.get("result", False)
                    
                    return {
                        "policy": policy.name,
                        "allow": allow,
                        "reason": f"Policy {policy.name} {'allowed' if allow else 'denied'} the action",
                        "opa_result": result
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"OPA query failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"OPA communication error: {e}")
            # Fallback to local policy evaluation when OPA server is not available
            return self._fallback_policy_evaluation(policy, opa_input)
    
    def _fallback_policy_evaluation(self, policy: PolicyRule, opa_input: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback policy evaluation when OPA server is not available."""
        logger.warning(f"Using fallback policy evaluation for {policy.name}")
        
        # Simple fallback logic based on policy type
        subject = opa_input.get("subject", "")
        action = opa_input.get("action", "")
        resource = opa_input.get("resource", "")
        
        # Default allow for most actions in test mode
        if "test" in subject.lower() or "test" in action.lower():
            return {
                "policy": policy.name,
                "allow": True,
                "reason": f"Fallback: Test mode - {policy.name} allowed",
                "fallback": True
            }
        
        # Deny dangerous actions
        dangerous_actions = ["delete", "remove", "destroy", "format"]
        if any(dangerous in action.lower() for dangerous in dangerous_actions):
            return {
                "policy": policy.name,
                "allow": False,
                "reason": f"Fallback: Dangerous action '{action}' denied by {policy.name}",
                "fallback": True
            }
        
        # Allow by default
        return {
            "policy": policy.name,
            "allow": True,
            "reason": f"Fallback: {policy.name} allowed by default",
            "fallback": True
        }
    
    def _determine_final_decision(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine final decision based on all policy evaluations."""
        if not decisions:
            return {
                "decision": Decision.ALLOW,
                "allow": True,
                "reason": "No policies evaluated"
            }
        
        # Check for any explicit denies
        for decision in decisions:
            if not decision["allow"]:
                return {
                    "decision": Decision.DENY,
                    "allow": False,
                    "reason": decision["reason"],
                    "conditions": [f"Policy {decision['policy']} denied the action"]
                }
        
        # All policies allowed
        return {
            "decision": Decision.ALLOW,
            "allow": True,
            "reason": "All policies allowed the action",
            "conditions": [f"Policy {d['policy']} allowed the action" for d in decisions]
        }
    
    def add_policy(self, policy: PolicyRule):
        """Add a new policy rule."""
        self.policies[policy.name] = policy
        logger.info(f"Policy '{policy.name}' toegevoegd")
    
    def remove_policy(self, policy_name: str):
        """Remove a policy rule."""
        if policy_name in self.policies:
            del self.policies[policy_name]
            logger.info(f"Policy '{policy_name}' verwijderd")
    
    def update_policy(self, policy_name: str, **updates):
        """Update an existing policy rule."""
        if policy_name in self.policies:
            policy = self.policies[policy_name]
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            logger.info(f"Policy '{policy_name}' bijgewerkt")
    
    def get_policy(self, policy_name: str) -> Optional[PolicyRule]:
        """Get a policy rule by name."""
        return self.policies.get(policy_name)
    
    def list_policies(self, policy_type: Optional[PolicyType] = None) -> List[PolicyRule]:
        """List all policies, optionally filtered by type."""
        policies = list(self.policies.values())
        if policy_type:
            policies = [p for p in policies if p.policy_type == policy_type]
        return policies
    
    def add_agent_policy(self, agent_policy: AgentPolicy):
        """Add or update an agent policy."""
        self.agent_policies[agent_policy.agent_name] = agent_policy
        logger.info(f"Agent policy voor '{agent_policy.agent_name}' toegevoegd/bijgewerkt")
    
    def get_agent_policy(self, agent_name: str) -> Optional[AgentPolicy]:
        """Get agent policy by name."""
        return self.agent_policies.get(agent_name)
    
    def list_agent_policies(self) -> List[AgentPolicy]:
        """List all agent policies."""
        return list(self.agent_policies.values())
    
    async def validate_agent_action(
        self,
        agent_name: str,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None
    ) -> PolicyResponse:
        """
        Validate if an agent can perform an action on a resource.
        
        Args:
            agent_name: Name of the agent
            action: Action to perform
            resource: Resource to act on
            context: Additional context
            
        Returns:
            PolicyResponse with validation result
        """
        request = PolicyRequest(
            subject=agent_name,
            action=action,
            resource=resource,
            context=context or {}
        )
        
        return await self.evaluate_policy(request)
    
    async def check_workflow_permission(
        self,
        agent_name: str,
        workflow_id: str,
        action: str,
        workflow_context: Optional[Dict[str, Any]] = None
    ) -> PolicyResponse:
        """
        Check if an agent has permission to perform an action on a workflow.
        
        Args:
            agent_name: Name of the agent
            workflow_id: Workflow ID
            action: Action to perform
            workflow_context: Workflow context
            
        Returns:
            PolicyResponse with permission result
        """
        context = {
            "workflow_id": workflow_id,
            "workflow_context": workflow_context or {}
        }
        
        return await self.validate_agent_action(
            agent_name=agent_name,
            action=action,
            resource=f"workflow:{workflow_id}",
            context=context
        )
    
    def export_policies(self, format: str = "json") -> str:
        """Export all policies in the specified format."""
        if format.lower() == "json":
            return json.dumps({
                "policies": [policy.__dict__ for policy in self.policies.values()],
                "agent_policies": [policy.__dict__ for policy in self.agent_policies.values()]
            }, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump({
                "policies": [policy.__dict__ for policy in self.policies.values()],
                "agent_policies": [policy.__dict__ for policy in self.agent_policies.values()]
            }, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_policies(self, policies_data: str, format: str = "json"):
        """Import policies from the specified format."""
        if format.lower() == "json":
            data = json.loads(policies_data)
        elif format.lower() == "yaml":
            data = yaml.safe_load(policies_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Import policies
        if "policies" in data:
            for policy_dict in data["policies"]:
                policy = PolicyRule(**policy_dict)
                self.add_policy(policy)
        
        # Import agent policies
        if "agent_policies" in data:
            for agent_policy_dict in data["agent_policies"]:
                agent_policy = AgentPolicy(**agent_policy_dict)
                self.add_agent_policy(agent_policy)
    
    async def close(self):
        """Close the policy engine and cleanup resources."""
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()

# Global policy engine instance
_global_policy_engine: Optional[OPAPolicyEngine] = None

def initialize_policy_engine(opa_url: str = "http://localhost:8181") -> OPAPolicyEngine:
    """Initialize global policy engine."""
    global _global_policy_engine
    _global_policy_engine = OPAPolicyEngine(opa_url)
    return _global_policy_engine

def get_policy_engine() -> Optional[OPAPolicyEngine]:
    """Get the global policy engine instance."""
    return _global_policy_engine

def require_policy_permission(action: str, resource: str):
    """Decorator to require policy permission for a function."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            policy_engine = get_policy_engine()
            if not policy_engine:
                return await func(*args, **kwargs)
            
            # Extract agent name from function context
            agent_name = getattr(func, '__self__', None)
            if agent_name:
                agent_name = agent_name.__class__.__name__
            else:
                agent_name = "unknown"
            
            # Validate permission
            response = await policy_engine.validate_agent_action(
                agent_name=agent_name,
                action=action,
                resource=resource,
                context=kwargs
            )
            
            if not response.allowed:
                raise PermissionError(f"Policy denied: {response.reason}")
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            policy_engine = get_policy_engine()
            if not policy_engine:
                return func(*args, **kwargs)
            
            # Extract agent name from function context
            agent_name = getattr(func, '__self__', None)
            if agent_name:
                agent_name = agent_name.__class__.__name__
            else:
                agent_name = "unknown"
            
            # Validate permission (sync version)
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(
                policy_engine.validate_agent_action(
                    agent_name=agent_name,
                    action=action,
                    resource=resource,
                    context=kwargs
                )
            )
            
            if not response.allowed:
                raise PermissionError(f"Policy denied: {response.reason}")
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 