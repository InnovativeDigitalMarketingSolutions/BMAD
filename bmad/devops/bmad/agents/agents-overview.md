| Architect            | Systeemontwerp, NFR, ADR           | design-api, nfrs, adr, checklist        | Dev, Security, PO, Scrummaster         |
| UX/UI Designer       | Wireframes, design tokens          | generate-wireframe, design-component    | Frontend, PO, Scrummaster              |
| Frontend Developer   | Componenten, accessibility         | build-component, run-accessibility-check| UX/UI, Test, PO, Scrummaster           |
| Fullstack Developer  | Frontend & backend, integratie     | build-feature, refactor, handover, monitor| Frontend, Backend, DevOps, Architect, Scrummaster |
| Backend Developer    | API's, databases, integraties      | build-api, optimize-db, monitor-api     | Fullstack, Frontend, DevOps, Architect, Scrummaster |

**Samenwerking:**
- Agents kunnen via de message bus context/events delen (bijv. feedback, blockers, release events).
- Elk agent kent zijn collega agents en kan relevante output/snippets delen of ophalen.
- Developer agents (Frontend, Backend, Fullstack) werken altijd samen met de Scrummaster voor sprintplanning, refinement en voortgangsbewaking.
- Dit overzicht is bedoeld als centrale referentie voor het hele team én voor agents zelf.