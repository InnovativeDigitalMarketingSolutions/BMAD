# Orchestrator Agent

> **Status**: ✅ **FULLY COMPLIANT** - 91/91 tests passing (100% success rate), Quality-First implementation

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De Orchestrator Agent coördineert workflows en orkestreert de samenwerking tussen verschillende agents.

## Verantwoordelijkheden
- Workflow orchestration en process coordination
- Multi-agent workflow management
- Process automation en efficiency
- Event-driven workflow execution
- Performance metrics tracking (12 orchestration-specific metrics)
- Message Bus Integration voor event-driven collaboration
- Enhanced MCP Integration voor multi-agent coordination
- Tracing en monitoring van orchestration operations
- HITL (Human-in-the-Loop) decision management
- Escalation handling en workflow optimization

## Message Bus & Event Contract
- Publiceren via wrapper: agent‑niveau `await self.publish_agent_event(...)`; module‑niveau via `await publish_agent_event(...)` voor out‑of‑class handlers
- Minimale payload: `status` (bij *_COMPLETED), domeinspecifieke sleutels; `request_id` optioneel
- Voorbeeld module‑level publish: `await publish_agent_event(EventTypes.WORKFLOW_EXECUTION_REQUESTED, {"workflow_id": id})`

## Belangrijke resources
- [Orchestration best practices](../../resources/templates/orchestrator/best-practices.md)
- [Workflow templates](../../resources/templates/orchestrator/workflow-template.md)
- [Agent changelog](changelog.md)

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent publiceert events via de wrapper (agent of module‑level), bv. bij start/voltooiing van workflows.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.
- **Performance Tracking:** 12 orchestration-specifieke metrics worden bijgehouden en gedeeld
- **Async Event Handlers:** Real-time event processing met async/await patterns
- **Quality-First Implementation:** Echte functionaliteit in plaats van mock operations

**Voorbeeld:**
```python
await publish_agent_event(EventTypes.WORKFLOW_EXECUTION_REQUESTED, {"workflow_id": workflow_id})
```

## Workflow Compliance Features

### Message Bus Integration
- `initialize-message-bus`: Initialiseer Message Bus integratie
- `message-bus-status`: Toon Message Bus status en performance metrics
- `publish-event`: Publiceer events naar Message Bus
- `subscribe-event`: Subscribe op events van andere agents
- `list-events`: Toon beschikbare events
- `event-history`: Toon event history
- `performance-metrics`: Toon performance metrics

### Enhanced MCP Integration
- `enhanced-collaborate`: Geavanceerde samenwerking met andere agents
- `enhanced-security`: Security-aware operations
- `enhanced-performance`: Performance-geoptimaliseerde operaties

### Tracing & Monitoring
- `trace-operation`: Trace specifieke operaties
- `trace-performance`: Performance tracing
- `trace-error`: Error tracing en logging
- `tracing-summary`: Overzicht van tracing data

### Workflow Management
- `start-workflow`: Start een workflow
- `monitor-workflows`: Monitor actieve workflows
- `orchestrate-agents`: Orkestreer agent activiteiten
- `manage-escalations`: Beheer workflow escalaties
- `analyze-metrics`: Analyseer orchestration metrics 