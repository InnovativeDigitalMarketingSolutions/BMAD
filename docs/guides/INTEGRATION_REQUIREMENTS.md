# Third-Party Integration Requirements Guide

## 🔑 **Integration Setup Requirements**

This document outlines all third-party integrations, their requirements, and setup instructions for the BMAD system.

---

## **✅ Completed Integrations**

### **1. Stripe Integration** ✅
**Status**: Complete  
**Requirements**:
- ✅ Stripe Account
- ✅ API Keys (Publishable & Secret)
- ✅ Webhook Endpoint

**Setup**:
```bash
# Environment variables needed:
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### **2. Auth0 Integration** ✅
**Status**: Complete  
**Requirements**:
- ✅ Auth0 Account
- ✅ Application Setup
- ✅ API Configuration

**Setup**:
```bash
# Environment variables needed:
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_AUDIENCE=your_api_identifier
```

### **3. PostgreSQL Integration** ✅
**Status**: Complete  
**Requirements**:
- ✅ PostgreSQL Database
- ✅ Connection Details

**Setup**:
```bash
# Environment variables needed:
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bmad_db
POSTGRES_USER=bmad_user
POSTGRES_PASSWORD=your_password
```

### **4. Redis Integration** ✅
**Status**: Complete  
**Requirements**:
- ✅ Redis Server
- ✅ Connection Details

**Setup**:
```bash
# Environment variables needed:
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0
```

### **5. Email Service Integration** ✅
**Status**: Complete  
**Requirements**:
- ✅ SendGrid Account OR Mailgun Account
- ✅ API Keys

**Setup**:
```bash
# For SendGrid:
SENDGRID_API_KEY=SG.your_api_key

# For Mailgun:
MAILGUN_API_KEY=key-your_api_key
MAILGUN_DOMAIN=your_domain.com
```

---

## **🔄 In Progress Integrations**

### **6. File Storage Integration** 🔄
**Status**: Planned (Week 3)  
**Requirements**:
- ❌ AWS Account OR Google Cloud Account
- ❌ Storage Bucket
- ❌ API Keys

**Setup Required**:
```bash
# For AWS S3:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name

# For Google Cloud Storage:
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

**Account Setup Instructions**:
1. **AWS S3**:
   - Create AWS Account
   - Create IAM User with S3 permissions
   - Generate Access Key & Secret Key
   - Create S3 Bucket

2. **Google Cloud Storage**:
   - Create Google Cloud Account
   - Create Project
   - Enable Cloud Storage API
   - Create Service Account
   - Download JSON key file
   - Create Storage Bucket

---

## **📋 Planned Integrations**

### **7. Monitoring & Observability** 📋
**Status**: Planned (Week 4-5)  
**Requirements**:
- ❌ Prometheus Server
- ❌ Grafana Account
- ❌ Error Tracking Service (Sentry)

**Setup**:
```bash
# Prometheus:
PROMETHEUS_URL=http://localhost:9090

# Grafana:
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your_api_key

# Sentry:
SENTRY_DSN=https://your-sentry-dsn
```

### **8. Container Orchestration** 📋
**Status**: Planned (Week 5-6)  
**Requirements**:
- ❌ Docker Hub Account
- ❌ Kubernetes Cluster
- ❌ Container Registry

**Setup**:
```bash
# Docker:
DOCKER_REGISTRY=your-registry.com
DOCKER_USERNAME=your_username
DOCKER_PASSWORD=your_password

# Kubernetes:
KUBECONFIG=path/to/kubeconfig
```

---

## **🔧 Development Mode**

### **DEV_MODE Configuration** ✅
**Status**: Complete  
**Requirements**: None (local development only)

**Setup**:
```bash
# In .env file:
DEV_MODE=true
```

**What it enables**:
- ✅ Authentication bypass
- ✅ Admin permissions
- ✅ Dev tenant context
- ✅ Slack notification bypass
- ✅ HITL auto-approval

---

## **📊 Integration Status Overview**

| Integration | Status | Account Required | API Keys Required | Setup Complexity |
|-------------|--------|------------------|-------------------|------------------|
| Stripe | ✅ Complete | ✅ | ✅ | Medium |
| Auth0 | ✅ Complete | ✅ | ✅ | Medium |
| PostgreSQL | ✅ Complete | ❌ | ❌ | Low |
| Redis | ✅ Complete | ❌ | ❌ | Low |
| Email Service | ✅ Complete | ✅ | ✅ | Medium |
| File Storage | 🔄 Planned | ✅ | ✅ | High |
| Monitoring | 📋 Planned | ✅ | ✅ | High |
| Container Orchestration | 📋 Planned | ✅ | ✅ | High |

---

## **🚀 Setup Priority**

### **Immediate (File Storage Integration)**
1. **Choose Provider**: AWS S3 OR Google Cloud Storage
2. **Create Account**: Set up cloud provider account
3. **Create Bucket**: Set up storage bucket
4. **Generate Keys**: Create API keys/service account
5. **Configure Environment**: Add environment variables

### **Next Steps**
1. **Monitoring Setup**: Prometheus, Grafana, Sentry
2. **Container Setup**: Docker Hub, Kubernetes
3. **Production Deployment**: Full infrastructure

---

## **🔒 Security Considerations**

### **API Key Management**
- ✅ Use environment variables (never hardcode)
- ✅ Rotate keys regularly
- ✅ Use least privilege principle
- ✅ Monitor key usage

### **Development vs Production**
- ✅ Use separate accounts for dev/prod
- ✅ Use different API keys for each environment
- ✅ Enable DEV_MODE only in development
- ✅ Never commit API keys to version control

---

## **📝 Environment Variables Template**

Create a `.env.template` file:

```bash
# Development Mode
DEV_MODE=true

# Stripe Integration
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Auth0 Integration
AUTH0_DOMAIN=
AUTH0_CLIENT_ID=
AUTH0_CLIENT_SECRET=
AUTH0_AUDIENCE=

# PostgreSQL Integration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bmad_db
POSTGRES_USER=bmad_user
POSTGRES_PASSWORD=

# Redis Integration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Email Service Integration
SENDGRID_API_KEY=
# OR
MAILGUN_API_KEY=
MAILGUN_DOMAIN=

# File Storage Integration (Choose one)
# AWS S3:
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=

# Google Cloud Storage:
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_STORAGE_BUCKET=
GOOGLE_APPLICATION_CREDENTIALS=

# Monitoring (Future)
PROMETHEUS_URL=
GRAFANA_URL=
GRAFANA_API_KEY=
SENTRY_DSN=
``` 