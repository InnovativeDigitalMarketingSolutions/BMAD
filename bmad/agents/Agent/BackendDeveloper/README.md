# BackendDeveloper Agent

## Overview
The BackendDeveloper agent is responsible for backend development, API design, and server-side implementation. It works closely with frontend developers, architects, and DevOps teams to build robust, scalable, and secure backend services.

## Enhanced MCP Integration (Phase 2)

### Features
- **Enhanced MCP Tools**: Advanced backend development and API design capabilities
- **Tracing Integration**: Comprehensive operation tracing for backend operations
- **Team Collaboration**: Enhanced communication with other agents for backend coordination
- **Performance Monitoring**: Real-time backend performance metrics

### Enhanced MCP Commands
- `enhanced-collaborate`: Enhanced inter-agent communication for backend coordination
- `enhanced-security`: Enhanced security validation for backend features
- `enhanced-performance`: Enhanced performance optimization for backend tools
- `trace-operation`: Trace backend operations
- `trace-performance`: Get performance metrics
- `trace-error`: Trace error scenarios
- `tracing-summary`: Get tracing summary

### Core Functionality
- **API Development**: RESTful API design and implementation
- **Database Design**: Database schema design and optimization
- **Authentication**: User authentication and authorization systems
- **Performance Optimization**: Backend performance tuning and optimization
- **Security Implementation**: Security best practices and vulnerability prevention
- **Integration Testing**: Backend integration testing and validation

### Integration Points
- **FrontendDeveloper**: API contract coordination and frontend integration
- **Architect**: Backend architecture design and implementation
- **DevOpsInfra**: Backend deployment and infrastructure coordination
- **SecurityDeveloper**: Backend security validation and compliance

## Usage

### Basic Commands
```bash
# Create API endpoint
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper create-api --endpoint users

# Design database schema
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper design-database --model User

# Performance optimization
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper optimize-performance --service user-service

# Enhanced MCP commands
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper enhanced-collaborate
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper trace-operation
```

### Enhanced MCP Integration
The agent now supports enhanced MCP Phase 2 capabilities including:
- Advanced backend development tools
- Real-time performance monitoring
- Comprehensive operation tracing
- Enhanced team collaboration features

## Dependencies
- Backend frameworks (Django, Flask, FastAPI, Express.js)
- Database systems (PostgreSQL, MongoDB, Redis)
- Authentication systems (JWT, OAuth, OpenID Connect)
- API documentation tools (Swagger, OpenAPI)

## Resources
- Templates: API templates, database schemas, authentication patterns
- Data: API documentation, database migrations, performance benchmarks
- Integration: MCP framework, tracing system, team collaboration tools 