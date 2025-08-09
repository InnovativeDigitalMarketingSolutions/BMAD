# ReleaseManager Agent

De ReleaseManager agent is verantwoordelijk voor releaseplanning, changelogs en deployment.

## Status: ✅ **FULLY COMPLIANT**

**Workflow Compliance**: Volledig geïmplementeerd met Quality-First approach
**Test Coverage**: 80/80 tests passing (100% coverage)
**Message Bus Integration**: ✅ Volledig geïmplementeerd
**Enhanced MCP Integration**: ✅ Volledig geïmplementeerd
**Tracing Integration**: ✅ Volledig geïmplementeerd

## Verantwoordelijkheden
- Plannen en coördineren van releases
- Bijhouden van changelogs
- Samenwerken met alle agents voor releasevoorbereiding
- Release lifecycle management (creation, approval, deployment, rollback)
- Performance metrics tracking en monitoring
- Enhanced MCP tool integration voor release management
- OpenTelemetry tracing voor release operations

## Belangrijke resources
- [Changelog](changelog.md)

## Samenwerking & Automatisering

De ReleaseManager werkt nauw samen met:
- **TestEngineer:** Start releaseproces na geslaagde tests.
- **DevOpsInfra:** Automatiseert deployment en monitoring.
- **Product Owner:** Wacht op goedkeuring voor release.
- **Architect:** Checkt of architecturale eisen zijn geborgd.

## Event Handlers & Message Bus Integration

De ReleaseManager kan automatisch events ontvangen en verwerken via de Message Bus:

### Input Events (Subscribed)
- `tests_passed` (TestEngineer): Start release flow.
- `release_approved` (Product Owner): Zet release live.
- `deployment_failed` (DevOpsInfra): Start rollback of notificatie.
- `release_requested`: Handle release creation requests
- `deployment_requested`: Handle deployment requests
- `rollback_requested`: Handle rollback requests
- `version_update_requested`: Handle version update requests

### Output Events (Published)
- `release_created`: Notify release creation
- `release_approved`: Notify release approval
- `release_deployed` (`EventTypes.RELEASE_DEPLOYED`): via `publish_agent_event` wrapper en event‑contract (`status`, `version`, …)
- `release_rolled_back`: Notify rollback completion
- `version_updated`: Notify version updates

### Event Contract & Wrapper
- Publicatie verloopt via `publish_agent_event(event_type, data, request_id=None)`
- Minimale payload: `status` (completed/failed), domeinspecifiek (bijv. `version`, `deployment_status`), optioneel `request_id`
- Geen directe `publish(...)` in agent‑code; CLI/demo paden kunnen kern `publish_event` gebruiken indien nodig

## Enhanced MCP Tools & Subscriptions
- Enhanced MCP Tools: `release.plan_release`, `release.approve_release`, `release.deploy_release`, `release.rollback_release`, `release.version_update`
- Tool-registratie: `register_enhanced_mcp_tools()` registreert bovenstaande tools wanneer Enhanced MCP geactiveerd is
- Subscriptions: `subscribe_to_event(event_type, callback)` biedt een passthrough naar de message bus (integratie/core/legacy fallback)

## Tracing
- `initialize_tracing()` activeert tracing en release-specifieke spans
- `trace_operation(name, data)` voegt tracepunten toe per release-operatie

## LLM Configuratie
- YAML (`releasemanager.yaml`): `llm.model: gpt-4o`, `provider: openai`, `temperature: 0.3`
- ENV override: `BMAD_LLM_RELEASEMANAGER_MODEL`
- Resolver: per-agent modelresolutie via `bmad.agents.core.ai.llm_client.resolve_agent_model`

## CLI Commands

### Core Release Management
- `create-release`: Create new release plan
- `approve-release`: Approve release for deployment
- `deploy-release`: Deploy release to production
- `rollback-release`: Rollback failed release

### Message Bus Integration
- `message-bus-status`: Show Message Bus status
- `publish-event`: Publish release management events
- `subscribe-event`: Show subscribed events
- `list-events`: List supported events
- `event-history`: Show event history
- `performance-metrics`: Show performance metrics

### Enhanced MCP Phase 2
- `enhanced-collaborate`: Enhanced collaboration with other agents
- `enhanced-security`: Enhanced security validation
- `enhanced-performance`: Enhanced performance optimization
- `trace-operation`: Trace release operations
- `trace-performance`: Trace performance metrics
- `trace-error`: Trace error analysis
- `tracing-summary`: Show tracing status
