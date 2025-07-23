# FeedbackAgent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De FeedbackAgent verzamelt, analyseert en rapporteert feedback van gebruikers en stakeholders.

## Verantwoordelijkheden
- Feedback verzamelen en analyseren
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

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.
