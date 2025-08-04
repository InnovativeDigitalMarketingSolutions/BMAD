# Retrospective Agent

## Overview

De **Retrospective Agent** is een gespecialiseerde agent die verantwoordelijk is voor het faciliteren van sprint retrospectives, het verzamelen van verbeterpunten en het bewaken van opvolging binnen de BMAD (Business Multi-Agent Development) suite. Deze agent focust op teamverbetering, procesoptimalisatie en continue verbetering van development workflows.

## Enhanced MCP Phase 2 Integration

### Features
- **Enhanced MCP Integration**: Volledige integratie met het Multi-Agent Communication Protocol voor Phase 2
- **Advanced Tracing**: OpenTelemetry-gebaseerde tracing voor retrospective operaties
- **Inter-agent Communication**: Geavanceerde communicatie met andere agents
- **Performance Optimization**: Enhanced performance monitoring en optimalisatie
- **Security Validation**: Uitgebreide security validatie voor retrospective data

### Enhanced MCP Commands

#### Core Enhanced Commands
- `enhanced-collaborate` - Enhanced inter-agent communicatie
- `enhanced-security` - Enhanced security validatie
- `enhanced-performance` - Enhanced performance optimalisatie

#### Tracing Commands
- `trace-operation` - Trace retrospective operations
- `trace-performance` - Get performance metrics
- `trace-error` - Trace error scenarios
- `tracing-summary` - Get tracing summary

## Core Functionality

### Retrospective Facilitation
- **Sprint Retrospectives**: Faciliteren van sprint retrospectives met gestructureerde processen
- **Feedback Collection**: Verzamelen en analyseren van team feedback
- **Action Planning**: Genereren van concrete verbeteracties
- **Progress Tracking**: Bewaken van de voortgang van verbeteracties

### Team Improvement
- **Feedback Analysis**: Geavanceerde analyse van team feedback en sentiment
- **Action Item Generation**: Automatische generatie van concrete verbeteracties
- **Improvement Tracking**: Tracking van verbeteringen over meerdere sprints
- **Team Collaboration**: Faciliteren van team samenwerking en communicatie

### Process Optimization
- **Retrospective Templates**: Gestandaardiseerde templates voor retrospectives
- **Best Practices**: Implementatie van retrospective best practices
- **Continuous Improvement**: Continue verbetering van retrospective processen
- **Performance Metrics**: Monitoring van retrospective effectiviteit

## Integration Points

### Team Collaboration
- **Scrummaster**: Sprint planning en retrospective coördinatie
- **ProductOwner**: Product feedback en prioritering
- **QualityGuardian**: Quality assurance en testing feedback
- **FeedbackAgent**: Feedback analyse en sentiment tracking

### External Integrations
- **Supabase**: Context management en retrospective data storage
- **Slack**: Notificaties en team communicatie
- **OpenTelemetry**: Distributed tracing
- **Policy Engine**: Advanced policy management

## Usage Examples

### Basic Retrospective Operations
```bash
# Conduct retrospective
python retrospective.py conduct-retrospective --sprint-name "Sprint 15" --team-size 8

# Analyze feedback
python retrospective.py analyze-feedback --feedback-list "Good communication" "Need better documentation"

# Create action plan
python retrospective.py create-action-plan

# Track improvements
python retrospective.py track-improvements --sprint-name "Sprint 15"
```

### Enhanced MCP Operations
```bash
# Enhanced collaboration
python retrospective.py enhanced-collaborate

# Security validation
python retrospective.py enhanced-security

# Performance optimization
python retrospective.py enhanced-performance

# Trace operations
python retrospective.py trace-operation
```

### History and Reporting
```bash
# Show retrospective history
python retrospective.py show-retro-history

# Show action history
python retrospective.py show-action-history

# Export report
python retrospective.py export-report --format json
```

## Dependencies

