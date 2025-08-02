"""
Load Balancer for API Gateway traffic distribution.
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    HEALTH_BASED = "health_based"


@dataclass
class ServiceInstance:
    """Service instance configuration."""
    id: str
    url: str
    weight: int = 1
    max_connections: int = 100
    health_check_url: str = "/health"
    enabled: bool = True
    healthy: bool = True
    last_health_check: float = 0
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    response_time_avg: float = 0


class LoadBalancerConfig(BaseModel):
    """Load balancer configuration."""
    strategy: LoadBalancingStrategy = Field(LoadBalancingStrategy.ROUND_ROBIN, description="Load balancing strategy")
    health_check_interval: int = Field(30, description="Health check interval in seconds")
    health_check_timeout: int = Field(5, description="Health check timeout in seconds")
    max_retries: int = Field(3, description="Maximum retries for failed requests")
    retry_delay: float = Field(1.0, description="Delay between retries in seconds")
    circuit_breaker_threshold: int = Field(5, description="Circuit breaker failure threshold")
    circuit_breaker_timeout: int = Field(60, description="Circuit breaker timeout in seconds")


class LoadBalancer:
    """Manages load balancing for service instances."""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.instances: Dict[str, ServiceInstance] = {}
        self.current_index: Dict[str, int] = defaultdict(int)
        self.health_check_task: Optional[asyncio.Task] = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the load balancer."""
        try:
            # Start health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            self._initialized = True
            logger.info("Load balancer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize load balancer: {e}")
            raise
    
    def add_instance(self, service_name: str, instance: ServiceInstance):
        """Add a service instance."""
        instance_key = f"{service_name}:{instance.id}"
        self.instances[instance_key] = instance
        logger.info(f"Added instance {instance_key} to load balancer")
    
    def remove_instance(self, service_name: str, instance_id: str):
        """Remove a service instance."""
        instance_key = f"{service_name}:{instance_id}"
        if instance_key in self.instances:
            del self.instances[instance_key]
            logger.info(f"Removed instance {instance_key} from load balancer")
    
    def get_instances_for_service(self, service_name: str) -> List[ServiceInstance]:
        """Get all instances for a service."""
        return [
            instance for key, instance in self.instances.items()
            if key.startswith(f"{service_name}:") and instance.enabled and instance.healthy
        ]
    
    def select_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Select an instance based on the load balancing strategy."""
        if not self._initialized:
            raise RuntimeError("Load balancer not initialized")
        
        instances = self.get_instances_for_service(service_name)
        if not instances:
            logger.warning(f"No healthy instances available for service {service_name}")
            return None
        
        if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_name, instances)
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(service_name, instances)
        elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(instances)
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_LEAST_CONNECTIONS:
            return self._weighted_least_connections_select(instances)
        elif self.config.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(instances)
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
            return self._weighted_random_select(instances)
        elif self.config.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based_select(instances)
        else:
            # Default to round robin
            return self._round_robin_select(service_name, instances)
    
    def _round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round robin selection."""
        if not instances:
            return None
        
        index = self.current_index[service_name] % len(instances)
        self.current_index[service_name] += 1
        return instances[index]
    
    def _weighted_round_robin_select(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted round robin selection."""
        if not instances:
            return None
        
        # Calculate total weight
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return instances[0]
        
        # Get current position
        current = self.current_index[service_name]
        
        # Find instance based on weight
        weight_sum = 0
        for instance in instances:
            weight_sum += instance.weight
            if current < weight_sum:
                self.current_index[service_name] += 1
                return instance
        
        # Reset if we've gone through all instances
        self.current_index[service_name] = 1
        return instances[0]
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection."""
        if not instances:
            return None
        
        return min(instances, key=lambda x: x.active_connections)
    
    def _weighted_least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted least connections selection."""
        if not instances:
            return None
        
        # Calculate weighted connections
        weighted_instances = [
            (instance, instance.active_connections / instance.weight)
            for instance in instances
        ]
        
        return min(weighted_instances, key=lambda x: x[1])[0]
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection."""
        if not instances:
            return None
        
        return random.choice(instances)
    
    def _weighted_random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted random selection."""
        if not instances:
            return None
        
        # Calculate total weight
        total_weight = sum(instance.weight for instance in instances)
        if total_weight == 0:
            return instances[0]
        
        # Generate random number
        rand = random.uniform(0, total_weight)
        
        # Select instance based on weight
        weight_sum = 0
        for instance in instances:
            weight_sum += instance.weight
            if rand <= weight_sum:
                return instance
        
        return instances[0]
    
    def _health_based_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Health-based selection (prefer healthier instances)."""
        if not instances:
            return None
        
        # Sort by health score (lower is better)
        health_scores = []
        for instance in instances:
            # Calculate health score based on various factors
            failure_rate = instance.failed_requests / max(instance.total_requests, 1)
            connection_usage = instance.active_connections / max(instance.max_connections, 1)
            health_score = failure_rate + connection_usage
            
            health_scores.append((instance, health_score))
        
        # Return instance with best health score
        return min(health_scores, key=lambda x: x[1])[0]
    
    def record_request(self, instance: ServiceInstance, success: bool, response_time: float):
        """Record request statistics for an instance."""
        instance.total_requests += 1
        instance.active_connections += 1
        
        if not success:
            instance.failed_requests += 1
        
        # Update average response time
        if instance.total_requests == 1:
            instance.response_time_avg = response_time
        else:
            instance.response_time_avg = (
                (instance.response_time_avg * (instance.total_requests - 1) + response_time) 
                / instance.total_requests
            )
    
    def record_response(self, instance: ServiceInstance):
        """Record response completion."""
        instance.active_connections = max(0, instance.active_connections - 1)
    
    async def _health_check_loop(self):
        """Health check loop for all instances."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _perform_health_checks(self):
        """Perform health checks for all instances."""
        import httpx
        
        async with httpx.AsyncClient(timeout=self.config.health_check_timeout) as client:
            tasks = []
            
            for instance in self.instances.values():
                if instance.enabled:
                    task = asyncio.create_task(self._check_instance_health(client, instance))
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_instance_health(self, client: httpx.AsyncClient, instance: ServiceInstance):
        """Check health of a single instance."""
        try:
            health_url = f"{instance.url.rstrip('/')}{instance.health_check_url}"
            response = await client.get(health_url)
            
            was_healthy = instance.healthy
            instance.healthy = response.status_code == 200
            instance.last_health_check = time.time()
            
            if was_healthy != instance.healthy:
                status = "healthy" if instance.healthy else "unhealthy"
                logger.info(f"Instance {instance.id} is now {status}")
                
        except Exception as e:
            was_healthy = instance.healthy
            instance.healthy = False
            instance.last_health_check = time.time()
            
            if was_healthy:
                logger.warning(f"Instance {instance.id} became unhealthy: {e}")
    
    def get_instance_stats(self, service_name: str) -> Dict[str, Any]:
        """Get statistics for instances of a service."""
        instances = self.get_instances_for_service(service_name)
        
        if not instances:
            return {"error": "No instances found"}
        
        stats = {
            "total_instances": len(instances),
            "healthy_instances": sum(1 for i in instances if i.healthy),
            "total_requests": sum(i.total_requests for i in instances),
            "total_failed_requests": sum(i.failed_requests for i in instances),
            "total_active_connections": sum(i.active_connections for i in instances),
            "average_response_time": sum(i.response_time_avg for i in instances) / len(instances),
            "instances": [
                {
                    "id": instance.id,
                    "url": instance.url,
                    "weight": instance.weight,
                    "healthy": instance.healthy,
                    "active_connections": instance.active_connections,
                    "total_requests": instance.total_requests,
                    "failed_requests": instance.failed_requests,
                    "response_time_avg": instance.response_time_avg,
                    "last_health_check": instance.last_health_check
                }
                for instance in instances
            ]
        }
        
        return stats
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all services."""
        services = set()
        for key in self.instances.keys():
            service_name = key.split(":")[0]
            services.add(service_name)
        
        stats = {}
        for service_name in services:
            stats[service_name] = self.get_instance_stats(service_name)
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the load balancer."""
        try:
            total_instances = len(self.instances)
            healthy_instances = sum(1 for i in self.instances.values() if i.healthy)
            
            return {
                "status": "healthy" if healthy_instances > 0 else "unhealthy",
                "total_instances": total_instances,
                "healthy_instances": healthy_instances,
                "strategy": self.config.strategy.value,
                "services": list(set(key.split(":")[0] for key in self.instances.keys()))
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass 