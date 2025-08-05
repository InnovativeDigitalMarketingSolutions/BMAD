# BMAD Microservices Deployment Guide

**Datum**: 27 januari 2025  
**Status**: ✅ **COMPLETE** - All 6 microservices implemented  
**Focus**: Complete deployment procedures for BMAD microservices architecture  
**Environment**: Development, Staging, Production  

## 🎯 Executive Summary

Deze deployment guide beschrijft de complete deployment procedures voor alle BMAD microservices. Alle 6 core services zijn geïmplementeerd en getest, klaar voor deployment in development, staging en production omgevingen.

## 📊 **Microservices Overview**

### **✅ Implemented Services (6/6 Complete)**

| Service | Status | Port | Responsibility | Tests |
|---------|--------|------|----------------|-------|
| **Agent Service** | ✅ Complete | 8001 | Agent lifecycle management | 26 tests |
| **Integration Service** | ✅ Complete | 8002 | External service integration | 25+ tests |
| **Context Service** | ✅ Complete | 8003 | Context management & analytics | 40+ tests |
| **Workflow Service** | ✅ Complete | 8004 | Workflow orchestration | 30+ tests |
| **Authentication Service** | ✅ Complete | 8005 | User auth & RBAC | 28 tests |
| **Notification Service** | ✅ Complete | 8006 | Multi-channel notifications | 40+ tests |

### **🏗 Architecture Overview**
```
BMAD Microservices Architecture:
├── API Gateway (Port 8000) - Entry point & routing
├── Agent Service (Port 8001) - Agent management
├── Integration Service (Port 8002) - External integrations
├── Context Service (Port 8003) - Context management
├── Workflow Service (Port 8004) - Workflow orchestration
├── Authentication Service (Port 8005) - User authentication
├── Notification Service (Port 8006) - Notifications
├── PostgreSQL (Port 5432) - Primary database
├── Redis (Port 6379) - Caching & message queue
├── Consul (Port 8500) - Service discovery
├── Prometheus (Port 9090) - Metrics collection
└── Grafana (Port 3000) - Monitoring dashboard
```

## 🚀 **Development Environment Deployment**

### **Prerequisites**
```bash
# Required Software
- Python 3.11+
- Docker & Docker Compose
- Git
- Make (optional, for convenience)

# Required Services
- PostgreSQL 14+
- Redis 6+
- Consul 1.13+
```

### **Quick Start (All Services)**
```bash
# Clone repository
git clone https://github.com/InnovativeDigitalMarketingSolutions/BMAD.git
cd BMAD

# Setup environment
cp microservices/microservices_env_template.env .env
# Edit .env with your configuration

# Start all services
docker-compose up --build

# Or start individual services
cd microservices/agent-service && docker-compose up --build
cd microservices/integration-service && docker-compose up --build
# ... repeat for other services
```

### **Individual Service Deployment**

#### **1. Agent Service**
```bash
cd microservices/agent-service

# Local development
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001

# Docker deployment
docker-compose up --build

# Health check
curl http://localhost:8001/health
```

#### **2. Integration Service**
```bash
cd microservices/integration-service

# Local development
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8002

# Docker deployment
docker-compose up --build

# Health check
curl http://localhost:8002/health
```

#### **3. Context Service**
```bash
cd microservices/context-service

# Local development
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8003

# Docker deployment
docker-compose up --build

# Health check
curl http://localhost:8003/health
```

#### **4. Workflow Service**
```bash
cd microservices/workflow-service

# Local development
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8004

# Docker deployment
docker-compose up --build

# Health check
curl http://localhost:8004/health
```

#### **5. Authentication Service**
```bash
cd microservices/auth-service

# Local development
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8005

# Docker deployment
docker-compose up --build

# Health check
curl http://localhost:8005/health
```

#### **6. Notification Service**
```bash
cd microservices/notification-service

# Local development
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8006

# Docker deployment
docker-compose up --build

# Health check
curl http://localhost:8006/health
```

## 🏭 **Staging Environment Deployment**

### **Infrastructure Requirements**
```bash
# Staging Server Requirements
- CPU: 4 cores minimum
- RAM: 8GB minimum
- Storage: 100GB SSD
- OS: Ubuntu 20.04 LTS or later
- Network: Stable internet connection
```

