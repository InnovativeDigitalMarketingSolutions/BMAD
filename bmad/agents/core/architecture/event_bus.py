"""
BMAD Event Bus

Event-driven architecture voor BMAD agents.
Zorgt voor loose coupling en scalable communication.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Event priorities voor ordered processing."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """Event data structure."""
    name: str
    data: Any
    timestamp: float
    source: str
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EventBus:
    """
    Event bus voor BMAD agents.
    Ondersteunt async event handling, priority queues, en event filtering.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._priority_subscribers: Dict[str, Dict[EventPriority, List[Callable]]] = defaultdict(lambda: defaultdict(list))
        self._event_history: List[Event] = []
        self._max_history: int = 1000
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._running: bool = False
    
    def subscribe(self, event_name: str, handler: Callable, priority: EventPriority = EventPriority.NORMAL):
        """
        Subscribe to een event.
        
        Args:
            event_name: Event naam
            handler: Event handler function
            priority: Event priority
        """
        if priority == EventPriority.NORMAL:
            self._subscribers[event_name].append(handler)
        else:
            self._priority_subscribers[event_name][priority].append(handler)
        
        logger.debug(f"Subscriber added for event: {event_name} with priority: {priority}")
    
    def unsubscribe(self, event_name: str, handler: Callable):
        """
        Unsubscribe from een event.
        
        Args:
            event_name: Event naam
            handler: Event handler function
        """
        # Remove from normal subscribers
        if event_name in self._subscribers:
            self._subscribers[event_name] = [
                h for h in self._subscribers[event_name] if h != handler
            ]
        
        # Remove from priority subscribers
        if event_name in self._priority_subscribers:
            for priority in EventPriority:
                self._priority_subscribers[event_name][priority] = [
                    h for h in self._priority_subscribers[event_name][priority] if h != handler
                ]
        
        logger.debug(f"Subscriber removed for event: {event_name}")
    
    async def publish(self, event_name: str, data: Any, source: str, 
                     priority: EventPriority = EventPriority.NORMAL,
                     correlation_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None):
        """
        Publish een event.
        
        Args:
            event_name: Event naam
            data: Event data
            source: Event source
            priority: Event priority
            correlation_id: Correlation ID voor tracing
            metadata: Extra metadata
        """
        event = Event(
            name=event_name,
            data=data,
            timestamp=time.time(),
            source=source,
            priority=priority,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Get all handlers for this event
        handlers = []
        
        # Add priority handlers in order
        for priority in sorted(EventPriority, key=lambda p: p.value, reverse=True):
            handlers.extend(self._priority_subscribers[event_name][priority])
        
        # Add normal handlers
        handlers.extend(self._subscribers[event_name])
        
        # Execute handlers
        if handlers:
            logger.debug(f"Publishing event: {event_name} to {len(handlers)} handlers")
            
            # Execute handlers asynchronously
            tasks = []
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        task = asyncio.create_task(handler(event))
                        tasks.append(task)
                    else:
                        # Run sync handler in thread pool
                        loop = asyncio.get_event_loop()
                        task = loop.run_in_executor(None, handler, event)
                        tasks.append(task)
                except Exception as e:
                    logger.error(f"Error creating task for handler {handler.__name__}: {e}")
            
            # Wait for all handlers to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        else:
            logger.debug(f"No handlers found for event: {event_name}")
    
    def publish_sync(self, event_name: str, data: Any, source: str,
                    priority: EventPriority = EventPriority.NORMAL,
                    correlation_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None):
        """
        Publish een event synchronously.
        
        Args:
            event_name: Event naam
            data: Event data
            source: Event source
            priority: Event priority
            correlation_id: Correlation ID voor tracing
            metadata: Extra metadata
        """
        event = Event(
            name=event_name,
            data=data,
            timestamp=time.time(),
            source=source,
            priority=priority,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Get all handlers for this event
        handlers = []
        
        # Add priority handlers in order
        for priority in sorted(EventPriority, key=lambda p: p.value, reverse=True):
            handlers.extend(self._priority_subscribers[event_name][priority])
        
        # Add normal handlers
        handlers.extend(self._subscribers[event_name])
        
        # Execute handlers synchronously
        if handlers:
            logger.debug(f"Publishing event synchronously: {event_name} to {len(handlers)} handlers")
            
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__}: {e}")
        else:
            logger.debug(f"No handlers found for event: {event_name}")
    
    def get_event_history(self, event_name: Optional[str] = None, 
                         since: Optional[float] = None,
                         limit: Optional[int] = None) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_name: Filter by event name
            since: Filter events since timestamp
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        events = self._event_history
        
        # Filter by event name
        if event_name:
            events = [e for e in events if e.name == event_name]
        
        # Filter by timestamp
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Apply limit
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_subscriber_count(self, event_name: str) -> int:
        """Get aantal subscribers voor een event."""
        count = len(self._subscribers[event_name])
        
        if event_name in self._priority_subscribers:
            for priority in EventPriority:
                count += len(self._priority_subscribers[event_name][priority])
        
        return count
    
    def get_all_events(self) -> Set[str]:
        """Get alle event names."""
        events = set(self._subscribers.keys())
        events.update(self._priority_subscribers.keys())
        return events
    
    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()
        logger.info("Event history cleared")

# Global event bus
event_bus = EventBus() 