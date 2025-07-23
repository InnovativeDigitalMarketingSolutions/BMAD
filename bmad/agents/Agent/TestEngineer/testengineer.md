# TestEngineer Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De TestEngineer agent is verantwoordelijk voor teststrategie, testautomatisering en kwaliteitsbewaking.

## Verantwoordelijkheden
- Ontwikkelen en uitvoeren van tests
- Teststrategie en coverage bewaken
- Samenwerken met Frontend, Backend, Fullstack, Architect en Security agents

## Belangrijke resources
- [Best practices](../../resources/templates/testengineer/best-practices.md)
- [Test changelog](../../resources/data/testengineer/test-changelog.md)
- [Agent changelog](changelog.md)

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld als alle tests geslaagd zijn.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.
