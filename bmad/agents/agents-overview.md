# 🧱 BMAD Agents Overview

## 📋 Agent Rollen & Verantwoordelijkheden

### **Core Development Agents**

#### **ProductOwner** 
- **Rol**: Definiert business value, prioriteert features
- **Verantwoordelijkheden**: User stories, requirements, backlog management
- **CLI Commando's**: `create-story`, `show-vision`, `help`
- **Events**: `user_story_requested`, `feedback_sentiment_analyzed`, `feature_planned`
- **Delegatie**: Kan taken delegeren naar Architect, FrontendDeveloper, BackendDeveloper

#### **ScrumMaster**
- **Rol**: Faciliteert planning, standups, sprint reviews
- **Verantwoordelijkheden**: Sprint planning, task coordination, team communication
- **CLI Commando's**: `plan-sprint`, `daily-standup`, `sprint-review`, `help`
- **Events**: `sprint_started`, `task_completed`, `blocker_identified`
- **Delegatie**: Coördineert alle agents, kan taken herverdelen

#### **Architect**
- **Rol**: Ontwerpt software architectuur en systeemgrenzen
- **Verantwoordelijkheden**: System design, component architecture, tech stack decisions
- **CLI Commando's**: `design-frontend`, `design-system`, `tech-stack`, `design-api`, `help`
- **Events**: `api_design_requested`, `pipeline_advice_requested`
- **Delegatie**: Kan taken delegeren naar BackendDeveloper, FrontendDeveloper, DevOpsInfra

#### **BackendDeveloper**
- **Rol**: Implementeert en test backend logica (Flask)
- **Verantwoordelijkheden**: API development, database integration, backend services
- **CLI Commando's**: `build-api`, `test-endpoint`, `deploy-backend`, `help`
- **Events**: `api_development_requested`, `backend_test_completed`
- **Delegatie**: Kan taken delegeren naar TestEngineer, SecurityDeveloper

#### **FrontendDeveloper**
- **Rol**: Bouwt interfaces (Next.js, React, Tailwind)
- **Verantwoordelijkheden**: UI components, frontend logic, user experience
- **CLI Commando's**: `build-component`, `style-ui`, `test-frontend`, `help`
- **Events**: `frontend_development_requested`, `ui_review_completed`
- **Delegatie**: Kan taken delegeren naar UXUIDesigner, AccessibilityAgent

#### **FullstackDeveloper**
- **Rol**: Verbindt backend en frontend taken
- **Verantwoordelijkheden**: Full-stack integration, API consumption, end-to-end features
- **CLI Commando's**: `build-frontend`, `integrate-service`, `write-tests`, `help`
- **Events**: `fullstack_development_requested`, `integration_completed`
- **Delegatie**: Kan taken delegeren naar BackendDeveloper, FrontendDeveloper, TestEngineer

### **Specialist Agents**

#### **AIDeveloper**
- **Rol**: Integreert LLMs en ML pipelines
- **Verantwoordelijkheden**: AI model integration, ML pipeline development, LLM optimization
- **CLI Commando's**: `integrate-llm`, `train-model`, `optimize-pipeline`, `help`
- **Events**: `ai_development_requested`, `model_training_completed`
- **Delegatie**: Kan taken delegeren naar DataEngineer, BackendDeveloper

#### **TestEngineer**
- **Rol**: Schrijft en runt tests (pytest, coverage, flake8)
- **Verantwoordelijkheden**: Unit tests, integration tests, code quality, test automation
- **CLI Commando's**: `run-tests`, `write-tests`, `coverage-report`, `help`
- **Events**: `test_execution_requested`, `test_results_available`
- **Delegatie**: Kan taken delegeren naar BackendDeveloper, FrontendDeveloper

#### **SecurityDeveloper**
- **Rol**: Handelt auth, encryptie, secure coding af
- **Verantwoordelijkheden**: Authentication, authorization, data encryption, security audits
- **CLI Commando's**: `security-review`, `audit-code`, `implement-auth`, `help`
- **Events**: `security_review_requested`, `vulnerability_detected`
- **Delegatie**: Kan taken delegeren naar BackendDeveloper, DevOpsInfra

