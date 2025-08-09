# DataEngineer Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De DataEngineer agent is verantwoordelijk voor het ontwerpen, bouwen en monitoren van data pipelines, data kwaliteit en data-integratie binnen het BMAD platform.

## Status: ✅ **FULLY COMPLIANT**

### Test Coverage: 78/78 tests passing (100% success rate)

### Scope
- **Data Engineering**: ETL pipelines, data quality checks, data monitoring
- **Pipeline Management**: Build, monitor, and explain data pipelines
- **Quality Assurance**: Data quality validation and reporting
- **History Tracking**: Pipeline and quality history management
- **Enhanced MCP Phase 2**: Advanced collaboration and tracing capabilities
- **Message Bus Integration**: Real-time event publishing and subscription

### Event Handlers (4 enhanced)
- `handle_data_quality_check_requested`: Async handler with metric logging and history updates
- `handle_explain_pipeline`: Async handler with metric logging and history updates
- `handle_pipeline_build_requested`: Async handler with metric logging and history updates
- `handle_monitoring_requested`: Async handler with metric logging and history updates

### CLI Commands
- **Core Commands**: 15 data engineering commands
- **Message Bus Commands**: 6 commands for event management
- **Enhanced MCP Phase 2**: 7 commands for advanced features
- **Total Commands**: 28 commands

### Quality-First Implementation
- ✅ All event handlers follow Quality-First principles
- ✅ Consistent async/await patterns
- ✅ Robust error handling and input validation
- ✅ Metric logging across all operations
- ✅ History management with dual-format support
- ✅ Message Bus integration with proper event publishing

## Verantwoordelijkheden
- Ontwikkelen en onderhouden van ETL-processen
- Bewaken van data kwaliteit en validatie
- Samenwerken met Backend, Architect, Test en Security agents
- Data pipeline lifecycle management (quality checks, ETL, monitoring)
- Performance metrics tracking en monitoring
- Enhanced MCP tool integration voor data engineering
- OpenTelemetry tracing voor data operations

## Belangrijke resources
- [Best practices](../../resources/templates/dataengineer/best-practices.md)
- [Pipeline changelog](../../resources/data/dataengineer/pipeline-changelog.md)
- [Agent changelog](changelog.md)

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld als een pipeline gevalideerd is.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.

## Event Contract & Wrapper
- Publicatie via `publish_agent_event(event_type, data, request_id=None)`
- Minimale payload: `status` (completed/failed) + domeinspecifiek (bijv. `pipeline_name`, `pipeline_id`, `data_summary`), optioneel `request_id`
- Geen directe `publish(...)` in agent‑code; legacy/demo paden kunnen kern `publish_event` gebruiken

## Enhanced MCP Tools & Subscriptions
- Enhanced MCP Tools: `data.quality_check`, `data.explain_pipeline`, `data.build_pipeline`, `data.monitor_pipeline`, `data.optimize_pipeline`
- Tool-registratie: `register_enhanced_mcp_tools()` registreert bovenstaande tools wanneer Enhanced MCP geactiveerd is
- Subscriptions: `subscribe_to_event(event_type, callback)` biedt een passthrough naar de message bus (integratie/core/legacy fallback)

## Tracing
- `initialize_tracing()` activeert tracing en data-specifieke spans
- `trace_operation(name, data)` voegt tracepunten toe per data engineering operatie

## LLM Configuratie
- YAML (`dataengineer.yaml`): `llm.model: gpt-4o` (of ENV override), `provider: openai`, `temperature: 0.3`
- ENV override: `BMAD_LLM_DATAENGINEER_MODEL`
- Resolver: per-agent modelresolutie via `bmad.agents.core.ai.llm_client.resolve_agent_model`
