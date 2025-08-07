# BMAD System Stabilization Workflow Guide

## Overview
Deze guide beschrijft de gestandaardiseerde workflow voor het implementeren van critical system stabilization, test infrastructure fixes, en production readiness voor BMAD met Quality-First Implementation principe.

## 🎯 Quality-First Implementation Principe

**KRITIEK PRINCIPE**: Implementeer **ÉÉN SYSTEEM COMPONENT PER KEER** om kwaliteit en complete implementatie te kunnen waarborgen.

### Waarom Één Component Per Keer?
- **Kwaliteitsborging**: Volledige focus op één component voorkomt rushed implementations
- **Complete Testing**: 100% test success rate per component voor elke stap
- **Root Cause Analysis**: Tijd voor grondige analyse bij issues in plaats van quick fixes
- **Documentation Completeness**: Volledige documentatie per component voordat verder te gaan
- **Risk Mitigation**: Voorkomen van cascade failures door incomplete implementations

### Component-per-Component Workflow:
1. **Selecteer Target Component**: Kies één specifieke system component uit Priority 0
2. **Complete Implementation**: Volg ALLE stappen hieronder voor deze ene component
3. **Test tot 100%**: Behaal 100% test success rate voordat verder te gaan
4. **Document Volledig**: Update alle documentatie (changelog, system-overview, kanban)
5. **Commit & Push**: Maak complete commit met alle wijzigingen
6. **Verification**: Verifieer dat component FULLY STABLE is
7. **Volgende Component**: Ga pas daarna naar de volgende component

**NEVER**: Werk niet aan meerdere system components tegelijk tijdens stabilization.

## Workflow Stappen

### 1. Pre-Stabilization Analysis
- [ ] **System Health Check**: Controleer huidige system status
- [ ] **Critical Issue Identification**: Identificeer alle critical issues
- [ ] **Impact Assessment**: Evalueer impact van fixes
- [ ] **Dependency Analysis**: Controleer dependencies tussen components

### 2. Test Infrastructure Stabilization (Priority 0.2)
- [ ] **Import Error Fixes**: Fix alle import errors in test files
- [ ] **Test Class Constructor Fixes**: Fix test class constructors
- [ ] **Pytest Marks Addition**: Voeg missing pytest marks toe
- [ ] **Test Coverage Completion**: Complete test coverage voor alle components
- [ ] **Test Suite Validation**: Valideer complete test suite

### 3. Critical Integration Fixes (Priority 0.1)
- [ ] **Enhanced MCP Phase 2 Activation**: Enable voor alle 23 agents
- [ ] **Message Bus Integration Activation**: Enable voor alle 23 agents
- [ ] **Tracing Integration Activation**: Enable voor alle 23 agents
- [ ] **Pytest Configuration Fixes**: Fix pytest configuration issues
- [ ] **Integration Testing**: Test alle integrations

### 4. Microservices Infrastructure Completion (Priority 0.3)
- [ ] **Docker Containerization**: Complete Docker containerization
- [ ] **Kubernetes Deployment**: Implement Kubernetes deployment
- [ ] **Service Discovery Setup**: Setup service discovery
- [ ] **Load Balancing Configuration**: Configure load balancing
- [ ] **Health Check Implementation**: Implement health checks

### 5. Security & Monitoring Implementation (Priority 0.4)
- [ ] **Security Features Completion**: Complete security features
- [ ] **Authentication/Authorization**: Implement auth system
- [ ] **Monitoring Dashboards**: Complete monitoring dashboards
- [ ] **Alerting System**: Implement alerting system
- [ ] **Performance Monitoring**: Add performance monitoring

### 6. Quality Assurance & Verification (VERPLICHT)
**CRITICAL**: Deze stap zorgt ervoor dat de Quality-First Implementation principe wordt nageleefd.

- [ ] **Single Component Focus Verified**: Bevestig dat alleen deze ene component is gewijzigd
- [ ] **100% Test Success**: Alle tests voor deze component passeren (geen enkele failure toegestaan)
- [ ] **No Regressions**: Bestaande functionaliteit blijft intact
- [ ] **Complete Documentation**: Alle documentatie is bijgewerkt en consistent
- [ ] **FULLY STABLE Status**: Component voldoet aan alle stability eisen
- [ ] **Commit Quality**: Alle wijzigingen zijn gecommit met gedetailleerde message
- [ ] **Verification Complete**: Component is getest en geverifieerd als complete implementation

**STOP POINT**: Ga NIET verder naar volgende component totdat huidige component 100% stable is.

## Success Metrics & Quality Indicators

### Test Quality Metrics
- **Test Success Rate**: 100% target (alle tests moeten slagen)
- **Test Coverage**: >90% voor kritieke componenten, >70% voor algemene componenten
- **Integration Test Coverage**: 100% van integrations hebben tests

### System Quality Metrics
- **Stability Score**: 100% target (geen critical errors)
- **Performance Impact**: <5% performance degradation
- **Security Compliance**: 100% security requirements met
- **Documentation Coverage**: 100% van stabilization methods gedocumenteerd

