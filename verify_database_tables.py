#!/usr/bin/env python3
"""
Verify database tables and data for BMAD system
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def verify_database_tables():
    """Verify that all expected tables exist in the database."""
    
    # Get database URL from environment or microservice .env file
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
    
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment or .env files")
        return False
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        print("✅ Database connection successful!")
        
        # Expected schemas and tables
        expected_schemas = {
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
        
        print("\n📋 Verifying schemas and tables...")
        
        for schema, expected_tables in expected_schemas.items():
            print(f"\n🔍 Checking schema: {schema}")
            
            # Check if schema exists
            schema_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = $1)",
                schema
            )
            
            if not schema_exists:
                print(f"❌ Schema '{schema}' does not exist")
                continue
            
            print(f"✅ Schema '{schema}' exists")
            
            # Check tables in schema
            for table in expected_tables:
                table_exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = $1 AND table_name = $2)",
                    schema, table
                )
                
                if table_exists:
                    # Get row count
                    row_count = await conn.fetchval(f"SELECT COUNT(*) FROM {schema}.{table}")
                    print(f"   ✅ {table}: {row_count} rows")
                else:
                    print(f"   ❌ {table}: Missing")
        
        # Check for default data
        print("\n📊 Checking default data...")
        
        # Check admin user
        admin_user = await conn.fetchrow(
            "SELECT id, email, username, status FROM auth_service.users WHERE email = $1",
            'innovativemarketinglisbon@gmail.com'
        )
        
        if admin_user:
            print(f"✅ Admin user exists: {admin_user['email']} ({admin_user['username']})")
        else:
            print("❌ Admin user not found")
        
        # Check roles
        roles = await conn.fetch("SELECT name, description FROM auth_service.roles")
        print(f"✅ Found {len(roles)} roles:")
        for role in roles:
            print(f"   - {role['name']}: {role['description']}")
        
        # Check notification templates
        templates = await conn.fetch("SELECT name, channel FROM notification_service.templates")
        print(f"✅ Found {len(templates)} notification templates:")
        for template in templates:
            print(f"   - {template['name']} ({template['channel']})")
        
        # Check integrations
        integrations = await conn.fetch("SELECT name, integration_type, provider FROM integration_service.integrations")
        print(f"✅ Found {len(integrations)} integrations:")
        for integration in integrations:
            print(f"   - {integration['name']} ({integration['integration_type']} - {integration['provider']})")
        
        # Test some basic queries
        print("\n🧪 Testing basic queries...")
        
        # Test auth service queries
        user_count = await conn.fetchval("SELECT COUNT(*) FROM auth_service.users")
        print(f"✅ Users table: {user_count} users")
        
        # Test notification service queries
        template_count = await conn.fetchval("SELECT COUNT(*) FROM notification_service.templates")
        print(f"✅ Templates table: {template_count} templates")
        
        # Test agent service queries
        agent_count = await conn.fetchval("SELECT COUNT(*) FROM agent_service.agents")
        print(f"✅ Agents table: {agent_count} agents")
        
        # Test workflow service queries
        workflow_count = await conn.fetchval("SELECT COUNT(*) FROM workflow_service.workflows")
        print(f"✅ Workflows table: {workflow_count} workflows")
        
        # Test context service queries
        context_count = await conn.fetchval("SELECT COUNT(*) FROM context_service.contexts")
        print(f"✅ Contexts table: {context_count} contexts")
        
        # Test integration service queries
        integration_count = await conn.fetchval("SELECT COUNT(*) FROM integration_service.integrations")
        print(f"✅ Integrations table: {integration_count} integrations")
        
        await conn.close()
        
        print("\n🎉 Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {str(e)}")
        return False

async def test_microservice_connections():
    """Test if microservices can connect to the database."""
    
    print("\n🔧 Testing microservice database connections...")
    
    # Get database URL from environment or microservice .env file
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
    
    if not database_url:
        print("❌ Error: DATABASE_URL not found")
        return False
    
    try:
        # Test connection with different connection parameters
        conn = await asyncpg.connect(database_url)
        
        # Test basic operations
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Database version: {version.split(',')[0]}")
        
        # Test schema access
        schemas = await conn.fetch("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE '%_service'")
        print(f"✅ Found {len(schemas)} service schemas")
        
        # Test table access
        total_tables = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema LIKE '%_service'
        """)
        print(f"✅ Total service tables: {total_tables}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing microservice connections: {str(e)}")
        return False

async def main():
    """Main verification function."""
    
    print("🔍 BMAD Database Verification")
    print("=" * 50)
    
    # Verify tables and data
    tables_ok = await verify_database_tables()
    
    # Test microservice connections
    connections_ok = await test_microservice_connections()
    
    print("\n" + "=" * 50)
    if tables_ok and connections_ok:
        print("✅ All database verifications passed!")
        print("\n📋 Database is ready for microservices")
        print("🚀 You can now start the BMAD system with:")
        print("   ./start_bmad.sh")
    else:
        print("❌ Some verifications failed")
        print("💡 Check the output above for details")

if __name__ == "__main__":
    asyncio.run(main()) 