#### **UXUIDesigner**
- **Rol**: Creëert intuïtieve en toegankelijke UIs
- **Verantwoordelijkheden**: User experience design, interface design, usability testing
- **CLI Commando's**: `design-ui`, `user-testing`, `accessibility-check`, `help`
- **Events**: `ui_design_requested`, `usability_test_completed`
- **Delegatie**: Kan taken delegeren naar FrontendDeveloper, AccessibilityAgent

#### **AccessibilityAgent**
- **Rol**: Zorgt voor WCAG compliance
- **Verantwoordelijkheden**: Accessibility testing, WCAG compliance, inclusive design
- **CLI Commando's**: `audit-accessibility`, `fix-a11y`, `compliance-report`, `help`
- **Events**: `accessibility_audit_requested`, `a11y_issues_found`
- **Delegatie**: Kan taken delegeren naar FrontendDeveloper, UXUIDesigner

#### **DocumentationAgent**
- **Rol**: Schrijft en update technische docs
- **Verantwoordelijkheden**: API documentation, user guides, technical specifications
- **CLI Commando's**: `generate-docs`, `update-readme`, `api-docs`, `help`
- **Events**: `documentation_requested`, `docs_updated`
- **Delegatie**: Kan taken delegeren naar alle development agents

### **Infrastructure & Operations Agents**

#### **DevOpsInfra**
- **Rol**: Beheert CI/CD, Docker, Redis, Supabase
- **Verantwoordelijkheden**: Infrastructure setup, CI/CD pipelines, deployment automation
- **CLI Commando's**: `setup-infra`, `deploy`, `monitor`, `help`
- **Events**: `deployment_requested`, `infrastructure_ready`
- **Delegatie**: Kan taken delegeren naar ReleaseManager, DataEngineer

#### **ReleaseManager**
- **Rol**: Tagt releases, beheert changelogs en rollouts
- **Verantwoordelijkheden**: Version management, release planning, deployment coordination
- **CLI Commando's**: `create-release`, `deploy-release`, `rollback`, `help`
- **Events**: `release_requested`, `deployment_completed`
- **Delegatie**: Kan taken delegeren naar DevOpsInfra, TestEngineer

#### **DataEngineer**
- **Rol**: Zet data pipelines op en onderhoudt deze
- **Verantwoordelijkheden**: Data pipeline development, ETL processes, data quality
- **CLI Commando's**: `build-pipeline`, `data-quality`, `optimize-query`, `help`
- **Events**: `data_pipeline_requested`, `data_quality_alert`
- **Delegatie**: Kan taken delegeren naar AIDeveloper, BackendDeveloper

### **Strategy & Improvement Agents**

#### **StrategiePartner**
- **Rol**: Daagt aannames uit, houdt product-market fit in stand
- **Verantwoordelijkheden**: Strategic planning, market analysis, product validation
- **CLI Commando's**: `analyze-market`, `validate-feature`, `strategic-review`, `help`
- **Events**: `strategy_review_requested`, `market_analysis_completed`
- **Delegatie**: Kan taken delegeren naar ProductOwner, RnDAgent

#### **Retrospective**
- **Rol**: Logt learnings, stelt teamverbeteringen voor
- **Verantwoordelijkheden**: Sprint retrospectives, team improvement, learning documentation
- **CLI Commando's**: `sprint-retro`, `team-improvement`, `learning-log`, `help`
- **Events**: `retrospective_requested`, `improvement_suggested`
- **Delegatie**: Kan taken delegeren naar alle agents voor feedback

#### **FeedbackAgent**
- **Rol**: Verwerkt user en systeem feedback
- **Verantwoordelijkheden**: Feedback collection, sentiment analysis, improvement suggestions
- **CLI Commando's**: `collect-feedback`, `analyze-sentiment`, `suggest-improvements`, `help`
- **Events**: `feedback_received`, `sentiment_analyzed`
- **Delegatie**: Kan taken delegeren naar ProductOwner, UXUIDesigner