### Stabilization Implementation Metrics
- **Integration Coverage**: Alle 23 agents hebben working integrations
- **Test Infrastructure**: 100% functional test infrastructure
- **Microservices Readiness**: Production-ready microservices
- **Security Implementation**: Production-grade security

## Common Issues & Troubleshooting

### Quick Reference
| Issue | Solution | Fix |
|-------|----------|-----|
| Import errors in tests | Fix import paths | Update import statements |
| Test class constructor errors | Fix constructor | Remove __init__ or make it compatible |
| Unknown pytest marks | Add marks to pytest.ini | Configure pytest properly |
| Integration not working | Enable integration flags | Set _enabled flags to True |
| Docker build failures | Fix Dockerfile | Update containerization |
| Kubernetes deployment issues | Fix deployment config | Update K8s manifests |

### Quality-First Problem Solving
1. **Identify Root Cause**: Analyseer de werkelijke oorzaak, niet alleen symptomen
2. **Consult Documentation**: Bekijk bestaande guides en best practices
3. **Apply Systematic Solution**: Implementeer complete oplossing, geen quick fixes
4. **Test Thoroughly**: Verifieer dat oplossing geen nieuwe problemen introduceert
5. **Document Learning**: Update troubleshooting knowledge voor future components

## 🚫 Critical DO NOT Rules

### **NEVER Remove Code Without Analysis**
```python
# ❌ VERKEERD - Willekeurige code verwijdering
def test_function():
    # Alle test code weggehaald om test te laten slagen
    pass
```

### **NEVER Skip Critical Fixes**
```python
# ❌ VERKEERD - Critical fixes overslaan
# Skip security implementation for now
# Skip monitoring setup for now
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

### 7. Commit and Push
- [ ] **Comprehensive Commit**: Gedetailleerde commit message met alle wijzigingen
- [ ] **Push to Repository**: Push naar GitHub branch
- [ ] **Progress Update**: Update project documentatie met voortgang

## Mandatory Requirements

### Code Standards
- **Import Consistency**: Gebruik correcte import paths
- **Error Handling**: Graceful fallback wanneer features niet beschikbaar zijn
- **Logging**: Uitgebreide logging voor debugging en monitoring
- **Type Hints**: Volledige type hints voor alle nieuwe methods

### Testing Standards
- **Test Coverage**: Minimaal 90% voor kritieke componenten
- **Integration Testing**: Alle integrations getest
- **Regression Prevention**: Geen regressies in bestaande functionaliteit
- **Performance Testing**: Performance impact gemeten

### Documentation Standards
- **Comprehensive Updates**: Volledige documentatie update voor alle wijzigingen
- **System Overview**: Update system overview met nieuwe status
- **Integration Points**: Duidelijke beschrijving van system integraties
- **Performance Metrics**: Documentatie van performance impact
- **Changelog Maintenance**: Gedetailleerde changelog entries met datum en categorieën
- **Project Documentation Sync**: Alle project documentatie moet gesynchroniseerd zijn

### System Standards
- **Stability Check**: Alle system components moeten stable zijn
- **Integration Accuracy**: Alle integrations moeten correct werken
- **Security Compliance**: Alle security requirements moeten voldaan zijn
- **Performance Compliance**: Performance requirements moeten voldaan zijn

## Success Criteria
- ✅ Alle tests passing (100% test success rate)
- ✅ Alle integrations working (23/23 agents)
- ✅ System stable en production-ready
- ✅ Security implementation complete
- ✅ Monitoring implementation complete
- ✅ Microservices infrastructure complete
- ✅ Documentatie volledig bijgewerkt
- ✅ Changelog bijgewerkt met gedetailleerde entry
- ✅ System overview bijgewerkt met nieuwe status
- ✅ Kanban board gesynchroniseerd
- ✅ Commit en push succesvol
- ✅ Progress bijgewerkt in project documentatie

## Workflow Compliance
**CRITICAL**: Deze workflow moet strikt gevolgd worden voor elke system stabilization. Afwijkingen van deze workflow zijn niet toegestaan zonder expliciete toestemming van de gebruiker.

**DOCUMENTATION COMPLIANCE**: System documentatie updates zijn verplicht en moeten altijd worden uitgevoerd na elke system wijziging.

**QUALITY-FIRST COMPLIANCE**: Implementeer altijd echte functionaliteit in plaats van test aanpassingen. Gebruik failing tests als guide voor implementation improvements.

**STABILITY COMPLIANCE**: Zorg ervoor dat het systeem altijd stable blijft tijdens stabilization process.

## Reference Documents
- Agent Enhancement Workflow: `docs/guides/AGENT_ENHANCEMENT_WORKFLOW.md`
- Best Practices Guide: `docs/guides/BEST_PRACTICES_GUIDE.md`
- Lessons Learned Guide: `docs/guides/LESSONS_LEARNED_GUIDE.md`
- Quality Guide: `docs/guides/QUALITY_GUIDE.md`
- Test Workflow Guide: `docs/guides/TEST_WORKFLOW_GUIDE.md` 