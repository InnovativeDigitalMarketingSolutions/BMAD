# ClickUp Integratie Configuratie

Webhook URL: https://n8n.innovative-digitalmarketing.com/webhook/copilot_clickup_agent

## Voorbeeld operatie: createTask
{
  "operation": "createTask",
  "parameters": {
    "list_id": "LIST_ID_HIER",
    "name": "User Authentication Flow",
    "content": "Implementeer login, registratie en beveiligde sessies",
    "status": "todo",
    "priority": 2,
    "tags": ["Frontend", "Security"],
    "assignees": ["USER_ID_HIER"]
  }
}
