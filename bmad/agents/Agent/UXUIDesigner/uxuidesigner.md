# UXUIDesigner Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

De UXUIDesigner agent ontwerpt wireframes, componenten en design tokens voor optimale user experience.

## Verantwoordelijkheden
- Ontwerpen van wireframes en componenten
- Bewaken van toegankelijkheid en gebruikerservaring
- Samenwerken met Frontend, Fullstack, Product Owner en Accessibility agents

## Belangrijke resources
- [Design changelog](../../resources/data/uxuidesigner/design-changelog.md)
- [Agent changelog](changelog.md)

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld als een design is afgerond.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.
