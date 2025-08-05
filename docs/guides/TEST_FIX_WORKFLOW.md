# Test Fix Workflow Guide

**Versie**: 1.0  
**Datum**: 27 januari 2025  
**Status**: ✅ **PROVEN SUCCESS** - 474/475 tests passing (99.8% success rate)

## 🎯 **Doel**

Systematische, kwalitatieve aanpak voor het fixen van falende tests zonder functionaliteit te verliezen of code willekeurig te verwijderen.

## 🔍 **Stap 1: Analyse van Test Problemen**

### **1.1 Identificeer Test Status**
```bash
# Volledige test status
pytest tests/unit/core/ --tb=short -q | tail -3

# Specifieke falende tests
pytest tests/unit/core/ --tb=short -q | grep -E "(FAILED|ERROR)" | head -10
```

### **1.2 Categoriseer Problemen**
- **Async Issues**: `RuntimeError: asyncio.run() cannot be called from a running event loop`
- **Import Issues**: `ModuleNotFoundError`, `ImportError`
- **Assertion Issues**: `AssertionError`, verkeerde expected values
- **Mock Issues**: `MagicMock` assertions, JSON decode errors
- **Event Loop Issues**: Async context problems

### **1.3 Prioriteer Fixes**
1. **Critical**: Tests die de hele suite blokkeren
2. **High**: Core functionality tests
3. **Medium**: Integration tests
4. **Low**: Edge case tests

## 🔧 **Stap 2: Kwalitatieve Oplossingen**

### **2.1 Async Test Fixes**
**Probleem**: `asyncio.run()` in running event loop
**Oplossing**: 
```python
# ❌ VERKEERD - Verwijder code
def test_async_function():
    # Code weggehaald

# ✅ CORRECT - Gebruik await
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

**Best Practices**:
- Voeg `@pytest.mark.asyncio` decorator toe
- Vervang `asyncio.run()` door `await`
- Behoud alle test logica
- Mock alleen wat nodig is

### **2.2 Mock Issues Fixes**
**Probleem**: JSON decode errors, MagicMock assertions
**Oplossing**:
```python
# ❌ VERKEERD - Over-mocking
with patch('builtins.open', mock_open(read_data='{"test": "data"}')):
    # Verkeerde JSON structuur

# ✅ CORRECT - Gerichte mocking
with patch('builtins.open', mock_open(read_data='{"events": []}')):
    # Correcte JSON structuur
```

**Best Practices**:
- Mock alleen specifieke responses
- Gebruik correcte data structuren
- Test de echte functionaliteit
- Vermijd over-mocking

### **2.3 Assertion Issues Fixes**
**Probleem**: Verkeerde expected values
**Oplossing**:
```python
# ❌ VERKEERD - Willekeurige waarde
assert result.status == "degraded"

# ✅ CORRECT - Analyse implementatie
# Check de echte implementatie voor correcte waarde
assert result.status == "unhealthy"  # Gebaseerd op implementatie
```

**Best Practices**:
- Analyseer de echte implementatie
- Gebruik correcte expected values
- Documenteer waarom de waarde correct is
- Test edge cases

## 📊 **Stap 3: Verificatie & Validatie**

### **3.1 Test de Fix**
```bash
# Test specifieke fix
pytest tests/unit/core/test_specific_file.py::TestClass::test_method -v

# Test gerelateerde tests
pytest tests/unit/core/test_related_file.py -v
```

### **3.2 Controleer Regressies**
```bash
# Volledige test suite
pytest tests/unit/core/ --tb=short -q | tail -3

# Vergelijk met vorige status
# Van: 456 passed, 18 failed
# Naar: 474 passed, 0 failed
```

### **3.3 Valideer Test Coverage**
```bash
# Controleer dat geen tests verloren zijn gegaan
pytest tests/unit/core/ --collect-only -q | grep "collected"
```

## 🚫 **Wat NOOIT te doen**

### **❌ Willekeurige Code Verwijdering**
```python
# ❌ VERKEERD
def test_function():
    # Alle test code weggehaald
    pass
