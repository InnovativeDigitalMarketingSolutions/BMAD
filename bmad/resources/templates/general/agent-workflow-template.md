# Agent Workflow Template

## Overview

Dit document bevat de complete workflow template voor agent development en enhancement, gebaseerd op de succesvolle Enhanced MCP integratie. Deze template dient als standaard workflow voor alle agent development activiteiten.

**Laatste Update**: 2025-01-27  
**Versie**: 1.0  
**Status**: Actief - Proven successful workflow

## 🎯 **Agent Workflow Fases**

### **Fase 1: Analyse** 🔍
**Doel**: Begrijp de agent requirements en bestaande situatie

#### **1.1 Agent Requirements Analysis**
- [ ] **Functionaliteit Analyse**: Wat moet de agent precies doen?
- [ ] **Scope Definitie**: Wat valt binnen en buiten agent scope?
- [ ] **Dependencies Identificatie**: Welke bestaande systemen zijn betrokken?
- [ ] **Impact Assessment**: Welke impact heeft dit op bestaande agent functionaliteit?

#### **1.2 Current Agent State Analysis**
- [ ] **Bestaande Agent Code Review**: Analyseer relevante bestaande agent code
- [ ] **Agent Documentation Review**: Check bestaande agent documentatie
- [ ] **Agent Test Coverage Assessment**: Evalueer huidige agent test coverage
- [ ] **Agent Performance Baseline**: Meet huidige agent performance metrics

#### **1.3 Agent Risk Assessment**
- [ ] **Technical Risks**: Identificeer technische risico's voor agent
- [ ] **Integration Risks**: Evalueer integratie risico's met andere agents
- [ ] **Regression Risks**: Beoordeel risico op regressie in agent functionaliteit
- [ ] **Mitigation Planning**: Plan risico mitigatie strategieën

### **Fase 2: Guide en Deployment Files Review** 📚
**Doel**: Raadpleeg bestaande best practices en lessons learned

#### **2.1 Agent Documentation Review**
- [ ] **Lessons Learned Guide**: `docs/guides/LESSONS_LEARNED_GUIDE.md`
- [ ] **Best Practices Guide**: `docs/guides/BEST_PRACTICES_GUIDE.md`
- [ ] **MCP Integration Guide**: `docs/guides/MCP_INTEGRATION_GUIDE.md`
- [ ] **Test Workflow Guide**: `docs/guides/TEST_WORKFLOW_GUIDE.md`
- [ ] **Agent Optimization Guide**: `docs/guides/agent-optimization-guide.md`

#### **2.2 Agent Deployment Files Review**
- [ ] **Kanban Board**: `docs/deployment/KANBAN_BOARD.md`
- [ ] **Master Planning**: `docs/deployment/BMAD_MASTER_PLANNING.md`
- [ ] **Implementation Details**: `docs/deployment/IMPLEMENTATION_DETAILS.md`
- [ ] **Agent Status Files**: Check relevante agent status documentatie

#### **2.3 Agent Pattern Identification**
- [ ] **Bestaande Agent Oplossingen**: Zoek naar vergelijkbare agent implementaties
- [ ] **Proven Agent Patterns**: Identificeer bewezen agent oplossingspatronen
- [ ] **Agent Anti-patterns**: Herken patronen die vermeden moeten worden
- [ ] **Agent Best Practices**: Noteer relevante agent best practices

### **Fase 3: Agent Wijzigingen Doorvoeren** 🔧
**Doel**: Implementeer de gewenste agent functionaliteit

#### **3.1 Agent Implementation Planning**
- [ ] **Agent Architecture Design**: Ontwerp de agent implementatie architectuur
- [ ] **Agent File Structure**: Plan agent bestandsstructuur wijzigingen
- [ ] **Agent Integration Points**: Identificeer agent integratie punten
- [ ] **Agent Error Handling**: Plan agent error handling strategie

#### **3.2 Agent Code Implementation**
- [ ] **Agent Core Implementation**: Implementeer agent hoofdfunctionaliteit
- [ ] **Agent Integration Code**: Voeg agent integratie code toe
- [ ] **Agent Error Handling**: Implementeer agent error handling
- [ ] **Agent Logging**: Voeg agent logging toe voor debugging

