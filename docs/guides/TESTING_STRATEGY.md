# BMAD Testing Strategy Guide

## Overzicht
Deze gids beschrijft de test strategie voor BMAD, inclusief de balans tussen pragmatisch mocken en echte integratie testing. Voor praktische implementatie details, zie `TEST_WORKFLOW_GUIDE.md`.

## Test Pyramid

```
    🔺 E2E Tests (weinig, volledige workflows)
   🔺🔺 Integration Tests (gemiddeld, echte dependencies)  
🔺🔺🔺 Unit Tests (veel, gemockt)
```

## 1. Unit Tests (Basis)

### Doel
- Test individuele componenten in isolatie
- Snelle feedback tijdens ontwikkeling
- Detecteer regressies in component logica

### Mocking Strategie
```python
# Pragmatisch mocken van zware externe dependencies
sys.modules['opentelemetry'] = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
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

**Voor praktische implementatie details, zie**: `TEST_WORKFLOW_GUIDE.md`

## Referenties

- [TEST_WORKFLOW_GUIDE.md](./TEST_WORKFLOW_GUIDE.md) - Praktische test implementatie
- [CLI_TESTING_COMPLETE_REPORT.md](../reports/CLI_TESTING_COMPLETE_REPORT.md) - CLI testing success case
- [CLI_TEST_FAILURES_ANALYSIS.md](../reports/CLI_TEST_FAILURES_ANALYSIS.md) - Test failure analysis 