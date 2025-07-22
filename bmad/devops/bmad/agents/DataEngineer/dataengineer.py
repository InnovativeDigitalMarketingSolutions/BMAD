import argparse
from pathlib import Path
from datetime import datetime

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "pipeline-template": RESOURCE_BASE / "templates/dataengineer/pipeline-template.md",
    "quality-check-template": RESOURCE_BASE / "templates/dataengineer/quality-check-template.md",
    "report-template": RESOURCE_BASE / "templates/dataengineer/report-template.md",
    "pipeline-report-export-md": RESOURCE_BASE / "templates/dataengineer/pipeline-report-export-template.md",
    "pipeline-report-export-json": RESOURCE_BASE / "templates/dataengineer/pipeline-report-export-template.json",
    "best-practices": RESOURCE_BASE / "templates/dataengineer/best-practices.md"
}
DATA_PATHS = {
    "pipeline-history": RESOURCE_BASE / "data/dataengineer/pipeline-history.md",
    "quality-history": RESOURCE_BASE / "data/dataengineer/quality-history.md",
    "pipeline-changelog": RESOURCE_BASE / "data/dataengineer/pipeline-changelog.md"
}
AGENT_VERSION = "1.0.0"
LOG_PATH = RESOURCE_BASE / "data/dataengineer/dataengineeragent-log.md"

class DataEngineerAgent:
    def __init__(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Data Engineer Agent: {message}\n")
        except Exception as e:
            print(f"⚠️  Logging fout: {e}")

    def show_help(self):
        print("""🛠️ Data Engineer Agent - Beschikbare commando's:
- build-pipeline: Bouw of update een data pipeline (ETL/ELT)
- run-quality-check: Voer een data quality check uit
- generate-report: Genereer een data-analyse rapport
- monitor-pipeline: Monitor pipeline status en performance
- show-best-practices: Toon best practices voor data engineering
- export-pipeline-report: Exporteer pipeline rapport naar Markdown of JSON
- show-changelog: Toon changelog van pipelines en data
- show-collaboration: Toon samenwerking met andere agents
- show-version: Toon agentversie
- test: Controleer of alle resource-bestanden aanwezig zijn
- list-resources: Toon alle beschikbare resource-bestanden
- help: Toon deze help
        """)
        print("""
📋 Uitleg per commando:
- build-pipeline: Toont pipeline-template en logt de actie
- run-quality-check: Toont quality-check-template en logt de actie
- generate-report: Toont report-template en logt de actie
- monitor-pipeline: Toont pipeline-template en logt de actie
- export-pipeline-report: Toont export templates (MD/JSON) en logt de actie
- test: Controleert of alle resource- en databestanden aanwezig zijn en geeft een samenvatting
- list-resources: Toont een lijst van alle beschikbare resource- en databestanden
- show-changelog: Toont changelog van pipelines en data
- show-collaboration: Toont samenwerking met AI, devops, test, PO, architect
- show-version: Toont de huidige versie van de agent
        """)

    def show_version(self):
        print(f"🛠️ Data Engineer Agent versie: {AGENT_VERSION}")

    def show_resource(self, key):
        path = TEMPLATE_PATHS.get(key)
        if path and path.exists():
            print(path.read_text())
        else:
            print(f"⚠️  Geen resource gevonden voor: {key}")

    def show_data(self, key):
        path = DATA_PATHS.get(key)
        if path and path.exists():
            print(path.read_text())
        else:
            print(f"⚠️  Geen data gevonden voor: {key}")

    def show_collaboration(self):
        self.log("show-collaboration")
        print("""🤝 Data Engineer Agent - Samenwerking met andere agents:

Deze agent werkt samen met AI Developer, Architect, Test Engineer, DevOps/Infra en Product Owner voor schaalbare en betrouwbare data flows. Data pipelines, quality checks en rapportages worden gedeeld met het hele team.
        """)
        print("✅ Samenwerking overzicht getoond.")

    def show_changelog(self):
        self.log("show-changelog")
        print("🗒️ Pipeline/Data Changelog:")
        self.show_data("pipeline-changelog")
        print("✅ Pipeline/data changelog getoond.")

    def show_best_practices(self):
        self.log("show-best-practices")
        print("📚 Best Practices Data Engineering:")
        self.show_resource("best-practices")
        print("✅ Best practices getoond.")

    def test_resources(self):
        print("🔧 Test resource-bestanden:")
        missing = []
        for key, path in {**TEMPLATE_PATHS, **DATA_PATHS}.items():
            if not path.exists():
                missing.append(str(path))
        total = len(TEMPLATE_PATHS) + len(DATA_PATHS)
        found = total - len(missing)
        print(f"Samenvatting: {found}/{total} bestanden gevonden.")
        if missing:
            print("❌ Ontbrekende bestanden:")
            for m in missing:
                print(f"- {m}")
        else:
            print("✅ Alle resource- en databestanden aanwezig!")

    def list_resources(self):
        print("📂 Beschikbare resource-bestanden:")
        for key, path in {**TEMPLATE_PATHS, **DATA_PATHS}.items():
            status = "✅" if path.exists() else "❌"
            print(f"{status} {key}: {path}")

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "build-pipeline": lambda: self._show_and_log("pipeline-template", "build-pipeline"),
            "run-quality-check": lambda: self._show_and_log("quality-check-template", "run-quality-check"),
            "generate-report": lambda: self._show_and_log("report-template", "generate-report"),
            "monitor-pipeline": lambda: self._show_and_log("pipeline-template", "monitor-pipeline"),
            "export-pipeline-report": lambda: self._show_export(["pipeline-report-export-md", "pipeline-report-export-json"], "export-pipeline-report"),
            "show-best-practices": self.show_best_practices,
            "show-changelog": self.show_changelog,
            "show-collaboration": self.show_collaboration,
            "test": self.test_resources,
            "list-resources": self.list_resources,
        }
        func = commands.get(command)
        if func:
            try:
                func()
            except Exception as e:
                print(f"❌ Fout bij uitvoeren van commando '{command}': {e}")
        else:
            print(f"❌ Onbekend commando: {command}")
            print("💡 Gebruik 'help' voor beschikbare commando's.")
            self.show_help()

    def _show_and_log(self, template_key, log_action):
        self.log(log_action)
        print(f"🔧 {log_action.replace('-', ' ').capitalize()}:")
        self.show_resource(template_key)
        print(f"✅ {log_action.replace('-', ' ').capitalize()} template getoond.")

    def _show_export(self, template_keys, log_action):
        self.log(log_action)
        print(f"📤 Export {log_action.replace('-', ' ')}:")
        for key in template_keys:
            self.show_resource(key)
        print(f"✅ Export templates getoond.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Engineer Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = DataEngineerAgent()
    agent.run(args.command)
