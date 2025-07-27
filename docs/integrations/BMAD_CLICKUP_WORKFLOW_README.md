# BMAD ClickUp Workflow

Dit document beschrijft hoe je de BMAD agents kunt gebruiken om ClickUp spaces automatisch aan te passen aan de BMAD workflow en frontend planningen te genereren.

## 🚀 Snelle Start

### 1. Environment Setup
Zorg dat je `.env` file geladen is:
```bash
source .env
```

### 2. Complete Workflow Uitvoeren
```bash
# Python script
python bmad_clickup_workflow.py

# Of via CLI
python bmad_cli_clickup.py full-workflow bmad-frontend
```

## 📋 Beschikbare Commando's

### Python Script
```bash
# Complete workflow (template + planning + ClickUp creatie)
python bmad_clickup_workflow.py
```

### CLI Commando's
```bash
# Template aanpassen aan BMAD workflow
python bmad_cli_clickup.py adapt-template [project_id]

# Frontend planning genereren
python bmad_cli_clickup.py generate-planning [project_id]

# Sprints aanmaken in ClickUp
python bmad_cli_clickup.py create-sprints [project_id]

# Complete workflow uitvoeren
python bmad_cli_clickup.py full-workflow [project_id]

# Projecten overzicht
python bmad_cli_clickup.py list-projects
```

## 🔧 Wat Doen de Agents?

### ProductOwner Agent
- **User Stories Genereren**: Maakt user stories aan op basis van project requirements
- **Acceptance Criteria**: Definieert duidelijke acceptatiecriteria voor elke story
- **Prioriteiten**: Stelt prioriteiten in (Critical, High, Medium, Low)
- **Story Points**: Schat de complexiteit van elke story

### ScrumMaster Agent
- **Sprint Planning**: Verdeelt user stories over sprints
- **Sprint Structuur**: Maakt sprint folders en lists aan in ClickUp
- **Ceremonies**: Voegt sprint ceremonies toe (planning, review, retrospective)
- **Team Capaciteit**: Houdt team velocity en capaciteit bij

### Gezamenlijke Workflow
1. **Template Aanpassing**: Past ClickUp template aan aan BMAD workflow
2. **Planning Generatie**: Genereert complete frontend planning
3. **ClickUp Creatie**: Maakt folders, lists en custom fields aan
4. **Task Creatie**: Voegt user stories en taken toe aan de juiste sprints

## 📁 ClickUp Structuur

De agents maken de volgende structuur aan in je ClickUp space:

```
📋 Product Backlog/
├── 🎯 Epics
├── 📝 User Stories
└── 🔧 Technical Tasks

🏃‍♂️ Sprint Management/
├── 📅 Sprint Planning
├── 🔄 Sprint Backlog
├── 📊 Sprint Review
└── 🔄 Sprint Retrospective

📚 Documentation/
├── 📖 Technical Docs
└── 🎨 Design Assets
```

### Custom Fields
Elke list krijgt relevante custom fields:
- **Story Points**: Voor effort schatting
- **Priority**: Critical/High/Medium/Low
- **Acceptance Criteria**: Voor user stories
- **Sprint**: Voor sprint assignment
- **Status**: Voor task tracking

## 🎯 Frontend Planning Voorbeeld

Het script genereert een complete planning voor een BMAD frontend met:

### Sprint 1: Foundation & Setup (2 weken)
- Project setup & architecture
- Authentication system
- Basic layout & navigation

### Sprint 2: Dashboard & Core Features (2 weken)
- Project dashboard
- Agent management interface
- Real-time notifications

### Sprint 3: ClickUp Integration & Advanced Features (2 weken)
- ClickUp integration dashboard
- Configuration management
- Logs & debugging tools

### Sprint 4: Polish & Launch (2 weken)
- Mobile responsiveness
- Dark/light mode
- Performance optimization
- Testing & documentation

## 📊 Output Bestanden

Het script genereert verschillende bestanden:

### JSON Bestanden
- `bmad_template_[project]_[timestamp].json`: Aangepaste ClickUp template
- `bmad_planning_[project]_[timestamp].json`: Frontend planning met sprints

### Markdown Rapport
- `bmad_frontend_planning_[timestamp].md`: Uitgebreid planning rapport

## 🔍 Troubleshooting

### Veelvoorkomende Problemen

#### 1. API Key Problemen
```bash
❌ CLICKUP_API_KEY niet gevonden in environment
```
**Oplossing**: Zorg dat je `.env` file geladen is:
```bash
source .env
```

#### 2. Space ID Niet Gevonden
```bash
❌ Space ID niet geconfigureerd
```
**Oplossing**: Controleer je `projects_config.json`:
```json
{
  "bmad-frontend": {
    "name": "BMAD Frontend",
    "clickup": {
      "space_id": "90155930087"
    }
  }
}
```

#### 3. LLM Problemen
```bash
⚠️ LLM error, gebruik fallback user stories
```
**Oplossing**: Controleer je `OPENAI_API_KEY` in `.env`

### Debug Mode
Voor meer details, voeg debug logging toe:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎨 Customization

### Template Aanpassen
Je kunt het BMAD template aanpassen in `bmad_clickup_workflow.py`:

```python
def adapt_clickup_template_to_bmad(self):
    # Pas hier je template aan
    bmad_template = {
        "folders": [
            {
                "name": "Jouw Custom Folder",
                "lists": [...]
            }
        ]
    }
```

### Planning Aanpassen
Pas de frontend planning aan in `generate_frontend_planning()`:

```python
def generate_frontend_planning(self):
    # Pas hier je planning aan
    frontend_requirements = """
    Jouw custom requirements hier...
    """
```

## 🔄 Workflow Integratie

### Met Bestaande BMAD Workflow
De agents integreren naadloos met de bestaande BMAD workflow:

1. **ProductOwner** genereert user stories
2. **Architect** maakt technische designs
3. **ScrumMaster** plant sprints
4. **DocumentationAgent** maakt documentatie
5. **ClickUp Integration** synchroniseert alles

### Webhook Integratie
Voor real-time synchronisatie, configureer ClickUp webhooks:

```yaml
# In agent configuratie
clickup_webhooks:
  - event: "taskCreated"
    url: "https://your-bmad-api.com/webhooks/clickup"
  - event: "taskUpdated"
    url: "https://your-bmad-api.com/webhooks/clickup"
```

## 📈 Metrics & Monitoring

Het script genereert metrics voor:
- **Story Points per Sprint**: Voor velocity tracking
- **Task Completion**: Voor burndown charts
- **Team Performance**: Voor retrospectives

## 🚀 Volgende Stappen

Na het uitvoeren van het script:

1. **Review Planning**: Bekijk de gegenereerde planning in ClickUp
2. **Team Kickoff**: Plan een sprint kickoff meeting
3. **Capacity Planning**: Bepaal team capaciteit per sprint
4. **Technical Architecture**: Plan een architectuur sessie
5. **Start Sprint 1**: Begin met de eerste sprint!

## 📞 Support

Voor vragen of problemen:
1. Check de troubleshooting sectie
2. Review de logs in de terminal
3. Controleer je ClickUp API permissions
4. Verify je BMAD project configuratie

---

**Happy Planning! 🎉** 