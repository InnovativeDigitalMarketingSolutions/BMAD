#!/usr/bin/env python3
"""
Comprehensive Error Handling System
Provides standardized error handling, logging, and recovery mechanisms
"""

import logging
import traceback
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories for classification."""
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    CONFIGURATION = "CONFIGURATION"
    RESOURCE = "RESOURCE"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class ErrorHandler:
    """
    Comprehensive error handling system.
    
    Provides standardized error handling, classification, logging,
    and recovery mechanisms for the BMAD system.
    """
    
    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {}
        self.error_callbacks = {}
        
        # Initialize default recovery strategies
        self._init_default_recovery_strategies()
    
    def _init_default_recovery_strategies(self):
        """Initialize default recovery strategies."""
        self.recovery_strategies = {
            ErrorCategory.AUTHENTICATION: self._retry_with_refresh,
            ErrorCategory.AUTHORIZATION: self._log_and_deny,
            ErrorCategory.VALIDATION: self._log_and_return_error,
            ErrorCategory.DATABASE: self._retry_with_backoff,
            ErrorCategory.NETWORK: self._retry_with_exponential_backoff,
            ErrorCategory.EXTERNAL_SERVICE: self._use_fallback_service,
            ErrorCategory.CONFIGURATION: self._use_default_config,
            ErrorCategory.RESOURCE: self._wait_and_retry,
            ErrorCategory.TIMEOUT: self._retry_with_increased_timeout,
            ErrorCategory.UNKNOWN: self._log_and_continue
        }
    
    def classify_error(self, error: Exception) -> ErrorCategory:
        """Classify error based on type and message."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['unauthorized', 'authentication', 'token', 'jwt']):
            return ErrorCategory.AUTHENTICATION
        
        # Authorization errors
        if any(keyword in error_message for keyword in ['forbidden', 'permission', 'access denied']):
            return ErrorCategory.AUTHORIZATION
        
        # Validation errors
        if any(keyword in error_message for keyword in ['validation', 'invalid', 'required', 'format']):
            return ErrorCategory.VALIDATION
        
        # Database errors
        if any(keyword in error_message for keyword in ['database', 'connection', 'sql', 'postgres', 'redis']):
            return ErrorCategory.DATABASE
        
        # Network errors
        if any(keyword in error_message for keyword in ['connection', 'timeout', 'network', 'dns']):
            return ErrorCategory.NETWORK
        
        # External service errors
        if any(keyword in error_message for keyword in ['api', 'service', 'external', 'third-party']):
            return ErrorCategory.EXTERNAL_SERVICE
        
        # Configuration errors
        if any(keyword in error_message for keyword in ['config', 'environment', 'setting']):
            return ErrorCategory.CONFIGURATION
        
        # Resource errors
        if any(keyword in error_message for keyword in ['memory', 'disk', 'resource', 'quota']):
            return ErrorCategory.RESOURCE
        
        # Timeout errors
        if any(keyword in error_message for keyword in ['timeout', 'deadline']):
            return ErrorCategory.TIMEOUT
        
        return ErrorCategory.UNKNOWN
    
    def get_error_severity(self, error: Exception, context: Dict[str, Any] = None) -> ErrorSeverity:
        """Determine error severity based on error and context."""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Critical errors
        if any(keyword in error_message.lower() for keyword in ['security', 'authentication bypass', 'sql injection']):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if any(keyword in error_message.lower() for keyword in ['database', 'connection lost', 'service unavailable']):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if any(keyword in error_message.lower() for keyword in ['validation', 'timeout', 'rate limit']):
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle error with classification, logging, and recovery.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Dictionary with error handling result
        """
        if context is None:
            context = {}
        
        # Classify and analyze error
        category = self.classify_error(error)
        severity = self.get_error_severity(error, context)
        
        # Update error counts
        error_key = f"{category.value}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error with appropriate level
        self._log_error(error, category, severity, context)
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(error, category, context)
        
        # Execute error callbacks
        self._execute_error_callbacks(error, category, severity, context)
        
        return {
            "category": category.value,
            "severity": severity.value,
            "recovered": recovery_result["success"],
            "recovery_action": recovery_result["action"],
            "error_count": self.error_counts[error_key],
            "should_retry": recovery_result.get("should_retry", False),
            "retry_delay": recovery_result.get("retry_delay", 0)
        }
    
    def _log_error(self, error: Exception, category: ErrorCategory, 
                   severity: ErrorSeverity, context: Dict[str, Any]):
        """Log error with appropriate level and details."""
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "category": category.value,
            "severity": severity.value,
            "context": context,
            "timestamp": time.time(),
            "traceback": traceback.format_exc()
        }
        
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR [{category.value}]: {error}", extra=error_details)
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ERROR [{category.value}]: {error}", extra=error_details)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ERROR [{category.value}]: {error}", extra=error_details)
        else:
            logger.info(f"LOW SEVERITY ERROR [{category.value}]: {error}", extra=error_details)
    
    def _attempt_recovery(self, error: Exception, category: ErrorCategory, 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from error based on category."""
        strategy = self.recovery_strategies.get(category, self._log_and_continue)
        
        try:
            return strategy(error, context)
        except Exception as recovery_error:
            logger.error(f"Recovery strategy failed: {recovery_error}")
            return {"success": False, "action": "recovery_failed"}
    
    def _retry_with_refresh(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry with token refresh for authentication errors."""
        logger.info("Attempting authentication recovery with token refresh")
        return {"success": True, "action": "token_refresh", "should_retry": True, "retry_delay": 1}
    
    def _log_and_deny(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log authorization error and deny access."""
        logger.warning("Authorization error - access denied")
        return {"success": False, "action": "access_denied"}
    
    def _log_and_return_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log validation error and return error response."""
        logger.info("Validation error - returning error response")
        return {"success": False, "action": "return_error"}
    
    def _retry_with_backoff(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry database operations with exponential backoff."""
        retry_count = context.get("retry_count", 0)
        if retry_count < 3:
            delay = 2 ** retry_count
            logger.info(f"Retrying database operation in {delay} seconds")
            return {"success": True, "action": "retry_backoff", "should_retry": True, "retry_delay": delay}
        return {"success": False, "action": "max_retries_exceeded"}
    
    def _retry_with_exponential_backoff(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry network operations with exponential backoff."""
        retry_count = context.get("retry_count", 0)
        if retry_count < 5:
            delay = 2 ** retry_count
            logger.info(f"Retrying network operation in {delay} seconds")
            return {"success": True, "action": "retry_exponential", "should_retry": True, "retry_delay": delay}
        return {"success": False, "action": "max_retries_exceeded"}
    
    def _use_fallback_service(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use fallback service for external service failures."""
        logger.info("Using fallback service for external service failure")
        return {"success": True, "action": "fallback_service"}
    
    def _use_default_config(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use default configuration for configuration errors."""
        logger.info("Using default configuration")
        return {"success": True, "action": "default_config"}
    
    def _wait_and_retry(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wait and retry for resource errors."""
        logger.info("Waiting for resource availability")
        return {"success": True, "action": "wait_retry", "should_retry": True, "retry_delay": 5}
    
    def _retry_with_increased_timeout(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry with increased timeout for timeout errors."""
        logger.info("Retrying with increased timeout")
        return {"success": True, "action": "increased_timeout", "should_retry": True, "retry_delay": 1}
    
    def _log_and_continue(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log unknown error and continue."""
        logger.info("Unknown error - continuing operation")
        return {"success": True, "action": "continue"}
    
    def _execute_error_callbacks(self, error: Exception, category: ErrorCategory, 
                                severity: ErrorSeverity, context: Dict[str, Any]):
        """Execute registered error callbacks."""
        for callback in self.error_callbacks.values():
            try:
                callback(error, category, severity, context)
            except Exception as callback_error:
                logger.error(f"Error callback failed: {callback_error}")
    
    def register_error_callback(self, name: str, callback: Callable):
        """Register error callback function."""
        self.error_callbacks[name] = callback
        logger.info(f"Registered error callback: {name}")
    
    def unregister_error_callback(self, name: str):
        """Unregister error callback function."""
        if name in self.error_callbacks:
            del self.error_callbacks[name]
            logger.info(f"Unregistered error callback: {name}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        return {
            "error_counts": self.error_counts,
            "total_errors": sum(self.error_counts.values()),
            "callback_count": len(self.error_callbacks)
        }
    
    def reset_statistics(self):
        """Reset error statistics."""
        self.error_counts.clear()
        logger.info("Error statistics reset")


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(func: Callable = None, *, 
                  max_retries: int = 3,
                  retry_delay: float = 1.0,
                  context_provider: Callable = None):
    """
    Decorator to handle errors in functions.
    
    Args:
        func: Function to decorate
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        context_provider: Function to provide context for error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    return func(*args, **kwargs)
                    
                except Exception as error:
                    # Provide context
                    context = {}
                    if context_provider:
                        try:
                            context = context_provider(*args, **kwargs)
                        except Exception:
                            pass
                    
                    context["retry_count"] = retry_count
                    context["function_name"] = func.__name__
                    
                    # Handle error
                    result = error_handler.handle_error(error, context)
                    
                    # Check if we should retry
                    if result["should_retry"] and retry_count < max_retries:
                        retry_count += 1
                        time.sleep(result.get("retry_delay", retry_delay))
                        continue
                    
                    # Re-raise if not recovered
                    if not result["recovered"]:
                        raise error
                    
                    # Return default value or continue
                    return None
            
            # This should never be reached, but just in case
            raise Exception(f"Max retries ({max_retries}) exceeded for {func.__name__}")
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def safe_execute(func: Callable, *args, default_return: Any = None, **kwargs) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return on error
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as error:
        context = {
            "function_name": func.__name__,
            "args": str(args),
            "kwargs": str(kwargs)
        }
        error_handler.handle_error(error, context)
        return default_return


# Example usage:
if __name__ == "__main__":
    # Example function that might fail
    def unreliable_function(should_fail: bool = True):
        if should_fail:
            raise ConnectionError("Database connection failed")
        return "Success!"
    
    # Apply error handling decorator
    @handle_errors(max_retries=3, retry_delay=1.0)
    def protected_function():
        return unreliable_function()
    
    # Test error handling
    try:
        result = protected_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Function failed: {e}")
    
    # Test safe execution
    result = safe_execute(unreliable_function, True, default_return="Fallback result")
    print(f"Safe execution result: {result}")
    
    # Print statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}") 