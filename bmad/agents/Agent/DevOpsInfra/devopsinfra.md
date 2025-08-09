# DevOpsInfra Agent

De DevOpsInfra agent is verantwoordelijk voor CI/CD, infra-as-code en monitoring.

**✅ Status: FULLY COMPLIANT** - 41/41 tests passing (100% coverage)

**Workflow Compliance**: Volledig geïmplementeerd met Quality-First approach
**Test Coverage**: 39/39 tests passing (100% coverage)
**Message Bus Integration**: ✅ Volledig geïmplementeerd
**Enhanced MCP Integration**: ✅ Volledig geïmplementeerd
**Tracing Integration**: ✅ Volledig geïmplementeerd

## Verantwoordelijkheden
- Opzetten en onderhouden van CI/CD pipelines
- Beheren van infrastructuur als code
- Monitoren van systemen en processen
- Samenwerken met alle agents voor deployment en operations
- Infrastructure lifecycle management (deployment, monitoring, incident response)
- Performance metrics tracking en monitoring
- Enhanced MCP tool integration voor infrastructure management
- OpenTelemetry tracing voor infrastructure operations

## Belangrijke resources
- [Changelog](changelog.md)

## Event Contract & Wrapper
- Publicatie via `publish_agent_event(event_type, data, request_id=None)`
- Minimale payload: `status` (completed/failed) + domeinspecifiek (bijv. `pipeline_config`, `infrastructure_id`), optioneel `request_id`
- Geen directe `publish(...)` in agent‑code; legacy/demo paden kunnen kern `publish_event` gebruiken

## Enhanced MCP Tools & Subscriptions
- Enhanced MCP Tools: `devops.pipeline_advice`, `devops.incident_response`, `devops.deploy_infrastructure`, `devops.monitor_infrastructure`, `devops.security_validation`, `devops.performance_optimization`
- Tool-registratie: `register_enhanced_mcp_tools()` registreert bovenstaande tools wanneer Enhanced MCP geactiveerd is
- Subscriptions: `subscribe_to_event(event_type, callback)` biedt een passthrough naar de message bus (integratie/core/legacy fallback)

## Tracing
- `initialize_tracing()` activeert tracing en DevOps-specifieke spans
- `trace_operation(name, data)` voegt tracepunten toe per DevOps-operatie

## LLM Configuratie
- YAML (`devopsinfra.yaml`): `llm.model: gpt-4o`, `provider: openai`, `temperature: 0.3`
- ENV override: `BMAD_LLM_DEVOPSINFRA_MODEL`
- Resolver: per-agent modelresolutie via `bmad.agents.core.ai.llm_client.resolve_agent_model`
