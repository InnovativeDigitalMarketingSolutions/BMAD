"""
Client Manager for Integration Service

This module manages external service clients and provides a centralized interface
for integration operations.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from ..integrations.auth0_client import Auth0Client
from ..integrations.postgresql_client import PostgreSQLClient
from ..integrations.redis_client import RedisClient
from ..integrations.stripe_client import StripeClient
from ..integrations.email_client import EmailClient, EmailMessage
from ..integrations.storage_client import StorageClient

logger = logging.getLogger(__name__)

class ClientManager:
    """Manages external service clients for the Integration Service."""
    
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self.client_configs: Dict[str, Dict[str, Any]] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        
    async def initialize_clients(self):
        """Initialize all configured clients."""
        logger.info("Initializing external service clients...")
        
        # Initialize Auth0 client
        if self._should_initialize_client("auth0"):
            await self._initialize_auth0_client()
            
        # Initialize PostgreSQL client
        if self._should_initialize_client("postgresql"):
            await self._initialize_postgresql_client()
            
        # Initialize Redis client
        if self._should_initialize_client("redis"):
            await self._initialize_redis_client()
            
        # Initialize Stripe client
        if self._should_initialize_client("stripe"):
            await self._initialize_stripe_client()
            
        # Initialize Email client
        if self._should_initialize_client("email"):
            await self._initialize_email_client()
            
        # Initialize Storage client
        if self._should_initialize_client("storage"):
            await self._initialize_storage_client()
            
        logger.info(f"Initialized {len(self.clients)} clients")
        
    def _should_initialize_client(self, client_type: str) -> bool:
        """Check if client should be initialized based on environment variables."""
        env_var = f"{client_type.upper()}_ENABLED"
        return os.getenv(env_var, "false").lower() == "true"
        
    async def _initialize_auth0_client(self):
        """Initialize Auth0 client."""
        try:
            domain = os.getenv("AUTH0_DOMAIN")
            client_id = os.getenv("AUTH0_CLIENT_ID")
            client_secret = os.getenv("AUTH0_CLIENT_SECRET")
            
            if not all([domain, client_id, client_secret]):
                logger.warning("Auth0 credentials not fully configured")
                return
                
            client = Auth0Client(domain, client_id, client_secret)
            self.clients["auth0"] = client
            self.client_configs["auth0"] = {
                "domain": domain,
                "client_id": client_id,
                "type": "authentication"
            }
            logger.info("Auth0 client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Auth0 client: {e}")
            
    async def _initialize_postgresql_client(self):
        """Initialize PostgreSQL client."""
        try:
            connection_string = os.getenv("POSTGRESQL_URL")
            pool_size = int(os.getenv("POSTGRESQL_POOL_SIZE", "10"))
            
            if not connection_string:
                logger.warning("PostgreSQL connection string not configured")
                return
                
            client = PostgreSQLClient(connection_string, pool_size)
            await client.connect()
            self.clients["postgresql"] = client
            self.client_configs["postgresql"] = {
                "connection_string": connection_string,
                "pool_size": pool_size,
                "type": "database"
            }
            logger.info("PostgreSQL client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL client: {e}")
            
    async def _initialize_redis_client(self):
        """Initialize Redis client."""
        try:
            connection_string = os.getenv("REDIS_URL")
            pool_size = int(os.getenv("REDIS_POOL_SIZE", "10"))
            
            if not connection_string:
                logger.warning("Redis connection string not configured")
                return
                
            client = RedisClient(connection_string, pool_size)
            await client.connect()
            self.clients["redis"] = client
            self.client_configs["redis"] = {
                "connection_string": connection_string,
                "pool_size": pool_size,
                "type": "cache"
            }
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            
    async def _initialize_stripe_client(self):
        """Initialize Stripe client."""
        try:
            api_key = os.getenv("STRIPE_API_KEY")
            webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
            
            if not api_key:
                logger.warning("Stripe API key not configured")
                return
                
            client = StripeClient(api_key, webhook_secret)
            self.clients["stripe"] = client
            self.client_configs["stripe"] = {
                "api_key_configured": bool(api_key),
                "webhook_secret_configured": bool(webhook_secret),
                "type": "payment"
            }
            logger.info("Stripe client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Stripe client: {e}")
            
    async def _initialize_email_client(self):
        """Initialize Email client."""
        try:
            provider = os.getenv("EMAIL_PROVIDER", "sendgrid")
            api_key = os.getenv("EMAIL_API_KEY")
            domain = os.getenv("EMAIL_DOMAIN")
            from_email = os.getenv("EMAIL_FROM")
            
            if not api_key:
                logger.warning("Email API key not configured")
                return
                
            client = EmailClient(provider, api_key, domain, from_email)
            self.clients["email"] = client
            self.client_configs["email"] = {
                "provider": provider,
                "api_key_configured": bool(api_key),
                "domain": domain,
                "from_email": from_email,
                "type": "email"
            }
            logger.info(f"Email client initialized ({provider})")
        except Exception as e:
            logger.error(f"Failed to initialize Email client: {e}")
            
    async def _initialize_storage_client(self):
        """Initialize Storage client."""
        try:
            provider = os.getenv("STORAGE_PROVIDER", "aws")
            bucket = os.getenv("STORAGE_BUCKET")
            region = os.getenv("STORAGE_REGION")
            
            if not bucket:
                logger.warning("Storage bucket not configured")
                return
                
            # Get credentials based on provider
            if provider == "aws":
                credentials = {
                    "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
                    "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY")
                }
            elif provider == "gcs":
                credentials = {
                    "access_token": os.getenv("GCS_ACCESS_TOKEN")
                }
            else:
                logger.warning(f"Unsupported storage provider: {provider}")
                return
                
            if not any(credentials.values()):
                logger.warning(f"{provider.upper()} credentials not configured")
                return
                
            client = StorageClient(provider, credentials, bucket, region)
            self.clients["storage"] = client
            self.client_configs["storage"] = {
                "provider": provider,
                "bucket": bucket,
                "region": region,
                "credentials_configured": bool(any(credentials.values())),
                "type": "storage"
            }
            logger.info(f"Storage client initialized ({provider})")
        except Exception as e:
            logger.error(f"Failed to initialize Storage client: {e}")
            
    async def get_client(self, client_type: str) -> Optional[Any]:
        """Get a specific client by type."""
        return self.clients.get(client_type)
        
    async def get_all_clients(self) -> Dict[str, Any]:
        """Get all initialized clients."""
        return self.clients.copy()
        
    async def get_client_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all client configurations."""
        return self.client_configs.copy()
        
    async def check_client_health(self, client_type: str) -> Dict[str, Any]:
        """Check health of a specific client."""
        try:
            client = self.clients.get(client_type)
            if not client:
                return {
                    "status": "not_initialized",
                    "client_type": client_type,
                    "error": "Client not initialized"
                }
                
            if hasattr(client, 'health_check'):
                health_result = await client.health_check()
                self.health_status[client_type] = health_result
                return health_result
            else:
                return {
                    "status": "unknown",
                    "client_type": client_type,
                    "error": "Client does not support health checks"
                }
        except Exception as e:
            error_result = {
                "status": "error",
                "client_type": client_type,
                "error": str(e)
            }
            self.health_status[client_type] = error_result
            return error_result
            
    async def check_all_clients_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all clients."""
        health_results = {}
        
        for client_type in self.clients.keys():
            health_results[client_type] = await self.check_client_health(client_type)
            
        return health_results
        
    async def test_client_operation(self, client_type: str, operation: str, **kwargs) -> Dict[str, Any]:
        """Test a specific client operation."""
        try:
            client = self.clients.get(client_type)
            if not client:
                return {
                    "success": False,
                    "error": "Client not initialized",
                    "client_type": client_type,
                    "operation": operation
                }
                
            # Define test operations for each client type
            if client_type == "auth0":
                if operation == "list_users":
                    result = await client.list_users(limit=1)
                    return {
                        "success": True,
                        "result": len(result),
                        "client_type": client_type,
                        "operation": operation
                    }
                    
            elif client_type == "postgresql":
                if operation == "query":
                    result = await client.execute_query("SELECT 1 as test")
                    return {
                        "success": result.success,
                        "result": result.row_count,
                        "client_type": client_type,
                        "operation": operation
                    }
                    
            elif client_type == "redis":
                if operation == "ping":
                    await client.client.ping()
                    return {
                        "success": True,
                        "result": "pong",
                        "client_type": client_type,
                        "operation": operation
                    }
                    
            elif client_type == "stripe":
                if operation == "list_customers":
                    result = await client.list_customers(limit=1)
                    return {
                        "success": True,
                        "result": len(result),
                        "client_type": client_type,
                        "operation": operation
                    }
                    
            elif client_type == "email":
                if operation == "health_check":
                    result = await client.health_check()
                    return {
                        "success": result.get("status") == "healthy",
                        "result": result,
                        "client_type": client_type,
                        "operation": operation
                    }
                    
            elif client_type == "storage":
                if operation == "list_files":
                    result = await client.list_files(max_keys=1)
                    return {
                        "success": True,
                        "result": len(result),
                        "client_type": client_type,
                        "operation": operation
                    }
                    
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "client_type": client_type,
                "operation": operation
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "client_type": client_type,
                "operation": operation
            }
            
    async def cleanup(self):
        """Cleanup all clients."""
        logger.info("Cleaning up external service clients...")
        
        for client_type, client in self.clients.items():
            try:
                if hasattr(client, 'disconnect'):
                    await client.disconnect()
                elif hasattr(client, 'close'):
                    await client.close()
                logger.info(f"Cleaned up {client_type} client")
            except Exception as e:
                logger.error(f"Failed to cleanup {client_type} client: {e}")
                
        self.clients.clear()
        self.client_configs.clear()
        self.health_status.clear()
        logger.info("All clients cleaned up") 