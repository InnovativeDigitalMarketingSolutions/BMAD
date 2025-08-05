#!/usr/bin/env python3
"""
Setup database connection for BMAD microservices
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_connection_info():
    """Get Supabase connection information from environment."""
    
    supabase_url = os.getenv('SUPABASE_URL')
    if not supabase_url:
        print("❌ Error: SUPABASE_URL not found in environment")
        return None
    
    # Extract project reference
    project_ref = supabase_url.split('//')[1].split('.')[0]
    
    print(f"🔍 Supabase Project: {project_ref}")
    print(f"🌐 Supabase URL: {supabase_url}")
    
    return {
        'project_ref': project_ref,
        'supabase_url': supabase_url,
        'database_host': f"db.{project_ref}.supabase.co",
        'database_port': 5432,
        'database_name': 'postgres',
        'database_user': 'postgres'
    }

def update_env_files_with_password(password):
    """Update all microservice .env files with the database password."""
    
    if not password:
        print("❌ Error: No password provided")
        return False
    
    # Get connection info
    conn_info = get_supabase_connection_info()
    if not conn_info:
        return False
    
    # Construct database URL
    database_url = f"postgresql://{conn_info['database_user']}:{password}@{conn_info['database_host']}:{conn_info['database_port']}/{conn_info['database_name']}"
    
    print(f"🔗 Database URL: postgresql://{conn_info['database_user']}:***@{conn_info['database_host']}:{conn_info['database_port']}/{conn_info['database_name']}")
    
    # Update each microservice .env file
    microservices = [
        'auth-service',
        'notification-service', 
        'agent-service',
        'workflow-service',
        'context-service',
        'integration-service',
        'api-gateway'
    ]
    
    updated_count = 0
    for service in microservices:
        env_file = Path(f"microservices/{service}/.env")
        
        if env_file.exists():
            try:
                # Read current content
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Replace the placeholder with actual password
                updated_content = content.replace(
                    'DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@',
                    f'DATABASE_URL=postgresql://postgres:{password}@'
                )
                
                # Write back
                with open(env_file, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated {service}/.env")
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Error updating {service}/.env: {str(e)}")
        else:
            print(f"⚠️  {service}/.env not found")
    
    print(f"\n📊 Updated {updated_count} microservice environment files")
    return True

def test_database_connection(password):
    """Test the database connection."""
    
    conn_info = get_supabase_connection_info()
    if not conn_info:
        return False
    
    database_url = f"postgresql://{conn_info['database_user']}:{password}@{conn_info['database_host']}:{conn_info['database_port']}/{conn_info['database_name']}"
    
    print("\n🔍 Testing database connection...")
    
    try:
        # Try to connect using psql (if available)
        test_command = [
            'psql', database_url, 
            '-c', 'SELECT version();',
            '-t'  # Tuple only output
        ]
        
        result = subprocess.run(
            test_command, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Database connection successful!")
            print(f"📋 PostgreSQL version: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Database connection failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  psql not found. Skipping connection test.")
        print("💡 You can test the connection manually using:")
        print(f"   psql {database_url}")
        return True
    except subprocess.TimeoutExpired:
        print("❌ Database connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        return False

def main():
    """Main function."""
    
    print("🚀 BMAD Database Connection Setup")
    print("=" * 50)
    
    # Get connection info
    conn_info = get_supabase_connection_info()
    if not conn_info:
        sys.exit(1)
    
    print("\n📋 To get your database password:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings > Database")
    print("4. Copy the password from the connection string")
    print("5. Or use the 'Reset database password' option")
    
    print(f"\n🔗 Direct link to your project:")
    print(f"   https://supabase.com/dashboard/project/{conn_info['project_ref']}/settings/database")
    
    # Ask for password
    print("\n" + "=" * 50)
    password = input("🔑 Enter your Supabase database password: ").strip()
    
    if not password:
        print("❌ No password provided")
        sys.exit(1)
    
    # Test connection
    if test_database_connection(password):
        # Update environment files
        if update_env_files_with_password(password):
            print("\n✅ Database setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Test individual microservices")
            print("2. Start the API Gateway")
            print("3. Verify all services can connect to the database")
        else:
            print("\n❌ Failed to update environment files")
            sys.exit(1)
    else:
        print("\n❌ Database connection failed. Please check your password.")
        sys.exit(1)

if __name__ == "__main__":
    main() 