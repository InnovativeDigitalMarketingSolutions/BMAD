# BMAD Core utilities package

# Export commonly used modules for backward compatibility
try:
    from .data.redis_cache import RedisCache
    redis_cache = RedisCache()
except ImportError:
    redis_cache = None

try:
    from .communication.slack_notify import send_slack_message
    slack_notify = send_slack_message
except ImportError:
    slack_notify = None
