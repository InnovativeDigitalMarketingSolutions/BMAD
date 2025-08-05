# BMAD API Endpoints Guide

**Datum**: 27 januari 2025  
**Status**: ✅ **COMPLETE** - All endpoints documented  
**Scope**: Complete API endpoint documentation met security en enterprise features  

## 🎯 Executive Summary

Deze guide documenteert alle BMAD API endpoints inclusief de recent geïmplementeerde security features, period-based usage tracking, en tenant limit checking. Alle endpoints zijn getest en gevalideerd voor productie gebruik.

## 🔐 **Authentication & Security**

### **Authentication Required**
Alle endpoints (behalve `/test/*`) vereisen JWT token authenticatie:

```bash
# Request Header
Authorization: Bearer <your-jwt-token>
```

### **Security Features**
- **Rate Limiting**: 200 requests/day, 50/hour
- **Security Headers**: 8 security headers op alle responses
- **Permission Checking**: Role-based access control
- **Tenant Isolation**: Multi-tenant support

## 📊 **API Endpoints**

### **1. Authentication Endpoints**

#### **POST /api/auth/login**
Authenticate user en krijg JWT tokens.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Permissions**: None (public endpoint)

#### **POST /api/auth/refresh**
Refresh access token met refresh token.

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Permissions**: None (public endpoint)

### **2. Orchestrator Endpoints**

#### **POST /orchestrator/start-workflow**
Start een workflow met tenant limit checking.

**Request Body**:
```json
{
  "workflow": "data_processing_workflow"
}
```

**Response**:
```json
{
  "status": "started",
  "workflow": "data_processing_workflow"
}
```

**Permissions**: `execute_workflows` (tenant-aware)
**Security**: Tenant workflow limit checking

#### **GET /orchestrator/status**
Krijg orchestrator status.

**Response**:
```json
{
  "status": "running",
  "active_workflows": 5,
  "total_workflows": 25
}
```

**Permissions**: None (authenticated users)

#### **GET /orchestrator/workflow/{name}/status**
Krijg specifieke workflow status.

**Response**:
```json
{
  "workflow": "data_processing_workflow",
  "status": "completed"
}
```

**Permissions**: None (authenticated users)

#### **GET /orchestrator/metrics**
Krijg orchestrator metrics.

**Response**:
```json
{
  "total_workflows": 25,
  "completed_workflows": 20,
  "failed_workflows": 2,
  "running_workflows": 3
}
```

**Permissions**: `view_analytics` (tenant-aware)

### **3. Agent Endpoints**

#### **POST /agent/{agent_name}/command**
Voer agent commando uit met tenant limit checking.

**Request Body**:
```json
{
  "command": "process_data",
  "parameters": {
    "data_source": "database",
    "output_format": "json"
  }
}
```

**Response**:
```json
{
  "status": "command received",
  "agent": "DataEngineer",
  "command": "process_data"
}
```

**Permissions**: `execute_agents` (tenant-aware)
**Security**: Tenant agent limit checking

#### **GET /agent/{agent_name}/status**
Krijg agent status.

**Response**:
```json
{
  "agent": "DataEngineer",
  "status": "idle"
}
```

**Permissions**: None (authenticated users)

### **4. Context Endpoints**

#### **GET /context/{agent}/{type}**
Krijg agent context.

**Response**:
```json
{
  "agent": "DataEngineer",
  "type": "pipeline",
  "context": {
    "current_pipeline": "data_processing",
    "status": "running"
  }
}
```

**Permissions**: None (authenticated users)

#### **POST /context/{agent}/{type}**
Update agent context.

**Request Body**:
```json
{
  "pipeline_config": {
    "source": "database",
    "destination": "warehouse"
  }
}
```

**Response**:
```json
{
  "status": "context saved",
  "agent": "DataEngineer",
  "type": "pipeline"
}
```

**Permissions**: `edit_agents` (tenant-aware)

### **5. Enterprise Features - Multi-Tenancy**

#### **GET /api/tenants**
Lijst alle tenants.

**Response**:
```json
[
  {
    "id": "tenant_123",
    "name": "Acme Corp",
    "domain": "acme.com",
    "plan": "premium",
    "status": "active"
  }
]
```

