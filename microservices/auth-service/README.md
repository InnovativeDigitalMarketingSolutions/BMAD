# Authentication Service

**Status**: 🚧 **In Development**  
**Priority**: High  
**Timeline**: 1 week  

## 🎯 Overview

The Authentication Service is a dedicated microservice responsible for handling all authentication and authorization operations in the BMAD system. It integrates with Auth0 for enterprise-grade authentication and provides JWT token management, role-based access control, and user session management.

## 🏗 Architecture

```
Authentication Service Architecture:
├── FastAPI Application (20+ endpoints)
├── Auth0 Integration (enterprise authentication)
├── JWT Token Management (issuance, validation, refresh)
├── Role-Based Access Control (RBAC)
├── User Session Management
├── Password Management (reset, change)
├── Multi-Factor Authentication (MFA)
├── Audit Logging
├── Database Schema (users, sessions, roles, permissions)
├── Caching Layer (Redis)
└── Comprehensive Test Suite (40+ tests)
```

## 🔧 Core Features

### **Authentication**
- User registration and login
- JWT token issuance and validation
- Token refresh and revocation
- Password reset and change
- Multi-factor authentication (MFA)

### **Authorization**
- Role-based access control (RBAC)
- Permission management
- Resource-level authorization
- API endpoint protection

### **User Management**
- User profile management
- Session management
- Account status management
- User analytics and metrics

### **Security**
- Audit logging
- Security event monitoring
- Rate limiting
- Brute force protection

## 📡 API Endpoints

### **Health & Monitoring**
```
GET /health - Basic health check
GET /health/ready - Readiness probe
GET /health/live - Liveness probe
```

### **Authentication**
```
POST /auth/register - User registration
POST /auth/login - User login
POST /auth/logout - User logout
POST /auth/refresh - Refresh access token
POST /auth/validate - Validate token
POST /auth/forgot-password - Request password reset
POST /auth/reset-password - Reset password
POST /auth/change-password - Change password
```

### **User Management**
```
GET /users - List users (admin only)
GET /users/{user_id} - Get user details
PUT /users/{user_id} - Update user profile
DELETE /users/{user_id} - Delete user (admin only)
GET /users/{user_id}/sessions - Get user sessions
POST /users/{user_id}/sessions/revoke - Revoke user sessions
```

### **Role & Permission Management**
```
GET /roles - List all roles
POST /roles - Create new role
GET /roles/{role_id} - Get role details
PUT /roles/{role_id} - Update role
DELETE /roles/{role_id} - Delete role
GET /permissions - List all permissions
POST /permissions - Create new permission
```

### **Multi-Factor Authentication**
```
POST /auth/mfa/enable - Enable MFA
POST /auth/mfa/disable - Disable MFA
POST /auth/mfa/verify - Verify MFA code
POST /auth/mfa/setup - Setup MFA device
```

### **Analytics & Monitoring**
```
GET /analytics/users - User analytics
GET /analytics/sessions - Session analytics
GET /analytics/security - Security event analytics
GET /metrics - Service metrics
```

### **Service Information**
```
GET /info - Service information
```

## 🗄 Database Schema

### **Users Table**
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    password_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    auth0_id VARCHAR(255) UNIQUE
);
```

### **Sessions Table**
```sql
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    device_info JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

### **Roles Table**
```sql
CREATE TABLE roles (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **User Roles Table**
```sql
CREATE TABLE user_roles (
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    role_id VARCHAR(255) REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by VARCHAR(255),
    PRIMARY KEY (user_id, role_id)
);
```

### **Audit Logs Table**
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(255),
    resource_id VARCHAR(255),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔐 Security Features

### **JWT Token Management**
- Secure token issuance with proper expiration
- Token refresh mechanism
- Token revocation and blacklisting
- Claims-based authorization

### **Password Security**
- Bcrypt password hashing
- Password complexity requirements
- Brute force protection
- Secure password reset flow

### **Multi-Factor Authentication**
- TOTP (Time-based One-Time Password)
- SMS-based verification
- Backup codes
- Device management

### **Rate Limiting**
- Login attempt limiting
- API rate limiting
- IP-based restrictions
- Account lockout protection

## 🧪 Testing Strategy

### **Unit Tests**
- Authentication logic testing
- JWT token validation
- Password hashing and verification
- Role and permission checking

### **Integration Tests**
- Auth0 integration testing
- Database operations testing
- Redis caching testing
- API endpoint testing

### **Security Tests**
- Authentication bypass testing
- Token manipulation testing
- Rate limiting testing
- SQL injection testing

## 🚀 Deployment

### **Docker Configuration**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/auth_service

# Redis
REDIS_URL=redis://localhost:6379

# Auth0
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_PER_MINUTE=60
```

## 📊 Monitoring & Observability

### **Metrics**
- Authentication success/failure rates
- Token issuance and validation metrics
- User session statistics
- Security event monitoring

### **Logging**
- Structured logging with correlation IDs
- Security event logging
- Performance monitoring
- Error tracking

### **Health Checks**
- Database connectivity
- Redis connectivity
- Auth0 service health
- External service dependencies

## 🔄 Integration Points

### **Auth0 Integration**
- User authentication delegation
- Social login providers
- Enterprise SSO
- User profile synchronization

### **Other Services**
- Agent Service (user context)
- Context Service (user preferences)
- Notification Service (security alerts)
- API Gateway (token validation)

## 📈 Performance Considerations

### **Caching Strategy**
- User session caching in Redis
- Role and permission caching
- Token validation caching
- Database query optimization

### **Scalability**
- Horizontal scaling with load balancing
- Database connection pooling
- Redis cluster support
- Stateless service design

## 🛡 Security Best Practices

### **Token Security**
- Short-lived access tokens
- Secure refresh token rotation
- Token blacklisting
- Claims validation

### **Data Protection**
- PII encryption at rest
- Secure data transmission
- Audit trail maintenance
- GDPR compliance

### **Access Control**
- Principle of least privilege
- Role-based access control
- Resource-level permissions
- API endpoint protection

---

**Document Version**: 1.0  
**Last Updated**: 27 januari 2025  
**Next Review**: After implementation completion 