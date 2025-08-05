#!/usr/bin/env python3
"""
Simple test for auth service only
"""

import os
import sys
import subprocess
import time
import requests

def test_auth_service():
    """Test auth service specifically."""
    print("🔍 Testing Auth Service...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://postgres:test@localhost:5432/test'
    os.environ['JWT_SECRET_KEY'] = 'test-secret'
    
    try:
        # Add service path
        sys.path.insert(0, 'microservices/auth-service')
        
        # Import the app
        from main import app
        print("✅ Auth service imported successfully")
        
        # Test with TestClient
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test info endpoint
        response = client.get("/info")
        print(f"✅ Info check: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_auth_service()
    if success:
        print("\n✅ Auth service test completed successfully!")
    else:
        print("\n❌ Auth service test failed!") 