### **Staging Deployment Script**
```bash
#!/bin/bash
# deploy-staging.sh

set -e

echo "🚀 Deploying BMAD to Staging Environment..."

# Environment setup
export ENVIRONMENT=staging
export COMPOSE_PROJECT_NAME=bmad-staging

# Pull latest code
git pull origin main

# Build and deploy
docker-compose -f docker-compose.staging.yml up --build -d

# Health checks
echo "🔍 Running health checks..."
./scripts/health-check.sh

# Database migrations
echo "🗄️ Running database migrations..."
./scripts/migrate.sh

echo "✅ Staging deployment complete!"
```

### **Staging Configuration**
```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  agent-service:
    build: ./microservices/agent-service
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://user:pass@postgres:5432/bmad_staging
      - REDIS_URL=redis://redis:6379
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis

  integration-service:
    build: ./microservices/integration-service
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://user:pass@postgres:5432/bmad_staging
    ports:
      - "8002:8002"
    depends_on:
      - postgres

  # ... other services

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=bmad_staging
      - POSTGRES_USER=bmad_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  consul:
    image: consul:1.13
    ports:
      - "8500:8500"
    command: agent -server -bootstrap-expect=1 -ui -client=0.0.0.0

volumes:
  postgres_data:
```

## 🌐 **Production Environment Deployment**

### **Infrastructure Requirements**
```bash
# Production Server Requirements
- CPU: 8 cores minimum (16 recommended)
- RAM: 16GB minimum (32GB recommended)
- Storage: 500GB SSD with backup
- OS: Ubuntu 20.04 LTS or later
- Network: High-speed, redundant connections
- Load Balancer: HAProxy or Nginx
- SSL Certificates: Let's Encrypt or commercial
```

### **Production Deployment Strategy**

#### **Blue-Green Deployment**
```bash
#!/bin/bash
# deploy-production.sh

set -e

echo "🚀 Starting Blue-Green Production Deployment..."

# Determine current environment
CURRENT_ENV=$(docker-compose -f docker-compose.prod.yml ps -q | wc -l)
if [ $CURRENT_ENV -eq 0 ]; then
    NEW_ENV="blue"
else
    CURRENT_ENV_NAME=$(docker-compose -f docker-compose.prod.yml ps --format "table {{.Names}}" | grep -E "(blue|green)" | head -1)
    if [[ $CURRENT_ENV_NAME == *"blue"* ]]; then
        NEW_ENV="green"
    else
        NEW_ENV="blue"
    fi
fi

echo "📦 Deploying to $NEW_ENV environment..."

# Deploy new environment
docker-compose -f docker-compose.prod.yml -p bmad-$NEW_ENV up --build -d

# Health checks
echo "🔍 Running health checks..."
./scripts/health-check-prod.sh $NEW_ENV

# Database migrations
echo "🗄️ Running database migrations..."
./scripts/migrate-prod.sh

# Switch traffic (if load balancer configured)
if [ "$NEW_ENV" = "green" ]; then
    echo "🔄 Switching traffic to green environment..."
    ./scripts/switch-traffic.sh green
else
    echo "🔄 Switching traffic to blue environment..."
    ./scripts/switch-traffic.sh blue
fi

# Cleanup old environment
if [ $CURRENT_ENV -gt 0 ]; then
    echo "🧹 Cleaning up old environment..."
    docker-compose -f docker-compose.prod.yml -p bmad-$CURRENT_ENV down
fi

echo "✅ Production deployment complete!"
```

### **Production Configuration**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - agent-service
      - integration-service
      - context-service
      - workflow-service
      - auth-service
      - notification-service

  agent-service:
    build: ./microservices/agent-service
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  integration-service:
    build: ./microservices/integration-service
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  context-service:
    build: ./microservices/context-service
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  workflow-service:
    build: ./microservices/workflow-service
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  auth-service:
    build: ./microservices/auth-service
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  notification-service:
    build: ./microservices/notification-service
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

  consul:
    image: consul:1.13
    command: agent -server -bootstrap-expect=3 -ui -client=0.0.0.0
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.2'
          memory: 256M

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

volumes:
  postgres_data:
  redis_data:
  grafana_data:
```

## 🔧 **Configuration Management**

### **Environment Variables**
```bash
# .env.production
# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/bmad_production
POSTGRES_DB=bmad_production
POSTGRES_USER=bmad_user
POSTGRES_PASSWORD=secure_production_password

# Redis Configuration
REDIS_URL=redis://redis:6379

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# External Service Keys
SENDGRID_API_KEY=your-sendgrid-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token

