#!/usr/bin/env python3
"""
Analytics Service voor Notification Service
Advanced reporting en analytics voor delivery performance
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .database import DatabaseService

logger = logging.getLogger(__name__)

class AnalyticsPeriod(str, Enum):
    """Analytics period enum."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class MetricType(str, Enum):
    """Metric type enum."""
    DELIVERY_RATE = "delivery_rate"
    SUCCESS_RATE = "success_rate"
    FAILURE_RATE = "failure_rate"
    RETRY_RATE = "retry_rate"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"

class AnalyticsRequest(BaseModel):
    """Analytics request model."""
    start_date: datetime = Field(..., description="Start date for analytics")
    end_date: datetime = Field(..., description="End date for analytics")
    period: AnalyticsPeriod = Field(default=AnalyticsPeriod.DAY, description="Analytics period")
    channels: Optional[List[str]] = Field(None, description="Filter by channels")
    templates: Optional[List[str]] = Field(None, description="Filter by templates")
    metrics: List[MetricType] = Field(default_factory=list, description="Metrics to calculate")

class AnalyticsResponse(BaseModel):
    """Analytics response model."""
    period: AnalyticsPeriod = Field(..., description="Analytics period")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    metrics: Dict[str, List[Dict[str, Any]]] = Field(..., description="Metrics data")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    generated_at: datetime = Field(..., description="Report generation timestamp")

class PerformanceMetrics(BaseModel):
    """Performance metrics model."""
    total_deliveries: int = Field(..., description="Total number of deliveries")
    successful_deliveries: int = Field(..., description="Number of successful deliveries")
    failed_deliveries: int = Field(..., description="Number of failed deliveries")
    delivery_rate: float = Field(..., description="Delivery success rate")
    average_response_time: float = Field(..., description="Average response time in seconds")
    throughput_per_hour: float = Field(..., description="Deliveries per hour")
    retry_rate: float = Field(..., description="Retry rate percentage")

class ChannelPerformance(BaseModel):
    """Channel performance model."""
    channel: str = Field(..., description="Channel name")
    total_deliveries: int = Field(..., description="Total deliveries")
    successful_deliveries: int = Field(..., description="Successful deliveries")
    failed_deliveries: int = Field(..., description="Failed deliveries")
    delivery_rate: float = Field(..., description="Delivery success rate")
    average_response_time: float = Field(..., description="Average response time")
    error_breakdown: Dict[str, int] = Field(..., description="Error type breakdown")

class TemplatePerformance(BaseModel):
    """Template performance model."""
    template_id: str = Field(..., description="Template ID")
    template_name: str = Field(..., description="Template name")
    total_uses: int = Field(..., description="Total template uses")
    successful_uses: int = Field(..., description="Successful uses")
    failed_uses: int = Field(..., description="Failed uses")
    success_rate: float = Field(..., description="Success rate")
    average_rendering_time: float = Field(..., description="Average rendering time")

