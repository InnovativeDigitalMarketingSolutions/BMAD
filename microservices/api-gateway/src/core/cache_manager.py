"""
Cache Manager for API Gateway response caching.
"""

import asyncio
import logging
import time
import hashlib
import json
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as aioredis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CacheStrategy(str, Enum):
    """Cache strategies."""
    NONE = "none"
    RESPONSE = "response"
    PARTIAL = "partial"
    AGGRESSIVE = "aggressive"


@dataclass
class CacheEntry:
    """Cache entry data."""
    key: str
    value: bytes
    ttl: int
    created_at: float
    accessed_at: float
    access_count: int = 0


class CacheConfig(BaseModel):
    """Cache configuration."""
    redis_url: str = Field("redis://localhost:6379", description="Redis connection URL")
    default_ttl: int = Field(300, description="Default cache TTL in seconds")
    max_size: int = Field(1000, description="Maximum number of cache entries")
    enable_compression: bool = Field(False, description="Enable response compression")
    cache_strategy: CacheStrategy = Field(CacheStrategy.RESPONSE, description="Default cache strategy")
    enable_stats: bool = Field(True, description="Enable cache statistics")


class CacheManager:
    """Manages response caching for the API Gateway."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        self._initialized = False
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the cache manager."""
        try:
            # Connect to Redis
            self.redis = aioredis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=False  # Keep as bytes for binary data
            )
            
            # Test connection
            await self.redis.ping()
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
            
            self._initialized = True
            logger.info("Cache manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            raise
    
    def _generate_cache_key(self, method: str, path: str, query_params: Dict[str, str], headers: Dict[str, str]) -> str:
        """Generate cache key from request parameters."""
        # Create a hash of the request parameters
        key_data = {
            "method": method.upper(),
            "path": path,
            "query": sorted(query_params.items()),
            "headers": {k.lower(): v for k, v in headers.items() if k.lower() in ['accept', 'content-type']}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"gateway:cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def get(self, key: str) -> Optional[bytes]:
        """Get value from cache."""
        if not self._initialized or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                self.stats["hits"] += 1
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                self.stats["misses"] += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: bytes, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self._initialized or not self.redis:
            return False
        
        try:
            ttl = ttl or self.config.default_ttl
            await self.redis.setex(key, ttl, value)
            self.stats["sets"] += 1
            logger.debug(f"Cache set for key: {key} with TTL: {ttl}")
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._initialized or not self.redis:
            return False
        
        try:
            result = await self.redis.delete(key)
            if result > 0:
                self.stats["deletes"] += 1
                logger.debug(f"Cache delete for key: {key}")
            return result > 0
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._initialized or not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL for a key."""
        if not self._initialized or not self.redis:
            return -1
        
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL: {e}")
            return -1
    
    async def cache_response(
        self,
        method: str,
        path: str,
        query_params: Dict[str, str],
        headers: Dict[str, str],
        response_body: bytes,
        response_headers: Dict[str, str],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache a complete response."""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(method, path, query_params, headers)
            
            # Create cache entry
            cache_entry = {
                "body": response_body,
                "headers": response_headers,
                "cached_at": time.time()
            }
            
            # Serialize cache entry
            cache_data = json.dumps(cache_entry).encode()
            
            # Store in cache
            return await self.set(cache_key, cache_data, ttl)
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False
    
    async def get_cached_response(
        self,
        method: str,
        path: str,
        query_params: Dict[str, str],
        headers: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(method, path, query_params, headers)
            
            # Get from cache
            cache_data = await self.get(cache_key)
            if not cache_data:
                return None
            
            # Deserialize cache entry
            cache_entry = json.loads(cache_data.decode())
            
            # Check if cache is still valid
            cached_at = cache_entry.get("cached_at", 0)
            if time.time() - cached_at > (self.config.default_ttl or 300):
                await self.delete(cache_key)
                return None
            
            return cache_entry
            
        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        if not self._initialized or not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries matching pattern: {pattern}")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
            return 0
    
    async def invalidate_service(self, service_name: str) -> int:
        """Invalidate all cache entries for a service."""
        pattern = f"gateway:cache:*{service_name}*"
        return await self.invalidate_pattern(pattern)
    
    async def clear_all(self) -> bool:
        """Clear all cache entries."""
        if not self._initialized or not self.redis:
            return False
        
        try:
            keys = await self.redis.keys("gateway:cache:*")
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._initialized or not self.redis:
            return {"error": "Cache not initialized"}
        
        try:
            # Get Redis info
            info = await self.redis.info()
            
            # Calculate hit rate
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            # Get cache size
            cache_keys = await self.redis.keys("gateway:cache:*")
            
            return {
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "sets": self.stats["sets"],
                "deletes": self.stats["deletes"],
                "errors": self.stats["errors"],
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "cache_size": len(cache_keys),
                "redis_info": {
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_peak": info.get("used_memory_peak", 0),
                    "connected_clients": info.get("connected_clients", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries."""
        while True:
            try:
                # Redis automatically handles TTL, but we can do additional cleanup here
                # For example, remove entries that are too old
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def should_cache_response(self, method: str, status_code: int, headers: Dict[str, str]) -> bool:
        """Determine if response should be cached."""
        # Don't cache non-GET requests
        if method.upper() != "GET":
            return False
        
        # Don't cache error responses
        if status_code >= 400:
            return False
        
        # Check cache control headers
        cache_control = headers.get("cache-control", "").lower()
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        # Check if response is cacheable
        content_type = headers.get("content-type", "").lower()
        if "application/json" in content_type or "text/" in content_type:
            return True
        
        return False
    
    def get_cache_ttl(self, headers: Dict[str, str]) -> Optional[int]:
        """Get TTL from response headers."""
        # Check cache-control max-age
        cache_control = headers.get("cache-control", "")
        if "max-age=" in cache_control:
            try:
                max_age = cache_control.split("max-age=")[1].split(",")[0]
                return int(max_age)
            except (ValueError, IndexError):
                pass
        
        # Check expires header
        expires = headers.get("expires")
        if expires:
            try:
                from email.utils import parsedate_to_datetime
                import datetime
                expires_time = parsedate_to_datetime(expires)
                now = datetime.datetime.now(datetime.timezone.utc)
                ttl = int((expires_time - now).total_seconds())
                return max(0, ttl)
            except Exception:
                pass
        
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the cache manager."""
        try:
            if not self.redis:
                return {"status": "unhealthy", "error": "Redis not connected"}
            
            # Test Redis connection
            await self.redis.ping()
            
            # Get basic stats
            stats = await self.get_cache_stats()
            
            return {
                "status": "healthy",
                "redis_connected": True,
                "stats": stats
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis:
            await self.redis.close() 