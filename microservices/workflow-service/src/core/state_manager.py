"""
State Manager

This module provides state management functionality for workflows,
handling workflow state persistence, transitions, and recovery.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone, timedelta
import json
import uuid
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class StateType(str, Enum):
    """State type enumeration."""
    WORKFLOW = "workflow"
    STEP = "step"
    EXECUTION = "execution"

class StateStatus(str, Enum):
    """State status enumeration."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"

class WorkflowState(BaseModel):
    """Workflow state model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    execution_id: Optional[str] = None
    state_type: StateType
    status: StateStatus = StateStatus.INITIALIZED
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class StateManager:
    """Manages workflow state and transitions."""
    
    def __init__(self, store=None):
        self.store = store
        self.states: Dict[str, WorkflowState] = {}
        self.state_locks: Dict[str, asyncio.Lock] = {}
        
    async def create_state(self, workflow_id: str, state_type: StateType,
                          execution_id: Optional[str] = None,
                          initial_data: Optional[Dict[str, Any]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """Create a new workflow state."""
        try:
            state = WorkflowState(
                workflow_id=workflow_id,
                execution_id=execution_id,
                state_type=state_type,
                data=initial_data or {},
                metadata=metadata or {}
            )
            
            # Store state
            if self.store:
                await self.store.save_state(state)
            else:
                self.states[state.id] = state
                
            # Create lock for this state
            self.state_locks[state.id] = asyncio.Lock()
                
            logger.info(f"Created state: {state.id} for workflow: {workflow_id}")
            return state
            
        except Exception as e:
            logger.error(f"Failed to create state: {e}")
            raise
            
    async def get_state(self, state_id: str) -> Optional[WorkflowState]:
        """Get state by ID."""
        try:
            if self.store:
                return await self.store.get_state(state_id)
            else:
                return self.states.get(state_id)
                
        except Exception as e:
            logger.error(f"Failed to get state {state_id}: {e}")
            return None
            
    async def get_workflow_state(self, workflow_id: str, state_type: Optional[StateType] = None) -> Optional[WorkflowState]:
        """Get current state for a workflow."""
        try:
            if self.store:
                states = await self.store.list_states(workflow_id=workflow_id, state_type=state_type)
            else:
                states = [s for s in self.states.values() if s.workflow_id == workflow_id]
                if state_type:
                    states = [s for s in states if s.state_type == state_type]
                    
            if not states:
                return None
                
            # Return the most recent state
            states.sort(key=lambda x: x.updated_at, reverse=True)
            return states[0]
            
        except Exception as e:
            logger.error(f"Failed to get workflow state {workflow_id}: {e}")
            return None
            
    async def update_state(self, state_id: str, updates: Dict[str, Any]) -> Optional[WorkflowState]:
        """Update state with thread-safe locking."""
        try:
            # Get or create lock for this state
            lock = self.state_locks.get(state_id)
            if not lock:
                lock = asyncio.Lock()
                self.state_locks[state_id] = lock
                
            async with lock:
                state = await self.get_state(state_id)
                if not state:
                    return None
                    
                # Update fields
                for key, value in updates.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
                        
                state.updated_at = datetime.now(timezone.utc)
                
                # Store updated state
                if self.store:
                    await self.store.save_state(state)
                else:
                    self.states[state_id] = state
                    
                logger.debug(f"Updated state: {state_id}")
                return state
                
        except Exception as e:
            logger.error(f"Failed to update state {state_id}: {e}")
            return None
            
    async def transition_state(self, state_id: str, new_status: StateStatus,
                             data_updates: Optional[Dict[str, Any]] = None,
                             metadata_updates: Optional[Dict[str, Any]] = None) -> Optional[WorkflowState]:
        """Transition state to a new status with data updates."""
        try:
            updates = {"status": new_status}
            
            if data_updates:
                updates["data"] = data_updates
                
            if metadata_updates:
                updates["metadata"] = metadata_updates
                
            return await self.update_state(state_id, updates)
            
        except Exception as e:
            logger.error(f"Failed to transition state {state_id}: {e}")
            return None
            
    async def add_state_data(self, state_id: str, key: str, value: Any) -> bool:
        """Add data to state."""
        try:
            state = await self.get_state(state_id)
            if not state:
                return False
                
            state.data[key] = value
            state.updated_at = datetime.now(timezone.utc)
            
            # Store updated state
            if self.store:
                await self.store.save_state(state)
            else:
                self.states[state_id] = state
                
            logger.debug(f"Added data to state {state_id}: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add data to state {state_id}: {e}")
            return False
            
    async def get_state_data(self, state_id: str, key: str, default: Any = None) -> Any:
        """Get data from state."""
        try:
            state = await self.get_state(state_id)
            if not state:
                return default
                
            return state.data.get(key, default)
            
        except Exception as e:
            logger.error(f"Failed to get data from state {state_id}: {e}")
            return default
            
    async def remove_state_data(self, state_id: str, key: str) -> bool:
        """Remove data from state."""
        try:
            state = await self.get_state(state_id)
            if not state:
                return False
                
            if key in state.data:
                del state.data[key]
                state.updated_at = datetime.now(timezone.utc)
                
                # Store updated state
                if self.store:
                    await self.store.save_state(state)
                else:
                    self.states[state_id] = state
                    
                logger.debug(f"Removed data from state {state_id}: {key}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove data from state {state_id}: {e}")
            return False
            
    async def list_states(self, workflow_id: Optional[str] = None,
                         state_type: Optional[StateType] = None,
                         status: Optional[StateStatus] = None,
                         limit: int = 100) -> List[WorkflowState]:
        """List states with optional filtering."""
        try:
            if self.store:
                states = await self.store.list_states(workflow_id, state_type, status, limit)
            else:
                states = list(self.states.values())
                
                # Apply filters
                if workflow_id:
                    states = [s for s in states if s.workflow_id == workflow_id]
                    
                if state_type:
                    states = [s for s in states if s.state_type == state_type]
                    
                if status:
                    states = [s for s in states if s.status == status]
                    
                # Sort by updated_at descending and limit
                states.sort(key=lambda x: x.updated_at, reverse=True)
                states = states[:limit]
                
            return states
            
        except Exception as e:
            logger.error(f"Failed to list states: {e}")
            return []
            
    async def delete_state(self, state_id: str) -> bool:
        """Delete state."""
        try:
            if self.store:
                success = await self.store.delete_state(state_id)
            else:
                success = state_id in self.states
                if success:
                    del self.states[state_id]
                    
            # Remove lock
            if state_id in self.state_locks:
                del self.state_locks[state_id]
                
            if success:
                logger.info(f"Deleted state: {state_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete state {state_id}: {e}")
            return False
            
    async def cleanup_expired_states(self, max_age_hours: int = 24) -> int:
        """Clean up expired states."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            states = await self.list_states()
            
            expired_count = 0
            for state in states:
                if state.expires_at and state.expires_at < cutoff_time:
                    await self.delete_state(state.id)
                    expired_count += 1
                    
            logger.info(f"Cleaned up {expired_count} expired states")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired states: {e}")
            return 0
            
    async def create_checkpoint(self, workflow_id: str, execution_id: str,
                              checkpoint_data: Dict[str, Any]) -> str:
        """Create a checkpoint for workflow recovery."""
        try:
            checkpoint_id = f"checkpoint_{workflow_id}_{execution_id}_{int(datetime.now(timezone.utc).timestamp())}"
            
            state = await self.create_state(
                workflow_id=workflow_id,
                state_type=StateType.EXECUTION,
                execution_id=execution_id,
                initial_data=checkpoint_data,
                metadata={"checkpoint_id": checkpoint_id, "type": "checkpoint"}
            )
            
            logger.info(f"Created checkpoint: {checkpoint_id} for workflow: {workflow_id}")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            raise
            
    async def restore_checkpoint(self, workflow_id: str, execution_id: str,
                               checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore workflow state from checkpoint."""
        try:
            states = await self.list_states(
                workflow_id=workflow_id,
                state_type=StateType.EXECUTION
            )
            
            # Find the checkpoint
            checkpoint_state = None
            for state in states:
                if (state.execution_id == execution_id and 
                    state.metadata.get("checkpoint_id") == checkpoint_id):
                    checkpoint_state = state
                    break
                    
            if not checkpoint_state:
                logger.warning(f"Checkpoint not found: {checkpoint_id}")
                return None
                
            logger.info(f"Restored checkpoint: {checkpoint_id} for workflow: {workflow_id}")
            return checkpoint_state.data
            
        except Exception as e:
            logger.error(f"Failed to restore checkpoint: {e}")
            return None
            
    async def get_state_history(self, workflow_id: str, limit: int = 50) -> List[WorkflowState]:
        """Get state history for a workflow."""
        try:
            states = await self.list_states(workflow_id=workflow_id, limit=limit)
            return states
            
        except Exception as e:
            logger.error(f"Failed to get state history for workflow {workflow_id}: {e}")
            return []
            
    async def get_state_stats(self) -> Dict[str, Any]:
        """Get state statistics."""
        try:
            states = await self.list_states()
            
            if not states:
                return {
                    "total_states": 0,
                    "state_types": {},
                    "status_distribution": {}
                }
                
            # Count by type
            type_counts = {}
            for state in states:
                type_counts[state.state_type] = type_counts.get(state.state_type, 0) + 1
                
            # Count by status
            status_counts = {}
            for state in states:
                status_counts[state.status] = status_counts.get(state.status, 0) + 1
                
            return {
                "total_states": len(states),
                "state_types": type_counts,
                "status_distribution": status_counts,
                "active_locks": len(self.state_locks)
            }
            
        except Exception as e:
            logger.error(f"Failed to get state stats: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Check state manager health."""
        try:
            stats = await self.get_state_stats()
            
            return {
                "status": "healthy",
                "total_states": stats.get("total_states", 0),
                "active_locks": stats.get("active_locks", 0),
                "store_available": self.store is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "store_available": self.store is not None
            } 