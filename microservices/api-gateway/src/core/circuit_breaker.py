"""
Circuit Breaker for API Gateway fault tolerance.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration."""
    failure_threshold: int = Field(5, description="Number of failures before opening circuit")
    recovery_timeout: int = Field(60, description="Time to wait before trying half-open state")
    success_threshold: int = Field(3, description="Number of successes to close circuit")
    timeout: float = Field(30.0, description="Request timeout in seconds")
    enable_monitoring: bool = Field(True, description="Enable circuit breaker monitoring")


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self.last_state_change = time.time()
        self._initialized = False
        
    async def initialize(self):
        """Initialize the circuit breaker."""
        try:
            self._initialized = True
            logger.info(f"Circuit breaker '{self.name}' initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breaker '{self.name}': {e}")
            raise
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if not self._initialized:
            raise RuntimeError("Circuit breaker not initialized")
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                await self._transition_to_half_open()
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is open")
        
        # Execute function
        start_time = time.time()
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
            await self._on_success()
            return result
            
        except asyncio.TimeoutError:
            await self._on_failure("timeout")
            raise CircuitBreakerTimeoutError(f"Circuit breaker '{self.name}' timeout")
            
        except Exception as e:
            await self._on_failure(str(e))
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset."""
        if self.state != CircuitState.OPEN:
            return False
        
        time_since_last_failure = time.time() - (self.stats.last_failure_time or 0)
        return time_since_last_failure >= self.config.recovery_timeout
    
    async def _transition_to_half_open(self):
        """Transition circuit to half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}' transitioned to half-open")
    
    async def _transition_to_open(self):
        """Transition circuit to open state."""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        self.stats.consecutive_successes = 0
        logger.warning(f"Circuit breaker '{self.name}' opened after {self.stats.consecutive_failures} failures")
    
    async def _transition_to_closed(self):
        """Transition circuit to closed state."""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        self.stats.consecutive_failures = 0
        logger.info(f"Circuit breaker '{self.name}' closed after {self.stats.consecutive_successes} successes")
    
    async def _on_success(self):
        """Handle successful request."""
        self.stats.total_requests += 1
        self.stats.successful_requests += 1
        self.stats.last_success_time = time.time()
        self.stats.consecutive_successes += 1
        self.stats.consecutive_failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            if self.stats.consecutive_successes >= self.config.success_threshold:
                await self._transition_to_closed()
    
    async def _on_failure(self, error: str):
        """Handle failed request."""
        self.stats.total_requests += 1
        self.stats.failed_requests += 1
        self.stats.last_failure_time = time.time()
        self.stats.consecutive_failures += 1
        self.stats.consecutive_successes = 0
        
        if self.state == CircuitState.CLOSED:
            if self.stats.consecutive_failures >= self.config.failure_threshold:
                await self._transition_to_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            await self._transition_to_open()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "name": self.name,
            "state": self.state.value,
            "last_state_change": self.last_state_change,
            "stats": {
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "consecutive_failures": self.stats.consecutive_failures,
                "consecutive_successes": self.stats.consecutive_successes,
                "last_failure_time": self.stats.last_failure_time,
                "last_success_time": self.stats.last_success_time
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout
            }
        }
    
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == CircuitState.OPEN
    
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self.state == CircuitState.CLOSED
    
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self.state == CircuitState.HALF_OPEN
    
    def force_open(self):
        """Force circuit to open state."""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}' forced open")
    
    def force_close(self):
        """Force circuit to closed state."""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        self.stats.consecutive_failures = 0
        self.stats.consecutive_successes = 0
        logger.info(f"Circuit breaker '{self.name}' forced closed")
    
    def reset_stats(self):
        """Reset circuit breaker statistics."""
        self.stats = CircuitBreakerStats()
        logger.info(f"Circuit breaker '{self.name}' statistics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the circuit breaker."""
        try:
            return {
                "status": "healthy" if self.state != CircuitState.OPEN else "degraded",
                "state": self.state.value,
                "stats": {
                    "total_requests": self.stats.total_requests,
                    "successful_requests": self.stats.successful_requests,
                    "failed_requests": self.stats.failed_requests,
                    "success_rate": (self.stats.successful_requests / max(self.stats.total_requests, 1)) * 100
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize the circuit breaker manager."""
        try:
            self._initialized = True
            logger.info("Circuit breaker manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breaker manager: {e}")
            raise
    
    def create_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create a new circuit breaker."""
        if name in self.circuit_breakers:
            logger.warning(f"Circuit breaker '{name}' already exists, returning existing instance")
            return self.circuit_breakers[name]
        
        circuit_breaker = CircuitBreaker(name, config)
        self.circuit_breakers[name] = circuit_breaker
        logger.info(f"Created circuit breaker '{name}'")
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        return self.circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str):
        """Remove a circuit breaker."""
        if name in self.circuit_breakers:
            del self.circuit_breakers[name]
            logger.info(f"Removed circuit breaker '{name}'")
    
    async def call_with_circuit_breaker(
        self,
        circuit_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection."""
        circuit_breaker = self.get_circuit_breaker(circuit_name)
        if not circuit_breaker:
            # Create default circuit breaker if it doesn't exist
            config = CircuitBreakerConfig()
            circuit_breaker = self.create_circuit_breaker(circuit_name, config)
            await circuit_breaker.initialize()
        
        return await circuit_breaker.call(func, *args, **kwargs)
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers."""
        return {
            name: circuit_breaker.get_state()
            for name, circuit_breaker in self.circuit_breakers.items()
        }
    
    def get_open_circuits(self) -> Dict[str, CircuitBreaker]:
        """Get all open circuit breakers."""
        return {
            name: circuit_breaker
            for name, circuit_breaker in self.circuit_breakers.items()
            if circuit_breaker.is_open()
        }
    
    def force_close_all(self):
        """Force close all circuit breakers."""
        for circuit_breaker in self.circuit_breakers.values():
            circuit_breaker.force_close()
        logger.info("All circuit breakers forced closed")
    
    def reset_all_stats(self):
        """Reset statistics for all circuit breakers."""
        for circuit_breaker in self.circuit_breakers.values():
            circuit_breaker.reset_stats()
        logger.info("All circuit breaker statistics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of all circuit breakers."""
        try:
            total_circuits = len(self.circuit_breakers)
            open_circuits = len(self.get_open_circuits())
            closed_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.is_closed())
            half_open_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.is_half_open())
            
            return {
                "status": "healthy" if open_circuits == 0 else "degraded",
                "total_circuits": total_circuits,
                "open_circuits": open_circuits,
                "closed_circuits": closed_circuits,
                "half_open_circuits": half_open_circuits,
                "circuits": self.get_all_states()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerTimeoutError(Exception):
    """Exception raised when circuit breaker times out."""
    pass 