"""
Redis Integration Client

Provides comprehensive Redis integration for BMAD including:
- Connection management with connection pooling
- Cache invalidation strategies
- Session storage
- Rate limiting
- Performance monitoring
- Failover handling
"""

import os
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from contextlib import contextmanager
try:
    import redis
    from redis import Redis, ConnectionPool, Sentinel
    from redis.exceptions import RedisError, ConnectionError, TimeoutError
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    Redis = None
    ConnectionPool = None
    Sentinel = None
    RedisError = None
    ConnectionError = None
    TimeoutError = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class RedisConfig:
    """Redis configuration settings."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    ssl_cert_reqs: Optional[str] = None
    max_connections: int = 20
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    decode_responses: bool = True
    use_sentinel: bool = False
    sentinel_hosts: Optional[List[str]] = None
    sentinel_password: Optional[str] = None
    sentinel_service_name: str = "mymaster"

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    access_count: int = 0

@dataclass
class RateLimitInfo:
    """Rate limiting information."""
    key: str
    limit: int
    window: int
    current_count: int
    reset_time: datetime
    blocked: bool = False

@dataclass
class RedisMetrics:
    """Redis performance metrics."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_response_time: float = 0.0
    last_operation_time: Optional[datetime] = None
    connection_errors: int = 0
    timeout_errors: int = 0