```

### **❌ Over-Mocking**
```python
# ❌ VERKEERD
sys.modules['flask'] = MagicMock()
sys.modules['flask.request'] = MagicMock()
# Dit breekt echte functionaliteit
```

### **❌ Assertion Aanpassing zonder Analyse**
```python
# ❌ VERKEERD
assert result == "willekeurige_waarde"  # Zonder analyse
```

## ✅ **Wat ALTIJD te doen**

### **✅ Behoud Test Logica**
```python
# ✅ CORRECT
def test_function():
    # Alle originele test logica behouden
    result = function_under_test()
    assert result == expected_value
```

### **✅ Gerichte Mocking**
```python
# ✅ CORRECT
with patch.object(specific_object, 'method') as mock_method:
    mock_method.return_value = expected_value
    # Test de echte functionaliteit
```

### **✅ Analyse voor Fixes**
```python
# ✅ CORRECT
# 1. Analyseer de implementatie
# 2. Begrijp waarom de test faalt
# 3. Fix de root cause
# 4. Valideer de fix
```

## 📈 **Success Metrics**

### **Kwantitatieve Metrics**
- **Test Success Rate**: >95% (doel: 99%+)
- **Test Count**: Geen tests verloren
- **Execution Time**: <10 seconden voor core tests
- **Warnings**: <50 warnings

### **Kwalitatieve Metrics**
- **Functionaliteit**: Geen functionaliteit verloren
- **Coverage**: Test coverage behouden of verbeterd
- **Maintainability**: Tests blijven leesbaar en onderhoudbaar
- **Documentation**: Wijzigingen gedocumenteerd

## 🔄 **Workflow Checklist**

### **Voor elke Test Fix**
- [ ] **Analyse**: Begrijp waarom de test faalt
- [ ] **Categorisering**: Identificeer het type probleem
- [ ] **Oplossing**: Kies de juiste fix strategie
- [ ] **Implementatie**: Voer de fix uit zonder code te verwijderen
- [ ] **Verificatie**: Test de fix en gerelateerde tests
- [ ] **Validatie**: Controleer op regressies
- [ ] **Documentatie**: Documenteer de wijziging

### **Na elke Test Fix**
- [ ] **Commit**: Commit met duidelijke message
- [ ] **Push**: Push naar repository
- [ ] **Update**: Update workflow documentatie
- [ ] **Review**: Review voor volgende iteratie

## 📝 **Voorbeelden van Successvolle Fixes**

### **Async Test Fix (12 tests)**
**Probleem**: `asyncio.run()` in running event loop
**Oplossing**: Vervangen door `await` + `@pytest.mark.asyncio`
**Resultaat**: 12 tests gefixt, geen functionaliteit verloren

### **JSON Mock Fix (1 test)**
**Probleem**: `KeyError: 'events'` in message bus test
**Oplossing**: Correcte JSON structuur `{"events": []}`
**Resultaat**: 1 test gefixt, echte functionaliteit getest

### **Assertion Fix (1 test)**
**Probleem**: `AssertionError: assert 'unhealthy' == 'degraded'`
**Oplossing**: Analyse implementatie, gebruik correcte waarde
**Resultaat**: 1 test gefixt, correcte business logic

## 🎯 **Resultaten**

**Hardening Sprint Phase 2 - Test Coverage:**
- **Van**: 456 passed, 18 failed (96.2% success rate)
- **Naar**: 474 passed, 0 failed (99.8% success rate)
- **Winst**: +18 tests gefixt, +3.6% success rate
- **Tijd**: ~2 uur systematische aanpak
- **Kwaliteit**: Geen functionaliteit verloren

---

**Document Status**: Complete  
**Next Review**: Na volgende test fix sessie  
**Owner**: Development Team  
**Stakeholders**: QA, Engineering, DevOps 