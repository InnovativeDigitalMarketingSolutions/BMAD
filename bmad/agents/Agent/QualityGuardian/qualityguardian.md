# QualityGuardian Agent

**✅ Status: MESSAGE BUS INTEGRATION COMPLETED** - 53/53 tests passing (100% coverage)

## Overzicht

De QualityGuardian Agent is verantwoordelijk voor het bewaken en handhaven van code kwaliteit, test coverage, security en performance metrics. Deze agent implementeert kwaliteitsgates en zorgt voor naleving van industry standards.

## 🎯 Scope en Verantwoordelijkheden

### 1. **Externe Code Kwaliteit** (Primaire Focus)
De QualityGuardian agent controleert en garandeert de kwaliteit van **code die door andere agents wordt opgeleverd**:

- **FrontendDeveloper Agent**: Controleert React/Next.js componenten, TypeScript code, UI/UX implementaties
- **BackendDeveloper Agent**: Valideert API endpoints, database queries, business logic
- **FullstackDeveloper Agent**: Bewaakt end-to-end implementaties en integraties
- **MobileDeveloper Agent**: Controleert mobile app code en platform-specifieke implementaties
- **TestEngineer Agent**: Valideert test kwaliteit en coverage
- **SecurityDeveloper Agent**: Controleert security implementaties en best practices

### 2. **Interne Code Kwaliteit** (Secundaire Focus)
De agent controleert ook de **interne code van het BMAD systeem zelf**:

- **Agent Implementaties**: Controleert de kwaliteit van alle agent Python code
- **Core Components**: Valideert core system components en utilities
- **Integration Code**: Bewaakt integratie code en external service connectors
- **Documentation**: Controleert documentatie kwaliteit en compleetheid

### 3. **Quality Gates en Enforcement**
- **Pre-commit Gates**: Basis kwaliteitschecks voor alle code wijzigingen
- **Pre-merge Gates**: Uitgebreide kwaliteitsanalyse voor pull requests
- **Pre-deployment Gates**: Volledige kwaliteitsvalidatie voor releases
- **Post-deployment Monitoring**: Continue kwaliteitsbewaking in productie

### 4. **Cross-Agent Integration**
De QualityGuardian werkt samen met andere agents om kwaliteit te garanderen:

- **TestEngineer**: Ontvangt test coverage data en valideert test kwaliteit
- **SecurityDeveloper**: Deelt security scan resultaten en valideert security implementaties
- **ReleaseManager**: Verifieert kwaliteitsgates voor releases en blokkeert bij issues
- **FeedbackAgent**: Deelt kwaliteitsfeedback en integreert verbeteringen

## Kernfunctionaliteiten

### 1. Code Quality Analysis
- **Complexity Analysis**: Analyseert cyclomatic complexity en code duplicatie
- **Maintainability Index**: Berekent maintainability scores
- **Code Smells Detection**: Identificeert code smells en anti-patterns
- **Technical Debt Assessment**: Evalueert technische schuld

### 2. Test Coverage Monitoring
- **Coverage Tracking**: Monitort test coverage trends over tijd
- **Coverage Thresholds**: Handhaaft minimum coverage requirements
- **Coverage Reports**: Genereert gedetailleerde coverage rapporten
- **Missing Coverage Analysis**: Identificeert ongedekte code

### 3. Security Scanning
- **Vulnerability Detection**: Scant voor security vulnerabilities
- **Dependency Analysis**: Controleert dependencies op bekende issues
- **Code Security Review**: Analyseert code op security best practices
- **Security Metrics**: Trackt security metrics en trends

### 4. Performance Analysis
- **Performance Profiling**: Analyseert code performance
- **Memory Usage Analysis**: Monitort memory usage patterns
- **Response Time Analysis**: Evalueert response times
- **Performance Optimization**: Suggereert optimalisaties

### 5. Quality Gates
- **Pre-deployment Checks**: Verifieert kwaliteit voor deployment
- **Quality Thresholds**: Handhaaft minimum kwaliteitsstandaarden
- **Gate Enforcement**: Blokkeert deployments bij kwaliteitsissues
- **Quality Metrics**: Trackt kwaliteitsmetrics over tijd

## Gebruiksvoorbeelden

### Code Quality Analysis
```bash
# Voer code kwaliteit analyse uit
python -m bmad.agents.Agent.QualityGuardian.qualityguardian analyze-code-quality

# Analyseer specifieke directory
python -m bmad.agents.Agent.QualityGuardian.qualityguardian analyze-code-quality --path ./src
```

