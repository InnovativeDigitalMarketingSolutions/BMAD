# Agent Completeness Implementation Workflow

## Overview

Deze workflow definieert de gestandaardiseerde aanpak voor het implementeren van alle ontbrekende agent functionaliteiten geïdentificeerd door de comprehensive audit. Het doel is om alle 23 agents complete te maken volgens de Agent Completeness Prevention Strategy.

**Workflow**: [Agent Completeness Prevention Strategy](../guides/AGENT_COMPLETENESS_PREVENTION_STRATEGY.md)

## 🎯 **Quality-First Implementation Principe**

**KRITIEK PRINCIPE**: Implementeer **ÉÉN AGENT PER KEER** met volledige kwaliteitscontrole voordat naar de volgende agent te gaan.

### Waarom Één Agent Per Keer?
- **Kwaliteitsborging**: Volledige focus op één agent voorkomt rushed implementations
- **Complete Testing**: 100% test success rate per agent voor elke stap
- **Root Cause Analysis**: Tijd voor grondige analyse bij issues
- **Documentation Completeness**: Volledige documentatie per agent
- **Knowledge Transfer**: Lessons learned kunnen toegepast worden op volgende agents
- **Risk Mitigation**: Voorkomen van cascade failures

## 📚 Referenties
- [Agent Completeness Prevention Strategy](../guides/AGENT_COMPLETENESS_PREVENTION_STRATEGY.md)
- [BMAD Test Strategy](../guides/TEST_STRATEGY.md)
- [Message Bus Event Standards](../guides/MESSAGE_BUS_EVENT_STANDARDS.md)

## 📋 **Pre-Implementation Setup**

### 1. Environment Preparation
- [ ] **Virtual Environment**: Activate `.venv` environment
- [ ] **Dependencies**: Ensure all required packages are installed
- [ ] **Test Infrastructure**: Verify test infrastructure is working
- [ ] **Audit Scripts**: Verify comprehensive audit scripts are functional
- [ ] **Wrapper Audit**: Run `python scripts/check_no_direct_publish.py` en noteer agent‑hits

### 2. Agent Inventory Analysis
- [ ] **Run Comprehensive Audit**: Execute `scripts/comprehensive_agent_audit.py`
- [ ] **Identify Priority Agents**: Sort agents by completeness score (lowest first)
- [ ] **Create Implementation Plan**: Plan implementation order based on dependencies
- [ ] **Resource Assessment**: Identify missing resources per agent
- [ ] **Direct Publish Scan**: Zoek naar directe `publish(` calls in de betreffende agent

### 3. Implementation Strategy
- [ ] **Batch Processing**: Group agents by missing functionality type
- [ ] **Dependency Order**: Implement agents with fewer dependencies first
- [ ] **Resource Preparation**: Prepare templates and resources for all agents
- [ ] **Test Preparation**: Prepare test infrastructure for all agents

## 🔧 **Implementation Workflow**

### **Phase 1: Core Implementation (23 agents)**

#### **Step 1: Select Target Agent**
- [ ] **Agent Selection**: Choose next agent from priority list
- [ ] **Current State Analysis**: Run agent-specific audit
- [ ] **Missing Items Identification**: List all missing attributes and methods
- [ ] **Implementation Plan**: Create detailed plan for this agent
- [ ] **Quality-First**: Root cause analysis uitvoeren; geen quick fixes

#### **Step 2: Core Attributes Implementation**
- [ ] **Required Attributes Check**: Verify missing attributes from audit
- [ ] **Attribute Implementation**: Add missing attributes to `__init__` method
  - [ ] `mcp_client`, `enhanced_mcp`, `enhanced_mcp_enabled`, `tracing_enabled`, `agent_name`, `message_bus_integration`
- [ ] **Class-Level Attributes**: Definieer kritieke attributen op class‑niveau i.p.v. alleen in `__init__`
- [ ] **Initialization Logic**: Implement proper initialization logic
- [ ] **Error Handling**: Add error handling for initialization

#### **Step 3: Core Methods Implementation**
- [ ] **Required Methods Check**: Verify missing methods from audit
- [ ] **Method Implementation**: Add missing methods conform standaard patterns
- [ ] **Enhanced MCP Pattern**: Volg standaard init/registratie methods
- [ ] **Tracing**: Implementeer `trace_operation()` en integreer in kernpaden

