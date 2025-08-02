"""
Rate Limiter for API Gateway request throttling.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RateLimitType(str, Enum):
    """Rate limit types."""
    USER = "user"
    IP = "ip"
    GLOBAL = "global"


@dataclass
class RateLimitWindow:
    """Rate limit window for tracking requests."""
    start_time: float
    request_count: int
    limit: int
    window_size: int


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    default_requests_per_minute: int = Field(100, description="Default requests per minute")
    default_requests_per_hour: int = Field(1000, description="Default requests per hour")
    default_requests_per_day: int = Field(10000, description="Default requests per day")
    burst_limit: int = Field(10, description="Burst limit for short time windows")
    burst_window: int = Field(1, description="Burst window in seconds")
    enable_ip_limiting: bool = Field(True, description="Enable IP-based rate limiting")
    enable_user_limiting: bool = Field(True, description="Enable user-based rate limiting")
    enable_global_limiting: bool = Field(True, description="Enable global rate limiting")


class RateLimitResult(BaseModel):
    """Rate limit check result."""
    allowed: bool = Field(..., description="Whether request is allowed")
    limit: int = Field(..., description="Request limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_time: float = Field(..., description="Reset time timestamp")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")


class RateLimiter:
    """Manages rate limiting for API requests."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.windows: Dict[str, Dict[str, RateLimitWindow]] = defaultdict(dict)
        self.global_windows: Dict[str, RateLimitWindow] = {}
        self._initialized = False
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the rate limiter."""
        try:
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_windows())
            
            self._initialized = True
            logger.info("Rate limiter initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter: {e}")
            raise
    
    def _get_window_key(self, limit_type: RateLimitType, identifier: str, window_size: int) -> str:
        """Generate window key for rate limiting."""
        return f"{limit_type.value}:{identifier}:{window_size}"
    
    def _get_current_window(self, window_size: int) -> int:
        """Get current window start time."""
        return int(time.time() // window_size) * window_size
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: RateLimitType = RateLimitType.USER,
        custom_limit: Optional[int] = None,
        custom_window: Optional[int] = None
    ) -> RateLimitResult:
        """Check if request is allowed based on rate limits."""
        if not self._initialized:
            raise RuntimeError("Rate limiter not initialized")
        
        try:
            # Determine limit and window size
            if custom_limit and custom_window:
                limit = custom_limit
                window_size = custom_window
            else:
                # Use default limits based on window size
                if limit_type == RateLimitType.GLOBAL:
                    limit = self.config.default_requests_per_minute
                    window_size = 60
                else:
                    limit = self.config.default_requests_per_minute
                    window_size = 60
            
            # Get window key
            window_key = self._get_window_key(limit_type, identifier, window_size)
            current_time = time.time()
            current_window_start = self._get_current_window(window_size)
            
            # Get or create window
            if limit_type == RateLimitType.GLOBAL:
                window = self.global_windows.get(window_key)
            else:
                window = self.windows[limit_type.value].get(window_key)
            
            # Create new window if needed
            if not window or window.start_time < current_window_start:
                window = RateLimitWindow(
                    start_time=current_window_start,
                    request_count=0,
                    limit=limit,
                    window_size=window_size
                )
                
                if limit_type == RateLimitType.GLOBAL:
                    self.global_windows[window_key] = window
                else:
                    self.windows[limit_type.value][window_key] = window
            
            # Check if request is allowed
            if window.request_count >= window.limit:
                # Calculate retry after time
                reset_time = window.start_time + window.window_size
                retry_after = max(0, int(reset_time - current_time))
                
                logger.warning(f"Rate limit exceeded for {limit_type.value}:{identifier}")
                
                return RateLimitResult(
                    allowed=False,
                    limit=window.limit,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=retry_after
                )
            
            # Increment request count
            window.request_count += 1
            
            # Calculate remaining requests and reset time
            remaining = max(0, window.limit - window.request_count)
            reset_time = window.start_time + window.window_size
            
            return RateLimitResult(
                allowed=True,
                limit=window.limit,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=None
            )
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request on error
            return RateLimitResult(
                allowed=True,
                limit=100,
                remaining=99,
                reset_time=time.time() + 60,
                retry_after=None
            )
    
    async def check_multiple_limits(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        custom_limits: Optional[Dict[str, Tuple[int, int]]] = None
    ) -> Dict[str, RateLimitResult]:
        """Check multiple rate limits simultaneously."""
        results = {}
        
        # Check user limit
        if user_id and self.config.enable_user_limiting:
            results["user"] = await self.check_rate_limit(
                user_id, 
                RateLimitType.USER
            )
        
        # Check IP limit
        if ip_address and self.config.enable_ip_limiting:
            results["ip"] = await self.check_rate_limit(
                ip_address, 
                RateLimitType.IP
            )
        
        # Check global limit
        if self.config.enable_global_limiting:
            results["global"] = await self.check_rate_limit(
                "global", 
                RateLimitType.GLOBAL
            )
        
        # Check custom limits
        if custom_limits:
            for limit_name, (limit, window) in custom_limits.items():
                results[limit_name] = await self.check_rate_limit(
                    limit_name,
                    RateLimitType.GLOBAL,
                    custom_limit=limit,
                    custom_window=window
                )
        
        return results
    
    def is_request_allowed(self, results: Dict[str, RateLimitResult]) -> bool:
        """Check if request is allowed based on multiple rate limit results."""
        return all(result.allowed for result in results.values())
    
    def get_retry_after(self, results: Dict[str, RateLimitResult]) -> Optional[int]:
        """Get the maximum retry after time from rate limit results."""
        retry_times = [result.retry_after for result in results.values() 
                      if result.retry_after is not None]
        
        return max(retry_times) if retry_times else None
    
    def get_rate_limit_headers(self, results: Dict[str, RateLimitResult]) -> Dict[str, str]:
        """Generate rate limit headers for response."""
        headers = {}
        
        for limit_type, result in results.items():
            prefix = f"X-RateLimit-{limit_type.title()}"
            headers[f"{prefix}-Limit"] = str(result.limit)
            headers[f"{prefix}-Remaining"] = str(result.remaining)
            headers[f"{prefix}-Reset"] = str(int(result.reset_time))
            
            if result.retry_after is not None:
                headers["Retry-After"] = str(result.retry_after)
        
        return headers
    
    async def reset_limits(self, identifier: str, limit_type: RateLimitType = RateLimitType.USER):
        """Reset rate limits for an identifier."""
        try:
            if limit_type == RateLimitType.GLOBAL:
                # Remove all global windows for this identifier
                keys_to_remove = [key for key in self.global_windows.keys() 
                                if key.startswith(f"{limit_type.value}:{identifier}:")]
                for key in keys_to_remove:
                    del self.global_windows[key]
            else:
                # Remove all windows for this identifier
                keys_to_remove = [key for key in self.windows[limit_type.value].keys() 
                                if key.startswith(f"{limit_type.value}:{identifier}:")]
                for key in keys_to_remove:
                    del self.windows[limit_type.value][key]
            
            logger.info(f"Reset rate limits for {limit_type.value}:{identifier}")
            
        except Exception as e:
            logger.error(f"Error resetting rate limits: {e}")
    
    async def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        try:
            stats = {
                "user_windows": len(self.windows.get("user", {})),
                "ip_windows": len(self.windows.get("ip", {})),
                "global_windows": len(self.global_windows),
                "total_windows": sum(len(windows) for windows in self.windows.values()) + len(self.global_windows)
            }
            
            # Calculate total requests
            total_requests = 0
            for windows in self.windows.values():
                total_requests += sum(window.request_count for window in windows.values())
            total_requests += sum(window.request_count for window in self.global_windows.values())
            
            stats["total_requests"] = total_requests
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting rate limit stats: {e}")
            return {"error": str(e)}
    
    async def _cleanup_expired_windows(self):
        """Clean up expired rate limit windows."""
        while True:
            try:
                current_time = time.time()
                
                # Clean up user and IP windows
                for limit_type in ["user", "ip"]:
                    if limit_type in self.windows:
                        expired_keys = []
                        for key, window in self.windows[limit_type].items():
                            if current_time - window.start_time > window.window_size * 2:
                                expired_keys.append(key)
                        
                        for key in expired_keys:
                            del self.windows[limit_type][key]
                
                # Clean up global windows
                expired_global_keys = []
                for key, window in self.global_windows.items():
                    if current_time - window.start_time > window.window_size * 2:
                        expired_global_keys.append(key)
                
                for key in expired_global_keys:
                    del self.global_windows[key]
                
                # Log cleanup if any windows were removed
                total_removed = sum(len([k for k in self.windows.get(lt, {}).keys() 
                                       if current_time - self.windows[lt][k].start_time > self.windows[lt][k].window_size * 2])
                                  for lt in ["user", "ip"]) + len(expired_global_keys)
                
                if total_removed > 0:
                    logger.info(f"Cleaned up {total_removed} expired rate limit windows")
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in rate limit cleanup: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the rate limiter."""
        try:
            stats = await self.get_rate_limit_stats()
            
            return {
                "status": "healthy",
                "stats": stats,
                "config": {
                    "default_requests_per_minute": self.config.default_requests_per_minute,
                    "enable_ip_limiting": self.config.enable_ip_limiting,
                    "enable_user_limiting": self.config.enable_user_limiting,
                    "enable_global_limiting": self.config.enable_global_limiting
                }
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