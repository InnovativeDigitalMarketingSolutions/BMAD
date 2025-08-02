# Testing Strategy Template

## 🎯 **Agent Testing Strategy**

**⚠️ LEVENDE DOCUMENT - Agents mogen en moeten verbeteringen aanbrengen!**

### Overzicht
Dit template beschrijft de test strategie die alle agents moeten volgen voor consistente, hoogwaardige software testing.

## Test Philosophy

### 1. Test-Driven Quality Assurance
- **Doel**: Tests valideren systeemkwaliteit, niet alleen functionaliteit
- **Proces**: 
  1. Analyseer eerst de rootcause van falende tests
  2. Implementeer kwalitatieve oplossingen
  3. Fix tests niet om simpelweg te laten slagen
  4. Zorg dat oplossingen de systeemkwaliteit verbeteren

### 2. Pragmatic Mocking Strategy
- **Doel**: Test robuustheid zonder externe dependencies
- **Methode**: Mock zware externe dependencies voor unit tests
- **Voordeel**: Snelle, betrouwbare tests in CI/CD

### 3. Integration Testing Balance
- **Doel**: Test echte integraties zonder unit test compromis
- **Methode**: Aparte integration test suites met echte dependencies
- **Voordeel**: Vertrouwen in productie readiness

## Test Pyramid

```
    🔺 E2E Tests (weinig, volledige workflows)
   🔺🔺 Integration Tests (gemiddeld, echte dependencies)  
🔺🔺🔺 Unit Tests (veel, gemockt)
```

### Test Distribution
- **Unit Tests**: 70% van alle tests (snel, gemockt)
- **Integration Tests**: 20% van alle tests (echte dependencies)
- **E2E Tests**: 10% van alle tests (volledige workflows)

## 1. Unit Tests (Basis)

### Doel
- Test individuele componenten in isolatie
- Snelle feedback tijdens ontwikkeling
- Detecteer regressies in component logica

### Mocking Strategie
```python
# Pragmatisch mocken van zware externe dependencies
import sys
from unittest.mock import MagicMock

# Mock externe modules
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['psutil'] = MagicMock()
```

### Voordelen
- ✅ Snel (milliseconden)
- ✅ Betrouwbaar (geen externe afhankelijkheden)
- ✅ CI-vriendelijk
- ✅ Goede code coverage

### Nadelen
- ❌ Test niet of integraties daadwerkelijk werken
- ❌ Kan echte integratie problemen missen

### Wanneer Gebruiken
- Dagelijkse ontwikkeling
- CI/CD pipelines
- Regressie testing
- Code reviews

### Coverage Requirements
- **Line Coverage**: 90%+
- **Branch Coverage**: 85%+
- **Function Coverage**: 95%+

## 2. Integration Tests (Kritiek)

### Doel
- Test of componenten correct samenwerken
- Verifieer dat externe integraties werken
- Detecteer API veranderingen en configuratie problemen

### Echte Dependencies
```python
# Gebruik echte services
@pytest.mark.integration
async def test_supabase_integration(self):
    # Echte database operaties
    result = await cli.create_tenant("test", "test.com", "basic")
    assert result is not None
```

### Voordelen
- ✅ Detecteert echte integratie problemen
- ✅ Verifieert API compatibiliteit
- ✅ Test configuratie en credentials
- ✅ Vertrouwen in productie readiness

### Nadelen
- ❌ Langzamer (seconden tot minuten)
- ❌ Afhankelijk van externe services
- ❌ Kan falen door externe problemen
- ❌ Vereist API keys en configuratie

### Wanneer Gebruiken
- Voor releases
- Na dependency updates
- Bij configuratie wijzigingen
- Staging environment validatie

### Integration Test Categories
- **Database Integration**: Supabase CRUD operaties
- **LLM Integration**: OpenRouter API calls
- **Tracing Integration**: OpenTelemetry spans
- **Workflow Integration**: LangGraph workflows
- **Policy Integration**: OPA policy evaluation
- **Full Integration**: Complete workflow testing

## 3. End-to-End Tests (Compleet)

### Doel
- Test volledige workflows van begin tot eind
- Verifieer systeem-brede functionaliteit
- Simuleer echte gebruikers scenarios

### Scope
```python
# Volledige workflow testing
async def test_full_workflow():
    # 1. Setup project
    # 2. Configure agents
    # 3. Execute workflow
    # 4. Verify results
    # 5. Cleanup
```

### Voordelen
- ✅ Test complete user journeys
- ✅ Detecteert systeem-brede problemen
- ✅ Vertrouwen in productie readiness

### Nadelen
- ❌ Zeer traag (minuten tot uren)
- ❌ Complexe setup en teardown
- ❌ Brittle (veel failure points)
- ❌ Duur om te onderhouden

