#!/usr/bin/env python3
"""
Architect Agent voor CoPilot AI Business Suite
Adviseert over schaalbare, modulaire architectuur. Output in markdown, diagrammen, ADR’s, risicoanalyses, technische logs, en NFR-advies.
"""

import argparse
import sys
from pathlib import Path
import textwrap

RESOURCE_BASE = Path(__file__).parent.parent / "resources"
TEMPLATE_PATHS = {
    "design-api": RESOURCE_BASE / "templates/architect/api-design-template.md",
    "microservices": RESOURCE_BASE / "templates/architect/microservices-template.md",
    "event-flow": RESOURCE_BASE / "templates/architect/event-flow-template.md",
    "memory-design": RESOURCE_BASE / "templates/architect/memory-design-template.md",
    "nfrs": RESOURCE_BASE / "templates/architect/nfr-template.md",
    "adr": RESOURCE_BASE / "templates/architect/adr-template.md",
    "risk-analysis": RESOURCE_BASE / "templates/architect/risk-analysis-template.md",
    "review": RESOURCE_BASE / "templates/general/review-checklist.md",
    "refactor": RESOURCE_BASE / "data/general/refactoring-patterns.md",
    "infra-as-code": RESOURCE_BASE / "templates/architect/infra-as-code-template.md",
    "release-strategy": RESOURCE_BASE / "templates/architect/release-strategy-template.md",
    "poc": RESOURCE_BASE / "data/architect/architecture-examples.md",
    "security-review": RESOURCE_BASE / "templates/general/security-checklist.md",
    "tech-stack-eval": RESOURCE_BASE / "data/architect/architecture-examples.md",
    "checklist": RESOURCE_BASE / "templates/general/review-checklist.md",
    "api-contract": RESOURCE_BASE / "templates/general/openapi-snippet.yaml",
    "test-strategy": RESOURCE_BASE / "templates/architect/test-strategy-template.md",
}

