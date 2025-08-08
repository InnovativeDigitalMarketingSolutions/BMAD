# BMAD Agent Enhancement Workflow Guide

## Overview
Deze guide beschrijft de gestandaardiseerde workflow voor het implementeren van agent enhancements, MCP Phase 2 features en tracing functionaliteit voor BMAD agents met Quality-First Implementation principe.

## 🎯 Quality-First Implementation Principe

**KRITIEK PRINCIPE**: Implementeer **ÉÉN AGENT PER KEER** om kwaliteit en complete implementatie te kunnen waarborgen.

### Waarom Één Agent Per Keer?
- **Kwaliteitsborging**: Volledige focus op één agent voorkomt rushed implementations
- **Complete Testing**: 100% test success rate per agent voor elke stap
- **Root Cause Analysis**: Tijd voor grondige analyse bij issues in plaats van quick fixes
- **Documentation Completeness**: Volledige documentatie per agent voordat verder te gaan
- **Knowledge Transfer**: Lessons learned van één agent kunnen toegepast worden op volgende agents
- **Risk Mitigation**: Voorkomen van cascade failures door incomplete implementations

### Agent-per-Agent Workflow:
1. **Selecteer Target Agent**: Kies één specifieke agent uit de MCP Phase 2 backlog
2. **Complete Implementation**: Volg ALLE stappen hieronder voor deze ene agent
3. **Test tot 100%**: Behaal 100% test success rate voordat verder te gaan
4. **Document Volledig**: Update alle documentatie (changelog, agents-overview, kanban)
5. **Commit & Push**: Maak complete commit met alle wijzigingen
6. **Verification**: Verifieer dat agent FULLY COMPLIANT is
7. **Volgende Agent**: Ga pas daarna naar de volgende agent

**NEVER**: Werk niet aan meerdere agents tegelijk tijdens MCP Phase 2 implementatie.

## Workflow Stappen

### 1. Pre-Implementation Analysis
- [ ] **Agent Status Check**: Controleer huidige agent implementatie
- [ ] **Resource Analysis**: Analyseer bestaande templates en data files
- [ ] **Dependency Review**: Controleer YAML configuratie en dependencies
- [ ] **Test Coverage Assessment**: Evalueer bestaande test coverage

### 1.1 Agent Completeness Prevention (VERPLICHT)
- [ ] **Test-Driven Verification**: Gebruik echte test execution als primaire verificatie methode
- [ ] **Standardized Interface Check**: Verifieer dat agent alle required attributes en methods heeft
- [ ] **Enhanced MCP Integration Check**: Controleer enhanced MCP integration volgens standaard pattern
- [ ] **Automated Completeness Verification**: Run automated completeness verification script
- [ ] **Consistency Check**: Verifieer dat agent dezelfde patterns volgt als andere agents
- [ ] **Message Bus Wrapper Compliance**: Geen directe `publish(...)` in agents; gebruik `await self.publish_agent_event(...)` met minimaal `status` + domeinspecifieke sleutel en optioneel `request_id`

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
- [ ] **Mocking Strategy**: Mock `publish_agent_event` (AsyncMock) i.p.v. directe `publish(...)`
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

#### **Step 6: Message Bus Integration**
- [ ] **Message Bus Setup**: Initialize message bus integration
- [ ] **Event Handling**: Implement event handling capabilities
- [ ] **Communication Setup**: Setup inter-agent communication
- [ ] **Error Handling**: Add message bus error handling
- [ ] **Wrapper Usage**: Alle event-publicaties via `publish_agent_event` (async); geen directe `publish(...)`
- [ ] **Payload Contract**: Payload bevat minimaal `status` en een domeinspecifieke sleutel; `request_id` indien beschikbaar

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
  - [ ] **New Commands**: Voeg alle nieuw geïmplementeerde commands toe
  - [ ] **Message Bus Commands**: Voeg Message Bus commands toe (message-bus-status, publish-event, etc.)
  - [ ] **Enhanced MCP Commands**: Voeg Enhanced MCP Phase 2 commands toe
  - [ ] **Command Descriptions**: Korte Nederlandse beschrijving voor elk command
- [ ] **Dependencies Section**: Volledige dependency lijst
  - [ ] **Template Dependencies**: Update template paths voor nieuwe commands
  - [ ] **Data Dependencies**: Update data file dependencies
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

### 8. Quality Assurance & Verification (VERPLICHT)
**CRITICAL**: Deze stap zorgt ervoor dat de Quality-First Implementation principe wordt nageleefd.

