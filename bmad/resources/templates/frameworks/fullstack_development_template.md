# Fullstack Development Framework Template

## 🎯 Fullstack Development Overview

Dit framework template biedt een complete gids voor fullstack development binnen het BMAD systeem, inclusief end-to-end development workflows, fullstack architecture patterns, en development best practices.

## 🏗️ Fullstack Architecture Patterns

### Fullstack Application Architecture
```
Fullstack Application:
├── Frontend (React + TypeScript)
│   ├── Components/           # Reusable UI components
│   ├── Pages/               # Page components
│   ├── Hooks/               # Custom React hooks
│   ├── Services/            # API services
│   ├── Utils/               # Utility functions
│   └── Types/               # TypeScript definitions
├── Backend (FastAPI + Python)
│   ├── API/                 # REST API endpoints
│   ├── Services/            # Business logic
│   ├── Models/              # Data models
│   ├── Database/            # Database layer
│   └── Utils/               # Backend utilities
├── Shared/
│   ├── Types/               # Shared type definitions
│   ├── Constants/           # Shared constants
│   └── Utils/               # Shared utilities
└── Infrastructure/
    ├── Docker/              # Containerization
    ├── Kubernetes/          # Orchestration
    ├── CI/CD/               # Pipeline configuration
    └── Monitoring/          # Observability
```

### Fullstack Data Flow
```
User Interaction → Frontend → API Gateway → Backend Services → Database
       ↑                                                           ↓
       └─────────────── Real-time Updates ← WebSocket ←───────────┘
```

### Fullstack State Management
- **Frontend State**: React Query + Zustand voor client-side state
- **Backend State**: Database + Redis voor server-side state
- **Shared State**: WebSocket voor real-time synchronization
- **Form State**: React Hook Form voor form management
- **API State**: React Query voor server state caching

## 🔧 Fullstack Development Best Practices

### Project Structure
```
fullstack-app/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   ├── utils/          # Utility functions
│   │   ├── types/          # TypeScript types
│   │   └── styles/         # Global styles
│   ├── public/             # Static assets
│   ├── tests/              # Frontend tests
│   ├── package.json        # Frontend dependencies
│   └── vite.config.ts      # Frontend build config
├── backend/                 # FastAPI backend application
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic
│   │   ├── models/         # Data models
│   │   ├── database/       # Database layer
│   │   └── utils/          # Backend utilities
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Backend dependencies
│   └── main.py             # Backend entry point
├── shared/                  # Shared code between frontend and backend
│   ├── types/              # Shared TypeScript types
│   ├── constants/          # Shared constants
│   └── utils/              # Shared utilities
├── infrastructure/          # Infrastructure configuration
│   ├── docker/             # Docker configuration
│   ├── k8s/                # Kubernetes manifests
│   ├── ci/                 # CI/CD pipelines
│   └── monitoring/         # Monitoring configuration
├── docs/                    # Documentation
├── scripts/                 # Development scripts
└── docker-compose.yml       # Local development setup
```

### TypeScript Shared Types
```typescript
// shared/types/index.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

export type UserRole = 'admin' | 'user' | 'guest';

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  config: AgentConfig;
  createdAt: Date;
  updatedAt: Date;
}

export type AgentType = 'backend' | 'frontend' | 'fullstack' | 'testing' | 'devops';
export type AgentStatus = 'idle' | 'running' | 'completed' | 'failed';

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  status: WorkflowStatus;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  timestamp: Date;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  message: string;
  success: boolean;
}
```