#### **3.3 Agent Configuration Updates**
- [ ] **Agent YAML Configuratie**: Update agent configuratie bestanden
- [ ] **Agent CLI Commands**: Voeg nieuwe agent CLI commands toe
- [ ] **Agent Environment Variables**: Update agent environment configuratie
- [ ] **Agent Dependencies**: Update agent requirements indien nodig

### **Fase 4: Agent Testen van Functionaliteit** 🧪
**Doel**: Verificeer dat de nieuwe agent functionaliteit werkt

#### **4.1 Agent Manual Testing**
- [ ] **Agent Core Functionality**: Test agent hoofdfunctionaliteit handmatig
- [ ] **Agent CLI Commands**: Test nieuwe agent CLI commands
- [ ] **Agent Integration Points**: Test agent integratie met andere agents
- [ ] **Agent Error Scenarios**: Test agent error handling scenarios

#### **4.2 Agent Automated Testing**
- [ ] **Agent Unit Tests**: Voer bestaande agent unit tests uit
- [ ] **Agent Integration Tests**: Voer agent integration tests uit
- [ ] **Agent Performance Tests**: Voer agent performance tests uit
- [ ] **Agent Regression Tests**: Controleer op agent regressie

#### **4.3 Agent Validation**
- [ ] **Agent Functional Validation**: Verificeer dat agent functionaliteit werkt zoals verwacht
- [ ] **Agent Performance Validation**: Controleer agent performance impact
- [ ] **Agent Integration Validation**: Verificeer agent integratie met andere agents
- [ ] **Agent User Experience Validation**: Test agent vanuit gebruiker perspectief

### **Fase 5: Agent Test Suite Uitbreiden** 📈
**Doel**: Zorg voor adequate agent test coverage

#### **5.1 Agent Test Analysis**
- [ ] **Agent Coverage Assessment**: Evalueer huidige agent test coverage
- [ ] **Agent Gap Identification**: Identificeer agent test gaps
- [ ] **Agent Test Strategy**: Bepaal agent test strategie voor nieuwe functionaliteit
- [ ] **Agent Test Types**: Bepaal welke agent test types nodig zijn

#### **5.2 Agent Test Implementation**
- [ ] **Agent Unit Tests**: Schrijf agent unit tests voor nieuwe functionaliteit
- [ ] **Agent Integration Tests**: Schrijf agent integration tests
- [ ] **Agent Performance Tests**: Schrijf agent performance tests indien nodig
- [ ] **Agent Error Tests**: Test agent error scenarios

#### **5.3 Agent Test Validation**
- [ ] **Agent Test Execution**: Voer alle agent tests uit
- [ ] **Agent Coverage Verification**: Controleer agent test coverage
- [ ] **Agent Test Quality**: Evalueer kwaliteit van agent tests
- [ ] **Agent CI Integration**: Zorg dat agent tests in CI pipeline werken

### **Fase 6: Agent Documentatie Bijwerken** 📝
**Doel**: Houd agent documentatie up-to-date

#### **6.1 Agent Code Documentation**
- [ ] **Agent Docstrings**: Update agent docstrings in code
- [ ] **Agent Comments**: Voeg relevante agent comments toe
- [ ] **Agent Type Hints**: Update agent type hints indien nodig
- [ ] **Agent README Files**: Update agent README bestanden

#### **6.2 Agent Technical Documentation**
- [ ] **Agent Integration Guides**: Update relevante agent integration guides
- [ ] **Agent API Documentation**: Update agent API documentatie
- [ ] **Agent Architecture Docs**: Update agent architectuur documentatie
- [ ] **Agent Deployment Docs**: Update agent deployment documentatie

#### **6.3 Agent User Documentation**
- [ ] **Agent User Guides**: Update agent user guides
- [ ] **Agent CLI Documentation**: Update agent CLI help en documentatie
- [ ] **Agent Examples**: Voeg agent gebruiksvoorbeelden toe
- [ ] **Agent Troubleshooting**: Update agent troubleshooting guides

### **Fase 7: Agent Commit en Push** 🚀
**Doel**: Version control en deployment

#### **7.1 Agent Pre-commit Checks**
- [ ] **Agent Code Quality**: Controleer agent code kwaliteit
- [ ] **Agent Test Results**: Verificeer dat alle agent tests slagen
- [ ] **Agent Documentation**: Controleer agent documentatie compleetheid
- [ ] **Agent Review**: Doe een laatste review van agent wijzigingen

