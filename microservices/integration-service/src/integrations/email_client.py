"""
Email Integration Client

This module provides the Email client for the Integration Service,
handling email sending, templates, and analytics.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

class EmailMessage(BaseModel):
    to: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None

class EmailResult(BaseModel):
    message_id: str
    status: str
    sent_at: datetime
    to: List[str]
    subject: str
    provider: str

class EmailTemplate(BaseModel):
    id: str
    name: str
    subject: str
    html_content: str
    text_content: str
    created_at: datetime
    updated_at: datetime

class EmailClient:
    """Email client for sending emails via SendGrid or Mailgun."""
    
    def __init__(self, provider: str, api_key: str, domain: Optional[str] = None, 
                 from_email: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.domain = domain
        self.from_email = from_email
        self.session: Optional[aiohttp.ClientSession] = None
        
        if self.provider == "sendgrid":
            self.base_url = "https://api.sendgrid.com/v3"
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        elif self.provider == "mailgun":
            self.base_url = f"https://api.mailgun.net/v3/{domain}"
            self.auth = aiohttp.BasicAuth("api", api_key)
        else:
            raise ValueError(f"Unsupported email provider: {provider}")
            
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def send_email(self, message: EmailMessage) -> Optional[EmailResult]:
        """Send an email."""
        if self.provider == "sendgrid":
            return await self._send_sendgrid(message)
        elif self.provider == "mailgun":
            return await self._send_mailgun(message)
        else:
            logger.error(f"Unsupported provider: {self.provider}")
            return None
            
    async def _send_sendgrid(self, message: EmailMessage) -> Optional[EmailResult]:
        """Send email via SendGrid."""
        try:
            payload = {
                "personalizations": [{
                    "to": [{"email": email} for email in message.to]
                }],
                "from": {"email": message.from_email or self.from_email},
                "subject": message.subject,
                "content": []
            }
            
            if message.html_body:
                payload["content"].append({
                    "type": "text/html",
                    "value": message.html_body
                })
            
            payload["content"].append({
                "type": "text/plain",
                "value": message.body
            })
            
            if message.reply_to:
                payload["reply_to"] = {"email": message.reply_to}
                
            url = f"{self.base_url}/mail/send"
            async with self.session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 202:
                    # SendGrid returns 202 for success
                    result = await response.text()
                    return EmailResult(
                        message_id=result,
                        status="sent",
                        sent_at=datetime.now(),
                        to=message.to,
                        subject=message.subject,
                        provider="sendgrid"
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"SendGrid error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            return None
            
    async def _send_mailgun(self, message: EmailMessage) -> Optional[EmailResult]:
        """Send email via Mailgun."""
        try:
            data = {
                "to": ",".join(message.to),
                "subject": message.subject,
                "text": message.body
            }
            
            if message.html_body:
                data["html"] = message.html_body
                
            if message.from_email or self.from_email:
                data["from"] = message.from_email or self.from_email
                
            if message.reply_to:
                data["h:Reply-To"] = message.reply_to
                
            url = f"{self.base_url}/messages"
            async with self.session.post(url, data=data, auth=self.auth) as response:
                if response.status == 200:
                    result = await response.json()
                    return EmailResult(
                        message_id=result["id"],
                        status="sent",
                        sent_at=datetime.now(),
                        to=message.to,
                        subject=message.subject,
                        provider="mailgun"
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"Mailgun error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to send email via Mailgun: {e}")
            return None
            
    async def send_template_email(self, template_id: str, to: List[str], 
                                template_data: Dict[str, Any], 
                                subject: Optional[str] = None) -> Optional[EmailResult]:
        """Send email using a template."""
        if self.provider == "sendgrid":
            return await self._send_sendgrid_template(template_id, to, template_data, subject)
        elif self.provider == "mailgun":
            return await self._send_mailgun_template(template_id, to, template_data, subject)
        else:
            logger.error(f"Template sending not supported for provider: {self.provider}")
            return None
            
    async def _send_sendgrid_template(self, template_id: str, to: List[str], 
                                    template_data: Dict[str, Any], 
                                    subject: Optional[str] = None) -> Optional[EmailResult]:
        """Send template email via SendGrid."""
        try:
            payload = {
                "personalizations": [{
                    "to": [{"email": email} for email in to],
                    "dynamic_template_data": template_data
                }],
                "from": {"email": self.from_email},
                "template_id": template_id
            }
            
            if subject:
                payload["personalizations"][0]["subject"] = subject
                
            url = f"{self.base_url}/mail/send"
            async with self.session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 202:
                    result = await response.text()
                    return EmailResult(
                        message_id=result,
                        status="sent",
                        sent_at=datetime.now(),
                        to=to,
                        subject=subject or "Template Email",
                        provider="sendgrid"
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"SendGrid template error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to send template email via SendGrid: {e}")
            return None
            
    async def _send_mailgun_template(self, template_id: str, to: List[str], 
                                   template_data: Dict[str, Any], 
                                   subject: Optional[str] = None) -> Optional[EmailResult]:
        """Send template email via Mailgun."""
        try:
            data = {
                "to": ",".join(to),
                "template": template_id,
                "h:X-Mailgun-Variables": json.dumps(template_data)
            }
            
            if subject:
                data["subject"] = subject
                
            if self.from_email:
                data["from"] = self.from_email
                
            url = f"{self.base_url}/messages"
            async with self.session.post(url, data=data, auth=self.auth) as response:
                if response.status == 200:
                    result = await response.json()
                    return EmailResult(
                        message_id=result["id"],
                        status="sent",
                        sent_at=datetime.now(),
                        to=to,
                        subject=subject or "Template Email",
                        provider="mailgun"
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"Mailgun template error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to send template email via Mailgun: {e}")
            return None
            
    async def create_template(self, template: EmailTemplate) -> Optional[EmailTemplate]:
        """Create an email template."""
        if self.provider == "sendgrid":
            return await self._create_sendgrid_template(template)
        elif self.provider == "mailgun":
            return await self._create_mailgun_template(template)
        else:
            logger.error(f"Template creation not supported for provider: {self.provider}")
            return None
            
    async def _create_sendgrid_template(self, template: EmailTemplate) -> Optional[EmailTemplate]:
        """Create template via SendGrid."""
        try:
            payload = {
                "name": template.name,
                "generation": "dynamic",
                "html_content": template.html_content,
                "plain_content": template.text_content
            }
            
            url = f"{self.base_url}/templates"
            async with self.session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 201:
                    result = await response.json()
                    return EmailTemplate(
                        id=result["id"],
                        name=template.name,
                        subject=template.subject,
                        html_content=template.html_content,
                        text_content=template.text_content,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"SendGrid template creation error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to create SendGrid template: {e}")
            return None
            
    async def _create_mailgun_template(self, template: EmailTemplate) -> Optional[EmailTemplate]:
        """Create template via Mailgun."""
        try:
            data = {
                "name": template.name,
                "template": template.html_content,
                "tag": template.name.lower().replace(" ", "_")
            }
            
            url = f"{self.base_url}/templates"
            async with self.session.post(url, data=data, auth=self.auth) as response:
                if response.status == 200:
                    result = await response.json()
                    return EmailTemplate(
                        id=result["template"]["name"],
                        name=template.name,
                        subject=template.subject,
                        html_content=template.html_content,
                        text_content=template.text_content,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"Mailgun template creation error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Failed to create Mailgun template: {e}")
            return None
            
    async def get_email_stats(self) -> Dict[str, Any]:
        """Get email sending statistics."""
        if self.provider == "sendgrid":
            return await self._get_sendgrid_stats()
        elif self.provider == "mailgun":
            return await self._get_mailgun_stats()
        else:
            return {"error": f"Stats not supported for provider: {self.provider}"}
            
    async def _get_sendgrid_stats(self) -> Dict[str, Any]:
        """Get SendGrid statistics."""
        try:
            # Get global stats for last 30 days
            url = f"{self.base_url}/stats"
            params = {
                "start_date": (datetime.now().replace(day=1)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            async with self.session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    stats = await response.json()
                    return {
                        "provider": "sendgrid",
                        "stats": stats
                    }
                else:
                    return {"error": f"Failed to get SendGrid stats: {response.status}"}
        except Exception as e:
            return {"error": f"Failed to get SendGrid stats: {e}"}
            
    async def _get_mailgun_stats(self) -> Dict[str, Any]:
        """Get Mailgun statistics."""
        try:
            # Get events for last 30 days
            url = f"{self.base_url}/events"
            params = {
                "begin": (datetime.now().replace(day=1)).strftime("%a, %d %b %Y %H:%M:%S %z"),
                "end": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            }
            
            async with self.session.get(url, params=params, auth=self.auth) as response:
                if response.status == 200:
                    events = await response.json()
                    return {
                        "provider": "mailgun",
                        "events": events
                    }
                else:
                    return {"error": f"Failed to get Mailgun stats: {response.status}"}
        except Exception as e:
            return {"error": f"Failed to get Mailgun stats: {e}"}
            
    async def health_check(self) -> Dict[str, Any]:
        """Check email service health."""
        try:
            # Test API connection
            if self.provider == "sendgrid":
                url = f"{self.base_url}/user/profile"
                async with self.session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        profile = await response.json()
                        return {
                            "status": "healthy",
                            "provider": "sendgrid",
                            "api_key_configured": bool(self.api_key),
                            "from_email": self.from_email,
                            "profile": profile
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "provider": "sendgrid",
                            "error": f"API test failed: {response.status}",
                            "api_key_configured": bool(self.api_key)
                        }
            elif self.provider == "mailgun":
                url = f"{self.base_url}/domains"
                async with self.session.get(url, auth=self.auth) as response:
                    if response.status == 200:
                        domains = await response.json()
                        return {
                            "status": "healthy",
                            "provider": "mailgun",
                            "api_key_configured": bool(self.api_key),
                            "domain": self.domain,
                            "domains": domains
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "provider": "mailgun",
                            "error": f"API test failed: {response.status}",
                            "api_key_configured": bool(self.api_key)
                        }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Unsupported provider: {self.provider}"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider,
                "api_key_configured": bool(self.api_key)
            } 