# ClickUp Integration Setup Guide

## Overzicht

De ClickUp integratie in BMAD maakt het mogelijk om projecten, taken en user stories te synchroniseren tussen het BMAD systeem en ClickUp. Dit zorgt voor een naadloze workflow tussen AI agents en traditioneel project management.

## Benodigde Environment Variables

Voeg de volgende variabelen toe aan je `.env` file:

```bash
# ClickUp API Configuration
CLICKUP_API_KEY=your_clickup_api_key_here
CLICKUP_SPACE_ID=your_space_id_here
CLICKUP_FOLDER_ID=your_folder_id_here
CLICKUP_LIST_ID=your_list_id_here
```

### Hoe je deze waarden vindt:

1. **CLICKUP_API_KEY**: 
   - Ga naar ClickUp Settings → Apps → API Token
   - Genereer een nieuwe API token
   - Kopieer de token naar je .env file

2. **CLICKUP_SPACE_ID**:
   - Open je ClickUp workspace
   - Klik op de space naam
   - De space ID staat in de URL: `https://app.clickup.com/[workspace_id]/v/li/[space_id]`

3. **CLICKUP_FOLDER_ID**:
   - Open de folder in ClickUp
   - De folder ID staat in de URL: `https://app.clickup.com/[workspace_id]/v/li/[space_id]/f/[folder_id]`

4. **CLICKUP_LIST_ID**:
   - Open de list in ClickUp
   - De list ID staat in de URL: `https://app.clickup.com/[workspace_id]/v/li/[list_id]`

## Webhook Configuratie

De integratie gebruikt een webhook voor bidirectional synchronisatie:

**Webhook URL:** `https://n8n.innovative-digitalmarketing.com/webhook/copilot_clickup_agent`

### Webhook Payload Format

```json
{
  "operation": "createTask",
  "parameters": {
    "list_id": "LIST_ID_HIER",
    "name": "Task Name",
    "content": "Task Description",
    "status": "todo",
    "priority": 2,
    "tags": ["Tag1", "Tag2"],
    "assignees": ["USER_ID_HIER"]
  }
}
```

## Functionaliteiten

### 1. Project Management

```python
from bmad.agents.core.clickup_integration import clickup_integration

# Nieuw project aanmaken
project_id = clickup_integration.create_project(
    project_name="My Project",
    project_type="web_app",
    description="Project description"
)
```

### 2. Task Management

```python
# Taak aanmaken
task_id = clickup_integration.create_task(
    project_name="My Project",
    task_name="Implement feature",
    description="Detailed task description",
    priority="high",
    assignee="developer_id"
)

# Taak status updaten
clickup_integration.update_task_status(task_id, "in_progress")

# Taak als voltooid markeren
clickup_integration.mark_task_completed(task_id, "Feature implemented successfully")
```

### 3. User Stories Synchronisatie

```python
user_stories = [
    {
        "title": "User Authentication",
        "as_a": "end user",
        "i_want": "secure login",
        "so_that": "I can access the platform",
        "acceptance_criteria": "Login form, validation, error handling",
        "priority": "high",
        "story_points": "5"
    }
]

clickup_integration.sync_user_stories("My Project", user_stories)
```

### 4. Agent Task Management

```python
# Taak voor specifieke agent aanmaken
task_id = clickup_integration.create_agent_task(
    project_name="My Project",
    agent_name="FrontendDeveloper",
    task_description="Implement login form",
    estimated_hours=8
)
```

### 5. Project Metrics

```python
# Project metrics ophalen
metrics = clickup_integration.get_project_metrics("My Project")
print(f"Completion rate: {metrics['completion_rate']}%")
```

## Agent Integratie

### ProductOwner Agent

De ProductOwner agent kan automatisch:
- Projecten aanmaken in ClickUp
- User stories synchroniseren
- Backlog items exporteren

```bash
python bmad/agents/Agent/ProductOwner/productowner.py sync-clickup
```

### ScrumMaster Agent

De ScrumMaster agent kan automatisch:
- Sprint taken aanmaken
- Task assignments beheren
- Sprint metrics bijhouden

```bash
python bmad/agents/Agent/Scrummaster/scrummaster.py create-sprint-tasks
```

### Developer Agents

Developer agents kunnen automatisch:
- Task status updaten
- Completion notes toevoegen
- Time tracking bijhouden

## Testing

### 1. Environment Variables Test

```bash
python test_clickup_integration.py
```

### 2. Integration Test

```bash
python example_clickup_usage.py
```

### 3. Agent Integration Test

```bash
# Test ProductOwner integratie
python bmad/agents/Agent/ProductOwner/productowner.py create-story

# Test ScrumMaster integratie  
python bmad/agents/Agent/Scrummaster/scrummaster.py sprint-planning
```

## Troubleshooting

### Veelvoorkomende Problemen

1. **API Key Error**
   - Controleer of CLICKUP_API_KEY correct is ingesteld
   - Verifieer dat de API key geldig is in ClickUp

2. **Space/Folder/List ID Error**
   - Controleer of alle IDs correct zijn gekopieerd uit de URL
   - Verifieer dat je toegang hebt tot de space/folder/list

3. **Permission Error**
   - Zorg dat je API key de juiste permissions heeft
   - Controleer of je toegang hebt tot de ClickUp workspace

4. **Webhook Error**
   - Controleer of de webhook URL correct is
   - Verifieer dat de n8n workflow actief is

### Debug Mode

Voeg debug logging toe aan je `.env`:

```bash
LOG_LEVEL=DEBUG
```

## Best Practices

1. **Project Naming**: Gebruik consistente naamgeving voor projecten
2. **Task Descriptions**: Schrijf duidelijke, gedetailleerde beschrijvingen
3. **Status Updates**: Update task status regelmatig
4. **Comments**: Voeg nuttige comments toe bij task updates
5. **Tags**: Gebruik tags voor categorisatie en filtering

## Monitoring

### Webhook Events

Monitor webhook events in je n8n workflow:
- Task creation events
- Status update events
- Completion events

### API Usage

Monitor API usage in ClickUp:
- Ga naar Settings → Apps → API
- Bekijk usage statistics en rate limits

## Security

1. **API Key**: Bewaar je API key veilig, deel deze nooit
2. **Environment Variables**: Gebruik .env files voor lokale ontwikkeling
3. **Permissions**: Geef minimale benodigde permissions aan API keys
4. **Audit Logs**: Monitor API usage voor ongewone activiteit

## Support

Voor vragen of problemen:
1. Controleer de troubleshooting sectie
2. Run de test scripts
3. Bekijk de ClickUp API documentatie
4. Neem contact op met het development team 