#### **Step 4a: Enhanced MCP Integration**
- [ ] **MCP Client Setup**: Initialize MCP client properly
- [ ] **Enhanced MCP Initialization**: Implement `initialize_enhanced_mcp()`
- [ ] **Tool Registration**: Implement tool registration logic
- [ ] **Error Handling**: Add comprehensive error handling

#### **Step 4b: Tracing Integration**
- [ ] **Tracing Service Setup**: Initialize tracing service
- [ ] **Operation Tracing**: Implement `trace_operation()` method
- [ ] **Performance Tracking**: Add performance tracking capabilities
- [ ] **Error Tracing**: Add error tracing capabilities

#### **Step 4c: Message Bus Integration (Wrapper & Contract)**
- [ ] **Wrapper Usage**: Vervang directe `publish(...)` door `await self.publish_agent_event(...)`
- [ ] **Payload Contract**: Payload bevat minimaal `status` + domeinspecifieke sleutel; `request_id` optioneel
- [ ] **EventTypes**: Gebruik consistente `EventTypes.*` waarden
- [ ] **Failure Paths**: Publiceer bij errors een corresponderend `*_FAILED` event
- [ ] **Handlers**: Registreer relevante event handlers (`register_event_handler`)

#### **Step 5: Sync Compatibility (optioneel)**
- [ ] **Sync Wrapper**: Indien publiek API sync vereist is, bied een dunne sync wrapper die `asyncio.run(...)` gebruikt

### **Phase 2: Testing Implementation**

#### **Step 6: Unit Test Implementation**
- [ ] **BMAD Test Strategy**: Volg `TEST_STRATEGY.md` (async, mocking, quality gates)
- [ ] **Mock Wrapper**: Mock `publish_agent_event` met `AsyncMock`; verifieer payload‑contract
- [ ] **Core Method Tests**: Test alle publieke methods/attributen
- [ ] **Error Scenario Tests**: Test foutpaden + FAILED events

#### **Step 7: Integration & Component Tests**
- [ ] **Integration Tests**: Test message bus flows; MCP en tracing integratie; retries/timeout/failure‑paths
- [ ] **Component Tests**: Test subsystemen met meerdere agents (end‑to‑end paden binnen subsystem)
- [ ] **Contracttests**: Valideer event‑payloads tegen pydantic schema’s

#### **Step 8: AI Evaluations (indien relevant)**
- [ ] **Prompt/Output Evaluatie**: LLM‑as‑judge en metrics; nightly uitgebreide set

### **Phase 3: Quality Assurance**

#### **Step 9: Code Quality & Security**
- [ ] **Lint/Format/Type**: black, ruff/flake8, mypy
- [ ] **Security**: safety/pip‑audit, gitleaks; SBOM (CycloneDX) waar mogelijk

#### **Step 10: Documentation, Resources & Governance**
- [ ] **Agent .md**: Update status, capabilities, handlers, events
- [ ] **Changelog**: Voeg gedetailleerde changelog entry toe (datum, Added/Enhanced/Technical)
- [ ] **Agents Overview**: Update `bmad/agents/agents-overview.md`
- [ ] **Kanban Board**: Update taakstatus
- [ ] **Master Planning**: Update voortgang en roadmap indien van toepassing
- [ ] **Lessons Learned**: Noteer nieuwe inzichten in `LESSONS_LEARNED_GUIDE.md`
- [ ] **Best Practices**: Actualiseer `BEST_PRACTICES_GUIDE.md` indien patronen wijzigen
- [ ] **Resource Verification**: YAML configs, templates, data files controleren en bijwerken; resource tests uitvoeren

### **Phase 4: Verification & Validation**

#### **Step 11: Automated Verification**
- [ ] **Wrapper Audit**: `python scripts/check_no_direct_publish.py` (moet 0 hits geven voor agent)
- [ ] **Comprehensive Audit**: `python scripts/comprehensive_agent_audit.py` (agent score 1.0)
- [ ] **Test Suite**: Alle relevante tests groen; coverage ≥ 70% (≥ 80% high‑risk)

#### **Step 12: Commit, Push & CI**
- [ ] **Commit**: Korte, duidelijke commit message
- [ ] **Push**: Trigger CI pipeline
- [ ] **CI Gates**: Lint/type/tests/security/contract checks allemaal groen

