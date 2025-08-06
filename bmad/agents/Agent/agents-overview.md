# BMAD Agent Overview

## 📋 **Agent Inventory (23 Total Agents)**

### **Core Development Agents**
1. **FrontendDeveloper** - React/Next.js development, Shadcn/ui components, accessibility
2. **BackendDeveloper** - API development, database design, server-side logic
3. **FullstackDeveloper** - Full-stack development, end-to-end solutions
4. **MobileDeveloper** - Mobile app development, cross-platform solutions
5. **AiDeveloper** - AI/ML development, model integration, data science

### **Architecture & Design Agents**
6. **Architect** - Software architecture, system design, API design
7. **UXUIDesigner** - User experience design, interface design, usability
8. **AccessibilityAgent** - Accessibility compliance, WCAG guidelines, inclusive design

### **Quality & Testing Agents**
9. **TestEngineer** - Test automation, quality assurance, testing strategies
10. **QualityGuardian** - Quality management, standards enforcement, best practices

### **Project Management Agents**
11. **ProductOwner** - Product management, user stories, backlog management
12. **Scrummaster** - Agile project management, sprint planning, team coordination
13. **ReleaseManager** - Release management, deployment coordination, version control

### **Infrastructure & Operations Agents**
14. **DevOpsInfra** - Infrastructure management, CI/CD pipelines, deployment
15. **DataEngineer** - Data pipeline development, ETL processes, data architecture

### **Security & Compliance Agents**
16. **SecurityDeveloper** - Security analysis, vulnerability assessment, compliance

### **Documentation & Communication Agents**
17. **DocumentationAgent** - Technical documentation, user guides, API docs
18. **FeedbackAgent** - Feedback collection, sentiment analysis, improvement tracking

### **Process & Workflow Agents**
19. **Orchestrator** - Workflow orchestration, process coordination, automation
20. **WorkflowAutomator** - Process automation, workflow optimization, efficiency
21. **Retrospective** - Process improvement, lessons learned, team retrospectives

### **Strategy & Innovation Agents**
22. **StrategiePartner** - Strategic planning, business alignment, innovation
23. **RnD** - Research and development, experimentation, innovation

## 🔄 **MCP Integration Status**

📋 **Voor gedetailleerde Enhanced MCP Integration status en planning, zie:**
- `docs/deployment/KANBAN_BOARD.md` - MCP Phase 2: Agent Enhancement sectie
- `docs/guides/MCP_PHASE2_WORKFLOW_GUIDE.md` - Enhanced MCP workflow guide

**Huidige Status**: 6/23 agents hebben Enhanced MCP + Tracing integration

## 🚀 **Message Bus Integration Status**

✅ **VOLTOOID**: Alle 23 agents hebben Message Bus Integration geïmplementeerd

### **Message Bus Integration Overzicht**
- **FrontendDeveloper**: ✅ Geïmplementeerd
- **BackendDeveloper**: ✅ Geïmplementeerd (imports geüpdatet)
- **FullstackDeveloper**: ✅ Geïmplementeerd
- **MobileDeveloper**: ✅ Geïmplementeerd
- **AiDeveloper**: ✅ Geïmplementeerd
- **Architect**: ✅ Geïmplementeerd
- **UXUIDesigner**: ✅ Geïmplementeerd
- **AccessibilityAgent**: ✅ Geïmplementeerd
- **TestEngineer**: ✅ Geïmplementeerd
- **QualityGuardian**: ✅ Geïmplementeerd
- **ProductOwner**: ✅ Geïmplementeerd
- **Scrummaster**: ✅ Geïmplementeerd
- **ReleaseManager**: ✅ Geïmplementeerd
- **DevOpsInfra**: ✅ Geïmplementeerd
- **DataEngineer**: ✅ Geïmplementeerd
- **SecurityDeveloper**: ✅ Geïmplementeerd
- **DocumentationAgent**: ✅ Geïmplementeerd
- **FeedbackAgent**: ✅ Geïmplementeerd (imports geüpdatet)
- **Orchestrator**: ✅ Geïmplementeerd (imports geüpdatet)
- **WorkflowAutomator**: ✅ Geïmplementeerd
- **Retrospective**: ✅ Geïmplementeerd
- **StrategiePartner**: ✅ Geïmplementeerd
- **RnD**: ✅ Geïmplementeerd

