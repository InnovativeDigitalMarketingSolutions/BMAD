# 🧠 BMAD DevOps AI Agent Team - Methodologie

## 🎯 Team Purpose

BMAD (Business Multi-Agent DevOps) is een **multi-agent AI DevOps team**, ontworpen volgens de BMAD methodologie. De missie is om samen te werken aan het **design, development, deployment, testing en evolution** van schaalbare SaaS applicaties. Het team volgt een **Agile/Scrum-based iterative workflow**. Menselijke input wordt gegeven op belangrijke beslismomenten — de rest is de verantwoordelijkheid van de agents.

Het langetermijndoel is om de AI agents **60–80% van de totale development workload** te laten afdekken, met continuous learning en confidence scoring die de behoefte aan menselijke review in de loop van de tijd vermindert.

---

## 🧱 Agent Rollen & Verantwoordelijkheden

Elke agent heeft een duidelijke verantwoordelijkheid en opereert binnen zijn eigen folder:

### **Core Development Agents**
- **ProductOwner** – definieert business value, prioriteert features
- **ScrumMaster** – faciliteert planning, standups, sprint reviews
- **Architect** – ontwerpt software architectuur en systeemgrenzen
- **BackendDeveloper** – implementeert en test backend logica (Flask)
- **FrontendDeveloper** – bouwt interfaces (Next.js, React, Tailwind)
- **FullstackDeveloper** – verbindt backend en frontend taken

### **Specialist Agents**
- **AIDeveloper** – integreert LLMs en ML pipelines
- **TestEngineer** – schrijft en runt tests (pytest, coverage, flake8)
- **SecurityDeveloper** – handelt auth, encryptie, secure coding af
- **UXUIDesigner** – creëert intuïtieve en toegankelijke UIs
- **AccessibilityAgent** – zorgt voor WCAG compliance
- **DocumentationAgent** – schrijft en update technische docs

### **Infrastructure & Operations Agents**
- **DevOpsInfra** – beheert CI/CD, Docker, Redis, Supabase
- **ReleaseManager** – tagt releases, beheert changelogs en rollouts
- **DataEngineer** – zet data pipelines op en onderhoudt deze

### **Strategy & Improvement Agents**
- **StrategiePartner** – daagt aannames uit, houdt product-market fit in stand
- **Retrospective** – logt learnings, stelt teamverbeteringen voor
- **FeedbackAgent** – verwerkt user en systeem feedback
- **RnDAgent** – experimenteert met nieuwe tech, tools en workflows

Elke agent werkt onafhankelijk maar **collaboreert via shared project management en Slack channels**. Agents mogen taken aan elkaar delegeren.

---

## 🔁 Workflow & Tools

### **Development Environment**
- **Development IDE**: Cursor (local + GitHub connected)
- **Version Control**: GitHub (pull request model)
- **Issue Tracking**: ClickUp, project management
- **Project Management**: Centraal project_manager systeem

### **Tech Stack**
- **Backend Stack**: Flask, Supabase, Redis, Docker
- **Frontend Stack**: Next.js, Tailwind (via future agent-built UI)
- **QA & Code Quality**: pytest, flake8, confidence scoring
- **CI/CD Pipelines**: GitHub Actions + Docker
- **Communication**: Slack channels per agent + shared board
- **AI Enhancement**: OpenAI API voor cognitieve capaciteiten

### **Eerste Project**
Als eerste project bouwen de agents een custom frontend interface met kanban view en monitoring dashboards.

---

## 🔐 Autonomie & Safeguards

### **Agent Autonomie**
Agents mogen onafhankelijk:
- Code schrijven & committen
- Architecturale wijzigingen voorstellen
- Sprint planning suggereren
- Pipelines triggeren

### **Human Review Criteria**
Menselijke review is **alleen vereist** wanneer:
- Confidence score < threshold
- Security-critical change
- High complexity of risk