- [ ] **Single Agent Focus Verified**: Bevestig dat alleen deze ene agent is gewijzigd
- [ ] **100% Test Success**: Alle tests voor deze agent passeren (geen enkele failure toegestaan)
- [ ] **No Regressions**: Bestaande functionaliteit blijft intact
- [ ] **Complete Documentation**: Alle documentatie is bijgewerkt en consistent
- [ ] **FULLY COMPLIANT Status**: Agent voldoet aan alle MCP Phase 2 eisen
- [ ] **Commit Quality**: Alle wijzigingen zijn gecommit met gedetailleerde message
- [ ] **Verification Complete**: Agent is getest en geverifieerd als complete implementation

**STOP POINT**: Ga NIET verder naar volgende agent totdat huidige agent 100% compliant is.

## Success Metrics & Quality Indicators

### Test Quality Metrics
- **Test Success Rate**: 100% target (alle tests moeten slagen)
- **Test Coverage**: >90% voor kritieke componenten, >70% voor algemene componenten  
- **Async Test Coverage**: 100% van async methodes hebben `@pytest.mark.asyncio` tests

### Code Quality Metrics
- **Linting Score**: 0 errors (flake8 compliant)
- **Documentation Coverage**: 100% van enhancement methods gedocumenteerd
- **Type Safety**: Proper type hints voor alle nieuwe methods

### Enhancement Implementation Metrics
- **Event Handler Coverage**: Minimaal 6 agent-specifieke event handlers
- **CLI Command Coverage**: Alle enhanced features beschikbaar via CLI
- **Performance Metrics**: 12+ agent-specifieke performance KPIs
- **Error Handling**: Robust error recovery en fallback mechanisms

### Integration Quality Metrics
- **MCP Tool Integration**: Agent-specifieke enhanced tools geïmplementeerd
- **Message Bus Integration**: Real-time event publishing en subscription
- **Tracing Integration**: Comprehensive operation tracing en monitoring
- **Documentation Maintenance**: Changelog, agents-overview, en kanban board bijgewerkt

## Common Issues & Troubleshooting

### Quick Reference
| Issue | Solution | Fix |
|-------|----------|-----|
| `TypeError: 'coroutine' object is not subscriptable` | Add `@pytest.mark.asyncio` and `await` | Maak test async |
| `ValueError: a coroutine was expected, got <MagicMock>` | Use `AsyncMock` for async methods | Vervang Mock met AsyncMock |
| `SyntaxError: 'await' outside async function` | Make method async | Voeg `async def` toe |
| `SystemExit: 1` in CLI tests | Fix async mocking in CLI | Mock `asyncio.run()` |
| Test failures na enhancement | Root cause analysis vereist | Gebruik Quality-First approach |

### Async Issues Prevention
- **Always use AsyncMock** voor async method mocking
- **Add @pytest.mark.asyncio** voor async test methods  
- **Use await** bij async method calls in tests
- **Mock asyncio.run()** in CLI tests met async calls

### Quality-First Problem Solving
1. **Identify Root Cause**: Analyseer de werkelijke oorzaak, niet alleen symptomen
2. **Consult Successful Agents**: Bekijk hoe andere FULLY COMPLIANT agents het oplossen
3. **Apply Systematic Solution**: Implementeer complete oplossing, geen quick fixes
4. **Test Thoroughly**: Verifieer dat oplossing geen nieuwe problemen introduceert
5. **Document Learning**: Update troubleshooting knowledge voor future agents

## 🚫 Critical DO NOT Rules

### **NEVER Remove Code Without Analysis**
```python
# ❌ VERKEERD - Willekeurige code verwijdering
def test_function():
    # Alle test code weggehaald om test te laten slagen
    pass
```

### **NEVER Over-Mock Critical Components**
```python
# ❌ VERKEERD - Over-mocking breaks real functionality
sys.modules['flask'] = MagicMock()
sys.modules['flask.request'] = MagicMock()
# Dit breekt echte functionaliteit
```

### **NEVER Adjust Assertions Without Root Cause Analysis**
```python
# ❌ VERKEERD - Assertion aanpassing zonder analyse
assert result == "willekeurige_waarde"  # Zonder te begrijpen waarom
```

### **ALWAYS Apply Quality-First Principles**
- ✅ **Extend Don't Replace**: Voeg functionaliteit toe, vervang niet
- ✅ **Root Cause Analysis**: Begrijp het werkelijke probleem
- ✅ **Test Preservation**: Behoud bestaande test logica
- ✅ **Documentation**: Document alle changes en learnings
- ✅ **Verification**: Test thoroughly na elke change

## Workflow Stappen

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
- Agent Completeness Prevention Strategy: `docs/guides/AGENT_COMPLETENESS_PREVENTION_STRATEGY.md` 