# Monitoring
GRAFANA_PASSWORD=secure-grafana-password
PROMETHEUS_RETENTION_DAYS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### **Service Discovery Configuration**
```yaml
# consul-config.json
{
  "service": {
    "name": "bmad-agent-service",
    "tags": ["api", "agent", "microservice"],
    "port": 8001,
    "check": {
      "http": "http://localhost:8001/health",
      "interval": "10s",
      "timeout": "5s"
    }
  }
}
```

## 📊 **Monitoring & Health Checks**

### **Health Check Script**
```bash
#!/bin/bash
# health-check.sh

SERVICES=(
    "http://localhost:8001/health"
    "http://localhost:8002/health"
    "http://localhost:8003/health"
    "http://localhost:8004/health"
    "http://localhost:8005/health"
    "http://localhost:8006/health"
)

echo "🔍 Running health checks..."

for service in "${SERVICES[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" $service)
    if [ $response -eq 200 ]; then
        echo "✅ $service - HEALTHY"
    else
        echo "❌ $service - UNHEALTHY (HTTP $response)"
        exit 1
    fi
done

echo "✅ All services healthy!"
```

### **Monitoring Dashboard**
```yaml
# grafana-dashboard.json
{
  "dashboard": {
    "title": "BMAD Microservices Dashboard",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"agent-service\"}",
            "legendFormat": "Agent Service"
          },
          {
            "expr": "up{job=\"integration-service\"}",
            "legendFormat": "Integration Service"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_sum[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      }
    ]
  }
}
```

## 🔒 **Security Configuration**

### **SSL/TLS Configuration**
```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name bmad.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bmad.example.com;

    ssl_certificate /etc/nginx/ssl/bmad.crt;
    ssl_certificate_key /etc/nginx/ssl/bmad.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://agent-service:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Security Headers**
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

## 📋 **Deployment Checklist**

### **Pre-Deployment**
- [ ] Code review completed
- [ ] All tests passing (133+ tests)
- [ ] Security scan completed
- [ ] Performance testing completed
- [ ] Database migrations prepared
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Monitoring configured

### **Deployment**
- [ ] Backup current environment
- [ ] Deploy new version
- [ ] Run health checks
- [ ] Execute database migrations
- [ ] Verify service discovery
- [ ] Test API endpoints
- [ ] Monitor error rates
- [ ] Update DNS/load balancer

### **Post-Deployment**
- [ ] Monitor application metrics
- [ ] Verify user functionality
- [ ] Check error logs
- [ ] Validate performance
- [ ] Update documentation
- [ ] Notify stakeholders

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Service Won't Start**
```bash
# Check logs
docker-compose logs service-name

# Check environment variables
docker-compose config

# Check port conflicts
netstat -tulpn | grep :8001
```

#### **Database Connection Issues**
```bash
# Test database connection
docker exec -it postgres psql -U bmad_user -d bmad_production

# Check database logs
docker-compose logs postgres
```

#### **Service Discovery Issues**
```bash
# Check Consul health
curl http://localhost:8500/v1/health/service/agent-service

# Restart Consul
docker-compose restart consul
```

### **Rollback Procedure**
```bash
#!/bin/bash
# rollback.sh

echo "🔄 Rolling back deployment..."

# Stop current deployment
docker-compose down

# Restore from backup
docker-compose -f docker-compose.backup.yml up -d

# Verify rollback
./scripts/health-check.sh

echo "✅ Rollback complete!"
```

## 📚 **Additional Resources**

### **Documentation Links**
- [Agent Service README](../microservices/agent-service/README.md)
- [Integration Service README](../microservices/integration-service/README.md)
- [Context Service README](../microservices/context-service/README.md)
- [Workflow Service README](../microservices/workflow-service/README.md)
- [Authentication Service README](../microservices/auth-service/README.md)
- [Notification Service README](../microservices/notification-service/README.md)

### **API Documentation**
- Agent Service: http://localhost:8001/docs
- Integration Service: http://localhost:8002/docs
- Context Service: http://localhost:8003/docs
- Workflow Service: http://localhost:8004/docs
- Authentication Service: http://localhost:8005/docs
- Notification Service: http://localhost:8006/docs

### **Monitoring URLs**
- Consul UI: http://localhost:8500
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

---

**Document Version**: 1.0  
**Last Updated**: 27 januari 2025  
**Next Review**: After each deployment  
**Status**: ✅ **COMPLETE** - Ready for production deployment 