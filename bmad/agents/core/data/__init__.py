"""
BMAD Data Core Services

This module provides core data management and storage services.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"

# Import main data components
from .connection_pool import (
    ConnectionPoolManager,
    get_http_session,
    get_postgres,
    get_redis,
)
from .redis_cache import (
    RedisCache,
    cache_agent_confidence,
    cache_clickup_api,
    cache_llm_response,
    cache_project_config,
)
from .supabase_context import archive_old_context, get_context, save_context

__all__ = [
    "ConnectionPoolManager",
    "RedisCache",
    "archive_old_context",
    "cache_agent_confidence",
    "cache_clickup_api",
    "cache_llm_response",
    "cache_project_config",
    "get_context",
    "get_http_session",
    "get_postgres",
    "get_redis",
    "save_context"
]