#### **7.2 Agent Git Operations**
- [ ] **Agent Stage Changes**: `git add` relevante agent bestanden
- [ ] **Agent Commit**: `git commit` met beschrijvende agent message
- [ ] **Agent Push**: `git push` naar repository
- [ ] **Agent Branch Management**: Merge agent branch indien nodig

#### **7.3 Agent Post-deployment**
- [ ] **Agent Deployment Verification**: Controleer agent deployment succes
- [ ] **Agent Monitoring**: Monitor agent performance
- [ ] **Agent User Feedback**: Verzamel agent user feedback
- [ ] **Agent Lessons Learned**: Update agent lessons learned

### **Fase 8: Agent Communication** 📢
**Doel**: Communiceer agent wijzigingen naar stakeholders

#### **8.1 Agent Stakeholder Communication**
- [ ] **Agent Pre-Implementation**: Informeer stakeholders over geplande agent wijzigingen
- [ ] **Agent Implementation Progress**: Update stakeholders over agent voortgang
- [ ] **Agent Post-Implementation**: Informeer stakeholders over voltooide agent wijzigingen
- [ ] **Agent Issue Communication**: Communiceer agent issues en mitigatie strategieën

#### **8.2 Agent Team Communication**
- [ ] **Agent Team Sync**: Synchroniseer met team members over agent wijzigingen
- [ ] **Agent Knowledge Sharing**: Deel agent lessons learned en best practices
- [ ] **Agent Status Updates**: Update team over agent project status
- [ ] **Agent Collaboration**: Werk samen met relevante team members

#### **8.3 Agent Documentation Updates**
- [ ] **Agent Status Documentation**: Update agent project status documentatie
- [ ] **Agent Progress Tracking**: Track agent voortgang in project management tools
- [ ] **Agent Issue Tracking**: Update agent issue tracking systemen
- [ ] **Agent Knowledge Base**: Update agent knowledge base met nieuwe informatie

### **Fase 9: Agent Performance Monitoring** 📈
**Doel**: Monitor agent performance en optimaliseer indien nodig

#### **9.1 Agent Performance Baseline**
- [ ] **Agent Pre-Implementation Metrics**: Meet agent performance voor implementatie
- [ ] **Agent Key Performance Indicators**: Identificeer relevante agent KPIs
- [ ] **Agent Baseline Documentation**: Documenteer agent baseline metrics
- [ ] **Agent Performance Targets**: Stel agent performance targets vast

#### **9.2 Agent Performance Measurement**
- [ ] **Agent Post-Implementation Metrics**: Meet agent performance na implementatie
- [ ] **Agent Performance Comparison**: Vergelijk agent pre- en post-implementation
- [ ] **Agent Performance Analysis**: Analyseer agent performance impact
- [ ] **Agent Performance Reporting**: Rapporteer agent performance resultaten

#### **9.3 Agent Performance Alerts**
- [ ] **Agent Performance Thresholds**: Stel agent performance thresholds vast
- [ ] **Agent Alert Setup**: Setup agent alerts voor performance degradatie
- [ ] **Agent Performance Monitoring**: Continue agent performance monitoring
- [ ] **Agent Performance Optimization**: Optimaliseer agent indien nodig

### **Fase 10: Agent Security Review** 🔒
**Doel**: Review agent security en valideer security maatregelen

#### **10.1 Agent Code Security**
- [ ] **Agent Security Scan**: Voer agent security scan uit op code
- [ ] **Agent Vulnerability Assessment**: Identificeer agent security vulnerabilities
- [ ] **Agent Code Review**: Security-focused agent code review
- [ ] **Agent Security Testing**: Voer agent security tests uit

#### **10.2 Agent Configuration Security**
- [ ] **Agent Configuration Review**: Review agent configuratie voor security issues
- [ ] **Agent Access Control**: Controleer agent access control implementatie
- [ ] **Agent Secret Management**: Verificeer agent secret management
- [ ] **Agent Security Compliance**: Controleer agent compliance met security policies

#### **10.3 Agent Integration Security**
- [ ] **Agent API Security**: Verificeer security van agent API integraties
- [ ] **Agent Authentication**: Controleer agent authentication implementatie
- [ ] **Agent Authorization**: Verificeer agent authorization mechanismen
- [ ] **Agent Data Protection**: Controleer agent data protection maatregelen

### **Fase 11: Agent Rollback Procedures** 🔄
**Doel**: Plan en test agent rollback procedures

