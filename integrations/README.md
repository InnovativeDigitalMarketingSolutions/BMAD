# BMAD Integrations

## 📚 Overview

Deze directory bevat alle integratie modules voor het BMAD systeem, georganiseerd per integratie type voor eenvoudige toegang en onderhoud.

## 📁 Integration Modules

### **🔗 External Service Integrations**

#### **📋 ClickUp Integration**
- **Directory**: `clickup/`
- **Purpose**: ClickUp project management integratie
- **Components**:
  - `clickup_integration.py` - Core ClickUp API integratie
  - `bmad_clickup_workflow.py` - BMAD workflow voor ClickUp
  - `clickup_id_finder.py` - ClickUp ID utilities
  - `setup_clickup.py` - ClickUp setup tools
  - `implement_clickup_template.py` - Template implementatie

#### **🎨 Figma Integration**
- **Directory**: `figma/`
- **Purpose**: Figma design platform integratie
- **Components**:
  - `figma_client.py` - Figma API client
  - `figma_slack_notifier.py` - Figma-Slack notificaties

#### **💬 Slack Integration**
- **Directory**: `slack/`
- **Purpose**: Slack communication integratie
- **Components**:
  - `slack_notify.py` - Slack notificatie functionaliteit
  - `slack_event_server.py` - Slack event handling

#### **🔔 Webhook Integration**
- **Directory**: `webhook/`
- **Purpose**: Webhook notificatie integratie
- **Components**:
  - `webhook_notify.py` - Webhook notificatie systeem

### **🛠️ Repository Integrations**

#### **🤖 OpenRouter Integration**
- **Directory**: `openrouter/`
- **Purpose**: Multi-LLM provider routing
- **Components**:
  - `openrouter_client.py` - OpenRouter API client

#### **📊 OpenTelemetry Integration**
- **Directory**: `opentelemetry/`
- **Purpose**: Distributed tracing en observability
- **Components**:
  - `opentelemetry_tracing.py` - Tracing en monitoring

#### **🔒 OPA Integration**
- **Directory**: `opa/`
- **Purpose**: Policy enforcement en access control
- **Components**:
  - `opa_policy_engine.py` - Policy engine integratie

#### **🚀 Prefect Integration**
- **Directory**: `prefect/`
- **Purpose**: Workflow orchestration
- **Components**:
  - `prefect_workflow.py` - Prefect workflow management

#### **🔄 LangGraph Integration**
- **Directory**: `langgraph/`
- **Purpose**: Graph-based workflow orchestration
- **Components**:
  - `langgraph_workflow.py` - LangGraph workflow management

## 🚀 Usage

### **Importing Integrations**

```python
# ClickUp Integration
from integrations.clickup import ClickUpIntegration, BMADClickUpWorkflow

# Figma Integration
from integrations.figma import FigmaClient, FigmaSlackNotifier

# Slack Integration
from integrations.slack import send_slack_message, SlackEventServer

# Webhook Integration
from integrations.webhook import WebhookNotifier

# Repository Integrations
from integrations.openrouter import OpenRouterClient
from integrations.opentelemetry import BMADTracer, TracingConfig
from integrations.opa import OPAPolicyEngine, PolicyResponse
from integrations.prefect import PrefectWorkflowOrchestrator
from integrations.langgraph import LangGraphWorkflowOrchestrator
```

### **Quick Start Examples**

#### **ClickUp Integration**
```python
from integrations.clickup import ClickUpIntegration

clickup = ClickUpIntegration()
projects = clickup.list_projects()
```

#### **Figma Integration**
```python
from integrations.figma import FigmaClient

figma = FigmaClient()
file_data = figma.get_file("file_id")
```

#### **OpenRouter Integration**
```python
from integrations.openrouter import OpenRouterClient

router = OpenRouterClient()
response = await router.generate_response("Hello, world!")
```

## 📁 Directory Structure

```
integrations/
├── README.md                      # This file
├── clickup/                       # ClickUp integration
│   ├── __init__.py
│   ├── clickup_integration.py
│   ├── bmad_clickup_workflow.py
│   ├── clickup_id_finder.py
│   ├── setup_clickup.py
│   └── implement_clickup_template.py
├── figma/                         # Figma integration
│   ├── __init__.py
│   ├── figma_client.py
│   └── figma_slack_notifier.py
├── slack/                         # Slack integration
│   ├── __init__.py
│   ├── slack_notify.py
│   └── slack_event_server.py
├── webhook/                       # Webhook integration
│   ├── __init__.py
│   └── webhook_notify.py
├── openrouter/                    # OpenRouter integration
│   ├── __init__.py
│   └── openrouter_client.py
├── opentelemetry/                 # OpenTelemetry integration
│   ├── __init__.py
│   └── opentelemetry_tracing.py
├── opa/                          # OPA integration
│   ├── __init__.py
│   └── opa_policy_engine.py
├── prefect/                      # Prefect integration
│   ├── __init__.py
│   └── prefect_workflow.py
└── langgraph/                    # LangGraph integration
    ├── __init__.py
    └── langgraph_workflow.py
```

## 🔧 Development

### **Adding New Integrations**

1. **Create integration directory** in `integrations/`
2. **Add `__init__.py`** with proper imports
3. **Move integration files** to the new directory
4. **Update imports** in dependent modules
5. **Add documentation** to this README
6. **Test integration** functionality

### **Integration Standards**

- **Consistent naming**: Use lowercase for directories and files
- **Clear imports**: Export main classes/functions in `__init__.py`
- **Documentation**: Include docstrings and usage examples
- **Error handling**: Implement proper error handling and logging
- **Configuration**: Use environment variables for configuration

## 📚 Documentation

Voor gedetailleerde documentatie van elke integratie, zie:
- **ClickUp**: `../docs/integrations/BMAD_CLICKUP_WORKFLOW_README.md`
- **Figma**: `../docs/integrations/FIGMA_INTEGRATION_README.md`
- **Repository Integrations**: `../docs/integrations/REPOSITORY_INTEGRATIONS_README.md`
- **Webhook**: `../docs/integrations/WEBHOOK_INTEGRATION_README.md`

## 🔍 Testing

```bash
# Test specific integration
python -m pytest tests/integrations/test_clickup_integration.py

# Test all integrations
python -m pytest tests/integrations/
```

## 📞 Support

Voor vragen over integraties:
- **Issues**: GitHub issues
- **Documentation**: Zie de docs/ directory
- **Examples**: Zie de CLI tools in cli/ directory

---

**BMAD Integrations** - Georganiseerde integratie modules voor het BMAD systeem 🔗 