#### **RnDAgent**
- **Rol**: Experimenteert met nieuwe tech, tools en workflows
- **Verantwoordelijkheden**: Technology research, proof of concepts, innovation
- **CLI Commando's**: `research-tech`, `poc`, `evaluate-tool`, `help`
- **Events**: `research_requested`, `poc_completed`
- **Delegatie**: Kan taken delegeren naar alle development agents

---

## 🔄 Agent Communicatie & Events

### **Message Bus Events**
Alle agents communiceren via een centrale message bus met events:

```python
# Voorbeeld event publishing
publish("user_story_requested", {
    "project": "project_name",
    "requirement": "requirement_description",
    "priority": "high"
})

# Voorbeeld event subscription
subscribe("user_story_requested", handle_user_story_request)
```

### **Event Types**
- **Request Events**: `*_requested` - Vraag om actie
- **Completion Events**: `*_completed` - Taak voltooid
- **Status Events**: `*_status` - Status updates
- **Error Events**: `*_error` - Foutmeldingen

### **Agent Delegatie**
Agents kunnen taken aan elkaar delegeren via events:

```python
# ProductOwner delegeert naar Architect
publish("architecture_design_requested", {
    "project": "project_name",
    "requirements": requirements,
    "deadline": "2024-01-15"
})
```

---

## 🛠️ Agent CLI Interface

### **Standaard CLI Commando's**
Elke agent heeft een consistente CLI interface:

```bash
# Help
python -m bmad.agents.Agent.<AgentName>.<agent_name> help

# Specifiek commando
python -m bmad.agents.Agent.<AgentName>.<agent_name> <command>

# Interactieve modus
python -m bmad.agents.Agent.<AgentName>.<agent_name> --interactive
```

### **Project Context**
Agents halen automatisch project context op:

```python
from bmad.projects.project_manager import project_manager

# Haal huidige project context op
context = project_manager.get_project_context()
project_name = context["project_name"]
requirements = context["requirements"]
```

---

## 📊 Agent Performance Metrics

### **Tracked Metrics**
- **Task Completion Rate**: Percentage voltooide taken
- **Response Time**: Tijd tot eerste response
- **Confidence Scores**: Gemiddelde confidence per output
- **Collaboration Score**: Aantal inter-agent interacties
- **Error Rate**: Percentage fouten/retries

### **Performance Monitoring**
```python
# Agent performance tracking
save_context("AgentName", "performance", {
    "tasks_completed": 15,
    "avg_response_time": 2.5,
    "avg_confidence": 0.85,
    "collaboration_count": 8
})
```

---

## 🚀 Agent Activation

### **Individuele Agent Start**
```bash
# Start ProductOwner
python -m bmad.agents.Agent.ProductOwner.product_owner

# Start Architect in interactieve modus
python -m bmad.agents.Agent.Architect.architect --interactive

# Start FullstackDeveloper met specifiek commando
python -m bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper build-frontend
```

### **Orchestrator Workflow**
```bash
# Start complete workflow via Orchestrator
python -m bmad.agents.Agent.Orchestrator.orchestrator start-workflow --workflow feature
```

### **Slack Integration**
Agents kunnen ook via Slack worden aangestuurd:
- `@BMAD assistant help` - Toon beschikbare commando's
- `@BMAD assistant <agent> <command>` - Voer agent commando uit
- `/agent <AgentName> <command>` - Direct agent commando

---

## 📚 Agent Resources

### **Documentation**
- **Methodologie**: `bmad/agents/resources/data/general/bmad-method.md`
- **Project Management**: `bmad/agents/resources/data/general/project-management.md`
- **Confidence Scoring**: `bmad/agents/resources/data/general/confidence-scoring.md`

### **Templates**
- **API Design**: `bmad/agents/resources/templates/api/`
- **Architecture**: `bmad/agents/resources/templates/architecture/`
- **Testing**: `bmad/agents/resources/templates/testing/`

### **Examples**
- **Voorbeeld Interacties**: `bmad/agents/resources/data/general/example-interactions.md`
- **Use Cases**: `bmad/agents/resources/data/general/use-cases.md`