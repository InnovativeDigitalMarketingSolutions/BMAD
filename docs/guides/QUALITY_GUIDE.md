# BMAD Quality Guide

## Overview

Dit document dient als geconsolideerde handleiding voor kwaliteitsborging in het BMAD project. Het combineert development, testing, en implementation quality standards in één comprehensive guide.

**Versie**: 3.0  
**Status**: Actief  
**Laatste Update**: 2 augustus 2025

---

## Kernprincipes

### 1. Kwaliteit boven Snelheid
- **DOEL**: Software kwaliteit verbeteren en valideren
- **NIET**: Quick fixes implementeren zonder echte verbeteringen
- **WEL**: Echte bugs oplossen, architectuur verbeteren, edge cases afhandelen

### 2. Code Behoud en Uitbreiding
- **❌ NOOIT**: Code zomaar verwijderen zonder analyse
- **✅ WEL**: Code uitbreiden en verbeteren
- **✅ WEL**: Oude code vervangen met nieuwe, verbeterde code
- **✅ WEL**: Functionaliteit behouden en uitbreiden

### 3. Test-Driven Quality Assurance
- **Doel**: Tests valideren systeemkwaliteit, niet alleen functionaliteit
- **Proces**: 
  1. Analyseer eerst de rootcause van falende tests
  2. Implementeer kwalitatieve oplossingen
  3. Fix tests niet om simpelweg te laten slagen
  4. Zorg dat oplossingen de systeemkwaliteit verbeteren

### 4. Test Coverage en Validatie
- **Na elke implementatie**: Tests opstellen voor het nieuwe onderdeel
- **Na elk afgerond onderdeel**: 
  1. Test of alles goed werkt
  2. Controleer testcoverage (doel: >90-95% voor critical, >70% voor general)
  3. Vul tests aan waar nodig
  4. Commit en push

### 5. Consistentie en Lessons Learned
- **Gebruik**: Deze geconsolideerde quality guide
- **Update**: Deze guide regelmatig met lessons learned
- **Toepassing**: Zorg dat oplossingen consistent worden toegepast

---

## Development Quality Standards

### Code Quality & Linting Standards

#### Linting Configuration
Het BMAD project gebruikt een uitgebreide `.flake8` configuratie voor consistente code kwaliteit:

```ini
[flake8]
max-line-length = 120
ignore = E501,W503,E402,F401,F541,F821,F811,F841,E265,E303,E226,W291,W293,W292,E128,E129,E305,E302,E306,E261,E504,F824,W504,E122,E116
exclude = .git,__pycache__,.venv,venv,path/to/venv,htmlcov,.pytest_cache,allure-results,test_data
per-file-ignores = 
    bmad/resources/templates/**/*.py:F821
    bmad/agents/Agent/**/*.py:E402
    bmad/agents/core/**/*.py:F401
```

#### Linting Best Practices
1. **Pre-commit Checks**: Run linting before committing code
2. **CI/CD Integration**: Automatische linting checks in pipeline
3. **Template Files**: Template files zijn uitgezonderd van strict linting
4. **Agent Files**: Agent files hebben flexibele import regels
5. **Development vs Production**: Verschillende regels voor development en production

### Backward Compatibility
- **DOEL**: Behoud van bestaande functionaliteit naast nieuwe features
- **METHODE**: Extend implementatie zonder bestaande functionaliteit te breken
- **PATTERN**: Voeg nieuwe velden toe aan bestaande return structures

### Comprehensive Error Handling
- **DOEL**: Robuuste error handling met specifieke exception types
- **METHODE**: Custom exceptions voor verschillende error types
- **PATTERN**: Graceful degradation en informative error messages

### Third-Party Integration Standards
- **DOEL**: Robuuste integratie van externe services
- **PATTERN**: Conditionele imports met fallback mechanismen
- **TESTING**: Pragmatische mocking strategie voor complexe dependencies
- **ERROR HANDLING**: Comprehensive error handling met graceful degradation
- **DOCUMENTATION**: Complete API documentation en integration guides
- **VALIDATIE**: Alle integrations hebben comprehensive test suites

---

## Testing Quality Standards

### Test Isolation
- **DOEL**: Tests moeten onafhankelijk en reproduceerbaar zijn
- **METHODE**: Proper mocking van externe dependencies
- **RESULTAAT**: Tests falen alleen bij echte regressies

### Behoud van Bestaande Tests (KRITIEK)
- **VERBODEN**: Bestaande tests aanpassen of verwijderen
- **TOEGESTAAN**: Nieuwe tests toevoegen voor nieuwe functionaliteit
- **VERPLICHT**: Als implementatie verandert, pas de implementatie aan om tests te laten slagen
- **PATTERN**: "Implementation follows tests, not tests follow implementation"

