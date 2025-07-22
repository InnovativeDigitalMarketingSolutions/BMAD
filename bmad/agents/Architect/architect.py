import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

RESOURCE_BASE = Path(__file__).parent.parent / "resources"
TEMPLATE_PATHS = {
    "design-api": RESOURCE_BASE / "templates/api/design-api.md",
    "microservices": RESOURCE_BASE / "templates/architecture/microservices.md",
    "event-flow": RESOURCE_BASE / "templates/architecture/event-flow.md",
    "memory-design": RESOURCE_BASE / "templates/architecture/memory-design.md",
    "nfrs": RESOURCE_BASE / "templates/architecture/nfrs.md",
    "adr": RESOURCE_BASE / "templates/general/adr.md",
    "risk-analysis": RESOURCE_BASE / "templates/general/risk-analysis.md",
    "review": RESOURCE_BASE / "templates/general/review.md",
    "refactor": RESOURCE_BASE / "templates/general/refactor.md",
    "infra-as-code": RESOURCE_BASE / "templates/devops/infra-as-code.md",
    "release-strategy": RESOURCE_BASE / "templates/devops/release-strategy.md",
    "poc": RESOURCE_BASE / "templates/general/poc.md",
    "security-review": RESOURCE_BASE / "templates/security/security-review.md",
    "tech-stack-eval": RESOURCE_BASE / "templates/general/tech-stack-eval.md",
    "checklist": RESOURCE_BASE / "templates/general/checklist.md",
    "api-contract": RESOURCE_BASE / "templates/api/api-contract.md",
    "test-strategy": RESOURCE_BASE / "templates/testing/test-strategy.md",
    "best-practices": RESOURCE_BASE / "templates/general/best-practices.md",
    "export": RESOURCE_BASE / "data/architect/architecture-examples.md",
    "changelog": RESOURCE_BASE / "data/general/changelog.md",
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
- best-practices: Toon architectuur best practices
- export: Exporteer architectuur artefacten
- changelog: Toon changelog van architectuurwijzigingen
- test: Test resource completeness
- list-resources: Toon alle beschikbare resource-bestanden
- help: Toon deze help

Samenwerking: Werkt nauw samen met Fullstack, Backend, DevOps, Product Owner, AI/MLOps, Test en Security agents. Output is direct bruikbaar voor devs, testers en business.
        """)

    # ... bestaande fallback-methodes ...
    def best_practices(self):
        path = TEMPLATE_PATHS.get("best-practices")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen best practices resource gevonden.")

    def export(self):
        path = TEMPLATE_PATHS.get("export")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen export resource gevonden.")

    def changelog(self):
        path = TEMPLATE_PATHS.get("changelog")
        if path and path.exists():
            print(path.read_text())
        else:
            print("Geen changelog resource gevonden.")

    def list_resources(self):
        print("Beschikbare resource-bestanden:")
        for key, path in TEMPLATE_PATHS.items():
            print(f"- {key}: {path}")

    def test(self):
        missing = []
        for key, path in TEMPLATE_PATHS.items():
            if not path.exists():
                missing.append((key, str(path)))
        if missing:
            print("[FOUT] Ontbrekende resource-bestanden:")
            for key, path in missing:
                print(f"- {key}: {path}")
        else:
            print("[OK] Alle resource-bestanden zijn aanwezig.")

    def run(self, command):
        if command == "help" or command is None:
            self.show_help()
            return
        path = TEMPLATE_PATHS.get(command)
        if path and path.exists():
            logging.info(f"Resource-bestand geladen: {path}")
            print(path.read_text())
            return
        # Fallback naar Python-functie
        func = getattr(self, command.replace("-", "_"), None)
        if callable(func):
            logging.info(f"Fallback Python-methode aangeroepen: {command}")
            func()
        else:
            logging.error(f"Onbekend commando of ontbrekend resource-bestand: {command}")
            self.show_help()