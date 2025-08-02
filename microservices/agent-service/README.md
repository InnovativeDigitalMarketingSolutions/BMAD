# Agent Service

**Service**: Agent Service  
**Responsibility**: Agent lifecycle management, execution, and coordination  
**Status**: 🚧 In Development  
**Version**: 1.0.0  

## 🎯 Overview

The Agent Service is responsible for managing the lifecycle of all BMAD agents, including registration, discovery, execution, and coordination. This service provides the core agent framework functionality in a microservices architecture.

## 🏗 Architecture

```
agent-service/
├── src/
│   ├── agents/            # Individual agent implementations
│   ├── core/              # Agent framework
│   ├── orchestrator/      # Agent orchestration
│   └── api/               # Agent API endpoints
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Redis (for message queue)
- PostgreSQL (for agent state)

### Local Development
```bash
# Clone and setup
cd microservices/agent-service
pip install -r requirements.txt

# Run the service
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001

# Run tests
pytest tests/
```

### Docker Deployment
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## 📋 API Endpoints

### Agent Management
- `GET /agents` - List all agents
- `POST /agents` - Register new agent
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Deregister agent

### Agent Execution
- `POST /agents/{agent_id}/execute` - Execute agent
- `GET /agents/{agent_id}/status` - Get execution status
- `POST /agents/{agent_id}/stop` - Stop execution

### Agent Discovery
- `GET /agents/discover` - Discover available agents
- `GET /agents/types` - List agent types
- `GET /agents/health` - Health check

## 🔧 Configuration

### Environment Variables
```bash
# Service Configuration
AGENT_SERVICE_HOST=0.0.0.0
AGENT_SERVICE_PORT=8001
AGENT_SERVICE_DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/agent_service

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Service Discovery
CONSUL_HOST=localhost
CONSUL_PORT=8500

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration Files
- `config/agent_service.yaml` - Service configuration
- `config/agents.yaml` - Agent definitions
- `config/orchestration.yaml` - Orchestration rules

## 🧪 Testing

### Test Structure
```
tests/
├── unit/              # Unit tests
│   ├── test_agents/
│   ├── test_core/
│   └── test_orchestrator/
├── integration/       # Integration tests
│   ├── test_api/
│   └── test_database/
└── e2e/              # End-to-end tests
    └── test_workflows/
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📊 Monitoring

### Health Checks
- `GET /health` - Service health
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Metrics
- Agent execution metrics
- Performance metrics
- Error rates
- Response times

### Logging
- Structured JSON logging
- Correlation IDs
- Request tracing
- Error tracking

## 🔄 Service Communication

### Event Publishing
The Agent Service publishes events to Redis Pub/Sub:
- `agent.registered`
- `agent.executed`
- `agent.failed`
- `agent.completed`

### Event Consumption
The Agent Service consumes events:
- `workflow.started`
- `context.updated`
- `notification.sent`

## 🛡 Security

### Authentication
- JWT token validation
- API key authentication
- Role-based access control

### Authorization
- Agent execution permissions
- Resource access control
- Audit logging

## 📈 Performance

### Optimization Strategies
- Agent caching
- Connection pooling
- Async execution
- Load balancing

### Scaling
- Horizontal scaling
- Auto-scaling rules
- Resource limits
- Performance monitoring

## 🚨 Troubleshooting

### Common Issues
1. **Agent Registration Fails**
   - Check database connectivity
   - Verify agent configuration
   - Check service discovery

2. **Agent Execution Timeout**
   - Check agent implementation
   - Verify resource limits
   - Check external dependencies

3. **Service Communication Issues**
   - Check Redis connectivity
   - Verify event format
   - Check service discovery

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export AGENT_SERVICE_DEBUG=true

# Run with debug flags
uvicorn src.api.main:app --reload --log-level debug
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Agent Development Guide](docs/agent-development.md)
- [Orchestration Guide](docs/orchestration.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

1. Follow the coding standards
2. Write comprehensive tests
3. Update documentation
4. Submit pull requests

## 📄 License

This service is part of the BMAD system and follows the same license terms.

---

**Last Updated**: 1 augustus 2025  
**Next Review**: Weekly during development 