# Backend Development Framework Template

## 🎯 Backend Development Overview

Dit framework template biedt een complete gids voor backend development binnen het BMAD systeem, inclusief best practices, architectuur patterns, en development workflows.

## 🏗️ Backend Architecture Patterns

### Microservices Architecture
```
Backend Services:
├── API Gateway (FastAPI)
├── Authentication Service (Auth0 + JWT)
├── Agent Service (Agent management)
├── Integration Service (External APIs)
├── Context Service (Context management)
├── Workflow Service (Workflow orchestration)
├── Notification Service (Email, SMS, Slack)
└── Database Services (PostgreSQL, Redis)
```

### Service Communication Patterns
- **Synchronous**: HTTP/REST APIs voor directe communicatie
- **Asynchronous**: Message queues (Redis Pub/Sub) voor event-driven patterns
- **Circuit Breaker**: Fallback mechanisms voor service failures
- **Retry Logic**: Exponential backoff voor transient failures

### Database Patterns
- **Database per Service**: Isolated data storage per microservice
- **Event Sourcing**: Audit trail en state reconstruction
- **CQRS**: Command Query Responsibility Segregation
- **Saga Pattern**: Distributed transaction management

## 🔧 Backend Development Best Practices

### Code Structure
```
backend_service/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── database.py      # Database configuration
│   │   ├── security.py      # Security utilities
│   │   └── config.py        # Configuration management
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   ├── base.py          # Base service class
│   │   └── specific.py      # Service-specific logic
│   ├── api/
│   │   ├── routes/          # API route handlers
│   │   └── middleware/      # Custom middleware
│   └── utils/
│       ├── logging.py       # Structured logging
│       └── helpers.py       # Utility functions
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Local development setup
└── requirements.txt        # Dependencies
```

### API Design Principles
- **RESTful Design**: Consistent resource-based URLs
- **HTTP Status Codes**: Proper status code usage
- **Request/Response Validation**: Pydantic schema validation
- **Error Handling**: Structured error responses
- **API Versioning**: URL-based versioning (/v1/, /v2/)
- **Rate Limiting**: Request throttling per client
- **CORS Configuration**: Cross-origin resource sharing

### Security Implementation
```python
# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}

# Authentication Middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # JWT token validation
    # Role-based access control
    # Rate limiting
    pass
```

### Database Best Practices
```python
# Connection Pooling
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600
}

# Transaction Management
async def create_user_with_profile(user_data: dict, profile_data: dict):
    async with db.transaction():
        user = await create_user(user_data)
        profile = await create_profile(user.id, profile_data)
        return user, profile
```

## 🧪 Backend Testing Strategy

### Unit Testing Framework
```python
# Test Structure
class TestUserService:
    @pytest.fixture
    async def db_session(self):
        # Database session fixture
        pass
    
    @pytest.fixture
    def mock_external_service(self):
        # Mock external dependencies
        pass
    
    async def test_create_user_success(self, db_session, mock_external_service):
        # Test user creation
        pass
    
    async def test_create_user_validation_error(self, db_session):
        # Test validation errors
        pass
```

### Integration Testing
```python
# Service Integration Tests
class TestUserAPI:
    async def test_user_registration_flow(self):
        # Test complete registration flow
        # 1. Create user
        # 2. Send verification email
        # 3. Verify email
        # 4. Complete profile
        pass
    
    async def test_user_authentication_flow(self):
        # Test authentication flow
        # 1. Login
        # 2. JWT token generation
        # 3. Token validation
        # 4. Refresh token
        pass
```

### Performance Testing
```python
# Load Testing with Locust
from locust import HttpUser, task, between

class BackendLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def test_user_creation(self):
        self.client.post("/api/v1/users", json={
            "email": "test@example.com",
            "password": "secure_password"
        })
    
    @task(1)
    def test_user_retrieval(self):
        self.client.get("/api/v1/users/me")
```

## 🚀 Backend Development Workflow

### Development Environment Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup database
docker-compose up -d postgres redis

# 4. Run migrations
alembic upgrade head

# 5. Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality Gates
```python
# Pre-commit hooks
pre-commit:
  - black --check .
  - flake8 .
  - mypy .
  - pytest tests/unit/ --cov=src --cov-report=html

# CI/CD Pipeline
ci:
  - install_dependencies
  - run_linting
  - run_unit_tests
  - run_integration_tests
  - run_security_scan
  - build_docker_image
  - deploy_to_staging
```

