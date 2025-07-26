# 🔧 BMAD Example Interactions & Use Cases

## 🎯 Overzicht

Deze documentatie bevat praktische voorbeelden van hoe BMAD agents samenwerken aan verschillende taken en projecten. Deze voorbeelden dienen als referentie en learning materiaal.

---

## 🏗️ Voorbeeld 1: Authentication Backend Development

### **Scenario**
Een nieuwe SaaS applicatie heeft een robuuste authenticatie backend nodig met email/password en OAuth ondersteuning.

### **Human Input**
```
"Create the authentication backend (email/password + OAuth) using Supabase. 
Ensure JWT-based auth and secure refresh token rotation. Use Docker and include 
flake8 and pytest tests. Use Redis for session cache."
```

### **Agent Workflow**

#### **1. ProductOwner - Requirements Analysis**
```bash
python -m bmad.projects.cli load my-saas-app
python -m bmad.agents.Agent.ProductOwner.product_owner create-story
```

**Output:**
```
📋 User Stories Created:
1. As a user, I want to register with email/password so that I can create an account
2. As a user, I want to login with OAuth providers so that I can use my existing accounts
3. As a user, I want secure JWT tokens so that my sessions are protected
4. As a user, I want automatic token refresh so that I don't get logged out unexpectedly
```

#### **2. Architect - System Design**
```bash
python -m bmad.agents.Agent.Architect.architect design-api
```

**Output:**
```
🏗️ Authentication API Design:
- POST /auth/register - User registration
- POST /auth/login - Email/password login
- POST /auth/oauth/{provider} - OAuth login
- POST /auth/refresh - Token refresh
- POST /auth/logout - User logout
- GET /auth/me - Get current user

Database Schema:
- users (id, email, password_hash, oauth_provider, oauth_id, created_at)
- sessions (id, user_id, token_hash, expires_at, created_at)
```

#### **3. BackendDeveloper - Implementation**
```bash
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper build-api
```

**Output:**
```
🔧 Backend Implementation:
✅ Flask app with Supabase integration
✅ JWT token generation and validation
✅ OAuth provider integration (Google, GitHub)
✅ Redis session caching
✅ Password hashing with bcrypt
✅ Input validation and error handling
```

#### **4. SecurityDeveloper - Security Review**
```bash
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper security-review
```

**Output:**
```
🔒 Security Review Complete:
✅ JWT tokens properly signed and validated
✅ Password hashing with salt and pepper
✅ Rate limiting implemented
✅ CORS properly configured
✅ Input sanitization applied
✅ Session timeout configured
```

#### **5. TestEngineer - Testing**
```bash
python -m bmad.agents.Agent.TestEngineer.testengineer run-tests
```

**Output:**
```
🧪 Test Results:
✅ Unit tests: 15/15 passed
✅ Integration tests: 8/8 passed
✅ Security tests: 5/5 passed
✅ Coverage: 92%
✅ Linting: 0 errors, 0 warnings
```

#### **6. DevOpsInfra - Deployment**
```bash
python -m bmad.agents.Agent.DevOpsInfra.devopsinfra deploy
```

**Output:**
```
🚀 Deployment Complete:
✅ Docker container built and tested
✅ Environment variables configured
✅ Health checks implemented
✅ Monitoring and logging setup
✅ Rollback procedures documented
```

---

## 🎨 Voorbeeld 2: Frontend Dashboard Development

### **Scenario**
Het BMAD team moet een monitoring dashboard bouwen voor real-time agent status en workflow management.

### **Human Input**
```
"Build a monitoring dashboard for the BMAD agents with real-time status, 
workflow management, and API testing interface. Use React with TypeScript 
and Tailwind CSS."
```

### **Agent Workflow**

#### **1. ProductOwner - User Stories**
```bash
python -m bmad.projects.cli create bmad-dashboard web_app
python -m bmad.projects.cli load bmad-dashboard
python -m bmad.agents.Agent.ProductOwner.product_owner create-story
```

**Output:**
```
📋 User Stories Created:
1. As a developer, I want to see real-time agent status so that I can monitor system health
2. As a developer, I want to manage workflows so that I can coordinate agent activities
3. As a developer, I want to test API endpoints so that I can verify functionality
4. As a developer, I want to view metrics and charts so that I can track performance
```

#### **2. Architect - Frontend Design**
```bash
python -m bmad.agents.Agent.Architect.architect design-frontend
```

