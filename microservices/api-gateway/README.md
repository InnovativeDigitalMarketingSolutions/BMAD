# API Gateway Service

## Overview

The API Gateway is a centralized service that provides unified access to all BMAD microservices. It handles request routing, load balancing, authentication, rate limiting, and API versioning.

## Features

### Core Functionality
- **Request Routing**: Route requests to appropriate microservices
- **Load Balancing**: Distribute traffic across service instances
- **Authentication**: JWT token validation and user authentication
- **Rate Limiting**: Prevent API abuse with configurable limits
- **API Versioning**: Support multiple API versions simultaneously
- **Request/Response Transformation**: Modify requests and responses as needed
- **Caching**: Cache frequently requested data
- **Monitoring**: Request metrics and health monitoring

### Security Features
- **JWT Validation**: Verify authentication tokens
- **CORS Support**: Cross-origin resource sharing
- **Request Validation**: Input sanitization and validation
- **Security Headers**: Add security headers to responses
- **IP Whitelisting**: Restrict access by IP address

### Performance Features
- **Connection Pooling**: Efficient connection management
- **Circuit Breaker**: Prevent cascading failures
- **Retry Logic**: Automatic retry for failed requests
- **Timeout Management**: Configurable request timeouts
- **Compression**: Response compression for bandwidth optimization

## Architecture

```
API Gateway Architecture:
├── FastAPI Application (20+ endpoints)
├── Router Manager (request routing logic)
├── Authentication Manager (JWT validation)
├── Rate Limiter (request throttling)
├── Load Balancer (traffic distribution)
├── Circuit Breaker (fault tolerance)
├── Cache Manager (response caching)
├── Monitoring (metrics & health)
└── Configuration Manager (dynamic config)
```

## API Endpoints

### Health & Monitoring
```
GET /health - Basic health check
GET /health/ready - Readiness probe
GET /health/live - Liveness probe
GET /metrics - Prometheus metrics
```

### Authentication
```
POST /auth/login - User authentication
POST /auth/refresh - Token refresh
POST /auth/logout - User logout
GET /auth/validate - Token validation
```

### Service Routing
```
GET /api/v1/agents - Route to Agent Service
POST /api/v1/agents - Route to Agent Service
GET /api/v1/integrations - Route to Integration Service
GET /api/v1/contexts - Route to Context Service
GET /api/v1/workflows - Route to Workflow Service
```

### Configuration
```
GET /config - Get gateway configuration
PUT /config - Update gateway configuration
GET /config/routes - Get routing rules
PUT /config/routes - Update routing rules
```

## Installation

### Prerequisites
- Python 3.9+
- Docker
- Docker Compose

### Local Development
```bash
# Clone the repository
cd microservices/api-gateway

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the service
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
# Build the image
docker build -t bmad-api-gateway .

# Run with Docker Compose
docker-compose up -d
```

## Configuration

### Environment Variables
```bash
# Service Configuration
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
DEBUG=false

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Service Discovery
CONSUL_HOST=localhost
CONSUL_PORT=8500

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
```

### Service Configuration
```yaml
# config/services.yaml
services:
  agent-service:
    url: http://agent-service:8001
    health_check: /health
    timeout: 30
    retries: 3
    
  integration-service:
    url: http://integration-service:8002
    health_check: /health
    timeout: 30
    retries: 3
    
  context-service:
    url: http://context-service:8003
    health_check: /health
    timeout: 30
    retries: 3
    
  workflow-service:
    url: http://workflow-service:8004
    health_check: /health
    timeout: 30
    retries: 3
```

## Testing

### Unit Tests
```bash
# Run unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/ -v
```

### Performance Tests
```bash
# Run load tests
pytest tests/performance/ -v
```

## Development

### Project Structure
```
api-gateway/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py        # Health endpoints
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── proxy.py         # Service routing
│   │   │   └── config.py        # Configuration endpoints
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py          # Authentication middleware
│   │       ├── rate_limit.py    # Rate limiting middleware
│   │       ├── cors.py          # CORS middleware
│   │       └── logging.py       # Request logging
│   ├── core/
│   │   ├── __init__.py
│   │   ├── router_manager.py    # Request routing logic
│   │   ├── auth_manager.py      # Authentication management
│   │   ├── rate_limiter.py      # Rate limiting logic
│   │   ├── load_balancer.py     # Load balancing logic
│   │   ├── circuit_breaker.py   # Circuit breaker pattern
│   │   ├── cache_manager.py     # Caching logic
│   │   └── config_manager.py    # Configuration management
│   └── utils/
│       ├── __init__.py
│       ├── http_client.py       # HTTP client utilities
│       ├── jwt_utils.py         # JWT utilities
│       └── metrics.py           # Metrics collection
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_router_manager.py
│   │   ├── test_auth_manager.py
│   │   ├── test_rate_limiter.py
│   │   ├── test_load_balancer.py
│   │   ├── test_circuit_breaker.py
│   │   ├── test_cache_manager.py
│   │   └── test_config_manager.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   └── test_service_routing.py
│   └── performance/
│       ├── __init__.py
│       └── test_load.py
├── config/
│   ├── services.yaml            # Service configuration
│   └── routes.yaml              # Routing rules
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Monitoring

### Health Checks
- **Liveness Probe**: `/health/live`
- **Readiness Probe**: `/health/ready`
- **Metrics**: `/metrics`

### Metrics
- Request count and duration
- Error rates
- Circuit breaker status
- Cache hit/miss ratios
- Rate limiting statistics

### Logging
- Request/response logging
- Error logging
- Performance metrics
- Security events

## Security

### Authentication
- JWT token validation
- Role-based access control
- Token refresh mechanism
- Secure token storage

### Rate Limiting
- Per-user rate limiting
- Per-IP rate limiting
- Burst protection
- Configurable limits

### Input Validation
- Request sanitization
- SQL injection prevention
- XSS protection
- Input size limits

## Performance

### Caching
- Response caching
- Cache invalidation
- Cache warming
- Cache statistics

### Load Balancing
- Round-robin distribution
- Health-based routing
- Weighted routing
- Failover handling

### Circuit Breaker
- Failure threshold detection
- Automatic recovery
- Fallback responses
- Monitoring and alerting

## Troubleshooting

### Common Issues
1. **Service Unavailable**: Check service health and circuit breaker status
2. **Authentication Errors**: Verify JWT tokens and configuration
3. **Rate Limiting**: Check rate limit configuration and user limits
4. **Performance Issues**: Monitor cache hit rates and response times

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
uvicorn src.api.main:app --reload --log-level debug
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 