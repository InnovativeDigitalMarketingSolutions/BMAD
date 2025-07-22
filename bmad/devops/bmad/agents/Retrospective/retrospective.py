from pathlib import Path

# ... bestaande code ...

    def show_last_retro(self):
        self.log("show-last-retro")
        print("🕑 Laatste Retro-rapport:")
        path = DATA_PATHS.get("retro-history")
        if path and path.exists():
            content = path.read_text().strip().split("# Sprint Retrospective ")
            if len(content) > 1:
                print("# Sprint Retrospective " + content[-1])
            else:
                print("Geen retro-rapporten gevonden.")
        else:
            print("Geen retro-rapporten gevonden.")
        print("✅ Laatste retro getoond.")

    def list_retros(self):
        self.log("list-retros")
        print("📚 Alle Retro-rapporten:")
        path = DATA_PATHS.get("retro-history")
        if path and path.exists():
            content = path.read_text().strip().split("# Sprint Retrospective ")
            for i, retro in enumerate(content[1:], 1):
                print(f"---\n# Sprint Retrospective {retro.strip()}\n")
        else:
            print("Geen retro-rapporten gevonden.")
        print("✅ Alle retros getoond.")

    def show_feedback(self):
        self.log("show-feedback")
        print("💬 Feedback uit de sprint:")
        self.show_data("feedback")
        print("✅ Feedback getoond.")

    def show_velocity(self):
        self.log("show-velocity")
        print("🏃 Velocity van de sprint:")
        self.show_data("velocity")
        print("✅ Velocity getoond.")

# ... bestaande code ...

    def show_help(self):
        print("""🔄 Retrospective Agent - Beschikbare commando's:
- generate-retro: Genereer een retro-rapport op basis van sprintdata
- show-last-retro: Toon het laatste retro-rapport
- list-retros: Toon alle retro-rapporten
- export-retro: Exporteer retro-rapport(en) naar Markdown of CSV
- show-feedback: Toon feedback uit de sprint
- show-velocity: Toon velocity van de sprint
- show-best-practices: Toon best practices voor retrospectives
- show-changelog: Toon changelog van retro-rapporten
- show-collaboration: Toon samenwerking met andere agents
- show-version: Toon agentversie
- help: Toon deze help
        """)
        print("""
📋 Uitleg per commando:
- generate-retro: Toont retro-template en logt de actie
- show-last-retro: Toont het laatste retro-rapport uit retro-history
- list-retros: Toont alle retro-rapporten uit retro-history
- export-retro: Toont export templates (MD/CSV) en logt de actie
- show-feedback: Toont feedback uit de sprint
- show-velocity: Toont velocity van de sprint
- show-best-practices: Toont best practices voor retrospectives
- show-changelog: Toont changelog van retro-rapporten
- show-collaboration: Toont samenwerking met Scrummaster, Test, PO, Dev, etc.
- show-version: Toont de huidige versie van de agent
        """)

# ... bestaande code ...

    def run(self, command):
        if command in ["help", "--help", "-h", None]:
            self.show_help()
            return
        if command == "show-version":
            self.show_version()
            return
        commands = {
            "generate-retro": self.generate_retro,
            "show-last-retro": self.show_last_retro,
            "list-retros": self.list_retros,
            "export-retro": self.export_retro,
            "show-feedback": self.show_feedback,
            "show-velocity": self.show_velocity,
            "show-best-practices": self.show_best_practices,
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

# ... bestaande code ...