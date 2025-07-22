import argparse
from pathlib import Path
from datetime import datetime

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "wireframe": RESOURCE_BASE / "templates/uxuidesigner/wireframe-template.md",
    "component-spec": RESOURCE_BASE / "templates/uxuidesigner/component-spec-template.md",
    "design-tokens": RESOURCE_BASE / "templates/uxuidesigner/design-tokens-template.json",
    "component-spec-export-md": RESOURCE_BASE / "templates/uxuidesigner/component-spec-export-template.md",
    "component-spec-export-json": RESOURCE_BASE / "templates/uxuidesigner/component-spec-export-template.json",
    "best-practices": RESOURCE_BASE / "templates/uxuidesigner/best-practices.md"
}
DATA_PATHS = {
    "feedback": RESOURCE_BASE / "data/uxuidesigner/feedback.md",
    "design-history": RESOURCE_BASE / "data/uxuidesigner/design-history.md",
    "design-changelog": RESOURCE_BASE / "data/uxuidesigner/design-changelog.md"
}
AGENT_VERSION = "1.0.0"
LOG_PATH = RESOURCE_BASE / "data/uxuidesigner/uxuidesigneragent-log.md"

class UXUIDesignerAgent:
    def __init__(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] UX/UI Designer Agent: {message}\n")
        except Exception as e:
            print(f"⚠️  Logging fout: {e}")

    def show_help(self):
        print("""🎨 UX/UI Designer Agent - Beschikbare commando's:
- generate-wireframe: Genereer een wireframe voor een feature of user flow
- design-component: Genereer een UI-component specificatie
- export-design-tokens: Exporteer design tokens naar JSON of CSS
- show-feedback: Toon gebruikersfeedback en design history
- show-best-practices: Toon best practices voor UX/UI design
- export-component-spec: Exporteer component specs naar Markdown of JSON
- show-changelog: Toon changelog van designbeslissingen
- show-collaboration: Toon samenwerking met andere agents
- show-version: Toon agentversie
- help: Toon deze help
        """)
        print("""
📋 Uitleg per commando:
- generate-wireframe: Toont wireframe-template en logt de actie
- design-component: Toont component-spec-template en logt de actie
- export-design-tokens: Toont design tokens template en logt de actie
- show-feedback: Toont gebruikersfeedback en design history
- show-best-practices: Toont best practices voor UX/UI design
- export-component-spec: Toont export templates (MD/JSON) en logt de actie
- show-changelog: Toont changelog van designbeslissingen
- show-collaboration: Toont samenwerking met frontend, PO, accessibility, test
- show-version: Toont de huidige versie van de agent
        """)

    def show_version(self):
        print(f"🎨 UX/UI Designer Agent versie: {AGENT_VERSION}")

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
        print("""🤝 UX/UI Designer Agent - Samenwerking met andere agents:

Deze agent werkt samen met frontend developers, product owner, accessibility agent en test engineer om optimale gebruikerservaringen te realiseren. Feedback en specs worden gedeeld met het hele team.
        """)
        print("✅ Samenwerking overzicht getoond.")

    def generate_wireframe(self):
        self.log("generate-wireframe")
        print("🖼️ Wireframe:")
        self.show_resource("wireframe")
        print("✅ Wireframe template getoond.")

    def design_component(self):
        self.log("design-component")
        print("🧩 Component Specificatie:")
        self.show_resource("component-spec")
        print("✅ Component spec template getoond.")

    def export_design_tokens(self):
        self.log("export-design-tokens")
        print("🎨 Design Tokens:")
        self.show_resource("design-tokens")
        print("✅ Design tokens template getoond.")

    def show_feedback(self):
        self.log("show-feedback")
        print("💬 Gebruikersfeedback:")
        self.show_data("feedback")
        print("📚 Design History:")
        self.show_data("design-history")
        print("✅ Feedback en design history getoond.")

    def show_best_practices(self):
        self.log("show-best-practices")
        print("📚 Best Practices UX/UI:")
        self.show_resource("best-practices")
        print("✅ Best practices getoond.")

    def export_component_spec(self):
        self.log("export-component-spec")
        print("📤 Component Spec Export:")
        self.show_resource("component-spec-export-md")
        self.show_resource("component-spec-export-json")
        print("✅ Export templates (MD/JSON) getoond.")

    def show_changelog(self):
        self.log("show-changelog")
        print("🗒️ Design Changelog:")
        self.show_data("design-changelog")
        print("✅ Design changelog getoond.")

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "generate-wireframe": self.generate_wireframe,
            "design-component": self.design_component,
            "export-design-tokens": self.export_design_tokens,
            "show-feedback": self.show_feedback,
            "show-best-practices": self.show_best_practices,
            "export-component-spec": self.export_component_spec,
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
    parser = argparse.ArgumentParser(description="UX/UI Designer Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = UXUIDesignerAgent()
    agent.run(args.command)
