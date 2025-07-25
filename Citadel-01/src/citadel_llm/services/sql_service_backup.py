"""
SQL Database Service for Citadel LLM
Implements async PostgreSQL connection pooling using asyncpg
Handles metadata storage and conversation management
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import asyncpg
import yaml
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)


class SQLService:
    """Async PostgreSQL service with connection pooling and health monitoring"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.config: Dict[str, Any] = {}
        self.credentials: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load database configuration from YAML files"""
        try:
            # Load main database configuration
            with open("/opt/citadel/config/services/integration/sql-database.yaml", 'r') as f:
                self.config = yaml.safe_load(f)
                
            # Load database credentials
            with open("/opt/citadel/config/secrets/database-credentials.yaml", 'r') as f:
                self.credentials = yaml.safe_load(f)
                
            logger.info("Database configuration loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
    
    async def initialize_pool(self) -> None:
        """Initialize async connection pool with asyncpg"""
        if self.pool:
            logger.warning("Connection pool already initialized")
            return
            
        try:
            db_config = self.config["database"]
            db_creds = self.credentials["database"]
            
            # Create connection pool with configuration parameters
            self.pool = await asyncpg.create_pool(
                host=db_creds["host"],
                port=db_creds["direct_port"],  # Use direct PostgreSQL port for asyncpg
                database=db_creds["database"],
                user=db_creds["username"],
                password=db_creds["password"],
                min_size=5,  # Minimum connections in pool
                max_size=db_config.get("pool_size", 10),  # Maximum connections
                command_timeout=db_config.get("timeout_seconds", 30),
                server_settings={
                    'application_name': 'citadel_llm_service',
                    'timezone': 'UTC'
                }
            )
            
            # Test the connection
            await self.health_check()
            logger.info(f"Database connection pool initialized successfully with {db_config.get('pool_size', 10)} max connections")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise HTTPException(status_code=503, detail="Database connection failed")
    
    async def close_pool(self) -> None:
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with proper error handling"""
        if not self.pool:
            raise HTTPException(status_code=503, detail="Database pool not initialized")
            
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
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            async with self.get_connection() as conn:
                # Test basic connectivity and get server info
                result = await conn.fetchrow(
                    "SELECT current_database() as database, current_user as user, "
                    "inet_server_addr() as server_addr, version() as version"
                )
                
                # Check pool status
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
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def create_tables(self) -> None:
        """Create necessary tables for conversation management and metadata"""
        try:
            async with self.get_connection() as conn:
                # Create conversations table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id VARCHAR(255) NOT NULL,
                        model_name VARCHAR(100) NOT NULL,
                        title VARCHAR(500),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB DEFAULT '{}'
                    )
                """)
                
                # Create indexes for conversations table
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_user_created 
                    ON conversations (user_id, created_at)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_model_created 
                    ON conversations (model_name, created_at)
                """)
                
                # Create messages table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                        role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                        content TEXT NOT NULL,
                        tokens_used INTEGER,
                        model_name VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB DEFAULT '{}'
                    )
                """)
                
                # Create indexes for messages table
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_conversation_created 
                    ON messages (conversation_id, created_at)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_role_created 
                    ON messages (role, created_at)
                """)
                
                # Create model_usage_stats table
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
                
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize database schema")
    
    async def save_conversation(self, user_id: str, model_name: str, title: str = None, 
                              metadata: Dict[str, Any] = None) -> str:
        """Save a new conversation and return its ID"""
        try:
            async with self.get_connection() as conn:
                # Convert metadata dict to JSON string for JSONB storage
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
                          metadata: Dict[str, Any] = None) -> str:
        """Save a message to a conversation"""
        try:
            async with self.get_connection() as conn:
                # Convert metadata dict to JSON string for JSONB storage
                metadata_json = json.dumps(metadata or {})
                
                message_id = await conn.fetchval("""
                    INSERT INTO messages (conversation_id, role, content, tokens_used, model_name, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                """, conversation_id, role, content, tokens_used, model_name, metadata_json)
                
                logger.debug(f"Message saved with ID: {message_id}")
                return str(message_id)
                
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise HTTPException(status_code=500, detail="Failed to save message")
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history with messages"""
        try:
            async with self.get_connection() as conn:
                # Get conversation details
                conversation = await conn.fetchrow("""
                    SELECT id, user_id, model_name, title, created_at, updated_at, metadata
                    FROM conversations WHERE id = $1
                """, conversation_id)
                
                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")
                
                # Get all messages for this conversation
                messages = await conn.fetch("""
                    SELECT id, role, content, tokens_used, model_name, created_at, metadata
                    FROM messages 
                    WHERE conversation_id = $1 
                    ORDER BY created_at
                """, conversation_id)
                
                return {
                    "conversation": dict(conversation),
                    "messages": [dict(msg) for msg in messages]
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve conversation")
    
    async def update_model_stats(self, model_name: str, tokens_used: int, 
                               response_time_ms: int) -> None:
        """Update model usage statistics"""
        try:
            async with self.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO model_usage_stats (model_name, request_count, total_tokens, avg_response_time_ms, last_used)
                    VALUES ($1, 1, $2, $3, CURRENT_TIMESTAMP)
                    ON CONFLICT (model_name, date_recorded)
                    DO UPDATE SET
                        request_count = model_usage_stats.request_count + 1,
                        total_tokens = model_usage_stats.total_tokens + $2,
                        avg_response_time_ms = (model_usage_stats.avg_response_time_ms + $3) / 2,
                        last_used = CURRENT_TIMESTAMP
                """, model_name, tokens_used, response_time_ms)
                
        except Exception as e:
            logger.error(f"Failed to update model stats: {e}")
            # Don't raise exception for stats updates to avoid breaking main flow
    
    async def get_model_stats(self, model_name: str = None) -> List[Dict[str, Any]]:
        """Get model usage statistics"""
        try:
            async with self.get_connection() as conn:
                if model_name:
                    stats = await conn.fetch("""
                        SELECT * FROM model_usage_stats 
                        WHERE model_name = $1 
                        ORDER BY date_recorded DESC
                    """, model_name)
                else:
                    stats = await conn.fetch("""
                        SELECT * FROM model_usage_stats 
                        ORDER BY last_used DESC
                    """)
                
                return [dict(stat) for stat in stats]
                
        except Exception as e:
            logger.error(f"Failed to retrieve model stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve model statistics")


