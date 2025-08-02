#!/usr/bin/env python3
"""
Comprehensive Microservices Test Script
Tests all BMAD microservices with database connectivity
"""

import os
import asyncio
import aiohttp
import asyncpg
import subprocess
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MicroservicesTester:
    def __init__(self):
        self.results = {}
        self.database_url = None
        self.services = {
            'auth-service': {'port': 8001, 'health_endpoint': '/health'},
            'notification-service': {'port': 8002, 'health_endpoint': '/health'},
            'agent-service': {'port': 8003, 'health_endpoint': '/health'},
            'workflow-service': {'port': 8004, 'health_endpoint': '/health'},
            'context-service': {'port': 8005, 'health_endpoint': '/health'},
            'integration-service': {'port': 8006, 'health_endpoint': '/health'},
            'api-gateway': {'port': 8000, 'health_endpoint': '/health'}
        }
    
    def get_database_url(self):
        """Get database URL from environment or .env file."""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Try to get from auth-service .env file
            try:
                with open('microservices/auth-service/.env', 'r') as f:
                    for line in f:
                        if line.startswith('DATABASE_URL='):
                            database_url = line.split('=', 1)[1].strip()
                            break
            except FileNotFoundError:
                pass
        
        return database_url
    
    async def test_database_connection(self):
        """Test database connection for microservices."""
        print("🔍 Testing database connection...")
        
        self.database_url = self.get_database_url()
        if not self.database_url:
            print("❌ Error: DATABASE_URL not found")
            return False
        
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Test basic queries for each service schema
            schemas = ['auth_service', 'notification_service', 'agent_service', 
                      'workflow_service', 'context_service', 'integration_service']
            
            for schema in schemas:
                try:
                    # Test a simple query
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {schema}.{schema.split('_')[0]}s")
                    print(f"   ✅ {schema}: {count} records")
                except Exception as e:
                    print(f"   ⚠️  {schema}: {str(e)}")
            
            await conn.close()
            print("✅ Database connection test completed")
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
    
    async def test_service_health(self, service_name, port, health_endpoint):
        """Test individual service health endpoint."""
        url = f"http://localhost:{port}{health_endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'healthy',
                            'response': data,
                            'response_time': response.headers.get('X-Response-Time', 'N/A')
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'error': f"HTTP {response.status}",
                            'response': await response.text()
                        }
        except aiohttp.ClientError as e:
            return {
                'status': 'unreachable',
                'error': str(e)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def test_all_services(self):
        """Test all microservices."""
        print("\n🔧 Testing all microservices...")
        
        for service_name, config in self.services.items():
            print(f"\n📋 Testing {service_name}...")
            
            # Test service health
            health_result = await self.test_service_health(
                service_name, 
                config['port'], 
                config['health_endpoint']
            )
            
            self.results[service_name] = {
                'health': health_result,
                'port': config['port'],
                'status': health_result['status']
            }
            
            if health_result['status'] == 'healthy':
                print(f"   ✅ {service_name}: Healthy")
            elif health_result['status'] == 'unreachable':
                print(f"   ⚠️  {service_name}: Unreachable (service not running)")
            else:
                print(f"   ❌ {service_name}: {health_result['error']}")
    
    def check_docker_services(self):
        """Check if Docker services are running."""
        print("\n🐳 Checking Docker services...")
        
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        print(f"   {line}")
            else:
                print("   ⚠️  Docker not available or no services running")
                
        except Exception as e:
            print(f"   ⚠️  Error checking Docker: {str(e)}")
    
    def check_environment_files(self):
        """Check if all environment files exist."""
        print("\n📁 Checking environment files...")
        
        for service_name in self.services.keys():
            env_file = Path(f"microservices/{service_name}/.env")
            if env_file.exists():
                print(f"   ✅ {service_name}: .env exists")
            else:
                print(f"   ❌ {service_name}: .env missing")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("📊 MICROSERVICES TEST REPORT")
        print("="*60)
        
        # Summary
        total_services = len(self.services)
        healthy_services = sum(1 for r in self.results.values() if r['status'] == 'healthy')
        unreachable_services = sum(1 for r in self.results.values() if r['status'] == 'unreachable')
        error_services = sum(1 for r in self.results.values() if r['status'] not in ['healthy', 'unreachable'])
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Services: {total_services}")
        print(f"   Healthy: {healthy_services}")
        print(f"   Unreachable: {unreachable_services}")
        print(f"   Errors: {error_services}")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for service_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'healthy' else "⚠️" if result['status'] == 'unreachable' else "❌"
            print(f"   {status_icon} {service_name} (port {result['port']}): {result['status']}")
            
            if result['status'] == 'healthy' and 'response' in result['health']:
                print(f"      Response: {result['health']['response']}")
            elif 'error' in result['health']:
                print(f"      Error: {result['health']['error']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if unreachable_services > 0:
            print(f"   🔄 Start unreachable services: ./start_bmad.sh")
        if error_services > 0:
            print(f"   🔧 Check service logs for errors")
        if healthy_services == total_services:
            print(f"   🎉 All services are healthy!")
        
        print("\n" + "="*60)
    
    async def run_comprehensive_test(self):
        """Run comprehensive microservices test."""
        print("🚀 BMAD Microservices Comprehensive Test")
        print("="*60)
        
        # Test database connection
        db_success = await self.test_database_connection()
        
        # Check environment files
        self.check_environment_files()
        
        # Check Docker services
        self.check_docker_services()
        
        # Test all services
        await self.test_all_services()
        
        # Generate report
        self.generate_report()
        
        return db_success and len([r for r in self.results.values() if r['status'] == 'healthy']) > 0

async def main():
    """Main test function."""
    tester = MicroservicesTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n✅ Microservices test completed successfully!")
        print("🚀 Ready for next steps!")
    else:
        print("\n❌ Some tests failed. Check the report above.")
        print("💡 Start services with: ./start_bmad.sh")

if __name__ == "__main__":
    asyncio.run(main()) 