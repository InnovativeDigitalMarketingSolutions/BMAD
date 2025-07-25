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

### One Command for Everything (IDE Installation)

**Just run one of these commands:**

```bash
npx bmad-method install
# OR if you already have BMad installed:
git pull
npm run install:bmad
```

This single command handles:

- **New installations** - Sets up BMad in your project
- **Upgrades** - Updates existing installations automatically
- **Expansion packs** - Installs any expansion packs you've added to package.json

> **That's it!** Whether you're installing for the first time, upgrading, or adding expansion packs - these commands do everything.

**Prerequisites**: [Node.js](https://nodejs.org) v20+ required

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

## Mappenstructuur

- `bmad/agents/` — Alle agent-implementaties en core modules
- `bmad/resources/` — Templates, data, changelogs, context
- `bmad/api.py` — REST API (Flask) met orchestrator- en agent-endpoints
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
