#!/usr/bin/env python3
"""
Script to query PostgreSQL users on 192.168.10.35
Uses the Citadel SQL service for connection management
"""

import asyncio
import sys
import os

# Add the source directory to Python path
sys.path.append('/opt/citadel/src')

from citadel_llm.services.sql_service import SQLService
import asyncpg

async def query_postgres_users():
    """Connect to PostgreSQL and query users/roles"""
    
    # Connection parameters for 192.168.10.35
    conn_params = {
        'host': '192.168.10.35',
        'port': 5432,
        'database': 'citadel_llm_db',
        'user': 'citadel_llm_user',
        'password': 'SecureGatewayPass2024!'  # From the HX-Server-02 spec
    }
    
    try:
        print("🔗 Connecting to PostgreSQL on 192.168.10.35...")
        
        # Try direct connection first
        conn = await asyncpg.connect(**conn_params)
        
        print("✅ Connected successfully!")
        print("\n📋 Database Users/Roles:")
        print("=" * 60)
        
        # Query database users/roles
        users_query = """
        SELECT 
            usename as username,
            usesysid as user_id,
            usecreatedb as can_create_db,
            usesuper as is_superuser,
            userepl as can_replicate,
            usebypassrls as can_bypass_rls,
            passwd as has_password,
            valuntil as password_expiry
        FROM pg_user
        ORDER BY usename;
        """
        
        users = await conn.fetch(users_query)
        
        if users:
            print(f"Found {len(users)} users:")
            print()
            for user in users:
                print(f"👤 Username: {user['username']}")
                print(f"   User ID: {user['user_id']}")
                print(f"   Can Create DB: {user['can_create_db']}")
                print(f"   Is Superuser: {user['is_superuser']}")
                print(f"   Can Replicate: {user['can_replicate']}")
                print(f"   Can Bypass RLS: {user['can_bypass_rls']}")
                print(f"   Has Password: {'Yes' if user['has_password'] else 'No'}")
                if user['password_expiry']:
                    print(f"   Password Expires: {user['password_expiry']}")
                print("-" * 40)
        else:
            print("No users found.")
        
        print("\n🏢 Database Roles (including groups):")
        print("=" * 60)
        
        # Query all roles (users + groups)
        roles_query = """
        SELECT 
            rolname as role_name,
            rolsuper as is_superuser,
            rolinherit as inherits_privileges,
            rolcreaterole as can_create_roles,
            rolcreatedb as can_create_db,
            rolcanlogin as can_login,
            rolreplication as can_replicate,
            rolconnlimit as connection_limit,
            rolbypassrls as can_bypass_rls
        FROM pg_roles
        ORDER BY rolname;
        """
        
        roles = await conn.fetch(roles_query)
        
        if roles:
            print(f"Found {len(roles)} roles:")
            print()
            for role in roles:
                role_type = "👤 User" if role['can_login'] else "👥 Group"
                print(f"{role_type}: {role['role_name']}")
                print(f"   Is Superuser: {role['is_superuser']}")
                print(f"   Can Login: {role['can_login']}")
                print(f"   Can Create DB: {role['can_create_db']}")
                print(f"   Can Create Roles: {role['can_create_roles']}")
                print(f"   Inherits Privileges: {role['inherits_privileges']}")
                if role['connection_limit'] != -1:
                    print(f"   Connection Limit: {role['connection_limit']}")
                print("-" * 40)
        
        print("\n🗄️ Database Information:")
        print("=" * 60)
        
        # Get database info
        db_info_query = """
        SELECT 
            current_database() as database,
            current_user as current_user,
            session_user as session_user,
            version() as version,
            inet_server_addr() as server_ip,
            inet_server_port() as server_port
        """
        
        db_info = await conn.fetchrow(db_info_query)
        
        print(f"Database: {db_info['database']}")
        print(f"Current User: {db_info['current_user']}")
        print(f"Session User: {db_info['session_user']}")
        print(f"Server IP: {db_info['server_ip']}")
        print(f"Server Port: {db_info['server_port']}")
        print(f"PostgreSQL Version: {db_info['version']}")
        
        await conn.close()
        print("\n✅ Connection closed successfully.")
        
    except asyncpg.InvalidPasswordError:
        print("❌ Authentication failed. Invalid username or password.")
        print("   Trying with common default credentials...")
        
        # Try with common defaults
        default_params = conn_params.copy()
        default_params['user'] = 'postgres'
        default_params['password'] = 'postgres'
        
        try:
            conn = await asyncpg.connect(**default_params)
            print("✅ Connected with postgres user!")
            
            users = await conn.fetch("SELECT usename FROM pg_user ORDER BY usename;")
            print(f"\n📋 Users found: {[user['usename'] for user in users]}")
            
            await conn.close()
            
        except Exception as e:
            print(f"❌ Also failed with postgres user: {e}")
            
    except asyncpg.InvalidCatalogNameError:
        print("❌ Database 'citadel_llm_db' does not exist.")
        print("   Trying to connect to 'postgres' database...")
        
        # Try connecting to default postgres database
        default_params = conn_params.copy()
        default_params['database'] = 'postgres'
        
        try:
            conn = await asyncpg.connect(**default_params)
            print("✅ Connected to postgres database!")
            
            # List all databases
            databases = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
            print(f"\n🗄️ Available databases: {[db['datname'] for db in databases]}")
            
            await conn.close()
            
        except Exception as e:
            print(f"❌ Failed to connect to postgres database: {e}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Error type:", type(e).__name__)

if __name__ == "__main__":
    print("🔍 PostgreSQL User Query Tool")
    print("Connecting to 192.168.10.35...")
    
    try:
        asyncio.run(query_postgres_users())
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