**Output:**
```
🎨 Frontend Architecture:
Components:
- Dashboard (main layout)
- AgentStatus (real-time agent monitoring)
- WorkflowManager (workflow control)
- APITester (API testing interface)
- MetricsChart (performance visualization)

State Management:
- Redux for global state
- WebSocket for real-time updates
- Local storage for user preferences
```

#### **3. FrontendDeveloper - Component Development**
```bash
python -m bmad.agents.Agent.FrontendDeveloper.frontenddeveloper build-component
```

**Output:**
```
⚛️ React Components Created:
✅ Dashboard.tsx - Main dashboard layout
✅ AgentStatus.tsx - Real-time agent status cards
✅ WorkflowManager.tsx - Workflow control panel
✅ APITester.tsx - API testing interface
✅ MetricsChart.tsx - Performance charts
✅ Navigation.tsx - Sidebar navigation
```

#### **4. FullstackDeveloper - Integration**
```bash
python -m bmad.agents.Agent.FullstackDeveloper.fullstackdeveloper build-frontend
```

**Output:**
```
🔗 Fullstack Integration:
✅ API integration with BMAD backend
✅ WebSocket connection for real-time updates
✅ State management with Redux Toolkit
✅ TypeScript types for all components
✅ Tailwind CSS styling
✅ Responsive design implementation
```

#### **5. UXUIDesigner - User Experience**
```bash
python -m bmad.agents.Agent.UXUIDesigner.uxuidesigner design-ui
```

**Output:**
```
🎯 UX Design Complete:
✅ Intuitive navigation and layout
✅ Consistent color scheme and typography
✅ Responsive design for all screen sizes
✅ Accessibility features implemented
✅ User feedback mechanisms
✅ Error handling and loading states
```

#### **6. TestEngineer - Frontend Testing**
```bash
python -m bmad.agents.Agent.TestEngineer.testengineer test-frontend
```

**Output:**
```
🧪 Frontend Test Results:
✅ Component tests: 12/12 passed
✅ Integration tests: 6/6 passed
✅ E2E tests: 4/4 passed
✅ Accessibility tests: 8/8 passed
✅ Performance tests: 3/3 passed
```

---

## 🔄 Voorbeeld 3: API Service Development

### **Scenario**
Een nieuwe microservice moet worden ontwikkeld voor data processing en analytics.

### **Human Input**
```
"Create a data processing API service that can handle large datasets, 
perform real-time analytics, and provide RESTful endpoints. Include 
authentication, rate limiting, and comprehensive monitoring."
```

### **Agent Workflow**

#### **1. ProductOwner - Service Requirements**
```bash
python -m bmad.projects.cli create data-api api_service
python -m bmad.projects.cli load data-api
python -m bmad.agents.Agent.ProductOwner.product_owner create-story
```

**Output:**
```
📋 API Service Requirements:
1. As a client, I want to upload datasets so that I can process my data
2. As a client, I want to run analytics queries so that I can get insights
3. As a client, I want real-time processing so that I can get immediate results
4. As an admin, I want monitoring and logging so that I can track system health
```

#### **2. Architect - Service Architecture**
```bash
python -m bmad.agents.Agent.Architect.architect design-api
```

**Output:**
```
🏗️ Service Architecture:
API Endpoints:
- POST /data/upload - Upload datasets
- GET /data/{id} - Get dataset info
- POST /analytics/query - Run analytics
- GET /analytics/results/{id} - Get results
- GET /health - Health check
- GET /metrics - System metrics

Technology Stack:
- FastAPI for API framework
- PostgreSQL for data storage
- Redis for caching
- Celery for background tasks
- Prometheus for monitoring
```

#### **3. BackendDeveloper - Service Implementation**
```bash
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper build-api
```

**Output:**
```
🔧 Service Implementation:
✅ FastAPI application with OpenAPI docs
✅ PostgreSQL database integration
✅ Redis caching layer
✅ Celery task queue setup
✅ File upload handling
✅ Analytics processing engine
✅ Rate limiting middleware
```

#### **4. DataEngineer - Data Pipeline**
```bash
python -m bmad.agents.Agent.DataEngineer.dataengineer build-pipeline
```

**Output:**
```
📊 Data Pipeline Created:
✅ ETL pipeline for data processing
✅ Data validation and cleaning
✅ Analytics query engine
✅ Real-time processing capabilities
✅ Data quality monitoring
✅ Backup and recovery procedures
```

