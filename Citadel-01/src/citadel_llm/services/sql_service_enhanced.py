"""
Enhanced SQL Database Service for Citadel LLM
Combines best practices from both implementations
Implements async PostgreSQL connection pooling using asyncpg
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any, List, Union
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
import yaml
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)


class SQLService:
    """Enhanced async PostgreSQL service with connection pooling and comprehensive monitoring"""
    
    def __init__(self, config_path: Optional[str] = None, credentials_path: Optional[str] = None):
        self.pool: Optional[asyncpg.Pool] = None
        self.config: Dict[str, Any] = {}
        self.credentials: Dict[str, Any] = {}
        self.config_path = config_path or "/opt/citadel/config/services/integration/sql-database.yaml"
        self.credentials_path = credentials_path or "/opt/citadel/config/secrets/database-credentials.yaml"
        self._is_initialized = False
        
    def _load_config(self) -> None:
        """Load database configuration from YAML files with error handling"""
        try:
            # Load main database configuration
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                
            # Load database credentials
            with open(self.credentials_path, 'r') as f:
                self.credentials = yaml.safe_load(f)
                
            logger.info("Database configuration loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
    
    def _get_connection_string(self) -> str:
        """Constructs the connection string from configuration"""
        db_config = self.config["database"]
        db_creds = self.credentials["database"]
        
        ssl_mode = db_config.get('ssl_mode', 'prefer')
        ssl_param = f"?sslmode={ssl_mode}" if ssl_mode != 'disable' else ""
        
        return (
            f"postgresql://{db_creds['username']}:{db_creds['password']}@"
            f"{db_creds['host']}:{db_creds['direct_port']}/{db_creds['database']}{ssl_param}"
        )
    
    async def initialize(self, db_config: Optional[Dict[str, Any]] = None, 
                        password: Optional[str] = None) -> None:
        """Initialize async connection pool with flexible configuration"""
        if self._is_initialized:
            logger.warning("SQLService already initialized")
            return
            
        try:
            # Load config if not provided via parameters
            if not db_config or not password:
                self._load_config()
                db_config = self.config["database"]
                password = self.credentials["database"]["password"]
            
            # Create connection pool using either DSN or individual parameters
            if hasattr(self, 'config') and self.config:
                # Use existing method with enhanced parameters
                self.pool = await asyncpg.create_pool(
                    host=self.credentials["database"]["host"],
                    port=self.credentials["database"]["direct_port"],
                    database=self.credentials["database"]["database"],
                    user=self.credentials["database"]["username"],
                    password=self.credentials["database"]["password"],
                    min_size=5,  # Minimum connections in pool
                    max_size=db_config.get("pool_size", 10),
                    command_timeout=db_config.get("timeout_seconds", 30),
                    ssl=db_config.get('ssl_mode', 'prefer') if db_config.get('ssl_mode') != 'disable' else False,
                    server_settings={
                        'application_name': 'citadel_llm_service',
                        'timezone': 'UTC'
                    }
                )
            else:
                # Use DSN method for external configuration
                conn_string = self._get_connection_string()
                self.pool = await asyncpg.create_pool(
                    dsn=conn_string,
                    min_size=db_config.get('pool_size', 5),
                    max_size=db_config.get('pool_size', 10),
                    command_timeout=db_config.get('timeout_seconds', 30)
                )
            
            # Test the connection
            await self.health_check()
            self._is_initialized = True
            logger.info(f"SQLService connection pool initialized successfully with {db_config.get('pool_size', 10)} max connections")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQLService connection pool: {e}")
            raise HTTPException(status_code=503, detail="Database connection failed")
    
    async def close(self) -> None:
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._is_initialized = False
            logger.info("SQLService connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with proper error handling"""
        if not self.pool or not self._is_initialized:
            raise HTTPException(status_code=503, detail="SQLService not initialized")
            
        connection = None
        try:
            connection = await self.pool.acquire()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        finally:
            if connection:
                await self.pool.release(connection)
    
    # Enhanced query methods with better error handling
    async def execute(self, query: str, *args: Any) -> str:
        """Execute a DDL/DML query and return status"""
        if not self._is_initialized:
            raise RuntimeError("SQLService not initialized. Call initialize() first.")
            
        async with self.get_connection() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(query, *args)
                    logger.debug(f"Executed query: {query[:100]}...")
                    return "OK"
                except Exception as e:
                    logger.error(f"Error executing query: {query[:100]}... - {e}")
                    raise
    
    async def fetch_one(self, query: str, *args: Any) -> Optional[Dict[str, Any]]:
        """Fetch a single row from a query"""
        if not self._is_initialized:
            raise RuntimeError("SQLService not initialized. Call initialize() first.")
            
        async with self.get_connection() as conn:
            try:
                record = await conn.fetchrow(query, *args)
                return dict(record) if record else None
            except Exception as e:
                logger.error(f"Error fetching one row: {query[:100]}... - {e}")
                raise
    
    async def fetch_all(self, query: str, *args: Any) -> List[Dict[str, Any]]:
        """Fetch all rows from a query"""
        if not self._is_initialized:
            raise RuntimeError("SQLService not initialized. Call initialize() first.")
            
        async with self.get_connection() as conn:
            try:
                records = await conn.fetch(query, *args)
                return [dict(record) for record in records]
            except Exception as e:
                logger.error(f"Error fetching all rows: {query[:100]}... - {e}")
                raise
    
    async def health_check(self) -> Union[bool, Dict[str, Any]]:
        """Comprehensive health check with detailed status"""
        try:
            async with self.get_connection() as conn:
                # Test basic connectivity and get server info
                result = await conn.fetchrow(
                    "SELECT current_database() as database, current_user as user, "
                    "inet_server_addr() as server_addr, version() as version"
                )
                
                if self.pool:
                    # Enhanced pool status
                    pool_status = {
                        "size": self.pool.get_size(),
                        "max_size": self.pool.get_max_size(),
                        "min_size": self.pool.get_min_size(),
                        "idle_connections": self.pool.get_idle_size()
                    }
                    
                    return {
                        "status": "healthy",
                        "database": dict(result),
                        "connection_pool": pool_status,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                else:
                    return True  # Simple boolean for basic health check
                    
        except Exception as e:
            logger.error(f"SQLService health check failed: {e}")
            if self.pool:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                return False
    
    # Enhanced schema management combining both approaches
    async def create_tables(self) -> None:
        """Create comprehensive tables for LLM metadata and conversation management"""
        try:
            async with self.get_connection() as conn:
                # LLM Metadata table (from proposed implementation)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS llm_metadata (
                        id SERIAL PRIMARY KEY,
                        model_name VARCHAR(255) NOT NULL UNIQUE,
                        description TEXT,
                        quantization VARCHAR(50),
                        size_gb NUMERIC,
                        last_pulled TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Enhanced conversations table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id VARCHAR(255) NOT NULL,
                        model_name VARCHAR(100) NOT NULL,
                        title VARCHAR(500),
                        start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP WITH TIME ZONE,
                        total_tokens INTEGER DEFAULT 0,
                        duration_ms INTEGER,
                        status VARCHAR(50) DEFAULT 'active',
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Enhanced messages table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                        role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                        content TEXT NOT NULL,
                        token_count INTEGER,
                        model_name VARCHAR(100),
                        message_order INTEGER NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB DEFAULT '{}'
                    )
                """)
                
                # User sessions table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id VARCHAR(255) NOT NULL,
                        login_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        status VARCHAR(50) DEFAULT 'active'
                    )
                """)
                
                # Model usage statistics
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_usage_stats (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        model_name VARCHAR(100) NOT NULL,
                        request_count INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        avg_response_time_ms INTEGER DEFAULT 0,
                        last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        date_recorded DATE DEFAULT CURRENT_DATE,
                        metadata JSONB DEFAULT '{}',
                        UNIQUE (model_name, date_recorded)
                    )
                """)
                
                # Create indexes for performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_user_created 
                    ON conversations (user_id, created_at)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_model_created 
                    ON conversations (model_name, created_at)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_conversation_created 
                    ON messages (conversation_id, timestamp)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_role_created 
                    ON messages (role, timestamp)
                """)
                
                logger.info("Enhanced database schema created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize database schema")
    
    # Enhanced conversation management methods with JSON handling
    async def save_conversation(self, user_id: str, model_name: str, title: str = None, 
                              metadata: Dict[str, Any] = None) -> str:
        """Save a new conversation and return its ID"""
        try:
            async with self.get_connection() as conn:
                metadata_json = json.dumps(metadata or {})
                
                conversation_id = await conn.fetchval("""
                    INSERT INTO conversations (user_id, model_name, title, metadata)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, user_id, model_name, title, metadata_json)
                
                logger.info(f"Conversation saved with ID: {conversation_id}")
                return str(conversation_id)
                
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            raise HTTPException(status_code=500, detail="Failed to save conversation")
    
    async def save_message(self, conversation_id: str, role: str, content: str,
                          tokens_used: int = None, model_name: str = None,
                          message_order: int = None, metadata: Dict[str, Any] = None) -> str:
        """Save a message to a conversation with enhanced tracking"""
        try:
            async with self.get_connection() as conn:
                metadata_json = json.dumps(metadata or {})
                
                # Auto-calculate message order if not provided
                if message_order is None:
                    order_result = await conn.fetchval("""
                        SELECT COALESCE(MAX(message_order), 0) + 1 
                        FROM messages WHERE conversation_id = $1
                    """, conversation_id)
                    message_order = order_result
                
                message_id = await conn.fetchval("""
                    INSERT INTO messages (conversation_id, role, content, token_count, 
                                        model_name, message_order, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                """, conversation_id, role, content, tokens_used, model_name, message_order, metadata_json)
                
                logger.debug(f"Message saved with ID: {message_id}")
                return str(message_id)
                
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise HTTPException(status_code=500, detail="Failed to save message")


# Global enhanced SQL service instance
sql_service = SQLService()


# Startup and shutdown functions for FastAPI
async def startup_sql_service():
    """Initialize enhanced SQL service on application startup"""
    await sql_service.initialize()
    await sql_service.create_tables()


async def shutdown_sql_service():
    """Clean up SQL service on application shutdown"""
    await sql_service.close()


# For backward compatibility and testing
def create_sql_service(config_path: str = None, credentials_path: str = None) -> SQLService:
    """Factory function to create a new SQL service instance"""
    return SQLService(config_path, credentials_path)


if __name__ == "__main__":
    # Simple test
    async def test():
        service = SQLService()
        await service.initialize()
        health = await service.health_check()
        print(f"Health check: {health}")
        await service.close()
    
    asyncio.run(test())
