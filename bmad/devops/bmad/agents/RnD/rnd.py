    def show_help(self):
        print("""
🔬 R&D Agent - Beschikbare commando's:
- help: Toon beschikbare R&D commando's
- trend-scan: Scan op relevante technologische trends
- generate-poc: Genereer proof-of-concept voorstel
- generate-innovation-roadmap: Genereer innovatie-roadmap
- refine-vision: Werk productvisie bij
- show-feedback: Toon feedback uit experimenten
- export-research: Exporteer onderzoeksresultaten (md/json/csv/yaml)
- changelog: Toon changelog van onderzoeksbeslissingen
- test: Test resource completeness

Samenwerking: Werkt samen met alle agents voor innovatie en trendonderzoek, inclusief Scrummaster voor sprintplanning en voortgangsbewaking.
        """)

    # ... bestaande methodes ...

    def export_research(self, format="md"):
        logging.info(f"Onderzoeksresultaten geëxporteerd in {format} formaat")
        print(f"📤 Onderzoeksresultaten Export ({format}):")
        if format == "json":
            print('{"research": "data", "format": "json"}')
        elif format == "csv":
            print("research,format,date\nR&D data,csv,2024-06-10")
        elif format == "yaml":
            print("research: data\nformat: yaml\ndate: 2024-06-10")
        else:
            self.show_resource("trend-scan")