### Wanneer Gebruiken
- Voor major releases
- Bij architectuur wijzigingen
- Voor performance validatie
- User acceptance testing

## Test Execution Strategie

### Development Workflow
```bash
# Dagelijks: Alleen unit tests
pytest tests/unit/ -v

# Voor commits: Unit + snelle integration tests
pytest tests/unit/ tests/integration/ -m "not slow" -v

# Voor releases: Alle tests
pytest tests/ -v --run-integration
```

### CI/CD Pipeline
```yaml
# Stage 1: Unit Tests (altijd)
- name: Unit Tests
  run: pytest tests/unit/ --cov=bmad

# Stage 2: Integration Tests (op staging)
- name: Integration Tests
  run: pytest tests/integration/ --run-integration
  environment: staging

# Stage 3: E2E Tests (op staging)
- name: E2E Tests
  run: pytest tests/e2e/ --run-e2e
  environment: staging
```

## Best Practices

### 1. Mock Strategie
```python
# ✅ Goed: Mock externe dependencies
sys.modules['opentelemetry'] = MagicMock()

# ❌ Slecht: Mock eigen business logic
sys.modules['bmad.core.workflow'] = MagicMock()
```

### 2. Integration Test Setup
```python
# ✅ Goed: Check environment variables
required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
if not all(os.getenv(var) for var in required_vars):
    pytest.skip("Missing required environment variables")

# ✅ Goed: Cleanup na tests
async def test_with_cleanup():
    # Create test data
    result = await create_test_data()
    
    try:
        # Run test
        assert result is not None
    finally:
        # Cleanup
        await cleanup_test_data(result["id"])
```

### 3. Test Data Management
```python
# ✅ Goed: Isolated test data
@pytest.fixture
def test_tenant():
    tenant = create_test_tenant()
    yield tenant
    cleanup_test_tenant(tenant["id"])

# ❌ Slecht: Gebruik productie data
def test_with_production_data():
    # Dit kan productie data beïnvloeden!
    pass
```

## Agent-Specific Testing Guidelines

### Voor AI Agents
- Mock LLM API calls in unit tests
- Test AI output validation en safety checks
- Implementeer integration tests met echte LLM APIs
- Test fallback mechanismen voor API failures

### Voor Development Agents
- Volg de test pyramid strategie
- Implementeer comprehensive unit tests
- Gebruik pragmatic mocking voor externe dependencies
- Valideer code quality met test coverage

### Voor Testing Agents
- Implementeer test frameworks en utilities
- Zorg voor comprehensive test coverage
- Valideer test quality en performance
- Implementeer test monitoring en reporting

## Monitoring en Alerting

### Test Metrics
- **Unit Test Coverage**: >90%
- **Integration Test Success Rate**: >95%
- **E2E Test Success Rate**: >90%
- **Test Execution Time**: <5 minuten voor unit tests

### Failure Analysis
```python
# Categoriseer test failures
FAILURE_CATEGORIES = {
    "unit": "Component logic problem",
    "integration": "External service problem", 
    "e2e": "System integration problem",
    "flaky": "Timing or race condition"
}
```

## Conclusie

De juiste balans tussen mocking en integratie testing is cruciaal:

1. **Unit Tests**: Basis voor snelle feedback en regressie detectie
2. **Integration Tests**: Essentieel voor vertrouwen in externe integraties
3. **E2E Tests**: Voor volledige systeem validatie

Door pragmatisch te mocken in unit tests en echte integraties te testen in aparte test suites, krijgen we:
- Snelle feedback tijdens ontwikkeling
- Vertrouwen dat integraties werken
- Detectie van zowel component als systeem problemen

## Agent Verbeteringen

**⚠️ AGENTS: Dit is een levend document!**

### Verbeteringen die agents mogen/moeten aanbrengen:
1. **Nieuwe Mocking Strategieën**: Voeg nieuwe mocking technieken toe
2. **Test Patterns**: Verbeter test patterns en best practices
3. **Integration Test Categories**: Voeg nieuwe integration test types toe
4. **Test Tools**: Voeg nieuwe test tools en frameworks toe
5. **Agent-Specific Guidelines**: Voeg guidelines toe voor specifieke agent types
6. **Monitoring**: Verbeter test monitoring en alerting
7. **Documentation**: Verbeter test documentatie en uitleg

### Hoe verbeteringen aanbrengen:
1. **Analyseer**: Identificeer gebieden voor verbetering
2. **Implementeer**: Test verbeteringen in praktijk
3. **Valideer**: Zorg dat verbeteringen test kwaliteit verhogen
4. **Documenteer**: Update dit template met verbeteringen
5. **Deel**: Deel verbeteringen met andere agents

---

**Status**: 🔄 **Levend Document** - Agents mogen en moeten verbeteringen aanbrengen  
**Laatste Update**: 2 augustus 2025  
**Volgende Review**: Continue door agents 