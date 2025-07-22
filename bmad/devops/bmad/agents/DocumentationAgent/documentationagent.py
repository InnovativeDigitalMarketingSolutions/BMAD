from pathlib import Path

DATA_PATHS = {
    "onboarding-history": Path("path/to/onboarding-history.txt")
}

TEMPLATE_PATHS = {
    "api-docs": Path("path/to/api-docs.md"),
    "onboarding-guide": Path("path/to/onboarding-guide.md"),
    "changelog": Path("path/to/changelog.md"),
    "best-practices": Path("path/to/best-practices.md"),
    "export-md": Path("path/to/export-md.md"),
    "export-pdf": Path("path/to/export-pdf.pdf"),
    "export-html": Path("path/to/export-html.html"),
    "collaboration": Path("path/to/collaboration.md")
}

class DocumentationAgent:
    def __init__(self):
        self.version = "1.0.0"

    def log(self, action):
        print(f"[LOG] {action}")

    def show_version(self):
        print(f"📦 Documentation Agent - Versie: {self.version}")

    def generate_api_docs(self):
        self.log("generate-api-docs")
        print("📝 Generating API documentation...")
        self.show_resource("api-docs")
        print("✅ API documentation generated.")

    def generate_onboarding_guide(self):
        self.log("generate-onboarding-guide")
        print("📝 Generating onboarding guide...")
        self.show_resource("onboarding-guide")
        print("✅ Onboarding guide generated.")

    def generate_changelog(self):
        self.log("generate-changelog")
        print("📝 Generating changelog...")
        self.show_resource("changelog")
        print("✅ Changelog generated.")

    def review_docs(self):
        self.log("review-docs")
        print("📝 Reviewing documentation...")
        print("✅ Documentation reviewed.")

    def show_best_practices(self):
        self.log("show-best-practices")
        print("📚 Best Practices for Documentation:")
        self.show_resource("best-practices")
        print("✅ Best practices shown.")

    def export_docs(self):
        self.log("export-docs")
        print("📤 Exporting documentation...")
        self.show_resource("export-md")
        self.show_resource("export-pdf")
        self.show_resource("export-html")
        print("✅ Documentation exported.")

    def show_collaboration(self):
        self.log("show-collaboration")
        print("🤝 Collaboration with other agents:")
        self.show_resource("collaboration")
        print("✅ Collaboration shown.")

    def show_data(self, key):
        path = DATA_PATHS.get(key)
        if path and path.exists():
            print(path.read_text())
        else:
            print(f"⚠️  Geen data gevonden voor: {key}")

    def show_onboarding_history(self):
        self.log("show-onboarding-history")
        print("👋 Onboarding History:")
        self.show_data("onboarding-history")
        print("✅ Onboarding history getoond.")

    def show_resource(self, key):
        path = TEMPLATE_PATHS.get(key)
        if path and path.exists():
            if path.suffix == '.pdf':
                print(f"[PDF-bestand: {path}] (Open dit bestand met een PDF-viewer)")
            else:
                print(path.read_text())
        else:
            print(f"⚠️  Geen resource gevonden voor: {key}")

    def show_help(self):
        print("""📚 Documentation Agent - Beschikbare commando's:
- generate-api-docs: Genereer API documentatie
- generate-onboarding-guide: Genereer onboarding guide
- generate-changelog: Genereer changelog
- review-docs: Review bestaande documentatie
- show-onboarding-history: Toon onboarding history
- show-best-practices: Toon best practices voor documentatie
- export-docs: Exporteer documentatie naar Markdown, PDF of HTML
- show-collaboration: Toon samenwerking met andere agents
- show-version: Toon agentversie
- help: Toon deze help
        """)
        print("""
📋 Uitleg per commando:
- generate-api-docs: Toont API docs template en logt de actie
- generate-onboarding-guide: Toont onboarding guide template en logt de actie
- generate-changelog: Toont changelog template en logt de actie
- review-docs: Toont docs-history en logt de actie
- show-onboarding-history: Toont onboarding history en logt de actie
- show-best-practices: Toont best practices voor documentatie
- export-docs: Toont export templates (MD/PDF/HTML) en logt de actie
- show-collaboration: Toont samenwerking met alle agents
- show-version: Toont de huidige versie van de agent
        """)

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "generate-api-docs": self.generate_api_docs,
            "generate-onboarding-guide": self.generate_onboarding_guide,
            "generate-changelog": self.generate_changelog,
            "review-docs": self.review_docs,
            "show-onboarding-history": self.show_onboarding_history,
            "show-best-practices": self.show_best_practices,
            "export-docs": self.export_docs,
            "show-collaboration": self.show_collaboration,
        }
        func = commands.get(command)
        if func:
            func()
        else:
            print(f"❌ Onbekend commando: {command}")
            print("💡 Gebruik 'help' voor beschikbare commando's.")
            self.show_help()