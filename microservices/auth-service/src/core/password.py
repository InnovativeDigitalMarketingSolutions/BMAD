"""
Password service for the Authentication Service.

This module handles password hashing, verification, and validation.
"""

import secrets
import hashlib
from typing import Optional
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)


class PasswordService:
    """Password service for password management."""
    
    def __init__(self, bcrypt_rounds: int = 12):
        """Initialize the password service."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=bcrypt_rounds
        )
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_password_reset_token(self) -> str:
        """Generate a secure password reset token."""
        return secrets.token_urlsafe(32)
    
    def hash_token(self, token: str) -> str:
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password."""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each required category
        password = [
            secrets.choice("abcdefghijklmnopqrstuvwxyz"),  # lowercase
            secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),  # uppercase
            secrets.choice("0123456789"),  # digit
            secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")   # special
        ]
        
        # Fill the rest with random characters
        for _ in range(length - 4):
            password.append(secrets.choice(alphabet))
        
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return "".join(password_list)
    
    def check_password_history(self, new_password: str, password_history: list[str]) -> bool:
        """
        Check if new password is not in recent password history.
        
        Args:
            new_password: The new password to check
            password_history: List of hashed previous passwords
            
        Returns:
            bool: True if password is not in history, False otherwise
        """
        for old_hash in password_history:
            if self.verify_password(new_password, old_hash):
                return False
        return True
    
    def get_password_hash_info(self, hashed_password: str) -> dict:
        """
        Get information about a password hash.
        
        Args:
            hashed_password: The hashed password
            
        Returns:
            dict: Information about the hash
        """
        try:
            # Extract information from bcrypt hash
            if hashed_password.startswith("$2b$"):
                parts = hashed_password.split("$")
                if len(parts) >= 4:
                    rounds = int(parts[2])
                    return {
                        "algorithm": "bcrypt",
                        "rounds": rounds,
                        "hash_length": len(hashed_password)
                    }
        except Exception as e:
            logger.warning(f"Could not parse password hash: {e}")
        
        return {
            "algorithm": "unknown",
            "rounds": None,
            "hash_length": len(hashed_password)
        }
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if a password hash needs to be rehashed.
        
        Args:
            hashed_password: The hashed password
            
        Returns:
            bool: True if rehash is needed, False otherwise
        """
        return self.pwd_context.needs_update(hashed_password)
    
    def rehash_password(self, password: str) -> str:
        """
        Rehash a password with current settings.
        
        Args:
            password: The plain text password
            
        Returns:
            str: The new hash
        """
        return self.hash_password(password) 