#!/usr/bin/env python3
"""
Async PostgreSQL Integration Test for Citadel LLM
Tests async connection pooling, database operations, and health monitoring
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from citadel_llm.services.sql_service import sql_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_async_integration():
    """Test async PostgreSQL integration with connection pooling"""
    
    print("🔄 Starting Async PostgreSQL Integration Test...")
    print("=" * 60)
    
    try:
        # Step 1: Initialize connection pool
        print("1️⃣ Initializing async connection pool...")
        await sql_service.initialize()
        print("   ✅ Connection pool initialized successfully")
        
        # Step 2: Health check
        print("\n2️⃣ Performing health check...")
        health_status = await sql_service.health_check()
        print(f"   ✅ Database status: {health_status['status']}")
        print(f"   📊 Connection pool size: {health_status['connection_pool']['size']}/{health_status['connection_pool']['max_size']}")
        print(f"   🗄️ Database: {health_status['database']['database']}")
        print(f"   👤 User: {health_status['database']['user']}")
        print(f"   🖥️ Server: {health_status['database']['server_addr']}")
        
        # Step 3: Create database schema
        print("\n3️⃣ Creating database tables...")
        await sql_service.create_tables()
        print("   ✅ Database schema created successfully")
        
        # Step 4: Test conversation management
        print("\n4️⃣ Testing conversation management...")
        
        # Create a test conversation
        conversation_id = await sql_service.save_conversation(
            user_id="test_user_001",
            model_name="qwen",
            title="Test Integration Conversation - Server-02",
            metadata={"test": True, "integration": "async_pool", "server": "hx-llm-server-02"}
        )
        print(f"   ✅ Conversation created with ID: {conversation_id}")
        
        # Add some test messages
        message1_id = await sql_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content="Hello, this is a test message for async integration on Server-02",
            tokens_used=12,
            model_name="qwen",
            metadata={"test_message": 1, "server": "hx-llm-server-02"}
        )
        
        message2_id = await sql_service.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content="Hello! I'm responding from the async PostgreSQL integration test on Server-02.",
            tokens_used=15,
            model_name="qwen",
            metadata={"test_message": 2, "server": "hx-llm-server-02"}
        )
        
        print(f"   ✅ Messages saved: {message1_id}, {message2_id}")
        
        # Step 5: Retrieve conversation history using direct SQL
        print("\n5️⃣ Testing conversation retrieval...")
        conversation = await sql_service.fetch_one(
            "SELECT * FROM conversations WHERE id = $1", conversation_id
        )
        messages = await sql_service.fetch_all(
            "SELECT * FROM messages WHERE conversation_id = $1 ORDER BY message_order", conversation_id
        )
        print(f"   ✅ Retrieved conversation with {len(messages)} messages")
        print(f"   📝 Conversation title: {conversation['title']}")
        
        # Step 6: Test basic model statistics using direct SQL
        print("\n6️⃣ Testing model statistics...")
        await sql_service.execute("""
            INSERT INTO model_usage_stats (model_name, request_count, total_tokens, avg_response_time_ms)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (model_name, date_recorded) 
            DO UPDATE SET 
                request_count = model_usage_stats.request_count + EXCLUDED.request_count,
                total_tokens = model_usage_stats.total_tokens + EXCLUDED.total_tokens
        """, "qwen", 1, 27, 150)
        
        stats = await sql_service.fetch_all(
            "SELECT * FROM model_usage_stats WHERE model_name = $1", "qwen"
        )
        print(f"   ✅ Model stats updated. Records: {len(stats)}")
        
        # Step 7: Final health check
        print("\n7️⃣ Final health check...")
        final_health = await sql_service.health_check()
        print(f"   ✅ Final status: {final_health['status']}")
        print(f"   📊 Pool usage: {final_health['connection_pool']['idle_connections']} idle connections")
        
        print("\n" + "=" * 60)
        print("🎉 All async integration tests completed successfully!")
        print("✅ PostgreSQL connection pooling is working correctly")
        print("✅ Database schema creation is functional")
        print("✅ Conversation management is operational")
        print("✅ Model statistics tracking is working")
        print("✅ Health monitoring is active")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        logger.exception("Integration test error")
        return False
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        await sql_service.close()
        print("   ✅ Connection pool closed")


async def test_concurrent_operations():
    """Test concurrent database operations to verify connection pooling"""
    
    print("\n🔄 Testing concurrent operations...")
    
    await sql_service.initialize()
    
    async def create_test_conversation(user_id: str, model: str):
        """Create a test conversation concurrently"""
        try:
            conv_id = await sql_service.save_conversation(
                user_id=user_id,
                model_name=model,
                title=f"Concurrent test for {user_id}",
                metadata={"concurrent_test": True}
            )
            
            await sql_service.save_message(
                conversation_id=conv_id,
                role="user",
                content=f"Concurrent message from {user_id}",
                tokens_used=10,
                model_name=model
            )
            
            return conv_id
        except Exception as e:
            logger.error(f"Concurrent operation failed for {user_id}: {e}")
            return None
    
    # Run 5 concurrent operations
    tasks = []
    for i in range(5):
        task = create_test_conversation(f"concurrent_user_{i}", "qwen")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    
    print(f"   ✅ Completed {len(successful)} concurrent operations successfully")
    
    await sql_service.close()
    return len(successful) == 5


if __name__ == "__main__":
    async def main():
        """Main test runner"""
        print("🚀 Citadel LLM - PostgreSQL Integration Test Suite")
        print("=" * 80)
        
        # Test 1: Basic async integration
        success1 = await test_async_integration()
        
        # Test 2: Concurrent operations
        success2 = await test_concurrent_operations()
        
        print("\n" + "=" * 80)
        if success1 and success2:
            print("🎉 ALL TESTS PASSED - PostgreSQL integration is ready for production!")
            print("✅ Task 2.1: SQL Database Server Integration - COMPLETED")
        else:
            print("❌ Some tests failed - please review the errors above")
            sys.exit(1)
    
    # Run the async tests
    asyncio.run(main())
