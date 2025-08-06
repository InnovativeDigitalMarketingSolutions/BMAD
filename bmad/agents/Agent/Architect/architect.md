# Architect Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

## Enhanced MCP Phase 2 Integration

De Architect Agent is volledig geïntegreerd met **Enhanced MCP Phase 2** en biedt:

### 🔧 **Enhanced Features**
- **Advanced Tracing**: OpenTelemetry-gebaseerde distributed tracing voor alle architectuur operaties
- **Enhanced Collaboration**: Geavanceerde inter-agent communicatie via MCP
- **Performance Monitoring**: Real-time performance metrics en optimalisatie
- **Security Validation**: Uitgebreide security checks en policy enforcement
- **Enhanced CLI**: Nieuwe commando's voor tracing, security, performance en collaboration

### 🚀 **Enhanced Commands**
```bash
# Enhanced MCP Phase 2 Commands
python3 architect.py enhanced-collaborate    # Enhanced inter-agent communicatie
python3 architect.py enhanced-security       # Enhanced security validatie
python3 architect.py enhanced-performance    # Enhanced performance optimalisatie
python3 architect.py trace-operation         # Trace architecture operations
python3 architect.py trace-performance       # Get performance metrics
python3 architect.py trace-error             # Trace error scenarios
python3 architect.py tracing-summary         # Get tracing summary
```

### 📊 **Tracing Capabilities**
- **Operation Tracing**: Trace alle architectuur operaties met context
- **Performance Metrics**: Real-time performance monitoring
- **Error Tracking**: Gedetailleerde error tracking en debugging
- **Collaboration Tracking**: Monitor inter-agent communicatie

## Samenwerking met andere agents

De Architect werkt nauw samen met:
- **Fullstack, Backend, Frontend Developers:** Voor technische implementatie, refactoring en API design.
- **DevOps/Infra:** Voor CI/CD, infra-as-code, monitoring en deployment.
- **Product Owner:** Voor afstemming van requirements, prioriteiten en roadmap.
- **Scrummaster:** Voor sprintplanning, refinement en voortgangsbewaking.
- **AI/MLOps:** Voor integratie van AI-componenten, context/memory architectuur en MLOps best practices.
- **Security Developer:** Voor security-by-design, compliance en risicoanalyses.
- **Test Engineer:** Voor teststrategie, coverage en kwaliteitsbewaking.

De output van de Architect is direct bruikbaar voor developers, testers en business stakeholders.

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld na een architectuur review.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.
- **Enhanced MCP Integration:** Geavanceerde communicatie via MCP met real-time tracing en monitoring.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.

## Core Features

### 🏗️ **Architecture Design**
- **API Design**: RESTful API endpoints en OpenAPI/Swagger specs
- **Microservices Architecture**: Scalable microservices design
- **Event-Driven Architecture**: Event flow design en messaging patterns
- **Memory/Context Architecture**: AI context en memory management design

### 📋 **Architecture Documentation**
- **Architecture Decision Records (ADRs)**: Documentatie van architectuur beslissingen
- **Non-Functional Requirements (NFRs)**: Performance, security, scalability requirements
- **Risk Analysis**: Technische risico's en mitigatie strategieën
- **Review Checklists**: Architectuur review checklists en best practices

### 🔧 **Technical Guidance**
- **Refactoring Recommendations**: Code en architectuur refactoring suggesties
- **Infrastructure as Code**: CI/CD en deployment strategieën
- **Release Strategy**: Release en rollback strategieën
- **Proof of Concept (PoC)**: Begeleiding van PoC trajecten

### 🛡️ **Security & Quality**
- **Security Review**: Security-by-design en compliance checks
- **Tech Stack Evaluation**: Evaluatie van technologie alternatieven
- **Test Strategy**: Test strategie en coverage planning
- **Best Practices**: Architectuur best practices en patterns

## Usage Examples

