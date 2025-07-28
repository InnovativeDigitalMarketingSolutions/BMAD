"""
BMAD Dependency Injection Container

Centralized dependency management voor BMAD agents.
Zorgt voor loose coupling en betere testability.
"""

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DependencyContainer:
    """
    Dependency injection container voor BMAD.
    Ondersteunt singleton, factory, en transient registrations.
    """
    
    def __init__(self):
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._transients: Dict[str, Type] = {}
        self._resolved_dependencies: Dict[str, Any] = {}
    
    def register_singleton(self, interface: str, implementation: Any):
        """
        Register een singleton dependency.
        
        Args:
            interface: Interface naam
            implementation: Implementation instance
        """
        self._singletons[interface] = implementation
        logger.debug(f"Singleton registered: {interface}")
    
    def register_factory(self, interface: str, factory: Callable):
        """
        Register een factory dependency.
        
        Args:
            interface: Interface naam
            factory: Factory function
        """
        self._factories[interface] = factory
        logger.debug(f"Factory registered: {interface}")
    
    def register_transient(self, interface: str, implementation: Type[T]):
        """
        Register een transient dependency.
        
        Args:
            interface: Interface naam
            implementation: Implementation class
        """
        self._transients[interface] = implementation
        logger.debug(f"Transient registered: {interface}")
    
    def resolve(self, interface: str) -> Any:
        """
        Resolve een dependency.
        
        Args:
            interface: Interface naam
            
        Returns:
            Resolved dependency
        """
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check factories
        if interface in self._factories:
            factory = self._factories[interface]
            instance = factory()
            logger.debug(f"Factory resolved: {interface}")
            return instance
        
        # Check transients
        if interface in self._transients:
            implementation = self._transients[interface]
            instance = implementation()
            logger.debug(f"Transient resolved: {interface}")
            return instance
        
        raise KeyError(f"Dependency not found: {interface}")
    
    def resolve_with_dependencies(self, interface: str, **dependencies) -> Any:
        """
        Resolve een dependency met extra dependencies.
        
        Args:
            interface: Interface naam
            dependencies: Extra dependencies
            
        Returns:
            Resolved dependency
        """
        # Store temporary dependencies
        original_dependencies = {}
        for key, value in dependencies.items():
            if key in self._singletons:
                original_dependencies[key] = self._singletons[key]
            self._singletons[key] = value
        
        try:
            return self.resolve(interface)
        finally:
            # Restore original dependencies
            for key, value in original_dependencies.items():
                self._singletons[key] = value
    
    def has_dependency(self, interface: str) -> bool:
        """Check of een dependency geregistreerd is."""
        return (
            interface in self._singletons or
            interface in self._factories or
            interface in self._transients
        )
    
    def clear(self):
        """Clear alle dependencies."""
        self._singletons.clear()
        self._factories.clear()
        self._transients.clear()
        self._resolved_dependencies.clear()
        logger.info("Dependency container cleared")
    
    def get_registered_services(self) -> Dict[str, str]:
        """Get overzicht van alle geregistreerde services."""
        services = {}
        
        for interface in self._singletons.keys():
            services[interface] = "singleton"
        
        for interface in self._factories.keys():
            services[interface] = "factory"
        
        for interface in self._transients.keys():
            services[interface] = "transient"
        
        return services

# Global dependency container
container = DependencyContainer()

def inject(*dependencies: str):
    """
    Decorator voor dependency injection.
    
    Args:
        dependencies: Dependency interfaces om te injecteren
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Resolve dependencies
            resolved_deps = {}
            for dep in dependencies:
                resolved_deps[dep] = container.resolve(dep)
            
            # Add to kwargs
            kwargs.update(resolved_deps)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def register_default_services():
    """Register default BMAD services."""
    from bmad.agents.core.monitoring.monitoring import get_performance_monitor
    from bmad.agents.core.policy.advanced_policy_engine import get_advanced_policy_engine
    from bmad.agents.core.agent.test_sprites import get_sprite_library
    from bmad.agents.core.security.input_validator import InputValidator
    from bmad.agents.core.security.rate_limiter import rate_limiter
    from bmad.agents.core.security.secrets_manager import secrets_manager
    
    # Register core services
    container.register_singleton("performance_monitor", get_performance_monitor())
    container.register_singleton("policy_engine", get_advanced_policy_engine())
    container.register_singleton("sprite_library", get_sprite_library())
    container.register_singleton("input_validator", InputValidator())
    container.register_singleton("rate_limiter", rate_limiter)
    container.register_singleton("secrets_manager", secrets_manager)
    
    logger.info("Default services registered in dependency container") 