#### **11.1 Agent Code Rollback**
- [ ] **Agent Git Revert**: `git revert <commit-hash>` voor veilige agent rollback
- [ ] **Agent Git Reset**: `git reset --hard <commit-hash>` voor complete agent rollback
- [ ] **Agent Branch Rollback**: Terug naar vorige agent branch versie
- [ ] **Agent Configuration Rollback**: Restore van agent backup configuratie bestanden

#### **11.2 Agent Database Rollback**
- [ ] **Agent Database Backup**: Maak agent database backup voor implementatie
- [ ] **Agent Database Restore**: Restore van agent database backup indien nodig
- [ ] **Agent Migration Rollback**: Rollback van agent database migrations
- [ ] **Agent Data Validation**: Verificeer agent data integriteit na rollback

#### **11.3 Agent Documentation Rollback**
- [ ] **Agent Version Control**: Gebruik git voor agent documentatie versie management
- [ ] **Agent Backup Restore**: Restore van agent documentatie backups
- [ ] **Agent Change Tracking**: Track alle agent documentatie wijzigingen
- [ ] **Agent Rollback Communication**: Communiceer agent rollback naar team

## 🔧 **Agent Quality Gates**

### **Agent Pre-Implementation Gates**
- [ ] **Agent Requirements Clear**: Alle agent requirements zijn duidelijk gedefinieerd
- [ ] **Agent Documentation Reviewed**: Relevante agent documentatie is geraadpleegd
- [ ] **Agent Risk Assessment**: Agent risico's zijn geïdentificeerd en gemitigeerd
- [ ] **Agent Approval**: Agent implementatie is goedgekeurd

### **Agent Implementation Gates**
- [ ] **Agent Code Quality**: Agent code voldoet aan kwaliteitsstandaarden
- [ ] **Agent Error Handling**: Adequate agent error handling is geïmplementeerd
- [ ] **Agent Logging**: Voldoende agent logging is toegevoegd
- [ ] **Agent Integration**: Agent integratie met andere systemen werkt

### **Agent Testing Gates**
- [ ] **Agent Test Coverage**: Adequate agent test coverage is bereikt
- [ ] **Agent All Tests Pass**: Alle agent tests slagen
- [ ] **Agent Performance**: Agent performance impact is acceptabel
- [ ] **Agent Regression**: Geen agent regressie in bestaande functionaliteit

### **Agent Documentation Gates**
- [ ] **Agent Code Documentation**: Agent code is adequaat gedocumenteerd
- [ ] **Agent User Documentation**: Agent user documentatie is bijgewerkt
- [ ] **Agent Technical Documentation**: Agent technische documentatie is bijgewerkt
- [ ] **Agent Examples**: Agent gebruiksvoorbeelden zijn toegevoegd

### **Agent Deployment Gates**
- [ ] **Agent Code Review**: Agent code review is voltooid
- [ ] **Agent Tests Pass**: Alle agent tests slagen in CI/CD
- [ ] **Agent Documentation Complete**: Agent documentatie is compleet
- [ ] **Agent Deployment Success**: Agent deployment is succesvol

### **Agent Communication Gates**
- [ ] **Agent Stakeholder Notification**: Agent stakeholders zijn geïnformeerd
- [ ] **Agent Team Sync**: Agent team is gesynchroniseerd
- [ ] **Agent Status Updates**: Agent status is bijgewerkt
- [ ] **Agent Knowledge Sharing**: Agent knowledge is gedeeld

### **Agent Performance Gates**
- [ ] **Agent Baseline Measured**: Agent performance baseline is gemeten
- [ ] **Agent Performance Validated**: Agent performance is gevalideerd
- [ ] **Agent Monitoring Setup**: Agent performance monitoring is opgezet
- [ ] **Agent Alerts Configured**: Agent performance alerts zijn geconfigureerd

### **Agent Security Gates**
- [ ] **Agent Security Scan**: Agent security scan is uitgevoerd
- [ ] **Agent Vulnerabilities Addressed**: Agent security vulnerabilities zijn aangepakt
- [ ] **Agent Access Control**: Agent access control is gecontroleerd
- [ ] **Agent Compliance Verified**: Agent security compliance is geverifieerd

### **Agent Rollback Gates**
- [ ] **Agent Backup Created**: Agent backup is aangemaakt
- [ ] **Agent Rollback Plan**: Agent rollback plan is voorbereid
- [ ] **Agent Rollback Tested**: Agent rollback procedure is getest
- [ ] **Agent Rollback Documentation**: Agent rollback documentatie is bijgewerkt