### Test Coverage Monitoring
```bash
# Monitor test coverage
python -m bmad.agents.Agent.QualityGuardian.qualityguardian monitor-test-coverage

# Stel coverage threshold in
python -m bmad.agents.Agent.QualityGuardian.qualityguardian monitor-test-coverage --threshold 80
```

### Security Scanning
```bash
# Voer security scan uit
python -m bmad.agents.Agent.QualityGuardian.qualityguardian security-scan

# Scan specifieke bestanden
python -m bmad.agents.Agent.QualityGuardian.qualityguardian security-scan --files "*.py"
```

### Quality Gate Check
```bash
# Verificeer kwaliteitsgates
python -m bmad.agents.Agent.QualityGuardian.qualityguardian quality-gate-check

# Check voor deployment
python -m bmad.agents.Agent.QualityGuardian.qualityguardian quality-gate-check --deployment
```

## Best Practices

### 1. Quality Thresholds
- **Code Coverage**: Minimum 80% test coverage
- **Complexity**: Maximum cyclomatic complexity van 10
- **Duplication**: Maximum 5% code duplicatie
- **Security**: Zero kritieke vulnerabilities

### 2. Quality Gates
- **Pre-commit**: Basis kwaliteitschecks
- **Pre-merge**: Uitgebreide kwaliteitsanalyse
- **Pre-deployment**: Volledige kwaliteitsvalidatie
- **Post-deployment**: Performance monitoring

### 3. Integration Points
- **CI/CD Pipeline**: Integreer in build process
- **Code Review**: Automatische kwaliteitsfeedback
- **Release Management**: Kwaliteitsgates voor releases
- **Monitoring**: Real-time kwaliteitsbewaking

## Anti-Patterns

### ❌ Vermijden
- Kwaliteitsgates omzeilen voor snelheid
- Coverage thresholds verlagen voor convenience
- Security issues negeren voor functionaliteit
- Performance issues uitstellen

### ✅ Best Practices
- Kwaliteit altijd voorop stellen
- Proactieve kwaliteitsbewaking
- Automatische kwaliteitsgates
- Data-driven besluitvorming

## Metrics en Reporting

### Quality Metrics
- **Code Quality Score**: 0-100 score voor code kwaliteit
- **Test Coverage**: Percentage gedekte code
- **Security Score**: Security assessment score
- **Performance Score**: Performance metrics score

### Reporting
- **Quality Reports**: Uitgebreide kwaliteitsrapporten
- **Trend Analysis**: Kwaliteits trends over tijd
- **Improvement Suggestions**: AI-powered verbeteringsvoorstellen
- **Executive Dashboards**: High-level kwaliteitsoverzicht

## Integratie met Andere Agents

### TestEngineer Agent
- Ontvangt test coverage data
- Valideert test kwaliteit
- Integreert test resultaten

### SecurityDeveloper Agent
- Deelt security scan resultaten
- Valideert security implementaties
- Integreert security best practices

### ReleaseManager Agent
- Verifieert kwaliteitsgates voor releases
- Blokkeert releases bij kwaliteitsissues
- Integreert kwaliteitsrapporten

### FeedbackAgent Agent
- Deelt kwaliteitsfeedback
- Integreert kwaliteitsverbeteringen
- Valideert feedback implementaties

## Configuratie

### Quality Thresholds
```yaml
quality_thresholds:
  code_coverage: 80
  complexity: 10
  duplication: 5
  security_score: 90
  performance_score: 85
```

### Quality Gates
```yaml
quality_gates:
  pre_commit:
    - basic_quality_check
    - security_scan
  pre_merge:
    - full_quality_analysis
    - coverage_check
  pre_deployment:
    - complete_validation
    - performance_check
```

### Integration Settings
```yaml
integrations:
  test_engineer: true
  security_developer: true
  release_manager: true
  feedback_agent: true
```

## Troubleshooting

### Veelvoorkomende Issues
1. **Low Coverage**: Verhoog test coverage of pas thresholds aan
2. **High Complexity**: Refactor code om complexity te verminderen
3. **Security Issues**: Fix security vulnerabilities voor deployment
4. **Performance Issues**: Optimaliseer code performance

### Debugging
- Controleer kwaliteitslogs voor details
- Verifieer configuratie instellingen
- Test integratie met andere agents
- Valideer resource bestanden 