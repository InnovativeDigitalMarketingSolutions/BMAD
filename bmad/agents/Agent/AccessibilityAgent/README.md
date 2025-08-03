# AccessibilityAgent

## Overview
The AccessibilityAgent is responsible for ensuring digital accessibility compliance and providing accessibility testing and recommendations. It works closely with UX/UI designers, frontend developers, and quality assurance teams to maintain high accessibility standards.

## Enhanced MCP Integration (Phase 2)

### Features
- **Enhanced MCP Tools**: Advanced accessibility validation and testing capabilities
- **Tracing Integration**: Comprehensive operation tracing for accessibility audits
- **Team Collaboration**: Enhanced communication with other agents for accessibility reviews
- **Performance Monitoring**: Real-time accessibility performance metrics

### Enhanced MCP Commands
- `enhanced-collaborate`: Enhanced inter-agent communication for accessibility reviews
- `enhanced-security`: Enhanced security validation for accessibility features
- `enhanced-performance`: Enhanced performance optimization for accessibility tools
- `trace-operation`: Trace accessibility operations
- `trace-performance`: Get performance metrics
- `trace-error`: Trace error scenarios
- `tracing-summary`: Get tracing summary

### Core Functionality
- **Accessibility Audits**: Comprehensive WCAG 2.1/2.2 compliance testing
- **ARIA Validation**: Advanced ARIA attribute validation and recommendations
- **Screen Reader Testing**: Automated screen reader compatibility testing
- **Design Token Validation**: Accessibility-focused design token analysis
- **Component Testing**: Shadcn/UI component accessibility validation

### Integration Points
- **UXUIDesigner**: Design accessibility reviews
- **FrontendDeveloper**: Component accessibility implementation
- **QualityGuardian**: Quality assurance for accessibility standards
- **ProductOwner**: Accessibility requirement validation

## Usage

### Basic Commands
```bash
# Run accessibility audit
python -m bmad.agents.Agent.AccessibilityAgent.accessibilityagent audit --target /page

# Test Shadcn component
python -m bmad.agents.Agent.AccessibilityAgent.accessibilityagent test-shadcn-component --component Button

# Validate ARIA attributes
python -m bmad.agents.Agent.AccessibilityAgent.accessibilityagent validate-aria --code "<button aria-label='Submit'>Submit</button>"

# Enhanced MCP commands
python -m bmad.agents.Agent.AccessibilityAgent.accessibilityagent enhanced-collaborate
python -m bmad.agents.Agent.AccessibilityAgent.accessibilityagent trace-operation
```

### Enhanced MCP Integration
The agent now supports enhanced MCP Phase 2 capabilities including:
- Advanced accessibility validation tools
- Real-time performance monitoring
- Comprehensive operation tracing
- Enhanced team collaboration features

## Dependencies
- WCAG 2.1/2.2 standards
- ARIA 1.2 specification
- Section 508 compliance
- Screen reader compatibility (NVDA, JAWS, VoiceOver)

## Resources
- Templates: Accessibility audit templates, checklists, best practices
- Data: Audit history, improvement reports, changelog
- Integration: MCP framework, tracing system, team collaboration tools 