## 📊 **Agent Success Metrics**

### **Agent Implementation Metrics**
- **Agent Code Quality**: Geen agent linting errors, adequate agent test coverage
- **Agent Performance**: Geen significante agent performance degradatie
- **Agent Integration**: Alle agent integratie punten werken correct
- **Agent Documentation**: Agent documentatie is compleet en up-to-date

### **Agent Process Metrics**
- **Agent Time Efficiency**: Agent workflow wordt efficiënt uitgevoerd
- **Agent Quality Focus**: Agent kwaliteit wordt voorop gesteld
- **Agent Knowledge Transfer**: Agent lessons learned worden gedeeld
- **Agent Continuous Improvement**: Agent workflow wordt continu verbeterd

## ⏱️ **Agent Time Tracking per Fase**

### **Agent Estimated Time per Fase**
- **Fase 1 (Agent Analyse)**: 15-30 minuten
- **Fase 2 (Agent Documentation Review)**: 10-20 minuten  
- **Fase 3 (Agent Implementation)**: 30-120 minuten (afhankelijk van scope)
- **Fase 4 (Agent Testing)**: 15-45 minuten
- **Fase 5 (Agent Test Suite)**: 20-60 minuten
- **Fase 6 (Agent Documentation)**: 15-30 minuten
- **Fase 7 (Agent Deployment)**: 5-15 minuten
- **Fase 8 (Agent Communication)**: 10-20 minuten
- **Fase 9 (Agent Performance)**: 15-30 minuten
- **Fase 10 (Agent Security)**: 15-30 minuten
- **Fase 11 (Agent Rollback)**: 10-20 minuten

### **Agent Total Estimated Time**
- **Agent Small Changes**: 2-4 uur
- **Agent Medium Changes**: 4-8 uur
- **Agent Large Changes**: 8-16 uur

## 📋 **Agent Checklist Template**

### **Agent Quick Reference Checklist**
```markdown
## Agent Workflow Checklist voor [Agent/Feature]

### Fase 1: Agent Analyse
- [ ] Agent requirements geanalyseerd
- [ ] Agent current state geëvalueerd
- [ ] Agent risico's geïdentificeerd

### Fase 2: Agent Documentation Review
- [ ] Agent lessons learned geraadpleegd
- [ ] Agent best practices gecontroleerd
- [ ] Agent relevante guides bekeken

### Fase 3: Agent Implementation
- [ ] Agent code geïmplementeerd
- [ ] Agent configuratie bijgewerkt
- [ ] Agent error handling toegevoegd

### Fase 4: Agent Testing
- [ ] Agent functionaliteit getest
- [ ] Agent tests uitgevoerd
- [ ] Agent validatie voltooid

### Fase 5: Agent Test Suite
- [ ] Agent tests uitgebreid
- [ ] Agent coverage gecontroleerd
- [ ] Agent CI integratie geverifieerd

### Fase 6: Agent Documentation
- [ ] Agent code gedocumenteerd
- [ ] Agent user docs bijgewerkt
- [ ] Agent technical docs bijgewerkt

### Fase 7: Agent Deployment
- [ ] Agent pre-commit checks voltooid
- [ ] Agent git operations uitgevoerd
- [ ] Agent post-deployment geverifieerd

### Fase 8: Agent Communication
- [ ] Agent stakeholders geïnformeerd
- [ ] Agent team gesynchroniseerd
- [ ] Agent status bijgewerkt
- [ ] Agent knowledge gedeeld

### Fase 9: Agent Performance
- [ ] Agent baseline gemeten
- [ ] Agent performance gevalideerd
- [ ] Agent monitoring opgezet
- [ ] Agent alerts geconfigureerd

### Fase 10: Agent Security
- [ ] Agent security scan uitgevoerd
- [ ] Agent vulnerabilities aangepakt
- [ ] Agent access control gecontroleerd
- [ ] Agent compliance geverifieerd

### Fase 11: Agent Rollback
- [ ] Agent backup aangemaakt
- [ ] Agent rollback plan voorbereid
- [ ] Agent rollback procedure getest
- [ ] Agent rollback documentatie bijgewerkt
```

---

**Document**: `bmad/resources/templates/general/agent-workflow-template.md`  
**Status**: ✅ **ACTIVE** - Proven successful agent workflow template  
**Last Update**: 2025-01-27 