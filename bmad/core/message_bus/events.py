#!/usr/bin/env python3
"""
BMAD Event Types
Definitie van alle event types voor inter-agent communicatie
"""

class EventTypes:
    """Event types for BMAD message bus"""
    
    # Product Development Events
    USER_STORY_REQUESTED = "user_story_requested"
    USER_STORY_CREATED = "user_story_created"
    USER_STORY_UPDATED = "user_story_updated"
    USER_STORY_COMPLETED = "user_story_completed"
    USER_STORIES_CREATED = "user_stories_created"
    USER_STORY_CREATION_FAILED = "user_story_creation_failed"
    EPIC_CREATED = "epic_created"
    EPIC_UPDATED = "epic_updated"
    EPIC_COMPLETED = "epic_completed"
    
    # Sprint Events
    SPRINT_STARTED = "sprint_started"
    SPRINT_COMPLETED = "sprint_completed"
    SPRINT_REVIEW_REQUESTED = "sprint_review_requested"
    DAILY_STANDUP_COMPLETED = "daily_standup_completed"
    
    # Development Events
    API_DESIGN_REQUESTED = "api_design_requested"
    API_DESIGN_COMPLETED = "api_design_completed"
    COMPONENT_BUILD_REQUESTED = "component_build_requested"
    COMPONENT_BUILD_COMPLETED = "component_build_completed"
    BACKEND_BUILD_REQUESTED = "backend_build_requested"
    BACKEND_BUILD_COMPLETED = "backend_build_completed"
    FRONTEND_BUILD_REQUESTED = "frontend_build_requested"
    FRONTEND_BUILD_COMPLETED = "frontend_build_completed"
    FULLSTACK_BUILD_REQUESTED = "fullstack_build_requested"
    FULLSTACK_BUILD_COMPLETED = "fullstack_build_completed"
    
    # Testing Events
    TEST_EXECUTION_REQUESTED = "test_execution_requested"
    TEST_EXECUTION_COMPLETED = "test_execution_completed"
    TEST_RESULTS_AVAILABLE = "test_results_available"
    TEST_FAILURE_DETECTED = "test_failure_detected"
    TEST_COVERAGE_UPDATED = "test_coverage_updated"
    
    # Quality Events
    SECURITY_REVIEW_REQUESTED = "security_review_requested"
    SECURITY_REVIEW_COMPLETED = "security_review_completed"
    SECURITY_VULNERABILITY_DETECTED = "security_vulnerability_detected"
    ACCESSIBILITY_AUDIT_REQUESTED = "accessibility_audit_requested"
    ACCESSIBILITY_AUDIT_COMPLETED = "accessibility_audit_completed"
    CODE_REVIEW_REQUESTED = "code_review_requested"
    CODE_REVIEW_COMPLETED = "code_review_completed"
    QUALITY_GATE_CHECK_REQUESTED = "quality_gate_check_requested"
    QUALITY_GATE_PASSED = "quality_gate_passed"
    QUALITY_GATE_FAILED = "quality_gate_failed"
    
    # Feedback Events
    FEEDBACK_COLLECTED = "feedback_collected"
    FEEDBACK_ANALYZED = "feedback_analyzed"
    FEEDBACK_TREND_DETECTED = "feedback_trend_detected"
    IMPROVEMENT_SUGGESTED = "improvement_suggested"
    SENTIMENT_ANALYSIS_COMPLETED = "sentiment_analysis_completed"
    
    # Documentation Events
    DOCUMENTATION_REQUESTED = "documentation_requested"
    DOCUMENTATION_COMPLETED = "documentation_completed"
    API_DOCS_GENERATED = "api_docs_generated"
    USER_GUIDE_UPDATED = "user_guide_updated"
    TECHNICAL_DOCS_UPDATED = "technical_docs_updated"
    
    # DevOps Events
    DEPLOYMENT_REQUESTED = "deployment_requested"
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    DEPLOYMENT_FAILED = "deployment_failed"
    INFRASTRUCTURE_UPDATED = "infrastructure_updated"
    MONITORING_ALERT = "monitoring_alert"
    PERFORMANCE_METRICS_UPDATED = "performance_metrics_updated"
    
    # Release Events
    RELEASE_REQUESTED = "release_requested"
    RELEASE_PREPARATION_STARTED = "release_preparation_started"
    RELEASE_PREPARATION_COMPLETED = "release_preparation_completed"
    RELEASE_DEPLOYED = "release_deployed"
    RELEASE_ROLLBACK_REQUESTED = "release_rollback_requested"
    RELEASE_ROLLBACK_COMPLETED = "release_rollback_completed"
    
    # AI/ML Events
    AI_MODEL_TRAINING_REQUESTED = "ai_model_training_requested"
    AI_MODEL_TRAINING_COMPLETED = "ai_model_training_completed"
    AI_MODEL_DEPLOYMENT_REQUESTED = "ai_model_deployment_requested"
    AI_MODEL_DEPLOYMENT_COMPLETED = "ai_model_deployment_completed"
    AI_EXPERIMENT_STARTED = "ai_experiment_started"
    AI_EXPERIMENT_COMPLETED = "ai_experiment_completed"
    
    # Data Events
    DATA_PIPELINE_REQUESTED = "data_pipeline_requested"
    DATA_PIPELINE_COMPLETED = "data_pipeline_completed"
    DATA_QUALITY_CHECK_REQUESTED = "data_quality_check_requested"
    DATA_QUALITY_CHECK_COMPLETED = "data_quality_check_completed"
    DATA_ANALYSIS_REQUESTED = "data_analysis_requested"
    DATA_ANALYSIS_COMPLETED = "data_analysis_completed"
    
    # Research Events
    RESEARCH_REQUESTED = "research_requested"
    RESEARCH_COMPLETED = "research_completed"
    INNOVATION_IDEA_GENERATED = "innovation_idea_generated"
    TECHNOLOGY_EVALUATION_REQUESTED = "technology_evaluation_requested"
    TECHNOLOGY_EVALUATION_COMPLETED = "technology_evaluation_completed"
    
    # Retrospective Events
    RETROSPECTIVE_REQUESTED = "retrospective_requested"
    RETROSPECTIVE_COMPLETED = "retrospective_completed"
    IMPROVEMENT_ACTION_IDENTIFIED = "improvement_action_identified"
    IMPROVEMENT_ACTION_COMPLETED = "improvement_action_completed"
    
    # Strategy Events
    STRATEGY_REVIEW_REQUESTED = "strategy_review_requested"
    STRATEGY_REVIEW_COMPLETED = "strategy_review_completed"
    ROADMAP_UPDATED = "roadmap_updated"
    BUSINESS_OBJECTIVE_UPDATED = "business_objective_updated"
    
    # Backlog Management Events
    BACKLOG_UPDATE_REQUESTED = "backlog_update_requested"
    BACKLOG_UPDATED = "backlog_updated"
    BACKLOG_UPDATE_FAILED = "backlog_update_failed"
    
    # Product Vision Events
    PRODUCT_VISION_REQUESTED = "product_vision_requested"
    PRODUCT_VISION_CREATED = "product_vision_created"
    PRODUCT_VISION_CREATION_FAILED = "product_vision_creation_failed"
    
    # Stakeholder Analysis Events
    STAKEHOLDER_ANALYSIS_REQUESTED = "stakeholder_analysis_requested"
    STAKEHOLDER_ANALYSIS_COMPLETED = "stakeholder_analysis_completed"
    STAKEHOLDER_ANALYSIS_FAILED = "stakeholder_analysis_failed"
    
    # Collaboration Events
    AGENT_COLLABORATION_REQUESTED = "agent_collaboration_requested"
    AGENT_COLLABORATION_STARTED = "agent_collaboration_started"
    AGENT_COLLABORATION_COMPLETED = "agent_collaboration_completed"
    TASK_DELEGATED = "task_delegated"
    TASK_ACCEPTED = "task_accepted"
    TASK_COMPLETED = "task_completed"
    
    # System Events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    ERROR_OCCURRED = "error_occurred"
    WARNING_GENERATED = "warning_generated"
    
    # MCP Events
    MCP_CONNECTION_ESTABLISHED = "mcp_connection_established"
    MCP_CONNECTION_LOST = "mcp_connection_lost"
    MCP_TOOL_CALLED = "mcp_tool_called"
    MCP_TOOL_COMPLETED = "mcp_tool_completed"
    MCP_TOOL_FAILED = "mcp_tool_failed"
    
    # Tracing Events
    TRACE_STARTED = "trace_started"
    TRACE_COMPLETED = "trace_completed"
    PERFORMANCE_METRIC_RECORDED = "performance_metric_recorded"
    
    # Resource Events
    RESOURCE_LOCKED = "resource_locked"
    RESOURCE_UNLOCKED = "resource_unlocked"
    RESOURCE_CONFLICT_DETECTED = "resource_conflict_detected"
    RESOURCE_CONFLICT_RESOLVED = "resource_conflict_resolved"
    
    # Workflow Events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_STEP_COMPLETED = "workflow_step_completed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_OPTIMIZATION_REQUESTED = "workflow_optimization_requested"
    WORKFLOW_OPTIMIZATION_COMPLETED = "workflow_optimization_completed"
    WORKFLOW_EXECUTION_REQUESTED = "workflow_execution_requested"
    WORKFLOW_EXECUTION_STARTED = "workflow_execution_started"
    WORKFLOW_EXECUTION_COMPLETED = "workflow_execution_completed"
    WORKFLOW_MONITORING_REQUESTED = "workflow_monitoring_requested"
    WORKFLOW_MONITORING_COMPLETED = "workflow_monitoring_completed"
    
    # Orchestration Events
    ORCHESTRATION_STARTED = "orchestration_started"
    ORCHESTRATION_COMPLETED = "orchestration_completed"
    ORCHESTRATION_FAILED = "orchestration_failed"
    
    # HITL Events
    HITL_DECISION = "hitl_decision"
    HITL_REQUESTED = "hitl_requested"
    
    # Idea Events
    IDEA_VALIDATION_REQUESTED = "idea_validation_requested"
    IDEA_REFINEMENT_REQUESTED = "idea_refinement_requested"
    EPIC_CREATION_REQUESTED = "epic_creation_requested"
    
    # Feedback Events (additional)
    FEEDBACK_RECEIVED = "feedback_received"
    FEEDBACK_PROCESSED = "feedback_processed"
    FEEDBACK_PROCESSING_FAILED = "feedback_processing_failed"
    PIPELINE_ADVICE_REQUESTED = "pipeline_advice_requested"