### Test Expectations vs Implementation
- **PROBLEEM**: Tests falen omdat implementatie is veranderd
- **OPLOSSING**: Pas implementatie aan om test expectations te vervullen
- **METHODE**: 
  1. Analyseer wat de test verwacht
  2. Pas implementatie aan om die verwachting te vervullen
  3. Voeg nieuwe tests toe voor nieuwe functionaliteit
  4. Verwijder NOOIT bestaande tests

### Implementatie Wijzigingen die Tests Breken (KRITIEK)
- **PROBLEEM**: Implementatie is uitgebreid/verbeterd maar bestaande tests falen
- **OPLOSSING**: Behoud backward compatibility in implementatie
- **METHODE**:
  1. **ANALYSEER**: Welke test expectations zijn gebroken?
  2. **BEHOUD**: Originele functionaliteit naast nieuwe functionaliteit
  3. **EXTEND**: Implementatie met nieuwe features zonder bestaande te breken
  4. **TEST**: Voeg nieuwe tests toe voor nieuwe features
  5. **DOCUMENT**: Waarom backward compatibility belangrijk is

**VOORBEELD**:
```python
# FOUT: Implementatie veranderen om nieuwe features toe te voegen
def method(self):
    return {"new_field": "value"}  # Breakt bestaande tests

# GOED: Backward compatibility behouden
def method(self):
    result = {"original_field": "original_value"}  # Behoud origineel
    result.update({"new_field": "value"})  # Voeg nieuw toe
    return result
```

### Thread Safety Testing (KRITIEK)
- **PROBLEEM**: Tests die vastlopen door recursive lock deadlocks of thread issues
- **SYMPTOMEN**: 
  - Tests die hangen zonder error
  - Timeout errors
  - Infinite loops
  - Thread hanging zonder duidelijke oorzaak

#### Recursive Lock Deadlock Detection
**PATROON**: Methode A verkrijgt lock en roept methode B aan die ook lock probeert te verkrijgen

```python
# ❌ PROBLEMATISCH PATROON
def update_context(self, key, value, layer=None):
    with CONTEXT_LOCK:
        entry = self.get_context_entry(key, layer)  # Probeert ook LOCK te verkrijgen
        # ... deadlock!
```

**OPLOSSING**: Gebruik reentrant locks of herstructureer code

```python
# ✅ OPLOSSING: Reentrant lock gebruiken
from threading import RLock

CONTEXT_LOCK = RLock()

def update_context(self, key, value, layer=None):
    with CONTEXT_LOCK:
        entry = self.get_context_entry(key, layer)  # Kan nu veilig lock verkrijgen
        # ... geen deadlock!
```

---

## Implementation Quality Standards

### Complete Implementation Vereisten

#### Project Planning & Context Check
- [ ] **Kanban Board Check**: Raadpleeg `docs/deployment/KANBAN_BOARD.md` voor huidige taken en status
- [ ] **Master Planning Check**: Raadpleeg `docs/deployment/BMAD_MASTER_PLANNING.md` voor uitgebreide backlog en roadmap
- [ ] **Implementation Details Check**: Raadpleeg `docs/deployment/IMPLEMENTATION_DETAILS.md` voor gedetailleerde implementatie uitleg
- [ ] **Agent Overview Check**: Raadpleeg `bmad/agents/Agent/agents-overview.md` voor complete agent lijst (23 agents)
- [ ] **Agent Status Verification**: Controleer MCP integration status van alle agents
- [ ] **Agent Dependencies**: Identificeer agent dependencies en integratie punten

#### Core Functionaliteit
- [ ] **Complete Feature Set**: Alle geplande features zijn geïmplementeerd
- [ ] **Error Handling**: Comprehensive error handling en logging
- [ ] **Input Validation**: Robuuste input validatie en sanitization
- [ ] **Documentation**: Complete inline en externe documentatie
- [ ] **Configuration**: Flexibele configuratie management

#### Integration Points
- [ ] **Framework Templates**: Integratie met bestaande framework templates
- [ ] **Agent Communication**: Inter-agent communicatie geïmplementeerd
- [ ] **External Services**: Externe service integraties getest
- [ ] **Data Persistence**: Data opslag en retrieval functionaliteit
- [ ] **Security**: Security controls en validatie

#### Testing & Quality
- [ ] **Unit Tests**: 100% test coverage voor core functionaliteit
- [ ] **Integration Tests**: End-to-end integratie tests
- [ ] **Performance Tests**: Performance en load testing
- [ ] **Security Tests**: Security validatie en penetration tests
- [ ] **User Acceptance**: User acceptance testing

### MCP Integration Vereisten

