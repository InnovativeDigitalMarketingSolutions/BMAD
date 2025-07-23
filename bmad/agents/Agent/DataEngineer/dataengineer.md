# DataEngineer Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De DataEngineer agent is verantwoordelijk voor het ontwerpen, bouwen en monitoren van data pipelines, data kwaliteit en data-integratie binnen het BMAD platform.

## Verantwoordelijkheden
- Ontwikkelen en onderhouden van ETL-processen
- Bewaken van data kwaliteit en validatie
- Samenwerken met Backend, Architect, Test en Security agents

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
