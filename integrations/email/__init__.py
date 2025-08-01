"""
Email Integration Module

Provides enterprise-grade email capabilities with SendGrid and Mailgun support.
"""

from .email_client import (
    EmailClient,
    EmailConfig,
    EmailTemplate,
    EmailRecipient,
    EmailResult,
    EmailAnalytics
)

__all__ = [
    "EmailClient",
    "EmailConfig",
    "EmailTemplate", 
    "EmailRecipient",
    "EmailResult",
    "EmailAnalytics"
] 