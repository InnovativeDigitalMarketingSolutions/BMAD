# Teststrategie
- Unit tests: Voor alle business logic (pytest, coverage > 90%)
- Integration tests: API endpoints, database interacties (pytest + testcontainers)
- E2E tests: Belangrijkste user flows (Playwright, Selenium)
- Security tests: OWASP ZAP scan in CI/CD
- Load tests: Locust, k6 voor performance baseline
