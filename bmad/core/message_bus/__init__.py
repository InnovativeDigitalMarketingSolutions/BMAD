#!/usr/bin/env python3
"""
BMAD Message Bus Module
Centrale message bus voor inter-agent communicatie
"""

from .message_bus import (
    MessageBus,
    get_message_bus,
    publish_event,
    subscribe_to_event
)

from .events import (
    EventTypes,
    get_events_by_category,
    get_all_event_types,
    is_valid_event_type,
    EVENT_CATEGORIES
)

from .agent_integration import (
    AgentMessageBusIntegration,
    create_agent_integration
)

__all__ = [
    # Message bus core
    "MessageBus",
    "get_message_bus",
    "publish_event",
    "subscribe_to_event",
    
    # Events
    "EventTypes",
    "get_events_by_category",
    "get_all_event_types",
    "is_valid_event_type",
    "EVENT_CATEGORIES",
    
    # Agent integration
    "AgentMessageBusIntegration",
    "create_agent_integration"
] 