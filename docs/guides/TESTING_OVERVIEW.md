# BMAD Testing Overview

## Document Overzicht

BMAD heeft twee complementaire test documenten die verschillende aspecten van testing behandelen:

### 📋 **TESTING_STRATEGY.md** - Strategisch Niveau
**Doel**: Test filosofie en strategie  
**Publiek**: Architects, Tech Leads, Product Owners  
**Inhoud**: Waarom, wanneer, welke test types  

**Belangrijkste Onderwerpen**:
- Test pyramid uitleg
- Balans tussen mocking vs echte integraties
- Wanneer welke test type gebruiken
- Pragmatische mocking strategie
- Test execution strategie

### 🔧 **TEST_WORKFLOW_GUIDE.md** - Tactisch Niveau
**Doel**: Praktische test workflow en implementatie  
**Publiek**: Developers, QA Engineers  
**Inhoud**: Hoe, wat, concrete voorbeelden  

**Belangrijkste Onderwerpen**:
- Concrete test workflow checklist
- Test structure en best practices
- Code voorbeelden en templates
- Quality gates en requirements
- Troubleshooting en debug tips

## Document Relatie

```
TESTING_STRATEGY.md (Waarom/Wanneer)
           ↓
    Strategie Implementatie
           ↓
TEST_WORKFLOW_GUIDE.md (Hoe/Wat)
```

## Wanneer Welk Document Gebruiken

### Voor Strategische Beslissingen
**Gebruik**: `TESTING_STRATEGY.md`
- Test type keuze (unit vs integration vs e2e)
- Mocking strategie bepaling
- Test execution planning
- Coverage requirements

### Voor Implementatie
**Gebruik**: `TEST_WORKFLOW_GUIDE.md`
- Concrete test schrijven
- Test structure opzetten
- Mocking implementatie
- Debugging test issues

### Voor Complete Understanding
**Gebruik**: Beide documenten
- Start met `TESTING_STRATEGY.md` voor context
- Volg met `TEST_WORKFLOW_GUIDE.md` voor implementatie

## Test Pyramid Implementatie

```
    🔺 E2E Tests (weinig, volledige workflows)
   🔺🔺 Integration Tests (gemiddeld, echte dependencies)
🔺🔺🔺 Unit Tests (veel, gemockt)
```

### Test Distribution
- **Unit Tests**: 70% van alle tests (snel, gemockt)
- **Integration Tests**: 20% van alle tests (echte dependencies)
- **E2E Tests**: 10% van alle tests (volledige workflows)

## Pragmatic Mocking Strategie

### Voor Zware Externe Dependencies
```python
# Mock externe modules
sys.modules['opentelemetry'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['psutil'] = MagicMock()
```

### Voordelen
- ✅ CI-robustheid (geen externe dependencies)
- ✅ Snelle feedback (milliseconden)
- ✅ Betrouwbare tests
- ✅ Goede code coverage

## Integration Testing Framework

### Execution Strategy
```bash
# Development: Alleen unit tests
pytest tests/unit/ -v

# Staging: Unit + integration tests
pytest tests/ -v --run-integration

# Production: Alle tests
pytest tests/ -v --run-integration --run-e2e
```

### Integration Test Categories
- **Database Integration**: Supabase CRUD operaties
- **LLM Integration**: OpenRouter API calls
- **Tracing Integration**: OpenTelemetry spans
- **Workflow Integration**: LangGraph workflows
- **Policy Integration**: OPA policy evaluation
- **Full Integration**: Complete workflow testing

## Success Metrics

### Test Coverage Requirements
- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 100% endpoint coverage
- **E2E Tests**: Alle kritieke user journeys

### Test Quality Requirements
- **Naming**: Beschrijvende test namen
- **Documentation**: Docstrings voor alle tests
- **Mocking**: Proper mocking van dependencies
- **Assertions**: Specifieke assertions

## Recent Success Cases

### CLI Test Coverage (✅ Complete)
- **Resultaat**: 55/55 tests slagen (100% success rate)
- **Implementatie**: Pragmatische mocking succesvol
- **Documentatie**: `CLI_TESTING_COMPLETE_REPORT.md`

### Test Strategy Validation
- **Unit Tests (gemockt)**: ✅ 55/55 slagen - Snel en betrouwbaar
- **Integration Tests (echte dependencies)**: ❌ Falen op import errors - Bewijst noodzaak van mocking
- **E2E Tests**: Framework klaar voor toekomstige implementatie

## Volgende Stappen

### Integration Testing Framework (Week 6-7)
1. **Setup Integration Test Environment**
   - Configure staging environment
   - Setup API keys voor external services
   - Implement test data management
   - Create cleanup procedures

2. **Implement Integration Test Categories**
   - Database Integration (Supabase CRUD operations)
   - LLM Integration (OpenRouter API calls)
   - Tracing Integration (OpenTelemetry spans)
   - Workflow Integration (LangGraph workflows)
   - Policy Integration (OPA policy evaluation)
   - Full Integration (Complete workflow testing)

### End-to-End Testing Framework (Week 8-9)
1. **E2E Test Strategy**
   - User Registration Flow
   - Agent Workflow Execution
   - Multi-Agent Collaboration
   - Error Recovery Scenarios
   - Performance Testing

## Referenties

- [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Test strategie en filosofie
- [TEST_WORKFLOW_GUIDE.md](./TEST_WORKFLOW_GUIDE.md) - Praktische test implementatie
- [CLI_TESTING_COMPLETE_REPORT.md](../reports/CLI_TESTING_COMPLETE_REPORT.md) - CLI testing success case
- [CLI_TEST_FAILURES_ANALYSIS.md](../reports/CLI_TEST_FAILURES_ANALYSIS.md) - Test failure analysis
- [BMAD_MASTER_PLANNING.md](../deployment/BMAD_MASTER_PLANNING.md) - Master planning met test strategie

---

**Status**: ✅ **Complete** - Beide documenten uitgewerkt en cross-referenced  
**Laatste Update**: 2 augustus 2025  
**Volgende Review**: Bij implementatie van integration testing framework 