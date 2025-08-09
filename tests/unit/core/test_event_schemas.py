import pytest
from bmad.core.message_bus.events import EventTypes
from bmad.core.message_bus.schemas import validate_event_payload


def test_validate_completed_minimal():
    data = {"status": "completed", "agent": "Test", "timestamp": "2025-08-09T12:00:00"}
    validate_event_payload(EventTypes.API_DESIGN_COMPLETED, data)


def test_validate_failed_requires_error():
    data = {"status": "failed", "agent": "Test"}
    with pytest.raises(ValueError):
        validate_event_payload(EventTypes.API_DESIGN_FAILED, data)


def test_validate_failed_ok_with_error():
    data = {"status": "failed", "agent": "Test", "error": "boom"}
    validate_event_payload(EventTypes.API_DESIGN_FAILED, data)


def test_validate_documentation_completed_minimal():
    data = {"status": "completed", "agent": "Doc", "timestamp": "2025-08-09T12:00:00"}
    validate_event_payload(EventTypes.DOCUMENTATION_COMPLETED, data)


def test_validate_deployment_completed_minimal():
    data = {"status": "completed", "agent": "DevOps", "timestamp": "2025-08-09T12:00:00"}
    validate_event_payload(EventTypes.DEPLOYMENT_COMPLETED, data)


def test_validate_workflow_execution_completed_minimal():
    data = {"status": "completed", "agent": "WF", "timestamp": "2025-08-09T12:00:00"}
    validate_event_payload(EventTypes.WORKFLOW_EXECUTION_COMPLETED, data)


def test_validate_architecture_review_completed_minimal():
    data = {"status": "completed", "agent": "Arch", "timestamp": "2025-08-09T12:00:00"}
    validate_event_payload(EventTypes.ARCHITECTURE_REVIEW_COMPLETED, data) 