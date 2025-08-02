"""
Redis Integration Client

This module provides the Redis client for the Integration Service,
handling caching, session storage, and rate limiting.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

class CacheEntry(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: datetime
    accessed_at: Optional[datetime] = None

class RateLimitInfo(BaseModel):
    key: str
    current_count: int
    limit: int
    window_seconds: int
    reset_time: datetime
    remaining: int

class RedisClient:
    """Redis client for caching, session storage, and rate limiting."""
    
    def __init__(self, connection_string: str, pool_size: int = 10):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.client: Optional[redis.Redis] = None
        self._connection_params = self._parse_connection_string(connection_string)
        
    def _parse_connection_string(self, connection_string: str) -> Dict[str, str]:
        """Parse Redis connection string."""
        if connection_string.startswith("redis://"):
            # Simple parsing - in production use proper URL parsing
            parts = connection_string.replace("redis://", "").split("/")
            if len(parts) >= 2:
                host_port = parts[0].split(":")
                host = host_port[0]
                port = host_port[1] if len(host_port) > 1 else "6379"
                database = parts[1] if len(parts) > 1 else "0"
                
                return {
                    "host": host,
                    "port": port,
                    "database": database
                }
        return {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
        
    async def connect(self):
        """Create Redis connection pool."""
        try:
            self.client = redis.from_url(
                self.connection_string,
                max_connections=self.pool_size,
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
            logger.info(f"Redis connection established with pool size {self.pool_size}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
            
    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
            
    async def set_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache entry with optional TTL."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)
                
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
                
            logger.debug(f"Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to set cache {key}: {e}")
            return False
            
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache entry."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
                
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Failed to get cache {key}: {e}")
            return None
            
    async def delete_cache(self, key: str) -> bool:
        """Delete cache entry."""
        try:
            result = await self.client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete cache {key}: {e}")
            return False
            
    async def clear_cache_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                result = await self.client.delete(*keys)
                logger.info(f"Cleared {result} cache entries matching pattern: {pattern}")
                return result
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0
            
    async def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set session data with TTL."""
        try:
            session_data = {
                "data": data,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
            }
            await self.client.setex(session_id, ttl, json.dumps(session_data))
            logger.debug(f"Session set: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set session {session_id}: {e}")
            return False
            
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        try:
            session_data = await self.client.get(session_id)
            if session_data is None:
                return None
                
            session = json.loads(session_data)
            # Update accessed time
            session["accessed_at"] = datetime.now().isoformat()
            await self.client.setex(session_id, 3600, json.dumps(session))
            
            return session["data"]
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
            
    async def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        return await self.delete_cache(session_id)
        
    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> RateLimitInfo:
        """Check rate limit for a key."""
        try:
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=window_seconds)
            
            # Get current count
            count = await self.client.zcount(key, window_start.timestamp(), current_time.timestamp())
            
            # Add current request
            await self.client.zadd(key, {str(current_time.timestamp()): current_time.timestamp()})
            await self.client.expire(key, window_seconds)
            
            # Calculate remaining requests
            remaining = max(0, limit - count - 1)
            reset_time = current_time + timedelta(seconds=window_seconds)
            
            return RateLimitInfo(
                key=key,
                current_count=count + 1,
                limit=limit,
                window_seconds=window_seconds,
                reset_time=reset_time,
                remaining=remaining
            )
        except Exception as e:
            logger.error(f"Failed to check rate limit {key}: {e}")
            return RateLimitInfo(
                key=key,
                current_count=0,
                limit=limit,
                window_seconds=window_seconds,
                reset_time=datetime.now(),
                remaining=limit
            )
            
    async def get_rate_limit_status(self, key: str) -> Optional[RateLimitInfo]:
        """Get current rate limit status."""
        try:
            # Get all entries for the key
            entries = await self.client.zrange(key, 0, -1, withscores=True)
            if not entries:
                return None
                
            current_time = datetime.now()
            window_seconds = 3600  # Default 1 hour window
            
            # Count entries in current window
            count = len(entries)
            limit = 100  # Default limit
            
            # Calculate reset time (1 hour from oldest entry)
            oldest_timestamp = min(score for _, score in entries)
            reset_time = datetime.fromtimestamp(oldest_timestamp) + timedelta(seconds=window_seconds)
            
            return RateLimitInfo(
                key=key,
                current_count=count,
                limit=limit,
                window_seconds=window_seconds,
                reset_time=reset_time,
                remaining=max(0, limit - count)
            )
        except Exception as e:
            logger.error(f"Failed to get rate limit status {key}: {e}")
            return None
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            info = await self.client.info()
            
            # Get cache keys count
            keys_count = await self.client.dbsize()
            
            # Get memory usage
            memory_info = await self.client.info("memory")
            
            return {
                "keys_count": keys_count,
                "memory_used": memory_info.get("used_memory_human", "unknown"),
                "memory_peak": memory_info.get("used_memory_peak_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis service health."""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "connection_string": self.connection_string
                }
                
            # Test connection
            await self.client.ping()
            
            # Get stats
            stats = await self.get_cache_stats()
            
            return {
                "status": "healthy",
                "connection_string": self.connection_string,
                "pool_size": self.pool_size,
                "cache_stats": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_string": self.connection_string
            } 