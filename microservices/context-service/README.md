# Context Service

**Service**: Context Service  
**Responsibility**: Enhanced context management and persistence  
**Status**: 🚧 In Development  
**Version**: 1.0.0  

## 🎯 Overview

The Context Service is responsible for managing enhanced context data across the BMAD system, including context layering, persistence, analytics, and sharing between services. This service provides a centralized context management system with versioning, analytics, and optimization capabilities.

## 🏗 Architecture

```
context-service/
├── src/
│   ├── context/           # Context management
│   ├── layers/            # Context layering
│   ├── analytics/         # Context analytics
│   └── api/               # Context API endpoints
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
- PostgreSQL (for context persistence)
- Redis (for caching)

### Local Development
```bash
# Clone and setup
cd microservices/context-service
pip install -r requirements.txt

# Run the service
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8003

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

### Context Management
- `GET /contexts` - List all contexts
- `POST /contexts` - Create new context
- `GET /contexts/{context_id}` - Get context details
- `PUT /contexts/{context_id}` - Update context
- `DELETE /contexts/{context_id}` - Delete context

### Context Layers
- `GET /contexts/{context_id}/layers` - List context layers
- `POST /contexts/{context_id}/layers` - Add context layer
- `GET /contexts/{context_id}/layers/{layer_id}` - Get layer details
- `PUT /contexts/{context_id}/layers/{layer_id}` - Update layer
- `DELETE /contexts/{context_id}/layers/{layer_id}` - Remove layer

### Context Analytics
- `GET /contexts/{context_id}/analytics` - Get context analytics
- `GET /contexts/analytics/summary` - Get system-wide analytics
- `GET /contexts/analytics/trends` - Get usage trends

### Context Sharing
- `POST /contexts/{context_id}/share` - Share context with service
- `GET /contexts/shared/{service_id}` - Get shared contexts for service
- `DELETE /contexts/{context_id}/share/{service_id}` - Remove sharing

## 🔧 Configuration

### Environment Variables
```bash
# Service Configuration
CONTEXT_SERVICE_HOST=0.0.0.0
CONTEXT_SERVICE_PORT=8003
CONTEXT_SERVICE_DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/context_service

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Service Discovery
CONSUL_HOST=localhost
CONSUL_PORT=8500

# Context Configuration
CONTEXT_CLEANUP_INTERVAL=3600
CONTEXT_RETENTION_DAYS=30
CONTEXT_MAX_SIZE_MB=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration Files
- `config/context_service.yaml` - Service configuration
- `config/context_types.yaml` - Context type definitions
- `config/analytics.yaml` - Analytics configuration

## 🧪 Testing

### Test Structure
```
tests/
├── unit/              # Unit tests
│   ├── test_context/
│   ├── test_layers/
│   ├── test_analytics/
│   └── test_api/
├── integration/       # Integration tests
│   ├── test_database/
│   └── test_api/
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
- Context creation/deletion rates
- Layer usage statistics
- Analytics performance
- Storage utilization
- Response times
- Error rates

### Logging
- Structured JSON logging
- Correlation IDs
- Request tracing
- Error tracking

## 🔄 Service Communication

### Event Publishing
The Context Service publishes events to Redis Pub/Sub:
- `context.created`
- `context.updated`
- `context.deleted`
- `layer.added`
- `analytics.updated`

### Event Consumption
The Context Service consumes events:
- `agent.executed`
- `workflow.started`
- `integration.registered`

## 🛡 Security

### Authentication
- JWT token validation
- API key authentication
- Role-based access control

### Authorization
- Context access permissions
- Layer modification rights
- Analytics access control
- Audit logging

## 📈 Performance

### Optimization Strategies
- Context caching
- Layer compression
- Analytics aggregation
- Background cleanup
- Connection pooling

### Scaling
- Horizontal scaling
- Auto-scaling rules
- Resource limits
- Performance monitoring

## 🚨 Troubleshooting

### Common Issues
1. **Context Creation Fails**
   - Check database connectivity
   - Verify storage limits
   - Check permissions

2. **Layer Operations Timeout**
   - Check context size
   - Verify layer complexity
   - Monitor performance

3. **Analytics Issues**
   - Check data aggregation
   - Verify storage space
   - Monitor query performance

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export CONTEXT_SERVICE_DEBUG=true

# Run with debug flags
uvicorn src.api.main:app --reload --log-level debug
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Context Development Guide](docs/context-development.md)
- [Analytics Guide](docs/analytics.md)
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