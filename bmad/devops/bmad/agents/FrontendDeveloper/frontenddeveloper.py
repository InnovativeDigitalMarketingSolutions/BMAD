def show_help(self):
    print("""
🎨 Frontend Developer Agent - Beschikbare commando's:
- help: Toon beschikbare Frontend Developer commando's
- build-component: Bouw of update een frontend component
- run-accessibility-check: Voer een accessibility check uit op component of pagina
- profile-performance: Voer performance profiling uit en genereer rapport
- export-storybook: Exporteer Storybook documentatie naar MDX of PDF
- show-best-practices: Toon best practices voor frontend development
- export-component: Exporteer component naar Markdown, JSON, CSV of YAML
- changelog: Toon changelog van componentwijzigingen
- test: Test resource completeness

Samenwerking: Werkt samen met UX/UI Designer, Test Engineer, Accessibility Agent, Product Owner en Scrummaster voor optimale kwaliteit en gebruikerservaring.
    """)

# ... bestaande methodes ...

def export_component(self, format="md"):
    logging.info(f"Component export uitgevoerd in {format} formaat")
    print(f"📤 Component Export ({format}):")
    if format == "json":
        self.show_resource("component-export-json")
    elif format == "csv":
        print("component,format,date\nFrontend component,csv,2024-06-10")
    elif format == "yaml":
        print("component: Frontend component\nformat: yaml\ndate: 2024-06-10")
    else:
        self.show_resource("component-export-md")