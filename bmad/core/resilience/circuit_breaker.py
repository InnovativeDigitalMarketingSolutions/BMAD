#!/usr/bin/env python3
"""
Circuit Breaker Pattern Implementation
Provides resilience against cascading failures in distributed systems
"""

import time
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, calls fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back


class CircuitBreaker:
    """
    Circuit Breaker implementation for resilience.
    
    The circuit breaker pattern prevents cascading failures by monitoring
    the success/failure of calls to external services and temporarily
    stopping calls when the failure rate exceeds a threshold.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout: int = 60,
                 expected_exception: type = Exception,
                 name: str = "default"):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds to wait before trying half-open
            expected_exception: Exception type to consider as failure
            name: Name for logging and identification
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        # Statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        
        logger.info(f"Circuit breaker '{name}' initialized with threshold={failure_threshold}, timeout={timeout}s")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: When circuit is open
            Exception: Original function exception
        """
        self.total_calls += 1
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._set_half_open()
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return False
        
        return time.time() - self.last_failure_time >= self.timeout
    
    def _set_half_open(self):
        """Set circuit to half-open state."""
        self.state = CircuitState.HALF_OPEN
        logger.info(f"Circuit breaker '{self.name}' set to HALF_OPEN")
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.last_success_time = time.time()
        self.successful_calls += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit breaker '{self.name}' reset to CLOSED")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.failed_calls += 1
        
        logger.warning(f"Circuit breaker '{self.name}' failure #{self.failure_count}")
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        success_rate = (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0
        
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": round(success_rate, 2),
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time
        }
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global circuit breaker registry
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, 
                       failure_threshold: int = 5,
                       timeout: int = 60,
                       expected_exception: type = Exception) -> CircuitBreaker:
    """
    Get or create a circuit breaker instance.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Time to wait before half-open
        expected_exception: Exception type to consider as failure
        
    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            timeout=timeout,
            expected_exception=expected_exception,
            name=name
        )
    
    return _circuit_breakers[name]


def circuit_breaker(name: str,
                   failure_threshold: int = 5,
                   timeout: int = 60,
                   expected_exception: type = Exception):
    """
    Decorator to apply circuit breaker pattern to functions.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Time to wait before half-open
        expected_exception: Exception type to consider as failure
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cb = get_circuit_breaker(name, failure_threshold, timeout, expected_exception)
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


def get_all_circuit_breakers() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all circuit breakers."""
    return {name: cb.get_stats() for name, cb in _circuit_breakers.items()}


def reset_all_circuit_breakers():
    """Reset all circuit breakers to closed state."""
    for cb in _circuit_breakers.values():
        cb.reset()
    logger.info("All circuit breakers reset")


# Pre-configured circuit breakers for common services
def get_database_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for database operations."""
    return get_circuit_breaker(
        name="database",
        failure_threshold=3,
        timeout=30,
        expected_exception=Exception
    )


def get_external_api_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for external API calls."""
    return get_circuit_breaker(
        name="external_api",
        failure_threshold=5,
        timeout=60,
        expected_exception=Exception
    )


def get_redis_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for Redis operations."""
    return get_circuit_breaker(
        name="redis",
        failure_threshold=3,
        timeout=30,
        expected_exception=Exception
    )


# Example usage:
if __name__ == "__main__":
    # Example function that might fail
    def unreliable_function():
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise Exception("Service temporarily unavailable")
        return "Success!"
    
    # Apply circuit breaker decorator
    @circuit_breaker("example_service", failure_threshold=3, timeout=10)
    def protected_function():
        return unreliable_function()
    
    # Test the circuit breaker
    for i in range(10):
        try:
            result = protected_function()
            print(f"Call {i+1}: {result}")
        except CircuitBreakerOpenError as e:
            print(f"Call {i+1}: {e}")
        except Exception as e:
            print(f"Call {i+1}: {e}")
        
        time.sleep(1)
    
    # Print statistics
    stats = get_all_circuit_breakers()
    print(f"\nCircuit breaker stats: {stats}") 