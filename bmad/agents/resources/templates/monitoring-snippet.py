# Monitoring Snippet

# Sentry integratie (FastAPI)
import sentry_sdk
sentry_sdk.init(dsn="<your-sentry-dsn>")

# Prometheus metrics endpoint
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
