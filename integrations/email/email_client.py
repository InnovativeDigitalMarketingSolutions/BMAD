"""
Email Service Integration Client

Provides comprehensive email integration for BMAD including:
- SendGrid and Mailgun support
- Email templates with dynamic content
- Email tracking and analytics
- Bounce handling and spam protection
- Multi-tenant email management
"""

import os
import logging
import time
import json
import base64
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from contextlib import contextmanager
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """Email service configuration settings."""
    provider: str = "sendgrid"  # "sendgrid" or "mailgun"
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    domain: Optional[str] = None
    from_email: str = "noreply@bmad.com"
    from_name: str = "BMAD System"
    reply_to: Optional[str] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    enable_tracking: bool = True
    enable_analytics: bool = True

@dataclass
class EmailTemplate:
    """Email template with dynamic content support."""
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: List[str] = None
    category: str = "general"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class EmailRecipient:
    """Email recipient with optional personalization."""
    email: str
    name: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

@dataclass
class EmailResult:
    """Email sending result with tracking information."""
    message_id: str
    status: str
    sent_at: datetime
    recipient: str
    template_id: Optional[str] = None
    tracking_id: Optional[str] = None
    delivery_status: Optional[str] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    bounce_reason: Optional[str] = None

@dataclass
class EmailAnalytics:
    """Email analytics and performance metrics."""
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_bounced: int = 0
    total_spam_reports: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    spam_report_rate: float = 0.0
    average_delivery_time: float = 0.0
    last_sent: Optional[datetime] = None

