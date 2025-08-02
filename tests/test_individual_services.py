#!/usr/bin/env python3
"""
Test individual microservices locally
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def test_service_import(service_name, main_file):
    """Test if a service can be imported."""
    print(f"🔍 Testing {service_name} import...")
    
    try:
        # Add service path to Python path
        service_path = f"microservices/{service_name}"
        sys.path.insert(0, service_path)
        
        # Try to import the main module
        if main_file.endswith('.py'):
            module_name = main_file[:-3]
        else:
            module_name = main_file
            
        exec(f"import {module_name}")
        print(f"   ✅ {service_name}: Import successful")
        return True
        
    except Exception as e:
        print(f"   ❌ {service_name}: Import failed - {str(e)}")
        return False

def test_service_startup(service_name, main_file, port):
    """Test if a service can start."""
    print(f"🚀 Testing {service_name} startup...")
    
    try:
        # Check if port is already in use
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ⚠️  {service_name}: Port {port} already in use")
            return True
        
        # Try to start the service
        service_path = f"microservices/{service_name}"
        cmd = f"cd {service_path} && python {main_file}"
        
        # Start in background
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"   ✅ {service_name}: Started successfully")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ {service_name}: Failed to start")
            print(f"      Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"   ❌ {service_name}: Startup test failed - {str(e)}")
        return False

def test_health_endpoint(service_name, port):
    """Test health endpoint."""
    print(f"🏥 Testing {service_name} health endpoint...")
    
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ {service_name}: Health endpoint working")
            print(f"      Response: {response.json()}")
            return True
        else:
            print(f"   ❌ {service_name}: Health endpoint failed - {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  {service_name}: Health endpoint unreachable - {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 BMAD Individual Services Test")
    print("="*50)
    
    # Define services to test
    services = [
        {
            'name': 'auth-service',
            'main_file': 'main.py',
            'port': 8001,
            'description': 'Authentication and Authorization'
        },
        {
            'name': 'notification-service', 
            'main_file': 'src/api/main.py',
            'port': 8002,
            'description': 'Notification Management'
        },
        {
            'name': 'agent-service',
            'main_file': 'src/api/main.py', 
            'port': 8003,
            'description': 'Agent Management'
        },
        {
            'name': 'workflow-service',
            'main_file': 'src/api/main.py',
            'port': 8004, 
            'description': 'Workflow Orchestration'
        },
        {
            'name': 'context-service',
            'main_file': 'src/api/main.py',
            'port': 8005,
            'description': 'Context Management'
        },
        {
            'name': 'integration-service',
            'main_file': 'src/api/main.py',
            'port': 8006,
            'description': 'External Integrations'
        }
    ]
    
    results = {}
    
    for service in services:
        print(f"\n📋 Testing {service['name']} ({service['description']})")
        print("-" * 40)
        
        # Test import
        import_success = test_service_import(service['name'], service['main_file'])
        
        # Test startup (only if import succeeded)
        startup_success = False
        if import_success:
            startup_success = test_service_startup(service['name'], service['main_file'], service['port'])
        
        # Test health endpoint (only if startup succeeded)
        health_success = False
        if startup_success:
            health_success = test_health_endpoint(service['name'], service['port'])
        
        results[service['name']] = {
            'import': import_success,
            'startup': startup_success,
            'health': health_success,
            'description': service['description']
        }
    
    # Generate report
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    total_services = len(services)
    import_success = sum(1 for r in results.values() if r['import'])
    startup_success = sum(1 for r in results.values() if r['startup'])
    health_success = sum(1 for r in results.values() if r['health'])
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Services: {total_services}")
    print(f"   Import Success: {import_success}/{total_services}")
    print(f"   Startup Success: {startup_success}/{total_services}")
    print(f"   Health Success: {health_success}/{total_services}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for service_name, result in results.items():
        status_icon = "✅" if result['health'] else "⚠️" if result['startup'] else "❌"
        print(f"   {status_icon} {service_name}: {result['description']}")
        print(f"      Import: {'✅' if result['import'] else '❌'}")
        print(f"      Startup: {'✅' if result['startup'] else '❌'}")
        print(f"      Health: {'✅' if result['health'] else '❌'}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if health_success == total_services:
        print("   🎉 All services are working!")
    elif startup_success > 0:
        print("   🔧 Some services can start but have issues")
    elif import_success > 0:
        print("   🔧 Some services can import but can't start")
    else:
        print("   🔧 All services have import issues")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main() 