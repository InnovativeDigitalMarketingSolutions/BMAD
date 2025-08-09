#!/usr/bin/env python3
"""
BMAD Message Bus System
Centrale message bus voor inter-agent communicatie
"""

import asyncio
import json
import logging
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from pathlib import Path
import redis
from time import perf_counter
from dataclasses import dataclass, asdict
from .schemas import validate_event_payload
from bmad.core.tracing.tracing_service import get_tracing_service

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event data structure"""
    event_type: str
    data: Dict[str, Any]
    source_agent: str
    timestamp: datetime
    event_id: str
    correlation_id: Optional[str] = None

class MessageBus:
    """
    Central message bus for inter-agent communication
    Supports both Redis Pub/Sub and file-based fallback
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", use_redis: bool = True):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.redis_client = None
        self.use_redis = use_redis
        self.redis_url = redis_url
        self.event_file = Path("bmad/shared_context.json")
        # Basic in-memory observability metrics
        self.metrics: Dict[str, Any] = {
            "total_published": 0,
            "total_failed": 0,
            "per_event_type": {},
            "subscriber_calls": 0,
            "subscriber_failures": 0,
        }
        
        # Initialize Redis if available
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("✅ Redis connection established for message bus")
            except Exception as e:
                logger.warning(f"Redis connection failed, falling back to file-based: {e}")
                self.use_redis = False
        
        # Ensure event file exists
        self.event_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.event_file.exists():
            self._save_events_to_file()
    
    async def publish(self, event_type: str, data: Dict[str, Any], 
                     source_agent: str = "unknown", 
                     correlation_id: Optional[str] = None) -> bool:
        """
        Publish event to all subscribers
        
        Args:
            event_type: Type of event
            data: Event data
            source_agent: Agent that published the event
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            bool: Success status
        """
        start = perf_counter()
        tracing = get_tracing_service()
        span_attrs = {"event_type": event_type, "source_agent": source_agent}
        if correlation_id:
            span_attrs["correlation_id"] = correlation_id
        try:
            # Tracing span around publish
            span_ctx = tracing.trace_operation("message_bus.publish", span_attrs) if tracing else None
            __enter__ctx = span_ctx.__enter__() if span_ctx else None
            # Derive correlation_id from tracing if not provided
            if correlation_id is None:
                try:
                    trace_id = tracing.get_trace_id() if tracing else None
                    if trace_id:
                        correlation_id = trace_id
                except Exception:
                    pass

            # Ensure correlation_id is reflected in payload for downstream consumers
            if correlation_id is not None and isinstance(data, dict) and 'correlation_id' not in data:
                data = {**data, 'correlation_id': correlation_id}

            # Validate payload against schema
            validate_event_payload(event_type, data)
            # Create event
            event = Event(
                event_type=event_type,
                data=data,
                source_agent=source_agent,
                timestamp=datetime.now(),
                event_id=f"{event_type}_{datetime.now().timestamp()}",
                correlation_id=correlation_id
            )
            
            # Add to history
            self.event_history.append(event)
            
            # Publish to Redis if available
            if self.use_redis and self.redis_client:
                await self._publish_to_redis(event)
            
            # Notify local subscribers
            await self._notify_subscribers(event)
            
            # Save to file for persistence
            self._save_events_to_file()
            
            # Metrics update
            self.metrics["total_published"] += 1
            per = self.metrics["per_event_type"].setdefault(event_type, {"published": 0, "failed": 0})
            per["published"] += 1

            # Structured log
            elapsed_ms = round((perf_counter() - start) * 1000, 3)
            log_payload = {
                "msg": "event_published",
                "event_type": event_type,
                "source_agent": source_agent,
                "event_id": event.event_id,
                "correlation_id": correlation_id,
                "elapsed_ms": elapsed_ms,
                "timestamp": event.timestamp.isoformat(),
            }
            logger.info(json.dumps(log_payload))
            if span_ctx:
                # end span
                span_ctx.__exit__(None, None, None)
            return True
            
        except Exception as e:
            # Metrics failure
            self.metrics["total_failed"] += 1
            per = self.metrics["per_event_type"].setdefault(event_type, {"published": 0, "failed": 0})
            per["failed"] += 1
            # Structured error log
            err_payload = {
                "msg": "event_publish_failed",
                "event_type": event_type,
                "source_agent": source_agent,
                "error": str(e),
            }
            logger.error(json.dumps(err_payload))
            return False
    
    async def subscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Subscribe to event type
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is received
            
        Returns:
            bool: Success status
        """
        try:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            self.subscribers[event_type].append(callback)
            logger.info(json.dumps({"msg": "subscribed", "event_type": event_type}))
            return True
            
        except Exception as e:
            logger.error(json.dumps({"msg": "subscribe_failed", "event_type": event_type, "error": str(e)}))
            return False
    
    async def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from event type
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
            
        Returns:
            bool: Success status
        """
        try:
            if event_type in self.subscribers:
                if callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
                    logger.info(json.dumps({"msg": "unsubscribed", "event_type": event_type}))
                    return True
            
            return False
            
        except Exception as e:
            logger.error(json.dumps({"msg": "unsubscribe_failed", "event_type": event_type, "error": str(e)}))
            return False
    
    async def get_events(self, event_type: Optional[str] = None, 
                        limit: int = 100) -> List[Event]:
        """
        Get recent events
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List[Event]: List of events
        """
        try:
            events = self.event_history[-limit:] if limit > 0 else self.event_history
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            return events
            
        except Exception as e:
            logger.error(json.dumps({"msg": "get_events_failed", "error": str(e)}))
            return []
    
    async def _publish_to_redis(self, event: Event) -> None:
        """Publish event to Redis"""
        try:
            event_data = asdict(event)
            event_data['timestamp'] = event.timestamp.isoformat()
            
            # Publish to Redis channel
            self.redis_client.publish(
                f"bmad:events:{event.event_type}",
                json.dumps(event_data)
            )
            
            # Store in Redis for persistence
            self.redis_client.lpush(
                f"bmad:events:history:{event.event_type}",
                json.dumps(event_data)
            )
            
            # Keep only last 1000 events per type
            self.redis_client.ltrim(f"bmad:events:history:{event.event_type}", 0, 999)
            
        except Exception as e:
            logger.error(json.dumps({"msg": "redis_publish_failed", "event_type": event.event_type, "error": str(e)}))
    
    async def _notify_subscribers(self, event: Event) -> None:
        """Notify all subscribers of an event"""
        try:
            if event.event_type in self.subscribers:
                for callback in self.subscribers[event.event_type]:
                    try:
                        cb_name = getattr(callback, "__name__", str(callback))
                        tracing = get_tracing_service()
                        span_ctx = tracing.trace_operation("message_bus.callback", {
                            "event_type": event.event_type,
                            "callback": cb_name,
                        }) if tracing else None
                        __enter__ctx = span_ctx.__enter__() if span_ctx else None
                        start_cb = perf_counter()
                        # Call callback asynchronously if it's async
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                        self.metrics["subscriber_calls"] += 1
                        elapsed_ms = round((perf_counter() - start_cb) * 1000, 3)
                        logger.debug(json.dumps({
                            "msg": "subscriber_called",
                            "event_type": event.event_type,
                            "callback": cb_name,
                            "elapsed_ms": elapsed_ms,
                        }))
                        if span_ctx:
                            span_ctx.__exit__(None, None, None)
                    except Exception as e:
                        self.metrics["subscriber_failures"] += 1
                        logger.error(json.dumps({
                            "msg": "subscriber_failed",
                            "event_type": event.event_type,
                            "error": str(e),
                        }))
                        
        except Exception as e:
            logger.error(json.dumps({"msg": "notify_subscribers_failed", "error": str(e)}))
    
    def _save_events_to_file(self) -> None:
        """Save events to file for persistence"""
        try:
            events_data = []
            for event in self.event_history[-1000:]:  # Keep last 1000 events
                event_dict = asdict(event)
                event_dict['timestamp'] = event.timestamp.isoformat()
                events_data.append(event_dict)
            
            with open(self.event_file, 'w') as f:
                json.dump({
                    'events': events_data,
                    'last_updated': datetime.now().isoformat(),
                    'total_events': len(self.event_history)
                }, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save events to file: {e}")
    
    def _load_events_from_file(self) -> None:
        """Load events from file"""
        try:
            if self.event_file.exists():
                with open(self.event_file, 'r') as f:
                    data = json.load(f)
                    
                for event_data in data.get('events', []):
                    event = Event(
                        event_type=event_data['event_type'],
                        data=event_data['data'],
                        source_agent=event_data['source_agent'],
                        timestamp=datetime.fromisoformat(event_data['timestamp']),
                        event_id=event_data['event_id'],
                        correlation_id=event_data.get('correlation_id')
                    )
                    self.event_history.append(event)
                    
                logger.info(f"✅ Loaded {len(data.get('events', []))} events from file")
                
        except Exception as e:
            logger.error(f"❌ Failed to load events from file: {e}")
    
    async def start_redis_listener(self) -> None:
        """Start Redis listener for external events"""
        if not self.use_redis or not self.redis_client:
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to all BMAD event channels
            pubsub.psubscribe("bmad:events:*")
            
            logger.info("✅ Redis listener started")
            
            for message in pubsub.listen():
                if message['type'] == 'pmessage':
                    try:
                        event_data = json.loads(message['data'])
                        
                        # Create event object
                        event = Event(
                            event_type=event_data['event_type'],
                            data=event_data['data'],
                            source_agent=event_data['source_agent'],
                            timestamp=datetime.fromisoformat(event_data['timestamp']),
                            event_id=event_data['event_id'],
                            correlation_id=event_data.get('correlation_id')
                        )
                        
                        # Add to history and notify subscribers
                        self.event_history.append(event)
                        await self._notify_subscribers(event)
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to process Redis message: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Redis listener failed: {e}")

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Return a shallow copy of current metrics."""
        try:
            return json.loads(json.dumps(self.metrics))
        except Exception:
            return dict(self.metrics)

# Global message bus instance
_message_bus: Optional[MessageBus] = None

def get_message_bus() -> MessageBus:
    """Get global message bus instance"""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus

async def publish_event(event_type: str, data: Dict[str, Any], 
                       source_agent: str = "unknown",
                       correlation_id: Optional[str] = None) -> bool:
    """Convenience function to publish event"""
    # Derive correlation_id from tracing if not provided
    if correlation_id is None:
        try:
            trace_id = get_tracing_service().get_trace_id()
            if trace_id:
                correlation_id = trace_id
        except Exception:
            pass

    # Ensure correlation_id is reflected in payload for downstream consumers
    if correlation_id is not None and isinstance(data, dict) and 'correlation_id' not in data:
        data = {**data, 'correlation_id': correlation_id}

    # Validate payload against schema early
    validate_event_payload(event_type, data)
    return await get_message_bus().publish(event_type, data, source_agent, correlation_id)

async def subscribe_to_event(event_type: str, callback: Callable) -> bool:
    """Convenience function to subscribe to event"""
    return await get_message_bus().subscribe(event_type, callback) 