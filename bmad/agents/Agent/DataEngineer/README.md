# DataEngineer Agent

## Overview

De **DataEngineer Agent** is een gespecialiseerde agent die verantwoordelijk is voor data pipeline development, ETL processes en data architecture binnen de BMAD (Business Multi-Agent Development) suite. Deze agent focust op data kwaliteit, pipeline optimalisatie en data monitoring om ervoor te zorgen dat data workflows efficiënt en betrouwbaar zijn.

## Enhanced MCP Phase 2 Integration

### Features
- **Enhanced MCP Integration**: Volledige integratie met het Multi-Agent Communication Protocol voor Phase 2
- **Advanced Tracing**: OpenTelemetry-gebaseerde tracing voor data operaties
- **Inter-agent Communication**: Geavanceerde communicatie met andere agents
- **Performance Optimization**: Enhanced performance monitoring en optimalisatie
- **Security Validation**: Uitgebreide security validatie voor data pipelines

### Enhanced MCP Commands

#### Core Enhanced Commands
- `enhanced-collaborate` - Enhanced inter-agent communicatie
- `enhanced-security` - Enhanced security validatie
- `enhanced-performance` - Enhanced performance optimalisatie

#### Tracing Commands
- `trace-operation` - Trace data operations
- `trace-performance` - Get performance metrics
- `trace-error` - Trace error scenarios
- `tracing-summary` - Get tracing summary

## Core Functionality

### Data Pipeline Development
- **ETL Pipeline Building**: Ontwikkeling van Extract, Transform, Load pipelines
- **Data Quality Assessment**: Uitgebreide data kwaliteit checks en validatie
- **Pipeline Optimization**: Performance optimalisatie van data workflows
- **Monitoring Setup**: Real-time monitoring en alerting voor data pipelines

### Data Quality Management
- **Quality Metrics**: Implementatie van data kwaliteit metrics
- **Validation Rules**: Configuratie van data validatie regels
- **Quality Reporting**: Generatie van data kwaliteit rapporten
- **Quality History**: Tracking van data kwaliteit over tijd

### Data Architecture
- **Pipeline Design**: Architectuur van data pipelines
- **Data Flow Management**: Beheer van data flows tussen systemen
- **Integration Patterns**: Implementatie van data integratie patronen
- **Scalability Planning**: Planning voor schaalbare data oplossingen

## Integration Points

### Team Collaboration
- **AiDeveloper**: AI/ML pipeline integratie
- **BackendDeveloper**: Backend data integratie
- **DevOpsInfra**: Infrastructure en deployment
- **QualityGuardian**: Quality assurance en testing

### External Integrations
- **Supabase**: Context management en data storage
- **Slack**: Notificaties en team communicatie
- **OpenTelemetry**: Distributed tracing
- **Policy Engine**: Advanced policy management

## Usage Examples

### Basic Data Engineering
```bash
# Check data quality
python dataengineer.py data-quality-check --data-summary "Sample data"

# Explain pipeline
python dataengineer.py explain-pipeline --pipeline-code "Sample ETL pipeline"

# Build pipeline
python dataengineer.py build-pipeline --pipeline-name "ETL Pipeline"

# Monitor pipeline
python dataengineer.py monitor-pipeline --pipeline-id "pipeline_001"
```

### Enhanced MCP Operations
```bash
# Enhanced collaboration
python dataengineer.py enhanced-collaborate

# Security validation
python dataengineer.py enhanced-security

# Performance optimization
python dataengineer.py enhanced-performance

# Trace operations
python dataengineer.py trace-operation
```

### History and Reporting
```bash
# Show pipeline history
python dataengineer.py show-pipeline-history

# Show quality history
python dataengineer.py show-quality-history

# Export report
python dataengineer.py export-report --format json
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
- `bmad.agents.core.utils.framework_templates` - Framework templates

## Resources

### Templates
- `resources/templates/dataengineer/pipeline-template.py` - Pipeline templates
- `resources/templates/dataengineer/data-quality-template.md` - Data quality templates
- `resources/templates/dataengineer/etl-template.py` - ETL templates
- `resources/templates/dataengineer/monitoring-template.md` - Monitoring templates
- `resources/templates/dataengineer/performance-report-template.md` - Performance reports

### Data Files
- `resources/data/dataengineer/pipeline-changelog.md` - Pipeline changelog
- `resources/data/dataengineer/pipeline-history.md` - Pipeline history
- `resources/data/dataengineer/quality-history.md` - Quality history

## Configuration

### YAML Configuration
De agent wordt geconfigureerd via `dataengineer.yaml` met:
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
- **76 unit tests** - Volledige test coverage
- **CLI testing** - Command-line interface testing
- **Integration testing** - MCP integration testing
- **Error handling** - Comprehensive error scenarios

### Test Categories
- Agent initialization
- Data pipeline operations
- Quality assessment
- Pipeline monitoring
- Enhanced MCP functionality

## Performance Metrics

### Data Engineering Metrics
- Pipeline execution time
- Data quality scores
- ETL performance metrics
- Error rates and recovery time
- Data throughput rates

### Enhanced MCP Metrics
- Inter-agent communication latency
- Security validation performance
- Tracing overhead
- Performance optimization results

## Best Practices

### Data Engineering
1. **Data Quality**: Always validate data quality before processing
2. **Pipeline Monitoring**: Monitor pipelines continuously
3. **Error Handling**: Implement robust error handling and recovery
4. **Documentation**: Maintain comprehensive pipeline documentation
5. **Testing**: Test pipelines thoroughly before deployment

### Enhanced MCP Usage
1. **Tracing**: Enable tracing for critical data operations
2. **Security**: Use enhanced security validation for production pipelines
3. **Collaboration**: Leverage inter-agent communication for complex data workflows
4. **Performance**: Monitor and optimize enhanced MCP operations

## Troubleshooting

### Common Issues
- **Pipeline Failures**: Check data sources and transformation logic
- **Quality Issues**: Review validation rules and data sources
- **Performance Problems**: Monitor resource usage and optimization
- **Integration Issues**: Verify data format and API connections

### Debug Commands
```bash
# Check MCP status
python dataengineer.py get-mcp-status

# Test resource completeness
python dataengineer.py test

# Get tracing summary
python dataengineer.py tracing-summary
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