**Permissions**: `view_tenants`

#### **POST /api/tenants**
Maak nieuwe tenant.

**Request Body**:
```json
{
  "name": "New Corp",
  "domain": "newcorp.com",
  "plan": "basic"
}
```

**Response**:
```json
{
  "id": "tenant_456",
  "name": "New Corp",
  "domain": "newcorp.com",
  "plan": "basic",
  "status": "active"
}
```

**Permissions**: `create_tenants`

#### **GET /api/tenants/{tenant_id}**
Krijg specifieke tenant.

**Response**:
```json
{
  "id": "tenant_123",
  "name": "Acme Corp",
  "domain": "acme.com",
  "plan": "premium",
  "status": "active"
}
```

**Permissions**: None (authenticated users)

#### **PUT /api/tenants/{tenant_id}**
Update tenant.

**Request Body**:
```json
{
  "name": "Updated Corp",
  "plan": "enterprise"
}
```

**Response**:
```json
{
  "id": "tenant_123",
  "name": "Updated Corp",
  "domain": "acme.com",
  "plan": "enterprise",
  "status": "active"
}
```

**Permissions**: `edit_tenants`

### **6. Enterprise Features - User Management**

#### **GET /api/users**
Lijst alle users.

**Response**:
```json
[
  {
    "id": "user_123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tenant_id": "tenant_123",
    "status": "active"
  }
]
```

**Permissions**: `view_users`

#### **POST /api/users**
Maak nieuwe user.

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "tenant_id": "tenant_123",
  "roles": ["user"]
}
```

**Response**:
```json
{
  "id": "user_456",
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "tenant_id": "tenant_123",
  "status": "active"
}
```

**Permissions**: `create_users`

#### **PUT /api/users/{user_id}**
Update user.

**Request Body**:
```json
{
  "first_name": "Updated",
  "roles": ["admin", "user"]
}
```

**Response**:
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "first_name": "Updated",
  "last_name": "Doe",
  "tenant_id": "tenant_123",
  "status": "active"
}
```

**Permissions**: `edit_users`

### **7. Enterprise Features - Permissions**

#### **GET /api/permissions/user/{user_id}**
Krijg user permissions.

**Response**:
```json
{
  "user_id": "user_123",
  "permissions": ["view_agents", "execute_agents", "view_analytics"],
  "roles": ["admin"],
  "tenant_id": "tenant_123"
}
```

**Permissions**: `view_users` (tenant-aware)

#### **POST /api/permissions/check**
Check permissions voor user.

**Request Body**:
```json
{
  "user_id": "user_123",
  "permissions": ["execute_agents", "view_analytics"]
}
```

**Response**:
```json
{
  "user_id": "user_123",
  "permissions": {
    "execute_agents": true,
    "view_analytics": true
  },
  "has_all": true
}
```

**Permissions**: None (authenticated users)

### **8. Enterprise Features - Billing**

#### **GET /api/billing/plans**
Lijst beschikbare billing plans.

**Response**:
```json
[
  {
    "id": "basic",
    "name": "Basic Plan",
    "price": 29.99,
    "features": ["5 agents", "10 workflows", "1GB storage"]
  },
  {
    "id": "premium",
    "name": "Premium Plan",
    "price": 99.99,
    "features": ["20 agents", "50 workflows", "10GB storage"]
  }
]
```

**Permissions**: None (authenticated users)

#### **GET /api/billing/subscription**
Krijg tenant subscription.

**Response**:
```json
{
  "tenant_id": "tenant_123",
  "plan": "premium",
  "status": "active",
  "current_period_start": "2025-01-01T00:00:00Z",
  "current_period_end": "2025-02-01T00:00:00Z"
}
```

**Permissions**: None (authenticated users)

#### **GET /api/billing/usage**
Krijg tenant usage met period-based tracking.

**Query Parameters**:
- `period` (optional): `current_month`, `current_quarter`, `current_year`, `last_month`, `last_quarter`, `last_year`

**Response**:
```json
{
  "api_calls": 1250,
  "agent_executions": 450,
  "workflow_executions": 120,
  "storage_used": 2.5
}
```

**Permissions**: None (authenticated users)
**Features**: Period-based usage tracking

