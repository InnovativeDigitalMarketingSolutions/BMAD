# AiDeveloper Changelog

Hier houdt de AiDeveloper agent zijn eigen wijzigingen, beslissingen en learnings bij.

## [YYYY-MM-DD] Wijziging/Feature
- ... 

## [2025-08-08] Wrapper-harmonisatie en Event Contract

### Changed
- Directe `publish(...)` vervangen door `await self.publish_agent_event(...)` in `collaborate_example`, `handle_model_training_requested`, `handle_evaluation_requested`
- EventTypes gebruikt: `AI_EXPERIMENT_STARTED`, `AI_EXPERIMENT_COMPLETED`, `AI_MODEL_TRAINING_COMPLETED`

### Rationale
- Uniform event‑contract en betere traceerbaarheid; centrale validatie via core message bus

### Impact
- Unit tests: groen (138/138)
- Documentatie: te updaten met Message Bus & Event Contract sectie 