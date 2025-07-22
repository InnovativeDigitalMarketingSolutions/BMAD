# Risicoanalyse: User Authentication
- Brute force attacks: Mitigeren met rate limiting (FastAPI middleware)
- Credential leaks: Gebruik environment secrets, geen hardcoded keys
- Session hijacking: JWT expiry en secure cookies
- Single point of failure: Redis cluster met sentinel