# Event categories for easier management
EVENT_CATEGORIES = {
    "product_development": [
        EventTypes.USER_STORY_REQUESTED,
        EventTypes.USER_STORY_CREATED,
        EventTypes.USER_STORY_UPDATED,
        EventTypes.USER_STORY_COMPLETED,
        EventTypes.USER_STORIES_CREATED,
        EventTypes.USER_STORY_CREATION_FAILED,
        EventTypes.EPIC_CREATED,
        EventTypes.EPIC_UPDATED,
        EventTypes.EPIC_COMPLETED,
    ],
    "sprint_management": [
        EventTypes.SPRINT_STARTED,
        EventTypes.SPRINT_COMPLETED,
        EventTypes.SPRINT_REVIEW_REQUESTED,
        EventTypes.DAILY_STANDUP_COMPLETED,
    ],
    "development": [
        EventTypes.API_DESIGN_REQUESTED,
        EventTypes.API_DESIGN_COMPLETED,
        EventTypes.COMPONENT_BUILD_REQUESTED,
        EventTypes.COMPONENT_BUILD_COMPLETED,
        EventTypes.BACKEND_BUILD_REQUESTED,
        EventTypes.BACKEND_BUILD_COMPLETED,
        EventTypes.FRONTEND_BUILD_REQUESTED,
        EventTypes.FRONTEND_BUILD_COMPLETED,
        EventTypes.FULLSTACK_BUILD_REQUESTED,
        EventTypes.FULLSTACK_BUILD_COMPLETED,
    ],
    "testing": [
        EventTypes.TEST_EXECUTION_REQUESTED,
        EventTypes.TEST_EXECUTION_COMPLETED,
        EventTypes.TEST_RESULTS_AVAILABLE,
        EventTypes.TEST_FAILURE_DETECTED,
        EventTypes.TEST_COVERAGE_UPDATED,
    ],
    "quality": [
        EventTypes.SECURITY_REVIEW_REQUESTED,
        EventTypes.SECURITY_REVIEW_COMPLETED,
        EventTypes.SECURITY_VULNERABILITY_DETECTED,
        EventTypes.ACCESSIBILITY_AUDIT_REQUESTED,
        EventTypes.ACCESSIBILITY_AUDIT_COMPLETED,
        EventTypes.CODE_REVIEW_REQUESTED,
        EventTypes.CODE_REVIEW_COMPLETED,
        EventTypes.QUALITY_GATE_CHECK_REQUESTED,
        EventTypes.QUALITY_GATE_PASSED,
        EventTypes.QUALITY_GATE_FAILED,
    ],
    "feedback": [
        EventTypes.FEEDBACK_COLLECTED,
        EventTypes.FEEDBACK_ANALYZED,
        EventTypes.FEEDBACK_TREND_DETECTED,
        EventTypes.IMPROVEMENT_SUGGESTED,
        EventTypes.SENTIMENT_ANALYSIS_COMPLETED,
        EventTypes.FEEDBACK_RECEIVED,
        EventTypes.FEEDBACK_PROCESSED,
        EventTypes.FEEDBACK_PROCESSING_FAILED,
        EventTypes.PIPELINE_ADVICE_REQUESTED,
    ],
    "user_stories": [
        EventTypes.USER_STORY_REQUESTED,
        EventTypes.USER_STORY_CREATED,
        EventTypes.USER_STORY_UPDATED,
        EventTypes.USER_STORY_COMPLETED,
        EventTypes.USER_STORIES_CREATED,
        EventTypes.USER_STORY_CREATION_FAILED,
    ],
    "backlog": [
        EventTypes.BACKLOG_UPDATE_REQUESTED,
        EventTypes.BACKLOG_UPDATED,
        EventTypes.BACKLOG_UPDATE_FAILED,
    ],
    "product_management": [
        EventTypes.PRODUCT_VISION_REQUESTED,
        EventTypes.PRODUCT_VISION_CREATED,
        EventTypes.PRODUCT_VISION_CREATION_FAILED,
        EventTypes.STAKEHOLDER_ANALYSIS_REQUESTED,
        EventTypes.STAKEHOLDER_ANALYSIS_COMPLETED,
        EventTypes.STAKEHOLDER_ANALYSIS_FAILED,
    ],
    "documentation": [
        EventTypes.DOCUMENTATION_REQUESTED,
        EventTypes.DOCUMENTATION_COMPLETED,
        EventTypes.API_DOCS_GENERATED,
        EventTypes.USER_GUIDE_UPDATED,
        EventTypes.TECHNICAL_DOCS_UPDATED,
    ],
    "devops": [
        EventTypes.DEPLOYMENT_REQUESTED,
        EventTypes.DEPLOYMENT_STARTED,
        EventTypes.DEPLOYMENT_COMPLETED,
        EventTypes.DEPLOYMENT_FAILED,
        EventTypes.INFRASTRUCTURE_UPDATED,
        EventTypes.MONITORING_ALERT,
        EventTypes.PERFORMANCE_METRICS_UPDATED,
    ],
    "release": [
        EventTypes.RELEASE_REQUESTED,
        EventTypes.RELEASE_PREPARATION_STARTED,
        EventTypes.RELEASE_PREPARATION_COMPLETED,
        EventTypes.RELEASE_DEPLOYED,
        EventTypes.RELEASE_ROLLBACK_REQUESTED,
        EventTypes.RELEASE_ROLLBACK_COMPLETED,
    ],
    "ai_ml": [
        EventTypes.AI_MODEL_TRAINING_REQUESTED,
        EventTypes.AI_MODEL_TRAINING_COMPLETED,
        EventTypes.AI_MODEL_DEPLOYMENT_REQUESTED,
        EventTypes.AI_MODEL_DEPLOYMENT_COMPLETED,
        EventTypes.AI_EXPERIMENT_STARTED,
        EventTypes.AI_EXPERIMENT_COMPLETED,
    ],
    "data": [
        EventTypes.DATA_PIPELINE_REQUESTED,
        EventTypes.DATA_PIPELINE_COMPLETED,
        EventTypes.DATA_QUALITY_CHECK_REQUESTED,
        EventTypes.DATA_QUALITY_CHECK_COMPLETED,
        EventTypes.DATA_ANALYSIS_REQUESTED,
        EventTypes.DATA_ANALYSIS_COMPLETED,
    ],
    "research": [
        EventTypes.RESEARCH_REQUESTED,
        EventTypes.RESEARCH_COMPLETED,
        EventTypes.INNOVATION_IDEA_GENERATED,
        EventTypes.TECHNOLOGY_EVALUATION_REQUESTED,
        EventTypes.TECHNOLOGY_EVALUATION_COMPLETED,
    ],
    "retrospective": [
        EventTypes.RETROSPECTIVE_REQUESTED,
        EventTypes.RETROSPECTIVE_COMPLETED,
        EventTypes.IMPROVEMENT_ACTION_IDENTIFIED,
        EventTypes.IMPROVEMENT_ACTION_COMPLETED,
    ],
    "strategy": [
        EventTypes.STRATEGY_REVIEW_REQUESTED,
        EventTypes.STRATEGY_REVIEW_COMPLETED,
        EventTypes.ROADMAP_UPDATED,
        EventTypes.BUSINESS_OBJECTIVE_UPDATED,
    ],
    "collaboration": [
        EventTypes.AGENT_COLLABORATION_REQUESTED,
        EventTypes.AGENT_COLLABORATION_STARTED,
        EventTypes.AGENT_COLLABORATION_COMPLETED,
        EventTypes.TASK_DELEGATED,
        EventTypes.TASK_ACCEPTED,
        EventTypes.TASK_COMPLETED,
    ],
    "system": [
        EventTypes.SYSTEM_STARTUP,
        EventTypes.SYSTEM_SHUTDOWN,
        EventTypes.AGENT_STARTED,
        EventTypes.AGENT_STOPPED,
        EventTypes.ERROR_OCCURRED,
        EventTypes.WARNING_GENERATED,
    ],
    "mcp": [
        EventTypes.MCP_CONNECTION_ESTABLISHED,
        EventTypes.MCP_CONNECTION_LOST,
        EventTypes.MCP_TOOL_CALLED,
        EventTypes.MCP_TOOL_COMPLETED,
        EventTypes.MCP_TOOL_FAILED,
    ],
    "tracing": [
        EventTypes.TRACE_STARTED,
        EventTypes.TRACE_COMPLETED,
        EventTypes.PERFORMANCE_METRIC_RECORDED,
    ],
    "resources": [
        EventTypes.RESOURCE_LOCKED,
        EventTypes.RESOURCE_UNLOCKED,
        EventTypes.RESOURCE_CONFLICT_DETECTED,
        EventTypes.RESOURCE_CONFLICT_RESOLVED,
    ],
    "workflow": [
        EventTypes.WORKFLOW_STARTED,
        EventTypes.WORKFLOW_STEP_COMPLETED,
        EventTypes.WORKFLOW_COMPLETED,
        EventTypes.WORKFLOW_FAILED,
        EventTypes.WORKFLOW_OPTIMIZATION_REQUESTED,
        EventTypes.WORKFLOW_OPTIMIZATION_COMPLETED,
        EventTypes.WORKFLOW_EXECUTION_REQUESTED,
        EventTypes.WORKFLOW_EXECUTION_STARTED,
        EventTypes.WORKFLOW_EXECUTION_COMPLETED,
        EventTypes.WORKFLOW_MONITORING_REQUESTED,
        EventTypes.WORKFLOW_MONITORING_COMPLETED,
    ],
    "orchestration": [
        EventTypes.ORCHESTRATION_STARTED,
        EventTypes.ORCHESTRATION_COMPLETED,
        EventTypes.ORCHESTRATION_FAILED,
    ],
    "hitl": [
        EventTypes.HITL_DECISION,
        EventTypes.HITL_REQUESTED,
    ],
    "ideas": [
        EventTypes.IDEA_VALIDATION_REQUESTED,
        EventTypes.IDEA_REFINEMENT_REQUESTED,
        EventTypes.EPIC_CREATION_REQUESTED,
    ]
}

def get_events_by_category(category: str) -> list:
    """Get all events for a specific category"""
    return EVENT_CATEGORIES.get(category, [])

def get_all_event_types() -> list:
    """Get all event types"""
    return [getattr(EventTypes, attr) for attr in dir(EventTypes) 
            if not attr.startswith('_') and isinstance(getattr(EventTypes, attr), str)]

def is_valid_event_type(event_type: str) -> bool:
    """Check if event type is valid"""
    return event_type in get_all_event_types() 