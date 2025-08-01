"""
Enhanced Context Management Module

This module provides advanced context management capabilities including:
- Context layering (session, user, global, workflow)
- Context persistence and retrieval
- Context sharing between agents
- Context versioning and analytics
- Context optimization

Follows clean code principles and BMAD development quality guide.
"""

import json
import logging
import threading
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
CONTEXT_STORAGE_PATH = Path(__file__).parent.parent / "context_storage"
CONTEXT_STORAGE_PATH.mkdir(exist_ok=True)

# Thread safety
CONTEXT_LOCK = threading.Lock()


class ContextLayer(Enum):
    """Enumeration of context layers with priority levels."""
    GLOBAL = 1      # System-wide context (lowest priority)
    WORKFLOW = 2    # Workflow-specific context
    USER = 3        # User-specific context
    SESSION = 4     # Session-specific context (highest priority)


class ContextType(Enum):
    """Enumeration of context types."""
    CONFIGURATION = "configuration"
    STATE = "state"
    MEMORY = "memory"
    PREFERENCES = "preferences"
    ANALYTICS = "analytics"
    WORKFLOW = "workflow"


@dataclass
class ContextEntry:
    """Data class for context entries with metadata."""
    id: str
    layer: ContextLayer
    context_type: ContextType
    key: str
    value: Any
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['layer'] = self.layer.value
        data['context_type'] = self.context_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextEntry':
        """Create from dictionary for deserialization."""
        data['layer'] = ContextLayer(data['layer'])
        data['context_type'] = ContextType(data['context_type'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)


class ContextLayerManager:
    """Manages context layers with priority-based resolution."""
    
    def __init__(self):
        self._layers: Dict[ContextLayer, Dict[str, ContextEntry]] = {
            layer: {} for layer in ContextLayer
        }
        self._subscribers: Dict[str, List[callable]] = {}
        self._analytics: Dict[str, Any] = {}
    
    def set_context(
        self,
        key: str,
        value: Any,
        layer: ContextLayer = ContextLayer.SESSION,
        context_type: ContextType = ContextType.STATE,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> str:
        """
        Set context value in specified layer.
        
        Args:
            key: Context key
            value: Context value
            layer: Context layer (default: SESSION)
            context_type: Type of context
            metadata: Additional metadata
            ttl_seconds: Time to live in seconds
            
        Returns:
            Context entry ID
        """
        with CONTEXT_LOCK:
            entry_id = str(uuid.uuid4())
            now = datetime.now()
            
            expires_at = None
            if ttl_seconds:
                expires_at = now + timedelta(seconds=ttl_seconds)
            
            entry = ContextEntry(
                id=entry_id,
                layer=layer,
                context_type=context_type,
                key=key,
                value=value,
                metadata=metadata or {},
                created_at=now,
                updated_at=now,
                expires_at=expires_at
            )
            
            self._layers[layer][key] = entry
            
            # Update analytics
            self._update_analytics('set', layer, context_type)
            
            # Notify subscribers
            self._notify_subscribers('context_set', entry)
            
            logger.info(f"[ContextLayerManager] Set context '{key}' in layer {layer.name}")
            return entry_id
    
    def get_context(
        self,
        key: str,
        layer: Optional[ContextLayer] = None,
        include_expired: bool = False
    ) -> Optional[Any]:
        """
        Get context value with layer resolution.
        
        Args:
            key: Context key
            layer: Specific layer to check (None for all layers)
            include_expired: Whether to include expired entries
            
        Returns:
            Context value or None if not found
        """
        with CONTEXT_LOCK:
            if layer:
                # Check specific layer
                entry = self._layers[layer].get(key)
                if entry and (include_expired or not self._is_expired(entry)):
                    self._update_analytics('get', layer, entry.context_type)
                    return entry.value
            else:
                # Check all layers in priority order (highest to lowest)
                for layer_enum in reversed(list(ContextLayer)):
                    entry = self._layers[layer_enum].get(key)
                    if entry and (include_expired or not self._is_expired(entry)):
                        self._update_analytics('get', layer_enum, entry.context_type)
                        return entry.value
            
            return None
    
    def get_context_entry(
        self,
        key: str,
        layer: Optional[ContextLayer] = None,
        include_expired: bool = False
    ) -> Optional[ContextEntry]:
        """
        Get full context entry with metadata.
        
        Args:
            key: Context key
            layer: Specific layer to check (None for all layers)
            include_expired: Whether to include expired entries
            
        Returns:
            ContextEntry or None if not found
        """
        with CONTEXT_LOCK:
            if layer:
                entry = self._layers[layer].get(key)
                if entry and (include_expired or not self._is_expired(entry)):
                    return entry
            else:
                for layer_enum in reversed(list(ContextLayer)):
                    entry = self._layers[layer_enum].get(key)
                    if entry and (include_expired or not self._is_expired(entry)):
                        return entry
            
            return None
    
    def update_context(
        self,
        key: str,
        value: Any,
        layer: Optional[ContextLayer] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update existing context value.
        
        Args:
            key: Context key
            value: New value
            layer: Specific layer to update (None for highest priority)
            metadata: Additional metadata
            
        Returns:
            True if updated, False if not found
        """
        with CONTEXT_LOCK:
            # Direct entry lookup to avoid recursive lock
            entry = None
            if layer:
                entry = self._layers[layer].get(key)
                if entry and self._is_expired(entry):
                    entry = None
            else:
                # Check all layers in priority order (highest to lowest)
                for layer_enum in reversed(list(ContextLayer)):
                    entry = self._layers[layer_enum].get(key)
                    if entry and not self._is_expired(entry):
                        break
                    entry = None
            
            if entry:
                entry.value = value
                entry.updated_at = datetime.now()
                entry.version += 1
                if metadata:
                    entry.metadata.update(metadata)
                
                self._update_analytics('update', entry.layer, entry.context_type)
                self._notify_subscribers('context_updated', entry)
                
                logger.info(f"[ContextLayerManager] Updated context '{key}' in layer {entry.layer.name}")
                return True
            
            return False
    
    def delete_context(
        self,
        key: str,
        layer: Optional[ContextLayer] = None
    ) -> bool:
        """
        Delete context entry.
        
        Args:
            key: Context key
            layer: Specific layer to delete from (None for all layers)
            
        Returns:
            True if deleted, False if not found
        """
        with CONTEXT_LOCK:
            if layer:
                # Delete from specific layer
                if key in self._layers[layer]:
                    entry = self._layers[layer][key]  # Get entry before popping
                    self._update_analytics('delete', layer, entry.context_type)
                    self._notify_subscribers('context_deleted', entry)
                    del self._layers[layer][key]  # Use del instead of pop
                    logger.info(f"[ContextLayerManager] Deleted context '{key}' from layer {layer.name}")
                    return True
            else:
                # Delete from all layers
                deleted = False
                for layer_enum in ContextLayer:
                    if key in self._layers[layer_enum]:
                        entry = self._layers[layer_enum][key]  # Get entry before popping
                        self._update_analytics('delete', layer_enum, entry.context_type)
                        self._notify_subscribers('context_deleted', entry)
                        del self._layers[layer_enum][key]  # Use del instead of pop
                        deleted = True
                        logger.info(f"[ContextLayerManager] Deleted context '{key}' from layer {layer_enum.name}")
                return deleted
            
            return False
    
    def clear_layer(self, layer: ContextLayer) -> int:
        """
        Clear all entries from a specific layer.
        
        Args:
            layer: Layer to clear
            
        Returns:
            Number of entries cleared
        """
        with CONTEXT_LOCK:
            count = len(self._layers[layer])
            self._layers[layer].clear()
            logger.info(f"[ContextLayerManager] Cleared {count} entries from layer {layer.name}")
            return count
    
    def get_layer_contexts(
        self,
        layer: ContextLayer,
        context_type: Optional[ContextType] = None,
        include_expired: bool = False
    ) -> Dict[str, Any]:
        """
        Get all contexts from a specific layer.
        
        Args:
            layer: Layer to get contexts from
            context_type: Filter by context type
            include_expired: Whether to include expired entries
            
        Returns:
            Dictionary of key-value pairs
        """
        with CONTEXT_LOCK:
            contexts = {}
            for key, entry in self._layers[layer].items():
                if context_type and entry.context_type != context_type:
                    continue
                if not include_expired and self._is_expired(entry):
                    continue
                contexts[key] = entry.value
            
            return contexts
    
    def get_context_analytics(self) -> Dict[str, Any]:
        """Get context usage analytics."""
        with CONTEXT_LOCK:
            return self._analytics.copy()
    
    def subscribe(self, event_type: str, callback: callable) -> None:
        """Subscribe to context events."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"[ContextLayerManager] Subscriber added for event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: callable) -> None:
        """Unsubscribe from context events."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.info(f"[ContextLayerManager] Subscriber removed for event: {event_type}")
    
    def _is_expired(self, entry: ContextEntry) -> bool:
        """Check if context entry is expired."""
        if entry.expires_at:
            return datetime.now() > entry.expires_at
        return False
    
    def _update_analytics(self, operation: str, layer: ContextLayer, context_type: ContextType) -> None:
        """Update analytics data."""
        if 'operations' not in self._analytics:
            self._analytics['operations'] = {}
        
        op_key = f"{operation}_{layer.name}_{context_type.value}"
        self._analytics['operations'][op_key] = self._analytics['operations'].get(op_key, 0) + 1
        
        # Update layer statistics
        if 'layers' not in self._analytics:
            self._analytics['layers'] = {}
        if layer.name not in self._analytics['layers']:
            self._analytics['layers'][layer.name] = {
                'total_entries': 0,
                'context_types': {}
            }
        
        self._analytics['layers'][layer.name]['total_entries'] = len(self._layers[layer])
        
        if context_type.value not in self._analytics['layers'][layer.name]['context_types']:
            self._analytics['layers'][layer.name]['context_types'][context_type.value] = 0
        self._analytics['layers'][layer.name]['context_types'][context_type.value] += 1
    
    def _notify_subscribers(self, event_type: str, entry: ContextEntry) -> None:
        """Notify subscribers of context events."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(entry)
                except Exception as e:
                    logger.error(f"[ContextLayerManager] Error in subscriber callback: {e}")


class EnhancedContextManager:
    """Enhanced context manager with layering, persistence, and analytics."""
    
    def __init__(self, disable_cleanup: bool = False):
        self.layer_manager = ContextLayerManager()
        self._persistence_enabled = True
        self._auto_cleanup_enabled = True and not disable_cleanup
        self._cleanup_interval = 300  # 5 minutes
        
        # Load persisted contexts
        if self._persistence_enabled:
            self._load_persisted_contexts()
        
        # Start cleanup thread if enabled
        if self._auto_cleanup_enabled:
            self._start_cleanup_thread()
    
    def set_context(
        self,
        key: str,
        value: Any,
        layer: ContextLayer = ContextLayer.SESSION,
        context_type: ContextType = ContextType.STATE,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
        persist: bool = True
    ) -> str:
        """
        Set context with enhanced features.
        
        Args:
            key: Context key
            value: Context value
            layer: Context layer
            context_type: Type of context
            metadata: Additional metadata
            ttl_seconds: Time to live in seconds
            persist: Whether to persist to storage
            
        Returns:
            Context entry ID
        """
        entry_id = self.layer_manager.set_context(
            key, value, layer, context_type, metadata, ttl_seconds
        )
        
        if persist and self._persistence_enabled:
            self._persist_context(entry_id)
        
        return entry_id
    
    def get_context(
        self,
        key: str,
        layer: Optional[ContextLayer] = None,
        include_expired: bool = False
    ) -> Optional[Any]:
        """Get context value with layer resolution."""
        return self.layer_manager.get_context(key, layer, include_expired)
    
    def get_context_entry(
        self,
        key: str,
        layer: Optional[ContextLayer] = None,
        include_expired: bool = False
    ) -> Optional[ContextEntry]:
        """Get full context entry with metadata."""
        return self.layer_manager.get_context_entry(key, layer, include_expired)
    
    def update_context(
        self,
        key: str,
        value: Any,
        layer: Optional[ContextLayer] = None,
        metadata: Optional[Dict[str, Any]] = None,
        persist: bool = True
    ) -> bool:
        """Update existing context value."""
        success = self.layer_manager.update_context(key, value, layer, metadata)
        
        if success and persist and self._persistence_enabled:
            entry = self.layer_manager.get_context_entry(key, layer)
            if entry:
                self._persist_context(entry.id)
        
        return success
    
    def delete_context(
        self,
        key: str,
        layer: Optional[ContextLayer] = None,
        persist: bool = True
    ) -> bool:
        """Delete context entry."""
        entry = self.layer_manager.get_context_entry(key, layer)
        success = self.layer_manager.delete_context(key, layer)
        
        if success and persist and self._persistence_enabled and entry:
            self._remove_persisted_context(entry.id)
        
        return success
    
    def get_layer_contexts(
        self,
        layer: ContextLayer,
        context_type: Optional[ContextType] = None,
        include_expired: bool = False
    ) -> Dict[str, Any]:
        """Get all contexts from a specific layer."""
        return self.layer_manager.get_layer_contexts(layer, context_type, include_expired)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive context analytics."""
        analytics = self.layer_manager.get_context_analytics()
        analytics['manager_info'] = {
            'persistence_enabled': self._persistence_enabled,
            'auto_cleanup_enabled': self._auto_cleanup_enabled,
            'cleanup_interval': self._cleanup_interval
        }
        return analytics
    
    def subscribe(self, event_type: str, callback: callable) -> None:
        """Subscribe to context events."""
        self.layer_manager.subscribe(event_type, callback)
    
    def unsubscribe(self, event_type: str, callback: callable) -> None:
        """Unsubscribe from context events."""
        self.layer_manager.unsubscribe(event_type, callback)
    
    def _persist_context(self, entry_id: str) -> None:
        """Persist context entry to storage."""
        try:
            entry = None
            for layer in ContextLayer:
                for key, context_entry in self.layer_manager._layers[layer].items():
                    if context_entry.id == entry_id:
                        entry = context_entry
                        break
                if entry:
                    break
            
            if entry:
                file_path = CONTEXT_STORAGE_PATH / f"{entry_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(entry.to_dict(), f, indent=2, default=str)
                
                logger.debug(f"[EnhancedContextManager] Persisted context {entry_id}")
        except Exception as e:
            logger.error(f"[EnhancedContextManager] Error persisting context {entry_id}: {e}")
    
    def _remove_persisted_context(self, entry_id: str) -> None:
        """Remove persisted context entry."""
        try:
            file_path = CONTEXT_STORAGE_PATH / f"{entry_id}.json"
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"[EnhancedContextManager] Removed persisted context {entry_id}")
        except Exception as e:
            logger.error(f"[EnhancedContextManager] Error removing persisted context {entry_id}: {e}")
    
    def _load_persisted_contexts(self) -> None:
        """Load persisted contexts from storage."""
        try:
            for file_path in CONTEXT_STORAGE_PATH.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    entry = ContextEntry.from_dict(data)
                    
                    # Only load if not expired
                    if not self.layer_manager._is_expired(entry):
                        self.layer_manager._layers[entry.layer][entry.key] = entry
                        logger.debug(f"[EnhancedContextManager] Loaded persisted context {entry.id}")
                    else:
                        # Remove expired persisted context
                        file_path.unlink()
                        logger.debug(f"[EnhancedContextManager] Removed expired persisted context {entry.id}")
                        
                except Exception as e:
                    logger.error(f"[EnhancedContextManager] Error loading persisted context {file_path}: {e}")
            
            logger.info(f"[EnhancedContextManager] Loaded persisted contexts from {CONTEXT_STORAGE_PATH}")
        except Exception as e:
            logger.error(f"[EnhancedContextManager] Error loading persisted contexts: {e}")
    
    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""
        def cleanup_worker():
            while self._auto_cleanup_enabled:
                try:
                    self._cleanup_expired_contexts()
                    threading.Event().wait(self._cleanup_interval)
                except Exception as e:
                    logger.error(f"[EnhancedContextManager] Error in cleanup worker: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("[EnhancedContextManager] Started cleanup thread")
    
    def _cleanup_expired_contexts(self) -> None:
        """Clean up expired context entries."""
        with CONTEXT_LOCK:
            total_cleaned = 0
            for layer in ContextLayer:
                expired_keys = []
                for key, entry in self.layer_manager._layers[layer].items():
                    if self.layer_manager._is_expired(entry):
                        expired_keys.append(key)
                        if self._persistence_enabled:
                            self._remove_persisted_context(entry.id)
                
                for key in expired_keys:
                    del self.layer_manager._layers[layer][key]
                    total_cleaned += 1
            
            if total_cleaned > 0:
                logger.info(f"[EnhancedContextManager] Cleaned up {total_cleaned} expired contexts")


# Global instance for easy access
enhanced_context_manager = EnhancedContextManager() 