# FeedbackAgent

> **Status**: ✅ **FULLY COMPLIANT** - 54/54 tests passing, Quality-First implementation

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De FeedbackAgent verzamelt, analyseert en rapporteert feedback van gebruikers en stakeholders.

## Verantwoordelijkheden
- Feedback verzamelen en analyseren
- Sentiment analysis en trend tracking
- Template quality monitoring en improvement
- Performance metrics tracking (12 feedback-specific metrics)
- Message Bus Integration voor event-driven collaboration
- Enhanced MCP Integration voor multi-agent coordination
- Tracing en monitoring van feedback operations
- Trends en rapportages genereren
- Samenwerken met Product Owner, UX/UI Designer, Test en Fullstack agents

## Belangrijke resources
- [Feedback trends](../../resources/data/feedbackagent/feedback-trends.md)
- [Feedback changelog](../../resources/data/feedbackagent/feedback-changelog.md)
- [Agent changelog](changelog.md)

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld als feedback is verzameld.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.
- **Performance Tracking:** 12 feedback-specifieke metrics worden bijgehouden en gedeeld
- **Async Event Handlers:** Real-time event processing met async/await patterns
- **Quality-First Implementation:** Echte functionaliteit in plaats van mock operations

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.

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
