"""
Analytics Manager

This module provides analytics management functionality for the Context Service,
handling metrics collection, analysis, and reporting.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import json
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AnalyticsEvent(BaseModel):
    """Analytics event model."""
    event_type: str
    context_id: Optional[str] = None
    layer_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AnalyticsMetrics(BaseModel):
    """Analytics metrics model."""
    total_contexts: int = 0
    total_layers: int = 0
    total_size_mb: float = 0.0
    average_context_size_mb: float = 0.0
    average_layers_per_context: float = 0.0
    context_types_distribution: Dict[str, int] = Field(default_factory=dict)
    status_distribution: Dict[str, int] = Field(default_factory=dict)
    access_patterns: Dict[str, int] = Field(default_factory=dict)

class AnalyticsManager:
    """Manages analytics collection and analysis."""
    
    def __init__(self, store=None):
        self.store = store
        self.events: List[AnalyticsEvent] = []
        self.metrics_cache: Optional[AnalyticsMetrics] = None
        self.last_update: Optional[datetime] = None
        
    async def record_event(self, event_type: str, context_id: Optional[str] = None,
                          layer_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record an analytics event."""
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                context_id=context_id,
                layer_id=layer_id,
                metadata=metadata or {}
            )
            
            self.events.append(event)
            
            # Invalidate cache
            self.metrics_cache = None
            
            logger.debug(f"Recorded analytics event: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to record analytics event: {e}")
            
    async def get_metrics(self, force_refresh: bool = False) -> AnalyticsMetrics:
        """Get current analytics metrics."""
        try:
            # Return cached metrics if available and not stale
            if (not force_refresh and self.metrics_cache and self.last_update and 
                datetime.now(timezone.utc) - self.last_update < timedelta(minutes=5)):
                return self.metrics_cache
                
            # Calculate metrics from store
            if self.store:
                contexts = await self.store.list_contexts()
            else:
                contexts = []
                
            metrics = AnalyticsMetrics()
            
            if contexts:
                metrics.total_contexts = len(contexts)
                metrics.total_layers = sum(c.layer_count for c in contexts)
                metrics.total_size_mb = sum(c.size_mb for c in contexts)
                metrics.average_context_size_mb = metrics.total_size_mb / metrics.total_contexts
                metrics.average_layers_per_context = metrics.total_layers / metrics.total_contexts
                
                # Calculate distributions
                for context in contexts:
                    # Type distribution
                    metrics.context_types_distribution[context.type] = (
                        metrics.context_types_distribution.get(context.type, 0) + 1
                    )
                    
                    # Status distribution
                    metrics.status_distribution[context.status] = (
                        metrics.status_distribution.get(context.status, 0) + 1
                    )
                    
            # Cache the results
            self.metrics_cache = metrics
            self.last_update = datetime.now(timezone.utc)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get analytics metrics: {e}")
            return AnalyticsMetrics()
            
    async def get_usage_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get usage trends over time."""
        try:
            # Filter events by time range
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            recent_events = [e for e in self.events if e.timestamp >= cutoff_time]
            
            # Group events by day
            daily_events = {}
            for event in recent_events:
                day_key = event.timestamp.date().isoformat()
                if day_key not in daily_events:
                    daily_events[day_key] = []
                daily_events[day_key].append(event)
                
            # Calculate daily metrics
            trends = {
                "period_days": days,
                "total_events": len(recent_events),
                "daily_events": {},
                "event_types": {},
                "context_activity": {}
            }
            
            for day, events in daily_events.items():
                trends["daily_events"][day] = len(events)
                
                # Count event types
                for event in events:
                    trends["event_types"][event.event_type] = (
                        trends["event_types"].get(event.event_type, 0) + 1
                    )
                    
                    # Count context activity
                    if event.context_id:
                        trends["context_activity"][event.context_id] = (
                            trends["context_activity"].get(event.context_id, 0) + 1
                        )
                        
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get usage trends: {e}")
            return {"error": str(e)}
            
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        try:
            metrics = await self.get_metrics()
            
            # Calculate performance indicators
            performance = {
                "context_efficiency": {
                    "average_size_mb": metrics.average_context_size_mb,
                    "average_layers": metrics.average_layers_per_context,
                    "size_distribution": self._calculate_size_distribution(),
                    "layer_distribution": self._calculate_layer_distribution()
                },
                "usage_patterns": {
                    "most_active_contexts": await self._get_most_active_contexts(),
                    "context_type_popularity": metrics.context_types_distribution,
                    "status_health": metrics.status_distribution
                },
                "storage_efficiency": {
                    "total_storage_mb": metrics.total_size_mb,
                    "storage_per_context": metrics.average_context_size_mb,
                    "storage_utilization": await self._calculate_storage_utilization()
                }
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
            
    def _calculate_size_distribution(self) -> Dict[str, int]:
        """Calculate context size distribution."""
        if not self.metrics_cache:
            return {}
            
        # This would need access to individual context sizes
        # For now, return empty distribution
        return {
            "small": 0,    # < 1MB
            "medium": 0,   # 1-10MB
            "large": 0,    # 10-50MB
            "xlarge": 0    # > 50MB
        }
        
    def _calculate_layer_distribution(self) -> Dict[str, int]:
        """Calculate layer count distribution."""
        if not self.metrics_cache:
            return {}
            
        # This would need access to individual context layer counts
        # For now, return empty distribution
        return {
            "single": 0,   # 1 layer
            "few": 0,      # 2-5 layers
            "many": 0,     # 6-20 layers
            "complex": 0   # > 20 layers
        }
        
    async def _get_most_active_contexts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most active contexts based on access patterns."""
        try:
            if self.store:
                contexts = await self.store.list_contexts()
            else:
                contexts = []
                
            # Sort by access count
            active_contexts = sorted(
                contexts,
                key=lambda c: c.access_count,
                reverse=True
            )[:limit]
            
            return [
                {
                    "context_id": c.id,
                    "name": c.name,
                    "access_count": c.access_count,
                    "last_updated": c.updated_at.isoformat()
                }
                for c in active_contexts
            ]
            
        except Exception as e:
            logger.error(f"Failed to get most active contexts: {e}")
            return []
            
    async def _calculate_storage_utilization(self) -> float:
        """Calculate storage utilization percentage."""
        try:
            # This would compare actual storage used vs allocated
            # For now, return a placeholder
            return 75.5  # 75.5% utilization
            
        except Exception as e:
            logger.error(f"Failed to calculate storage utilization: {e}")
            return 0.0
            
    async def generate_report(self, report_type: str = "summary") -> Dict[str, Any]:
        """Generate analytics report."""
        try:
            metrics = await self.get_metrics()
            trends = await self.get_usage_trends()
            performance = await self.get_performance_metrics()
            
            report = {
                "report_type": report_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "metrics": metrics.dict(),
                "trends": trends,
                "performance": performance,
                "summary": {
                    "total_contexts": metrics.total_contexts,
                    "total_layers": metrics.total_layers,
                    "total_storage_mb": metrics.total_size_mb,
                    "average_context_size_mb": metrics.average_context_size_mb
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            return {"error": str(e)}
            
    async def cleanup_old_events(self, max_age_days: int = 30) -> int:
        """Clean up old analytics events."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=max_age_days)
            initial_count = len(self.events)
            
            # Remove old events
            self.events = [e for e in self.events if e.timestamp >= cutoff_time]
            
            removed_count = initial_count - len(self.events)
            logger.info(f"Cleaned up {removed_count} old analytics events")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0
            
    async def health_check(self) -> Dict[str, Any]:
        """Check analytics manager health."""
        try:
            metrics = await self.get_metrics()
            
            return {
                "status": "healthy",
                "total_events": len(self.events),
                "metrics_cache_valid": self.metrics_cache is not None,
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "total_contexts_tracked": metrics.total_contexts
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "total_events": len(self.events)
            } 