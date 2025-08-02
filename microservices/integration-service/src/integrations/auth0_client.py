"""
Auth0 Integration Client

This module provides the Auth0 client for the Integration Service,
handling authentication, user management, and token validation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Auth0User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False
    created_at: str
    updated_at: str

class Auth0Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    refresh_token: Optional[str] = None

class Auth0Client:
    """Auth0 client for authentication and user management."""
    
    def __init__(self, domain: str, client_id: str, client_secret: str):
        self.domain = domain
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = f"https://{domain}"
        self.session: Optional[aiohttp.ClientSession] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _get_access_token(self) -> str:
        """Get or refresh access token."""
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
            
        # Get new token
        token_url = f"{self.base_url}/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": f"{self.base_url}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        async with self.session.post(token_url, json=payload) as response:
            if response.status == 200:
                token_data = await response.json()
                self._access_token = token_data["access_token"]
                self._token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"] - 60)
                return self._access_token
            else:
                raise Exception(f"Failed to get access token: {response.status}")
                
    async def get_user(self, user_id: str) -> Optional[Auth0User]:
        """Get user by ID."""
        try:
            token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"{self.base_url}/api/v2/users/{user_id}"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return Auth0User(**user_data)
                elif response.status == 404:
                    return None
                else:
                    logger.error(f"Failed to get user {user_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
            
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Auth0User]:
        """Create a new user."""
        try:
            token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"{self.base_url}/api/v2/users"
            async with self.session.post(url, json=user_data, headers=headers) as response:
                if response.status == 201:
                    user_data = await response.json()
                    return Auth0User(**user_data)
                else:
                    logger.error(f"Failed to create user: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
            
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Auth0User]:
        """Update user by ID."""
        try:
            token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"{self.base_url}/api/v2/users/{user_id}"
            async with self.session.patch(url, json=user_data, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return Auth0User(**user_data)
                else:
                    logger.error(f"Failed to update user {user_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
            
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID."""
        try:
            token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"{self.base_url}/api/v2/users/{user_id}"
            async with self.session.delete(url, headers=headers) as response:
                return response.status == 204
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
            
    async def list_users(self, page: int = 0, per_page: int = 100) -> List[Auth0User]:
        """List users with pagination."""
        try:
            token = await self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"{self.base_url}/api/v2/users"
            params = {"page": page, "per_page": per_page}
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    users_data = await response.json()
                    return [Auth0User(**user_data) for user_data in users_data]
                else:
                    logger.error(f"Failed to list users: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
            
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token."""
        try:
            url = f"{self.base_url}/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
            
    async def health_check(self) -> Dict[str, Any]:
        """Check Auth0 service health."""
        try:
            # Try to get access token as health check
            token = await self._get_access_token()
            return {
                "status": "healthy",
                "domain": self.domain,
                "client_id": self.client_id,
                "token_available": bool(token)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "domain": self.domain,
                "client_id": self.client_id,
                "token_available": False
            } 