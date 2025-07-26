# 📁 BMAD Project Management System

## 🎯 Overzicht

Het BMAD Project Management System is een centraal systeem dat alle project-specifieke informatie beheert en beschikbaar maakt voor alle agents. Dit zorgt ervoor dat agents consistent kunnen werken aan verschillende projecten zonder hardcoded informatie.

---

## 🏗️ Architectuur

### **Project Manager**
- **Locatie**: `bmad/projects/project_manager.py`
- **Functie**: Centrale project configuratie en context management
- **Opslag**: JSON bestanden in `bmad/projects/configs/`

### **Project CLI**
- **Locatie**: `bmad/projects/cli.py`
- **Functie**: Command-line interface voor project management
- **Features**: Project aanmaken, laden, requirements toevoegen, user stories beheren

---

## 📋 Project Structuur

### **Project Configuratie**
```json
{
  "project_name": "project-name",
  "project_type": "web_app|mobile_app|api_service",
  "created_at": 1703123456.789,
  "updated_at": 1703123456.789,
  "status": "active|archived|completed",
  "description": "Project beschrijving",
  "tech_stack": {
    "frontend": ["React", "TypeScript", "Vite"],
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Docker", "AWS/GCP"]
  },
  "architecture": {
    "type": "microservices",
    "frontend": "SPA",
    "backend": "REST API",
    "database": "PostgreSQL"
  },
  "requirements": {
    "functional": [...],
    "non_functional": [...],
    "technical": [...],
    "general": [...]
  },
  "user_stories": [...],
  "api_endpoints": [...],
  "database_schema": {...},
  "deployment_config": {...}
}
```

### **Project Types**
- **web_app**: Web applicatie met frontend en backend
- **mobile_app**: Mobile applicatie (React Native)
- **api_service**: API service (backend only)

---

## 🚀 Gebruik

### **Project CLI Commando's**

```bash
# Projecten beheren
python -m bmad.projects.cli list                    # Toon alle projecten
python -m bmad.projects.cli create <name> --type <type>  # Nieuw project
python -m bmad.projects.cli load <name>             # Laad project
python -m bmad.projects.cli info                    # Project informatie

# Content toevoegen
python -m bmad.projects.cli add-requirement <req> --category <cat>
python -m bmad.projects.cli add-story <story> --priority <pri>

# Interactieve modus
python -m bmad.projects.cli interactive
```

### **Interactieve Modus**
```bash
python -m bmad.projects.cli interactive

# Beschikbare commando's:
# list                    - Toon alle projecten
# create <name> [type]    - Maak nieuw project
# load <name>             - Laad een project
# info                    - Toon huidig project info
# add-req <cat> <req>     - Voeg requirement toe
# add-story <story> [pri] - Voeg user story toe
# help                    - Toon help
# quit                    - Stop interactieve modus
```

---

## 🔧 Agent Integratie

### **Project Context Ophalen**
```python
from bmad.projects.project_manager import project_manager

# Haal huidige project context op
context = project_manager.get_project_context()

if context:
    project_name = context["project_name"]
    requirements = context["requirements"]
    user_stories = context["user_stories"]
    tech_stack = context["tech_stack"]
else:
    print("❌ Geen project geladen!")
```

### **Project Updates**
```python
# Update project configuratie
project_manager.update_project({
    "status": "in_progress",
    "new_field": "value"
})

# Voeg requirement toe
project_manager.add_requirement(
    "User authentication with OAuth", 
    "functional"
)

# Voeg user story toe
project_manager.add_user_story(
    "As a user, I want to login with Google so that I can access the application",
    "high"
)
```

### **Event Publishing**
```python
from bmad.agents.core.message_bus import publish

# Publiceer project events
publish("project_loaded", {
    "project_name": "project-name",
    "config": project_config
})

publish("project_updated", {
    "project_name": "project-name",
    "updates": updates
})
```

---

## 📊 Project Templates