class AnalyticsService:
    """Advanced analytics and reporting service."""
    
    def __init__(self, db_service: DatabaseService):
        """Initialize analytics service."""
        self.db_service = db_service
        logger.info("Analytics Service initialized")
    
    async def generate_analytics_report(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """Generate comprehensive analytics report."""
        try:
            logger.info(f"Generating analytics report: {request.start_date} to {request.end_date}")
            
            # Calculate metrics
            metrics_data = {}
            for metric in request.metrics:
                metrics_data[metric.value] = await self._calculate_metric(
                    metric, request.start_date, request.end_date, request.period,
                    request.channels, request.templates
                )
            
            # Generate summary
            summary = await self._generate_summary(
                request.start_date, request.end_date, request.channels, request.templates
            )
            
            response = AnalyticsResponse(
                period=request.period,
                start_date=request.start_date,
                end_date=request.end_date,
                metrics=metrics_data,
                summary=summary,
                generated_at=datetime.utcnow()
            )
            
            logger.info("Analytics report generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {str(e)}")
            raise
    
    async def get_performance_metrics(self, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> PerformanceMetrics:
        """Get overall performance metrics."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get delivery statistics
            stats = await self.db_service.get_delivery_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            total_deliveries = stats.get("total_deliveries", 0)
            successful_deliveries = stats.get("successful_deliveries", 0)
            failed_deliveries = stats.get("failed_deliveries", 0)
            
            # Calculate metrics
            delivery_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            average_response_time = stats.get("average_response_time", 0)
            throughput_per_hour = stats.get("throughput_per_hour", 0)
            retry_rate = stats.get("retry_rate", 0)
            
            return PerformanceMetrics(
                total_deliveries=total_deliveries,
                successful_deliveries=successful_deliveries,
                failed_deliveries=failed_deliveries,
                delivery_rate=delivery_rate,
                average_response_time=average_response_time,
                throughput_per_hour=throughput_per_hour,
                retry_rate=retry_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            return PerformanceMetrics(
                total_deliveries=0,
                successful_deliveries=0,
                failed_deliveries=0,
                delivery_rate=0.0,
                average_response_time=0.0,
                throughput_per_hour=0.0,
                retry_rate=0.0
            )
    
    async def get_channel_performance(self, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[ChannelPerformance]:
        """Get performance metrics by channel."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get channel statistics
            channel_stats = await self.db_service.get_channel_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            channel_performance = []
            for channel, stats in channel_stats.items():
                total_deliveries = stats.get("total_deliveries", 0)
                successful_deliveries = stats.get("successful_deliveries", 0)
                failed_deliveries = stats.get("failed_deliveries", 0)
                
                delivery_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
                average_response_time = stats.get("average_response_time", 0)
                error_breakdown = stats.get("error_breakdown", {})
                
                channel_performance.append(ChannelPerformance(
                    channel=channel,
                    total_deliveries=total_deliveries,
                    successful_deliveries=successful_deliveries,
                    failed_deliveries=failed_deliveries,
                    delivery_rate=delivery_rate,
                    average_response_time=average_response_time,
                    error_breakdown=error_breakdown
                ))
            
            return channel_performance
            
        except Exception as e:
            logger.error(f"Failed to get channel performance: {str(e)}")
            return []
    
    async def get_template_performance(self, 
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> List[TemplatePerformance]:
        """Get performance metrics by template."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get template statistics
            template_stats = await self.db_service.get_template_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            template_performance = []
            for template_id, stats in template_stats.items():
                total_uses = stats.get("total_uses", 0)
                successful_uses = stats.get("successful_uses", 0)
                failed_uses = stats.get("failed_uses", 0)
                
                success_rate = (successful_uses / total_uses * 100) if total_uses > 0 else 0
                average_rendering_time = stats.get("average_rendering_time", 0)
                template_name = stats.get("template_name", template_id)
                
                template_performance.append(TemplatePerformance(
                    template_id=template_id,
                    template_name=template_name,
                    total_uses=total_uses,
                    successful_uses=successful_uses,
                    failed_uses=failed_uses,
                    success_rate=success_rate,
                    average_rendering_time=average_rendering_time
                ))
            
            return template_performance
            
        except Exception as e:
            logger.error(f"Failed to get template performance: {str(e)}")
            return []
    
    async def get_trend_analysis(self, 
                               metric: MetricType,
                               days: int = 30,
                               channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trend analysis for a specific metric."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get trend data
            trend_data = await self.db_service.get_trend_data(
                metric=metric.value,
                start_date=start_date,
                end_date=end_date,
                channel=channel
            )
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Failed to get trend analysis: {str(e)}")
            return []
    
    async def get_error_analysis(self, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get error analysis and breakdown."""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get error statistics
            error_stats = await self.db_service.get_error_statistics(
                start_date=start_date,
                end_date=end_date
            )
            
            return error_stats
            
        except Exception as e:
            logger.error(f"Failed to get error analysis: {str(e)}")
            return {}
    
    async def _calculate_metric(self, 
                              metric: MetricType,
                              start_date: datetime,
                              end_date: datetime,
                              period: AnalyticsPeriod,
                              channels: Optional[List[str]] = None,
                              templates: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Calculate specific metric over time period."""
        try:
            # Get metric data from database
            metric_data = await self.db_service.get_metric_data(
                metric=metric.value,
                start_date=start_date,
                end_date=end_date,
                period=period.value,
                channels=channels,
                templates=templates
            )
            
            return metric_data
            
        except Exception as e:
            logger.error(f"Failed to calculate metric {metric.value}: {str(e)}")
            return []
    
    async def _generate_summary(self, 
                              start_date: datetime,
                              end_date: datetime,
                              channels: Optional[List[str]] = None,
                              templates: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate summary statistics."""
        try:
            # Get overall statistics
            stats = await self.db_service.get_delivery_statistics(
                start_date=start_date,
                end_date=end_date,
                channels=channels,
                templates=templates
            )
            
            # Calculate summary metrics
            total_deliveries = stats.get("total_deliveries", 0)
            successful_deliveries = stats.get("successful_deliveries", 0)
            failed_deliveries = stats.get("failed_deliveries", 0)
            
            summary = {
                "total_deliveries": total_deliveries,
                "successful_deliveries": successful_deliveries,
                "failed_deliveries": failed_deliveries,
                "delivery_rate": (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
                "average_response_time": stats.get("average_response_time", 0),
                "throughput_per_hour": stats.get("throughput_per_hour", 0),
                "retry_rate": stats.get("retry_rate", 0),
                "top_channels": stats.get("top_channels", []),
                "top_templates": stats.get("top_templates", []),
                "error_breakdown": stats.get("error_breakdown", {})
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return {} 