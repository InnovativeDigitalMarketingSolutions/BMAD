# BMAD Project Management

## 📋 Overzicht

De BMAD Project Manager is een centraal systeem voor het beheren van project configuraties, requirements, en context voor alle BMAD agents.

## 🏗️ Architectuur

### Project Manager vs Agents

| Component | Type | Locatie | Functie |
|-----------|------|---------|---------|
| **Project Manager** | Utility/Service | `/projects/` | Project configuratie & context |
| **Agents** | AI/LLM Workers | `/agents/` | Specifieke taken (Frontend, UX, etc.) |

### Bestandsstructuur

```
bmad/projects/
├── project_manager.py  # Core project management class
├── cli.py             # Command-line interface
└── configs/           # Project configuratie files (.json)
    ├── project1.json
    ├── project2.json
    └── ...
```

## 🚀 Gebruik

### CLI Commando's

```bash
# Toon alle projecten
python3 bmad/projects/cli.py list

# Maak nieuw project
python3 bmad/projects/cli.py create my-project --type web_app

# Laad project
python3 bmad/projects/cli.py load my-project

# Toon project info
python3 bmad/projects/cli.py info

# Voeg requirement toe
python3 bmad/projects/cli.py add-requirement "User authentication required"

# Voeg user story toe
python3 bmad/projects/cli.py add-story "As a user, I want to log in"

# Interactieve modus
python3 bmad/projects/cli.py interactive
```

### Programmatisch Gebruik

```python
from bmad.projects.project_manager import project_manager

# Maak nieuw project
config = project_manager.create_project("my-app", "web_app")

# Laad project
config = project_manager.load_project("my-app")

# Voeg requirement toe
project_manager.add_requirement("Responsive design", "non_functional")

# Haal project context op
context = project_manager.get_project_context()
```

## 📊 Project Types

### Web App
```json
{
  "project_type": "web_app",
  "tech_stack": {
    "frontend": ["React", "TypeScript", "Vite"],
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Docker", "AWS/GCP"]
  },
  "architecture": {
    "type": "microservices",
    "frontend": "SPA",
    "backend": "REST API"
  }
}
```

### Mobile App
```json
{
  "project_type": "mobile_app",
  "tech_stack": {
    "frontend": ["React Native", "TypeScript"],
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Expo", "App Store"]
  }
}
```

### API Service
```json
{
  "project_type": "api_service",
  "tech_stack": {
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Docker", "Kubernetes"]
  }
}
```

## 🔄 Event System

De Project Manager publiceert events naar het message bus systeem:

### Events
- `project_loaded` - Wanneer een project wordt geladen
- `project_updated` - Wanneer project configuratie wordt bijgewerkt
- `requirement_added` - Wanneer een requirement wordt toegevoegd
- `user_story_added` - Wanneer een user story wordt toegevoegd

### Event Handlers
Agents kunnen luisteren naar deze events:

```python
from bmad.agents.core.message_bus import subscribe

def on_project_loaded(event):
    project_name = event["project_name"]
    config = event["config"]
    print(f"Project {project_name} loaded for agent processing")

subscribe("project_loaded", on_project_loaded)
```

## 📋 Project Context

De Project Manager biedt context voor alle agents:

```python
context = project_manager.get_project_context()

# Beschikbare context:
{
    "project_name": "my-app",
    "config": {...},
    "requirements": {
        "functional": [...],
        "non_functional": [...],
        "technical": [...]
    },
    "user_stories": [...],
    "tech_stack": {...},
    "architecture": {...},
    "api_endpoints": [...],
    "database_schema": {...},
    "deployment_config": {...}
}
```

## 🔧 Integratie met Agents

### FrontendDeveloper Agent
```python
# Agent gebruikt project context voor component generatie
context = project_manager.get_project_context()
tech_stack = context["tech_stack"]["frontend"]

if "React" in tech_stack:
    # Genereer React componenten
    generate_react_components()
elif "Vue" in tech_stack:
    # Genereer Vue componenten
    generate_vue_components()
```

### UXUIDesigner Agent
```python
# Agent gebruikt requirements voor design analyse
context = project_manager.get_project_context()
requirements = context["requirements"]["non_functional"]

if "accessibility" in requirements:
    # Voer accessibility checks uit
    check_accessibility()
```

### DocumentationAgent
```python
# Agent gebruikt project info voor documentatie
context = project_manager.get_project_context()
project_name = context["project_name"]
tech_stack = context["tech_stack"]

# Genereer project-specifieke documentatie
generate_project_docs(project_name, tech_stack)
```

## 🎯 Best Practices

### 1. Project Setup
```bash
# 1. Maak project aan
python3 bmad/projects/cli.py create my-app --type web_app

# 2. Laad project
python3 bmad/projects/cli.py load my-app

# 3. Voeg requirements toe
python3 bmad/projects/cli.py add-requirement "User authentication"
python3 bmad/projects/cli.py add-requirement "Responsive design" --category non_functional

# 4. Voeg user stories toe
python3 bmad/projects/cli.py add-story "As a user, I want to log in" --priority high
```

### 2. Agent Workflow
```python
# 1. Laad project context
project_manager.load_project("my-app")
context = project_manager.get_project_context()

# 2. Agents gebruiken context
frontend_agent.process_with_context(context)
ux_agent.analyze_with_context(context)
docs_agent.generate_with_context(context)
```

### 3. Project Updates
```python
# Update project configuratie
project_manager.update_project({
    "status": "in_development",
    "tech_stack": {
        "frontend": ["React", "TypeScript", "Tailwind CSS"]
    }
})
```

## 🔍 Troubleshooting

### Project niet gevonden
```bash
# Controleer beschikbare projecten
python3 bmad/projects/cli.py list

# Controleer configs directory
ls bmad/projects/configs/
```

### Context niet beschikbaar
```python
# Zorg dat project is geladen
if not project_manager.get_current_project():
    project_manager.load_project("project_name")

context = project_manager.get_project_context()
```

### Events niet ontvangen
```python
# Controleer event subscriptions
from bmad.agents.core.message_bus import get_subscribers
print(get_subscribers("project_loaded"))
```

## 📚 Meer Informatie

- [BMAD Agents Documentation](./agents.md)
- [Message Bus System](./message-bus.md)
- [Project Templates](./templates.md) 