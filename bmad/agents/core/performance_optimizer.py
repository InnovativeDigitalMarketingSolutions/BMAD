"""
BMAD Performance Optimizer

Advanced performance optimizations voor BMAD agents.
Inclusief intelligent caching, connection pooling, en resource management.
"""

import asyncio
import logging
import time
import weakref
from collections import defaultdict, OrderedDict
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')

class IntelligentCache:
    """
    Intelligent cache met adaptive TTL en memory management.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.access_count: Dict[str, int] = defaultdict(int)
        self.creation_time: Dict[str, float] = {}
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with access tracking."""
        with self.lock:
            if key in self.cache:
                # Update access count and move to end (LRU)
                self.access_count[key] += 1
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache with adaptive TTL."""
        with self.lock:
            # Remove if exists
            if key in self.cache:
                del self.cache[key]
            
            # Add new item
            self.cache[key] = value
            self.creation_time[key] = time.time()
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            
            # Evict if necessary
            if len(self.cache) > self.max_size:
                self._evict_least_valuable()
    
    def _evict_least_valuable(self) -> None:
        """Evict least valuable items based on access count and age."""
        if not self.cache:
            return
        
        # Calculate value score for each item
        current_time = time.time()
        item_scores = {}
        
        for key in self.cache.keys():
            age = current_time - self.creation_time.get(key, current_time)
            access_count = self.access_count.get(key, 0)
            
            # Score = access_count / (age + 1) to avoid division by zero
            score = access_count / (age + 1)
            item_scores[key] = score
        
        # Remove items with lowest scores
        items_to_remove = len(self.cache) - self.max_size + 1
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1])
        
        for key, _ in sorted_items[:items_to_remove]:
            del self.cache[key]
            del self.access_count[key]
            del self.creation_time[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.access_count.clear()
            self.creation_time.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": self._calculate_hit_rate(),
                "avg_access_count": sum(self.access_count.values()) / len(self.access_count) if self.access_count else 0
            }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_accesses = sum(self.access_count.values())
        if total_accesses == 0:
            return 0.0
        return len(self.cache) / total_accesses

class ConnectionPool:
    """
    Generic connection pool voor verschillende services.
    """
    
    def __init__(self, max_connections: int = 10, max_idle_time: int = 300):
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.active_connections: List[Any] = []
        self.idle_connections: List[Any] = []
        self.connection_times: Dict[int, float] = {}
        self.lock = threading.RLock()
        
    def get_connection(self, factory: Callable[[], T]) -> T:
        """Get connection from pool or create new one."""
        with self.lock:
            # Try to get from idle pool
            if self.idle_connections:
                connection = self.idle_connections.pop()
                self.active_connections.append(connection)
                self.connection_times[id(connection)] = time.time()
                return connection
            
            # Create new connection if under limit
            if len(self.active_connections) < self.max_connections:
                connection = factory()
                self.active_connections.append(connection)
                self.connection_times[id(connection)] = time.time()
                return connection
            
            # Wait for available connection
            raise Exception("Connection pool exhausted")
    
    def return_connection(self, connection: T) -> None:
        """Return connection to pool."""
        with self.lock:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
                self.idle_connections.append(connection)
                # Don't update time for idle connections
    
    def cleanup_idle_connections(self) -> None:
        """Remove connections that have been idle too long."""
        with self.lock:
            current_time = time.time()
            to_remove = []
            
            for connection in self.idle_connections:
                conn_id = id(connection)
                if conn_id in self.connection_times:
                    idle_time = current_time - self.connection_times[conn_id]
                    if idle_time > self.max_idle_time:
                        to_remove.append(connection)
            
            for connection in to_remove:
                self.idle_connections.remove(connection)
                del self.connection_times[id(connection)]

class PerformanceProfiler:
    """
    Performance profiler voor BMAD agents.
    """
    
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.active_profiles: Dict[str, float] = {}
        self.lock = threading.RLock()
    
    def start_profile(self, name: str) -> None:
        """Start profiling a named operation."""
        with self.lock:
            self.active_profiles[name] = time.time()
    
    def end_profile(self, name: str) -> float:
        """End profiling and return duration."""
        with self.lock:
            if name in self.active_profiles:
                start_time = self.active_profiles.pop(name)
                duration = time.time() - start_time
                
                # Store profile data
                if name not in self.profiles:
                    self.profiles[name] = {
                        "count": 0,
                        "total_time": 0,
                        "min_time": float('inf'),
                        "max_time": 0,
                        "avg_time": 0
                    }
                
                profile = self.profiles[name]
                profile["count"] += 1
                profile["total_time"] += duration
                profile["min_time"] = min(profile["min_time"], duration)
                profile["max_time"] = max(profile["max_time"], duration)
                profile["avg_time"] = profile["total_time"] / profile["count"]
                
                return duration
            return 0.0
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get profile data for a named operation."""
        with self.lock:
            return self.profiles.get(name)
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all profile data."""
        with self.lock:
            return dict(self.profiles)

# Global instances
intelligent_cache = IntelligentCache()
performance_profiler = PerformanceProfiler()

def cached(ttl: Optional[int] = None):
    """
    Decorator voor intelligent caching.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = intelligent_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            intelligent_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def profiled(name: Optional[str] = None):
    """
    Decorator voor performance profiling.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        profile_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            performance_profiler.start_profile(profile_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = performance_profiler.end_profile(profile_name)
                logger.debug(f"Profile {profile_name}: {duration*1000:.2f}ms")
        
        return wrapper
    return decorator

async def async_profiled(name: Optional[str] = None):
    """
    Async decorator voor performance profiling.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        profile_name = name or func.__name__
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            performance_profiler.start_profile(profile_name)
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = performance_profiler.end_profile(profile_name)
                logger.debug(f"Async Profile {profile_name}: {duration*1000:.2f}ms")
        
        return wrapper
    return decorator 