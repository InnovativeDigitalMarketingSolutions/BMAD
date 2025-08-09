# Scrummaster Agent

De Scrummaster agent faciliteert het scrumproces, bewaakt voortgang en ondersteunt het team.

> Status: ✅ COMPLETENESS 1.0 — wrapper-compliant, enhanced MCP tools geregistreerd, tracing actief, subscriptions aanwezig

## Verantwoordelijkheden
- Organiseren van sprintplanning en retrospectives
- Bewaken van voortgang en teamcohesie
- Ondersteunen van developers, Product Owner en andere agents

## Wrapper & Subscriptions
- Publicatie via `await self.publish_agent_event(event_type, data)` (minimaal `status` en domeinspecifieke sleutel; optioneel `request_id`)
- Abonneren via `await self.subscribe_to_event(event_type, callback)` (passthrough naar Message Bus; core/legacy fallback)

## Enhanced MCP tools
- Beschikbaar wanneer Enhanced MCP geactiveerd is:
  - `scrum.sprint_planning`
  - `scrum.daily_standup_summary`
  - `scrum.impediment_analysis`
  - `scrum.velocity_analysis`
  - `scrum.team_health_check`

## Tracing
- Tracing wordt tijdens init geactiveerd; `initialize_tracing()` initialiseert waar nodig
- Generieke tracing haak: `await self.trace_operation(name, data)`

## Belangrijke resources
- [Changelog](changelog.md)