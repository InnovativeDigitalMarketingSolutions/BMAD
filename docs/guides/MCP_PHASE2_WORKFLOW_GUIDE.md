# MCP Phase 2 Agent Enhancement Workflow Guide

## Overview
Deze guide beschrijft de gestandaardiseerde workflow voor het implementeren van MCP Phase 2 enhancements en tracing functionaliteit voor BMAD agents.

## Workflow Stappen

### 1. Pre-Implementation Analysis
- [ ] **Agent Status Check**: Controleer huidige agent implementatie
- [ ] **Resource Analysis**: Analyseer bestaande templates en data files
- [ ] **Dependency Review**: Controleer YAML configuratie en dependencies
- [ ] **Test Coverage Assessment**: Evalueer bestaande test coverage

### 2. Core Implementation
- [ ] **Import Updates**: Voeg enhanced MCP en tracing imports toe
- [ ] **Agent Initialization**: Voeg enhanced MCP en tracing attributes toe
- [ ] **Enhanced MCP Methods**: Implementeer enhanced MCP initialization en tool methods
- [ ] **Tracing Methods**: Implementeer tracing initialization en agent-specific tracing methods
- [ ] **Integration**: Integreer enhanced MCP en tracing in bestaande agent methods

### 3. CLI Extension
- [ ] **Command Addition**: Voeg enhanced MCP en tracing commands toe aan main()
- [ ] **Argument Parsing**: Implementeer argument parsing voor nieuwe commands
- [ ] **Help Update**: Update show_help() method met nieuwe commands en voorbeelden

### 4. Testing Implementation
- [ ] **Test File Creation**: Maak nieuwe test file voor enhanced MCP en tracing
- [ ] **Comprehensive Test Coverage**: 24-25 tests voor alle nieuwe functionaliteit
- [ ] **Mocking Strategy**: Gebruik uitgebreide mocking voor dependencies
- [ ] **Regression Testing**: Voer bestaande tests uit om regressies te voorkomen

### 5. Resource Management
- [ ] **Resource Check**: Controleer alle templates en data files
- [ ] **Missing Resources**: Identificeer en voeg ontbrekende resources toe
- [ ] **YAML Update**: Update YAML configuratie met nieuwe dependencies
- [ ] **Resource Test**: Voer resource completeness test uit

### 6. Documentation Updates
- [ ] **Agent Documentation**: Update agent .md file met nieuwe capabilities
- [ ] **YAML Configuration**: Update YAML met nieuwe commands en dependencies
- [ ] **Changelog**: Voeg gedetailleerde changelog entry toe
- [ ] **Project Documentation**: Update MCP Phase 2 plan en kanban board
- [ ] **Agent Overview**: Update agents-overview.md met message bus integratie status
- [ ] **Lessons Learned**: Update lessons learned guide met nieuwe ervaringen
- [ ] **Integration Report**: Maak gedetailleerd integratie rapport

### 7. Agent Documentation Maintenance (VERPLICHT)
**CRITICAL**: Deze stap is verplicht volgens de Agent Documentation Maintenance workflow.

#### 7.1 Changelog Update (VERPLICHT)
- [ ] **Nieuwe Entry**: Voeg nieuwe changelog entry toe met datum (YYYY-MM-DD)
- [ ] **Added Section**: Documenteer alle nieuwe features en functionaliteit
- [ ] **Enhanced Section**: Documenteer verbeterde bestaande functionaliteit
- [ ] **Technical Section**: Documenteer technische implementatie details
- [ ] **Impact Metrics**: Voeg test coverage en performance metrics toe

#### 7.2 Agent .md File Update (VERPLICHT)
- [ ] **Status Update**: Update agent status (FULLY COMPLIANT, etc.)
- [ ] **Overview Section**: Update agent beschrijving en core features
- [ ] **Quality-First Section**: Documenteer quality-first implementation details
- [ ] **Test Coverage**: Documenteer test coverage en quality metrics
- [ ] **Event Handlers**: Documenteer event handlers met echte functionaliteit
- [ ] **Resource Management**: Documenteer resource paths en template management
- [ ] **CLI Extension**: Documenteer CLI commands en Message Bus integration
- [ ] **MCP Integration**: Documenteer MCP capabilities en tools
- [ ] **Usage Examples**: Praktische voorbeelden voor alle features
- [ ] **Integration Points**: Beschrijving van inter-agent communicatie

#### 7.3 YAML Configuration Update (VERPLICHT)
- [ ] **Commands Section**: Alle commands met korte beschrijvingen
- [ ] **Dependencies Section**: Volledige dependency lijst
- [ ] **Persona Section**: Agent persona en core principles
- [ ] **Customization Section**: Agent-specifieke customization details

#### 7.4 Agents Overview Update (VERPLICHT)
- [ ] **Status Update**: Update agent status naar FULLY COMPLIANT indien van toepassing
- [ ] **Quality Metrics**: Voeg test coverage en quality metrics toe
- [ ] **Features Update**: Update agent features en capabilities
- [ ] **Progress Metrics**: Update overall project progress

#### 7.5 Project Documentation Sync (VERPLICHT)
- [ ] **Kanban Board**: Update progress en status in KANBAN_BOARD.md
- [ ] **Lessons Learned**: Voeg nieuwe lessons learned toe aan LESSONS_LEARNED_GUIDE.md
- [ ] **Best Practices**: Voeg nieuwe best practices toe aan BEST_PRACTICES_GUIDE.md
- [ ] **Integration Reports**: Update relevante rapporten indien nodig