### **9. Enterprise Features - Feature Flags**

#### **GET /api/features/{flag_name}**
Krijg feature flag waarde.

**Response**:
```json
{
  "flag": "advanced_analytics",
  "value": true
}
```

**Permissions**: None (authenticated users)

### **10. Enterprise Features - Security**

#### **GET /api/security/compliance**
Krijg security compliance status.

**Response**:
```json
{
  "tenant_id": "tenant_123",
  "compliance": {
    "gdpr": true,
    "soc2": true,
    "iso27001": false
  },
  "last_audit": "2025-01-15T00:00:00Z"
}
```

**Permissions**: `view_analytics`

#### **GET /api/security/audit-logs**
Krijg audit logs.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)
- `limit` (optional): Number of logs (default: 100)

**Response**:
```json
[
  {
    "id": "log_123",
    "user_id": "user_123",
    "tenant_id": "tenant_123",
    "event_type": "authentication",
    "action": "login",
    "timestamp": "2025-01-27T10:00:00Z",
    "ip_address": "192.168.1.1",
    "success": true
  }
]
```

**Permissions**: `view_logs`

#### **GET /api/security/report**
Genereer security report.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "tenant_id": "tenant_123",
  "period": "last_30_days",
  "summary": {
    "total_events": 1250,
    "security_events": 5,
    "failed_logins": 2,
    "permission_denials": 3
  },
  "recommendations": [
    "Enable MFA for all users",
    "Review failed login attempts"
  ]
}
```

**Permissions**: `view_analytics`

### **11. Test Endpoints**

#### **GET /test/ping**
Health check endpoint.

**Response**:
```json
{
  "pong": true
}
```

**Permissions**: None (public endpoint)

#### **POST /test/echo**
Echo request body.

**Request Body**:
```json
{
  "message": "Hello World"
}
```

**Response**:
```json
{
  "message": "Hello World"
}
```

**Permissions**: None (public endpoint)

## 🔧 **Error Responses**

Alle endpoints kunnen de volgende error responses retourneren:

### **400 Bad Request**
```json
{
  "error": "Bad request",
  "message": "Invalid request parameters"
}
```

### **401 Unauthorized**
```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### **403 Forbidden**
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### **404 Not Found**
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

### **429 Too Many Requests**
```json
{
  "error": "Too many requests",
  "message": "Rate limit exceeded"
}
```

### **500 Internal Server Error**
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 📊 **Rate Limiting**

### **Default Limits**
- **Daily**: 200 requests per day
- **Hourly**: 50 requests per hour

### **Rate Limit Headers**
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1643270400
```

## 🔐 **Security Headers**

Alle responses bevatten de volgende security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## 🚀 **Production Usage**

### **Base URL**
```
https://api.bmad.com
```

### **Authentication**
```bash
# Get JWT token
curl -X POST https://api.bmad.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use token in requests
curl -X GET https://api.bmad.com/api/tenants \
  -H "Authorization: Bearer <your-jwt-token>"
```

### **Environment Variables**
```bash
# Required for production
export JWT_SECRET_KEY=your-production-secret-key
export ALLOWED_ORIGINS=https://yourdomain.com
export DEV_MODE=false
```

## 📝 **Best Practices**

### **API Usage**
1. **Always use HTTPS**: All endpoints require HTTPS
2. **Handle rate limits**: Implement exponential backoff
3. **Validate responses**: Check HTTP status codes
4. **Use pagination**: For large data sets
5. **Cache tokens**: JWT tokens expire after 30 minutes

### **Error Handling**
1. **Check status codes**: Always verify HTTP status
2. **Handle 429 errors**: Implement retry logic
3. **Log errors**: For debugging and monitoring
4. **User feedback**: Provide clear error messages

### **Security**
1. **Secure token storage**: Store JWT tokens securely
2. **Token refresh**: Use refresh tokens before expiry
3. **Input validation**: Validate all user inputs
4. **Monitor usage**: Track API usage patterns

---

**Document Status**: Complete  
**Last Updated**: 27 januari 2025  
**Next Review**: Monthly API review  
**Owner**: API Team  
**Stakeholders**: Development, DevOps, Security 