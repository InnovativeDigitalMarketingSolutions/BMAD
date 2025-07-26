# Multi-Project Architecture Guide

## Overzicht

BMAD ondersteunt nu multi-project configuratie, waardoor je meerdere projecten kunt beheren met één ClickUp account maar verschillende folders en lists per project. Dit zorgt voor project isolatie terwijl je de voordelen van gedeelde agent expertise behoudt.

## Architectuur

### Project-Scoped Agents

Elke agent kan werken met meerdere projecten door project scoping:

```
ClickUp Account (één API key)
├── Space (gedeeld)
    ├── Folder: CoPilot Project
    │   ├── List: Backlog
    │   ├── List: Sprint Tasks
    │   └── List: Completed
    ├── Folder: Client A Project
    │   ├── List: Requirements
    │   ├── List: Development
    │   └── List: Testing
    └── Folder: Client B Project
        ├── List: Features
        ├── List: Bugs
        └── List: Releases
```

### Agent Pooling

Agents worden gedeeld tussen projecten maar werken met project-specifieke context:

```
Agent Pool
├── ProductOwner (werkt met project A, B, C)
├── ScrumMaster (werkt met project A, B, C)
├── Architect (werkt met project A, B, C)
└── Developers (toegewezen per project)
```

## Configuratie

### 1. Environment Variables

Basis configuratie in `.env`:
```bash
# Gedeelde ClickUp configuratie
CLICKUP_API_KEY=your_api_key_here
CLICKUP_SPACE_ID=your_space_id_here

# Optioneel: Default project configuratie
CLICKUP_FOLDER_ID=default_folder_id
CLICKUP_LIST_ID=default_list_id

# Actief project
BMAD_ACTIVE_PROJECT=default
```

### 2. Project Configuratie

Projecten worden geconfigureerd in `bmad/resources/data/general/projects_config.json`:

```json
{
  "copilot": {
    "name": "CoPilot AI Business Suite",
    "description": "AI-powered business suite",
    "clickup": {
      "folder_id": "111111111",
      "list_id": "222222222"
    },
    "agents": {
      "product_owner": "copilot_po",
      "scrum_master": "copilot_sm"
    },
    "settings": {
      "auto_sync": true,
      "webhook_enabled": true
    }
  }
}
```

## Project Management CLI

### Basis Commando's

```bash
# Toon alle projecten
python bmad/project_cli.py list

# Maak nieuw project aan
python bmad/project_cli.py create copilot "CoPilot Project" \
  --description "AI-powered business suite" \
  --folder-id "111111111" \
  --list-id "222222222"

# Stel actief project in
python bmad/project_cli.py active copilot

# Toon project details
python bmad/project_cli.py show copilot

# Update project configuratie
python bmad/project_cli.py update copilot --name "New Name"

# Test ClickUp integratie
python bmad/project_cli.py test-clickup copilot

# Verwijder project
python bmad/project_cli.py delete copilot
```

### Workflow Voorbeelden

#### 1. Nieuw Project Setup

```bash
# 1. Maak project aan
python bmad/project_cli.py create client_x "Client X Platform" \
  --description "E-commerce platform voor Client X" \
  --folder-id "777777777" \
  --list-id "888888888"

# 2. Stel actief project in
python bmad/project_cli.py active client_x

# 3. Test ClickUp integratie
python bmad/project_cli.py test-clickup

# 4. Begin met agent workflow
python bmad/agents/Agent/ProductOwner/productowner.py create-story
```

#### 2. Project Wisselen

```bash
# Schakel naar ander project
python bmad/project_cli.py active copilot

# Werk met CoPilot project
python bmad/agents/Agent/Scrummaster/scrummaster.py sprint-planning

# Schakel terug naar client project
python bmad/project_cli.py active client_x
```

## Agent Integratie

### Project-Scoped Context

Agents gebruiken automatisch project scoping:

```python
from bmad.agents.core.project_manager import project_manager
from bmad.agents.core.clickup_integration import ClickUpIntegration

# Agent krijgt automatisch project context
project_id = project_manager.active_project
clickup = ClickUpIntegration(project_id=project_id)

# Context wordt opgeslagen met project scope
project_scope = project_manager.get_project_scope(project_id)
save_context("ProductOwner", "user_stories", stories, scope=project_scope)
```

### Agent Commando's met Project Context

```bash
# ProductOwner werkt met actief project
python bmad/agents/Agent/ProductOwner/productowner.py create-story

# ScrumMaster plant sprint voor actief project
python bmad/agents/Agent/Scrummaster/scrummaster.py sprint-planning

# Architect ontwerpt voor actief project
python bmad/agents/Agent/Architect/architect.py design-system
```

