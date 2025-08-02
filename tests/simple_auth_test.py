#!/usr/bin/env python3
"""
Simple auth service test without database dependencies
"""

import os
import sys
sys.path.insert(0, 'microservices/auth-service')

# Mock database connection for testing
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'

try:
    from main import app
    print("✅ App imported successfully")
    
    # Test health endpoint
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.get("/health")
    print(f"✅ Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test info endpoint
    response = client.get("/info")
    print(f"✅ Info check: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 