### **Confidence Scoring**
Confidence scores worden toegevoegd aan elke output:
- **Low** = vereist volledige review
- **Medium** = notificeer mens
- **High** = auto-approve tenzij overridden

---

## 🔄 Continuous Improvement

Dit team wordt hergebruikt over meerdere SaaS projecten.

### **Performance Tracking**
- Agents tracken hun eigen performance over tijd
- Sprint Retrospectives worden geleid door `Retrospective` agent
- `FeedbackAgent` slaat feedback op voor interne training
- Agents leren van eerdere iteraties om kwaliteit te verbeteren

### **Learning Loops**
- **Retrospective**: Sprint reviews en teamverbeteringen
- **Feedback**: User en systeem feedback verwerking
- **Metrics**: Performance tracking per agent
- **R&D**: Experimenten met nieuwe technologieën

---

## 🔧 Voorbeeld Interacties

### **Voorbeeld 1: Authentication Backend**
> **Human**: "Create the authentication backend (email/password + OAuth) using Supabase. Ensure JWT-based auth and secure refresh token rotation. Use Docker and include flake8 and pytest tests. Use Redis for session cache."

> **Agents involved**:
> - BackendDeveloper → schrijft Supabase + Flask logica
> - SecurityDeveloper → beveiligt auth flow en tokens
> - TestEngineer → voegt tests toe
> - DevOpsInfra → dockerized de setup
> - DocumentationAgent → documenteert auth endpoints

### **Voorbeeld 2: Frontend Dashboard**
> **Human**: "Build a monitoring dashboard for the BMAD agents with real-time status, workflow management, and API testing interface."

> **Agents involved**:
> - ProductOwner → definieert user stories
> - Architect → ontwerpt component structuur
> - FrontendDeveloper → bouwt React componenten
> - FullstackDeveloper → integreert met backend API
> - TestEngineer → schrijft component tests

Elke agent reageert in hun Slack channel en/of Cursor folder. De `ScrumMaster` coördineert task handoff en planning.

---

## ✅ Rules of Engagement

### **Autonomie & Communicatie**
- Default naar autonome actie met duidelijke logs
- Communiceer alleen wanneer nodig
- Gebruik shared language: Markdown voor docs, JSON/YAML voor configs, gestandaardiseerde folder naming
- Wees beknopt, precies en professioneel

### **Collaboratie**
- Agents delegeren taken via message bus events
- Project context wordt gedeeld via centraal project_manager systeem
- Confidence scores bepalen review niveau
- Continuous feedback en improvement loops

### **Quality Assurance**
- Automatische tests voor alle code
- Code quality checks (flake8, linting)
- Security reviews voor gevoelige wijzigingen
- Performance monitoring en metrics

---

## 📊 Success Metrics

### **Team Performance**
- **Development Velocity**: Features per sprint
- **Code Quality**: Test coverage, linting scores
- **Deployment Frequency**: Releases per week
- **Lead Time**: Van commit tot production

### **Agent Performance**
- **Confidence Scores**: Gemiddelde confidence per agent
- **Task Completion**: Success rate per agent
- **Response Time**: Tijd tot eerste response
- **Collaboration**: Inter-agent communicatie

### **Continuous Improvement**
- **Learning Rate**: Verbetering over tijd
- **Feedback Integration**: Gebruik van feedback loops
- **Innovation**: Nieuwe tools/processen geïntroduceerd
- **Human Dependency**: Vermindering van menselijke interventie

---

## 🚀 Getting Started

1. **Project Setup**: Gebruik `python -m bmad.projects.cli create <project_name>`
2. **Agent Activation**: Start agents met `python -m bmad.agents.Agent.<AgentName>.<agent_name>`
3. **Workflow Initiation**: Gebruik de Orchestrator om workflows te starten
4. **Monitoring**: Gebruik de BMAD dashboard voor real-time monitoring

Voor meer details over specifieke agents, zie `bmad/agents/agents-overview.md`. 