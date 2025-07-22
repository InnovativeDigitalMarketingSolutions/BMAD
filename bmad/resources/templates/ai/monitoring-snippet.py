# Monitoring & Drift Detectie Snippet
# Log inference requests en responses
# Monitor latency en foutpercentages
# Detecteer concept drift met periodieke evaluatie
# Sentry integratie (FastAPI)
import sentry_sdk
sentry_sdk.init(dsn="<your-sentry-dsn>")

# Prometheus metrics endpoint
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
