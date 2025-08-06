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
- `design_processing_started` - Design processing started
- `design_completion_reported` - Design completion reported
- `figma_analysis_completed` - Figma analysis completed
- `design_feedback_processed` - Design feedback processed

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