### Fullstack API Integration
```typescript
// frontend/src/services/api.ts
import axios from 'axios';
import type { User, Agent, Workflow, ApiResponse, PaginatedResponse } from '../../../shared/types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// User API
export const userApi = {
  getUsers: (): Promise<ApiResponse<User[]>> => 
    api.get('/users').then(res => res.data),
  
  getUser: (id: string): Promise<ApiResponse<User>> => 
    api.get(`/users/${id}`).then(res => res.data),
  
  createUser: (userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<User>> => 
    api.post('/users', userData).then(res => res.data),
  
  updateUser: (id: string, updates: Partial<User>): Promise<ApiResponse<User>> => 
    api.put(`/users/${id}`, updates).then(res => res.data),
  
  deleteUser: (id: string): Promise<ApiResponse<void>> => 
    api.delete(`/users/${id}`).then(res => res.data),
};

// Agent API
export const agentApi = {
  getAgents: (): Promise<ApiResponse<Agent[]>> => 
    api.get('/agents').then(res => res.data),
  
  getAgent: (id: string): Promise<ApiResponse<Agent>> => 
    api.get(`/agents/${id}`).then(res => res.data),
  
  createAgent: (agentData: Omit<Agent, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<Agent>> => 
    api.post('/agents', agentData).then(res => res.data),
  
  updateAgent: (id: string, updates: Partial<Agent>): Promise<ApiResponse<Agent>> => 
    api.put(`/agents/${id}`, updates).then(res => res.data),
  
  deleteAgent: (id: string): Promise<ApiResponse<void>> => 
    api.delete(`/agents/${id}`).then(res => res.data),
  
  executeAgent: (id: string, input: any): Promise<ApiResponse<any>> => 
    api.post(`/agents/${id}/execute`, input).then(res => res.data),
};

// Workflow API
export const workflowApi = {
  getWorkflows: (): Promise<ApiResponse<Workflow[]>> => 
    api.get('/workflows').then(res => res.data),
  
  getWorkflow: (id: string): Promise<ApiResponse<Workflow>> => 
    api.get(`/workflows/${id}`).then(res => res.data),
  
  createWorkflow: (workflowData: Omit<Workflow, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<Workflow>> => 
    api.post('/workflows', workflowData).then(res => res.data),
  
  updateWorkflow: (id: string, updates: Partial<Workflow>): Promise<ApiResponse<Workflow>> => 
    api.put(`/workflows/${id}`, updates).then(res => res.data),
  
  deleteWorkflow: (id: string): Promise<ApiResponse<void>> => 
    api.delete(`/workflows/${id}`).then(res => res.data),
  
  executeWorkflow: (id: string, input: any): Promise<ApiResponse<any>> => 
    api.post(`/workflows/${id}/execute`, input).then(res => res.data),
};
```

## 🧪 Fullstack Testing Strategy

### End-to-End Testing
```typescript
// tests/e2e/fullstack.test.ts
import { test, expect } from '@playwright/test';

test.describe('Fullstack Application', () => {
  test('complete user workflow', async ({ page }) => {
    // 1. User registration
    await page.goto('/register');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.fill('[data-testid="name-input"]', 'Test User');
    await page.click('[data-testid="register-button"]');
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    
    // 2. User login
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'Password123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // 3. Create agent
    await page.click('[data-testid="create-agent-button"]');
    await page.fill('[data-testid="agent-name-input"]', 'Test Agent');
    await page.selectOption('[data-testid="agent-type-select"]', 'backend');
    await page.fill('[data-testid="agent-description-input"]', 'Test agent for backend development');
    await page.click('[data-testid="submit-button"]');
    
    await expect(page.locator('text=Test Agent')).toBeVisible();
    
    // 4. Execute agent
    await page.click('[data-testid="execute-agent-button"]');
    await page.fill('[data-testid="agent-input"]', 'Create a REST API endpoint');
    await page.click('[data-testid="execute-button"]');
    
    await expect(page.locator('[data-testid="execution-result"]')).toBeVisible();
    
    // 5. Create workflow
    await page.click('[data-testid="create-workflow-button"]');
    await page.fill('[data-testid="workflow-name-input"]', 'Test Workflow');
    await page.fill('[data-testid="workflow-description-input"]', 'Test workflow for fullstack development');
    await page.click('[data-testid="add-step-button"]');
    await page.selectOption('[data-testid="step-agent-select"]', 'Test Agent');
    await page.click('[data-testid="submit-button"]');
    
    await expect(page.locator('text=Test Workflow')).toBeVisible();
    
    // 6. Execute workflow
    await page.click('[data-testid="execute-workflow-button"]');
    await page.fill('[data-testid="workflow-input"]', 'Build a fullstack application');
    await page.click('[data-testid="execute-button"]');
    
    await expect(page.locator('[data-testid="workflow-result"]')).toBeVisible();
  });
  
  test('real-time collaboration', async ({ page, context }) => {
    // Create second browser context for collaboration
    const page2 = await context.newPage();
    
    // User 1 creates a workflow
    await page.goto('/workflows');
    await page.click('[data-testid="create-workflow-button"]');
    await page.fill('[data-testid="workflow-name-input"]', 'Collaborative Workflow');
    await page.click('[data-testid="save-button"]');
    
    // User 2 should see the workflow in real-time
    await page2.goto('/workflows');
    await expect(page2.locator('text=Collaborative Workflow')).toBeVisible();
    
    // User 1 updates the workflow
    await page.click('[data-testid="edit-workflow-button"]');
    await page.fill('[data-testid="workflow-description-input"]', 'Updated description');
    await page.click('[data-testid="save-button"]');
    
    // User 2 should see the update in real-time
    await expect(page2.locator('text=Updated description')).toBeVisible();
  });
});
```

