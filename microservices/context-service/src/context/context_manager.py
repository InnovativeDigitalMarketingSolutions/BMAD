"""
Context Manager

This module provides the main context management functionality for the Context Service,
handling context creation, retrieval, updates, and lifecycle management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import json
import uuid
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class Context(BaseModel):
    """Context model for storing context information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    size_mb: float = 0.0
    layer_count: int = 0
    access_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class ContextManager:
    """Manages context lifecycle and operations."""
    
    def __init__(self, store=None):
        self.store = store
        self.contexts: Dict[str, Context] = {}
        
    async def create_context(self, name: str, context_type: str, 
                           metadata: Optional[Dict[str, Any]] = None,
                           tags: Optional[List[str]] = None) -> Context:
        """Create a new context."""
        try:
            context = Context(
                name=name,
                type=context_type,
                metadata=metadata or {},
                tags=tags or []
            )
            
            # Store context
            if self.store:
                await self.store.save_context(context)
            else:
                self.contexts[context.id] = context
                
            logger.info(f"Created context: {context.id} ({name})")
            return context
            
        except Exception as e:
            logger.error(f"Failed to create context: {e}")
            raise
            
    async def get_context(self, context_id: str) -> Optional[Context]:
        """Get context by ID."""
        try:
            if self.store:
                return await self.store.get_context(context_id)
            else:
                context = self.contexts.get(context_id)
                if context:
                    # Update access count
                    context.access_count += 1
                    context.updated_at = datetime.now(timezone.utc)
                return context
                
        except Exception as e:
            logger.error(f"Failed to get context {context_id}: {e}")
            return None
            
    async def update_context(self, context_id: str, 
                           updates: Dict[str, Any]) -> Optional[Context]:
        """Update context."""
        try:
            context = await self.get_context(context_id)
            if not context:
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                    
            context.updated_at = datetime.now(timezone.utc)
            
            # Store updated context
            if self.store:
                await self.store.save_context(context)
            else:
                self.contexts[context_id] = context
                
            logger.info(f"Updated context: {context_id}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to update context {context_id}: {e}")
            return None
            
    async def delete_context(self, context_id: str) -> bool:
        """Delete context."""
        try:
            if self.store:
                success = await self.store.delete_context(context_id)
            else:
                success = context_id in self.contexts
                if success:
                    del self.contexts[context_id]
                    
            if success:
                logger.info(f"Deleted context: {context_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete context {context_id}: {e}")
            return False
            
    async def list_contexts(self, context_type: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          limit: int = 100) -> List[Context]:
        """List contexts with optional filtering."""
        try:
            if self.store:
                contexts = await self.store.list_contexts()
            else:
                contexts = list(self.contexts.values())
                
            # Apply filters
            if context_type:
                contexts = [c for c in contexts if c.type == context_type]
                
            if tags:
                contexts = [c for c in contexts if any(tag in c.tags for tag in tags)]
                
            # Sort by updated_at descending and limit
            contexts.sort(key=lambda x: x.updated_at, reverse=True)
            return contexts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to list contexts: {e}")
            return []
            
    async def search_contexts(self, query: str, 
                            context_type: Optional[str] = None) -> List[Context]:
        """Search contexts by name or metadata."""
        try:
            contexts = await self.list_contexts(context_type=context_type)
            
            # Simple text search
            query_lower = query.lower()
            results = []
            
            for context in contexts:
                # Search in name
                if query_lower in context.name.lower():
                    results.append(context)
                    continue
                    
                # Search in metadata
                for key, value in context.metadata.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        results.append(context)
                        break
                        
                # Search in tags
                for tag in context.tags:
                    if query_lower in tag.lower():
                        results.append(context)
                        break
                        
            return results
            
        except Exception as e:
            logger.error(f"Failed to search contexts: {e}")
            return []
            
    async def get_context_stats(self) -> Dict[str, Any]:
        """Get context statistics."""
        try:
            contexts = await self.list_contexts()
            
            if not contexts:
                return {
                    "total_contexts": 0,
                    "total_size_mb": 0.0,
                    "context_types": {},
                    "status_distribution": {}
                }
                
            total_size = sum(c.size_mb for c in contexts)
            
            # Count by type
            type_counts = {}
            for context in contexts:
                type_counts[context.type] = type_counts.get(context.type, 0) + 1
                
            # Count by status
            status_counts = {}
            for context in contexts:
                status_counts[context.status] = status_counts.get(context.status, 0) + 1
                
            return {
                "total_contexts": len(contexts),
                "total_size_mb": total_size,
                "context_types": type_counts,
                "status_distribution": status_counts,
                "average_size_mb": total_size / len(contexts) if contexts else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get context stats: {e}")
            return {"error": str(e)}
            
    async def cleanup_expired_contexts(self, max_age_hours: int = 24) -> int:
        """Clean up expired contexts."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            contexts = await self.list_contexts()
            
            expired_count = 0
            for context in contexts:
                if context.updated_at < cutoff_time and context.status == "inactive":
                    await self.delete_context(context.id)
                    expired_count += 1
                    
            logger.info(f"Cleaned up {expired_count} expired contexts")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired contexts: {e}")
            return 0
            
    async def health_check(self) -> Dict[str, Any]:
        """Check context manager health."""
        try:
            stats = await self.get_context_stats()
            
            return {
                "status": "healthy",
                "total_contexts": stats.get("total_contexts", 0),
                "total_size_mb": stats.get("total_size_mb", 0.0),
                "store_available": self.store is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "store_available": self.store is not None
            } 