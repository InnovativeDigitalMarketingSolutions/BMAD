# DocumentationAgent

## Overview
The DocumentationAgent is responsible for documentation generation, API documentation, user guides, and technical documentation. It works closely with development teams to ensure comprehensive and up-to-date documentation for all system components.

## Enhanced MCP Integration (Phase 2)

### Features
- **Enhanced MCP Tools**: Advanced documentation generation and management capabilities
- **Tracing Integration**: Comprehensive operation tracing for documentation operations
- **Team Collaboration**: Enhanced communication with other agents for documentation reviews
- **Performance Monitoring**: Real-time documentation performance metrics

### Enhanced MCP Commands
- `enhanced-collaborate`: Enhanced inter-agent communication for documentation reviews
- `enhanced-security`: Enhanced security validation for documentation features
- `enhanced-performance`: Enhanced performance optimization for documentation tools
- `trace-operation`: Trace documentation operations
- `trace-performance`: Get performance metrics
- `trace-error`: Trace error scenarios
- `tracing-summary`: Get tracing summary

### Core Functionality
- **API Documentation**: Comprehensive API documentation generation and maintenance
- **User Guides**: User-friendly guides and tutorials for system usage
- **Technical Documentation**: Detailed technical documentation and architecture guides
- **Figma Documentation**: UI/UX documentation from Figma designs
- **Changelog Management**: Automated changelog summarization and organization
- **Documentation Export**: Multiple format export capabilities (Markdown, CSV, JSON)

### Integration Points
- **UXUIDesigner**: UI/UX documentation and design system documentation
- **FrontendDeveloper**: Frontend component documentation and API integration
- **BackendDeveloper**: API documentation and technical implementation details
- **ProductOwner**: Product documentation and user guide coordination

## Usage

### Basic Commands
```bash
# Create API documentation
python -m bmad.agents.Agent.DocumentationAgent.documentationagent create-api-docs --api-name "BMAD API"

# Create user guide
python -m bmad.agents.Agent.DocumentationAgent.documentationagent create-user-guide --product-name "BMAD System"

# Document Figma UI
python -m bmad.agents.Agent.DocumentationAgent.documentationagent document-figma --figma-file-id "your_figma_file_id"

# Enhanced MCP commands
python -m bmad.agents.Agent.DocumentationAgent.documentationagent enhanced-collaborate
python -m bmad.agents.Agent.DocumentationAgent.documentationagent trace-operation
```

### Enhanced MCP Integration
The agent now supports enhanced MCP Phase 2 capabilities including:
- Advanced documentation generation tools
- Real-time documentation metrics monitoring
- Comprehensive operation tracing
- Enhanced team collaboration features

## Dependencies
- Documentation frameworks (Markdown, reStructuredText, AsciiDoc)
- API documentation tools (Swagger, OpenAPI, Postman)
- Design tools (Figma API, Sketch, Adobe XD)
- Content management systems (GitBook, Notion, Confluence)

## Resources
- Templates: Documentation templates, API doc templates, user guide templates
- Data: Documentation history, changelog data, Figma documentation history
- Integration: MCP framework, tracing system, team collaboration tools 