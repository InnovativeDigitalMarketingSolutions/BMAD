"""
Context Store

This module provides persistent storage for contexts using PostgreSQL and Redis.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import asyncpg
import redis.asyncio as redis
from pydantic import BaseModel

from .context_manager import Context

logger = logging.getLogger(__name__)

class ContextStore:
    """Persistent storage for contexts using PostgreSQL and Redis."""
    
    def __init__(self, postgres_url: str, redis_url: str):
        self.postgres_url = postgres_url
        self.redis_url = redis_url
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Initialize database connections."""
        try:
            # PostgreSQL connection
            self.pg_pool = await asyncpg.create_pool(
                self.postgres_url,
                min_size=1,
                max_size=10
            )
            
            # Redis connection
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Create tables if they don't exist
            await self._create_tables()
            
            logger.info("Context store connections established")
            
        except Exception as e:
            logger.error(f"Failed to connect to context store: {e}")
            raise
            
    async def disconnect(self):
        """Close database connections."""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Context store connections closed")
        
    async def _create_tables(self):
        """Create database tables if they don't exist."""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(100) NOT NULL,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    size_mb DECIMAL(10,2) DEFAULT 0.0,
                    layer_count INTEGER DEFAULT 0,
                    access_count INTEGER DEFAULT 0,
                    metadata JSONB DEFAULT '{}',
                    tags TEXT[] DEFAULT '{}'
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS context_layers (
                    id VARCHAR(255) PRIMARY KEY,
                    context_id VARCHAR(255) REFERENCES contexts(id) ON DELETE CASCADE,
                    layer_type VARCHAR(100) NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(type);
                CREATE INDEX IF NOT EXISTS idx_contexts_status ON contexts(status);
                CREATE INDEX IF NOT EXISTS idx_contexts_updated_at ON contexts(updated_at);
                CREATE INDEX IF NOT EXISTS idx_context_layers_context_id ON context_layers(context_id);
            """)
            
    async def save_context(self, context: Context) -> bool:
        """Save context to database and cache."""
        try:
            # Save to PostgreSQL
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO contexts (id, name, type, status, created_at, updated_at, 
                                        size_mb, layer_count, access_count, metadata, tags)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        type = EXCLUDED.type,
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at,
                        size_mb = EXCLUDED.size_mb,
                        layer_count = EXCLUDED.layer_count,
                        access_count = EXCLUDED.access_count,
                        metadata = EXCLUDED.metadata,
                        tags = EXCLUDED.tags
                """, context.id, context.name, context.type, context.status,
                     context.created_at, context.updated_at, context.size_mb,
                     context.layer_count, context.access_count,
                     json.dumps(context.metadata), context.tags)
                
            # Cache in Redis
            cache_key = f"context:{context.id}"
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(context.dict())
            )
            
            logger.debug(f"Saved context: {context.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save context {context.id}: {e}")
            return False
            
    async def get_context(self, context_id: str) -> Optional[Context]:
        """Get context from cache or database."""
        try:
            # Try cache first
            cache_key = f"context:{context_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                context_data = json.loads(cached_data)
                return Context(**context_data)
                
            # Get from database
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, name, type, status, created_at, updated_at,
                           size_mb, layer_count, access_count, metadata, tags
                    FROM contexts WHERE id = $1
                """, context_id)
                
                if not row:
                    return None
                    
                # Convert to Context object
                context_data = dict(row)
                context_data['metadata'] = json.loads(context_data['metadata'])
                context = Context(**context_data)
                
                # Cache the result
                await self.redis_client.setex(
                    cache_key,
                    3600,
                    json.dumps(context.dict())
                )
                
                return context
                
        except Exception as e:
            logger.error(f"Failed to get context {context_id}: {e}")
            return None
            
    async def delete_context(self, context_id: str) -> bool:
        """Delete context from database and cache."""
        try:
            # Delete from database
            async with self.pg_pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM contexts WHERE id = $1",
                    context_id
                )
                
            # Remove from cache
            cache_key = f"context:{context_id}"
            await self.redis_client.delete(cache_key)
            
            success = result != "DELETE 0"
            if success:
                logger.debug(f"Deleted context: {context_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete context {context_id}: {e}")
            return False
            
    async def list_contexts(self, context_type: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          limit: int = 100) -> List[Context]:
        """List contexts from database."""
        try:
            query = """
                SELECT id, name, type, status, created_at, updated_at,
                       size_mb, layer_count, access_count, metadata, tags
                FROM contexts
            """
            params = []
            conditions = []
            
            if context_type:
                conditions.append("type = $1")
                params.append(context_type)
                
            if tags:
                tag_conditions = []
                for i, tag in enumerate(tags):
                    param_idx = len(params) + 1
                    tag_conditions.append(f"${param_idx} = ANY(tags)")
                    params.append(tag)
                conditions.append(f"({' OR '.join(tag_conditions)})")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY updated_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
            contexts = []
            for row in rows:
                context_data = dict(row)
                context_data['metadata'] = json.loads(context_data['metadata'])
                contexts.append(Context(**context_data))
                
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to list contexts: {e}")
            return []
            
    async def save_layer(self, context_id: str, layer_id: str, layer_type: str,
                        data: Dict[str, Any]) -> bool:
        """Save context layer."""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO context_layers (id, context_id, layer_type, data, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        layer_type = EXCLUDED.layer_type,
                        data = EXCLUDED.data,
                        updated_at = NOW()
                """, layer_id, context_id, layer_type, json.dumps(data))
                
            # Update context layer count
            await conn.execute("""
                UPDATE contexts 
                SET layer_count = (SELECT COUNT(*) FROM context_layers WHERE context_id = $1),
                    updated_at = NOW()
                WHERE id = $1
            """, context_id)
            
            # Invalidate cache
            cache_key = f"context:{context_id}"
            await self.redis_client.delete(cache_key)
            
            logger.debug(f"Saved layer: {layer_id} for context: {context_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save layer {layer_id}: {e}")
            return False
            
    async def get_layer(self, context_id: str, layer_id: str) -> Optional[Dict[str, Any]]:
        """Get context layer."""
        try:
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, context_id, layer_type, data, created_at, updated_at
                    FROM context_layers WHERE id = $1 AND context_id = $2
                """, layer_id, context_id)
                
                if not row:
                    return None
                    
                layer_data = dict(row)
                layer_data['data'] = json.loads(layer_data['data'])
                return layer_data
                
        except Exception as e:
            logger.error(f"Failed to get layer {layer_id}: {e}")
            return None
            
    async def delete_layer(self, context_id: str, layer_id: str) -> bool:
        """Delete context layer."""
        try:
            async with self.pg_pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM context_layers WHERE id = $1 AND context_id = $2
                """, layer_id, context_id)
                
                # Update context layer count
                await conn.execute("""
                    UPDATE contexts 
                    SET layer_count = (SELECT COUNT(*) FROM context_layers WHERE context_id = $1),
                        updated_at = NOW()
                    WHERE id = $1
                """, context_id)
                
            success = result != "DELETE 0"
            if success:
                # Invalidate cache
                cache_key = f"context:{context_id}"
                await self.redis_client.delete(cache_key)
                logger.debug(f"Deleted layer: {layer_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete layer {layer_id}: {e}")
            return False
            
    async def list_layers(self, context_id: str) -> List[Dict[str, Any]]:
        """List layers for a context."""
        try:
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, context_id, layer_type, data, created_at, updated_at
                    FROM context_layers WHERE context_id = $1
                    ORDER BY created_at ASC
                """, context_id)
                
            layers = []
            for row in rows:
                layer_data = dict(row)
                layer_data['data'] = json.loads(layer_data['data'])
                layers.append(layer_data)
                
            return layers
            
        except Exception as e:
            logger.error(f"Failed to list layers for context {context_id}: {e}")
            return []
            
    async def health_check(self) -> Dict[str, Any]:
        """Check store health."""
        try:
            # Test PostgreSQL
            async with self.pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                
            # Test Redis
            await self.redis_client.ping()
            
            return {
                "status": "healthy",
                "postgresql": "connected",
                "redis": "connected"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 