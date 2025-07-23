# FullstackDeveloper Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De FullstackDeveloper agent is verantwoordelijk voor zowel frontend als backend ontwikkeling, integratie en performance.

## Verantwoordelijkheden
- Ontwikkelen van frontend en backend features
- Integratie van systemen en API's
- Performance optimalisatie
- Samenwerken met Frontend, Backend, DevOps, Architect en Scrummaster

## Belangrijke resources
- [Best practices](../../resources/templates/fullstackdeveloper/best-practices.md)
- [Performance voorbeelden](../../resources/data/fullstackdeveloper/performance-examples.md)
- [Agent changelog](changelog.md)

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld als een feature is gedeployed.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.
