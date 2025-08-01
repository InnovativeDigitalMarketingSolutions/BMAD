"""
Auth0 Integration Client

Provides comprehensive Auth0 integration for enterprise authentication including:
- Single Sign-On (SSO) support
- Multi-factor authentication (MFA)
- Social login integration
- Role-based access control (RBAC)
- User provisioning/deprovisioning
- JWT token management
"""

import os
import logging
import time
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
import requests
from urllib.parse import urlencode
import jwt
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)

@dataclass
class Auth0Config:
    """Configuration for Auth0 integration."""
    domain: str
    client_id: str
    client_secret: str
    audience: Optional[str] = None
    api_audience: Optional[str] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    token_cache_duration: int = 3600  # 1 hour

@dataclass
class Auth0User:
    """Auth0 user information."""
    user_id: str
    email: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False
    blocked: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    logins_count: int = 0
    app_metadata: Optional[Dict[str, Any]] = None
    user_metadata: Optional[Dict[str, Any]] = None

@dataclass
class Auth0Role:
    """Auth0 role information."""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = None

@dataclass
class Auth0Permission:
    """Auth0 permission information."""
    resource_server_identifier: str
    permission_name: str
    resource_server_name: Optional[str] = None

class Auth0Client:
    """
    Comprehensive Auth0 client for enterprise authentication.
    """
    
    def __init__(self, config: Auth0Config):
        """Initialize Auth0 client with configuration."""
        self.config = config
        self.base_url = f"https://{config.domain}"
        self.api_url = f"https://{config.domain}/api/v2"
        self.token_cache = {}
        self.token_cache_expiry = {}
        
        logger.info(f"Auth0 client initialized for domain: {config.domain}")
    
    def _get_management_token(self) -> Optional[str]:
        """Get management API token with caching."""
        cache_key = "management_token"
        
        # Check cache
        if (cache_key in self.token_cache and 
            cache_key in self.token_cache_expiry and
            datetime.now(UTC) < self.token_cache_expiry[cache_key]):
            return self.token_cache[cache_key]
        
        # Get new token
        token_url = f"{self.base_url}/oauth/token"
        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "audience": self.config.api_audience or f"https://{self.config.domain}/api/v2/",
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(token_url, json=payload)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                # Cache token
                expiry = datetime.now(UTC) + timedelta(seconds=self.config.token_cache_duration)
                self.token_cache[cache_key] = access_token
                self.token_cache_expiry[cache_key] = expiry
                
                logger.debug("Management token obtained and cached")
                return access_token
            else:
                logger.error("No access token in response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get management token: {e}")
            return None
    
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                         params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Auth0."""
        token = self._get_management_token()
        if not token:
            return {"success": False, "error": "Failed to get management token"}
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {"success": True, "data": None}
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def create_user(self, email: str, password: str, name: Optional[str] = None,
                   connection: str = "Username-Password-Authentication",
                   **kwargs) -> Dict[str, Any]:
        """Create a new Auth0 user."""
        user_data = {
            "email": email,
            "password": password,
            "connection": connection,
            "email_verified": False
        }
        
        if name:
            user_data["name"] = name
        
        # Add additional fields
        user_data.update(kwargs)
        
        return self._make_api_request("POST", "users", data=user_data)
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID."""
        return self._make_api_request("GET", f"users/{user_id}")
    
    def update_user(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update user information."""
        return self._make_api_request("PUT", f"users/{user_id}", data=kwargs)
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete user."""
        return self._make_api_request("DELETE", f"users/{user_id}")
    
    def get_users(self, page: int = 0, per_page: int = 100, 
                  include_totals: bool = True, **filters) -> Dict[str, Any]:
        """Get users with optional filtering."""
        params = {
            "page": page,
            "per_page": per_page,
            "include_totals": str(include_totals).lower()
        }
        
        # Add filters
        for key, value in filters.items():
            if value is not None:
                params[f"q"] = f"{key}:{value}"
        
        return self._make_api_request("GET", "users", params=params)
    
    def create_role(self, name: str, description: Optional[str] = None,
                   permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new role."""
        role_data = {
            "name": name,
            "description": description or ""
        }
        
        result = self._make_api_request("POST", "roles", data=role_data)
        
        if result["success"] and permissions:
            role_id = result["data"]["id"]
            self.assign_permissions_to_role(role_id, permissions)
        
        return result
    
    def get_role(self, role_id: str) -> Dict[str, Any]:
        """Get role by ID."""
        return self._make_api_request("GET", f"roles/{role_id}")
    
    def update_role(self, role_id: str, **kwargs) -> Dict[str, Any]:
        """Update role information."""
        return self._make_api_request("PUT", f"roles/{role_id}", data=kwargs)
    
    def delete_role(self, role_id: str) -> Dict[str, Any]:
        """Delete role."""
        return self._make_api_request("DELETE", f"roles/{role_id}")
    
    def get_roles(self, page: int = 0, per_page: int = 100,
                  include_totals: bool = True) -> Dict[str, Any]:
        """Get roles."""
        params = {
            "page": page,
            "per_page": per_page,
            "include_totals": str(include_totals).lower()
        }
        
        return self._make_api_request("GET", "roles", params=params)
    
    def assign_roles_to_user(self, user_id: str, role_ids: List[str]) -> Dict[str, Any]:
        """Assign roles to user."""
        data = {"roles": role_ids}
        return self._make_api_request("POST", f"users/{user_id}/roles", data=data)
    
    def get_user_roles(self, user_id: str) -> Dict[str, Any]:
        """Get roles assigned to user."""
        return self._make_api_request("GET", f"users/{user_id}/roles")
    
    def remove_roles_from_user(self, user_id: str, role_ids: List[str]) -> Dict[str, Any]:
        """Remove roles from user."""
        data = {"roles": role_ids}
        return self._make_api_request("DELETE", f"users/{user_id}/roles", data=data)
    
    def assign_permissions_to_role(self, role_id: str, permissions: List[str]) -> Dict[str, Any]:
        """Assign permissions to role."""
        data = {"permissions": permissions}
        return self._make_api_request("POST", f"roles/{role_id}/permissions", data=data)
    
    def get_role_permissions(self, role_id: str) -> Dict[str, Any]:
        """Get permissions assigned to role."""
        return self._make_api_request("GET", f"roles/{role_id}/permissions")
    
    def remove_permissions_from_role(self, role_id: str, permissions: List[str]) -> Dict[str, Any]:
        """Remove permissions from role."""
        data = {"permissions": permissions}
        return self._make_api_request("DELETE", f"roles/{role_id}/permissions", data=data)
    
    def create_permission(self, resource_server_identifier: str, permission_name: str,
                         resource_server_name: Optional[str] = None,
                         description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new permission."""
        permission_data = {
            "resource_server_identifier": resource_server_identifier,
            "permission_name": permission_name,
            "resource_server_name": resource_server_name or resource_server_identifier,
            "description": description or ""
        }
        
        return self._make_api_request("POST", "resource-servers", data=permission_data)
    
    def get_permissions(self, resource_server_identifier: Optional[str] = None) -> Dict[str, Any]:
        """Get permissions."""
        params = {}
        if resource_server_identifier:
            params["resource_server_identifier"] = resource_server_identifier
        
        return self._make_api_request("GET", "resource-servers", params=params)
    
    def validate_token(self, token: str, audience: Optional[str] = None) -> Dict[str, Any]:
        """Validate JWT token."""
        try:
            # Decode token without verification first to get header
            header = jwt.get_unverified_header(token)
            
            # Get public key
            jwks_url = f"{self.base_url}/.well-known/jwks.json"
            response = requests.get(jwks_url)
            response.raise_for_status()
            
            jwks = response.json()
            public_key = None
            
            # Find the right key
            for key in jwks["keys"]:
                if key["kid"] == header["kid"]:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not public_key:
                return {"success": False, "error": "Public key not found"}
            
            # Verify token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=audience or self.config.audience,
                issuer=f"https://{self.config.domain}/"
            )
            
            return {"success": True, "data": payload}
            
        except InvalidTokenError as e:
            return {"success": False, "error": f"Invalid token: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Token validation failed: {e}"}
    
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information from token."""
        validation_result = self.validate_token(token)
        if not validation_result["success"]:
            return validation_result
        
        user_id = validation_result["data"].get("sub")
        if not user_id:
            return {"success": False, "error": "No user ID in token"}
        
        return self.get_user(user_id)
    
    def block_user(self, user_id: str) -> Dict[str, Any]:
        """Block a user."""
        return self.update_user(user_id, blocked=True)
    
    def unblock_user(self, user_id: str) -> Dict[str, Any]:
        """Unblock a user."""
        return self.update_user(user_id, blocked=False)
    
    def get_user_logs(self, user_id: str, page: int = 0, per_page: int = 100) -> Dict[str, Any]:
        """Get user logs."""
        params = {
            "q": f"user_id:{user_id}",
            "page": page,
            "per_page": per_page
        }
        
        return self._make_api_request("GET", "logs", params=params)
    
    def create_organization(self, name: str, display_name: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """Create a new organization."""
        org_data = {
            "name": name,
            "display_name": display_name or name
        }
        org_data.update(kwargs)
        
        return self._make_api_request("POST", "organizations", data=org_data)
    
    def add_user_to_organization(self, organization_id: str, user_id: str,
                                role_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Add user to organization."""
        data = {"members": [user_id]}
        if role_ids:
            data["roles"] = role_ids
        
        return self._make_api_request("POST", f"organizations/{organization_id}/members", data=data)
    
    def get_organization_members(self, organization_id: str) -> Dict[str, Any]:
        """Get organization members."""
        return self._make_api_request("GET", f"organizations/{organization_id}/members")
    
    def generate_password_reset_token(self, email: str, connection: str = "Username-Password-Authentication") -> Dict[str, Any]:
        """Generate password reset token."""
        data = {
            "client_id": self.config.client_id,
            "email": email,
            "connection": connection
        }
        
        url = f"{self.base_url}/dbconnections/change_password"
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user summary."""
        user_result = self.get_user(user_id)
        if not user_result["success"]:
            return user_result
        
        user = user_result["data"]
        
        # Get user roles
        roles_result = self.get_user_roles(user_id)
        roles = roles_result.get("data", []) if roles_result["success"] else []
        
        # Get user logs (recent)
        logs_result = self.get_user_logs(user_id, per_page=10)
        logs = logs_result.get("data", []) if logs_result["success"] else []
        
        summary = {
            "user": user,
            "roles": roles,
            "recent_logs": logs,
            "summary": {
                "total_roles": len(roles),
                "total_logs": len(logs),
                "last_login": user.get("last_login"),
                "logins_count": user.get("logins_count", 0),
                "blocked": user.get("blocked", False),
                "email_verified": user.get("email_verified", False)
            }
        }
        
        return {"success": True, "data": summary} 