## ClickUp Integratie

### Project-Specifieke Configuratie

Elk project heeft zijn eigen ClickUp configuratie:

```python
# Project A
clickup_a = ClickUpIntegration(project_id="client_a")
# Gebruikt folder_id: "333333333", list_id: "444444444"

# Project B  
clickup_b = ClickUpIntegration(project_id="client_b")
# Gebruikt folder_id: "555555555", list_id: "666666666"
```

### Task Management per Project

```python
# Taken worden automatisch in juiste project folder/list geplaatst
clickup_a.create_task("client_a", "Implement login", "User authentication")
clickup_b.create_task("client_b", "Add offline mode", "Offline functionality")
```

## Best Practices

### 1. Project Naming

- Gebruik korte, duidelijke project IDs: `copilot`, `client_a`, `client_b`
- Gebruik beschrijvende namen: `"CoPilot AI Business Suite"`
- Documenteer project doel en scope

### 2. ClickUp Organisatie

- **Space**: Gedeeld voor alle projecten
- **Folders**: Één per project
- **Lists**: Verschillende lists per project (Backlog, Sprint, Done, etc.)

### 3. Agent Management

- **Gedeelde Agents**: ProductOwner, ScrumMaster, Architect
- **Project-Specifieke Agents**: Developers kunnen per project worden toegewezen
- **Context Isolatie**: Elke agent werkt met project-specifieke context

### 4. Workflow Management

```bash
# Start nieuwe werkdag
python bmad/project_cli.py active copilot
python bmad/agents/Agent/Scrummaster/scrummaster.py daily-standup

# Wissel naar client project
python bmad/project_cli.py active client_a
python bmad/agents/Agent/ProductOwner/productowner.py create-story

# Terug naar hoofdproject
python bmad/project_cli.py active copilot
```

## Monitoring & Analytics

### Project Metrics

```python
# Haal metrics op per project
metrics_copilot = clickup_copilot.get_project_metrics("CoPilot")
metrics_client_a = clickup_client_a.get_project_metrics("Client A")

print(f"CoPilot completion rate: {metrics_copilot['completion_rate']}%")
print(f"Client A completion rate: {metrics_client_a['completion_rate']}%")
```

### Cross-Project Reporting

```python
# Vergelijk projecten
projects = project_manager.list_projects()
for project in projects:
    clickup = ClickUpIntegration(project_id=project["id"])
    metrics = clickup.get_project_metrics(project["name"])
    print(f"{project['name']}: {metrics['completion_rate']}%")
```

## Troubleshooting

### Veelvoorkomende Problemen

1. **Project niet gevonden**
   ```bash
   # Controleer beschikbare projecten
   python bmad/project_cli.py list
   
   # Stel correct project in
   python bmad/project_cli.py active project_id
   ```

2. **ClickUp configuratie fout**
   ```bash
   # Test ClickUp integratie
   python bmad/project_cli.py test-clickup project_id
   
   # Update configuratie
   python bmad/project_cli.py update project_id --folder-id "new_id"
   ```

3. **Context confusion**
   - Zorg dat je het juiste actieve project hebt ingesteld
   - Gebruik `python bmad/project_cli.py show` om huidige configuratie te controleren

### Debug Tips

```bash
# Debug project configuratie
python bmad/project_cli.py show

# Debug ClickUp integratie
python bmad/project_cli.py test-clickup

# Controleer environment variables
echo $BMAD_ACTIVE_PROJECT
echo $CLICKUP_API_KEY
```

## Migratie van Single-Project

Als je al een single-project setup hebt:

1. **Backup bestaande configuratie**
2. **Maak default project aan** met bestaande ClickUp IDs
3. **Test integratie** met default project
4. **Voeg nieuwe projecten toe** als nodig

```bash
# Maak default project met bestaande configuratie
python bmad/project_cli.py create default "Default Project" \
  --folder-id "$CLICKUP_FOLDER_ID" \
  --list-id "$CLICKUP_LIST_ID"

# Test dat alles nog werkt
python bmad/project_cli.py test-clickup default
```

## Toekomstige Uitbreidingen

### Geplande Features

1. **Project Templates**: Vooraf gedefinieerde project configuraties
2. **Agent Pooling**: Dynamische agent toewijzing per project
3. **Cross-Project Dependencies**: Taken die meerdere projecten beïnvloeden
4. **Project Analytics**: Uitgebreide reporting en metrics
5. **Automated Project Setup**: Scripts voor snelle project initialisatie

### Roadmap

- **Q1**: Project templates en agent pooling
- **Q2**: Cross-project dependencies en analytics
- **Q3**: Automated setup en advanced monitoring
- **Q4**: Multi-tenant support en enterprise features 