# Global SQL service instance
sql_service = SQLService()


# Startup and shutdown functions for FastAPI
async def startup_sql_service():
    """Initialize SQL service on application startup"""
    await sql_service.initialize_pool()
    await sql_service.create_tables()


async def shutdown_sql_service():
    """Clean up SQL service on application shutdown"""
    await sql_service.close_pool()


# Sync version for testing and compatibility
def test_sync_connection():
    """Sync connection test function for debugging"""
    import psycopg
    
    try:
        # Load config for sync test
        with open("/opt/citadel/config/services/integration/sql-database.yaml", 'r') as f:
            config = yaml.safe_load(f)
        with open("/opt/citadel/config/secrets/database-credentials.yaml", 'r') as f:
            credentials = yaml.safe_load(f)
        
        db_conf = config["database"]
        db_creds = credentials["database"]
        
        # Connect using psycopg (sync)
        conn = psycopg.connect(
            host=db_creds["host"],
            port=db_creds["direct_port"],  # Use direct port for testing
            dbname=db_creds["database"],
            user=db_creds["username"],
            password=db_creds["password"]
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, inet_server_addr(), version();")
            result = cur.fetchone()
            print("✅ Sync Connection Test Result:")
            print(f"   Database: {result[0]}")
            print(f"   User: {result[1]}")
            print(f"   Server: {result[2]}")
            print(f"   Version: {result[3]}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Sync Connection Test Failed: {e}")
        return False


if __name__ == "__main__":
    # Run sync test when executed directly
    test_sync_connection()
