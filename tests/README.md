# BMAD Test Suite

## Test Pyramid Structuur

De BMAD test suite is georganiseerd volgens de test pyramid principes:

```
tests/
├── unit/           # Unit tests (70% van tests) - 15 tests
│   ├── agents/     # Agent unit tests
│   ├── core/       # Core module unit tests
│   ├── cli/        # CLI unit tests
│   └── utils/      # Utility unit tests
├── integration/    # Integration tests (20% van tests) - 13 tests
│   ├── workflows/  # Workflow integration tests
│   ├── agents/     # Agent integration tests
│   └── external/   # External service integration
├── regression/     # Regression tests (5% van tests) - 0 tests
│   ├── critical/   # Critical path regression
│   ├── performance/ # Performance regression
│   └── security/   # Security regression
├── e2e/           # End-to-end tests (5% van tests) - 0 tests
│   ├── workflows/  # Complete workflow e2e
│   └── scenarios/  # Business scenario e2e
└── fixtures/      # Test fixtures en data
    ├── data/       # Test data files
    ├── mocks/      # Mock objects
    └── configs/    # Test configuraties
```

## Test Categorieën

### Unit Tests (`tests/unit/`)
- **Doel**: Testen van individuele functies en klassen in isolatie
- **Coverage**: 70% van alle tests
- **Snelheid**: Zeer snel (< 1 seconde per test)
- **Mocking**: Uitgebreid gebruik van mocks voor externe dependencies

**Voorbeelden:**
- `test_confidence_scoring.py` - Confidence scoring algoritme
- `test_redis_cache_coverage.py` - Redis cache functionaliteit
- `test_llm_client_coverage.py` - LLM client unit tests

### Integration Tests (`tests/integration/`)
- **Doel**: Testen van interacties tussen modules en externe services
- **Coverage**: 20% van alle tests
- **Snelheid**: Medium (1-5 seconden per test)
- **Mocking**: Beperkt, echte service connecties waar mogelijk

**Voorbeelden:**
- `test_advanced_workflow_coverage.py` - Workflow orchestrator integratie
- `test_clickup_integration.py` - ClickUp API integratie
- `test_bmad_agents_cli.py` - Agent CLI integratie

### Regression Tests (`tests/regression/`)
- **Doel**: Testen van kritieke paden en performance regressies
- **Coverage**: 5% van alle tests
- **Snelheid**: Langzaam (5-30 seconden per test)
- **Focus**: Kritieke business logic en performance

**Status**: Nog te implementeren

### End-to-End Tests (`tests/e2e/`)
- **Doel**: Testen van complete workflows en business scenarios
- **Coverage**: 5% van alle tests
- **Snelheid**: Zeer langzaam (30+ seconden per test)
- **Focus**: Complete user journeys

**Status**: Nog te implementeren

## Test Fixtures (`tests/fixtures/`)

### Data (`tests/fixtures/data/`)
- Test data bestanden
- Mock responses
- Configuration templates

### Mocks (`tests/fixtures/mocks/`)
- Mock object definities
- Debug utilities
- Disabled test modules

### Configs (`tests/fixtures/configs/`)
- Test configuraties
- Environment setups
- Test scenario definities

## Test Uitvoering

### Alle Tests Uitvoeren
```bash
python -m pytest tests/ -v
```

### Specifieke Test Categorieën
```bash
# Unit tests alleen
python -m pytest tests/unit/ -v

# Integration tests alleen
python -m pytest tests/integration/ -v

# Workflow tests alleen
python -m pytest tests/integration/workflows/ -v

# Agent tests alleen
python -m pytest tests/unit/agents/ tests/integration/agents/ -v
```

### Coverage Rapport
```bash
python -m pytest tests/ --cov=bmad --cov-report=html
```

## Test Best Practices

### ISTQB & TMAP Principes
1. **Test Pyramid**: 70% unit, 20% integration, 5% regression, 5% e2e
2. **Test Isolation**: Elke test is onafhankelijk
3. **Test Data Management**: Gebruik fixtures voor herbruikbare data
4. **Mocking Strategy**: Mock externe dependencies in unit tests
5. **Assertion Quality**: Gebruik specifieke assertions

### Code Quality
- **Naming**: Duidelijke test namen die het scenario beschrijven
- **Documentation**: Docstrings voor alle test functies
- **Error Handling**: Test zowel success als failure scenarios
- **Performance**: Tests moeten snel uitvoerbaar zijn

### Maintenance
- **No Test Removal**: Tests worden niet verwijderd, alleen verbeterd of uitgebreid
- **Bug Fixing**: Fix bugs in code, niet in tests
- **Regular Updates**: Update tests bij code wijzigingen
- **Coverage Monitoring**: Monitor test coverage trends

## Test Status

### Huidige Status
- ✅ **Unit Tests**: 15 tests, allemaal werkend
- ✅ **Integration Tests**: 13 tests, allemaal werkend
- ⏳ **Regression Tests**: 0 tests, te implementeren
- ⏳ **E2E Tests**: 0 tests, te implementeren

### Volgende Stappen
1. Implementeer regression tests voor kritieke paden
2. Implementeer e2e tests voor complete workflows
3. Verhoog test coverage naar 90%+
4. Implementeer performance tests
5. Implementeer security tests

## Troubleshooting

### Import Errors
Als je import errors tegenkomt:
1. Controleer of de module bestaat in de juiste directory
2. Update import paths naar de nieuwe modulaire structuur
3. Zorg dat `__init__.py` bestanden aanwezig zijn

### Test Failures
Als tests falen:
1. Controleer of de onderliggende code correct werkt
2. Fix bugs in de code, niet in de tests
3. Update tests alleen als de functionaliteit is gewijzigd

### Performance Issues
Als tests te langzaam zijn:
1. Gebruik meer mocking in unit tests
2. Paralleliseer test uitvoering
3. Optimaliseer test data setup 