class EmailClient:
    """Comprehensive email client with multiple provider support."""
    
    def __init__(self, config: EmailConfig):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests is required for email integration. Install with: pip install requests")
        
        self.config = config
        self.analytics = EmailAnalytics()
        self.templates: Dict[str, EmailTemplate] = {}
        self._initialize_provider()
        logger.info(f"Email client initialized with provider: {config.provider}")
    
    def _initialize_provider(self):
        """Initialize email provider configuration."""
        if self.config.provider == "sendgrid":
            if not self.config.api_key:
                self.config.api_key = os.getenv("SENDGRID_API_KEY")
            if not self.config.api_url:
                self.config.api_url = "https://api.sendgrid.com/v3"
        elif self.config.provider == "mailgun":
            if not self.config.api_key:
                self.config.api_key = os.getenv("MAILGUN_API_KEY")
            if not self.config.api_url:
                self.config.api_url = f"https://api.mailgun.net/v3/{self.config.domain}"
            if not self.config.domain:
                self.config.domain = os.getenv("MAILGUN_DOMAIN")
        else:
            raise ValueError(f"Unsupported email provider: {self.config.provider}")
        
        if not self.config.api_key:
            raise ValueError(f"API key required for {self.config.provider}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to email provider API."""
        try:
            url = f"{self.config.api_url}{endpoint}"
            headers = self._get_headers()
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params if params else None,
                timeout=self.config.timeout
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                return {"success": True, "data": response.json() if response.content else {}}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Email API request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        if self.config.provider == "sendgrid":
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        elif self.config.provider == "mailgun":
            return {
                "Authorization": f"Basic {base64.b64encode(f'api:{self.config.api_key}'.encode()).decode()}"
            }
        return {}
    
    # Template Management
    def create_template(self, template: EmailTemplate) -> Dict[str, Any]:
        """Create an email template."""
        try:
            if self.config.provider == "sendgrid":
                data = {
                    "name": template.name,
                    "generation": "dynamic",
                    "html_content": template.html_content,
                    "subject": template.subject
                }
                if template.text_content:
                    data["plain_content"] = template.text_content
                
                result = self._make_request("POST", "/templates", data)
                if result["success"]:
                    template.template_id = result["data"]["id"]
                    template.created_at = datetime.now(UTC)
                    self.templates[template.template_id] = template
                    logger.info(f"Template created: {template.name}")
                
                return result
                
            elif self.config.provider == "mailgun":
                # Mailgun uses stored templates
                template.created_at = datetime.now(UTC)
                self.templates[template.template_id] = template
                logger.info(f"Template stored: {template.name}")
                return {"success": True, "template_id": template.template_id}
                
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return {"success": False, "error": str(e)}
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get an email template."""
        try:
            if template_id in self.templates:
                template = self.templates[template_id]
                return {"success": True, "template": template}
            
            if self.config.provider == "sendgrid":
                result = self._make_request("GET", f"/templates/{template_id}")
                if result["success"]:
                    data = result["data"]
                    template = EmailTemplate(
                        template_id=data["id"],
                        name=data["name"],
                        subject=data["subject"],
                        html_content=data["html_content"],
                        text_content=data.get("plain_content"),
                        created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                        updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
                    )
                    self.templates[template_id] = template
                    return {"success": True, "template": template}
                
                return result
                
            elif self.config.provider == "mailgun":
                # Mailgun templates are stored locally
                return {"success": False, "error": "Template not found"}
                
        except Exception as e:
            logger.error(f"Failed to get template: {e}")
            return {"success": False, "error": str(e)}
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an email template."""
        try:
            if template_id not in self.templates:
                return {"success": False, "error": "Template not found"}
            
            template = self.templates[template_id]
            
            if self.config.provider == "sendgrid":
                data = {}
                if "name" in updates:
                    data["name"] = updates["name"]
                if "html_content" in updates:
                    data["html_content"] = updates["html_content"]
                if "subject" in updates:
                    data["subject"] = updates["subject"]
                if "text_content" in updates:
                    data["plain_content"] = updates["text_content"]
                
                result = self._make_request("PATCH", f"/templates/{template_id}", data)
                if result["success"]:
                    # Update local template
                    for key, value in updates.items():
                        setattr(template, key, value)
                    template.updated_at = datetime.now(UTC)
                    logger.info(f"Template updated: {template.name}")
                
                return result
                
            elif self.config.provider == "mailgun":
                # Update local template
                for key, value in updates.items():
                    setattr(template, key, value)
                template.updated_at = datetime.now(UTC)
                logger.info(f"Template updated: {template.name}")
                return {"success": True, "template": template}
                
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete an email template."""
        try:
            if self.config.provider == "sendgrid":
                result = self._make_request("DELETE", f"/templates/{template_id}")
                if result["success"]:
                    if template_id in self.templates:
                        del self.templates[template_id]
                    logger.info(f"Template deleted: {template_id}")
                
                return result
                
            elif self.config.provider == "mailgun":
                if template_id in self.templates:
                    del self.templates[template_id]
                    logger.info(f"Template deleted: {template_id}")
                    return {"success": True}
                else:
                    return {"success": False, "error": "Template not found"}
                    
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return {"success": False, "error": str(e)}
    
    # Email Sending
    def send_email(self, to_emails: List[str], subject: str, html_content: str,
                   text_content: Optional[str] = None, from_email: Optional[str] = None,
                   from_name: Optional[str] = None, reply_to: Optional[str] = None,
                   template_id: Optional[str] = None, template_variables: Optional[Dict[str, Any]] = None,
                   category: Optional[str] = None) -> Dict[str, Any]:
        """Send an email."""
        try:
            from_email = from_email or self.config.from_email
            from_name = from_name or self.config.from_name
            reply_to = reply_to or self.config.reply_to
            
            if self.config.provider == "sendgrid":
                data = {
                    "personalizations": [{
                        "to": [{"email": email} for email in to_emails],
                        "subject": subject
                    }],
                    "from": {
                        "email": from_email,
                        "name": from_name
                    },
                    "content": [{
                        "type": "text/html",
                        "value": html_content
                    }]
                }
                
                if text_content:
                    data["content"].append({
                        "type": "text/plain",
                        "value": text_content
                    })
                
                if reply_to:
                    data["reply_to"] = {"email": reply_to}
                
                if template_id:
                    data["template_id"] = template_id
                    if template_variables:
                        data["personalizations"][0]["dynamic_template_data"] = template_variables
                
                if category:
                    data["categories"] = [category]
                
                if self.config.enable_tracking:
                    data["tracking_settings"] = {
                        "click_tracking": {"enable": True, "enable_text": True},
                        "open_tracking": {"enable": True},
                        "subscription_tracking": {"enable": True}
                    }
                
                result = self._make_request("POST", "/mail/send", data)
                if result["success"]:
                    self._update_analytics("sent", len(to_emails))
                    logger.info(f"Email sent to {len(to_emails)} recipients")
                
                return result
                
            elif self.config.provider == "mailgun":
                data = {
                    "from": f"{from_name} <{from_email}>",
                    "to": to_emails,
                    "subject": subject,
                    "html": html_content
                }
                
                if text_content:
                    data["text"] = text_content
                
                if reply_to:
                    data["h:Reply-To"] = reply_to
                
                if template_id and template_id in self.templates:
                    template = self.templates[template_id]
                    if template_variables:
                        for key, value in template_variables.items():
                            data[f"v:{key}"] = str(value)
                
                if category:
                    data["o:tag"] = category
                
                if self.config.enable_tracking:
                    data["o:tracking"] = "yes"
                    data["o:tracking-opens"] = "yes"
                    data["o:tracking-clicks"] = "yes"
                
                result = self._make_request("POST", "/messages", data)
                if result["success"]:
                    self._update_analytics("sent", len(to_emails))
                    logger.info(f"Email sent to {len(to_emails)} recipients")
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}
    
    def send_template_email(self, template_id: str, to_emails: List[str],
                           template_variables: Optional[Dict[str, Any]] = None,
                           from_email: Optional[str] = None, from_name: Optional[str] = None,
                           category: Optional[str] = None) -> Dict[str, Any]:
        """Send an email using a template."""
        try:
            template = self.get_template(template_id)
            if not template["success"]:
                return template
            
            template_obj = template["template"]
            
            # Replace variables in content
            html_content = template_obj.html_content
            text_content = template_obj.text_content
            subject = template_obj.subject
            
            if template_variables:
                for key, value in template_variables.items():
                    placeholder = f"{{{{{key}}}}}"
                    html_content = html_content.replace(placeholder, str(value))
                    if text_content:
                        text_content = text_content.replace(placeholder, str(value))
                    subject = subject.replace(placeholder, str(value))
            
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=from_email,
                from_name=from_name,
                category=category
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return {"success": False, "error": str(e)}
    
    # Bounce Handling
    def get_bounces(self, limit: int = 100) -> Dict[str, Any]:
        """Get bounce information."""
        try:
            if self.config.provider == "sendgrid":
                result = self._make_request("GET", f"/suppression/bounces?limit={limit}")
                if result["success"]:
                    bounces = []
                    for bounce in result["data"]:
                        bounces.append({
                            "email": bounce["email"],
                            "reason": bounce["reason"],
                            "bounced_at": datetime.fromisoformat(bounce["created"].replace("Z", "+00:00")),
                            "status": bounce["status"]
                        })
                    return {"success": True, "bounces": bounces}
                
                return result
                
            elif self.config.provider == "mailgun":
                result = self._make_request("GET", "/bounces", {"limit": limit})
                if result["success"]:
                    bounces = []
                    for bounce in result["data"]["items"]:
                        bounces.append({
                            "email": bounce["address"],
                            "reason": bounce["error"],
                            "bounced_at": datetime.fromtimestamp(bounce["created_at"]),
                            "status": "bounced"
                        })
                    return {"success": True, "bounces": bounces}
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get bounces: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_bounce(self, email: str) -> Dict[str, Any]:
        """Delete a bounce record."""
        try:
            if self.config.provider == "sendgrid":
                result = self._make_request("DELETE", f"/suppression/bounces/{email}")
                if result["success"]:
                    logger.info(f"Bounce deleted: {email}")
                return result
                
            elif self.config.provider == "mailgun":
                result = self._make_request("DELETE", f"/bounces/{email}")
                if result["success"]:
                    logger.info(f"Bounce deleted: {email}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to delete bounce: {e}")
            return {"success": False, "error": str(e)}
    
    # Analytics and Tracking
    def get_analytics(self, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get email analytics."""
        try:
            if not start_date:
                start_date = datetime.now(UTC) - timedelta(days=30)
            if not end_date:
                end_date = datetime.now(UTC)
            
            if self.config.provider == "sendgrid":
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")
                
                result = self._make_request("GET", f"/mail/stats?start_date={start_str}&end_date={end_str}")
                if result["success"]:
                    stats = result["data"][0]["stats"][0]["metrics"]
                    analytics = EmailAnalytics(
                        total_sent=stats.get("delivered", 0),
                        total_delivered=stats.get("delivered", 0),
                        total_opened=stats.get("opens", 0),
                        total_clicked=stats.get("clicks", 0),
                        total_bounced=stats.get("bounces", 0),
                        total_spam_reports=stats.get("spam_reports", 0)
                    )
                    
                    if analytics.total_delivered > 0:
                        analytics.open_rate = analytics.total_opened / analytics.total_delivered
                        analytics.click_rate = analytics.total_clicked / analytics.total_delivered
                        analytics.bounce_rate = analytics.total_bounced / analytics.total_delivered
                        analytics.spam_report_rate = analytics.total_spam_reports / analytics.total_delivered
                    
                    return {"success": True, "analytics": analytics}
                
                return result
                
            elif self.config.provider == "mailgun":
                start_str = start_date.strftime("%Y-%m-%d")
                end_str = end_date.strftime("%Y-%m-%d")
                
                result = self._make_request("GET", f"/stats?start={start_str}&end={end_str}")
                if result["success"]:
                    stats = result["data"]["items"]
                    analytics = EmailAnalytics()
                    
                    for stat in stats:
                        analytics.total_sent += stat.get("delivered", 0)
                        analytics.total_delivered += stat.get("delivered", 0)
                        analytics.total_opened += stat.get("opened", 0)
                        analytics.total_clicked += stat.get("clicked", 0)
                        analytics.total_bounced += stat.get("bounced", 0)
                        analytics.total_spam_reports += stat.get("complained", 0)
                    
                    if analytics.total_delivered > 0:
                        analytics.open_rate = analytics.total_opened / analytics.total_delivered
                        analytics.click_rate = analytics.total_clicked / analytics.total_delivered
                        analytics.bounce_rate = analytics.total_bounced / analytics.total_delivered
                        analytics.spam_report_rate = analytics.total_spam_reports / analytics.total_delivered
                    
                    return {"success": True, "analytics": analytics}
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_analytics(self, event_type: str, count: int = 1):
        """Update local analytics."""
        if event_type == "sent":
            self.analytics.total_sent += count
            self.analytics.last_sent = datetime.now(UTC)
    
    # Utility Methods
    def test_connection(self) -> Dict[str, Any]:
        """Test email service connection."""
        try:
            if self.config.provider == "sendgrid":
                result = self._make_request("GET", "/user/profile")
            elif self.config.provider == "mailgun":
                result = self._make_request("GET", "/domains")
            
            if result["success"]:
                return {"success": True, "status": "connected"}
            else:
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"Failed to test connection: {e}")
            return {"success": False, "error": str(e)}
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        try:
            info = {
                "provider": self.config.provider,
                "from_email": self.config.from_email,
                "from_name": self.config.from_name,
                "enable_tracking": self.config.enable_tracking,
                "enable_analytics": self.config.enable_analytics,
                "templates_count": len(self.templates)
            }
            
            return {"success": True, "connection_info": info}
            
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"success": False, "error": str(e)} 