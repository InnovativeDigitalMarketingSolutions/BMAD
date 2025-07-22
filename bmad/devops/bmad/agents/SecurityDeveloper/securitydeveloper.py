import argparse
from pathlib import Path
from datetime import datetime

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "security-checklist": RESOURCE_BASE / "templates/securitydeveloper/security-checklist.md",
    "compliance-report": RESOURCE_BASE / "templates/securitydeveloper/compliance-report-template.md",
    "scan-report-export-md": RESOURCE_BASE / "templates/securitydeveloper/scan-report-export-template.md",
    "scan-report-export-json": RESOURCE_BASE / "templates/securitydeveloper/scan-report-export-template.json",
    "best-practices": RESOURCE_BASE / "templates/securitydeveloper/best-practices.md"
}
DATA_PATHS = {
    "scan-history": RESOURCE_BASE / "data/securitydeveloper/scan-history.md",
    "incidents": RESOURCE_BASE / "data/securitydeveloper/incidents.md",
    "security-changelog": RESOURCE_BASE / "data/securitydeveloper/security-changelog.md"
}
AGENT_VERSION = "1.0.0"
LOG_PATH = RESOURCE_BASE / "data/securitydeveloper/securitydeveloperagent-log.md"

class SecurityDeveloperAgent:
    def __init__(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Security Developer Agent: {message}\n")
        except Exception as e:
            print(f"⚠️  Logging fout: {e}")

    def show_help(self):
        print("""🔒 Security Developer Agent - Beschikbare commando's:
- scan-code: Scan de codebase op kwetsbaarheden en security issues
- generate-checklist: Genereer een security checklist voor het project
- review-dependency: Review afhankelijkheden op security en licenties
- generate-compliance-report: Genereer een compliance rapport (AVG, ISO, etc.)
- show-best-practices: Toon best practices voor secure development
- export-scan-report: Exporteer scanresultaten naar Markdown of JSON
- show-changelog: Toon changelog van security scans en incidenten
- show-collaboration: Toon samenwerking met andere agents
- show-version: Toon agentversie
- help: Toon deze help
        """)
        print("""
📋 Uitleg per commando:
- scan-code: Toont security checklist en logt de actie
- generate-checklist: Toont security checklist template en logt de actie
- review-dependency: Toont afhankelijkheden review (mock output)
- generate-compliance-report: Toont compliance report template en logt de actie
- show-best-practices: Toont best practices voor secure development
- export-scan-report: Toont export templates (MD/JSON) en logt de actie
- show-changelog: Toont changelog van security scans en incidenten
- show-collaboration: Toont samenwerking met architect, dev, devops, test
- show-version: Toont de huidige versie van de agent
        """)

    def show_version(self):
        print(f"🔒 Security Developer Agent versie: {AGENT_VERSION}")

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
        print("""🤝 Security Developer Agent - Samenwerking met andere agents:

Deze agent werkt samen met Architect, Backend/Frontend Developer, DevOps/Infra en Test Engineer voor veilige software en compliance. Security bevindingen en rapportages worden gedeeld met het hele team.
        """)
        print("✅ Samenwerking overzicht getoond.")

    def scan_code(self):
        self.log("scan-code")
        print("🔍 Codebase scan:")
        self.show_resource("security-checklist")
        print("✅ Security checklist getoond.")

    def generate_checklist(self):
        self.log("generate-checklist")
        print("📋 Security Checklist:")
        self.show_resource("security-checklist")
        print("✅ Security checklist template getoond.")

    def review_dependency(self):
        self.log("review-dependency")
        print("🔗 Dependency Review:")
        print("Alle dependencies zijn gecontroleerd op bekende kwetsbaarheden en licenties (mock output).")
        print("✅ Dependency review uitgevoerd.")

    def generate_compliance_report(self):
        self.log("generate-compliance-report")
        print("📄 Compliance Rapport:")
        self.show_resource("compliance-report")
        print("✅ Compliance rapport template getoond.")

    def show_best_practices(self):
        self.log("show-best-practices")
        print("📚 Best Practices Security:")
        self.show_resource("best-practices")
        print("✅ Best practices getoond.")

    def export_scan_report(self):
        self.log("export-scan-report")
        print("📤 Scan Report Export:")
        self.show_resource("scan-report-export-md")
        self.show_resource("scan-report-export-json")
        print("✅ Export templates (MD/JSON) getoond.")

    def show_changelog(self):
        self.log("show-changelog")
        print("🗒️ Security Changelog:")
        self.show_data("security-changelog")
        print("✅ Security changelog getoond.")

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "scan-code": self.scan_code,
            "generate-checklist": self.generate_checklist,
            "review-dependency": self.review_dependency,
            "generate-compliance-report": self.generate_compliance_report,
            "show-best-practices": self.show_best_practices,
            "export-scan-report": self.export_scan_report,
            "show-changelog": self.show_changelog,
            "show-collaboration": self.show_collaboration,
        }
        func = commands.get(command)
        if func:
            func()
        else:
            print(f"❌ Onbekend commando: {command}")
            print("💡 Gebruik 'help' voor beschikbare commando's.")
            self.show_help()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Security Developer Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = SecurityDeveloperAgent()
    agent.run(args.command)
