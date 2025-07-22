import argparse
from pathlib import Path
from datetime import datetime

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "strategy-roadmap": RESOURCE_BASE / "templates/strategiepartner/strategy-roadmap-template.md",
    "value-proposition": RESOURCE_BASE / "templates/strategiepartner/value-proposition-template.md",
    "stakeholder-mapping": RESOURCE_BASE / "templates/strategiepartner/stakeholder-mapping-template.md",
    "best-practices": RESOURCE_BASE / "templates/strategiepartner/best-practices.md"
}
DATA_PATHS = {
    "strategy-history": RESOURCE_BASE / "data/strategiepartner/strategy-history.md",
    "stakeholder-list": RESOURCE_BASE / "data/strategiepartner/stakeholder-list.md",
    "strategy-changelog": RESOURCE_BASE / "data/strategiepartner/strategy-changelog.md"
}
AGENT_VERSION = "1.0.0"
LOG_PATH = RESOURCE_BASE / "data/strategiepartner/strategiepartner-log.md"

class StrategiePartnerAgent:
    def log(self, message):
        with open(LOG_PATH, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

    def show_help(self):
        print("""Beschikbare commando's:
- generate-strategy-roadmap: Genereer strategische roadmap
- define-value-proposition: Definieer value-propositie
- map-stakeholders: Maak stakeholder mapping
- review-alignment: Review business/tech alignment
- export-strategy: Exporteer strategische roadmap of value-propositie
- show-best-practices: Toon strategie best practices
- show-version: Toon agentversie
- help: Toon deze help
        """)

    def show_version(self):
        print(f"Strategie Partner Agent versie: {AGENT_VERSION}")

    def show_resource(self, key):
        path = TEMPLATE_PATHS.get(key)
        if path and path.exists():
            print(path.read_text())
        else:
            print(f"Geen resource gevonden voor: {key}")

    def show_data(self, key):
        path = DATA_PATHS.get(key)
        if path and path.exists():
            print(path.read_text())
        else:
            print(f"Geen data gevonden voor: {key}")

    def generate_strategy_roadmap(self):
        self.log("generate-strategy-roadmap")
        self.show_resource("strategy-roadmap")

    def define_value_proposition(self):
        self.log("define-value-proposition")
        self.show_resource("value-proposition")

    def map_stakeholders(self):
        self.log("map-stakeholders")
        self.show_resource("stakeholder-mapping")

    def review_alignment(self):
        self.log("review-alignment")
        print("Business/tech alignment review: [voorbeeldoutput]")

    def export_strategy(self):
        self.log("export-strategy")
        self.show_data("strategy-history")
        self.show_data("strategy-changelog")

    def show_best_practices(self):
        self.log("show-best-practices")
        self.show_resource("best-practices")

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "generate-strategy-roadmap": self.generate_strategy_roadmap,
            "define-value-proposition": self.define_value_proposition,
            "map-stakeholders": self.map_stakeholders,
            "review-alignment": self.review_alignment,
            "export-strategy": self.export_strategy,
            "show-best-practices": self.show_best_practices,
        }
        func = commands.get(command)
        if func:
            func()
        else:
            print(f"Onbekend commando: {command}")
            self.show_help()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Strategie Partner Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = StrategiePartnerAgent()
    agent.run(args.command)
