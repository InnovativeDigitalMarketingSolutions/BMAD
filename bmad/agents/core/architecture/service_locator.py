"""
BMAD Service Locator

Service locator pattern voor BMAD agents.
Zorgt voor centrale service discovery en management.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar
from threading import Lock

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceLocator:
    """
    Service locator voor BMAD services.
    Ondersteunt service registration, discovery, en lifecycle management.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._service_types: Dict[str, Type] = {}
        self._service_configs: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def register_service(self, name: str, service: Any, service_type: Optional[Type] = None, config: Optional[Dict[str, Any]] = None):
        """
        Register een service.
        
        Args:
            name: Service naam
            service: Service instance
            service_type: Service type (optional)
            config: Service configuratie (optional)
        """
        with self._lock:
            self._services[name] = service
            if service_type:
                self._service_types[name] = service_type
            if config:
                self._service_configs[name] = config
            
            logger.info(f"Service registered: {name}")
    
    def get_service(self, name: str) -> Any:
        """
        Get een service by naam.
        
        Args:
            name: Service naam
            
        Returns:
            Service instance
        """
        with self._lock:
            if name not in self._services:
                raise KeyError(f"Service not found: {name}")
            return self._services[name]
    
    def get_service_with_type(self, name: str, service_type: Type[T]) -> T:
        """
        Get een service met type checking.
        
        Args:
            name: Service naam
            service_type: Expected service type
            
        Returns:
            Typed service instance
        """
        service = self.get_service(name)
        if not isinstance(service, service_type):
            raise TypeError(f"Service {name} is not of type {service_type}")
        return service
    
    def has_service(self, name: str) -> bool:
        """Check of een service bestaat."""
        with self._lock:
            return name in self._services
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List alle services met metadata."""
        with self._lock:
            services_info = {}
            for name, service in self._services.items():
                info = {
                    "type": type(service).__name__,
                    "config": self._service_configs.get(name, {}),
                    "registered_type": self._service_types.get(name, type(service)).__name__
                }
                services_info[name] = info
            return services_info
    
    def remove_service(self, name: str):
        """Remove een service."""
        with self._lock:
            if name in self._services:
                del self._services[name]
                del self._service_types[name]
                del self._service_configs[name]
                logger.info(f"Service removed: {name}")
    
    def clear_services(self):
        """Clear alle services."""
        with self._lock:
            self._services.clear()
            self._service_types.clear()
            self._service_configs.clear()
            logger.info("All services cleared")
    
    def get_service_health(self, name: str) -> Dict[str, Any]:
        """Get health status van een service."""
        if not self.has_service(name):
            return {"status": "not_found", "error": f"Service {name} not found"}
        
        service = self.get_service(name)
        
        # Check if service has health check method
        if hasattr(service, 'health_check'):
            try:
                health = service.health_check()
                return {"status": "healthy", "service": name, "details": health}
            except Exception as e:
                return {"status": "unhealthy", "service": name, "error": str(e)}
        
        # Basic health check
        try:
            # Try to access service
            _ = str(service)
            return {"status": "healthy", "service": name, "type": type(service).__name__}
        except Exception as e:
            return {"status": "unhealthy", "service": name, "error": str(e)}
    
    def get_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status van alle services."""
        health_status = {}
        for name in self._services.keys():
            health_status[name] = self.get_service_health(name)
        return health_status

# Global service locator
service_locator = ServiceLocator()

def register_default_services():
    """Register default BMAD services in service locator."""
    from bmad.agents.core.monitoring.monitoring import PerformanceMonitor
    from bmad.agents.core.policy.advanced_policy_engine import AdvancedPolicyEngine
    from bmad.agents.core.agent.test_sprites import TestSpriteLibrary
    from bmad.agents.core.security.input_validator import InputValidator
    from bmad.agents.core.security.rate_limiter import RateLimiter
    from bmad.agents.core.security.secrets_manager import SecretsManager
    
    # Register core services
    service_locator.register_service(
        "performance_monitor",
        PerformanceMonitor(),
        config={"type": "monitoring", "version": "1.0"}
    )
    
    service_locator.register_service(
        "policy_engine",
        AdvancedPolicyEngine(),
        config={"type": "policy", "version": "1.0"}
    )
    
    service_locator.register_service(
        "sprite_library",
        TestSpriteLibrary(),
        config={"type": "testing", "version": "1.0"}
    )
    
    service_locator.register_service(
        "input_validator",
        InputValidator(),
        config={"type": "security", "version": "1.0"}
    )
    
    service_locator.register_service(
        "rate_limiter",
        RateLimiter(),
        config={"type": "security", "version": "1.0"}
    )
    
    service_locator.register_service(
        "secrets_manager",
        SecretsManager(),
        config={"type": "security", "version": "1.0"}
    )
    
    logger.info("Default services registered in service locator") 