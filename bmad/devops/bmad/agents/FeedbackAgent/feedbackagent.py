import argparse
from pathlib import Path
from datetime import datetime

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "feedback-form": RESOURCE_BASE / "templates/feedbackagent/feedback-form-template.md",
    "feedback-report": RESOURCE_BASE / "templates/feedbackagent/feedback-report-template.md",
    "best-practices": RESOURCE_BASE / "templates/feedbackagent/best-practices.md",
    "export-csv": RESOURCE_BASE / "templates/feedbackagent/feedback-export-template.csv",
    "export-json": RESOURCE_BASE / "templates/feedbackagent/feedback-export-template.json"
}
DATA_PATHS = {
    "feedback-history": RESOURCE_BASE / "data/feedbackagent/feedback-history.md",
    "feedback-trends": RESOURCE_BASE / "data/feedbackagent/feedback-trends.md",
    "feedback-changelog": RESOURCE_BASE / "data/feedbackagent/feedback-changelog.md"
}
AGENT_VERSION = "1.0.0"
LOG_PATH = RESOURCE_BASE / "data/feedbackagent/feedbackagent-log.md"

class FeedbackAgent:
    def __init__(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat()}] Feedback Agent: {message}\n")
        except Exception as e:
            print(f"⚠️  Logging fout: {e}")

    def show_help(self):
        print("""📝 Feedback Agent - Beschikbare commando's:
- collect-feedback: Verzamel nieuwe feedback
- analyze-feedback: Analyseer feedback op trends
- generate-feedback-report: Genereer feedbackrapport
- show-feedback-history: Toon feedbackhistorie
- export-feedback: Exporteer feedback naar CSV/JSON
- show-best-practices: Toon best practices voor feedback
- show-collaboration: Toon samenwerking met andere agents
- show-version: Toon agentversie
- help: Toon deze help
        """)
        print("""
📋 Uitleg per commando:
- collect-feedback: Toont feedbackformulier template en logt de actie
- analyze-feedback: Toont feedbacktrends en logt de actie
- generate-feedback-report: Toont feedbackrapport template en logt de actie
- show-feedback-history: Toont feedbackhistorie en logt de actie
- export-feedback: Toont export templates (CSV/JSON) en logt de actie
- show-best-practices: Toont best practices voor feedbackverwerking
- show-collaboration: Toont samenwerking met PO, UX/UI, Test, R&D
- show-version: Toont de huidige versie van de agent
        """)

    def show_version(self):
        print(f"📝 Feedback Agent versie: {AGENT_VERSION}")

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
        print("""🤝 Feedback Agent - Samenwerking met andere agents:

🔗 **Product Owner**: Ontvangt en verwerkt feedback voor backlog en visie
🔗 **UX/UI Designer**: Gebruikt feedback voor designverbeteringen
🔗 **Test Engineer**: Integreert feedback in testscenario's en kwaliteitsverbetering
🔗 **R&D Agent**: Gebruikt feedback voor innovatie en validatie van nieuwe ideeën
        """)
        print("✅ Samenwerking overzicht getoond.")

    def collect_feedback(self):
        self.log("collect-feedback")
        print("📝 Feedbackformulier:")
        self.show_resource("feedback-form")
        print("✅ Feedbackformulier template getoond.")

    def analyze_feedback(self):
        self.log("analyze-feedback")
        print("📊 Feedback Analyse:")
        self.show_data("feedback-trends")
        print("✅ Feedbacktrends getoond.")

    def generate_feedback_report(self):
        self.log("generate-feedback-report")
        print("📄 Feedbackrapport:")
        self.show_resource("feedback-report")
        print("✅ Feedbackrapport template getoond.")

    def show_feedback_history(self):
        self.log("show-feedback-history")
        print("📚 Feedbackhistorie:")
        self.show_data("feedback-history")
        print("✅ Feedbackhistorie getoond.")

    def export_feedback(self):
        self.log("export-feedback")
        print("📤 Feedback exporteren:")
        self.show_resource("export-csv")
        self.show_resource("export-json")
        print("✅ Export templates (CSV/JSON) getoond.")

    def show_best_practices(self):
        self.log("show-best-practices")
        print("📚 Best Practices Feedback:")
        self.show_resource("best-practices")
        print("✅ Best practices getoond.")

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "collect-feedback": self.collect_feedback,
            "analyze-feedback": self.analyze_feedback,
            "generate-feedback-report": self.generate_feedback_report,
            "show-feedback-history": self.show_feedback_history,
            "export-feedback": self.export_feedback,
            "show-best-practices": self.show_best_practices,
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
    parser = argparse.ArgumentParser(description="Feedback Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    args = parser.parse_args()
    agent = FeedbackAgent()
    agent.run(args.command)