### 8. Quality Assurance
- [ ] **Test Execution**: Voer alle nieuwe tests uit (24-25 tests)
- [ ] **Regression Testing**: Voer bestaande tests uit (80+ tests)
- [ ] **Resource Validation**: Controleer resource completeness
- [ ] **CLI Testing**: Test alle nieuwe CLI commands
- [ ] **Documentation Review**: Controleer alle documentatie updates

### 9. Commit and Push
- [ ] **Comprehensive Commit**: Gedetailleerde commit message met alle wijzigingen
- [ ] **Push to Repository**: Push naar GitHub branch
- [ ] **Progress Update**: Update project documentatie met voortgang

## Mandatory Requirements

### Code Standards
- **Import Consistency**: Gebruik correcte import paths voor BMADTracer en EnhancedMCPIntegration
- **Error Handling**: Graceful fallback wanneer enhanced MCP of tracing niet beschikbaar is
- **Logging**: Uitgebreide logging voor debugging en monitoring
- **Type Hints**: Volledige type hints voor alle nieuwe methods

### Testing Standards
- **Test Coverage**: Minimaal 24 tests voor nieuwe functionaliteit
- **Mocking**: Uitgebreide mocking van alle dependencies
- **Regression Prevention**: Geen regressies in bestaande functionaliteit
- **Async Testing**: Proper async test implementatie

### Documentation Standards
- **Comprehensive Updates**: Volledige documentatie update voor alle wijzigingen
- **CLI Examples**: Praktische voorbeelden voor alle nieuwe commands
- **Integration Points**: Duidelijke beschrijving van agent integraties
- **Performance Metrics**: Documentatie van performance impact
- **Changelog Maintenance**: Gedetailleerde changelog entries met datum en categorieën
- **Agent Documentation Sync**: Alle agent-specifieke documentatie moet up-to-date zijn
- **Project Documentation Sync**: Alle project documentatie moet gesynchroniseerd zijn

### Resource Standards
- **Completeness Check**: Alle resources moeten beschikbaar zijn
- **YAML Accuracy**: YAML configuratie moet alle dependencies bevatten
- **Template Quality**: Templates moeten up-to-date en relevant zijn
- **Data Integrity**: Data files moeten consistent en compleet zijn

## Agent Documentation Maintenance Checklist

### Changelog Requirements
- [ ] **Datum**: Gebruik YYYY-MM-DD formaat
- [ ] **Categorieën**: Added, Enhanced, Technical secties
- [ ] **Details**: Specifieke features en wijzigingen
- [ ] **Technical Details**: Implementatie details voor developers

### Agent .md File Requirements
- [ ] **Overview**: Update agent beschrijving en core features
- [ ] **MCP Integration**: Documenteer MCP capabilities en tools
- [ ] **CLI Commands**: Volledige command lijst met voorbeelden
- [ ] **Usage Examples**: Praktische voorbeelden voor alle features
- [ ] **Integration Points**: Beschrijving van inter-agent communicatie

### YAML Configuration Requirements
- [ ] **Commands**: Alle commands met korte beschrijvingen
- [ ] **Dependencies**: Volledige dependency lijst
- [ ] **Persona**: Agent persona en core principles
- [ ] **Customization**: Agent-specifieke customization details

### Project Documentation Sync Requirements
- [ ] **Agents Overview**: Update status en progress
- [ ] **Kanban Board**: Update task status en progress
- [ ] **Integration Reports**: Update relevante rapporten
- **Best Practices**: Voeg nieuwe lessons learned toe
- [ ] **Workflow Guides**: Update workflow guides indien nodig

## Success Criteria
- ✅ Alle tests passing (95+ tests voor quality-first agents)
- ✅ Alle bestaande tests passing (geen regressies)
- ✅ Resource completeness test successful
- ✅ CLI commands functioneel en gedocumenteerd
- ✅ Quality-first implementation met echte functionaliteit
- ✅ Resource paths correct geïmplementeerd (data_paths, template_paths)
- ✅ Event handlers met echte functionaliteit (geen mock-only)
- ✅ Documentatie volledig bijgewerkt volgens Agent Documentation Maintenance workflow
- ✅ Changelog bijgewerkt met gedetailleerde entry (datum, categorieën, details)
- ✅ Agent .md file bijgewerkt met status en quality-first details
- ✅ Agents overview bijgewerkt met nieuwe status en metrics
- ✅ Lessons learned en best practices bijgewerkt
- ✅ Kanban board gesynchroniseerd
- ✅ Commit en push succesvol
- ✅ Progress bijgewerkt in project documentatie

## Workflow Compliance
**CRITICAL**: Deze workflow moet strikt gevolgd worden voor elke agent enhancement. Afwijkingen van deze workflow zijn niet toegestaan zonder expliciete toestemming van de gebruiker.

**DOCUMENTATION COMPLIANCE**: Agent documentatie updates zijn verplicht en moeten altijd worden uitgevoerd na elke agent wijziging volgens de Agent Documentation Maintenance workflow.

**QUALITY-FIRST COMPLIANCE**: Implementeer altijd echte functionaliteit in plaats van test aanpassingen. Gebruik failing tests als guide voor implementation improvements.

**RESOURCE PATHS COMPLIANCE**: Implementeer altijd proper resource paths (data_paths en template_paths) in agent initialization voor correcte file operations.

## Reference Documents
- MCP Integration Guide: `docs/guides/MCP_INTEGRATION_GUIDE.md`
- Best Practices Guide: `docs/guides/BEST_PRACTICES_GUIDE.md`
- Lessons Learned Guide: `docs/guides/LESSONS_LEARNED_GUIDE.md`
- Agent Optimization Guide: `docs/guides/agent-optimization-guide.md`
- Quality Guide: `docs/guides/QUALITY_GUIDE.md`
- Test Workflow Guide: `docs/guides/TEST_WORKFLOW_GUIDE.md` 