### **Web App Template**
```json
{
  "description": "Web applicatie met frontend en backend",
  "tech_stack": {
    "frontend": ["React", "TypeScript", "Vite"],
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Docker", "AWS/GCP"]
  },
  "architecture": {
    "type": "microservices",
    "frontend": "SPA",
    "backend": "REST API",
    "database": "PostgreSQL"
  }
}
```

### **Mobile App Template**
```json
{
  "description": "Mobile applicatie",
  "tech_stack": {
    "frontend": ["React Native", "TypeScript"],
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Expo", "App Store"]
  },
  "architecture": {
    "type": "client-server",
    "frontend": "React Native",
    "backend": "REST API",
    "database": "PostgreSQL"
  }
}
```

### **API Service Template**
```json
{
  "description": "API service",
  "tech_stack": {
    "backend": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": ["Docker", "Kubernetes"]
  },
  "architecture": {
    "type": "api_service",
    "backend": "REST API",
    "database": "PostgreSQL"
  }
}
```

---

## 🔄 Workflow Integratie

### **Agent Workflow**
1. **Project Laden**: `python -m bmad.projects.cli load <project_name>`
2. **Agent Starten**: Agent haalt automatisch project context op
3. **Taak Uitvoeren**: Agent gebruikt project-specifieke informatie
4. **Resultaten Opslaan**: Agent slaat output op in project context

### **Voorbeeld Workflow**
```bash
# 1. Project aanmaken
python -m bmad.projects.cli create my-saas-app web_app

# 2. Project laden
python -m bmad.projects.cli load my-saas-app

# 3. Requirements toevoegen
python -m bmad.projects.cli add-requirement "User authentication" functional
python -m bmad.projects.cli add-requirement "Real-time notifications" functional

# 4. Agent starten (automatisch project context)
python -m bmad.agents.Agent.ProductOwner.product_owner create-story
```

---

## 📈 Project Metrics

### **Tracked Metrics**
- **Project Status**: active, archived, completed
- **Requirements Count**: Per categorie
- **User Stories Count**: Per prioriteit
- **Last Updated**: Timestamp van laatste wijziging
- **Agent Usage**: Welke agents hebben het project gebruikt

### **Performance Tracking**
```python
# Project performance metrics
project_metrics = {
    "requirements_completed": 15,
    "user_stories_implemented": 8,
    "agents_involved": ["ProductOwner", "Architect", "FullstackDeveloper"],
    "last_activity": time.time()
}
```

---

## 🔗 Integraties

### **ClickUp Integration** (Toekomstig)
```python
# ClickUp project koppeling
clickup_config = {
    "project_id": "clickup_project_id",
    "space_id": "clickup_space_id",
    "api_key": "clickup_api_key"
}

# Sync requirements met ClickUp
project_manager.sync_with_clickup(clickup_config)
```

### **GitHub Integration** (Toekomstig)
```python
# GitHub repository koppeling
github_config = {
    "repo_url": "https://github.com/user/repo",
    "branch": "main",
    "webhook_url": "webhook_url"
}

# Sync project met GitHub
project_manager.sync_with_github(github_config)
```

---

## 🛠️ Best Practices

### **Project Naming**
- Gebruik kebab-case: `my-saas-app`, `ecommerce-platform`
- Beschrijvende namen: `user-management-system`, `analytics-dashboard`
- Consistent naming across environments

### **Requirements Management**
- Categoriseer requirements: functional, non_functional, technical
- Gebruik duidelijke, testbare beschrijvingen
- Prioriteer requirements met labels

### **User Stories**
- Volg Gherkin format: "As a [user], I want [feature] so that [benefit]"
- Voeg acceptatiecriteria toe
- Prioriteer met low/medium/high

### **Context Sharing**
- Agents delen automatisch project context
- Gebruik events voor inter-agent communicatie
- Sla resultaten op in project configuratie

---

## 📚 Gerelateerde Documentatie

- **BMAD Methodologie**: `bmad-method.md`
- **Agent Overview**: `agents-overview.md`
- **Confidence Scoring**: `confidence-scoring.md`
- **Example Interactions**: `example-interactions.md` 