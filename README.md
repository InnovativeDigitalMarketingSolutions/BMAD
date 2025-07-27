# BMad-Method: Universal AI Agent Framework

[![Version](https://img.shields.io/npm/v/bmad-method?color=blue&label=version)](https://www.npmjs.com/package/bmad-method)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D20.0.0-brightgreen)](https://nodejs.org)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-7289da?logo=discord&logoColor=white)](https://discord.gg/gk8jAdXWmj)

Foundations in Agentic Agile Driven Development, known as the Breakthrough Method of Agile AI-Driven Development, yet so much more. Transform any domain with specialized AI expertise: software development, entertainment, creative writing, business strategy to personal wellness just to name a few.

**[Subscribe to BMadCode on YouTube](https://www.youtube.com/@BMadCode?sub_confirmation=1)**

**[Join our Discord Community](https://discord.gg/gk8jAdXWmj)** - A growing community for AI enthusiasts! Get help, share ideas, explore AI agents & frameworks, collaborate on tech projects, enjoy hobbies, and help each other succeed. Whether you're stuck on BMad, building your own agents, or just want to chat about the latest in AI - we're here for you! **Some mobile and VPN may have issue joining the discord, this is a discord issue - if the invite does not work, try from your own internet or another network, or non-VPN.**

⭐ **If you find this project helpful or useful, please give it a star in the upper right hand corner!** It helps others discover BMad-Method and you will be notified of updates!

## Overview

**BMad Method's Two Key Innovations:**

**1. Agentic Planning:** Dedicated agents (Analyst, PM, Architect) collaborate with you to create detailed, consistent PRDs and Architecture documents. Through advanced prompt engineering and human-in-the-loop refinement, these planning agents produce comprehensive specifications that go far beyond generic AI task generation.

**2. Context-Engineered Development:** The Scrum Master agent then transforms these detailed plans into hyper-detailed development stories that contain everything the Dev agent needs - full context, implementation details, and architectural guidance embedded directly in story files.

This two-phase approach eliminates both **planning inconsistency** and **context loss** - the biggest problems in AI-assisted development. Your Dev agent opens a story file with complete understanding of what to build, how to build it, and why.

**📖 [See the complete workflow in the User Guide](bmad-core/user-guide.md)** - Planning phase, development cycle, and all agent roles

## Quick Navigation

### Understanding the BMad Workflow

**Before diving in, review these critical workflow diagrams that explain how BMad works:**

1. **[Planning Workflow (Web UI)](bmad-core/user-guide.md#the-planning-workflow-web-ui)** - How to create PRD and Architecture documents
2. **[Core Development Cycle (IDE)](bmad-core/user-guide.md#the-core-development-cycle-ide)** - How SM, Dev, and QA agents collaborate through story files

> ⚠️ **These diagrams explain 90% of BMad Method Agentic Agile flow confusion** - Understanding the PRD+Architecture creation and the SM/Dev/QA workflow and how agents pass notes through story files is essential - and also explains why this is NOT taskmaster or just a simple task runner!

### What would you like to do?

- **[Install and Build software with Full Stack Agile AI Team](#quick-start)** → Quick Start Instruction
- **[Learn how to use BMad](bmad-core/user-guide.md)** → Complete user guide and walkthrough
- **[See available AI agents](#available-agents)** → Specialized roles for your team
- **[Explore non-technical uses](#-beyond-software-development---expansion-packs)** → Creative writing, business, wellness, education
- **[Create my own AI agents](#creating-your-own-expansion-pack)** → Build agents for your domain
- **[Browse ready-made expansion packs](expansion-packs/)** → Game dev, DevOps, infrastructure and get inspired with ideas and examples
- **[Understand the architecture](docs/core-architecture.md)** → Technical deep dive
- **[Join the community](https://discord.gg/gk8jAdXWmj)** → Get help and share ideas

### 📚 BMAD Documentation

- **[BMAD Methodologie](bmad/agents/resources/data/general/bmad-method.md)** → Team purpose, roles, workflow, autonomy & safeguards
- **[Agent Overview](bmad/agents/agents-overview.md)** → Complete agent roles, CLI commands, events & delegation
- **[Project Management](bmad/agents/resources/data/general/project-management.md)** → Central project system & context management
- **[Confidence Scoring](bmad/agents/resources/data/general/confidence-scoring.md)** → Review flows, safeguards & continuous improvement
- **[Agent Metrics](bmad/agents/resources/data/general/agent-metrics.md)** → Performance tracking & feedback loops
- **[Example Interactions](bmad/agents/resources/data/general/example-interactions.md)** → Practical workflows & use cases

## Important: Keep Your BMad Installation Updated

**Stay up-to-date effortlessly!** If you already have BMad-Method installed in your project, simply run:

```bash
npx bmad-method install
# OR
git pull
npm run install:bmad
```

This will:

- ✅ Automatically detect your existing v4 installation
- ✅ Update only the files that have changed and add new files
- ✅ Create `.bak` backup files for any custom modifications you've made
- ✅ Preserve your project-specific configurations

This makes it easy to benefit from the latest improvements, bug fixes, and new agents without losing your customizations!

## Quick Start

### BMAD Agent Team Setup

**Prerequisites**: Python 3.8+, Node.js v20+ (for frontend development)

#### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd BMAD

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

#### 2. Project Management
```bash
# Create a new project
python -m bmad.projects.cli create my-saas-app web_app

# Load the project
python -m bmad.projects.cli load my-saas-app

# Add requirements
python -m bmad.projects.cli add-requirement "User authentication" functional
python -m bmad.projects.cli add-requirement "Real-time notifications" functional
```

#### 3. Start BMAD Agents
```bash
# Start ProductOwner to create user stories
python -m bmad.agents.Agent.ProductOwner.product_owner create-story

# Start Architect to design system
python -m bmad.agents.Agent.Architect.architect design-frontend

# Start FullstackDeveloper to build features
python -m bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper build-frontend
```

#### 4. Advanced Integrations (Optional)
```bash
# Performance monitoring
python3 performance_monitor_cli.py start-monitoring --interval 5
python3 performance_monitor_cli.py system-summary

# Test sprites
python3 test_sprites_cli.py list-sprites
python3 test_sprites_cli.py test-sprite AgentStatus_sprite --type all

# Integrated workflow orchestration
python3 integrated_workflow_cli.py test-integrations
python3 integrated_workflow_cli.py list-workflows

# Repository integrations
python3 repository_integration_cli.py test-all
```

#### 5. Slack Integration (Optional)
```bash
# Start Slack event server
python -m bmad.agents.core.slack_event_server

# In another terminal, start ngrok
ngrok http 5001

# Configure Slack app with ngrok URL
# Test with: @BMAD assistant help
```

### Fastest Start: Web UI Full Stack Team at your disposal (2 minutes)

1. **Get the bundle**: Save or clone the [full stack team file](dist/teams/team-fullstack.txt) or choose another team
2. **Create AI agent**: Create a new Gemini Gem or CustomGPT
3. **Upload & configure**: Upload the file and set instructions: "Your critical operating instructions are attached, do not break character as directed"
4. **Start Ideating and Planning**: Start chatting! Type `*help` to see available commands or pick an agent like `*analyst` to start right in on creating a brief.
5. **CRITICAL**: Talk to BMad Orchestrator in the web at ANY TIME (#bmad-orchestrator command) and ask it questions about how this all works!
6. **When to move to the IDE**: Once you have your PRD, Architecture, optional UX and Briefs - its time to switch over to the IDE to shard your docs, and start implementing the actual code! See the [User guide](bmad-core/user-guide.md) for more details

### Alternative: Clone and Build

```bash
git clone https://github.com/bmadcode/bmad-method.git
npm run install:bmad # build and install all to a destination folder
```

## 🚀 New Integrations & Features

BMAD now includes advanced integrations for enhanced agent orchestration, performance monitoring, and intelligent workflows:

### **📊 Performance Monitor Integration**
- **Real-time monitoring** of agent performance and system resources
- **Intelligent alerting** with configurable thresholds
- **Performance analytics** with trend analysis and recommendations
- **Auto-scaling support** for optimal resource utilization

### **🧪 Test Sprites Integration**
- **Visual test helpers** for UI component testing
- **Accessibility testing** with automated checks
- **Performance testing** with visual regression detection
- **Component sprite library** for comprehensive testing

### **🔗 Repository Integrations**
- **LangGraph**: Async stateful workflow orchestration
- **OpenRouter**: Multi-LLM provider routing and load balancing
- **OpenTelemetry**: Distributed tracing and observability
- **OPA**: Granular policy enforcement and access control
- **Prefect**: CI/CD pipeline orchestration

### **🛠️ CLI Tools**
- `performance_monitor_cli.py` - Performance monitoring and analytics
- `test_sprites_cli.py` - Test sprite management and execution
- `integrated_workflow_cli.py` - Complete workflow orchestration
- `repository_integration_cli.py` - Repository integration testing

## Environment Variables (.env)

Voor een werkende BMAD-omgeving heb je een `.env` bestand nodig in de projectroot.  
Hieronder vind je een voorbeeld en uitleg van de belangrijkste variabelen:

```env
# --- Slack integratie ---
SLACK_BOT_TOKEN=        # Slack Bot User OAuth Token (xoxb-...)
SLACK_SIGNING_SECRET=   # Slack Signing Secret
SLACK_WEBHOOK_URL=      # (optioneel) Slack Webhook URL
SLACK_DEFAULT_CHANNEL=  # Channel ID voor standaardnotificaties (bijv. C097FTDU1A5)
SLACK_ALERT_CHANNEL=    # Channel ID voor alerts (bijv. C097G8YLBMY)
SLACK_PO_CHANNEL=       # Channel ID voor Product Owner escalaties (bijv. C097G9RFBBL)

# --- OpenAI / LLM integratie ---
OPENAI_API_KEY=         # OpenAI API key (sk-...)
OPENAI_MODEL=gpt-4o     # (optioneel) Modelnaam

# --- Supabase integratie ---
SUPABASE_URL=           # Supabase project URL
SUPABASE_KEY=           # Supabase service role key

# --- Overige configuratie ---
LOG_LEVEL=INFO

# --- (optioneel) Voor Swagger UI tests ---
SLACK_EVENT_URL=http://localhost:5001/slack/events

# --- (optioneel) Voor CI/CD of test skips ---
CI=false

# --- Performance Monitor ---
OTEL_SERVICE_NAME=bmad-agents
OTEL_ENVIRONMENT=development

# --- OpenRouter (Multi-LLM) ---
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# --- OPA (Policy Engine) ---
OPA_URL=http://localhost:8181

# --- OpenTelemetry (Observability) ---
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14268/api/traces
```

### Uitleg per variabele

- **SLACK_BOT_TOKEN**: Nodig voor alle Slack API-calls (chat.postMessage, events, etc.)
- **SLACK_SIGNING_SECRET**: Nodig voor het valideren van inkomende Slack events.
- **SLACK_DEFAULT_CHANNEL / SLACK_ALERT_CHANNEL / SLACK_PO_CHANNEL**: Channel ID’s waar de bot berichten mag sturen. Haal deze op via Slack of met een testscript.
- **OPENAI_API_KEY**: Voor LLM-integratie (TestEngineer, ProductOwner, etc.)
- **SUPABASE_URL / SUPABASE_KEY**: Voor contextopslag en resource management.
- **LOG_LEVEL**: Loggingniveau (INFO, DEBUG, WARNING, etc.)
- **SLACK_EVENT_URL**: Handig voor lokale Swagger UI tests.
- **CI**: Wordt automatisch gezet in CI/CD pipelines.

> **Let op:** Deel je echte secrets nooit publiekelijk! Gebruik `.env.example` als template.

## 🌟 Beyond Software Development - Expansion Packs

BMad's natural language framework works in ANY domain. Expansion packs provide specialized AI agents for creative writing, business strategy, health & wellness, education, and more. Also expansion packs can expand the core BMad-Method with specific functionality that is not generic for all cases. [See the Expansion Packs Guide](docs/expansion-packs.md) and learn to create your own!

## Documentation & Resources

### Essential Guides

- 📖 **[User Guide](bmad-core/user-guide.md)** - Complete walkthrough from project inception to completion
- 🏗️ **[Core Architecture](docs/core-architecture.md)** - Technical deep dive and system design
- 🚀 **[Expansion Packs Guide](docs/expansion-packs.md)** - Extend BMad to any domain beyond software development

### Integration Documentation

- 📊 **[Performance Monitor Integration](PERFORMANCE_MONITOR_INTEGRATION_README.md)** - Real-time agent performance monitoring
- 🧪 **[Test Sprites Integration](TEST_SPRITES_INTEGRATION_README.md)** - Visual testing and component validation
- 🔗 **[Repository Integrations](REPOSITORY_INTEGRATIONS_README.md)** - LangGraph, OpenRouter, OpenTelemetry, OPA, Prefect
- 🔄 **[Agent Workflow Integration](AGENT_WORKFLOW_INTEGRATION_README.md)** - Advanced workflow orchestration
- 🌍 **[Environment Setup](ENVIRONMENT_SETUP.md)** - Complete environment configuration guide
- 📈 **[Implementation Status](IMPLEMENTATION_STATUS.md)** - Current implementation overview

## Support

- 💬 [Discord Community](https://discord.gg/gk8jAdXWmj)
- 🐛 [Issue Tracker](https://github.com/bmadcode/bmad-method/issues)
- 💬 [Discussions](https://github.com/bmadcode/bmad-method/discussions)

## Contributing

**We're excited about contributions and welcome your ideas, improvements, and expansion packs!** 🎉

📋 **[Read CONTRIBUTING.md](CONTRIBUTING.md)** - Complete guide to contributing, including guidelines, process, and requirements

## License

MIT License - see [LICENSE](LICENSE) for details.

[![Contributors](https://contrib.rocks/image?repo=bmadcode/bmad-method)](https://github.com/bmadcode/bmad-method/graphs/contributors)

<sub>Built with ❤️ for the AI-assisted development community</sub>

## Architectuur & Workflow

BMAD is een event-driven multi-agent framework. Agents communiceren via een message bus en worden gecoördineerd door een centrale orchestrator. Workflows bestaan uit een serie events, met optionele human-in-the-loop (HITL) stappen en Slack-integratie.

- **Agents:** Gespecialiseerde rollen (ProductOwner, Developer, TestEngineer, etc.)
- **Orchestrator:** Stuurt workflows aan, coördineert events, escalaties en feedback loops
- **Message bus:** Pub/Sub mechanisme voor events tussen agents
- **Slack:** Voor notificaties, commando’s en HITL
- **Supabase:** Contextopslag en resource management
- **LLM:** Voor intelligente taken (testgeneratie, story parsing, etc.)

## 📚 Documentation

### **🔗 Integrations**
- [Repository Integrations](docs/integrations/REPOSITORY_INTEGRATIONS_README.md)
- [Agent Workflow Integration](docs/integrations/AGENT_WORKFLOW_INTEGRATION_README.md)
- [Performance Monitor](docs/integrations/PERFORMANCE_MONITOR_INTEGRATION_README.md)
- [Test Sprites](docs/integrations/TEST_SPRITES_INTEGRATION_README.md)
- [Advanced Policy Engine](docs/integrations/ADVANCED_POLICY_ENGINE_README.md)
- [LangGraph Integration](docs/integrations/LANGGRAPH_INTEGRATION_README.md)
- [Webhook Integration](docs/integrations/WEBHOOK_INTEGRATION_README.md)
- [Figma Integration](docs/integrations/FIGMA_INTEGRATION_README.md)
- [ClickUp Workflow](docs/integrations/BMAD_CLICKUP_WORKFLOW_README.md)

### **📊 Status & Guides**
- [Environment Setup](docs/guides/ENVIRONMENT_SETUP.md)
- [Implementation Status](docs/status/IMPLEMENTATION_STATUS.md)
- [Production Status](docs/status/PRODUCTION_STATUS.md)
- [Contributing Guidelines](docs/guides/CONTRIBUTING.md)

### **📖 Core Documentation**
- [BMAD Method](bmad/resources/data/general/bmad-method.md)
- [Agent Metrics](bmad/resources/data/general/agent-metrics.md)
- [Confidence Scoring](bmad/resources/data/general/confidence-scoring.md)
- [CLI Tools](cli/README.md)
- [Full Documentation Index](docs/README.md)

## 📁 Project Structure

- `bmad/agents/` — Alle agent-implementaties en core modules
- `bmad/resources/` — Templates, data, changelogs, context
- `bmad/api.py` — REST API (Flask) met orchestrator- en agent-endpoints
- `cli/` — Alle CLI tools georganiseerd
- `docs/` — Georganiseerde documentatie (integrations, status, guides, results)
- `swagger-ui/` — Swagger UI frontend en OpenAPI-spec
- `tests/` — Alle tests, gestructureerd per domein (slack, orchestrator, agents, utils)
- `.github/workflows/` — CI/CD workflows (linting, testen, health checks)

## Setup & Development

1. Clone de repo en ga naar de projectmap
2. Maak een Python venv aan en installeer requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Vul je `.env` in (zie voorbeeld hierboven)
4. Start de API:
   ```bash
   python bmad/api.py
   ```
5. Open de Swagger UI: [http://localhost:5001/swagger](http://localhost:5001/swagger)

## Testen

- **Alle tests draaien:**
  ```bash
  pytest tests/
  ```
- **Automatische tests:** Draaien altijd in CI/CD
- **Handmatige/integratietests:** Gemarkeerd met `@pytest.mark.skipif(os.getenv("CI"), ...)`, lokaal te draaien
- **Nieuwe tests toevoegen:** Plaats in de juiste subfolder, gebruik pytest-stijl

## CI/CD

- **Workflow:** `.github/workflows/ci.yml`
- **Checks:** Linting (flake8), formatting (black), pytest, health check, optionele Slack-notificatie
- **Alleen checks, geen auto-merge/deploy**
- **Branches worden niet automatisch overschreven**

## Deployment

- **Development:**
  - Start de API met Flask (`python bmad/api.py`)
- **Productie:**
  - Gebruik een WSGI-server zoals gunicorn:
    ```bash
    gunicorn -w 4 -b 0.0.0.0:5001 bmad.api:app
    ```
  - Zet environment variables via `.env` of je deployment platform
  - (Optioneel) Gebruik Docker of een cloud platform

## API-documentatie

- **Swagger UI:** [http://localhost:5001/swagger](http://localhost:5001/swagger)
- **OpenAPI-spec:** [http://localhost:5001/openapi.yaml](http://localhost:5001/openapi.yaml)
- **Endpoints:** Zie Swagger UI voor alle routes en documentatie
- **Test direct via de UI**

## Slack-integratie

- Maak een Slack app aan via [api.slack.com/apps](https://api.slack.com/apps)
- Voeg de juiste scopes toe: `chat:write`, `channels:read`, `groups:read`, `im:write`, etc.
- Zet de `SLACK_BOT_TOKEN` en `SLACK_SIGNING_SECRET` in je `.env`
- Voeg de bot toe aan de gewenste kanalen met `/invite @BMAD assistant`
- Zet de Interactivity URL op `http://<jouw-ngrok-of-server-url>/slack/interactivity`
- Test met de Slack testscripts in `tests/slack/`

## LLM/Supabase integratie

- **OpenAI:**
  - Maak een account aan op [platform.openai.com](https://platform.openai.com/)
  - Zet je API key in `.env` als `OPENAI_API_KEY`
- **Supabase:**
  - Maak een project aan op [supabase.com](https://supabase.com/)
  - Zet je project-URL en service role key in `.env`

## Troubleshooting & FAQ

- **Slack: channel_not_found:**
  - Controleer of de bot is toegevoegd aan het kanaal en de channel-ID klopt
- **OPENAI_API_KEY niet gevonden:**
  - Controleer je `.env` en activeer je venv opnieuw
- **Supabase errors:**
  - Controleer of je Supabase keys en URL correct zijn
- **Tests blijven hangen:**
  - Sommige tests vereisen handmatige actie of een actieve agent (zie README)
- **CI/CD faalt op handmatige tests:**
  - Handmatige tests zijn gemarkeerd en worden automatisch overgeslagen in CI
- **Swagger UI laadt niet:**
  - Controleer of je API draait en `/openapi.yaml` bereikbaar is

Voor meer hulp: zie de Discord community of open een issue!
