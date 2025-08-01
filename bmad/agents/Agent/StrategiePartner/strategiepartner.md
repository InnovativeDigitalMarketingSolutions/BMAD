# StrategiePartner Agent

De StrategiePartner agent bewaakt de strategie, visie en samenwerking binnen het project, met een focus op idea validation en epic creation.

## 🎯 Scope en Verantwoordelijkheden

### Primaire Focus (Externe Code Kwaliteit)
- **Idea Validation**: Valideer en verfijn vage ideeën tot concrete plannen
- **Epic Creation**: Genereer epics en Product Backlog Items (PBIs) van gevalideerde ideeën
- **Strategic Planning**: Ontwikkelen en bewaken van de projectvisie
- **Cross-Agent Coordination**: Coördineren van samenwerking tussen agents

### Secundaire Focus (Interne BMAD Systeem Kwaliteit)
- **Alignment & Brugfunctie**: Brengt businessdoelen en technische uitvoering samen
- **Strategic Advisory**: Adviseren over strategische keuzes op basis van actuele context

## 🚀 Core Functionalities

### Idea Validation & Refinement
- **`validate-idea`**: Analyseer idee completeness en genereer refinement vragen
- **`refine-idea`**: Verfijn idee op basis van aanvullende informatie
- **`create-epic-from-idea`**: Maak epic van gevalideerd idee voor ProductOwner en Scrummaster

### Strategic Planning
- **`develop-strategy`**: Ontwikkel nieuwe business strategie
- **`analyze-market`**: Voer marktanalyse uit
- **`competitive-analysis`**: Analyseer concurrentie
- **`assess-risks`**: Evalueer strategische risico's
- **`stakeholder-analysis`**: Analyseer stakeholders
- **`create-roadmap`**: Maak strategische roadmap
- **`calculate-roi`**: Bereken ROI van strategie
- **`business-model-canvas`**: Maak business model canvas

### Data Management
- **`show-strategy-history`**: Toon strategie historie
- **`show-market-data`**: Toon marktdata
- **`show-competitive-data`**: Toon competitive data
- **`show-risk-register`**: Toon risk register

## 📋 Usage Examples

### Idea Validation Workflow
```bash
# Step 1: Validate initial idea
python -m bmad.agents.Agent.StrategiePartner.strategiepartner validate-idea --idea-description "A mobile app for task management"

# Step 2: Refine idea with additional information
python -m bmad.agents.Agent.StrategiePartner.strategiepartner refine-idea --idea-description "A mobile app" --refinement-data '{"problem_statement": "Users need organization", "target_audience": "Professionals"}'

# Step 3: Create epic from validated idea
python -m bmad.agents.Agent.StrategiePartner.strategiepartner create-epic-from-idea --validated-idea '{"validation_status": "ready_for_development", "completeness_score": 85.0}'
```

### Strategic Planning
```bash
# Develop strategy
python -m bmad.agents.Agent.StrategiePartner.strategiepartner develop-strategy --strategy-name "Digital Transformation Strategy"

# Market analysis
python -m bmad.agents.Agent.StrategiePartner.strategiepartner analyze-market --sector "Technology"

# Risk assessment
python -m bmad.agents.Agent.StrategiePartner.strategiepartner assess-risks --strategy-name "Digital Transformation"
```

## 🔄 Event-Driven Integration

### Event Handlers
- **`handle_idea_validation_requested`**: Verwerk idea validation requests
- **`handle_idea_refinement_requested`**: Verwerk idea refinement requests
- **`handle_epic_creation_requested`**: Verwerk epic creation requests
- **`handle_strategy_development_requested`**: Verwerk strategy development requests
- **`handle_alignment_check_completed`**: Verwerk alignment check completion

### Event Publishing
- **`idea_validation_completed`**: Publiceer validation resultaten
- **`idea_refinement_completed`**: Publiceer refinement resultaten
- **`epic_creation_completed`**: Publiceer epic creation resultaten

## 🏗️ Workflow Integration