### Basic Architecture Design
```bash
# Design API endpoints
python3 architect.py design-api

# Design microservices architecture
python3 architect.py microservices

# Design event-driven flows
python3 architect.py event-flow

# Design memory/context architecture
python3 architect.py memory-design
```

### Architecture Documentation
```bash
# Create Architecture Decision Record
python3 architect.py adr

# Analyze non-functional requirements
python3 architect.py nfrs

# Perform risk analysis
python3 architect.py risk-analysis

# Generate review checklist
python3 architect.py checklist
```

### Technical Guidance
```bash
# Review existing architecture
python3 architect.py review

# Suggest refactoring
python3 architect.py refactor

# Advise on infrastructure as code
python3 architect.py infra-as-code

# Plan release strategy
python3 architect.py release-strategy
```

### Enhanced MCP Phase 2 Features
```bash
# Enhanced collaboration with other agents
python3 architect.py enhanced-collaborate

# Enhanced security validation
python3 architect.py enhanced-security

# Enhanced performance optimization
python3 architect.py enhanced-performance

# Trace architecture operations
python3 architect.py trace-operation

# Get performance metrics
python3 architect.py trace-performance

# Get tracing summary
python3 architect.py tracing-summary
```

## Output Formats

De Architect Agent genereert output in verschillende formaten:

### 📄 **Markdown Documentation**
- Architecture Decision Records (ADRs)
- API specifications en contracts
- Risk analysis reports
- Review checklists
- Best practices guides

### 🔧 **Technical Specifications**
- OpenAPI/Swagger snippets
- Infrastructure as Code templates
- CI/CD pipeline configurations
- Test strategy documents

### 📊 **Analysis Reports**
- Risk assessment reports
- Performance analysis
- Security review reports
- Technology evaluation reports

### 🔄 **Export Formats**
- **Markdown**: Voor documentatie en rapporten
- **JSON**: Voor API contracts en configuraties
- **YAML**: Voor infrastructure en CI/CD configuraties
- **CSV**: Voor data analysis en metrics

## Best Practices

### 🏗️ **Architecture Design**
- **Modularity**: Design voor modulariteit en separation of concerns
- **Scalability**: Plan voor toekomstige groei en schaalbaarheid
- **Security**: Implementeer security-by-design principes
- **Performance**: Optimaliseer voor performance en efficiency

### 📋 **Documentation**
- **ADRs**: Documenteer alle belangrijke architectuur beslissingen
- **NFRs**: Definieer non-functional requirements duidelijk
- **Risk Management**: Identificeer en mitigeer technische risico's
- **Review Process**: Implementeer regelmatige architectuur reviews

### 🔧 **Technical Excellence**
- **Code Quality**: Zorg voor hoge code kwaliteit en maintainability
- **Testing**: Implementeer uitgebreide test strategieën
- **Monitoring**: Plan voor monitoring en observability
- **Deployment**: Design voor reliable deployment en rollback

## Integration with Other Agents

### 🤝 **Collaboration Patterns**
- **Product Owner**: Align architectuur met business requirements
- **Development Teams**: Provide technical guidance en best practices
- **DevOps**: Coordinate infrastructure en deployment strategieën
- **Security**: Integrate security requirements en compliance
- **Testing**: Align test strategie met architectuur design

### 📡 **Message Bus Events**
- `architecture_review_completed`: Na voltooiing van architectuur review
- `api_design_updated`: Bij updates van API design
- `risk_assessment_completed`: Na voltooiing van risico analyse
- `architecture_decision_made`: Bij nieuwe architectuur beslissingen

### 🔄 **Context Sharing**
- **Architecture Decisions**: Gedeelde context over architectuur beslissingen
- **Risk Assessments**: Gedeelde risico analyses en mitigatie strategieën
- **Technical Specifications**: Gedeelde technische specificaties en requirements
- **Review Results**: Gedeelde resultaten van architectuur reviews
