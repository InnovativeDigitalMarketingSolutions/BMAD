    def show_help(self):
        print("""
🔧 Backend Developer Agent - Beschikbare commando's:
- help: Toon beschikbare Backend Developer commando's
- build-api: Bouw of update een API endpoint
- optimize-db: Optimaliseer database queries en schema
- monitor-api: Monitor API performance en health
- test-integration: Test externe integraties
- generate-docs: Genereer API documentatie
- security-scan: Voer security scan uit op backend code
- export-api: Exporteer API specs naar OpenAPI, JSON, YAML of CSV
- changelog: Toon changelog van backend wijzigingen
- test: Test resource completeness

Samenwerking: Werkt samen met Fullstack Developer, Frontend Developer, DevOps/Infra, Architect, Test Engineer, Security Developer, Product Owner en Scrummaster voor optimale backend kwaliteit en performance.
        """)

    # ... bestaande methodes ...

    def export_api(self, format="md"):
        logging.info(f"API export uitgevoerd in {format} formaat")
        print(f"📤 API Export ({format}):")
        if format == "json":
            self.show_resource("api-export-json")
        elif format == "yaml":
            print("openapi: 3.0.0\ninfo:\n  title: Backend API\n  version: 1.0.0")
        elif format == "openapi":
            print("openapi: 3.0.0\ninfo:\n  title: Backend API\n  version: 1.0.0\npaths:\n  /api/v1:\n    get:\n      summary: API endpoint")
        elif format == "csv":
            print("endpoint,method,description,status\n/api/v1,GET,API endpoint,active")
        else:
            self.show_resource("api-export-md")