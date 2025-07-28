"""
BMAD Rate Limiter

Rate limiting voor BMAD agents om abuse en DDoS attacks te voorkomen.
"""

import time
import logging
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration voor rate limiting."""
    max_requests: int
    window_seconds: int
    burst_size: Optional[int] = None

class RateLimiter:
    """
    Rate limiter voor BMAD agents.
    Ondersteunt sliding window en token bucket algoritmes.
    """
    
    def __init__(self):
        self.limits: Dict[str, RateLimitConfig] = {}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque())
        self.token_buckets: Dict[str, Tuple[float, int]] = {}
        
        # Default limits
        self.set_default_limits()
    
    def set_default_limits(self):
        """Set default rate limits voor verschillende agent types."""
        self.limits.update({
            "llm_requests": RateLimitConfig(max_requests=100, window_seconds=3600),  # 100 per hour
            "api_calls": RateLimitConfig(max_requests=1000, window_seconds=3600),    # 1000 per hour
            "file_operations": RateLimitConfig(max_requests=500, window_seconds=3600), # 500 per hour
            "database_queries": RateLimitConfig(max_requests=2000, window_seconds=3600), # 2000 per hour
            "webhook_calls": RateLimitConfig(max_requests=100, window_seconds=3600),  # 100 per hour
            "agent_initialization": RateLimitConfig(max_requests=50, window_seconds=3600), # 50 per hour
        })
    
    def add_limit(self, key: str, max_requests: int, window_seconds: int, burst_size: Optional[int] = None):
        """Add een nieuwe rate limit."""
        self.limits[key] = RateLimitConfig(max_requests, window_seconds, burst_size)
        logger.info(f"Rate limit toegevoegd: {key} = {max_requests} requests per {window_seconds}s")
    
    def is_allowed(self, key: str, identifier: str = "default") -> Tuple[bool, Dict[str, Any]]:
        """
        Check of een request toegestaan is.
        
        Args:
            key: Rate limit key
            identifier: Unique identifier (IP, user ID, etc.)
            
        Returns:
            Tuple van (allowed, info)
        """
        if key not in self.limits:
            return True, {"message": "No rate limit configured"}
        
        config = self.limits[key]
        full_key = f"{key}:{identifier}"
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(full_key, current_time, config.window_seconds)
        
        # Check if under limit
        request_count = len(self.request_history[full_key])
        
        if request_count >= config.max_requests:
            return False, {
                "message": "Rate limit exceeded",
                "limit": config.max_requests,
                "window": config.window_seconds,
                "current": request_count,
                "reset_time": current_time + config.window_seconds
            }
        
        # Add current request
        self.request_history[full_key].append(current_time)
        
        return True, {
            "message": "Request allowed",
            "limit": config.max_requests,
            "current": request_count + 1,
            "remaining": config.max_requests - (request_count + 1)
        }
    
    def _clean_old_requests(self, key: str, current_time: float, window_seconds: int):
        """Remove old requests buiten de window."""
        history = self.request_history[key]
        cutoff_time = current_time - window_seconds
        
        # Remove old requests
        while history and history[0] < cutoff_time:
            history.popleft()
    
    def get_stats(self, key: str, identifier: str = "default") -> Dict[str, Any]:
        """Get rate limit statistics."""
        full_key = f"{key}:{identifier}"
        current_time = time.time()
        
        if key not in self.limits:
            return {"error": "No rate limit configured"}
        
        config = self.limits[key]
        self._clean_old_requests(full_key, current_time, config.window_seconds)
        
        request_count = len(self.request_history[full_key])
        
        return {
            "key": key,
            "identifier": identifier,
            "limit": config.max_requests,
            "window_seconds": config.window_seconds,
            "current_requests": request_count,
            "remaining_requests": max(0, config.max_requests - request_count),
            "utilization_percent": (request_count / config.max_requests) * 100
        }
    
    def reset_limit(self, key: str, identifier: str = "default"):
        """Reset rate limit voor een specifieke key/identifier."""
        full_key = f"{key}:{identifier}"
        if full_key in self.request_history:
            self.request_history[full_key].clear()
            logger.info(f"Rate limit reset voor: {full_key}")
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics voor alle rate limits."""
        stats = {}
        for key in self.limits.keys():
            stats[key] = self.get_stats(key)
        return stats

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(key: str, identifier: str = "default"):
    """
    Decorator voor rate limiting.
    
    Args:
        key: Rate limit key
        identifier: Unique identifier
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            allowed, info = rate_limiter.is_allowed(key, identifier)
            
            if not allowed:
                logger.warning(f"Rate limit exceeded: {key} - {info['message']}")
                raise Exception(f"Rate limit exceeded: {info['message']}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator 