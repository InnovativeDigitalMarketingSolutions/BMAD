"""
Config Manager for API Gateway dynamic configuration management.
"""

import asyncio
import logging
import time
import json
from typing import Dict, Optional, Any, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConfigSource(str, Enum):
    """Configuration sources."""
    FILE = "file"
    ENV = "environment"
    CONSUL = "consul"
    REDIS = "redis"
    DATABASE = "database"


@dataclass
class ConfigChange:
    """Configuration change event."""
    key: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str


class ConfigManager:
    """Manages dynamic configuration for the API Gateway."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Any] = {}
        self.watchers: Dict[str, List[callable]] = {}
        self.change_history: List[ConfigChange] = []
        self._initialized = False
        self._watch_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the configuration manager."""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Load initial configurations
            await self._load_all_configs()
            
            # Start file watching
            self._watch_task = asyncio.create_task(self._watch_config_files())
            
            self._initialized = True
            logger.info("Config manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize config manager: {e}")
            raise
    
    async def _load_all_configs(self):
        """Load all configuration files."""
        try:
            # Load services configuration
            services_config = await self._load_config_file("services.yaml")
            if services_config:
                self.configs["services"] = services_config
            
            # Load routes configuration
            routes_config = await self._load_config_file("routes.yaml")
            if routes_config:
                self.configs["routes"] = routes_config
            
            # Load gateway configuration
            gateway_config = await self._load_config_file("gateway.yaml")
            if gateway_config:
                self.configs["gateway"] = gateway_config
            
            logger.info(f"Loaded {len(self.configs)} configuration files")
            
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
    
    async def _load_config_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a configuration file."""
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    config = yaml.safe_load(f)
                elif filename.endswith('.json'):
                    config = json.load(f)
                else:
                    logger.error(f"Unsupported configuration file format: {filename}")
                    return None
                
            logger.info(f"Loaded configuration from {filename}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration file {filename}: {e}")
            return None
    
    async def _save_config_file(self, filename: str, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        file_path = self.config_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    yaml.dump(config, f, default_flow_style=False, indent=2)
                elif filename.endswith('.json'):
                    json.dump(config, f, indent=2)
                else:
                    logger.error(f"Unsupported configuration file format: {filename}")
                    return False
            
            logger.info(f"Saved configuration to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration file {filename}: {e}")
            return False
    
    async def _watch_config_files(self):
        """Watch configuration files for changes."""
        while True:
            try:
                # Simple file watching implementation
                # In production, you might want to use a more sophisticated file watcher
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Reload configurations if files have changed
                await self._reload_if_changed()
                
            except Exception as e:
                logger.error(f"Error in config file watching: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _reload_if_changed(self):
        """Reload configurations if files have changed."""
        # This is a simplified implementation
        # In production, you would track file modification times
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        config = self.configs
        
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        
        return config
    
    async def set_config(self, key: str, value: Any, source: str = "api") -> bool:
        """Set configuration value."""
        try:
            keys = key.split('.')
            config = self.configs
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Store old value for change tracking
            old_value = config.get(keys[-1])
            
            # Set new value
            config[keys[-1]] = value
            
            # Record change
            change = ConfigChange(
                key=key,
                old_value=old_value,
                new_value=value,
                timestamp=time.time(),
                source=source
            )
            self.change_history.append(change)
            
            # Notify watchers
            await self._notify_watchers(key, old_value, value)
            
            logger.info(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting configuration {key}: {e}")
            return False
    
    def get_services_config(self) -> Dict[str, Any]:
        """Get services configuration."""
        return self.configs.get("services", {})
    
    def get_routes_config(self) -> List[Dict[str, Any]]:
        """Get routes configuration."""
        return self.configs.get("routes", [])
    
    def get_gateway_config(self) -> Dict[str, Any]:
        """Get gateway configuration."""
        return self.configs.get("gateway", {})
    
    async def update_services_config(self, services_config: Dict[str, Any]) -> bool:
        """Update services configuration."""
        try:
            old_config = self.configs.get("services", {})
            self.configs["services"] = services_config
            
            # Save to file
            await self._save_config_file("services.yaml", services_config)
            
            # Record change
            change = ConfigChange(
                key="services",
                old_value=old_config,
                new_value=services_config,
                timestamp=time.time(),
                source="api"
            )
            self.change_history.append(change)
            
            # Notify watchers
            await self._notify_watchers("services", old_config, services_config)
            
            logger.info("Services configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating services configuration: {e}")
            return False
    
    async def update_routes_config(self, routes_config: List[Dict[str, Any]]) -> bool:
        """Update routes configuration."""
        try:
            old_config = self.configs.get("routes", [])
            self.configs["routes"] = routes_config
            
            # Save to file
            await self._save_config_file("routes.yaml", routes_config)
            
            # Record change
            change = ConfigChange(
                key="routes",
                old_value=old_config,
                new_value=routes_config,
                timestamp=time.time(),
                source="api"
            )
            self.change_history.append(change)
            
            # Notify watchers
            await self._notify_watchers("routes", old_config, routes_config)
            
            logger.info("Routes configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating routes configuration: {e}")
            return False
    
    def add_watcher(self, key: str, callback: callable):
        """Add a configuration change watcher."""
        if key not in self.watchers:
            self.watchers[key] = []
        
        self.watchers[key].append(callback)
        logger.info(f"Added watcher for configuration key: {key}")
    
    def remove_watcher(self, key: str, callback: callable):
        """Remove a configuration change watcher."""
        if key in self.watchers and callback in self.watchers[key]:
            self.watchers[key].remove(callback)
            logger.info(f"Removed watcher for configuration key: {key}")
    
    async def _notify_watchers(self, key: str, old_value: Any, new_value: Any):
        """Notify watchers of configuration changes."""
        if key in self.watchers:
            for callback in self.watchers[key]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(key, old_value, new_value)
                    else:
                        callback(key, old_value, new_value)
                except Exception as e:
                    logger.error(f"Error in configuration watcher: {e}")
    
    def get_change_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get configuration change history."""
        history = []
        for change in self.change_history[-limit:]:
            history.append({
                "key": change.key,
                "old_value": change.old_value,
                "new_value": change.new_value,
                "timestamp": change.timestamp,
                "source": change.source
            })
        
        return history
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            "total_configs": len(self.configs),
            "config_keys": list(self.configs.keys()),
            "watchers": {key: len(watchers) for key, watchers in self.watchers.items()},
            "change_history_count": len(self.change_history),
            "last_change": self.change_history[-1].timestamp if self.change_history else None
        }
    
    async def reload_configs(self) -> bool:
        """Reload all configurations from files."""
        try:
            await self._load_all_configs()
            logger.info("Configurations reloaded")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading configurations: {e}")
            return False
    
    async def export_configs(self) -> Dict[str, Any]:
        """Export all configurations."""
        return {
            "services": self.get_services_config(),
            "routes": self.get_routes_config(),
            "gateway": self.get_gateway_config(),
            "exported_at": time.time()
        }
    
    async def import_configs(self, configs: Dict[str, Any]) -> bool:
        """Import configurations."""
        try:
            if "services" in configs:
                await self.update_services_config(configs["services"])
            
            if "routes" in configs:
                await self.update_routes_config(configs["routes"])
            
            if "gateway" in configs:
                self.configs["gateway"] = configs["gateway"]
                await self._save_config_file("gateway.yaml", configs["gateway"])
            
            logger.info("Configurations imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error importing configurations: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the config manager."""
        try:
            return {
                "status": "healthy",
                "configs_loaded": len(self.configs),
                "watchers_active": sum(len(watchers) for watchers in self.watchers.values()),
                "change_history_size": len(self.change_history),
                "config_dir": str(self.config_dir)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass 