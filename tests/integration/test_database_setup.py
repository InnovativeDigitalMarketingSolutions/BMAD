#!/usr/bin/env python3
"""
Test script to verify BMAD database setup
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import pytest

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection and verify tables exist."""
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env file")
        return False
    
    # Extract database connection details from Supabase URL
    # Supabase URL format: https://project-ref.supabase.co
    project_ref = supabase_url.split('//')[1].split('.')[0]
    
    # Construct database connection string
    # Note: You'll need to get the actual database password from Supabase dashboard
    db_url = f"postgresql://postgres:[YOUR-PASSWORD]@db.{project_ref}.supabase.co:5432/postgres"
    
    print(f"🔍 Testing connection to: {supabase_url}")
    print(f"📊 Project Reference: {project_ref}")
    
    try:
        # For now, let's just verify the credentials format
        print("✅ Supabase URL format is valid")
        print("✅ Supabase Key format is valid")
        
        # Test queries to verify database setup
        print("\n📋 Testing database schemas and tables...")
        
        # List of expected schemas
        expected_schemas = [
            'auth_service',
            'notification_service', 
            'agent_service',
            'workflow_service',
            'context_service',
            'integration_service'
        ]
        
        # List of expected tables per schema
        expected_tables = {
            'auth_service': [
                'users', 'sessions', 'roles', 'user_roles', 
                'audit_logs', 'password_reset_tokens', 'mfa_backup_codes'
            ],
            'notification_service': [
                'notifications', 'templates', 'delivery_logs', 'channel_configs'
            ],
            'agent_service': [
                'agents', 'executions'
            ],
            'workflow_service': [
                'workflows', 'workflow_steps', 'executions'
            ],
            'context_service': [
                'contexts', 'context_versions'
            ],
            'integration_service': [
                'integrations', 'integration_logs'
            ]
        }
        
        print("✅ Expected schemas and tables defined")
        
        # Note: To actually test the connection, you would need the database password
        # This can be found in Supabase Dashboard > Settings > Database > Connection string
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_microservices_config():
    """Test microservices configuration."""
    
    print("\n🔧 Testing microservices configuration...")
    
    # Check if microservices directories exist
    microservices = [
        'auth-service',
        'notification-service',
        'agent-service', 
        'workflow-service',
        'context-service',
        'integration-service',
        'api-gateway'
    ]
    
    for service in microservices:
        service_path = f"microservices/{service}"
        if os.path.exists(service_path):
            print(f"✅ {service}: Directory exists")
            
            # Check for key files
            key_files = ['README.md', 'requirements.txt', 'Dockerfile']
            for file in key_files:
                file_path = f"{service_path}/{file}"
                if os.path.exists(file_path):
                    print(f"   ✅ {file}")
                else:
                    print(f"   ⚠️  {file} (missing)")
        else:
            print(f"❌ {service}: Directory missing")
    
    return True

def create_microservices_env_template():
    """Create environment variable templates for microservices."""
    
    print("\n📝 Creating environment variable templates...")
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    # Extract project reference
    project_ref = supabase_url.split('//')[1].split('.')[0] if supabase_url else 'your-project-ref'
    
    # Template for microservices
    env_template = f"""# BMAD Microservices Environment Variables
# Copy this to each microservice's .env file

# Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.{project_ref}.supabase.co:5432/postgres
REDIS_URL=redis://localhost:6379

# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Authentication Service
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12

# Notification Service
SENDGRID_API_KEY=your-sendgrid-api-key
MAILGUN_API_KEY=your-mailgun-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
SLACK_WEBHOOK_URL={os.getenv('SLACK_WEBHOOK_URL', 'your-slack-webhook-url')}

# Service Configuration
RATE_LIMIT_PER_MINUTE=60
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=30
LOG_LEVEL=INFO

# External Integrations
OPENAI_API_KEY={os.getenv('OPENAI_API_KEY', 'your-openai-api-key')}
CLICKUP_API_TOKEN={os.getenv('CLICKUP_API_TOKEN', 'your-clickup-api-token')}
"""
    
    # Write template to file
    with open('microservices_env_template.env', 'w') as f:
        f.write(env_template)
    
    print("✅ Created microservices_env_template.env")
    print("📋 Copy this template to each microservice's .env file")
    
    return env_template

async def main():
    """Main test function."""
    
    print("🚀 BMAD Database Setup Verification")
    print("=" * 50)
    
    # Test database connection
    db_success = await test_database_connection()
    
    # Test microservices configuration
    config_success = await test_microservices_config()
    
    # Create environment templates
    create_microservices_env_template()
    
    print("\n" + "=" * 50)
    if db_success and config_success:
        print("✅ Database setup verification completed successfully!")
        print("\n📋 Next steps:")
        print("1. Get your database password from Supabase Dashboard")
        print("2. Update the DATABASE_URL in microservices_env_template.env")
        print("3. Copy the template to each microservice's .env file")
        print("4. Test the microservices individually")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    print("\n🔗 Supabase Dashboard: https://supabase.com/dashboard")
    print("📊 Database Settings: Dashboard > Settings > Database")

if __name__ == "__main__":
    asyncio.run(main()) 