### Database Migration Strategy
```python
# Alembic Migration Example
"""Create users table

Revision ID: 001_create_users
Revises: 
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
```

## 🔍 Backend Monitoring & Observability

### Logging Strategy
```python
# Structured Logging
import structlog

logger = structlog.get_logger()

async def create_user(user_data: dict):
    logger.info(
        "Creating new user",
        email=user_data["email"],
        user_type=user_data.get("type", "standard"),
        request_id=request_id
    )
    
    try:
        user = await user_service.create(user_data)
        logger.info(
            "User created successfully",
            user_id=user.id,
            email=user.email
        )
        return user
    except ValidationError as e:
        logger.error(
            "User creation failed - validation error",
            email=user_data["email"],
            errors=e.errors()
        )
        raise
```

### Metrics Collection
```python
# Prometheus Metrics
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Business metrics
USER_REGISTRATIONS = Counter('user_registrations_total', 'Total user registrations')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')

# Database metrics
DB_CONNECTION_POOL_SIZE = Gauge('db_connection_pool_size', 'Database connection pool size')
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration')
```

### Health Checks
```python
# Health Check Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/health/ready")
async def readiness_check():
    # Check database connectivity
    # Check external service dependencies
    # Check resource availability
    return {"status": "ready", "checks": {"database": "ok", "redis": "ok"}}

@app.get("/health/live")
async def liveness_check():
    # Basic application health
    return {"status": "alive"}
```

## 🔒 Backend Security Framework

### Authentication & Authorization
```python
# JWT Token Management
class JWTService:
    def create_access_token(self, user_id: str, roles: List[str]) -> str:
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Role-Based Access Control
def require_role(required_role: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check user role
            if required_role not in current_user.roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### Data Validation & Sanitization
```python
# Input Validation
from pydantic import BaseModel, EmailStr, validator

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

# SQL Injection Prevention
async def get_user_by_email(email: str):
    # Use parameterized queries
    query = "SELECT * FROM users WHERE email = :email"
    result = await db.fetch_one(query, {"email": email})
    return result
```

## 📊 Backend Performance Optimization

### Caching Strategy
```python
# Redis Caching
class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        cache_key = f"user:{user_id}"
        cached_user = await self.redis.get(cache_key)
        
        if cached_user:
            return json.loads(cached_user)
        
        # Fetch from database
        user = await user_repository.get_by_id(user_id)
        if user:
            # Cache for 1 hour
            await self.redis.setex(cache_key, 3600, json.dumps(user.dict()))
        
        return user

# Database Query Optimization
async def get_users_with_profiles():
    # Use JOIN instead of N+1 queries
    query = """
    SELECT u.*, p.* 
    FROM users u 
    LEFT JOIN profiles p ON u.id = p.user_id
    """
    return await db.fetch_all(query)
```

### Connection Pooling
```python
# Database Connection Pool
DATABASE_URL = "postgresql://user:pass@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Redis Connection Pool
redis_pool = aioredis.from_url(
    "redis://localhost:6379",
    encoding="utf-8",
    decode_responses=True,
    max_connections=20
)
```

## 🚀 Backend Deployment Strategy

### Docker Configuration
```dockerfile
# Multi-stage Docker build
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim as runtime
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
# Backend Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend-service
  template:
    metadata:
      labels:
        app: backend-service
    spec:
      containers:
      - name: backend
        image: backend-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 📚 Backend Development Resources

### Essential Libraries
- **FastAPI**: Modern web framework for APIs
- **SQLAlchemy**: Database ORM and toolkit
- **Pydantic**: Data validation using Python type annotations
- **Alembic**: Database migration tool
- **Redis**: In-memory data structure store
- **Prometheus**: Metrics collection and monitoring
- **Structlog**: Structured logging
- **Pytest**: Testing framework
- **Locust**: Load testing tool

### Development Tools
- **Black**: Code formatter
- **Flake8**: Linter
- **MyPy**: Static type checker
- **Pre-commit**: Git hooks for code quality
- **Docker**: Containerization
- **Kubernetes**: Container orchestration

### Documentation
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Pydantic Documentation**: https://pydantic-docs.helpmanual.io/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/

---

**Template Version**: 1.0  
**Last Updated**: 27 januari 2025  
**Maintained By**: Backend Development Team 