# Microservices Structuur
- user-service: authenticatie, profielbeheer
- project-service: projecten, taken
- ai-service: LLM, context, vector search
- event-bus: Redis Pub/Sub
- api-gateway: FastAPI, rate limiting, auth