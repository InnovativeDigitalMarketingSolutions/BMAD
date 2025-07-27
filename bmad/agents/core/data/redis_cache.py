"""
BMAD Redis Caching Layer

Dit module biedt een geavanceerde caching laag met Redis voor performance optimalisatie.
Implementeert intelligent caching met TTL, cache invalidation en fallback strategieën.
"""

import os
import json
import logging
import hashlib
import time
from typing import Any, Optional, Dict, List, Union
from functools import wraps
import redis
from redis.exceptions import RedisError, ConnectionError

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Geavanceerde Redis caching laag voor BMAD agents.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialiseer Redis cache.
        
        :param redis_url: Redis connection URL (optioneel)
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
        self.enabled = True
        
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
    
    def _connect(self):
        """Maak verbinding met Redis."""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info("✅ Redis cache verbonden")
        except (RedisError, ConnectionError) as e:
            logger.warning(f"⚠️ Redis niet beschikbaar: {e}")
            self.enabled = False
            self.client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Genereer een unieke cache key.
        
        :param prefix: Cache key prefix
        :param args: Positionele argumenten
        :param kwargs: Keyword argumenten
        :return: Unieke cache key
        """
        key_parts = [prefix]
        
        # Voeg positionele argumenten toe
        for arg in args:
            key_parts.append(str(arg))
        
        # Voeg keyword argumenten toe (gesorteerd voor consistentie)
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Maak hash van de key voor consistentie
        key_string = ":".join(key_parts)
        return f"bmad:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Haal waarde op uit cache.
        
        :param key: Cache key
        :param default: Default waarde als key niet bestaat
        :return: Gecachte waarde of default
        """
        if not self.enabled or not self.client:
            return default
        
        try:
            value = self.client.get(key)
            if value is None:
                return default
            
            # Probeer JSON deserialisatie
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except RedisError as e:
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
        if not self.enabled or not self.client:
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
            self.client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except RedisError as e:
            logger.warning(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Verwijder waarde uit cache.
        
        :param key: Cache key
        :return: True bij succes
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            result = self.client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return result > 0
        except RedisError as e:
            logger.warning(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Controleer of key bestaat in cache.
        
        :param key: Cache key
        :return: True als key bestaat
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.warning(f"Redis exists error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Verwijder alle keys die matchen met pattern.
        
        :param pattern: Redis pattern (bijv. "bmad:llm:*")
        :return: Aantal verwijderde keys
        """
        if not self.enabled or not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cache clear pattern '{pattern}': {deleted} keys verwijderd")
                return deleted
            return 0
        except RedisError as e:
            logger.warning(f"Redis clear pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Haal cache statistieken op.
        
        :return: Cache statistieken
        """
        if not self.enabled or not self.client:
            return {"enabled": False}
        
        try:
            info = self.client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except RedisError as e:
            logger.warning(f"Redis stats error: {e}")
            return {"enabled": False, "error": str(e)}

# Global cache instance
cache = RedisCache()

def cached(ttl: Optional[int] = None, cache_type: str = "default", 
           key_prefix: str = "function"):
    """
    Decorator voor function caching.
    
    :param ttl: Time-to-live in seconden
    :param cache_type: Type cache voor default TTL
    :param key_prefix: Prefix voor cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Genereer cache key
            cache_key = cache._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Probeer cache hit
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # Cache miss - voer functie uit
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # Cache resultaat
            cache.set(cache_key, result, ttl, cache_type)
            
            return result
        return wrapper
    return decorator

def cache_llm_response(func):
    """Decorator specifiek voor LLM response caching."""
    return cached(ttl=3600, cache_type="llm_response", key_prefix="llm")(func)

def cache_agent_confidence(func):
    """Decorator specifiek voor agent confidence caching."""
    return cached(ttl=86400, cache_type="agent_confidence", key_prefix="confidence")(func)

def cache_project_config(func):
    """Decorator specifiek voor project configuratie caching."""
    return cached(ttl=86400, cache_type="project_config", key_prefix="project")(func)

def cache_clickup_api(func):
    """Decorator specifiek voor ClickUp API response caching."""
    return cached(ttl=300, cache_type="clickup_api", key_prefix="clickup")(func) 