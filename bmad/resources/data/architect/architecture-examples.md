## Memory/Context Design
- Short-term: Redis (TTL 1h, per user/session)
- Long-term: Supabase (Postgres, JSONB, vector search via pgvector)
- AI context: pgvector (semantic search, context retrieval for LLMs)

## Non-Functional Requirements (NFR) Voorbeeld
- Performance: API response < 200ms, batch jobs < 5 min
- Scalability: Horizontale scaling via Kubernetes, stateless services
- Security: JWT auth, HTTPS only, OWASP top 10 mitigaties
- Monitoring: Prometheus metrics, Sentry error tracking
- Compliance: GDPR, audit logging, data retention policy

## Risicoanalyse Voorbeeld
- Brute force attacks: Mitigeren met rate limiting (FastAPI middleware)
- Credential leaks: Gebruik environment secrets, geen hardcoded keys
- Session hijacking: JWT expiry en secure cookies
- Single point of failure: Redis cluster met sentinel

## Best Practices
- Modulariseer services en houd verantwoordelijkheden gescheiden
- Implementeer async/event-driven waar mogelijk
- Documenteer alle architectuurkeuzes (ADR)
- Automatiseer tests en deployment (CI/CD)
- Security-by-design en regelmatige dependency scans
