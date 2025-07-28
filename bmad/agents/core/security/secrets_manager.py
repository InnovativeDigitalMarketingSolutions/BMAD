"""
BMAD Secrets Manager

Secure secrets management voor BMAD agents.
Beschermt API keys en andere sensitive data.
"""

import os
import base64
import logging
import hashlib
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import time

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Secure secrets manager voor BMAD.
    """
    
    def __init__(self):
        self.secrets: Dict[str, str] = {}
        self.encrypted_secrets: Dict[str, bytes] = {}
        self._fernet: Optional[Fernet] = None
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Load secrets from environment
        self._load_environment_secrets()
    
    def _initialize_encryption(self):
        """Initialize encryption key."""
        try:
            # Get encryption key from environment or generate one
            encryption_key = os.getenv("BMAD_ENCRYPTION_KEY")
            
            if not encryption_key:
                # Generate a new key
                encryption_key = Fernet.generate_key()
                logger.warning("No encryption key found. Generated new key. Set BMAD_ENCRYPTION_KEY for persistence.")
            
            # Convert to bytes if string
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            self._fernet = Fernet(encryption_key)
            logger.info("Secrets encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self._fernet = None
    
    def _load_environment_secrets(self):
        """Load secrets from environment variables."""
        secret_prefixes = [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "REDIS_PASSWORD",
            "SLACK_TOKEN",
            "FIGMA_TOKEN",
            "CLICKUP_TOKEN"
        ]
        
        for prefix in secret_prefixes:
            value = os.getenv(prefix)
            if value:
                self.set_secret(prefix, value)
                logger.debug(f"Loaded secret: {prefix}")
    
    def set_secret(self, key: str, value: str, encrypt: bool = True):
        """
        Set een secret value.
        
        Args:
            key: Secret key
            value: Secret value
            encrypt: Of de value geëncrypt moet worden
        """
        if encrypt and self._fernet:
            # Encrypt the value
            encrypted_value = self._fernet.encrypt(value.encode())
            self.encrypted_secrets[key] = encrypted_value
            logger.debug(f"Secret encrypted: {key}")
        else:
            # Store in plain text (not recommended)
            self.secrets[key] = value
            logger.warning(f"Secret stored in plain text: {key}")
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Get een secret value.
        
        Args:
            key: Secret key
            
        Returns:
            Secret value of None
        """
        # Try encrypted first
        if key in self.encrypted_secrets and self._fernet:
            try:
                encrypted_value = self.encrypted_secrets[key]
                decrypted_value = self._fernet.decrypt(encrypted_value)
                return decrypted_value.decode()
            except Exception as e:
                logger.error(f"Failed to decrypt secret {key}: {e}")
                return None
        
        # Try plain text
        if key in self.secrets:
            return self.secrets[key]
        
        # Try environment
        return os.getenv(key)
    
    def has_secret(self, key: str) -> bool:
        """Check of een secret bestaat."""
        return (
            key in self.encrypted_secrets or
            key in self.secrets or
            os.getenv(key) is not None
        )
    
    def remove_secret(self, key: str):
        """Remove een secret."""
        if key in self.encrypted_secrets:
            del self.encrypted_secrets[key]
        if key in self.secrets:
            del self.secrets[key]
        logger.info(f"Secret removed: {key}")
    
    def list_secrets(self) -> Dict[str, str]:
        """List alle secret keys (zonder values)."""
        keys = set()
        
        # Add encrypted secrets
        keys.update(self.encrypted_secrets.keys())
        
        # Add plain text secrets
        keys.update(self.secrets.keys())
        
        # Add environment secrets
        for key in os.environ.keys():
            if any(prefix in key for prefix in ["API_KEY", "TOKEN", "PASSWORD", "SECRET"]):
                keys.add(key)
        
        return {key: "***ENCRYPTED***" if key in self.encrypted_secrets else "***PLAIN***" 
                for key in sorted(keys)}
    
    def validate_secrets(self) -> Dict[str, bool]:
        """Validate alle required secrets."""
        required_secrets = [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY"
        ]
        
        validation_results = {}
        for secret in required_secrets:
            value = self.get_secret(secret)
            validation_results[secret] = value is not None and len(value) > 0
        
        return validation_results
    
    def rotate_secret(self, key: str, new_value: str):
        """Rotate een secret value."""
        old_value = self.get_secret(key)
        
        if old_value:
            # Store old value temporarily for rollback
            backup_key = f"{key}_backup_{int(time.time())}"
            self.set_secret(backup_key, old_value)
        
        # Set new value
        self.set_secret(key, new_value)
        logger.info(f"Secret rotated: {key}")
    
    def get_secret_hash(self, key: str) -> Optional[str]:
        """Get hash van een secret voor validation."""
        value = self.get_secret(key)
        if value:
            return hashlib.sha256(value.encode()).hexdigest()
        return None

# Global secrets manager instance
secrets_manager = SecretsManager()

def require_secret(secret_key: str):
    """
    Decorator om te checken of een secret beschikbaar is.
    
    Args:
        secret_key: Required secret key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not secrets_manager.has_secret(secret_key):
                raise Exception(f"Required secret not found: {secret_key}")
            return func(*args, **kwargs)
        return wrapper
    return decorator 