#### MCP Client Integration
- [ ] **Client Initialization**: Async client initialization geïmplementeerd
- [ ] **Connection Management**: Robust connection handling
- [ ] **Tool Registration**: Dynamic tool registration functionaliteit
- [ ] **Context Management**: Session-based context tracking
- [ ] **Error Recovery**: Connection failure recovery

#### Agent MCP Enhancement
- [ ] **MCP Import**: `from bmad.core.mcp import` toegevoegd
- [ ] **Async Initialization**: `initialize_mcp()` methode geïmplementeerd
- [ ] **Tool Usage**: `use_mcp_tool()` methode voor enhanced functionality
- [ ] **Agent-Specific Tools**: Agent-specifieke MCP tools geïmplementeerd
- [ ] **Graceful Fallback**: Local fallback mechanismen
- [ ] **Error Handling**: Comprehensive MCP error handling
- [ ] **Performance Metrics**: MCP performance monitoring

---

## Quality Assurance Workflow

### Pre-Implementation Quality Check
1. **Requirements Analysis**: Volledige analyse van requirements
2. **Design Review**: Architecture en design review
3. **Risk Assessment**: Identificeer en mitigeer risico's
4. **Resource Planning**: Zorg voor voldoende resources
5. **Timeline Validation**: Realistische timeline planning

### During Implementation Quality Check
1. **Code Review**: Regelmatige code reviews
2. **Testing**: Continuous testing tijdens development
3. **Documentation**: Real-time documentatie updates
4. **Integration Testing**: Continue integratie testing
5. **Performance Monitoring**: Real-time performance monitoring

### Post-Implementation Quality Check
1. **Comprehensive Testing**: Volledige test suite uitvoering
2. **Documentation Review**: Documentatie completeness check
3. **Performance Validation**: Performance benchmarks validatie
4. **Security Review**: Security audit en validatie
5. **User Acceptance**: User acceptance testing
6. **Deployment Validation**: Production deployment validatie

---

## Lessons Learned & Best Practices

### Development Lessons
1. **Agent Initialization**: Altijd proper error handling in agent initialization
2. **Async Development**: Gebruik async/await patterns consistent
3. **MCP Integration**: Implementeer graceful fallback voor MCP tools
4. **Error Handling**: Comprehensive error handling met specifieke exceptions
5. **Code Quality**: Volg linting standards en best practices

### Testing Lessons
1. **Test Isolation**: Zorg voor onafhankelijke en reproduceerbare tests
2. **Mocking Strategy**: Gebruik pragmatische mocking voor externe dependencies
3. **Test Data Management**: Proper test data setup en cleanup
4. **Performance Testing**: Include performance tests in test suite
5. **Security Testing**: Include security tests in test suite

### Implementation Lessons
1. **Backward Compatibility**: Behoud backward compatibility bij wijzigingen
2. **Documentation**: Documenteer alle wijzigingen en beslissingen
3. **Code Review**: Regelmatige code reviews voor kwaliteitsborging
4. **Integration Testing**: Test alle integratie punten
5. **Performance Monitoring**: Monitor performance tijdens development

---

## Quality Metrics & Monitoring

### Code Quality Metrics
- **Linting Score**: 100% linting compliance
- **Code Coverage**: >90-95% voor critical components, >70% voor general
- **Complexity**: Cyclomatic complexity < 10 per function
- **Documentation**: 100% function documentation
- **Error Handling**: Comprehensive error handling coverage

### Testing Quality Metrics
- **Test Success Rate**: 100% test success rate
- **Test Coverage**: >90-95% voor critical components, >70% voor general
- **Test Execution Time**: <5 minuten voor complete test suite
- **Test Reliability**: 100% (no flaky tests)
- **Integration Test Coverage**: 100% voor alle integratie punten

### Performance Quality Metrics
- **Response Time**: <2 seconden voor alle API endpoints
- **Throughput**: >100 requests per second
- **Resource Usage**: <80% CPU en memory usage
- **Error Rate**: <1% error rate
- **Availability**: >99.9% uptime

---

## Quality Gates

### Pre-Commit Quality Gates
- [ ] Linting passes (100% compliance)
- [ ] Unit tests pass (100% success rate)
- [ ] Code coverage meets targets
- [ ] Documentation is updated
- [ ] Error handling is comprehensive

### Pre-Merge Quality Gates
- [ ] All tests pass (100% success rate)
- [ ] Integration tests pass
- [ ] Performance tests pass
- [ ] Security tests pass
- [ ] Code review is completed
- [ ] Documentation is complete

### Pre-Deploy Quality Gates
- [ ] Full test suite passes
- [ ] Performance benchmarks are met
- [ ] Security audit is completed
- [ ] User acceptance testing is completed
- [ ] Rollback plan is ready

---

**Document Status**: Active  
**Last Updated**: 2 augustus 2025  
**Next Review**: Weekly during development  
**Owner**: Development Team 