### Fullstack Integration Testing
```typescript
// tests/integration/fullstack.integration.test.ts
import { test, expect } from '@playwright/test';

test.describe('Fullstack Integration', () => {
  test('API integration with frontend', async ({ request }) => {
    // Test user creation via API
    const userData = {
      email: 'integration@example.com',
      password: 'Password123!',
      name: 'Integration User',
      role: 'user'
    };
    
    const createResponse = await request.post('/api/v1/users', {
      data: userData
    });
    
    expect(createResponse.ok()).toBeTruthy();
    const user = await createResponse.json();
    expect(user.data.email).toBe(userData.email);
    
    // Test agent creation via API
    const agentData = {
      name: 'Integration Agent',
      type: 'backend',
      status: 'idle',
      config: { language: 'python' }
    };
    
    const agentResponse = await request.post('/api/v1/agents', {
      data: agentData,
      headers: {
        'Authorization': `Bearer ${user.data.token}`
      }
    });
    
    expect(agentResponse.ok()).toBeTruthy();
    const agent = await agentResponse.json();
    expect(agent.data.name).toBe(agentData.name);
    
    // Test workflow creation via API
    const workflowData = {
      name: 'Integration Workflow',
      description: 'Test workflow for integration testing',
      steps: [{ agentId: agent.data.id, order: 1 }]
    };
    
    const workflowResponse = await request.post('/api/v1/workflows', {
      data: workflowData,
      headers: {
        'Authorization': `Bearer ${user.data.token}`
      }
    });
    
    expect(workflowResponse.ok()).toBeTruthy();
    const workflow = await workflowResponse.json();
    expect(workflow.data.name).toBe(workflowData.name);
  });
  
  test('database integration', async ({ request }) => {
    // Test database operations
    const usersResponse = await request.get('/api/v1/users');
    expect(usersResponse.ok()).toBeTruthy();
    
    const agentsResponse = await request.get('/api/v1/agents');
    expect(agentsResponse.ok()).toBeTruthy();
    
    const workflowsResponse = await request.get('/api/v1/workflows');
    expect(workflowsResponse.ok()).toBeTruthy();
  });
});
```

## 🚀 Fullstack Development Workflow

### Development Environment Setup
```bash
# 1. Clone repository
git clone <repository-url>
cd fullstack-app

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 3. Setup frontend
cd ../frontend
npm install

# 4. Setup shared types
cd ../shared
npm install

# 5. Start development servers
# Terminal 1: Backend
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database
docker-compose up -d postgres redis
```

### Fullstack Development Scripts
```json
// package.json (root)
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "build": "npm run build:backend && npm run build:frontend",
    "build:backend": "cd backend && python -m build",
    "build:frontend": "cd frontend && npm run build",
    "test": "npm run test:backend && npm run test:frontend",
    "test:backend": "cd backend && pytest",
    "test:frontend": "cd frontend && npm run test",
    "test:e2e": "cd frontend && npm run test:e2e",
    "lint": "npm run lint:backend && npm run lint:frontend",
    "lint:backend": "cd backend && flake8 src/",
    "lint:frontend": "cd frontend && npm run lint",
    "format": "npm run format:backend && npm run format:frontend",
    "format:backend": "cd backend && black src/",
    "format:frontend": "cd frontend && npm run format",
    "docker:build": "docker-compose build",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down",
    "docker:logs": "docker-compose logs -f"
  },
  "devDependencies": {
    "concurrently": "^8.0.0"
  }
}
```

### Fullstack Code Quality Gates
```yaml
# .github/workflows/fullstack-ci.yml
name: Fullstack CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run backend tests
        run: |
          cd backend
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run frontend tests
        run: |
          cd frontend
          npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: frontend/coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Start backend
        run: |
          cd backend
          pip install -r requirements.txt
          uvicorn src.main:app --host 0.0.0.0 --port 8000 &
      - name: Start frontend
        run: |
          cd frontend
          npm run build
          npm run preview &
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

  build-and-deploy:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests, e2e-tests]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        run: |
          docker build -t fullstack-app:latest .
          docker push fullstack-app:latest
      - name: Deploy to production
        run: |
          kubectl apply -f infrastructure/k8s/
```

