"""
BMAD Redis Caching Layer

Dit module biedt een geavanceerde caching laag met Redis voor performance optimalisatie.
Implementeert intelligent caching met TTL, cache invalidation en fallback strategieën.
"""

import os
import json
import gzip
import pickle
import logging
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)

# Global connection pool for better performance
_redis_pool = None
_redis_client = None

def get_redis_client():
    """Get Redis client with connection pooling."""
    global _redis_client, _redis_pool
    
    if _redis_client is None:
        try:
            # Create connection pool
            _redis_pool = ConnectionPool(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                password=os.getenv("REDIS_PASSWORD"),
                max_connections=20,  # Connection pooling
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            _redis_client = redis.Redis(connection_pool=_redis_pool)
            
            # Test connection
            _redis_client.ping()
            logger.info("✅ Redis cache verbonden met connection pooling")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            _redis_client = None
    
    return _redis_client

def _compress_data(data: Any) -> bytes:
    """Compress data for storage with security measures."""
    try:
        # Handle function objects and other non-serializable types
        if callable(data):
            return json.dumps({"error": "Cannot serialize function object"}).encode('utf-8')
        
        # Use JSON for security instead of pickle when possible
        if isinstance(data, (dict, list, str, int, float, bool, type(None))):
            return json.dumps(data).encode('utf-8')
        
        # For other objects, try to convert to dict first
        if hasattr(data, '__dict__'):
            try:
                return json.dumps(data.__dict__).encode('utf-8')
            except (TypeError, ValueError):
                pass
        
        # Fallback to pickle only for complex objects, with security measures
        import pickle
        serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        if len(serialized) > 1024:  # Only compress if > 1KB
            return gzip.compress(serialized)
        return serialized
    except Exception as e:
        # Final fallback to JSON string representation
        return json.dumps({"error": f"Serialization failed: {str(e)}"}).encode('utf-8')

def _decompress_data(data: bytes) -> Any:
    """Decompress data from storage with security measures."""
    try:
        if data.startswith(b'\x1f\x8b'):  # Gzip header
            decompressed = gzip.decompress(data)
            # Try JSON first
            try:
                return json.loads(decompressed.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback to pickle with security check
                import pickle
                return pickle.loads(decompressed)
        else:
            # Try JSON first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fallback to pickle with security check
                import pickle
                return pickle.loads(data)
    except Exception as e:
        logger.warning(f"Data decompression failed: {e}")
        # Return safe fallback
        return None

class RedisCache:
    """Advanced Redis caching layer with intelligent fallback strategies."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self.enabled = True
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        # Default TTL settings (in seconds)
        self.default_ttls = {
            "llm_response": 3600,      # 1 uur
            "agent_confidence": 86400,  # 24 uur
            "project_config": 86400,   # 24 uur
            "clickup_api": 300,        # 5 minuten
            "user_context": 1800,      # 30 minuten
            "workflow_state": 7200,    # 2 uur
            "metrics": 60,             # 1 minuut
        }
        self._connect()

    def cache(self, *args, **kwargs):
        """Make the RedisCache instance callable for backward compatibility."""
        return self.get(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Make RedisCache callable like a function."""
        return self.get(*args, **kwargs)

    @property
    def client(self):
        """Backward compatibility property for tests."""
        return self.redis_client

    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key with secure hashing."""
        import hashlib
        
        # Filter out non-serializable objects (like functions)
        def filter_serializable(obj):
            if callable(obj):
                return f"<function:{getattr(obj, '__name__', 'unknown')}>"
            elif hasattr(obj, '__dict__'):
                return f"<object:{type(obj).__name__}>"
            else:
                return str(obj)
        
        # Filter args and kwargs
        filtered_args = [filter_serializable(arg) for arg in args]
        filtered_kwargs = {k: filter_serializable(v) for k, v in kwargs.items()}
        
        key_data = f"{func_name}:{str(filtered_args)}:{str(sorted(filtered_kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _connect(self):
        """Maak verbinding met Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache verbonden")
        except (redis.RedisError, redis.ConnectionError) as e:
            logger.warning(f"⚠️ Redis niet beschikbaar: {e}")
            self.enabled = False
            self.redis_client = None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Haal waarde op uit cache.
        
        :param key: Cache key
        :param default: Default waarde als key niet bestaat
        :return: Gecachte waarde of default
        """
        if not self.enabled or not self.redis_client:
            return default

        try:
            value = self.redis_client.get(key)
            if value is None:
                return default

            # Probeer JSON deserialisatie
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except redis.RedisError as e:
            logger.warning(f"Redis get error: {e}")
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            cache_type: str = "default") -> bool:
        """
        Sla waarde op in cache.
        
        :param key: Cache key
        :param value: Te cachen waarde
        :param ttl: Time-to-live in seconden
        :param cache_type: Type cache voor default TTL
        :return: True bij succes
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            # Bepaal TTL
            if ttl is None:
                ttl = self.default_ttls.get(cache_type, 3600)

            # Serialiseer waarde
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)

            # Sla op in Redis
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except redis.RedisError as e:
            logger.warning(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Verwijder waarde uit cache.
        
        :param key: Cache key
        :return: True bij succes
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            result = self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return result > 0
        except redis.RedisError as e:
            logger.warning(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Controleer of key bestaat in cache.
        
        :param key: Cache key
        :return: True als key bestaat
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            logger.warning(f"Redis exists error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Verwijder alle keys die matchen met pattern.
        
        :param pattern: Redis pattern (bijv. "bmad:llm:*")
        :return: Aantal verwijderde keys
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cache clear pattern '{pattern}': {deleted} keys verwijderd")
                return deleted
            return 0
        except redis.RedisError as e:
            logger.warning(f"Redis clear pattern error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Haal cache statistieken op.
        
        :return: Cache statistieken
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False}

        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except redis.RedisError as e:
            logger.warning(f"Redis stats error: {e}")
            return {"enabled": False, "error": str(e)}

# Global cache instance
cache = RedisCache()

def _generate_key(func_name: str, *args, **kwargs) -> str:
    """Generate cache key with secure hashing."""
    import hashlib
    
    # Filter out non-serializable objects (like functions)
    def filter_serializable(obj):
        if callable(obj):
            return f"<function:{getattr(obj, '__name__', 'unknown')}>"
        elif hasattr(obj, '__dict__'):
            return f"<object:{type(obj).__name__}>"
        else:
            return str(obj)
    
    # Filter args and kwargs
    filtered_args = [filter_serializable(arg) for arg in args]
    filtered_kwargs = {k: filter_serializable(v) for k, v in kwargs.items()}
    
    key_data = f"{func_name}:{str(filtered_args)}:{str(sorted(filtered_kwargs.items()))}"
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: Optional[int] = None, cache_type: str = "default",
           key_prefix: str = "function", expire: Optional[int] = None):
    """
    Decorator voor function caching.
    
    :param ttl: Time-to-live in seconden
    :param cache_type: Type cache voor default TTL
    :param key_prefix: Prefix voor cache key
    :param expire: Alias for ttl (backward compatibility)
    """
    # Use expire if provided, otherwise use ttl
    actual_ttl = expire if expire is not None else ttl
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Import here to get the current cache instance (allows for patching)
            from .redis_cache import cache
            
            # Genereer cache key using the standalone function
            cache_key = _generate_key(f"{key_prefix}_{func.__name__}", *args, **kwargs)

            # Probeer cache hit
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result

            # Cache miss - voer functie uit
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)

            # Cache resultaat
            cache.set(cache_key, result, actual_ttl, cache_type)

            return result
        return wrapper
    return decorator

def cache_llm_response(ttl: int = 3600):
    """
    Cache decorator voor LLM responses met verbeterde performance.
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Get Redis client
            redis_client = get_redis_client()
            if redis_client is None:
                # Fallback to function execution
                return func(*args, **kwargs)
            
            try:
                # Generate cache key
                cache_key = _generate_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_data = redis_client.get(cache_key)
                if cached_data is not None:
                    result = _decompress_data(cached_data)
                    cache_time = time.time() - start_time
                    logger.debug(f"Cache hit for {func.__name__} in {cache_time*1000:.2f}ms")
                    return result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                compressed_data = _compress_data(result)
                redis_client.setex(cache_key, ttl, compressed_data)
                
                execution_time = time.time() - start_time
                logger.debug(f"Cache miss for {func.__name__}, executed in {execution_time*1000:.2f}ms")
                
                return result
                
            except Exception as e:
                logger.warning(f"Cache error for {func.__name__}: {e}")
                # Fallback to function execution
                return func(*args, **kwargs)
                
        return wrapper
    
    # Handle both @cache_llm_response and @cache_llm_response(ttl=3600) usage
    if callable(ttl):
        # Called without parameters: @cache_llm_response
        return decorator(ttl)
    else:
        # Called with parameters: @cache_llm_response(ttl=3600)
        return decorator

def cache_agent_confidence(func):
    """Decorator specifiek voor agent confidence caching."""
    return cached(ttl=86400, cache_type="agent_confidence", key_prefix="confidence")(func)

def cache_project_config(func):
    """Decorator specifiek voor project configuratie caching."""
    return cached(ttl=86400, cache_type="project_config", key_prefix="project")(func)

def cache_clickup_api(func):
    """Decorator specifiek voor ClickUp API response caching."""
    return cached(ttl=300, cache_type="clickup_api", key_prefix="clickup")(func)