## ✅ Acceptatiecriteria per agent
- 100% wrapper‑compliance; 0 directe `publish(`
- Event‑payloads voldoen aan contract (`status`, domeinsleutel, optioneel `request_id`)
- Tests 100% groen; strategie gevolgd (`TEST_STRATEGY.md`)
- Documentatie bijgewerkt (agent .md, overview, kanban, planning)
- Comprehensive audit score: 1.0 (completeness)

## 🔧 Automatisering & Commando’s
- Wrapper scan: `python scripts/check_no_direct_publish.py`
- Agent audit: `python scripts/comprehensive_agent_audit.py | cat`
- Snelle agent tests: `pytest tests/unit/agents/test_{agent}_*.py -q`
- Volledige tests (subset): `pytest tests/unit -q && pytest tests/integration -q`

## 🔁 Periodieke Review
- Maandelijks: wrapper‑compliance, events, tests en documentatie herbevestigen
- Kwartaal: bijwerken strategie op basis van lessons learned en metrics

## 📊 **Progress Tracking**

### **Implementation Progress**
- [ ] **Agent 1**: [Agent Name] - Status: [In Progress/Complete]
- [ ] **Agent 2**: [Agent Name] - Status: [In Progress/Complete]
- [ ] **Agent 3**: [Agent Name] - Status: [In Progress/Complete]
- [ ] **...**: Continue for all 23 agents

### **Quality Metrics**
- [ ] **Test Coverage**: Target: 100% per agent
- [ ] **Code Quality**: Target: 0 linting errors
- [ ] **Documentation**: Target: 100% coverage
- [ ] **Resource Completeness**: Target: 100% complete
- [ ] **Dependency Completeness**: Target: 100% complete
- [ ] **Overall Score**: Target: 1.0 (100% completeness)

### **Success Criteria**
- [ ] **All 23 agents complete**: All required attributes and methods implemented
- [ ] **All tests passing**: 100% test success rate
- [ ] **All documentation complete**: 100% documentation coverage
- [ ] **All resources complete**: 100% resource completeness
- [ ] **All dependencies complete**: 100% dependency completeness
- [ ] **All integrations working**: Enhanced MCP, tracing, message bus working
- [ ] **Overall Score**: 1.0 (100% completeness) for all agents

## 🔄 **Continuous Improvement**

### **Lessons Learned**
- [ ] **Document Issues**: Document any issues encountered
- [ ] **Root Cause Analysis**: Analyze root causes of issues
- [ ] **Process Improvement**: Improve process based on lessons learned
- [ ] **Knowledge Sharing**: Share knowledge with team

### **Process Optimization**
- [ ] **Workflow Optimization**: Optimize workflow based on experience
- [ ] **Tool Improvement**: Improve tools and scripts
- [ ] **Documentation Updates**: Update documentation based on experience
- [ ] **Best Practices**: Update best practices

## 📚 **Related Documents**

- [Agent Completeness Prevention Strategy](../guides/AGENT_COMPLETENESS_PREVENTION_STRATEGY.md)
- [Agent Enhancement Workflow](../guides/AGENT_ENHANCEMENT_WORKFLOW.md)
- [Test Workflow Guide](../guides/TEST_WORKFLOW_GUIDE.md)
- [Quality Guide](../guides/QUALITY_GUIDE.md)
- [Best Practices Guide](../guides/BEST_PRACTICES_GUIDE.md)
- [Lessons Learned Guide](../guides/LESSONS_LEARNED_GUIDE.md)

## 🎯 **Success Criteria**

- ✅ **All 23 agents complete**: All required attributes and methods implemented
- ✅ **All tests passing**: 100% test success rate across all agents
- ✅ **All documentation complete**: 100% documentation coverage
- ✅ **All resources complete**: 100% resource completeness
- ✅ **All dependencies complete**: 100% dependency completeness
- ✅ **All integrations working**: Enhanced MCP, tracing, message bus working
- ✅ **Quality standards met**: Code quality, performance, security standards met
- ✅ **Compliance verified**: All compliance requirements met
- ✅ **Overall Score**: 1.0 (100% completeness) for all agents

## ⚠️ **Important Notes**

**CRITICAL**: Deze workflow moet strikt gevolgd worden voor elke agent implementation. Afwijkingen van deze workflow zijn niet toegestaan zonder expliciete toestemming.

**QUALITY-FIRST**: Implementeer altijd echte functionaliteit in plaats van quick fixes. Gebruik failing tests als guide voor implementation improvements.

**DOCUMENTATION**: Document alle changes en lessons learned voor toekomstige reference. 