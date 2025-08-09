from typing import Any, Dict
from pydantic import BaseModel, Field, ValidationError
from .events import EventTypes


class BaseEventPayload(BaseModel):
    status: str = Field(..., description="Event processing status: completed/failed/processing")
    agent: str | None = Field(default=None, description="Source agent name")
    timestamp: str | None = Field(default=None, description="ISO timestamp when the event was generated")


class FailedEventPayload(BaseEventPayload):
    error: str = Field(..., description="Error description for failed events")


# Curated set of completed-events that must include minimal contract
STRICT_COMPLETED_EVENTS = {
    EventTypes.API_DESIGN_COMPLETED,
    EventTypes.DOCUMENTATION_COMPLETED,
    EventTypes.DEPLOYMENT_COMPLETED,
    EventTypes.WORKFLOW_EXECUTION_COMPLETED,
    EventTypes.ARCHITECTURE_REVIEW_COMPLETED,
}


def validate_event_payload(event_type: str, data: Dict[str, Any]) -> None:
    """Validate event payload using Pydantic models.
    Rules:
    - Enforce strictly for *_FAILED events: require 'status' and 'error'
    - Enforce for specific *_COMPLETED events in STRICT_COMPLETED_EVENTS: require at least 'status'
    - For all other events or non-dict/None payloads: do not enforce (backward compatible)
    """
    if not isinstance(data, dict):
        return

    et = (event_type or "").lower()
    try:
        if et.endswith("_failed"):
            FailedEventPayload.model_validate(data)
        elif event_type in STRICT_COMPLETED_EVENTS:
            BaseEventPayload.model_validate(data)
        else:
            return
    except ValidationError as ve:
        raise ValueError(f"Invalid payload for {event_type}: {ve.errors()}" ) 