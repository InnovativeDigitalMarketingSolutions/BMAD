#!/usr/bin/env python3
"""
Simple test for auth service startup
"""

import sys
import os
sys.path.append('microservices/auth-service')

try:
    # Test imports
    print("Testing imports...")
    import sys
    sys.path.insert(0, 'microservices/auth-service')
    from main import app
    print("✅ App imported successfully")
    
    # Test basic functionality
    print("Testing basic functionality...")
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    print(f"✅ Health check response: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 