#### **5. DevOpsInfra - Infrastructure**
```bash
python -m bmad.agents.Agent.DevOpsInfra.devopsinfra setup-infra
```

**Output:**
```
🚀 Infrastructure Setup:
✅ Docker containers for all services
✅ Kubernetes deployment manifests
✅ Prometheus monitoring stack
✅ Grafana dashboards
✅ ELK stack for logging
✅ CI/CD pipeline configuration
```

---

## 🧪 Voorbeeld 4: Testing & Quality Assurance

### **Scenario**
Een bestaande applicatie heeft uitgebreide testing en quality assurance nodig.

### **Human Input**
```
"Implement comprehensive testing for our e-commerce platform. Include unit tests, 
integration tests, performance tests, and security tests. Achieve 90% code coverage 
and set up automated testing in CI/CD."
```

### **Agent Workflow**

#### **1. TestEngineer - Test Strategy**
```bash
python -m bmad.agents.Agent.TestEngineer.testengineer write-tests
```

**Output:**
```
🧪 Test Strategy:
Test Types:
- Unit tests (pytest) for individual functions
- Integration tests for API endpoints
- E2E tests for user workflows
- Performance tests for load testing
- Security tests for vulnerability scanning

Coverage Goals:
- Unit tests: 95% coverage
- Integration tests: 90% coverage
- E2E tests: 80% coverage
```

#### **2. BackendDeveloper - Unit Tests**
```bash
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper write-tests
```

**Output:**
```
✅ Unit Tests Created:
- User authentication tests (15 tests)
- Product management tests (12 tests)
- Order processing tests (18 tests)
- Payment integration tests (8 tests)
- Database operation tests (10 tests)

Coverage: 96% (exceeds target)
```

#### **3. FrontendDeveloper - Component Tests**
```bash
python -m bmad.agents.Agent.FrontendDeveloper.frontenddeveloper test-frontend
```

**Output:**
```
✅ Frontend Tests Created:
- Component rendering tests (20 tests)
- User interaction tests (15 tests)
- State management tests (8 tests)
- API integration tests (12 tests)
- Accessibility tests (6 tests)

Coverage: 94% (exceeds target)
```

#### **4. SecurityDeveloper - Security Testing**
```bash
python -m bmad.agents.Agent.SecurityDeveloper.securitydeveloper audit-code
```

**Output:**
```
🔒 Security Tests Complete:
✅ Authentication bypass tests
✅ SQL injection tests
✅ XSS vulnerability tests
✅ CSRF protection tests
✅ Input validation tests
✅ Authorization tests

Security Score: 95/100
```

#### **5. DevOpsInfra - CI/CD Integration**
```bash
python -m bmad.agents.Agent.DevOpsInfra.devopsinfra setup-ci
```

**Output:**
```
🚀 CI/CD Pipeline:
✅ Automated test execution on PR
✅ Coverage reporting
✅ Security scanning
✅ Performance testing
✅ Quality gates enforcement
✅ Automated deployment on success
```

---

## 📊 Voorbeeld 5: Performance Optimization

### **Scenario**
Een bestaande applicatie heeft performance problemen en moet geoptimaliseerd worden.

### **Human Input**
```
"Our web application is experiencing slow load times and high server costs. 
Analyze the performance bottlenecks and implement optimizations for better 
user experience and cost efficiency."
```

### **Agent Workflow**

#### **1. TestEngineer - Performance Analysis**
```bash
python -m bmad.agents.Agent.TestEngineer.testengineer performance-test
```

**Output:**
```
📊 Performance Analysis:
Current Performance:
- Page load time: 4.2s (target: <2s)
- API response time: 800ms (target: <200ms)
- Database query time: 500ms (target: <100ms)
- Memory usage: 2.1GB (target: <1GB)

Bottlenecks Identified:
- N+1 database queries
- Large bundle size (2.8MB)
- No caching layer
- Inefficient image loading
```

#### **2. BackendDeveloper - Backend Optimization**
```bash
python -m bmad.agents.Agent.BackendDeveloper.backenddeveloper optimize
```

**Output:**
```
🔧 Backend Optimizations:
✅ Database query optimization
✅ Redis caching implementation
✅ Connection pooling
✅ API response compression
✅ Background task processing
✅ Database indexing

Performance Improvement: 65% faster API responses
```

