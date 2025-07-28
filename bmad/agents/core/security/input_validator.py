"""
BMAD Input Validator

Security-focused input validation voor BMAD agents.
Beschermt tegen XSS, SQL injection, en andere security threats.
"""

import re
import logging
import html
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class InputValidator:
    """
    Security-focused input validator voor BMAD.
    """
    
    def __init__(self):
        # Dangerous patterns
        self.sql_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b',
            r'(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+',
            r'(\bOR\b|\bAND\b)\s+\'[^\']*\'\s*=\s*\'[^\']*\'',
            r'--\s*$',
            r'/\*.*?\*/',
            r'xp_cmdshell',
            r'sp_executesql'
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*>',
            r'<input[^>]*>',
            r'<textarea[^>]*>',
            r'<select[^>]*>'
        ]
        
        # Command injection patterns
        self.command_patterns = [
            r'[;&|`$(){}]',
            r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ipconfig)\b',
            r'\.\./',
            r'~',
            r'\$\([^)]*\)'
        ]
        
        # Compile patterns for performance
        self.sql_regex = re.compile('|'.join(self.sql_patterns), re.IGNORECASE)
        self.xss_regex = re.compile('|'.join(self.xss_patterns), re.IGNORECASE)
        self.command_regex = re.compile('|'.join(self.command_patterns), re.IGNORECASE)
    
    def validate_string(self, value: str, max_length: int = 1000, allow_html: bool = False) -> Dict[str, Any]:
        """
        Validate een string input voor security threats.
        
        Args:
            value: String om te valideren
            max_length: Maximum lengte
            allow_html: Of HTML toegestaan is
            
        Returns:
            Dict met validation result
        """
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": "Value must be a string",
                "sanitized": None
            }
        
        # Check length
        if len(value) > max_length:
            return {
                "valid": False,
                "error": f"String too long (max {max_length} characters)",
                "sanitized": None
            }
        
        # Check for SQL injection
        if self.sql_regex.search(value):
            return {
                "valid": False,
                "error": "Potential SQL injection detected",
                "sanitized": None
            }
        
        # Check for XSS
        if not allow_html and self.xss_regex.search(value):
            return {
                "valid": False,
                "error": "Potential XSS attack detected",
                "sanitized": None
            }
        
        # Check for command injection
        if self.command_regex.search(value):
            return {
                "valid": False,
                "error": "Potential command injection detected",
                "sanitized": None
            }
        
        # Sanitize if needed
        sanitized = self.sanitize_string(value, allow_html)
        
        return {
            "valid": True,
            "error": None,
            "sanitized": sanitized
        }
    
    def sanitize_string(self, value: str, allow_html: bool = False) -> str:
        """
        Sanitize een string input.
        
        Args:
            value: String om te sanitizen
            allow_html: Of HTML toegestaan is
            
        Returns:
            Sanitized string
        """
        if not allow_html:
            # HTML escape
            value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        return value
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate een URL voor security.
        
        Args:
            url: URL om te valideren
            
        Returns:
            Dict met validation result
        """
        try:
            parsed = urlparse(url)
            
            # Check for dangerous protocols
            if parsed.scheme.lower() in ['javascript', 'data', 'vbscript']:
                return {
                    "valid": False,
                    "error": "Dangerous protocol detected",
                    "sanitized": None
                }
            
            # Check for local file access
            if parsed.scheme.lower() == 'file':
                return {
                    "valid": False,
                    "error": "Local file access not allowed",
                    "sanitized": None
                }
            
            return {
                "valid": True,
                "error": None,
                "sanitized": url
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Invalid URL: {str(e)}",
                "sanitized": None
            }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Validate een email adres.
        
        Args:
            email: Email om te valideren
            
        Returns:
            Dict met validation result
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return {
                "valid": False,
                "error": "Invalid email format",
                "sanitized": None
            }
        
        # Check for dangerous characters
        if any(char in email for char in ['<', '>', '"', "'", '&']):
            return {
                "valid": False,
                "error": "Email contains dangerous characters",
                "sanitized": None
            }
        
        return {
            "valid": True,
            "error": None,
            "sanitized": email.lower().strip()
        } 