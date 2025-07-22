# Security Guidelines

- Gebruik HTTPS voor alle communicatie
- JWT tokens met korte expiry en secure cookies
- Nooit secrets hardcoden; gebruik environment variables
- Input validatie op alle endpoints (backend & frontend)
- Rate limiting op gevoelige endpoints (login, registratie)
- Dependency scanning (npm audit, pip-audit)
- Logging van security events (Sentry, custom logs)
