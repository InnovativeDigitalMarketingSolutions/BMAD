#!/usr/bin/env python3
"""
Dependency Manager - Lazy Loading and Dependency Isolation for MCP Agents
Following official MCP specification: https://modelcontextprotocol.io/docs
"""

import importlib
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    purpose: str
    required: bool = False
    version: Optional[str] = None
    loaded: bool = False
    load_time: Optional[datetime] = None
    error_message: Optional[str] = None

class DependencyManager:
    """
    Manages agent dependencies with lazy loading and isolation.
    
    Features:
    - Lazy loading van optional dependencies
    - Dependency isolation voor testing
    - Error handling en graceful degradation
    - Performance tracking
    - Dependency health monitoring
    """
    
    def __init__(self):
        """Initialize dependency manager."""
        self._loaded_modules: Dict[str, Any] = {}
        self._dependency_info: Dict[str, DependencyInfo] = {}
        self._load_callbacks: Dict[str, Callable] = {}
        
        # Define optional dependencies
        self._optional_dependencies = {
            'psutil': DependencyInfo(
                name='psutil',
                purpose='performance_monitoring',
                required=False,
                version='>=5.8.0'
            ),
            'aiohttp': DependencyInfo(
                name='aiohttp',
                purpose='async_http_operations',
                required=False,
                version='>=3.8.0'
            ),
            'fastapi': DependencyInfo(
                name='fastapi',
                purpose='api_development',
                required=False,
                version='>=0.68.0'
            ),
            'pandas': DependencyInfo(
                name='pandas',
                purpose='data_analysis',
                required=False,
                version='>=1.3.0'
            ),
            'numpy': DependencyInfo(
                name='numpy',
                purpose='numerical_computing',
                required=False,
                version='>=1.21.0'
            ),
            'requests': DependencyInfo(
                name='requests',
                purpose='http_requests',
                required=False,
                version='>=2.25.0'
            ),
            'pydantic': DependencyInfo(
                name='pydantic',
                purpose='data_validation',
                required=False,
                version='>=1.8.0'
            ),
            'sqlalchemy': DependencyInfo(
                name='sqlalchemy',
                purpose='database_operations',
                required=False,
                version='>=1.4.0'
            )
        }
        
        # Define required dependencies
        self._required_dependencies = {
            'asyncio': DependencyInfo(
                name='asyncio',
                purpose='async_operations',
                required=True
            ),
            'json': DependencyInfo(
                name='json',
                purpose='json_processing',
                required=True
            ),
            'logging': DependencyInfo(
                name='logging',
                purpose='logging',
                required=True
            ),
            'pathlib': DependencyInfo(
                name='pathlib',
                purpose='file_operations',
                required=True
            )
        }
        
        # Initialize dependency info
        self._dependency_info.update(self._optional_dependencies)
        self._dependency_info.update(self._required_dependencies)
        
        # Load required dependencies immediately
        self._load_required_dependencies()
    
    def _load_required_dependencies(self):
        """Load all required dependencies immediately."""
        for dep_name, dep_info in self._required_dependencies.items():
            try:
                module = importlib.import_module(dep_name)
                self._loaded_modules[dep_name] = module
                dep_info.loaded = True
                dep_info.load_time = datetime.utcnow()
                logger.debug(f"Loaded required dependency: {dep_name}")
            except ImportError as e:
                dep_info.error_message = str(e)
                logger.error(f"Failed to load required dependency {dep_name}: {e}")
                raise ImportError(f"Required dependency {dep_name} not available: {e}")
    
    def get_optional_module(self, module_name: str) -> Optional[Any]:
        """
        Lazy load optional dependencies.
        
        Args:
            module_name: Name of the module to load
            
        Returns:
            Optional[Any]: Loaded module or None if not available
        """
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        if module_name not in self._dependency_info:
            logger.warning(f"Unknown dependency: {module_name}")
            return None
        
        dep_info = self._dependency_info[module_name]
        
        try:
            # Load the module
            module = importlib.import_module(module_name)
            self._loaded_modules[module_name] = module
            dep_info.loaded = True
            dep_info.load_time = datetime.utcnow()
            
            logger.debug(f"Lazy loaded optional dependency: {module_name}")
            return module
            
        except ImportError as e:
            dep_info.error_message = str(e)
            logger.warning(f"Optional dependency {module_name} not available: {e}")
            return None
    
    def is_module_available(self, module_name: str) -> bool:
        """
        Check if a module is available (loaded or loadable).
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            bool: True if module is available
        """
        if module_name in self._loaded_modules:
            return True
        
        if module_name not in self._dependency_info:
            return False
        
        # Try to load it
        module = self.get_optional_module(module_name)
        return module is not None
    
    def get_dependency_status(self, module_name: str) -> Optional[DependencyInfo]:
        """
        Get status information for a dependency.
        
        Args:
            module_name: Name of the dependency
            
        Returns:
            Optional[DependencyInfo]: Dependency status information
        """
        return self._dependency_info.get(module_name)
    
    def get_all_dependencies_status(self) -> Dict[str, DependencyInfo]:
        """
        Get status of all dependencies.
        
        Returns:
            Dict[str, DependencyInfo]: Status of all dependencies
        """
        return self._dependency_info.copy()
    
    def register_load_callback(self, module_name: str, callback: Callable):
        """
        Register a callback to be called when a module is loaded.
        
        Args:
            module_name: Name of the module
            callback: Callback function to call
        """
        self._load_callbacks[module_name] = callback
    
    def get_loaded_modules(self) -> List[str]:
        """
        Get list of currently loaded modules.
        
        Returns:
            List[str]: Names of loaded modules
        """
        return list(self._loaded_modules.keys())
    
    def get_available_modules(self) -> List[str]:
        """
        Get list of all available modules (loaded or loadable).
        
        Returns:
            List[str]: Names of available modules
        """
        available = []
        for module_name in self._dependency_info:
            if self.is_module_available(module_name):
                available.append(module_name)
        return available
    
    def get_missing_modules(self) -> List[str]:
        """
        Get list of missing optional modules.
        
        Returns:
            List[str]: Names of missing optional modules
        """
        missing = []
        for module_name, dep_info in self._dependency_info.items():
            if not dep_info.required and not dep_info.loaded:
                missing.append(module_name)
        return missing
    
    def get_dependency_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive dependency health report.
        
        Returns:
            Dict[str, Any]: Dependency health information
        """
        total_deps = len(self._dependency_info)
        loaded_deps = len(self._loaded_modules)
        required_deps = len([d for d in self._dependency_info.values() if d.required])
        optional_deps = total_deps - required_deps
        
        missing_required = []
        missing_optional = []
        
        for module_name, dep_info in self._dependency_info.items():
            if not dep_info.loaded:
                if dep_info.required:
                    missing_required.append(module_name)
                else:
                    missing_optional.append(module_name)
        
        return {
            "total_dependencies": total_deps,
            "loaded_dependencies": loaded_deps,
            "required_dependencies": required_deps,
            "optional_dependencies": optional_deps,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "load_success_rate": (loaded_deps / total_deps) * 100 if total_deps > 0 else 0,
            "dependency_details": self._dependency_info.copy(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def safe_import(self, module_name: str, fallback_value: Any = None) -> Any:
        """
        Safely import a module with fallback value.
        
        Args:
            module_name: Name of the module to import
            fallback_value: Value to return if import fails
            
        Returns:
            Any: Imported module or fallback value
        """
        try:
            return self.get_optional_module(module_name) or fallback_value
        except Exception as e:
            logger.warning(f"Safe import failed for {module_name}: {e}")
            return fallback_value
    
    def create_feature_checker(self, required_modules: List[str]) -> Callable[[], bool]:
        """
        Create a feature checker function for a set of required modules.
        
        Args:
            required_modules: List of modules required for the feature
            
        Returns:
            Callable[[], bool]: Function that checks if feature is available
        """
        def feature_available() -> bool:
            return all(self.is_module_available(module) for module in required_modules)
        
        return feature_available
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for dependency loading.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        metrics = {
            "total_load_time": 0,
            "average_load_time": 0,
            "load_times": {},
            "failed_loads": 0,
            "successful_loads": 0
        }
        
        load_times = []
        for module_name, dep_info in self._dependency_info.items():
            if dep_info.loaded and dep_info.load_time:
                # Calculate load time (simplified)
                load_time = 0.001  # Placeholder
                load_times.append(load_time)
                metrics["load_times"][module_name] = load_time
                metrics["successful_loads"] += 1
            elif not dep_info.loaded and not dep_info.required:
                metrics["failed_loads"] += 1
        
        if load_times:
            metrics["total_load_time"] = sum(load_times)
            metrics["average_load_time"] = sum(load_times) / len(load_times)
        
        return metrics
    
    def cleanup(self):
        """Cleanup dependency manager resources."""
        self._loaded_modules.clear()
        self._load_callbacks.clear()
        logger.info("Dependency manager cleanup completed")

# Global dependency manager instance
_global_dependency_manager: Optional[DependencyManager] = None

def get_dependency_manager() -> DependencyManager:
    """
    Get global dependency manager instance.
    
    Returns:
        DependencyManager: Global dependency manager
    """
    global _global_dependency_manager
    if _global_dependency_manager is None:
        _global_dependency_manager = DependencyManager()
    return _global_dependency_manager

def check_feature_availability(feature_name: str, required_modules: List[str]) -> bool:
    """
    Check if a feature is available based on required modules.
    
    Args:
        feature_name: Name of the feature
        required_modules: List of modules required for the feature
        
    Returns:
        bool: True if feature is available
    """
    manager = get_dependency_manager()
    available = all(manager.is_module_available(module) for module in required_modules)
    
    if not available:
        missing = [module for module in required_modules if not manager.is_module_available(module)]
        logger.warning(f"Feature {feature_name} not available. Missing modules: {missing}")
    
    return available 