## 🔍 Fullstack Monitoring & Observability

### Fullstack Logging Strategy
```typescript
// frontend/src/utils/logger.ts
import { createLogger, format, transports } from 'winston';

const logger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  defaultMeta: { service: 'frontend' },
  transports: [
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.simple()
      )
    }),
    new transports.File({ filename: 'logs/frontend-error.log', level: 'error' }),
    new transports.File({ filename: 'logs/frontend-combined.log' })
  ]
});

export const logUserAction = (action: string, userId: string, details: any) => {
  logger.info('User action', {
    action,
    userId,
    details,
    timestamp: new Date().toISOString()
  });
};

export const logError = (error: Error, context: any) => {
  logger.error('Application error', {
    error: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString()
  });
};
```

```python
# backend/src/utils/logger.py
import logging
import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def log_api_request(method: str, path: str, user_id: str = None, status_code: int = None):
    logger.info("API request", {
        "method": method,
        "path": path,
        "user_id": user_id,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    })

def log_user_action(action: str, user_id: str, details: dict = None):
    logger.info("User action", {
        "action": action,
        "user_id": user_id,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })

def log_error(error: Exception, context: dict = None):
    logger.error("Application error", {
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    })
```

### Fullstack Performance Monitoring
```typescript
// frontend/src/utils/performance.ts
export const measurePageLoad = (pageName: string) => {
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  
  const metrics = {
    pageName,
    loadTime: navigation.loadEventEnd - navigation.loadEventStart,
    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
    timestamp: new Date().toISOString()
  };
  
  // Send metrics to analytics
  analytics.track('page_performance', metrics);
};

export const measureApiCall = (endpoint: string, method: string, duration: number, status: number) => {
  const metrics = {
    endpoint,
    method,
    duration,
    status,
    timestamp: new Date().toISOString()
  };
  
  analytics.track('api_performance', metrics);
};
```

```python
# backend/src/utils/performance.py
import time
from functools import wraps
from prometheus_client import Histogram, Counter

# Metrics
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])

def measure_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record metrics
            REQUEST_DURATION.labels(
                method=kwargs.get('method', 'unknown'),
                endpoint=kwargs.get('endpoint', 'unknown')
            ).observe(duration)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            # Record error metrics
            REQUEST_COUNT.labels(
                method=kwargs.get('method', 'unknown'),
                endpoint=kwargs.get('endpoint', 'unknown'),
                status='error'
            ).inc()
            raise
    return wrapper
```

## 🚀 Fullstack Deployment Strategy

### Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/fullstack
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=fullstack
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment
```yaml
# infrastructure/k8s/fullstack-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fullstack-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fullstack-app
  template:
    metadata:
      labels:
        app: fullstack-app
    spec:
      containers:
      - name: frontend
        image: fullstack-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: VITE_API_URL
          value: "http://backend-service:8000/api/v1"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

      - name: backend
        image: fullstack-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
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

---
apiVersion: v1
kind: Service
metadata:
  name: fullstack-service
spec:
  selector:
    app: fullstack-app
  ports:
  - name: frontend
    port: 80
    targetPort: 3000
  - name: backend
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## 📚 Fullstack Development Resources

### Essential Technologies
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI, Python, SQLAlchemy, Pydantic
- **Database**: PostgreSQL, Redis
- **Testing**: Playwright, Pytest, Vitest
- **Deployment**: Docker, Kubernetes, Nginx
- **Monitoring**: Prometheus, Grafana, Winston, Structlog

### Development Tools
- **IDE**: VS Code with extensions for React, Python, TypeScript
- **Version Control**: Git with conventional commits
- **Package Management**: npm (frontend), pip (backend)
- **Code Quality**: ESLint, Prettier, Black, Flake8
- **Testing**: Playwright, Pytest, Vitest, MSW

### Documentation
- **React Documentation**: https://react.dev/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **TypeScript Documentation**: https://www.typescriptlang.org/docs/
- **Playwright Documentation**: https://playwright.dev/
- **Docker Documentation**: https://docs.docker.com/
- **Kubernetes Documentation**: https://kubernetes.io/docs/

---

**Template Version**: 1.0  
**Last Updated**: 27 januari 2025  
**Maintained By**: Fullstack Development Team 