class RedisClient:
    """Comprehensive Redis client with enterprise features."""
    
    def __init__(self, config: RedisConfig):
        if not REDIS_AVAILABLE:
            raise ImportError("redis is required for Redis integration. Install with: pip install redis")
        
        self.config = config
        self.client = None
        self.pool = None
        self.sentinel = None
        self.metrics = RedisMetrics()
        self._initialize_connection()
        logger.info(f"Redis client initialized for {config.host}:{config.port}")
    
    def _initialize_connection(self):
        """Initialize Redis connection with failover support."""
        try:
            if self.config.use_sentinel and self.config.sentinel_hosts:
                # Use Redis Sentinel for high availability
                self.sentinel = Sentinel(
                    self.config.sentinel_hosts,
                    password=self.config.sentinel_password,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    retry_on_timeout=self.config.retry_on_timeout,
                    decode_responses=self.config.decode_responses
                )
                self.client = self.sentinel.master_for(
                    self.config.sentinel_service_name,
                    db=self.config.db,
                    password=self.config.password,
                    ssl=self.config.ssl,
                    ssl_cert_reqs=self.config.ssl_cert_reqs
                )
                logger.info("Redis Sentinel connection established")
            else:
                # Use standard Redis connection with connection pooling
                self.pool = ConnectionPool(
                    host=self.config.host,
                    port=self.config.port,
                    db=self.config.db,
                    password=self.config.password,
                    ssl=self.config.ssl,
                    ssl_cert_reqs=self.config.ssl_cert_reqs,
                    max_connections=self.config.max_connections,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    retry_on_timeout=self.config.retry_on_timeout,
                    decode_responses=self.config.decode_responses,
                    health_check_interval=self.config.health_check_interval
                )
                self.client = Redis(connection_pool=self.pool)
                logger.info("Redis connection pool established")
            
            # Test connection
            self.client.ping()
            logger.info("Redis connection test successful")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            raise
    
    def _update_metrics(self, operation: str, success: bool, response_time: float):
        """Update performance metrics."""
        self.metrics.total_operations += 1
        if success:
            self.metrics.successful_operations += 1
        else:
            self.metrics.failed_operations += 1
        
        # Update average response time
        if self.metrics.total_operations == 1:
            self.metrics.average_response_time = response_time
        else:
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_operations - 1) + response_time) /
                self.metrics.total_operations
            )
        
        self.metrics.last_operation_time = datetime.now(UTC)
    
    def _handle_redis_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Handle Redis errors with appropriate logging and metrics."""
        if isinstance(error, ConnectionError):
            self.metrics.connection_errors += 1
            logger.error(f"Redis connection error during {operation}: {error}")
        elif isinstance(error, TimeoutError):
            self.metrics.timeout_errors += 1
            logger.error(f"Redis timeout error during {operation}: {error}")
        else:
            logger.error(f"Redis error during {operation}: {error}")
        
        return {"success": False, "error": str(error), "operation": operation}
    
    @contextmanager
    def _operation_context(self, operation: str):
        """Context manager for Redis operations with metrics and error handling."""
        start_time = time.time()
        success = False
        
        try:
            yield
            success = True
        except Exception as e:
            self._handle_redis_error(e, operation)
            raise
        finally:
            response_time = time.time() - start_time
            self._update_metrics(operation, success, response_time)
    
    # Cache Management
    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None, 
                  namespace: Optional[str] = None) -> Dict[str, Any]:
        """Set a cache entry with optional TTL and namespace."""
        try:
            full_key = f"{namespace}:{key}" if namespace else key
            serialized_value = json.dumps(value) if not isinstance(value, (str, int, float, bool)) else value
            
            with self._operation_context("set_cache"):
                if ttl:
                    result = self.client.setex(full_key, ttl, serialized_value)
                else:
                    result = self.client.set(full_key, serialized_value)
                
                if result:
                    logger.debug(f"Cache set: {full_key}")
                    return {"success": True, "key": full_key, "ttl": ttl}
                else:
                    return {"success": False, "error": "Failed to set cache"}
                    
        except Exception as e:
            return self._handle_redis_error(e, "set_cache")
    
    def get_cache(self, key: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get a cache entry with automatic deserialization."""
        try:
            full_key = f"{namespace}:{key}" if namespace else key
            
            with self._operation_context("get_cache"):
                value = self.client.get(full_key)
                
                if value is None:
                    self.metrics.cache_misses += 1
                    logger.debug(f"Cache miss: {full_key}")
                    return {"success": True, "value": None, "cache_hit": False}
                
                self.metrics.cache_hits += 1
                logger.debug(f"Cache hit: {full_key}")
                
                # Try to deserialize JSON
                try:
                    deserialized_value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    deserialized_value = value
                
                return {"success": True, "value": deserialized_value, "cache_hit": True}
                
        except Exception as e:
            return self._handle_redis_error(e, "get_cache")
    
    def delete_cache(self, key: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Delete a cache entry."""
        try:
            full_key = f"{namespace}:{key}" if namespace else key
            
            with self._operation_context("delete_cache"):
                result = self.client.delete(full_key)
                logger.debug(f"Cache deleted: {full_key}")
                return {"success": True, "deleted": result > 0}
                
        except Exception as e:
            return self._handle_redis_error(e, "delete_cache")
    
    def invalidate_namespace(self, namespace: str) -> Dict[str, Any]:
        """Invalidate all cache entries in a namespace."""
        try:
            pattern = f"{namespace}:*"
            
            with self._operation_context("invalidate_namespace"):
                keys = self.client.keys(pattern)
                if keys:
                    result = self.client.delete(*keys)
                    logger.info(f"Invalidated {result} cache entries in namespace: {namespace}")
                    return {"success": True, "invalidated_count": result}
                else:
                    return {"success": True, "invalidated_count": 0}
                    
        except Exception as e:
            return self._handle_redis_error(e, "invalidate_namespace")
    
    # Session Storage
    def set_session(self, session_id: str, data: Dict[str, Any], 
                   ttl: Optional[int] = 3600) -> Dict[str, Any]:
        """Store session data with TTL."""
        return self.set_cache(session_id, data, ttl, namespace="session")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve session data."""
        return self.get_cache(session_id, namespace="session")
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete session data."""
        return self.delete_cache(session_id, namespace="session")
    
    def extend_session(self, session_id: str, ttl: int = 3600) -> Dict[str, Any]:
        """Extend session TTL."""
        try:
            with self._operation_context("extend_session"):
                result = self.client.expire(f"session:{session_id}", ttl)
                return {"success": True, "extended": result}
        except Exception as e:
            return self._handle_redis_error(e, "extend_session")
    
    # Rate Limiting
    def check_rate_limit(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Check and update rate limit for a key."""
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            with self._operation_context("check_rate_limit"):
                # Use Redis sorted set for sliding window rate limiting
                pipe = self.client.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.zcard(key)
                pipe.expire(key, window)
                results = pipe.execute()
                
                current_count = results[2]
                is_allowed = current_count <= limit
                
                reset_time = datetime.fromtimestamp(current_time + window, UTC)
                
                rate_limit_info = RateLimitInfo(
                    key=key,
                    limit=limit,
                    window=window,
                    current_count=current_count,
                    reset_time=reset_time,
                    blocked=not is_allowed
                )
                
                return {
                    "success": True,
                    "allowed": is_allowed,
                    "current_count": current_count,
                    "limit": limit,
                    "reset_time": reset_time.isoformat(),
                    "rate_limit_info": rate_limit_info
                }
                
        except Exception as e:
            return self._handle_redis_error(e, "check_rate_limit")
    
    def get_rate_limit_status(self, key: str) -> Dict[str, Any]:
        """Get current rate limit status for a key."""
        try:
            with self._operation_context("get_rate_limit_status"):
                current_time = int(time.time())
                count = self.client.zcard(key)
                ttl = self.client.ttl(key)
                
                return {
                    "success": True,
                    "current_count": count,
                    "ttl": ttl,
                    "key": key
                }
                
        except Exception as e:
            return self._handle_redis_error(e, "get_rate_limit_status")
    
    # Performance Monitoring
    def get_metrics(self) -> Dict[str, Any]:
        """Get Redis performance metrics."""
        try:
            with self._operation_context("get_metrics"):
                # Get Redis server info
                info = self.client.info()
                
                metrics_data = {
                    "client_metrics": {
                        "total_operations": self.metrics.total_operations,
                        "successful_operations": self.metrics.successful_operations,
                        "failed_operations": self.metrics.failed_operations,
                        "cache_hits": self.metrics.cache_hits,
                        "cache_misses": self.metrics.cache_misses,
                        "hit_rate": (
                            self.metrics.cache_hits / (self.metrics.cache_hits + self.metrics.cache_misses)
                            if (self.metrics.cache_hits + self.metrics.cache_misses) > 0 else 0
                        ),
                        "average_response_time": self.metrics.average_response_time,
                        "last_operation_time": (
                            self.metrics.last_operation_time.isoformat()
                            if self.metrics.last_operation_time else None
                        ),
                        "connection_errors": self.metrics.connection_errors,
                        "timeout_errors": self.metrics.timeout_errors
                    },
                    "server_info": {
                        "redis_version": info.get("redis_version"),
                        "connected_clients": info.get("connected_clients"),
                        "used_memory_human": info.get("used_memory_human"),
                        "total_commands_processed": info.get("total_commands_processed"),
                        "keyspace_hits": info.get("keyspace_hits"),
                        "keyspace_misses": info.get("keyspace_misses"),
                        "uptime_in_seconds": info.get("uptime_in_seconds")
                    }
                }
                
                return {"success": True, "metrics": metrics_data}
                
        except Exception as e:
            return self._handle_redis_error(e, "get_metrics")
    
    def reset_metrics(self) -> Dict[str, Any]:
        """Reset client metrics."""
        self.metrics = RedisMetrics()
        logger.info("Redis metrics reset")
        return {"success": True, "message": "Metrics reset"}
    
    # Failover Handling
    def test_connection(self) -> Dict[str, Any]:
        """Test Redis connection health."""
        try:
            with self._operation_context("test_connection"):
                self.client.ping()
                return {"success": True, "status": "connected"}
        except Exception as e:
            return self._handle_redis_error(e, "test_connection")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        try:
            info = {
                "host": self.config.host,
                "port": self.config.port,
                "db": self.config.db,
                "use_sentinel": self.config.use_sentinel,
                "ssl_enabled": self.config.ssl,
                "max_connections": self.config.max_connections
            }
            
            if self.config.use_sentinel:
                info["sentinel_hosts"] = self.config.sentinel_hosts
                info["sentinel_service_name"] = self.config.sentinel_service_name
            
            return {"success": True, "connection_info": info}
            
        except Exception as e:
            return self._handle_redis_error(e, "get_connection_info")
    
    # Utility Methods
    def flush_all(self) -> Dict[str, Any]:
        """Flush all Redis data (use with caution)."""
        try:
            with self._operation_context("flush_all"):
                result = self.client.flushall()
                logger.warning("Redis flush all executed")
                return {"success": True, "flushed": result}
        except Exception as e:
            return self._handle_redis_error(e, "flush_all")
    
    def get_keys(self, pattern: str = "*") -> Dict[str, Any]:
        """Get keys matching pattern."""
        try:
            with self._operation_context("get_keys"):
                keys = self.client.keys(pattern)
                return {"success": True, "keys": keys, "count": len(keys)}
        except Exception as e:
            return self._handle_redis_error(e, "get_keys")
    
    def close(self):
        """Close Redis connection."""
        try:
            if self.client:
                self.client.close()
            if self.pool:
                self.pool.disconnect()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}") 