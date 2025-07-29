"""
Webhook notification module for BMAD.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

def get_webhook_status() -> Dict[str, Any]:
    """Get webhook connection status."""
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        return {"status": "not_configured", "error": "WEBHOOK_URL not set"}
    
    try:
        response = requests.get(webhook_url, timeout=5)
        return {
            "status": "connected" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "url": webhook_url
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "url": webhook_url}

def test_webhook_connection() -> bool:
    """Test webhook connection."""
    status = get_webhook_status()
    return status.get("status") == "connected"

def send_webhook_message(text: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a webhook message."""
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        logger.error("WEBHOOK_URL not configured")
        return False
    
    try:
        payload = {
            "text": text,
            "channel": channel,
            **kwargs
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Webhook message sent successfully to {channel or 'default'}")
        return True
    except Exception as e:
        logger.error(f"Failed to send webhook message: {e}")
        return False

def send_webhook_hitl_alert(reason: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a Human-in-the-Loop alert via webhook."""
    text = f"🚨 **Human-in-the-Loop Required**: {reason}"
    return send_webhook_message(text, channel=channel, **kwargs)

def send_webhook_workflow_notification(workflow_name: str, status: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a workflow notification via webhook."""
    text = f"🔄 **Workflow Update**: {workflow_name} - {status}"
    return send_webhook_message(text, channel=channel, **kwargs)

def send_webhook_error_notification(error_message: str, context: Optional[str] = None, channel: Optional[str] = None, **kwargs) -> bool:
    """Send an error notification via webhook."""
    text = f"❌ **Error**: {error_message}"
    if context:
        text += f" (Context: {context})"
    return send_webhook_message(text, channel=channel, **kwargs)

def send_webhook_success_notification(success_message: str, context: Optional[str] = None, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a success notification via webhook."""
    text = f"✅ **Success**: {success_message}"
    if context:
        text += f" (Context: {context})"
    return send_webhook_message(text, channel=channel, **kwargs)

def send_webhook_deployment_notification(deployment_name: str, status: str, environment: Optional[str] = None, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a deployment notification via webhook."""
    text = f"🚀 **Deployment**: {deployment_name} - {status}"
    if environment:
        text += f" (Environment: {environment})"
    return send_webhook_message(text, channel=channel, **kwargs) 