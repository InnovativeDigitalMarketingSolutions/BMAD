# Non-Functional Requirements (NFR) Advies
- Performance: API response < 200ms, batch jobs < 5 min
- Scalability: Horizontale scaling via Kubernetes, stateless services
- Security: JWT auth, HTTPS only, OWASP top 10 mitigaties
- Monitoring: Prometheus metrics, Sentry error tracking
- Compliance: GDPR, audit logging, data retention policy