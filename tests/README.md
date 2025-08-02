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
- `test_mcp_quality_solutions.py` - MCP quality solutions testing
- `test_mcp_agent_simple.py` - MCP agent simple testing
- `test_mcp_phase2.py` - MCP phase 2 integration testing
- `test_dependency_visibility.py` - Dependency visibility testing

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

## File Organization

### Test File Locaties
Alle test files moeten in de juiste directory staan volgens de test pyramid structuur:

#### **Unit Tests** (`tests/unit/`)
- **Core Module Tests** (`tests/unit/core/`):
  - `test_enhanced_context_manager.py` - Context manager unit tests
  - `test_agent_modules.py` - Agent module unit tests
  - `test_performance_optimizer.py` - Performance optimizer tests
  - `test_core_modules.py` - Core module unit tests
  - `test_bmad_modules.py` - BMAD module unit tests
  - `test_validate_agent_resources_coverage.py` - Agent resources validation
  - `test_llm_client_coverage.py` - LLM client coverage tests
  - `test_monitoring_coverage.py` - Monitoring coverage tests
  - `test_redis_cache_coverage.py` - Redis cache coverage tests
  - `test_supabase_context_coverage.py` - Supabase context coverage tests
  - `test_notification_manager.py` - Notification manager tests
  - `test_connection_pool_coverage.py` - Connection pool coverage tests
  - `test_message_bus_coverage.py` - Message bus coverage tests
  - `test_mcp_quality_solutions.py` - MCP quality solutions testing
  - `test_mcp_agent_simple.py` - MCP agent simple testing
  - `test_mcp_phase2.py` - MCP phase 2 integration testing
  - `test_dependency_visibility.py` - Dependency visibility testing

- **Agent Tests** (`tests/unit/agents/`):
  - Agent-specifieke unit tests voor elke agent

- **CLI Tests** (`tests/unit/cli/`):
  - CLI command unit tests

- **Integration Tests** (`tests/unit/integrations/`):
  - Integration module unit tests

- **Enterprise Tests** (`tests/unit/enterprise/`):
  - Enterprise feature unit tests

- **Utils Tests** (`tests/unit/utils/`):
  - Utility function unit tests

#### **Integration Tests** (`tests/integration/`)
- **Workflow Tests** (`tests/integration/workflows/`):
  - Workflow integration tests

- **Agent Tests** (`tests/integration/agents/`):
  - Agent integration tests

- **External Tests** (`tests/integration/external/`):
  - External service integration tests

#### **Root Level Tests** (`tests/`)
- **Framework Template Tests**:
  - `test_framework_templates_core.py` - Core framework templates
  - `test_framework_templates_simple.py` - Simple framework templates
  - `test_management_framework_templates.py` - Management templates
  - `test_ai_framework_templates.py` - AI framework templates
  - `test_testing_framework_templates.py` - Testing framework templates
  - `test_development_templates_simple.py` - Development templates simple
  - `test_development_framework_templates.py` - Development framework templates
  - `test_framework_templates.py` - General framework templates

- **Microservice Tests**:
  - `test_microservices.py` - Microservice integration tests
  - `test_individual_services.py` - Individual service tests
  - `test_auth_service.py` - Auth service tests
  - `test_auth_only.py` - Auth-only tests
  - `simple_auth_test.py` - Simple auth tests

- **Database Tests**:
  - `test_database_setup.py` - Database setup tests
  - `setup_database_connection.py` - Database connection setup
  - `verify_database_tables.py` - Database table verification

### **❌ Verkeerde Locaties**
Test files die **NIET** in de root directory horen te staan:
- ~~`test_mcp_quality_solutions.py`~~ → Verplaatst naar `tests/unit/core/`
- ~~`test_mcp_agent_simple.py`~~ → Verplaatst naar `tests/unit/core/`
- ~~`test_mcp_phase2.py`~~ → Verplaatst naar `tests/unit/core/`
- ~~`test_dependency_visibility.py`~~ → Verplaatst naar `tests/unit/core/`

### **✅ Correcte Locaties**
Alle test files staan nu in de juiste directories volgens de test pyramid structuur.

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

### File Organization Best Practices
- **Test Pyramid**: Volg de 70/20/5/5 regel voor test distributie
- **Directory Structure**: Plaats tests in de juiste directory volgens functionaliteit
- **Naming Convention**: Gebruik `test_<module>_<functionality>.py` voor test files
- **No Root Tests**: Test files horen **NIET** in de root directory te staan
- **Import Paths**: Gebruik relatieve imports binnen de tests directory
- **Test Isolation**: Elke test file moet onafhankelijk uitvoerbaar zijn

### Maintenance
- **No Test Removal**: Tests worden niet verwijderd, alleen verbeterd of uitgebreid
- **Bug Fixing**: Fix bugs in code, niet in tests
- **Regular Updates**: Update tests bij code wijzigingen
- **Coverage Monitoring**: Monitor test coverage trends

## Test Status

### Huidige Status
- ✅ **Unit Tests**: 19 tests, allemaal werkend (inclusief 4 nieuwe MCP tests)
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