class ArchitectAgent:
    def __init__(self):
        pass

    def show_help(self):
        print("""
Beschikbare commando's:
- design-api: Ontwerp API endpoints en specs
- microservices: Stel microservices structuur voor
- event-flow: Ontwerp event-driven flows
- memory-design: Adviseer over memory/context architectuur
- nfrs: Adviseer over non-functional requirements
- adr: Maak of update Architecture Decision Record
- risk-analysis: Voer risicoanalyse uit
- review: Review bestaande architectuur of code
- refactor: Stel refactorings voor
- infra-as-code: Adviseer over infra-as-code en CI/CD
- release-strategy: Adviseer over release/rollback strategieën
- poc: Begeleid proof-of-concept trajecten
- security-review: Voer security review uit
- tech-stack-eval: Evalueer alternatieven in de stack
- checklist: Genereer architectuur review checklist
- api-contract: Genereer OpenAPI/Swagger snippet
- test-strategy: Stel teststrategie voor
- help: Toon deze help
        """)

    # Oude Python-functies als fallback
    def design_api(self):
        print("""
### User Service API (FastAPI)

| Endpoint    | Method | Description         | Auth Required |
|-------------|--------|---------------------|--------------|
| /users/     | GET    | List all users      | Yes          |
| /users/{id} | GET    | Get user by ID      | Yes          |
| /users/     | POST   | Create new user     | No           |
| /users/{id} | PUT    | Update user         | Yes          |
| /users/{id} | DELETE | Delete user         | Yes          |
""")

    def microservices(self):
        print(textwrap.dedent("""
        # Microservices Structuur
        - user-service: authenticatie, profielbeheer
        - project-service: projecten, taken
        - ai-service: LLM, context, vector search
        - event-bus: Redis Pub/Sub
        - api-gateway: FastAPI, rate limiting, auth
        """))

    def event_flow(self):
        print(textwrap.dedent("""
        ```mermaid
        sequenceDiagram
            participant API as FastAPI
            participant Queue as Redis Pub/Sub
            participant Worker as Background Worker
            API->>Queue: Publish "user_created" event
            Queue->>Worker: Consume event
            Worker->>Supabase: Write to DB
        ```
        """))

    def memory_design(self):
        print(textwrap.dedent("""
        #### Memory Design
        - Short-term: Redis (TTL 1h, per user/session)
        - Long-term: Supabase (Postgres, JSONB, vector search via pgvector)
        - AI context: pgvector (semantic search, context retrieval for LLMs)
        """))

    def nfrs(self):
        print(textwrap.dedent("""
        # Non-Functional Requirements (NFR) Advies
        - Performance: API response < 200ms, batch jobs < 5 min
        - Scalability: Horizontale scaling via Kubernetes, stateless services
        - Security: JWT auth, HTTPS only, OWASP top 10 mitigaties
        - Monitoring: Prometheus metrics, Sentry error tracking
        - Compliance: GDPR, audit logging, data retention policy
        """))

    def adr(self):
        print(textwrap.dedent("""
        # ADR-003: Choice of Redis for Event Queue
        ## Context
        We need a fast, reliable event queue for async communication between services.
        ## Decision
        We choose Redis Pub/Sub for its speed, simplicity, and existing use in our stack.
        ## Alternatives
        - RabbitMQ: More features, but more complex to operate.
        - Kafka: Overkill for our current scale.
        ## Consequences
        - Easy integration with FastAPI and Python.
        - Limited durability (no message persistence).
        - May need to revisit if scale increases.
        """))

    def risk_analysis(self):
        print(textwrap.dedent("""
        # Risicoanalyse: User Authentication
        - Brute force attacks: Mitigeren met rate limiting (FastAPI middleware)
        - Credential leaks: Gebruik environment secrets, geen hardcoded keys
        - Session hijacking: JWT expiry en secure cookies
        - Single point of failure: Redis cluster met sentinel
        """))

    def review(self):
        print(textwrap.dedent("""
        # Review-checklist
        - [x] API endpoints consistent en RESTful
        - [x] Alle data flows async waar mogelijk
        - [ ] Security headers en input validatie aanwezig
        - [ ] Logging en monitoring voorzien
        - [ ] Documentatie up-to-date
        """))

    def refactor(self):
        print(textwrap.dedent("""
        # Refactoring Advies
        - Splits monolithische modules in kleinere services
        - Implementeer dependency injection voor testbaarheid
        - Vervang hardcoded config door environment variables
        - Automatiseer deployment met CI/CD
        """))

    def infra_as_code(self):
        print(textwrap.dedent("""
        # Infra-as-Code Advies
        - Gebruik Terraform voor cloud resources
        - Docker Compose voor lokale development
        - CI/CD pipelines met GitHub Actions
        - Secrets management via Vault of environment variables
        """))

    def release_strategy(self):
        print(textwrap.dedent("""
        # Release/rollback strategieën
        - Blue/green deployment
        - Canary releases
        - Rollback via tagged Docker images
        - Feature toggles voor experimenten
        """))

    def poc(self):
        print(textwrap.dedent("""
        # Proof-of-Concept (PoC) begeleiding
        - Zet een minimal working example op voor nieuwe technologie
        - Meet performance en integratie met bestaande stack
        - Documenteer lessons learned en aanbevelingen
        """))

    def security_review(self):
        print(textwrap.dedent("""
        # Security Review
        - Threat modeling voor alle endpoints
        - Input validatie en sanitatie
        - Gebruik van HTTPS en secure cookies
        - Logging van security events
        - Regelmatige dependency scans
        """))

    def tech_stack_eval(self):
        print(textwrap.dedent("""
        # Tech Stack Evaluatie
        - FastAPI vs. Flask: async support, performance
        - Redis vs. RabbitMQ: eenvoud vs. features
        - Supabase vs. Firebase: open source vs. closed
        - pgvector vs. Pinecone: integratie, kosten, features
        """))

    def checklist(self):
        print(textwrap.dedent("""
        # Architectuur Review Checklist
        - [ ] Is de architectuur modulair en schaalbaar?
        - [ ] Zijn alle externe afhankelijkheden benoemd?
        - [ ] Is security-by-design toegepast?
        - [ ] Zijn NFRs en risico’s gedocumenteerd?
        - [ ] Is er monitoring/logging voorzien?
        """))

    def api_contract(self):
        print(textwrap.dedent("""
        # OpenAPI/Swagger Snippet
        openapi: 3.0.0
        info:
          title: User Service API
          version: 1.0.0
        paths:
          /users/:
            get:
              summary: List all users
              responses:
                '200':
                  description: OK
          /users/{id}:
            get:
              summary: Get user by ID
              parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: string
              responses:
                '200':
                  description: OK
        """))

    def test_strategy(self):
        print(textwrap.dedent("""
        # Teststrategie
        - Unit tests: Voor alle business logic (pytest, coverage > 90%)
        - Integration tests: API endpoints, database interacties (pytest + testcontainers)
        - E2E tests: Belangrijkste user flows (Playwright, Selenium)
        - Security tests: OWASP ZAP scan in CI/CD
        - Load tests: Locust, k6 voor performance baseline
        """))

    def run(self, command):
        if command == "help" or command is None:
            self.show_help()
            return
        path = TEMPLATE_PATHS.get(command)
        if path and path.exists():
            print(path.read_text())
            return
        # Fallback naar Python-functie
        func = getattr(self, command.replace("-", "_"), None)
        if callable(func):
            func()
        else:
            print(f"[FOUT] Onbekend commando of ontbrekend resource-bestand: {command}")
            self.show_help()

def main():
    parser = argparse.ArgumentParser(description="Architect Agent CLI")
    parser.add_argument("command", nargs="?", help="Commando om uit te voeren (of 'help')")
    args = parser.parse_args()
    agent = ArchitectAgent()
    agent.run(args.command)

if __name__ == "__main__":
    main()
