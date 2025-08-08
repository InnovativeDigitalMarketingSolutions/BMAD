# Message Bus Event Standards

## Doel
Consistente, traceerbare en testbare event-communicatie tussen agents via de AgentMessageBusIntegration-wrapper.

## Contract
- Gebruik: `await self.publish_agent_event(event_type, data, correlation_id=None)`
- Verboden: directe `publish(...)` in agents
- Payload minimaal:
  - `status`: "requested" | "completed" | "failed"
  - Domeinspecifieke sleutel: bijv. `api_design`, `system_design`, `architecture_review`, `tech_stack_evaluation`, `pipeline_advice`, `performance_metrics`
  - `request_id` (optioneel, aanbevolen)
  - `agent`, `timestamp` mogen door wrapper worden toegevoegd

## Naming
- EventTypes gebruiken snake_case strings, gegroepeerd per domein (API_DESIGN_COMPLETED, SPRINT_STARTED, ...)
- Failed events: `*_FAILED`

## Voorbeelden
```python
await self.publish_agent_event(EventTypes.API_DESIGN_COMPLETED, {
    "request_id": req_id,
    "status": "completed",
    "api_design": {"endpoints": [...]} 
})

await self.publish_agent_event(EventTypes.API_DESIGN_FAILED, {
    "request_id": req_id,
    "status": "failed",
    "error": str(exc)
})
```

## Testing
- Mock `publish_agent_event` met `AsyncMock`
- Verifieer event type en payload-contract
- Gebruik `pytest.mark.asyncio` voor async tests

## Compliance
- Audit controleert op: geen directe `publish(` in `bmad/agents/Agent/**`, aanwezigheid wrapper, payloads met `status` + domeinsleutel + optioneel `request_id`. 