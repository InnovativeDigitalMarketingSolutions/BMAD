"""
MFA service for the Authentication Service.

This module handles multi-factor authentication including TOTP,
backup codes, and device management.
"""

import pyotp
import secrets
import hashlib
import qrcode
import base64
from io import BytesIO
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MFAService:
    """MFA service for multi-factor authentication."""
    
    def __init__(self, issuer_name: str = "BMAD"):
        """Initialize the MFA service."""
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes."""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = secrets.token_hex(4).upper()[:8]
            codes.append(code)
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """Hash a backup code for storage."""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_totp(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: The TOTP secret
            token: The token to verify
            window: Time window for verification (default: 1)
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.warning(f"TOTP verification failed: {e}")
            return False
    
    def generate_qr_code(self, secret: str, email: str) -> str:
        """
        Generate QR code for TOTP setup.
        
        Args:
            secret: The TOTP secret
            email: User's email address
            
        Returns:
            str: Base64 encoded QR code image
        """
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=email,
                issuer_name=self.issuer_name
            )
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return ""
    
    def verify_backup_code(self, code: str, hashed_codes: List[str]) -> Optional[str]:
        """
        Verify a backup code.
        
        Args:
            code: The backup code to verify
            hashed_codes: List of hashed backup codes
            
        Returns:
            Optional[str]: The matched hashed code if valid, None otherwise
        """
        code_hash = self.hash_backup_code(code)
        for hashed_code in hashed_codes:
            if code_hash == hashed_code:
                return hashed_code
        return None
    
    def setup_mfa(self, email: str) -> Dict[str, Any]:
        """
        Setup MFA for a user.
        
        Args:
            email: User's email address
            
        Returns:
            Dict containing secret, QR code, and backup codes
        """
        secret = self.generate_secret()
        qr_code = self.generate_qr_code(secret, email)
        backup_codes = self.generate_backup_codes()
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes
        }
    
    def verify_mfa_token(self, secret: str, token: str, backup_codes: List[str] = None) -> Dict[str, Any]:
        """
        Verify MFA token (TOTP or backup code).
        
        Args:
            secret: The TOTP secret
            token: The token to verify
            backup_codes: List of hashed backup codes
            
        Returns:
            Dict containing verification result and type
        """
        # First try TOTP
        if self.verify_totp(secret, token):
            return {
                "valid": True,
                "type": "totp",
                "message": "TOTP token verified successfully"
            }
        
        # If TOTP fails and backup codes are provided, try backup code
        if backup_codes:
            matched_code = self.verify_backup_code(token, backup_codes)
            if matched_code:
                return {
                    "valid": True,
                    "type": "backup",
                    "message": "Backup code verified successfully",
                    "used_code": matched_code
                }
        
        return {
            "valid": False,
            "type": "invalid",
            "message": "Invalid MFA token"
        }
    
    def get_totp_uri(self, secret: str, email: str) -> str:
        """
        Get TOTP URI for manual setup.
        
        Args:
            secret: The TOTP secret
            email: User's email address
            
        Returns:
            str: TOTP URI
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
    
    def get_current_totp(self, secret: str) -> str:
        """
        Get current TOTP token (for testing purposes).
        
        Args:
            secret: The TOTP secret
            
        Returns:
            str: Current TOTP token
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception as e:
            logger.error(f"Failed to generate current TOTP: {e}")
            return ""
    
    def validate_secret(self, secret: str) -> bool:
        """
        Validate TOTP secret format.
        
        Args:
            secret: The secret to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            pyotp.TOTP(secret)
            return True
        except Exception:
            return False
    
    def get_remaining_time(self, secret: str) -> int:
        """
        Get remaining time for current TOTP token.
        
        Args:
            secret: The TOTP secret
            
        Returns:
            int: Remaining seconds
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.interval - (int(pyotp.time.time()) % totp.interval)
        except Exception as e:
            logger.error(f"Failed to get remaining time: {e}")
            return 0 