#!/usr/bin/env python3
"""
Main FastAPI Application voor Notification Service
API endpoints voor notification delivery en management
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .core.database import DatabaseService
from .core.template import TemplateService
from .core.email import EmailService
from .core.sms import SMSService
from .core.slack import SlackService
from .core.webhook import WebhookService
from .core.delivery import DeliveryService, DeliveryRequest, BulkDeliveryRequest
from .core.analytics import AnalyticsService, AnalyticsRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
db_service: DatabaseService = None
delivery_service: DeliveryService = None
analytics_service: AnalyticsService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global db_service, delivery_service, analytics_service
    
    # Startup
    logger.info("Starting Notification Service...")
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        await db_service.initialize()
        logger.info("Database service initialized")
        
        # Initialize delivery service
        delivery_service = DeliveryService(db_service)
        logger.info("Delivery service initialized")
        
        # Initialize analytics service
        analytics_service = AnalyticsService(db_service)
        logger.info("Analytics service initialized")
        
        logger.info("Notification Service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start Notification Service: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notification Service...")
    if db_service:
        await db_service.close()
    logger.info("Notification Service shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Multi-channel notification delivery service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
async def get_db_service() -> DatabaseService:
    """Get database service dependency."""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    return db_service

async def get_delivery_service() -> DeliveryService:
    """Get delivery service dependency."""
    if not delivery_service:
        raise HTTPException(status_code=503, detail="Delivery service not available")
    return delivery_service

async def get_analytics_service() -> AnalyticsService:
    """Get analytics service dependency."""
    if not analytics_service:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    return analytics_service

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "notification-service"}

@app.get("/health/ready")
async def readiness_check():
    """Readiness check."""
    try:
        if db_service:
            await db_service.check_connection()
            return {"status": "ready", "service": "notification-service"}
        else:
            return {"status": "not ready", "service": "notification-service", "error": "Database service not available"}
    except Exception as e:
        return {"status": "not ready", "service": "notification-service", "error": str(e)}

@app.get("/health/live")
async def liveness_check():
    """Liveness check."""
    return {"status": "alive", "service": "notification-service"}

# Template management endpoints
@app.post("/templates")
async def create_template(
    template_data: Dict[str, Any],
    db: DatabaseService = Depends(get_db_service)
):
    """Create a new notification template."""
    try:
        template_service = TemplateService(db)
        template_id = await template_service.create_template(template_data)
        return {"template_id": template_id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    db: DatabaseService = Depends(get_db_service)
):
    """Get a notification template."""
    try:
        template_service = TemplateService(db)
        template = await template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    template_data: Dict[str, Any],
    db: DatabaseService = Depends(get_db_service)
):
    """Update a notification template."""
    try:
        template_service = TemplateService(db)
        await template_service.update_template(template_id, template_data)
        return {"template_id": template_id, "status": "updated"}
    except Exception as e:
        logger.error(f"Failed to update template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    db: DatabaseService = Depends(get_db_service)
):
    """Delete a notification template."""
    try:
        template_service = TemplateService(db)
        await template_service.delete_template(template_id)
        return {"template_id": template_id, "status": "deleted"}
    except Exception as e:
        logger.error(f"Failed to delete template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/templates")
async def list_templates(
    db: DatabaseService = Depends(get_db_service)
):
    """List all notification templates."""
    try:
        template_service = TemplateService(db)
        templates = await template_service.list_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Delivery endpoints
@app.post("/deliver")
async def deliver_notification(
    request: DeliveryRequest,
    delivery: DeliveryService = Depends(get_delivery_service)
):
    """Deliver a single notification."""
    try:
        result = await delivery.deliver_notification(request)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to deliver notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deliver/bulk")
async def deliver_bulk_notifications(
    request: BulkDeliveryRequest,
    background_tasks: BackgroundTasks,
    delivery: DeliveryService = Depends(get_delivery_service)
):
    """Deliver notifications in bulk."""
    try:
        # For large bulk deliveries, process in background
        if len(request.recipients) > 1000:
            background_tasks.add_task(delivery.deliver_bulk_notifications, request)
            return {"status": "processing", "message": "Bulk delivery started in background"}
        else:
            result = await delivery.deliver_bulk_notifications(request)
            return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to deliver bulk notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deliveries/{delivery_id}")
async def get_delivery_status(
    delivery_id: str,
    delivery: DeliveryService = Depends(get_delivery_service)
):
    """Get delivery status."""
    try:
        status = await delivery.get_delivery_status(delivery_id)
        if not status:
            raise HTTPException(status_code=404, detail="Delivery not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get delivery status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deliveries/retry")
async def retry_failed_deliveries(
    max_retries: int = 3,
    delivery: DeliveryService = Depends(get_delivery_service)
):
    """Retry failed deliveries."""
    try:
        result = await delivery.retry_failed_deliveries(max_retries)
        return result
    except Exception as e:
        logger.error(f"Failed to retry deliveries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.post("/analytics/report")
async def generate_analytics_report(
    request: AnalyticsRequest,
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Generate analytics report."""
    try:
        report = await analytics.generate_analytics_report(request)
        return report
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/performance")
async def get_performance_metrics(
    start_date: str = None,
    end_date: str = None,
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get performance metrics."""
    try:
        from datetime import datetime
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        metrics = await analytics.get_performance_metrics(start, end)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/channels")
async def get_channel_performance(
    start_date: str = None,
    end_date: str = None,
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get channel performance metrics."""
    try:
        from datetime import datetime
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        performance = await analytics.get_channel_performance(start, end)
        return {"channels": performance}
    except Exception as e:
        logger.error(f"Failed to get channel performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/templates")
async def get_template_performance(
    start_date: str = None,
    end_date: str = None,
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get template performance metrics."""
    try:
        from datetime import datetime
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        performance = await analytics.get_template_performance(start, end)
        return {"templates": performance}
    except Exception as e:
        logger.error(f"Failed to get template performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/trends/{metric}")
async def get_trend_analysis(
    metric: str,
    days: int = 30,
    channel: str = None,
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get trend analysis for a specific metric."""
    try:
        from .core.analytics import MetricType
        metric_type = MetricType(metric)
        
        trends = await analytics.get_trend_analysis(metric_type, days, channel)
        return {"trends": trends}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid metric: {metric}")
    except Exception as e:
        logger.error(f"Failed to get trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/errors")
async def get_error_analysis(
    start_date: str = None,
    end_date: str = None,
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """Get error analysis."""
    try:
        from datetime import datetime
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        errors = await analytics.get_error_analysis(start, end)
        return errors
    except Exception as e:
        logger.error(f"Failed to get error analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Channel-specific endpoints
@app.post("/channels/email/test")
async def test_email_channel(
    test_data: Dict[str, Any],
    db: DatabaseService = Depends(get_db_service)
):
    """Test email channel configuration."""
    try:
        email_service = EmailService(db)
        result = await email_service.test_connection(test_data)
        return result
    except Exception as e:
        logger.error(f"Failed to test email channel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/channels/sms/test")
async def test_sms_channel(
    test_data: Dict[str, Any],
    db: DatabaseService = Depends(get_db_service)
):
    """Test SMS channel configuration."""
    try:
        sms_service = SMSService(db)
        result = await sms_service.test_connection(test_data)
        return result
    except Exception as e:
        logger.error(f"Failed to test SMS channel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/channels/slack/test")
async def test_slack_channel(
    test_data: Dict[str, Any],
    db: DatabaseService = Depends(get_db_service)
):
    """Test Slack channel configuration."""
    try:
        slack_service = SlackService(db)
        result = await slack_service.test_connection(test_data)
        return result
    except Exception as e:
        logger.error(f"Failed to test Slack channel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/channels/webhook/test")
async def test_webhook_channel(
    test_data: Dict[str, Any],
    db: DatabaseService = Depends(get_db_service)
):
    """Test webhook channel configuration."""
    try:
        webhook_service = WebhookService(db)
        result = await webhook_service.test_connection(test_data)
        return result
    except Exception as e:
        logger.error(f"Failed to test webhook channel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handling
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("NOTIFICATION_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("NOTIFICATION_SERVICE_PORT", "8003"))
    reload = os.getenv("NOTIFICATION_SERVICE_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting Notification Service on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 