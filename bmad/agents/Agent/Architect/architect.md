# Architect Agent

> **Let op:** Deze agent werkt actief samen met andere agents via een centrale message bus en gedeelde context in Supabase. Zie de sectie 'Samenwerking & Contextdeling' hieronder voor details.

# Samenwerking met andere agents

De Architect werkt nauw samen met:
- **Fullstack, Backend, Frontend Developers:** Voor technische implementatie, refactoring en API design.
- **DevOps/Infra:** Voor CI/CD, infra-as-code, monitoring en deployment.
- **Product Owner:** Voor afstemming van requirements, prioriteiten en roadmap.
- **Scrummaster:** Voor sprintplanning, refinement en voortgangsbewaking.
- **AI/MLOps:** Voor integratie van AI-componenten, context/memory architectuur en MLOps best practices.
- **Security Developer:** Voor security-by-design, compliance en risicoanalyses.
- **Test Engineer:** Voor teststrategie, coverage en kwaliteitsbewaking.

De output van de Architect is direct bruikbaar voor developers, testers en business stakeholders.

## Samenwerking & Contextdeling

Deze agent werkt samen met andere agents via een centrale message bus en gedeelde context in Supabase.

- **Events publiceren:** De agent kan events publiceren via de message_bus, bijvoorbeeld na een architectuur review.
- **Context delen:** Status en relevante data worden gedeeld via Supabase, zodat andere agents deze kunnen inzien.

**Voorbeeld:**
```python
self.collaborate_example()
```
Dit publiceert een event en slaat context op. Andere agents kunnen deze context ophalen of op het event reageren.
