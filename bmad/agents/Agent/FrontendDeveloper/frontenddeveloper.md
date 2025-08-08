# FrontendDeveloper Agent

## Status
- ✅ Unit tests groen (63/63)

## Message Bus & Event Contract
- Publiceren via wrapper: `await self.publish_agent_event(event_type, data)`; in sync paden is een kleine `asyncio.run(...)`-brug toegestaan
- Minimale payload: `status` (bij *_COMPLETED) + domeinspecifieke sleutel; `request_id` optioneel
- Gebruikte EventTypes: `COMPONENT_BUILD_REQUESTED`, `COMPONENT_BUILD_COMPLETED`, `ACCESSIBILITY_AUDIT_COMPLETED`

## Overview
De FrontendDeveloper Agent is gespecialiseerd in React/Next.js, Shadcn/ui, en moderne frontend development. Deze agent biedt uitgebreide mogelijkheden voor component development, accessibility testing, en design system integratie.

## Core Features
- **Component Development**: Bouw en update React/Next.js componenten
- **Shadcn/ui Integration**: Specialized Shadcn/ui component development
- **Accessibility Testing**: Uitgebreide accessibility checks en WCAG compliance
- **Design System Integration**: Integratie met design systems en component libraries
- **Performance Optimization**: Frontend performance monitoring en optimalisatie
- **Figma Integration**: Parse en genereer componenten vanuit Figma designs

## MCP Integration
De agent maakt gebruik van Model Context Protocol (MCP) voor enhanced capabilities:
- **Standard MCP**: Basis MCP tool integration
- **Frontend-specific MCP Tools**: Gespecialiseerde tools voor frontend development
- **Enhanced MCP Phase 2**: Advanced capabilities voor inter-agent communication en external tool integration
- **Tracing Integration**: Uitgebreide tracing capabilities voor performance monitoring en debugging

## MCP Phase 2: Enhanced Capabilities
De FrontendDeveloper agent beschikt over geavanceerde MCP Phase 2 capabilities:

### Enhanced MCP Tool Integration
- **Core Enhancement**: Advanced agent capabilities en performance metrics
- **Frontend-specific Enhancement**: Gespecialiseerde tools voor component development, accessibility testing, design system integration, en performance optimization

### Inter-Agent Communication
- **Enhanced Collaboration**: Geavanceerde communicatie met andere agents (BackendDeveloper, UXUIDesigner, etc.)
- **Real-time Coordination**: Synchronisatie van component development en API design

### External Tool Integration
- **Design Tools**: Figma, Sketch, Adobe XD integratie
- **Build Tools**: Webpack, Vite, Rollup optimalisatie
- **Testing Tools**: Jest, Cypress, Playwright integratie

### Security Enhancement
- **Component Security**: Security validation voor frontend componenten
- **Dependency Scanning**: Automatische security scanning van dependencies
- **Access Control**: Role-based access control voor component development

### Performance Optimization
- **Bundle Optimization**: Advanced bundling en code splitting
- **Lazy Loading**: Intelligent lazy loading strategieën
- **Caching Strategy**: Adaptive caching voor optimal performance

### Tracing Capabilities
- **Component Development Tracing**: Trace component build process, performance metrics, accessibility scores
- **User Interaction Tracing**: Track user behavior patterns, interaction types, performance impact
- **Performance Metrics Tracing**: Monitor bundle size, load times, render times, API response times
- **Error Event Tracing**: Track frontend errors, exceptions, component failures
- **Real-time Analytics**: Live performance monitoring en debugging insights

## Enhanced CLI Commands
De agent biedt uitgebreide CLI commands voor enhanced MCP capabilities:

```bash
# Enhanced collaboration met andere agents
python frontenddeveloper.py enhanced-collaborate --agents BackendDeveloper UXUIDesigner --message "Component API design"

# Enhanced security validation
python frontenddeveloper.py enhanced-security

# Enhanced performance optimization
python frontenddeveloper.py enhanced-performance

# Enhanced external tool integration
python frontenddeveloper.py enhanced-tools --tool-config '{"tool": "figma", "action": "parse"}'

# Enhanced performance en communication summaries
python frontenddeveloper.py enhanced-summary

# Tracing capabilities
python frontenddeveloper.py trace-component --name Button --component-data '{"phase": "build", "framework": "react"}'
python frontenddeveloper.py trace-interaction --interaction-data '{"type": "click", "component_name": "Button"}'
python frontenddeveloper.py trace-performance --performance-data '{"bundle_size": 150, "load_time": 200}'
python frontenddeveloper.py trace-error --error-data '{"type": "render_error", "message": "Component failed to render"}'
python frontenddeveloper.py tracing-summary
```

## Usage Examples

### Basic Component Development
```bash
# Build een Shadcn/ui component
python frontenddeveloper.py build-shadcn-component --name Button

# Run accessibility check
python frontenddeveloper.py run-accessibility-check --name Button

# Export component
python frontenddeveloper.py export-component --format md
```

### Enhanced MCP Usage
```bash
# Initialize enhanced MCP capabilities
python frontenddeveloper.py initialize-mcp

# Use enhanced MCP tools
python frontenddeveloper.py enhanced-collaborate --agents BackendDeveloper --message "API design for Button component"

# Get enhanced performance summary
python frontenddeveloper.py enhanced-summary
```

## Integration Points
- **BackendDeveloper**: API design en data flow coordination
- **UXUIDesigner**: Design system en component specification
- **AccessibilityAgent**: Accessibility compliance en testing
- **QualityGuardian**: Quality assurance en testing coordination

## Performance Metrics
- **Component Build Time**: < 2 seconds voor standaard componenten
- **Accessibility Score**: > 95% voor alle componenten
- **Performance Score**: > 90% voor bundle size en loading time
- **Test Coverage**: > 80% voor alle componenten

## Dependencies
- React/Next.js ecosystem
- Shadcn/ui component library
- Tailwind CSS
- TypeScript
- Testing frameworks (Jest, Cypress)
- Design tools (Figma API)

**Wrapper & Subscriptions**
- Events publiceren via `publish_agent_event(event_type, data)` met minimaal `status` en `agent`
- Abonneren via `subscribe_to_event(event_type, callback)` (passthrough naar Message Bus); in `run()` ook `subscribe(...)` registraties voor compatibiliteit
- Enhanced MCP tools: `get_enhanced_mcp_tools()` en `register_enhanced_mcp_tools()` beschikbaar
- Tracing: `initialize_tracing()` instantiëert en initialiseerde tracer correct; `trace_operation()` beschikbaar voor generieke traces