### Idea-to-Sprint Workflow
1. **Validate Initial Idea** (StrategiePartner)
2. **Refine Idea** (StrategiePartner)
3. **Create Epic** (StrategiePartner)
4. **Product Owner Review** (ProductOwner)
5. **Sprint Planning** (Scrummaster)

### Dependencies
- **ProductOwner**: Ontvangt epics en PBIs voor review
- **Scrummaster**: Ontvangt epics voor sprint planning
- **QualityGuardian**: Valideert kwaliteit van gegenereerde artifacts

## 📊 Metrics & Monitoring

### Performance Metrics
- **Idea Validation Success Rate**: Percentage succesvolle validaties
- **Refinement Improvement Score**: Gemiddelde verbetering per refinement
- **Epic Creation Quality**: Kwaliteit van gegenereerde epics
- **Strategy Development Time**: Tijd voor strategie ontwikkeling

### Quality Gates
- **Completeness Score**: Minimum 70% voor epic creation
- **Validation Status**: Moet "ready_for_development" zijn
- **PBI Coverage**: Alle epics moeten PBIs hebben

## 🔧 Configuration

### Environment Variables
- `SLACK_DEFAULT_CHANNEL`: Slack kanaal voor notificaties
- `SUPABASE_URL`: Supabase URL voor context sharing
- `SUPABASE_KEY`: Supabase API key

### Resource Files
- **Templates**: `resources/templates/strategiepartner/`
- **Data**: `resources/data/strategiepartner/`
- **History**: Strategy, market, competitive, and risk data

## 🚨 Troubleshooting

### Common Issues
1. **Low Completeness Score**: Voeg meer detail toe aan idee beschrijving
2. **Validation Failed**: Controleer input format en required fields
3. **Epic Creation Blocked**: Zorg dat idee eerst gevalideerd is

### Error Handling
- **StrategyValidationError**: Input validation errors
- **StrategyError**: General strategy processing errors
- **Graceful Degradation**: Fallback naar default values bij errors

## 📚 Best Practices

### Idea Validation
- Gebruik specifieke en gedetailleerde beschrijvingen
- Identificeer problem statement en target audience
- Definieer clear value proposition
- Schat effort en risico's realistisch in

### Epic Creation
- Zorg voor complete idee validatie
- Genereer realistische story points
- Identificeer dependencies tussen PBIs
- Definieer clear acceptance criteria

### Strategic Planning
- Baseer strategie op marktdata
- Evalueer concurrentie grondig
- Identificeer en mitigeer risico's
- Betrek stakeholders in analyse

## 🔗 Integration Points

### Orchestrator Integration
- **Intelligent Task Assignment**: StrategiePartner wordt geselecteerd voor idea validation tasks
- **Event Routing**: Orchestrator routeert idea validation events naar StrategiePartner
- **Workflow Coordination**: Orchestrator coördineert idea-to-sprint workflow

### Cross-Agent Communication
- **ProductOwner**: Ontvangt epics voor review en prioritization
- **Scrummaster**: Ontvangt epics voor sprint planning
- **QualityGuardian**: Valideert kwaliteit van gegenereerde artifacts
- **FeedbackAgent**: Ontvangt feedback over idea validation process

## 📈 Future Enhancements

### Planned Features
- **AI-Powered Idea Analysis**: Geavanceerde AI voor idee analyse
- **Market Trend Integration**: Real-time marktdata integratie
- **Stakeholder Feedback Loop**: Automatische stakeholder feedback verzameling
- **Predictive Analytics**: Voorspellende analyse voor idea success

### Scalability Improvements
- **Batch Processing**: Ondersteuning voor bulk idea validation
- **Template Customization**: Aanpasbare templates per project type
- **Multi-Language Support**: Ondersteuning voor meerdere talen
- **Advanced Reporting**: Geavanceerde rapportage en analytics

## 📄 Belangrijke resources
- [Changelog](changelog.md)
- [YAML Configuration](strategiepartner.yaml)
- [Integration Guide](../../../docs/integrations/AGENT_WORKFLOW_INTEGRATION_README.md)