**Status**: 23/23 agents (100%) hebben Message Bus Integration

## 🚀 **Quick Reference**

### **CLI Commands**
```bash
# Toon alle beschikbare agents
python3 bmad.py help

# Agent-specifieke help
python3 bmad.py <agent-name> help

# Voorbeelden
python3 bmad.py backend build-api
python3 bmad.py frontend create-component
python3 bmad.py test run-tests
```

### **Agent File Locations**
- **Agent Files**: `bmad/agents/Agent/<AgentName>/`
- **Test Files**: `tests/unit/agents/test_<agentname>.py`
- **Templates**: `bmad/resources/templates/<agentname>/`
- **Data**: `bmad/resources/data/<agentname>/`

## 🎯 **Agent Capabilities Overview**

### **Development & Architecture**
- **FrontendDeveloper**: React/Next.js, Shadcn/ui, component development
- **BackendDeveloper**: API development, database design, server-side logic
- **FullstackDeveloper**: End-to-end solutions, full-stack development
- **MobileDeveloper**: Mobile app development, cross-platform solutions
- **Architect**: Software architecture, system design, API design
- **UXUIDesigner**: User experience design, interface design, usability
- **AccessibilityAgent**: WCAG compliance, inclusive design, accessibility testing

### **Quality & Security**
- **TestEngineer**: Test automation, quality assurance, testing strategies
- **QualityGuardian**: Quality management, standards enforcement, best practices
- **SecurityDeveloper**: Security analysis, vulnerability assessment, compliance

### **Project & Process Management**
- **ProductOwner**: Product management, user stories, backlog management
- **Scrummaster**: Agile project management, sprint planning, team coordination
- **ReleaseManager**: Release management, deployment coordination, version control
- **Orchestrator**: Workflow orchestration, process coordination, automation
- **WorkflowAutomator**: Process automation, workflow optimization, efficiency
- **Retrospective**: Process improvement, lessons learned, team retrospectives

### **Infrastructure & Data**
- **DevOpsInfra**: Infrastructure management, CI/CD pipelines, deployment
- **DataEngineer**: Data pipeline development, ETL processes, data architecture

### **Documentation & Communication**
- **DocumentationAgent**: Technical documentation, user guides, API docs
- **FeedbackAgent**: Feedback collection, sentiment analysis, improvement tracking

### **Strategy & Innovation**
- **StrategiePartner**: Strategic planning, business alignment, innovation
- **RnD**: Research and development, experimentation, innovation
- **AiDeveloper**: AI/ML development, model integration, data science

## 🔗 **Inter-Agent Communication**

Alle agents communiceren via:
- **Message Bus**: Event-driven communication
- **Supabase Context**: Shared state management
- **MCP Integration**: Enhanced tool sharing (in progress)

## 📚 **Development Resources**

### **Guides & Documentation**
- **MCP Integration**: `docs/guides/MCP_INTEGRATION_GUIDE.md`
- **Enhanced MCP Workflow**: `docs/guides/MCP_PHASE2_WORKFLOW_GUIDE.md`
- **Best Practices**: `docs/guides/BEST_PRACTICES_GUIDE.md`
- **Development Workflow**: `docs/guides/DEVELOPMENT_WORKFLOW_GUIDE.md`
- **Agent Optimization**: `docs/guides/agent-optimization-guide.md`

### **Project Management**
- **Kanban Board**: `docs/deployment/KANBAN_BOARD.md`
- **Master Planning**: `docs/deployment/BMAD_MASTER_PLANNING.md`
- **Implementation Details**: `docs/deployment/IMPLEMENTATION_DETAILS.md`

## 📊 **Integration Progress**

📋 **Voor gedetailleerde Enhanced MCP Integration progress, zie:**
- `docs/deployment/KANBAN_BOARD.md` - MCP Phase 2: Agent Enhancement sectie

**Huidige Status**: 6/23 agents (26.1%) hebben Enhanced MCP + Tracing integration

---

**Last Updated**: August 2025
**Next Review**: After each agent Enhanced MCP integration 