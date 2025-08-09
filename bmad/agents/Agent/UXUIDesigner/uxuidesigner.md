# UXUIDesigner Agent

## Overview
De UXUIDesigner Agent is gespecialiseerd in UX/UI design, component development en design system management. Deze agent creëert gebruiksvriendelijke interfaces, ontwikkelt Shadcn/ui componenten en voert Figma analyses uit.

**✅ Status: FULLY COMPLIANT** - 79/79 tests passing (100% coverage)

## Core Features
- **Component Development**: Shadcn/ui componenten en design system management
- **Mobile UX Design**: iOS, Android, React Native en Flutter designs
- **Figma Integration**: Design analysis en accessibility checks
- **Design Feedback**: Feedback processing en design improvements
- **User Flow Design**: Mobile user flow creation en optimization
- **Message Bus Integration**: Event-driven design coordination

## Quality-First Implementation

### Test Coverage
- **79/79 tests passing** (100% coverage)
- **4 event handlers** met echte functionaliteit
- **6 Message Bus CLI commands** geïmplementeerd
- **12 performance metrics** voor design tracking

### Event Handlers
1. **`handle_design_requested`** - Design creation tracking en performance metrics
2. **`handle_design_completed`** - Design completion tracking en history management
3. **`handle_figma_analysis_requested`** - Figma analysis met accessibility checks en insights
4. **`handle_design_feedback_requested`** - Feedback processing en history tracking

### Message Bus CLI Extension
- **`message-bus-status`** - Status van Message Bus integratie
- **`publish-event`** - Event publishing met JSON data support
- **`subscribe-event`** - Event subscription en listening
- **`list-events`** - Overzicht van ondersteunde events
- **`event-history`** - Event history en design/feedback history
- **`performance-metrics`** - Performance metrics display

### Performance Metrics
- Total designs created, components built, Figma analyses
- Total design feedback, mobile designs, Shadcn components
- Total accessibility checks, user flows
- Average design time, design success rate
- Feedback processing time, component build success rate

## Resource Management
- **Template Paths**: 8 template paths voor design strategie en templates
- **Data Paths**: 3 data paths voor history en changelog
- **Resource Validation**: Complete resource completeness testing

## Enhanced MCP Integration
- **Phase 2 Capabilities**: Advanced tracing en collaboration
- **UX/UI-Specific Tools**: MCP tools voor design analysis en component development
- **Performance Optimization**: Enhanced performance monitoring
- **Design Validation**: Enterprise design compliance

## CLI Commands
```bash
# Core Commands
python uxuidesigner.py build-shadcn-component --component-name Button
python uxuidesigner.py create-mobile-ux --platform iOS --app-type native
python uxuidesigner.py design-feedback --feedback-text "Improve accessibility"
python uxuidesigner.py analyze-figma --figma-file-id abc123

# Message Bus Commands
python uxuidesigner.py message-bus-status
python uxuidesigner.py publish-event --event-type design_requested --event-data '{"design_type": "component"}'
python uxuidesigner.py event-history
python uxuidesigner.py performance-metrics

# Enhanced MCP Commands
python uxuidesigner.py enhanced-collaborate
python uxuidesigner.py enhanced-security
python uxuidesigner.py enhanced-performance
```

## Event System
### Input Events
- `design_requested` - Request design creation
- `design_completed` - Notify design completion
- `figma_analysis_requested` - Request Figma analysis
- `design_feedback_requested` - Request design feedback

### Output Events
- `component_build_requested` (`EventTypes.COMPONENT_BUILD_REQUESTED`) - via wrapper
- `component_build_completed` (`EventTypes.COMPONENT_BUILD_COMPLETED`) - via wrapper
- `accessibility_audit_completed` (`EventTypes.ACCESSIBILITY_AUDIT_COMPLETED`) - via wrapper
- `design_feedback_processed` - legacy naam waar relevant

### Event Contract & Wrapper
- Publicatie via `publish_agent_event(event_type, data, request_id=None)`
- Minimale payload: `status`, domeinspecifieke sleutel (bijv. `component`, `figma_file_id`), optioneel `request_id`
- Geen directe `publish(...)` in agent code; CLI/demo kan kern `publish_event` gebruiken

## Enhanced MCP Tools & Subscriptions
- Enhanced MCP Tools: `uxui.design_analysis`, `uxui.accessibility_check`, `uxui.component_spec_generation`, `uxui.figma_analysis`, `uxui.design_feedback`
- Tool-registratie: `register_enhanced_mcp_tools()` registreert bovenstaande tools wanneer Enhanced MCP geactiveerd is
- Subscriptions: `subscribe_to_event(event_type, callback)` biedt een passthrough naar de message bus (integratie/core/legacy fallback)

## Tracing
- `initialize_tracing()` activeert tracing en UX/UI-specifieke spans
- `trace_operation(name, data)` voegt tracepunten toe per UX/UI operatie

## LLM Configuratie
- YAML (`uxuidesigner.yaml`):
  - `llm.provider: openai`
  - `llm.model: gpt-5-reasoning`
  - `llm.temperature: 0.6`
- ENV override: `BMAD_LLM_UXUIDESIGNER_MODEL` (heeft voorrang op YAML)
- Resolver: per-agent modelresolutie via `bmad.agents.core.ai.llm_client.resolve_agent_model`

## Collaboration
Deze agent werkt samen met andere agents via Message Bus en gedeelde context:
- **FrontendDeveloper**: Component development coordination
- **AccessibilityAgent**: Accessibility compliance coordination
- **ProductOwner**: Design requirements coordination
- **QualityGuardian**: Design quality metrics sharing
- **TestEngineer**: Design testing coordination

## Resources
- [Design best practices](../../resources/templates/uxuidesigner/best-practices.md)
- [Shadcn design tokens](../../resources/templates/uxuidesigner/shadcn-design-tokens.md)
- [Accessibility checklist](../../resources/templates/uxuidesigner/accessibility-checklist.md)