### Core Dependencies
- `bmad.core.mcp` - MCP integration framework
- `bmad.core.mcp.enhanced_mcp_integration` - Enhanced MCP Phase 2
- `integrations.opentelemetry.opentelemetry_tracing` - Tracing capabilities
- `bmad.agents.core.agent.agent_performance_monitor` - Performance monitoring
- `bmad.agents.core.policy.advanced_policy_engine` - Policy management

### External Dependencies
- `integrations.slack.slack_notify` - Slack notifications
- `bmad.agents.core.data.supabase_context` - Context management
- `bmad.agents.core.ai.llm_client` - AI/LLM integration

## Resources

### Templates
- `resources/templates/retrospective/best-practices.md` - Best practices
- `resources/templates/retrospective/retro-template.md` - Retrospective templates
- `resources/templates/retrospective/action-plan-template.md` - Action plan templates
- `resources/templates/retrospective/feedback-template.md` - Feedback templates
- `resources/templates/retrospective/improvement-template.md` - Improvement templates
- `resources/templates/retrospective/retro-checklist-template.md` - Checklist templates

### Data Files
- `resources/data/retrospective/changelog.md` - Retrospective changelog
- `resources/data/retrospective/retro-history.md` - Retrospective history
- `resources/data/retrospective/action-history.md` - Action history

## Configuration

### YAML Configuration
De agent wordt geconfigureerd via `retrospective.yaml` met:
- Agent metadata en persona
- Command definitions
- Template dependencies
- Data file mappings

### Environment Variables
- `BMAD_ENVIRONMENT` - Environment configuration
- `SUPABASE_URL` - Supabase connection
- `SLACK_WEBHOOK_URL` - Slack notifications
- `OPENTELEMETRY_ENDPOINT` - Tracing endpoint

## Testing

### Test Coverage
- **86 unit tests** - Volledige test coverage
- **CLI testing** - Command-line interface testing
- **Integration testing** - MCP integration testing
- **Error handling** - Comprehensive error scenarios

### Test Categories
- Agent initialization
- Retrospective operations
- Feedback analysis
- Action planning
- Enhanced MCP functionality

## Performance Metrics

### Retrospective Metrics
- Feedback analysis speed
- Action generation accuracy
- Improvement tracking effectiveness
- Team satisfaction scores
- Process efficiency metrics

### Enhanced MCP Metrics
- Inter-agent communication latency
- Security validation performance
- Tracing overhead
- Performance optimization results

## Best Practices

### Retrospective Facilitation
1. **Safe Environment**: Create a safe environment for honest feedback
2. **Structured Process**: Follow a structured retrospective process
3. **Action Tracking**: Track and follow up on action items
4. **Continuous Improvement**: Focus on continuous process improvement
5. **Team Engagement**: Ensure full team participation

### Enhanced MCP Usage
1. **Tracing**: Enable tracing for critical retrospective operations
2. **Security**: Use enhanced security validation for sensitive feedback
3. **Collaboration**: Leverage inter-agent communication for complex retrospectives
4. **Performance**: Monitor and optimize enhanced MCP operations

## Troubleshooting

### Common Issues
- **Feedback Collection**: Ensure anonymous feedback collection for honest responses
- **Action Follow-up**: Implement systematic action item tracking
- **Team Participation**: Address low participation with facilitation techniques
- **Process Fatigue**: Vary retrospective formats to maintain engagement

### Debug Commands
```bash
# Check MCP status
python retrospective.py get-mcp-status

# Test resource completeness
python retrospective.py test

# Get tracing summary
python retrospective.py tracing-summary
```

## Contributing

### Development Guidelines
1. Follow BMAD coding standards
2. Maintain test coverage above 90%
3. Update documentation for new features
4. Use enhanced MCP for new integrations
5. Implement proper error handling

### Testing Requirements
- Run all unit tests before committing
- Test enhanced MCP functionality
- Verify tracing integration
- Check CLI command functionality

## License

This agent is part of the BMAD (Business Multi-Agent Development) suite and follows the project's licensing terms. 