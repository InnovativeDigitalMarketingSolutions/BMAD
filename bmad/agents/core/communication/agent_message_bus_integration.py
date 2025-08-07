#!/usr/bin/env python3
"""
Agent Message Bus Integration Module
Provides a standardized way for agents to integrate with the Message Bus system
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from .message_bus import publish, subscribe, unsubscribe

logger = logging.getLogger(__name__)

class AgentMessageBusIntegration:
    """Integration class for agents to use the Message Bus system."""
    
    def __init__(self, agent_name: str, agent_instance: Any):
        """
        Initialize the Message Bus Integration for an agent.
        
        Args:
            agent_name: Name of the agent
            agent_instance: Instance of the agent class
        """
        self.agent_name = agent_name
        self.agent_instance = agent_instance
        self.event_handlers: Dict[str, Callable] = {}
        self.enabled = False
        
        logger.info(f"Agent Message Bus Integration initialized for {agent_name}")
    
    async def register_event_handler(self, event_type: str, handler: Callable) -> bool:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Async function to handle the event
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Create a wrapper to handle async/sync conversion
            def sync_wrapper(event_data):
                try:
                    # Run async handler in event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, create task
                        asyncio.create_task(handler(event_data))
                    else:
                        # If no loop running, run directly
                        asyncio.run(handler(event_data))
                except Exception as e:
                    logger.error(f"Error in event handler {event_type}: {e}")
            
            # Register with message bus
            subscribe(event_type, sync_wrapper)
            
            # Store handler reference
            self.event_handlers[event_type] = handler
            
            logger.info(f"Registered event handler for {event_type} in {self.agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register event handler for {event_type}: {e}")
            return False
    
    async def unregister_event_handler(self, event_type: str) -> bool:
        """
        Unregister an event handler for a specific event type.
        
        Args:
            event_type: Type of event to unregister
            
        Returns:
            bool: True if unregistration successful
        """
        try:
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
                unsubscribe(event_type, handler)
                del self.event_handlers[event_type]
                
                logger.info(f"Unregistered event handler for {event_type} in {self.agent_name}")
                return True
            else:
                logger.warning(f"No event handler registered for {event_type} in {self.agent_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to unregister event handler for {event_type}: {e}")
            return False
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Publish an event to the message bus.
        
        Args:
            event_type: Type of event to publish
            event_data: Data to include with the event
            
        Returns:
            bool: True if publish successful
        """
        try:
            # Add agent metadata to event
            enhanced_data = {
                "agent_name": self.agent_name,
                "timestamp": asyncio.get_event_loop().time(),
                **event_data
            }
            
            # Publish to message bus
            success = publish(event_type, enhanced_data)
            
            if success:
                logger.info(f"Published event {event_type} from {self.agent_name}")
            else:
                logger.error(f"Failed to publish event {event_type} from {self.agent_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            return False
    
    async def get_agent_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get events for this agent.
        
        Args:
            event_type: Optional event type filter
            
        Returns:
            List of events
        """
        try:
            from .message_bus import get_events
            events = get_events(event_type)
            
            # Filter events for this agent
            agent_events = [
                event for event in events 
                if event.get("data", {}).get("agent_name") == self.agent_name
            ]
            
            return agent_events
            
        except Exception as e:
            logger.error(f"Error getting events for {self.agent_name}: {e}")
            return []
    
    async def enable(self) -> bool:
        """Enable the Message Bus Integration."""
        try:
            self.enabled = True
            logger.info(f"Message Bus Integration enabled for {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable Message Bus Integration for {self.agent_name}: {e}")
            return False
    
    async def disable(self) -> bool:
        """Disable the Message Bus Integration."""
        try:
            # Unregister all event handlers
            for event_type in list(self.event_handlers.keys()):
                await self.unregister_event_handler(event_type)
            
            self.enabled = False
            logger.info(f"Message Bus Integration disabled for {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable Message Bus Integration for {self.agent_name}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the Message Bus Integration."""
        return {
            "agent_name": self.agent_name,
            "enabled": self.enabled,
            "registered_events": list(self.event_handlers.keys()),
            "handler_count": len(self.event_handlers)
        }

def create_agent_message_bus_integration(agent_name: str, agent_instance: Any) -> AgentMessageBusIntegration:
    """
    Factory function to create an Agent Message Bus Integration instance.
    
    Args:
        agent_name: Name of the agent
        agent_instance: Instance of the agent class
        
    Returns:
        AgentMessageBusIntegration instance
    """
    return AgentMessageBusIntegration(agent_name, agent_instance) 