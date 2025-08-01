# Development Setup Guide

## 🔧 **Development Environment Configuration**

### **Environment Variables**

#### **DEV_MODE**
Set this environment variable to enable development mode with authentication bypass.

```bash
export DEV_MODE=true
```

**What DEV_MODE enables:**
- ✅ **Authentication Bypass**: All API endpoints accessible without login
- ✅ **Admin Permissions**: Full admin access to all features
- ✅ **Dev Tenant**: Automatic tenant context (`dev_tenant`)
- ✅ **Dev User**: Automatic user context (`dev_user`)
- ✅ **All Features**: All feature flags enabled
- ✅ **All Permissions**: All permissions granted

**Security Note**: This should **NEVER** be enabled in production environments.

### **Development Workflow**

#### **1. Enable Development Mode**
```bash
# Set environment variable
export DEV_MODE=true

# Or add to your .env file
echo "DEV_MODE=true" >> .env
```

#### **2. Start Development Server**
```bash
# Start the BMAD API server
python bmad/api.py

# Or use Flask development server
export FLASK_APP=bmad/api.py
export FLASK_ENV=development
flask run
```

#### **3. Test API Endpoints**
All endpoints are now accessible without authentication:

```bash
# Test orchestrator status
curl http://localhost:5000/orchestrator/status

# Test workflow execution
curl -X POST http://localhost:5000/orchestrator/start-workflow \
  -H "Content-Type: application/json" \
  -d '{"workflow": "test_workflow"}'

# Test agent commands
curl -X POST http://localhost:5000/agent/test_agent/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test_command"}'

# Test enterprise features
curl http://localhost:5000/api/tenants
curl http://localhost:5000/api/users
curl http://localhost:5000/api/billing/plans
```

### **Development Context**

When `DEV_MODE=true` is set, the system automatically provides:

**User Context:**
```python
request.user = {
    'id': 'dev_user',
    'email': 'dev@bmad.local',
    'roles': ['admin'],
    'permissions': ['*']  # All permissions
}
```

**Tenant Context:**
```python
request.tenant_id = 'dev_tenant'
```

**Enterprise Context:**
```python
get_enterprise_context() = {
    'tenant_id': 'dev_tenant',
    'user_id': 'dev_user'
}
```

### **Testing with Development Mode**

#### **Unit Tests**
Development mode is automatically enabled during testing:

```python
# Tests will automatically use dev context
def test_api_endpoint():
    response = client.get('/orchestrator/status')
    assert response.status_code == 200
```

#### **Integration Tests**
```python
# No need to mock authentication
def test_workflow_execution():
    response = client.post('/orchestrator/start-workflow', 
                          json={'workflow': 'test'})
    assert response.status_code == 200
```

#### **E2E Tests**
```python
# Full end-to-end testing without auth setup
def test_complete_workflow():
    # All enterprise features available
    response = client.get('/api/tenants')
    assert response.status_code == 200
```

### **Production vs Development**

| Feature | Development (DEV_MODE=true) | Production (DEV_MODE=false) |
|---------|------------------------------|------------------------------|
| Authentication | Bypassed | Required |
| Permissions | All granted | Checked |
| Feature Flags | All enabled | Tenant-specific |
| Tenant Context | `dev_tenant` | From request |
| User Context | `dev_user` | From JWT token |
| Security Checks | Disabled | Enforced |

### **Troubleshooting**

#### **Common Issues**

**1. Authentication Still Required**
```bash
# Check if DEV_MODE is set
echo $DEV_MODE

# Restart your application after setting DEV_MODE
```

**2. Permission Denied Errors**
```bash
# Ensure DEV_MODE=true is set
export DEV_MODE=true
```

**3. Tenant Not Found**
```bash
# Development mode should use dev_tenant automatically
# Check if DEV_MODE is properly set
```

### **Best Practices**

1. **Never commit DEV_MODE=true to production**
2. **Use .env files for local development**
3. **Test both with and without DEV_MODE**
4. **Document any DEV_MODE specific behavior**
5. **Use feature flags for development features**

### **Environment Setup Script**

Create a `setup_dev.sh` script:

```bash
#!/bin/bash
# Development environment setup

echo "Setting up BMAD development environment..."

# Set development mode
export DEV_MODE=true

# Set Flask environment
export FLASK_APP=bmad/api.py
export FLASK_ENV=development

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Development environment ready!"
echo "DEV_MODE: $DEV_MODE"
echo "FLASK_APP: $FLASK_APP"
echo "PYTHONPATH: $PYTHONPATH"
```

Make it executable:
```bash
chmod +x setup_dev.sh
source setup_dev.sh
``` 