#### **3. FrontendDeveloper - Frontend Optimization**
```bash
python -m bmad.agents.Agent.FrontendDeveloper.frontenddeveloper optimize
```

**Output:**
```
⚡ Frontend Optimizations:
✅ Code splitting and lazy loading
✅ Image optimization and WebP format
✅ Bundle size reduction (2.8MB → 1.2MB)
✅ Service worker for caching
✅ Critical CSS inlining
✅ Preloading strategies

Performance Improvement: 45% faster page loads
```

#### **4. DevOpsInfra - Infrastructure Optimization**
```bash
python -m bmad.agents.Agent.DevOpsInfra.devopsinfra optimize
```

**Output:**
```
🚀 Infrastructure Optimizations:
✅ CDN implementation
✅ Load balancing configuration
✅ Auto-scaling policies
✅ Resource monitoring and alerts
✅ Cost optimization strategies
✅ Performance monitoring dashboards

Cost Reduction: 30% lower infrastructure costs
```

---

## 🔄 Voorbeeld 6: Agent Collaboration

### **Scenario**
Meerdere agents moeten samenwerken aan een complexe feature.

### **Human Input**
```
"Implement a real-time chat feature with file sharing, message encryption, 
and push notifications. This should work across web and mobile platforms."
```

### **Agent Workflow**

#### **1. ProductOwner - Feature Planning**
```bash
python -m bmad.agents.Agent.ProductOwner.product_owner create-story
```

**Output:**
```
📋 Real-time Chat Requirements:
1. As a user, I want to send real-time messages so that I can communicate instantly
2. As a user, I want to share files so that I can collaborate effectively
3. As a user, I want encrypted messages so that my conversations are private
4. As a user, I want push notifications so that I don't miss important messages
```

#### **2. Architect - System Design**
```bash
python -m bmad.agents.Agent.Architect.architect design-system
```

**Output:**
```
🏗️ Chat System Architecture:
Components:
- WebSocket server for real-time communication
- File storage service for file sharing
- Encryption service for message security
- Push notification service
- Mobile API for mobile apps

Technology Stack:
- WebSocket (Socket.IO)
- File storage (AWS S3)
- Encryption (AES-256)
- Push notifications (Firebase)
- Mobile framework (React Native)
```

#### **3. Multi-Agent Collaboration**
```python
# Agents werken parallel aan verschillende componenten

# BackendDeveloper - WebSocket server
backend_dev.publish("websocket_implementation_started", {
    "component": "real_time_chat",
    "estimated_duration": "2 days"
})

# FrontendDeveloper - Chat UI
frontend_dev.publish("chat_ui_development_started", {
    "component": "chat_interface",
    "estimated_duration": "3 days"
})

# SecurityDeveloper - Encryption
security_dev.publish("encryption_implementation_started", {
    "component": "message_encryption",
    "estimated_duration": "1 day"
})

# MobileDeveloper - Mobile app
mobile_dev.publish("mobile_chat_development_started", {
    "component": "mobile_chat",
    "estimated_duration": "4 days"
})
```

#### **4. Integration & Testing**
```bash
# TestEngineer coördineert integration testing
python -m bmad.agents.Agent.TestEngineer.testengineer integration-test
```

**Output:**
```
🧪 Integration Testing:
✅ WebSocket connection tests
✅ File upload/download tests
✅ Message encryption/decryption tests
✅ Push notification tests
✅ Cross-platform compatibility tests
✅ Performance under load tests

All integration tests passed ✅
```

---

## 📚 Best Practices

### **Agent Communication**
- Gebruik events voor inter-agent communicatie
- Deel context via project management systeem
- Documenteer beslissingen en rationale
- Escaleer problemen tijdig naar menselijke review

### **Quality Assurance**
- Test alle code voordat deployment
- Implementeer automatische quality checks
- Monitor performance en security
- Documenteer alle wijzigingen

### **Continuous Improvement**
- Leer van elke interactie
- Update confidence scores gebaseerd op outcomes
- Verbeter processen gebaseerd op feedback
- Vier successen en analyseer failures

---

## 🔗 Gerelateerde Documentatie

- **BMAD Methodologie**: `bmad-method.md`
- **Agent Overview**: `agents-overview.md`
- **Project Management**: `project-management.md`
- **Confidence Scoring**: `confidence-scoring.md`
- **Agent Metrics**: `agent-metrics.md` 