"""
Slack notification module for BMAD.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

def send_slack_message(text: str, channel: Optional[str] = None, use_api: bool = False, **kwargs) -> bool:
    """Send a Slack message."""
    if use_api:
        return _send_slack_api_message(text, channel, **kwargs)
    else:
        return _send_slack_webhook_message(text, channel, **kwargs)

def _send_slack_webhook_message(text: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a Slack message via webhook."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL not configured")
        return False
    
    try:
        payload = {
            "text": text,
            "channel": channel,
            **kwargs
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Slack webhook message sent successfully to {channel or 'default'}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack webhook message: {e}")
        return False

def _send_slack_api_message(text: str, channel: Optional[str] = None, **kwargs) -> bool:
    """Send a Slack message via API."""
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        logger.error("SLACK_BOT_TOKEN not configured")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel or "#general",
            "text": text,
            **kwargs
        }
        
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            logger.info(f"Slack API message sent successfully to {channel or 'default'}")
            return True
        else:
            logger.error(f"Slack API error: {result.get('error')}")
            return False
    except Exception as e:
        logger.error(f"Failed to send Slack API message: {e}")
        return False

def send_human_in_loop_alert(reason: str, channel: Optional[str] = None, use_api: bool = False, **kwargs) -> bool:
    """Send a Human-in-the-Loop alert via Slack."""
    text = f"🚨 **Human-in-the-Loop Required**: {reason}"
    return send_slack_message(text, channel=channel, use_api=use_api, **kwargs) 