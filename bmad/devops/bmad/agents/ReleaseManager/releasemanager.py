import argparse
from pathlib import Path
from datetime import datetime

RESOURCE_BASE = Path(__file__).parent.parent.parent / "resources"
TEMPLATE_PATHS = {
    "release-plan": RESOURCE_BASE / "templates/releasemanager/release-plan-template.md",
    "changelog": RESOURCE_BASE / "templates/releasemanager/changelog-template.md",
    "release-notes": RESOURCE_BASE / "templates/releasemanager/release-notes-template.md",
    "deployment-checklist": RESOURCE_BASE / "templates/releasemanager/deployment-checklist.md",
    "best-practices": RESOURCE_BASE / "templates/releasemanager/best-practices.md"
}
DATA_PATHS = {
    "release-history": RESOURCE_BASE / "data/releasemanager/release-history.md",
    "deployment-history": RESOURCE_BASE / "data/releasemanager/deployment-history.md",
    "release-metrics": RESOURCE_BASE / "data/releasemanager/release-metrics.md"
}
AGENT_VERSION = "1.0.0"
LOG_PATH = RESOURCE_BASE / "data/releasemanager/releasemanager-log.md"

class ReleaseManagerAgent:
    def log(self, message):
        with open(LOG_PATH, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

    def show_help(self):
        print("""Beschikbare commando's:
- plan-release: Plan een nieuwe release (optioneel: --release-id)
- generate-changelog: Genereer changelog
- generate-release-notes: Genereer release notes
- check-deployment: Voer deployment check uit
- rollback-release: Voer een rollback van een release uit (optioneel: --release-id)
- release-metrics: Toon releasestatistieken
- notify-release: Informeer andere agents over een nieuwe release
- show-best-practices: Toon release best practices
- show-version: Toon agentversie
- help: Toon deze help
        """)
        print("""
Uitleg per commando:
- plan-release: Toont het releaseplan en logt de actie. Optioneel kun je een release-ID meegeven.
- generate-changelog: Toont het changelog-template en logt de actie.
- generate-release-notes: Toont het release notes-template en logt de actie.
- check-deployment: Toont de deployment checklist en logt de actie.
- rollback-release: Voert een rollback uit (optioneel: geef een release-ID mee).
- release-metrics: Toont release metrics uit het data-bestand.
- notify-release: Simuleert het informeren van andere agents (message bus/event).
- show-best-practices: Toont best practices voor release management.
- show-version: Toont de huidige versie van de agent.
        """)

    def show_version(self):
        print(f"Release Manager Agent versie: {AGENT_VERSION}")

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

    def plan_release(self, release_id=None):
        self.log(f"plan-release {release_id or ''}")
        self.show_resource("release-plan")
        print(f"✅ Release gepland{' voor ' + release_id if release_id else ''}.")

    def generate_changelog(self):
        self.log("generate-changelog")
        self.show_resource("changelog")
        print("✅ Changelog gegenereerd.")

    def generate_release_notes(self):
        self.log("generate-release-notes")
        self.show_resource("release-notes")
        print("✅ Release notes gegenereerd.")

    def check_deployment(self):
        self.log("check-deployment")
        self.show_resource("deployment-checklist")
        print("✅ Deployment check uitgevoerd.")

    def rollback_release(self, release_id=None):
        self.log(f"rollback-release {release_id or ''}")
        print(f"Rollback van release {release_id or '[onbekend]'} uitgevoerd. [voorbeeldoutput]")
        print("✅ Rollback uitgevoerd.")

    def release_metrics(self):
        self.log("release-metrics")
        self.show_data("release-metrics")
        print("✅ Release metrics getoond.")

    def notify_release(self, release_id=None):
        self.log(f"notify-release {release_id or ''}")
        print(f"[Message bus] Andere agents geïnformeerd over release {release_id or '[onbekend]'}.")
        print("✅ Notificatie verzonden.")

    def show_best_practices(self):
        self.log("show-best-practices")
        self.show_resource("best-practices")
        print("✅ Best practices getoond.")

    def run(self, command, **kwargs):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "plan-release": lambda: self.plan_release(kwargs.get("release_id")),
            "generate-changelog": self.generate_changelog,
            "generate-release-notes": self.generate_release_notes,
            "check-deployment": self.check_deployment,
            "rollback-release": lambda: self.rollback_release(kwargs.get("release_id")),
            "release-metrics": self.release_metrics,
            "notify-release": lambda: self.notify_release(kwargs.get("release_id")),
            "show-best-practices": self.show_best_practices,
        }
        func = commands.get(command)
        if func:
            func()
        else:
            print(f"Onbekend commando: {command}")
            self.show_help()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Release Manager Agent")
    parser.add_argument("command", help="Commando om uit te voeren")
    parser.add_argument("--release-id", help="ID van de release (optioneel)")
    args = parser.parse_args()
    agent = ReleaseManagerAgent()
    agent.run(args.command, release_id=args.release_id)
